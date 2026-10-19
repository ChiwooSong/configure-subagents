import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { install, packageRoot, skillFiles } from '../lib/install.js';

const cli = path.join(packageRoot, 'bin/configure-subagents.js');
const tempBase = fs.realpathSync(os.tmpdir());

function fixture(t) {
  const root = fs.mkdtempSync(path.join(tempBase, 'configure-subagents-test-'));
  t.after(() => {
    if (!fs.existsSync(root)) return;
    assert.equal(path.dirname(fs.realpathSync(root)), tempBase);
    assert.ok(path.basename(root).startsWith('configure-subagents-test-'));
    assert.equal(fs.lstatSync(root).isSymbolicLink(), false);
    fs.rmSync(root, { recursive: true });
  });
  return root;
}

function destination(root, host = 'claude') {
  return path.join(root, host === 'claude' ? '.claude' : '.agents', 'skills', 'configure-subagents');
}

function snapshot(root) {
  const result = {};
  function walk(dir) {
    for (const entry of fs.readdirSync(dir).sort()) {
      const name = path.join(dir, entry);
      const info = fs.lstatSync(name);
      const key = path.relative(root, name);
      if (info.isSymbolicLink()) result[key] = { link: fs.readlinkSync(name) };
      else if (info.isDirectory()) { result[key] = 'directory'; walk(name); }
      else result[key] = { bytes: fs.readFileSync(name).toString('base64'), mtime: info.mtimeMs };
    }
  }
  walk(root);
  return result;
}

function assertPayload(root, host) {
  for (const name of skillFiles) {
    assert.deepEqual(fs.readFileSync(path.join(destination(root, host), name)), fs.readFileSync(path.join(packageRoot, 'configure-subagents', name)));
  }
}

function run(root, args) {
  const result = spawnSync(process.execPath, [cli, ...args], { cwd: root, encoding: 'utf8' });
  assert.ifError(result.error);
  return result;
}

function linkDirectory(t, target, name) {
  try { fs.symlinkSync(target, name, process.platform === 'win32' ? 'junction' : 'dir'); }
  catch (error) {
    if (error.code === 'EPERM' || error.code === 'EACCES') { t.skip(`Directory links unavailable: ${error.code}`); return false; }
    throw error;
  }
  return true;
}

for (const host of ['claude', 'codex', 'both']) {
  test(`installs exact payload for ${host}, without agent generation`, t => {
    const root = fixture(t);
    fs.writeFileSync(path.join(root, 'keep.txt'), 'existing project data');
    const result = install({ host, project: root });
    const hosts = host === 'both' ? ['claude', 'codex'] : [host];
    assert.deepEqual(result.map(item => item.status), hosts.map(() => 'installed'));
    for (const value of hosts) assertPayload(root, value);
    assert.equal(fs.readFileSync(path.join(root, 'keep.txt'), 'utf8'), 'existing project data');
    assert.equal(fs.existsSync(path.join(root, '.claude', 'agents')), false);
    if (host === 'claude') assert.equal(fs.existsSync(path.join(root, '.agents')), false);
    if (host === 'codex') assert.equal(fs.existsSync(path.join(root, '.claude')), false);
  });
}

test('repeat installation preserves file bytes and mtimes', t => {
  const root = fixture(t);
  install({ host: 'both', project: root });
  const before = snapshot(root);
  const result = install({ host: 'both', project: root });
  assert.deepEqual(result.map(item => item.status), ['unchanged', 'unchanged']);
  assert.deepEqual(snapshot(root), before);
});

test('both preflights conflicts before creating the other host', t => {
  const root = fixture(t);
  const dest = destination(root, 'codex');
  fs.mkdirSync(dest, { recursive: true });
  fs.writeFileSync(path.join(dest, 'SKILL.md'), 'User instructions');
  const before = snapshot(root);
  assert.throws(() => install({ host: 'both', project: root }), /Existing Skill differs/);
  assert.deepEqual(snapshot(root), before);
});

test('extra files and empty directories cause conflicts, without deletion', t => {
  const root = fixture(t);
  install({ host: 'claude', project: root });
  fs.mkdirSync(path.join(destination(root), 'personal-notes'));
  fs.writeFileSync(path.join(destination(root), 'custom.txt'), 'keep');
  const before = snapshot(root);
  assert.throws(() => install({ host: 'claude', project: root }), /differs/);
  assert.deepEqual(snapshot(root), before);
});

test('an identical first host is preserved when installing the missing host', t => {
  const root = fixture(t);
  install({ host: 'claude', project: root });
  const before = snapshot(destination(root));
  assert.deepEqual(install({ host: 'both', project: root }).map(item => item.status), ['unchanged', 'installed']);
  assert.deepEqual(snapshot(destination(root)), before);
});

test('non-directory destination component is rejected unchanged', t => {
  const root = fixture(t);
  fs.writeFileSync(path.join(root, '.claude'), 'not a directory');
  const before = snapshot(root);
  assert.throws(() => install({ host: 'claude', project: root }), /non-directory/);
  assert.deepEqual(snapshot(root), before);
});

for (const component of ['.claude', '.claude/skills', '.claude/skills/configure-subagents']) {
  test(`rejects linked destination ${component} without writing outside`, t => {
    const root = fixture(t);
    const outside = fixture(t);
    fs.writeFileSync(path.join(outside, 'keep.txt'), 'outside data');
    const link = path.join(root, component);
    fs.mkdirSync(path.dirname(link), { recursive: true });
    if (!linkDirectory(t, outside, link)) return;
    const before = snapshot(outside);
    assert.throws(() => install({ host: 'claude', project: root }), /Linked/);
    assert.deepEqual(snapshot(outside), before);
  });
}

test('existing installation with a linked child directory is rejected', t => {
  const root = fixture(t);
  const outside = fixture(t);
  const dest = destination(root);
  fs.mkdirSync(dest, { recursive: true });
  if (!linkDirectory(t, outside, path.join(dest, 'references'))) return;
  assert.throws(() => install({ host: 'claude', project: root }), /Linked installation/);
  assert.deepEqual(snapshot(outside), {});
});

test('missing project or a file as project does not create a destination', t => {
  const root = fixture(t);
  const missing = path.join(root, 'missing');
  assert.throws(() => install({ host: 'claude', project: missing }), /ENOENT/);
  fs.writeFileSync(path.join(root, 'file'), 'data');
  assert.throws(() => install({ host: 'claude', project: path.join(root, 'file') }), /not a directory/);
  assert.deepEqual(fs.readdirSync(root), ['file']);
});

test('midway failure of both rolls back only newly created files', t => {
  const root = fixture(t);
  fs.mkdirSync(path.join(root, '.claude'));
  fs.writeFileSync(path.join(root, '.claude', 'keep.txt'), 'keep');
  const before = snapshot(root);
  const io = { ...fs, openSync(filename, ...args) {
    if (filename.startsWith(destination(root, 'codex') + path.sep)) throw new Error('Injected second-host failure');
    return fs.openSync(filename, ...args);
  } };
  assert.throws(() => install({ host: 'both', project: root, io }), /second-host failure.*\nNew installation files were rolled back/);
  assert.deepEqual(snapshot(root), before);
});

test('rollback does not remove an existing identical installation', t => {
  const root = fixture(t);
  install({ host: 'claude', project: root });
  const before = snapshot(root);
  const io = { ...fs, openSync() { throw new Error('Injected failure'); } };
  assert.throws(() => install({ host: 'both', project: root, io }), /Injected failure/);
  assert.deepEqual(snapshot(root), before);
});

test('rollback retains a concurrently modified file and reports it', t => {
  const root = fixture(t);
  const changed = path.join(destination(root), 'SKILL.md');
  const io = { ...fs, openSync(filename, ...args) {
    if (filename.endsWith(`${path.sep}LICENSE`)) {
      fs.writeFileSync(changed, 'Other writer content');
      throw new Error('Injected write failure');
    }
    return fs.openSync(filename, ...args);
  } };
  assert.throws(() => install({ host: 'claude', project: root, io }), error => {
    assert.match(error.message, /left changed or non-empty paths untouched/);
    assert.ok(error.message.includes(changed));
    return true;
  });
  assert.equal(fs.readFileSync(changed, 'utf8'), 'Other writer content');
});

test('rollback preserves an incomplete write rather than guessing ownership of its contents', t => {
  const root = fixture(t);
  const io = { ...fs, writeFileSync(fd, bytes) {
    fs.writeSync(fd, bytes.subarray(0, 12));
    throw new Error('Injected partial write');
  } };
  assert.throws(() => install({ host: 'claude', project: root, io }), /left changed/);
  assert.deepEqual(fs.readFileSync(path.join(destination(root), 'SKILL.md')), fs.readFileSync(path.join(packageRoot, 'configure-subagents/SKILL.md')).subarray(0, 12));
});

test('rollback preserves a replaced file even if its bytes match', t => {
  const root = fixture(t);
  const original = path.join(destination(root), 'SKILL.md');
  const saved = path.join(root, 'saved-by-other-writer');
  const io = { ...fs, openSync(filename, ...args) {
    if (filename.endsWith(`${path.sep}LICENSE`)) {
      fs.renameSync(original, saved);
      fs.copyFileSync(saved, original);
      throw new Error('Injected replacement');
    }
    return fs.openSync(filename, ...args);
  } };
  assert.throws(() => install({ host: 'claude', project: root, io }), /left changed/);
  assert.deepEqual(fs.readFileSync(original), fs.readFileSync(saved));
});

test('a destination created after preflight is not overwritten', t => {
  const root = fixture(t);
  const dest = destination(root);
  let checks = 0;
  const io = { ...fs, lstatSync(filename, ...args) {
    if (filename === dest && ++checks === 3) {
      fs.mkdirSync(dest, { recursive: true });
      fs.writeFileSync(path.join(dest, 'other.txt'), 'concurrent writer');
    }
    return fs.lstatSync(filename, ...args);
  } };
  assert.throws(() => install({ host: 'claude', project: root, io }), /appeared after preflight/);
  assert.equal(fs.readFileSync(path.join(dest, 'other.txt'), 'utf8'), 'concurrent writer');
  assert.deepEqual(fs.readdirSync(dest), ['other.txt']);
});

test('CLI supports Unicode/space paths and defaults to cwd', t => {
  const root = fixture(t);
  const project = path.join(root, '한글 프로젝트');
  fs.mkdirSync(project);
  const result = run(root, ['install', '--host', 'both', '--project', project]);
  assert.equal(result.status, 0, result.stderr);
  assertPayload(project, 'claude');
  assertPayload(project, 'codex');
  const other = fixture(t);
  const defaultResult = run(other, ['install', '--host', 'claude']);
  assert.equal(defaultResult.status, 0, defaultResult.stderr);
  assertPayload(other, 'claude');
});

test('CLI help, version, and empty invocation do not write files', t => {
  const root = fixture(t);
  for (const args of [[], ['--help'], ['-h'], ['--version'], ['-v'], ['install', '--help']]) {
    const result = run(root, args);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(result.stdout.trim());
    assert.deepEqual(snapshot(root), {});
  }
});

for (const agent of ['claude', 'codex', 'all']) {
  test(`CLI --agent ${agent} installs only the selected hosts and interoperates with --host`, t => {
    const root = fixture(t);
    const result = run(root, ['install', '--agent', agent]);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /^SUCCESS: Skill installation completed\.\r?\nCLI version: /);
    assert.equal(result.stderr, '');
    assert.doesNotMatch(result.stdout, /does not verify|ERROR:/);
    assert.equal(result.stdout.includes('Next: In Claude Code,'), agent !== 'codex');
    assert.equal(result.stdout.includes('Next: In Codex,'), agent !== 'claude');
    for (const host of ['claude', 'codex']) {
      if (agent === 'all' || agent === host) assertPayload(root, host);
      else assert.equal(fs.existsSync(destination(root, host)), false);
    }
    const before = snapshot(root);
    const repeated = run(root, ['install', '--host', agent === 'all' ? 'both' : agent]);
    assert.equal(repeated.status, 0, repeated.stderr);
    assert.match(repeated.stdout, /^SUCCESS: Skill files already match this version\. No changes needed\./);
    assert.equal(repeated.stderr, '');
    assert.match(repeated.stdout, /unchanged:/);
    assert.deepEqual(snapshot(root), before);
  });
}

test('CLI --agent all preflights both destinations without overwriting custom content', t => {
  const root = fixture(t);
  fs.mkdirSync(destination(root, 'codex'), { recursive: true });
  fs.writeFileSync(path.join(destination(root, 'codex'), 'SKILL.md'), 'custom Skill');
  const before = snapshot(root);
  const result = run(root, ['install', '--agent', 'all']);
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /^ERROR: Skill installation failed\./);
  assert.equal(result.stdout, '');
  assert.deepEqual(snapshot(root), before);
});

test('CLI rejects missing, unknown, and duplicate arguments without changes', t => {
  const root = fixture(t);
  for (const args of [
    ['install'], ['install', '--host'], ['install', '--host', 'invalid'], ['--force'],
    ['install', '--host', 'claude', '--force'], ['install', '--host', 'claude', '--project'],
    ['install', '--host', 'claude', '--host', 'codex'],
    ['install', '--host', 'claude', '--project', root, '--project', root],
    ['install', '--agent'], ['install', '--agent', 'both'],
    ['install', '--agent', 'all', '--agent', 'all'],
    ['install', '--agent', 'all', '--host', 'both'],
    ['install', '--host', 'codex', '--agent', 'claude'],
  ]) {
    const result = run(root, args);
    assert.equal(result.status, 2, `${args}: ${result.stderr}`);
    assert.match(result.stderr, /^ERROR: Invalid arguments\./);
    assert.equal(result.stdout, '');
    assert.deepEqual(snapshot(root), {});
  }
});

test('CLI filesystem conflicts return code 1', t => {
  const root = fixture(t);
  fs.mkdirSync(destination(root), { recursive: true });
  fs.writeFileSync(path.join(destination(root), 'SKILL.md'), 'existing');
  const before = snapshot(root);
  const result = run(root, ['install', '--host', 'claude']);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /^ERROR: Skill installation failed\./);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /differs/);
  assert.deepEqual(snapshot(root), before);
});

test('CLI partial install reports completion while distinguishing unchanged and installed hosts', t => {
  const root = fixture(t);
  install({ host: 'claude', project: root });
  const before = snapshot(destination(root));
  const result = run(root, ['install', '--agent', 'all']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /^SUCCESS: Skill installation completed\./);
  assert.equal((result.stdout.match(/^installed:/gm) || []).length, 1);
  assert.equal((result.stdout.match(/^unchanged:/gm) || []).length, 1);
  assert.equal(result.stderr, '');
  assert.deepEqual(snapshot(destination(root)), before);
  assertPayload(root, 'codex');
});
