#!/usr/bin/env python3
"""Opt-in host QA in fresh temporary projects, never called by the Skill.

Runs paid/authenticated host sessions only with --run. Does not call generated
agents. Raw local logs stay in the evaluation output directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "configure-subagents"
FIXTURES = {
    "small/README.md": "# Filename normalizer\nOne small local Python script. No recurring team workflow yet.\n",
    "small/normalize.py": "def normalize(name):\n    return name.strip().lower().replace(' ', '-')\n",
    "services/README.md": "# Order pipeline\nAPI and worker share the event contract. Changes to events require review in both services. Worker processing is tested independently.\n",
    "services/services/api/pyproject.toml": '[project]\nname = "order-api"\nversion = "0.1.0"\n',
    "services/services/api/handler.py": 'def submit(order_id):\n    return {"order_id": order_id}\n',
    "services/services/worker/worker.py": 'def process(event):\n    return event["order_id"]\n',
    "services/shared/events.py": 'REQUIRED_FIELDS = ("order_id",)\n',
    "services/tests/test_worker.py": "import unittest\nfrom services.worker.worker import process\n\nclass WorkerTests(unittest.TestCase):\n    def test_id(self):\n        self.assertEqual(process({'order_id': 'a'}), 'a')\n",
    "services/CLAUDE.md": "Test command: python -m unittest discover -s tests. Shared event changes need both consumers reviewed. Do not infer tests passed from their existence.\n",
    "docs/README.md": "# Operations handbook\nA Markdown-only handbook; authors draft and then check factual claims against source notes. No application build.\n",
    "docs/guide.md": "# Escalation\nCheck the source notes before naming an escalation owner.\n",
    "docs/sources/notes.md": "Escalation ownership is assigned separately by each project lead.\n",
    "existing/README.md": "# Existing reviewer\nThe reviewer should only inspect source files. Keep its reporting contract and integration metadata.\n",
    "existing/app.py": "def add(a, b):\n    return a + b\n",
    "existing/.claude/agents/reviewer.md": "---\nname: reviewer\ndescription: Review source changes without editing files or running commands.\n# Keep integration metadata and comments.\ntools: Read, Glob, Grep, Bash, Write, Edit\nmodel: inherit\nintegrationTag: handbook-v1\n---\n\nReview only the supplied change and relevant instructions.\nReport findings with file paths, impact, and missing evidence.\nPreserve the team's exact three-level severity scale: blocking, caution, note.\nDo not implement fixes or run commands.\n",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    # Path.rglob may silently skip unreadable directories on newer Python.
    # An incomplete snapshot must not count as a preservation pass.
    def fail(error):
        raise error
    files = []
    for folder, _, names in os.walk(root, onerror=fail):
        files.extend(Path(folder) / name for name in names)
    return {p.relative_to(root).as_posix(): {"sha256": digest(p), "mtime_ns": p.stat().st_mtime_ns}
            for p in sorted(files)}


def prepare(host, output):
    root = Path(tempfile.mkdtemp(prefix=f"configure-subagents-{host}-"))
    projects = root / "projects"
    for relative, content in FIXTURES.items():
        target = projects / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    skill_parent = root / (".claude/skills" if host == "claude" else ".agents/skills")
    shutil.copytree(PACKAGE, skill_parent / "configure-subagents", ignore=shutil.ignore_patterns("__pycache__"))
    # Git root allows normal parent-directory Skill discovery on both hosts.
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    state = {"host": host, "root": str(root), "output": str(output), "python": sys.executable,
             "package_hashes": {str(p.relative_to(PACKAGE)): digest(p) for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}}
    (output / f"{host}-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def prompt_for(state, phase):
    host, root = state["host"], Path(state["root"])
    invocation = "/configure-subagents" if host == "claude" else "$configure-subagents"
    common = (f"{invocation}\nWork only within {root}. This is an isolated Skill evaluation. "
              "Use the installed configure-subagents Skill. Do not delegate, spawn subagents, "
              "or call any generated agent. Do not read or modify personal/global settings. "
              "Report unavailable model or global-policy information honestly. Respond in Korean. ")
    if phase == "propose":
        return common + "Propose appropriate subagent configurations separately for projects/small, projects/services, and projects/docs, based on their files. This is a proposal request only."
    skill_dir = root / (".claude/skills" if host == "claude" else ".agents/skills") / "configure-subagents"
    return common + ("Improve and APPLY the existing projects/existing reviewer so it only reads source files "
                     "and cannot use shell or editing tools. Preserve the other instructions, comments, "
                     "integration metadata, and unrelated files. Run the Skill static validator. "
                     f"A Python environment with PyYAML is available at {state['python']}. "
                     f"The checker is {skill_dir / 'scripts/validate_agents.py'}. "
                     "Prepare any candidate files and original copies inside a new directory under the evaluation root, "
                     "outside all Agent discovery directories. Do not install dependencies or run project code. "
                     "If already adequate, do not rewrite files.")


def run_phase(state, phase, prompt_override=None):
    host, root, output = state["host"], Path(state["root"]), Path(state["output"])
    prompt = prompt_override if prompt_override is not None else prompt_for(state, phase)
    (output / f"{host}-{phase}-prompt.txt").write_text(prompt, encoding="utf-8")
    executable = shutil.which(host)
    if not executable:
        return {"phase": phase, "status": "unavailable", "reason": "Host CLI not found"}
    if host == "claude":
        command = [executable, "-p", "--output-format", "stream-json", "--verbose", "--no-session-persistence",
                   "--setting-sources", "project", "--strict-mcp-config", "--no-chrome",
                   "--permission-mode", "acceptEdits", "--permission-prompts", "none",
                   "--tools", "Read,Glob,Grep,Skill,Edit,Write,Bash",
                   "--allowedTools", "Read,Glob,Grep,Skill,Edit,Write"]
        if state.get("allow_static_validator"):
            checker = root / ".claude/skills/configure-subagents/scripts/validate_agents.py"
            prefix = f'"{Path(state["python"]).as_posix()}"'
            target = f'"{checker.as_posix()}"'
            command.extend(["--allowedTools", f'Bash({prefix} {target} *)', f'Bash({prefix} -I {target} *)'])
    else:
        command = [executable, "exec", "--ignore-user-config", "--ephemeral", "--sandbox", "workspace-write",
                   "-c", 'approval_policy="never"', "--json", "-C", str(root), "-"]
        if state.get("windows_sandbox"):
            command.extend(["-c", f'windows.sandbox="{state["windows_sandbox"]}"'])
    before = snapshot(root / "projects")
    started = time.monotonic()
    try:
        with (output / f"{host}-{phase}.stdout").open("w", encoding="utf-8") as out, (output / f"{host}-{phase}.stderr").open("w", encoding="utf-8") as err:
            completed = subprocess.run(command, input=prompt, text=True, encoding="utf-8", cwd=root,
                                       stdout=out, stderr=err, timeout=240)
        code = completed.returncode
        status = "finished" if code == 0 else "host_error"
    except subprocess.TimeoutExpired:
        code, status = None, "timeout"
    after = snapshot(root / "projects")
    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    result = {"phase": phase, "status": status, "returncode": code, "seconds": round(time.monotonic() - started, 2),
              "changed": changed, "before": before, "after": after}
    if phase in ("propose", "rerun"):
        result["no_project_mutation"] = not changed
    if phase == "apply":
        path = root / "projects/existing/.claude/agents/reviewer.md"
        import yaml
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        data = yaml.safe_load(parts[1]) if len(parts) == 3 else {}
        tools = data.get("tools", [])
        tools = [t.strip() for t in tools.split(",")] if isinstance(tools, str) else tools
        original = FIXTURES["existing/.claude/agents/reviewer.md"]
        result["checks"] = {
            "only_expected_file_changed": changed == ["existing/.claude/agents/reviewer.md"],
            "read_tools_only": bool(tools) and set(tools) <= {"Read", "Glob", "Grep"},
            "body_preserved": len(parts) == 3 and parts[2] == original.split("---", 2)[2],
            "comment_preserved": "# Keep integration metadata and comments." in content,
            "metadata_preserved": data.get("integrationTag") == "handbook-v1",
            "model_preserved": data.get("model") == "inherit",
        }
    (output / f"{host}-{phase}-evidence.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("claude", "codex"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("propose", "apply", "rerun"), default="propose")
    parser.add_argument("--run", action="store_true", help="Explicitly opt in to a host model session.")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    state_path = args.output / f"{args.host}-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else prepare(args.host, args.output)
    if not args.run:
        print(json.dumps({"prepared": state, "prompt": prompt_for(state, args.phase)}, ensure_ascii=True))
        return
    result = run_phase(state, args.phase)
    # Compact stdout; full byte/mtime snapshots stay in the evidence file.
    print(json.dumps({k: v for k, v in result.items() if k not in {"before", "after"}}, ensure_ascii=True))


if __name__ == "__main__":
    main()
