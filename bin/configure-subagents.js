#!/usr/bin/env node
import fs from 'node:fs';
import { install } from '../lib/install.js';

const metadata = JSON.parse(fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const help = `configure-subagents ${metadata.version}

Install the project-aware Skill for Claude Code or Codex.

Usage:
  configure-subagents install --host claude|codex|both [--project <directory>]
  configure-subagents --help
  configure-subagents --version

The project defaults to the current directory and must exist.
Identical installations are unchanged; differing installations are never overwritten.
No model calls, agent generation, global setup, or Python dependency installation.
`;

function parse(argv) {
  if (!argv.length || (argv.length === 1 && ['--help', '-h'].includes(argv[0]))) return { action: 'help' };
  if (argv.length === 1 && ['--version', '-v'].includes(argv[0])) return { action: 'version' };
  if (argv[0] !== 'install') throw new Error('Expected install, --help, or --version.');
  if (argv.length === 2 && ['--help', '-h'].includes(argv[1])) return { action: 'help' };
  const options = { action: 'install' };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!['--host', '--project'].includes(key) || !value || value.startsWith('--')) throw new Error(`Invalid option or missing value: ${key}`);
    const name = key.slice(2);
    if (Object.hasOwn(options, name)) throw new Error(`Duplicate option: ${key}`);
    options[name] = value;
  }
  if (!['claude', 'codex', 'both'].includes(options.host)) throw new Error('--host must be claude, codex, or both.');
  return options;
}

let options;
try { options = parse(process.argv.slice(2)); }
catch (error) { console.error(error.message); process.exitCode = 2; }
if (options?.action === 'help') console.log(help);
else if (options?.action === 'version') console.log(metadata.version);
else if (options) {
  try {
    if (Number(process.versions.node.split('.')[0]) < 22) throw new Error('Node.js 22 or later is required.');
    for (const item of install(options)) console.log(`${item.status}: ${item.directory}`);
    console.log('Invoke the Skill in your selected host. Installation does not verify host discovery or agent execution.');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
