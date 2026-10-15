#!/usr/bin/env python3
"""Opt-in, sequential sparse-project / growth / repetition host evaluation.

Uses isolated projects and records external snapshots. Mechanical checks are
not semantic passes: inspect the host trace and final response independently.
"""
import argparse
import json
from pathlib import Path

import evaluate_hosts as base


INITIAL_AGENT = """---
name: reviewer
description: Review the wording of project documentation.
# Preserve this integration comment.
tools: Read, Glob, Grep
model: inherit
integrationTag: lifecycle-v1
---

Review documentation wording and clarity.
Report findings with file paths and evidence.
Use the team's severity labels: blocking, caution, note.
Do not edit files or run commands.
"""
USER_NOTE = "Preserve terminology from glossary.md; do not silently rename domain terms."
GROWTH = {
    "README.md": "# Order pipeline\nThe project now has an API and an independently deployed worker. Both consume shared/events.py. Review omissions have repeatedly broken event compatibility.\n",
    "WORKFLOW.md": "# Change workflow\nShared event changes require review of API production and worker consumption, including optional-field defaults and backward compatibility. This is recurring review work. Tests are declared as python -m unittest discover -s tests. Test existence does not prove they pass. Keep all existing custom reviewer reporting instructions.\n",
    "glossary.md": "# Domain terms\nAn order_id identifies an order; an event_version identifies the shared contract version.\n",
    "shared/events.py": "REQUIRED_FIELDS = ('order_id', 'event_version')\n",
    "services/api/handler.py": "def submit(order_id):\n    return {'order_id': order_id, 'event_version': 1}\n",
    "services/worker/worker.py": "def process(event):\n    return event['order_id'], event.get('event_version', 1)\n",
    "tests/test_worker.py": "import unittest\nfrom services.worker.worker import process\n\nclass WorkerTests(unittest.TestCase):\n    def test_legacy_default(self):\n        self.assertEqual(process({'order_id': 'a'}), ('a', 1))\n",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=('claude', 'codex'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--phase', required=True, choices=('initial', 'growth', 'repeat'))
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--windows-sandbox', choices=('elevated', 'unelevated'),
                        help='Use the already-configured Windows sandbox backend; workspace-write remains enforced.')
    parser.add_argument('--allow-static-validator', action='store_true',
                        help='Allow only this evaluation copy of the checker through Claude Bash command rules.')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / f'{args.host}-state.json'
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding='utf-8'))
    else:
        if args.phase != 'initial':
            parser.error('Start with initial in a fresh output directory.')
        state = base.prepare(args.host, output)
        project = Path(state['root']) / 'projects/lifecycle'
        project.mkdir()
        (project / 'README.md').write_text('# New project\nA local tool is being explored. Scope and recurring workflows are not decided.\n', encoding='utf-8')
        (project / '.claude/agents').mkdir(parents=True)
        (project / '.claude/agents/reviewer.md').write_text(INITIAL_AGENT, encoding='utf-8')
        (project / 'personal-notes.txt').write_text('Unrelated user notes: retain exactly.\n', encoding='utf-8')
    if args.windows_sandbox:
        if state.get('windows_sandbox') not in (None, args.windows_sandbox):
            parser.error('Do not change sandbox backend within one evaluation output.')
        state['windows_sandbox'] = args.windows_sandbox
        state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
    if args.allow_static_validator:
        state['allow_static_validator'] = True
        state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
    current_hashes = {str(p.relative_to(base.PACKAGE)): base.digest(p) for p in base.PACKAGE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if current_hashes != state['package_hashes']:
        parser.error('Skill changed since preparation; use a fresh evaluation output.')
    root = Path(state['root'])
    project = root / 'projects/lifecycle'
    agent_path = project / '.claude/agents/reviewer.md'
    if args.phase == 'growth' and not state.get('growth_prepared'):
        initial = output / f'{args.host}-initial-evidence.json'
        if not initial.exists():
            parser.error('Run and review initial before preparing growth.')
        previous = json.loads(initial.read_text(encoding='utf-8'))
        if previous.get('status') != 'finished':
            parser.error('Initial host run did not finish; resolve the blocker first.')
        before = base.snapshot(project)
        for relative, content in GROWTH.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
        with agent_path.open('a', encoding='utf-8') as f:
            f.write('\n' + USER_NOTE + '\n')
        state['growth_prepared'] = True
        state_path.write_text(json.dumps(state, indent=2), encoding='utf-8')
        (output / f'{args.host}-fixture-transition.json').write_text(json.dumps({'before': before, 'after': base.snapshot(project)}, indent=2), encoding='utf-8')
    if args.phase == 'repeat' and not (output / f'{args.host}-growth-evidence.json').exists():
        parser.error('Run and review growth before repeat.')
    invocation = '/configure-subagents' if args.host == 'claude' else '$configure-subagents'
    prompt = (f'{invocation}\nUse the installed Skill for projects/lifecycle. Work only within {root}. '
              'Do not delegate, invoke generated agents, read personal/global settings, install dependencies, or run project code. '
              'This restriction does not prevent running the Skill static validator. Respond in Korean. '
              'The existing reviewer name, integration metadata, comment, severity labels, and explicit model choice inherit must be preserved. '
              f'A Python environment with PyYAML is available at {state["python"]}. '
              'Keep any original copies and candidate trees under this evaluation root, outside Agent discovery paths. ')
    if args.host == 'claude' and state.get('allow_static_validator'):
        checker = root / '.claude/skills/configure-subagents/scripts/validate_agents.py'
        prompt += (f'The permitted validator command prefix is "{Path(state["python"]).as_posix()}" '
                   f'"{checker.as_posix()}"; append --project-root and, when needed, --agents-dir and --format json. ')
    if args.phase == 'initial':
        prompt += 'Review the project and propose suitable subagent configuration. This request is proposal-only; do not change files.'
    else:
        prompt += 'The project has progressed. Read the current files and improve and apply the subagent configuration where appropriate. Preserve user customizations and unrelated files. Run static validation and report evidence, changes, and limitations.'
    if not args.run:
        print(json.dumps({'root': str(root), 'prompt': prompt}, ensure_ascii=True))
        return
    evidence_path = output / f'{args.host}-{args.phase}-evidence.json'
    if evidence_path.exists():
        parser.error('Do not overwrite evidence; use a fresh output for a new attempt.')
    result = base.run_phase(state, args.phase, prompt_override=prompt)
    if args.phase in ('initial', 'repeat'):
        result['no_project_mutation'] = not result['changed']
    content = agent_path.read_text(encoding='utf-8') if agent_path.exists() else ''
    result['preservation_checks'] = {
        'reviewer_exists': agent_path.exists(),
        'integration_comment': '# Preserve this integration comment.' in content,
        'metadata': 'integrationTag: lifecycle-v1' in content,
        'explicit_model': 'model: inherit' in content,
        'reporting_contract': "Use the team's severity labels: blocking, caution, note." in content,
        'user_note': args.phase == 'initial' or USER_NOTE in content,
        'only_agent_files_changed': all(p.replace('\\', '/').startswith('lifecycle/.claude/agents/') for p in result['changed']),
    }
    result['semantic_review'] = 'pending; inspect trace and outputs, not only exit code'
    evidence_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('before', 'after')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
