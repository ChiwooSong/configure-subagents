// Offline tarball smoke test. Run via npm run test:package (sets npm_execpath).
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { packageRoot, skillFiles } from '../lib/install.js';

const npmCli = process.env.npm_execpath;
assert.ok(npmCli && fs.existsSync(npmCli), 'Run this check with npm run test:package.');
const tempBase = fs.realpathSync(os.tmpdir());
const temp = fs.mkdtempSync(path.join(tempBase, 'configure-subagents-package-'));

function execute(command, args, cwd = packageRoot) {
  const result = spawnSync(command, args, { cwd, encoding: 'utf8', timeout: 60000 });
  assert.ifError(result.error);
  assert.equal(result.status, 0, `${command}: ${result.stdout}\n${result.stderr}`);
  return result.stdout;
}

try {
  const packed = JSON.parse(execute(process.execPath, [npmCli, 'pack', '--json', '--ignore-scripts', '--offline', '--pack-destination', temp]));
  assert.equal(packed.length, 1);
  const expected = [
    'package.json', 'README.md', 'LICENSE', 'bin/configure-subagents.js', 'lib/install.js', 'lib/update.js', 'lib/released-skills.json',
    ...skillFiles.map(name => `configure-subagents/${name}`),
  ].sort();
  assert.deepEqual(packed[0].files.map(entry => entry.path).sort(), expected, 'Tarball must match the explicit distributable file list.');
  const filename = packed[0].filename;
  assert.equal(path.basename(filename), filename);
  const tarball = path.join(temp, filename);
  assert.ok(fs.statSync(tarball).size > 0);

  const consumer = path.join(temp, 'consumer');
  fs.mkdirSync(consumer);
  fs.writeFileSync(path.join(consumer, 'package.json'), '{"name":"local-package-test","version":"0.0.0","private":true}\n');
  execute(process.execPath, [npmCli, 'install', '--offline', '--ignore-scripts', '--no-audit', '--no-fund', '--package-lock=false', tarball], consumer);
  const installed = path.join(consumer, 'node_modules', ...packed[0].name.split('/'));
  const project = path.join(temp, '한글 target project');
  fs.mkdirSync(project);
  const script = path.join(installed, 'bin', 'configure-subagents.js');
  const output = execute(process.execPath, [script, 'install', '--agent', 'all', '--project', project]);
  assert.equal((output.match(/^installed:/gm) || []).length, 2);
  const before = [];
  for (const host of ['.claude', '.agents']) {
    for (const name of skillFiles) {
      const target = path.join(project, host, 'skills/configure-subagents', name);
      const original = fs.readFileSync(path.join(packageRoot, 'configure-subagents', name));
      assert.deepEqual(fs.readFileSync(target), original, `Tarball payload differs: ${name}`);
      before.push([target, fs.statSync(target).mtimeMs, original]);
    }
  }
  const repeated = execute(process.execPath, [script, 'install', '--host', 'both', '--project', project]);
  assert.equal((repeated.match(/^unchanged:/gm) || []).length, 2);
  for (const [filename, mtime, bytes] of before) {
    assert.equal(fs.statSync(filename).mtimeMs, mtime);
    assert.deepEqual(fs.readFileSync(filename), bytes);
  }
  const oldProject = path.join(temp, 'old 한글 project');
  fs.mkdirSync(oldProject);
  const old = JSON.parse(fs.readFileSync(path.join(packageRoot, 'tests/fixtures/released-skills.json'), 'utf8')).at(-1);
  for (const host of ['.claude', '.agents']) {
    for (const [name, data] of Object.entries(old.files)) {
      const filename = path.join(oldProject, host, 'skills/configure-subagents', name);
      fs.mkdirSync(path.dirname(filename), { recursive: true });
      fs.writeFileSync(filename, Buffer.from(data, 'base64'));
    }
  }
  fs.mkdirSync(path.join(oldProject, '.claude/agents'));
  const agent = path.join(oldProject, '.claude/agents/custom.md');
  fs.writeFileSync(agent, 'Keep existing agent\r\n');
  const agentMtime = fs.statSync(agent).mtimeMs;
  const updated = execute(process.execPath, [script, 'update', '--agent', 'all', '--project', oldProject]);
  assert.equal((updated.match(/^updated:/gm) || []).length, 2);
  const updatedBefore = [];
  for (const host of ['.claude', '.agents']) {
    for (const name of skillFiles) {
      const filename = path.join(oldProject, host, 'skills/configure-subagents', name);
      const bytes = fs.readFileSync(path.join(packageRoot, 'configure-subagents', name));
      assert.deepEqual(fs.readFileSync(filename), bytes);
      updatedBefore.push([filename, bytes, fs.statSync(filename).mtimeMs]);
    }
  }
  assert.equal(fs.readFileSync(agent, 'utf8'), 'Keep existing agent\r\n');
  assert.equal(fs.statSync(agent).mtimeMs, agentMtime);
  const noUpdate = execute(process.execPath, [script, 'update', '--host', 'both', '--project', oldProject]);
  assert.equal((noUpdate.match(/^unchanged:/gm) || []).length, 2);
  for (const [filename, bytes, mtime] of updatedBefore) {
    assert.deepEqual(fs.readFileSync(filename), bytes);
    assert.equal(fs.statSync(filename).mtimeMs, mtime);
  }
  const metadata = JSON.parse(fs.readFileSync(path.join(installed, 'package.json'), 'utf8'));
  assert.equal(metadata.name, '@woody_s/configure-subagents');
  assert.equal(metadata.license, 'MIT');
  assert.equal(metadata.publishConfig.tag, 'next');
  assert.equal(fs.readFileSync(path.join(installed, 'LICENSE'), 'utf8'), fs.readFileSync(path.join(packageRoot, 'LICENSE'), 'utf8'));
  assert.equal(execute(process.execPath, [script, '--version']).trim(), metadata.version);
  console.log(`Offline tarball verified: ${packed[0].files.length} allowlisted files; both hosts installed and updated from alpha.5; repeats and project agents preserved.`);
} finally {
  assert.equal(path.dirname(fs.realpathSync(temp)), tempBase);
  assert.ok(path.basename(temp).startsWith('configure-subagents-package-'));
  assert.equal(fs.lstatSync(temp).isSymbolicLink(), false);
  fs.rmSync(temp, { recursive: true });
}
