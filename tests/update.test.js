import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { install, packageRoot, skillFiles } from '../lib/install.js';
import { update } from '../lib/update.js';

const releases = JSON.parse(fs.readFileSync(new URL('./fixtures/released-skills.json', import.meta.url), 'utf8'));
const manifests = JSON.parse(fs.readFileSync(new URL('../lib/released-skills.json', import.meta.url), 'utf8'));
const tempBase = fs.realpathSync(os.tmpdir());
const dest = (root, host = 'claude') => path.join(root, host === 'claude' ? '.claude' : '.agents', 'skills/configure-subagents');
function fixture(t) {
  const root = fs.mkdtempSync(path.join(tempBase, 'configure-subagents-update-'));
  t.after(() => {
    assert.equal(path.dirname(fs.realpathSync(root)), tempBase);
    assert.ok(path.basename(root).startsWith('configure-subagents-update-'));
    assert.equal(fs.lstatSync(root).isSymbolicLink(), false);
    fs.rmSync(root, { recursive: true });
  });
  return root;
}
function seed(root, host = 'claude', release = releases.at(-1)) {
  for (const [name, data] of Object.entries(release.files)) {
    const filename = path.join(dest(root, host), name);
    fs.mkdirSync(path.dirname(filename), { recursive: true });
    fs.writeFileSync(filename, Buffer.from(data, 'base64'));
  }
}
function tree(root) {
  const entries = {};
  function walk(dir) {
    for (const name of fs.readdirSync(dir).sort()) {
      const filename = path.join(dir, name), stat = fs.lstatSync(filename);
      const relative = path.relative(root, filename);
      if (stat.isSymbolicLink()) entries[relative] = { link: fs.readlinkSync(filename) };
      else if (stat.isDirectory()) { entries[relative] = 'directory'; walk(filename); }
      else entries[relative] = { data: fs.readFileSync(filename).toString('base64'), mtime: stat.mtimeMs };
    }
  }
  walk(root);
  return entries;
}
function assertCurrent(root, host = 'claude') {
  for (const name of skillFiles) assert.deepEqual(fs.readFileSync(path.join(dest(root, host), name)), fs.readFileSync(path.join(packageRoot, 'configure-subagents', name)));
}
function run(root, args) {
  const result = spawnSync(process.execPath, [path.join(packageRoot, 'bin/configure-subagents.js'), ...args], { cwd: root, encoding: 'utf8' });
  assert.ifError(result.error);
  return result;
}
function link(t, outside, filename) {
  try { fs.symlinkSync(outside, filename, process.platform === 'win32' ? 'junction' : 'dir'); return true; }
  catch (error) {
    if (['EPERM', 'EACCES'].includes(error.code)) { t.skip('Links unavailable'); return false; }
    throw error;
  }
}

test('bundled fingerprints correspond to integrity-verified public fixture bytes', () => {
  assert.equal(manifests.length, releases.length);
  for (const [index, release] of releases.entries()) {
    const { files, ...provenance } = release;
    const hashes = Object.fromEntries(Object.entries(files).map(([name, data]) => [name, createHash('sha256').update(Buffer.from(data, 'base64')).digest('hex')]));
    assert.deepEqual(manifests[index], { ...provenance, files: hashes });
  }
});

for (const release of releases) {
  test(`upgrades published ${release.package}@${release.version}; backs up exact old bytes/mtimes`, t => {
    const root = fixture(t);
    seed(root, 'claude', release);
    const before = tree(dest(root));
    const [result] = update({ host: 'claude', project: root });
    assert.equal(result.status, 'updated');
    assert.ok(result.fromVersion.includes(release.version));
    assertCurrent(root);
    assert.deepEqual(tree(result.backup), before);
    assert.ok(result.backup.startsWith(path.join(root, '.configure-subagents-updates') + path.sep));
    assert.equal(fs.existsSync(path.join(root, '.agents')), false);
  });
}

test('mixed older versions update both hosts, preserve project agents and unrelated project settings', t => {
  const root = fixture(t);
  seed(root, 'claude', releases[0]); seed(root, 'codex', releases.at(-1));
  fs.mkdirSync(path.join(root, '.claude/agents'), { recursive: true });
  fs.writeFileSync(path.join(root, '.claude/agents/custom.md'), Buffer.from('\ufeffEnglish agent\r\nkeep\r\n'));
  fs.writeFileSync(path.join(root, '.claude/settings.json'), '{"custom":true}');
  const before = tree(path.join(root, '.claude/agents'));
  const settings = fs.statSync(path.join(root, '.claude/settings.json')).mtimeMs;
  assert.deepEqual(update({ host: 'both', project: root }).map(item => item.status), ['updated', 'updated']);
  assertCurrent(root, 'claude'); assertCurrent(root, 'codex');
  assert.deepEqual(tree(path.join(root, '.claude/agents')), before);
  assert.equal(fs.readFileSync(path.join(root, '.claude/settings.json'), 'utf8'), '{"custom":true}');
  assert.equal(fs.statSync(path.join(root, '.claude/settings.json')).mtimeMs, settings);
});

test('repeat update is a complete no-op, including no new backups', t => {
  const root = fixture(t); seed(root, 'claude'); seed(root, 'codex');
  update({ host: 'both', project: root });
  const before = tree(root);
  assert.deepEqual(update({ host: 'both', project: root }).map(item => item.status), ['unchanged', 'unchanged']);
  assert.deepEqual(tree(root), before);
});

test('fresh current installation update does not create backup storage', t => {
  const root = fixture(t); install({ host: 'both', project: root });
  const before = tree(root);
  update({ host: 'both', project: root });
  assert.deepEqual(tree(root), before);
});

for (const change of ['edit', 'add', 'delete', 'empty-directory', 'line-endings', 'version-marker']) {
  test(`preserves ${change} and preflights both hosts without touching the clean host`, t => {
    const root = fixture(t); seed(root, 'claude'); seed(root, 'codex');
    const filename = path.join(dest(root, 'codex'), 'SKILL.md');
    if (change === 'edit') fs.appendFileSync(filename, '\nPersonal instructions');
    if (change === 'add') fs.writeFileSync(path.join(dest(root, 'codex'), 'custom.md'), 'keep');
    if (change === 'delete') fs.unlinkSync(filename);
    if (change === 'empty-directory') fs.mkdirSync(path.join(dest(root, 'codex'), 'custom'));
    if (change === 'line-endings') fs.writeFileSync(filename, fs.readFileSync(filename, 'utf8').replace(/\r?\n/g, '\r\n'));
    if (change === 'version-marker') fs.writeFileSync(path.join(dest(root, 'codex'), 'version.json'), '{"version":"0.1.0-alpha.5"}');
    const before = tree(root);
    assert.throws(() => update({ host: 'both', project: root }), /Nothing was updated.*\n.*Modified or unrecognized/);
    assert.deepEqual(tree(root), before);
  });
}

test('missing selected host fails before any update; explicit selector updates the installed one', t => {
  const root = fixture(t); seed(root);
  const before = tree(root);
  assert.throws(() => update({ host: 'both', project: root }), /Missing Skill/);
  assert.deepEqual(tree(root), before);
  update({ host: 'claude', project: root });
  assertCurrent(root);
});

test('unknown newer/customized current payload is never downgraded', t => {
  const root = fixture(t); install({ host: 'claude', project: root });
  fs.appendFileSync(path.join(dest(root), 'SKILL.md'), '\nFuture or custom revision');
  const before = tree(root);
  assert.throws(() => update({ host: 'claude', project: root }), /SKILL.md/);
  assert.deepEqual(tree(root), before);
});

test('current host plus old host retains current host mtimes', t => {
  const root = fixture(t); install({ host: 'claude', project: root }); seed(root, 'codex');
  const before = tree(dest(root));
  assert.deepEqual(update({ host: 'both', project: root }).map(item => item.status), ['unchanged', 'updated']);
  assert.deepEqual(tree(dest(root)), before);
});

test('staging write failure leaves both originals untouched', t => {
  const root = fixture(t); seed(root); seed(root, 'codex');
  const before = [tree(dest(root)), tree(dest(root, 'codex'))];
  const io = { ...fs, openSync() { throw new Error('Injected staging failure'); } };
  assert.throws(() => update({ host: 'both', project: root, io }), /Injected staging failure/);
  assert.deepEqual([tree(dest(root)), tree(dest(root, 'codex'))], before);
});

test('second-host publish failure restores both originals with their mtimes', t => {
  const root = fixture(t); seed(root); seed(root, 'codex');
  const before = [tree(dest(root)), tree(dest(root, 'codex'))];
  const io = { ...fs, renameSync(from, to) {
    if (to === dest(root, 'codex') && from.includes(`${path.sep}.agents${path.sep}`)) throw new Error('Injected second-host failure');
    fs.renameSync(from, to);
  } };
  assert.throws(() => update({ host: 'both', project: root, io }), /Injected second-host failure.*\nMoved originals were restored/);
  assert.deepEqual([tree(dest(root)), tree(dest(root, 'codex'))], before);
});

test('original edit after preflight aborts without overwriting that edit', t => {
  const root = fixture(t); seed(root);
  const filename = path.join(dest(root), 'SKILL.md');
  let injected = false;
  const io = { ...fs, openSync(...args) {
    if (!injected) { injected = true; fs.writeFileSync(filename, 'Concurrent original edit'); }
    return fs.openSync(...args);
  } };
  assert.throws(() => update({ host: 'claude', project: root, io }), /changed after preflight/);
  assert.equal(fs.readFileSync(filename, 'utf8'), 'Concurrent original edit');
});

test('rollback retains concurrent change in installed first host and reports original backup', t => {
  const root = fixture(t); seed(root); seed(root, 'codex');
  const oldSecond = tree(dest(root, 'codex'));
  const io = { ...fs, renameSync(from, to) {
    if (to === dest(root, 'codex') && from.includes(`${path.sep}.agents${path.sep}`)) {
      fs.writeFileSync(path.join(dest(root), 'SKILL.md'), 'Concurrent installed edit');
      throw new Error('Injected concurrency');
    }
    fs.renameSync(from, to);
  } };
  assert.throws(() => update({ host: 'both', project: root, io }), /original backup:/);
  assert.equal(fs.readFileSync(path.join(dest(root), 'SKILL.md'), 'utf8'), 'Concurrent installed edit');
  assert.deepEqual(tree(dest(root, 'codex')), oldSecond);
  const transaction = fs.readdirSync(path.join(root, '.configure-subagents-updates'))[0];
  assert.deepEqual(fs.readFileSync(path.join(root, '.configure-subagents-updates', transaction, 'backups/claude/SKILL.md')), Buffer.from(releases.at(-1).files['SKILL.md'], 'base64'));
});

test('a destination appearing after backup is preserved; original stays in backup', t => {
  const root = fixture(t); seed(root);
  const io = { ...fs, renameSync(from, to) {
    fs.renameSync(from, to);
    if (from === dest(root)) {
      fs.mkdirSync(from);
      fs.writeFileSync(path.join(from, 'other.md'), 'Concurrent owner');
    }
  } };
  assert.throws(() => update({ host: 'claude', project: root, io }), /Destination appeared.*\nConcurrent changes/);
  assert.equal(fs.readFileSync(path.join(dest(root), 'other.md'), 'utf8'), 'Concurrent owner');
});

test('rollback refuses an identical-byte file replacement by another writer', t => {
  const root = fixture(t); seed(root); seed(root, 'codex');
  const filename = path.join(dest(root), 'SKILL.md');
  const io = { ...fs, renameSync(from, to) {
    if (to === dest(root, 'codex') && from.includes(`${path.sep}.agents${path.sep}`)) {
      const saved = path.join(root, 'other-writer-copy');
      fs.renameSync(filename, saved);
      fs.copyFileSync(saved, filename);
      throw new Error('Injected replacement');
    }
    fs.renameSync(from, to);
  } };
  assert.throws(() => update({ host: 'both', project: root, io }), /original backup:/);
  assert.deepEqual(fs.readFileSync(filename), fs.readFileSync(path.join(root, 'other-writer-copy')));
});

test('backup edits are retained and reported rather than restored over a live destination', t => {
  const root = fixture(t); seed(root);
  let backup;
  const io = { ...fs, renameSync(from, to) {
    fs.renameSync(from, to);
    if (from === dest(root)) {
      backup = to;
      fs.writeFileSync(path.join(to, 'SKILL.md'), 'Another writer changed the backup');
    }
  } };
  assert.throws(() => update({ host: 'claude', project: root, io }), /Original changed while moving.*\nConcurrent changes/);
  assert.equal(fs.readFileSync(path.join(backup, 'SKILL.md'), 'utf8'), 'Another writer changed the backup');
});

test('recovery failure keeps recoverable originals and reports their location', t => {
  const root = fixture(t); seed(root); seed(root, 'codex');
  const io = { ...fs, renameSync(from, to) {
    if (to === dest(root, 'codex')) throw Object.assign(new Error('Injected permission denial'), { code: 'EACCES' });
    fs.renameSync(from, to);
  } };
  assert.throws(() => update({ host: 'both', project: root, io }), /original backup:/);
  const transaction = fs.readdirSync(path.join(root, '.configure-subagents-updates'))[0];
  assert.deepEqual(fs.readFileSync(path.join(root, '.configure-subagents-updates', transaction, 'backups/codex/SKILL.md')), Buffer.from(releases.at(-1).files['SKILL.md'], 'base64'));
  assert.deepEqual(fs.readFileSync(path.join(dest(root), 'SKILL.md')), Buffer.from(releases.at(-1).files['SKILL.md'], 'base64'));
});

for (const component of ['.claude', '.claude/skills', '.claude/skills/configure-subagents', '.configure-subagents-updates']) {
  test(`update refuses linked path ${component} without outside writes`, t => {
    const root = fixture(t), outside = fixture(t);
    if (component === '.configure-subagents-updates') seed(root);
    const filename = path.join(root, component);
    fs.mkdirSync(path.dirname(filename), { recursive: true });
    fs.writeFileSync(path.join(outside, 'keep'), 'outside');
    if (!link(t, outside, filename)) return;
    const before = tree(root), outsideBefore = tree(outside);
    assert.throws(() => update({ host: 'claude', project: root }), /Linked/);
    assert.deepEqual(tree(root), before); assert.deepEqual(tree(outside), outsideBefore);
  });
}

test('linked child in existing Skill is refused unchanged', t => {
  const root = fixture(t), outside = fixture(t); seed(root);
  if (!link(t, outside, path.join(dest(root), 'custom-link'))) return;
  const before = tree(root);
  assert.throws(() => update({ host: 'claude', project: root }), /Linked/);
  assert.deepEqual(tree(root), before);
});

test('CLI update supports Korean/space path, all and compatible host selectors', t => {
  const root = fixture(t), project = path.join(root, '한글 project'); fs.mkdirSync(project);
  seed(project); seed(project, 'codex');
  const result = run(root, ['update', '--agent', 'all', '--project', project]);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /^SUCCESS: Skill update completed\.\r?\nCLI version: /);
  assert.equal(result.stderr, '');
  assert.doesNotMatch(result.stdout, /does not verify|ERROR:/);
  assert.equal((result.stdout.match(/^updated:/gm) || []).length, 2);
  assert.match(result.stdout, /backup:/);
  assertCurrent(project); assertCurrent(project, 'codex');
  const before = tree(project);
  const repeated = run(project, ['update', '--host', 'both']);
  assert.equal(repeated.status, 0, repeated.stderr);
  assert.match(repeated.stdout, /^SUCCESS: Skill files already match this version\. No changes needed\./);
  assert.equal(repeated.stderr, '');
  assert.deepEqual(tree(project), before);
});

test('CLI update invalid arguments/help/conflicts have correct exit codes and no changes', t => {
  const root = fixture(t); seed(root);
  const before = tree(root);
  assert.equal(run(root, ['update', '--help']).status, 0);
  for (const args of [[], ['--agent', 'both'], ['--agent', 'all', '--host', 'both'], ['--agent', 'claude', '--force'], ['--project', root]]) {
    const invalid = run(root, ['update', ...args]);
    assert.equal(invalid.status, 2);
    assert.match(invalid.stderr, /^ERROR: Invalid arguments\./);
    assert.equal(invalid.stdout, '');
  }
  const failed = run(root, ['update', '--agent', 'all']);
  assert.equal(failed.status, 1);
  assert.match(failed.stderr, /^ERROR: Skill update failed\./);
  assert.equal(failed.stdout, '');
  assert.deepEqual(tree(root), before);
});

test('CLI mixed update reports completion with per-host outcomes and preserves current host', t => {
  const root = fixture(t);
  install({ host: 'claude', project: root }); seed(root, 'codex');
  const before = tree(dest(root));
  const result = run(root, ['update', '--agent', 'all']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /^SUCCESS: Skill update completed\./);
  assert.equal((result.stdout.match(/^updated:/gm) || []).length, 1);
  assert.equal((result.stdout.match(/^unchanged:/gm) || []).length, 1);
  assert.equal(result.stderr, '');
  assert.deepEqual(tree(dest(root)), before);
  assertCurrent(root, 'codex');
});
