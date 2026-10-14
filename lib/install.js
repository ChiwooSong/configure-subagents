import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const packageRoot = fileURLToPath(new URL('../', import.meta.url));
export const skillFiles = [
  'SKILL.md', 'LICENSE', 'requirements.txt',
  'references/project-analysis.md', 'references/role-and-model-selection.md',
  'references/claude-code.md', 'references/host-usage.md',
  'scripts/validate_agents.py',
];

function sameIdentity(a, b) {
  return a.dev === b.dev && a.ino === b.ino;
}

function maybeStat(io, filename) {
  try { return io.lstatSync(filename); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

function directoriesTo(root, target) {
  const relative = path.relative(root, target);
  if (relative.startsWith(`..${path.sep}`) || relative === '..' || path.isAbsolute(relative)) {
    throw new Error(`Destination is outside the project: ${target}`);
  }
  const result = [];
  let current = root;
  for (const part of relative.split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    result.push(current);
  }
  return result;
}

function checkParents(io, root, target, rootStat) {
  const currentRoot = io.lstatSync(root);
  if (!currentRoot.isDirectory() || !sameIdentity(currentRoot, rootStat) || io.realpathSync(root) !== root) {
    throw new Error(`Project directory changed during installation: ${root}`);
  }
  for (const dir of directoriesTo(root, target)) {
    const info = maybeStat(io, dir);
    if (!info) continue;
    if (info.isSymbolicLink() || !info.isDirectory() || io.realpathSync(dir) !== dir) {
      throw new Error(`Linked or non-directory destination component: ${dir}`);
    }
  }
}

function expectedEntries(payload) {
  const entries = new Map();
  for (const [name, bytes] of payload) {
    entries.set(name, bytes);
    let parent = path.posix.dirname(name);
    while (parent !== '.') {
      entries.set(`${parent}/`, null);
      parent = path.posix.dirname(parent);
    }
  }
  return entries;
}

function matches(io, directory, expected) {
  const observed = new Map();
  function visit(dir, prefix = '') {
    for (const name of io.readdirSync(dir)) {
      const filename = path.join(dir, name);
      const relative = prefix + name;
      const info = io.lstatSync(filename);
      if (info.isSymbolicLink()) throw new Error(`Linked installation entry: ${filename}`);
      if (info.isDirectory()) {
        observed.set(`${relative}/`, null);
        visit(filename, `${relative}/`);
      } else if (info.isFile()) {
        observed.set(relative, io.readFileSync(filename));
      } else throw new Error(`Unsupported installation entry: ${filename}`);
    }
  }
  visit(directory);
  if (observed.size !== expected.size) return false;
  for (const [name, bytes] of expected) {
    if (!observed.has(name)) return false;
    const actual = observed.get(name);
    if (bytes === null ? actual !== null : !Buffer.isBuffer(actual) || !bytes.equals(actual)) return false;
  }
  return true;
}

/** Local synchronous installer. io is injectable only for deterministic fault tests. */
export function install({ host, project = process.cwd(), io = fs }) {
  if (!['claude', 'codex', 'both'].includes(host)) throw new Error('host must be claude, codex, or both');
  const root = io.realpathSync(path.resolve(project));
  const rootStat = io.lstatSync(root);
  if (!rootStat.isDirectory()) throw new Error(`Project is not a directory: ${root}`);
  const payload = new Map(skillFiles.map(name => [name, io.readFileSync(path.join(packageRoot, 'configure-subagents', name))]));
  const expected = expectedEntries(payload);
  const hosts = host === 'both' ? ['claude', 'codex'] : [host];
  const destinations = hosts.map(value => ({
    host: value,
    directory: path.join(root, value === 'claude' ? '.claude' : '.agents', 'skills', 'configure-subagents'),
  }));

  // Preflight every destination before creating any directory.
  for (const dest of destinations) {
    checkParents(io, root, dest.directory, rootStat);
    dest.existed = Boolean(maybeStat(io, dest.directory));
    if (dest.existed && !matches(io, dest.directory, expected)) {
      throw new Error(`Existing Skill differs; nothing was installed. Compare it manually: ${dest.directory}`);
    }
  }

  const createdFiles = [];
  const createdDirs = [];
  try {
    for (const dest of destinations) {
      checkParents(io, root, dest.directory, rootStat);
      if (dest.existed) {
        if (!matches(io, dest.directory, expected)) throw new Error(`Installation changed after preflight: ${dest.directory}`);
        dest.status = 'unchanged';
        continue;
      }
      if (maybeStat(io, dest.directory)) throw new Error(`Destination appeared after preflight: ${dest.directory}`);
      const required = new Set(directoriesTo(root, dest.directory));
      for (const name of payload.keys()) {
        for (const dir of directoriesTo(root, path.dirname(path.join(dest.directory, name)))) required.add(dir);
      }
      for (const dir of required) {
        checkParents(io, root, path.dirname(dir), rootStat);
        const existing = maybeStat(io, dir);
        if (existing) {
          if (dir === dest.directory) throw new Error(`Destination appeared during installation: ${dir}`);
          checkParents(io, root, dir, rootStat);
          continue;
        }
        io.mkdirSync(dir); // Exclusive: a concurrently created destination causes a failure.
        createdDirs.push({ path: dir, stat: io.lstatSync(dir) });
      }
      for (const [name, bytes] of payload) {
        const filename = path.join(dest.directory, name);
        checkParents(io, root, path.dirname(filename), rootStat);
        const fd = io.openSync(filename, 'wx');
        const record = { path: filename, stat: io.fstatSync(fd), bytes: Buffer.alloc(0) };
        createdFiles.push(record);
        try {
          io.writeFileSync(fd, bytes);
          record.bytes = bytes;
        } finally { io.closeSync(fd); }
      }
      checkParents(io, root, dest.directory, rootStat);
      if (!matches(io, dest.directory, expected)) throw new Error(`Post-install verification failed: ${dest.directory}`);
      dest.status = 'installed';
    }
    return destinations.map(({ host: value, directory, status }) => ({ host: value, directory, status }));
  } catch (error) {
    const retained = [];
    for (const record of createdFiles.reverse()) {
      try {
        checkParents(io, root, path.dirname(record.path), rootStat);
        const current = maybeStat(io, record.path);
        if (!current) continue;
        if (!current.isFile() || !sameIdentity(current, record.stat) || !io.readFileSync(record.path).equals(record.bytes)) {
          retained.push(record.path);
          continue;
        }
        io.unlinkSync(record.path);
      } catch { retained.push(record.path); }
    }
    for (const record of createdDirs.reverse()) {
      try {
        checkParents(io, root, record.path, rootStat);
        const current = maybeStat(io, record.path);
        if (current && sameIdentity(current, record.stat)) io.rmdirSync(record.path); // Empty only; never recursive.
      } catch { retained.push(record.path); }
    }
    const detail = retained.length ? `\nRecovery left changed or non-empty paths untouched:\n${[...new Set(retained)].join('\n')}` : '\nNew installation files were rolled back.';
    throw new Error(`${error.message}${detail}`, { cause: error });
  }
}
