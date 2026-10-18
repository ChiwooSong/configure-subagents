import fs from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { checkParents, install, maybeStat, packageRoot, sameIdentity, skillFiles } from './install.js';

const releases = JSON.parse(fs.readFileSync(new URL('./released-skills.json', import.meta.url), 'utf8'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

function fingerprint(files) {
  const entries = new Map();
  for (const [name, digest] of Object.entries(files)) {
    entries.set(name, digest);
    let parent = path.posix.dirname(name);
    while (parent !== '.') {
      entries.set(`${parent}/`, null);
      parent = path.posix.dirname(parent);
    }
  }
  return entries;
}

// Snapshot the entire tree, including empty/extra directories and file identities.
// Never trust a version marker supplied by the installed (possibly edited) Skill.
function snapshot(io, directory) {
  const entries = new Map();
  function visit(filename, relative) {
    const info = io.lstatSync(filename);
    if (info.isSymbolicLink() || (!info.isDirectory() && !info.isFile())) {
      throw new Error(`Linked or unsupported Skill entry: ${filename}`);
    }
    const key = info.isDirectory() && relative ? `${relative}/` : relative;
    entries.set(key, {
      dev: info.dev, ino: info.ino, mtimeMs: info.mtimeMs, mode: info.mode,
      hash: info.isFile() ? hash(io.readFileSync(filename)) : null,
    });
    if (info.isDirectory()) {
      for (const name of io.readdirSync(filename).sort()) visit(path.join(filename, name), relative ? `${relative}/${name}` : name);
    }
  }
  visit(directory, '');
  return entries;
}

function differences(observed, expected) {
  return [...new Set([...observed.keys(), ...expected.keys()])]
    .filter(name => name !== '' && (!observed.has(name) || !expected.has(name) || observed.get(name).hash !== expected.get(name)))
    .sort();
}

function sameSnapshot(left, right) {
  return left.size === right.size && [...left].every(([name, info]) => JSON.stringify(info) === JSON.stringify(right.get(name)));
}

/** Upgrade only whole trees matching the bundled, verified release fingerprints.
 * io injection is for fault/concurrency tests, not a CLI option.
 * No network, code execution, recursive deletion, or project Agent edits.
 */
export function update({ host, project = process.cwd(), io = fs }) {
  if (!['claude', 'codex', 'both'].includes(host)) throw new Error('host must be claude, codex, or both');
  const root = io.realpathSync(path.resolve(project));
  const rootStat = io.lstatSync(root);
  if (!rootStat.isDirectory()) throw new Error(`Project is not a directory: ${root}`);
  const current = fingerprint(Object.fromEntries(skillFiles.map(name => [name, hash(io.readFileSync(path.join(packageRoot, 'configure-subagents', name)))])));
  const known = releases.map(release => ({ ...release, entries: fingerprint(release.files) }));
  const hosts = host === 'both' ? ['claude', 'codex'] : [host];
  const targets = hosts.map(value => ({
    host: value,
    directory: path.join(root, value === 'claude' ? '.claude' : '.agents', 'skills/configure-subagents'),
  }));

  // All selected hosts must pass before creating even a staging directory.
  const conflicts = [];
  for (const target of targets) {
    checkParents(io, root, target.directory, rootStat);
    if (!maybeStat(io, target.directory)) {
      conflicts.push(`Missing Skill; use install first: ${target.directory}`);
      continue;
    }
    target.before = snapshot(io, target.directory);
    if (!differences(target.before, current).length) {
      target.status = 'unchanged';
      continue;
    }
    const previous = known.filter(release => !differences(target.before, release.entries).length);
    if (previous.length) {
      target.fromVersion = previous.map(release => release.version).join(' / ');
      target.status = 'updated';
    } else {
      const closest = [current, ...known.map(release => release.entries)]
        .map(entries => differences(target.before, entries)).sort((a, b) => a.length - b.length)[0];
      conflicts.push(`Modified or unrecognized Skill: ${target.directory}\nReview these differing paths (nearest known payload):\n${closest.map(name => `  ${name}`).join('\n')}`);
    }
  }
  if (conflicts.length) throw new Error(`Nothing was updated. User content was preserved.\n${conflicts.join('\n')}\nInstall into a separate temporary project and merge custom changes manually; there is no force option.`);
  const pending = targets.filter(target => target.status === 'updated');
  if (!pending.length) return targets.map(({ host: value, directory, status }) => ({ host: value, directory, status }));

  // Same-filesystem staging and backups, outside both host discovery trees.
  const storage = path.join(root, '.configure-subagents-updates');
  checkParents(io, root, storage, rootStat);
  if (!maybeStat(io, storage)) io.mkdirSync(storage);
  checkParents(io, root, storage, rootStat);
  const transaction = path.join(storage, randomUUID());
  io.mkdirSync(transaction);
  const transactionStat = io.lstatSync(transaction);
  const guard = target => {
    checkParents(io, root, target, rootStat);
    if (!sameIdentity(io.lstatSync(transaction), transactionStat)) throw new Error(`Update staging directory changed: ${transaction}`);
  };
  try {
    guard(transaction);
    io.mkdirSync(path.join(transaction, 'backups'));
    io.mkdirSync(path.join(transaction, 'withdrawn'));
    for (const target of pending) {
      guard(transaction);
      install({ host: target.host, project: transaction, io });
      target.staged = path.join(transaction, target.host === 'claude' ? '.claude' : '.agents', 'skills/configure-subagents');
      target.ready = snapshot(io, target.staged);
      if (differences(target.ready, current).length) throw new Error(`Package payload changed during staging: ${target.staged}`);
      target.backup = path.join(transaction, 'backups', target.host);
    }
    for (const target of pending) {
      guard(target.directory);
      guard(target.staged);
      guard(path.dirname(target.backup));
      if (!sameSnapshot(snapshot(io, target.directory), target.before) || !sameSnapshot(snapshot(io, target.staged), target.ready)) {
        throw new Error(`Skill changed after preflight: ${target.directory}`);
      }
      if (maybeStat(io, target.backup)) throw new Error(`Backup destination appeared: ${target.backup}`);
      io.renameSync(target.directory, target.backup);
      target.moved = true;
      guard(target.backup);
      if (!sameSnapshot(snapshot(io, target.backup), target.before)) throw new Error(`Original changed while moving to backup: ${target.backup}`);
      guard(target.directory);
      guard(target.staged);
      if (maybeStat(io, target.directory)) throw new Error(`Destination appeared during update: ${target.directory}`);
      io.renameSync(target.staged, target.directory);
      target.published = true;
    }
    for (const target of targets) {
      guard(target.directory);
      if (!sameSnapshot(snapshot(io, target.directory), target.ready || target.before)) throw new Error(`Skill changed during update: ${target.directory}`);
      if (target.moved) {
        guard(target.backup);
        if (!sameSnapshot(snapshot(io, target.backup), target.before)) throw new Error(`Original backup changed during update: ${target.backup}`);
      }
    }
    return targets.map(({ host: value, directory, status, fromVersion, backup }) => ({ host: value, directory, status, fromVersion, backup }));
  } catch (error) {
    const retained = [];
    for (const target of [...pending].reverse()) {
      if (!target.moved) continue;
      try {
        guard(target.directory);
        guard(target.backup);
        if (target.published) {
          if (!sameSnapshot(snapshot(io, target.directory), target.ready)) throw new Error('Concurrent change to installed Skill');
          const withdrawn = path.join(transaction, 'withdrawn', target.host);
          guard(path.dirname(withdrawn));
          if (maybeStat(io, withdrawn)) throw new Error('Recovery destination appeared');
          io.renameSync(target.directory, withdrawn);
        }
        if (maybeStat(io, target.directory)) throw new Error('Concurrent destination');
        if (!sameSnapshot(snapshot(io, target.backup), target.before)) throw new Error('Backup changed');
        io.renameSync(target.backup, target.directory);
      } catch {
        retained.push(`${target.directory} (original backup: ${target.backup})`);
      }
    }
    const recovery = retained.length
      ? `Concurrent changes or recovery errors were preserved; inspect:\n${retained.join('\n')}`
      : 'Moved originals were restored; changes by other writers were not overwritten.';
    throw new Error(`${error.message}\n${recovery}\nRecovery/staging files retained outside Skill discovery: ${transaction}`, { cause: error });
  }
}
