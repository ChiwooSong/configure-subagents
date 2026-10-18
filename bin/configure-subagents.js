#!/usr/bin/env node
import fs from 'node:fs';
import { install } from '../lib/install.js';
import { update } from '../lib/update.js';

const metadata = JSON.parse(fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const help = `${metadata.name} ${metadata.version}

Install the project-aware Skill for Claude Code or Codex.

Usage:
  configure-subagents install --agent claude|codex|all [--project <directory>]
  configure-subagents install --host claude|codex|both [--project <directory>]
  configure-subagents update --agent claude|codex|all [--project <directory>]
  configure-subagents update --host claude|codex|both [--project <directory>]
  configure-subagents --help
  configure-subagents --version

The project defaults to the current directory and must exist.
Use either --agent or the compatible --host option, not both.
--agent all installs for both Claude Code and Codex.
Identical installations are unchanged; differing installations are never overwritten.
Use update for recognized, unmodified older releases. Modified or unknown Skills are preserved.
Update preflights all selected hosts and keeps backups in .configure-subagents-updates/.
Project .claude/agents files are never changed by install or update.
No model calls, agent generation, global setup, or Python dependency installation.
`;

function parse(argv) {
  if (!argv.length || (argv.length === 1 && ['--help', '-h'].includes(argv[0]))) return { action: 'help' };
  if (argv.length === 1 && ['--version', '-v'].includes(argv[0])) return { action: 'version' };
  if (!['install', 'update'].includes(argv[0])) throw new Error('Expected install, update, --help, or --version.');
  if (argv.length === 2 && ['--help', '-h'].includes(argv[1])) return { action: 'help' };
  const options = { action: argv[0] };
  for (let index = 1; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!['--agent', '--host', '--project'].includes(key) || !value || value.startsWith('--')) throw new Error(`Invalid option or missing value: ${key}`);
    const name = key.slice(2);
    if (Object.hasOwn(options, name)) throw new Error(`Duplicate option: ${key}`);
    options[name] = value;
  }
  if (options.agent !== undefined && options.host !== undefined) throw new Error('Use either --agent or --host, not both.');
  if (options.agent !== undefined) {
    if (!['claude', 'codex', 'all'].includes(options.agent)) throw new Error('--agent must be claude, codex, or all.');
    options.host = options.agent === 'all' ? 'both' : options.agent;
    delete options.agent;
  }
  if (!['claude', 'codex', 'both'].includes(options.host)) throw new Error('Specify --agent claude|codex|all or --host claude|codex|both.');
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
    for (const item of (options.action === 'update' ? update : install)(options)) {
      console.log(`${item.status}: ${item.directory}`);
      if (item.backup) console.log(`  matched previous payload: ${item.fromVersion}; backup: ${item.backup}`);
    }
    console.log('Invoke the Skill in your selected host. Installation does not verify host discovery or agent execution.');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
