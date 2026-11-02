#!/usr/bin/env python3
"""Opt-in model-selection QA; never invoked by the installed Skill.

Synthetic target eligibility/price/workload evidence is not a real account test.
Run propose-1, propose-2, apply, repeat as independent host CLI sessions. No
generated Agent invocation. All fixture/staging/log writes stay under --output.
Mechanical checks do not certify semantic reasoning or measured savings.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "configure-subagents"
PHASES = ("propose-1", "propose-2", "apply", "repeat")
MODELS = {
    "haiku": {"family": "Haiku", "input": 1, "output": 5, "latency": "short", "qualified": ["extract", "run-checks"]},
    "sonnet": {"family": "Sonnet", "input": 3, "output": 12, "latency": "medium", "qualified": ["extract", "run-checks", "research", "write", "implement", "routine-review"]},
    "opus": {"family": "Opus", "input": 6, "output": 28, "latency": "long", "qualified": ["extract", "run-checks", "research", "write", "implement", "routine-review", "risk-review"]},
    "fable": {"family": "Fable", "input": 12, "output": 60, "latency": "long", "qualified": ["extract", "run-checks", "research", "write", "implement", "routine-review", "risk-review"]},
}
WORK = {
    "extract": "Extract fixed fields from 40 daily short tickets; a deterministic schema catches malformed output. No policy interpretation.",
    "run-checks": "Run approved unit-check commands and summarize exit codes and failing cases; no test repair or deployment.",
    "research": "Compare provided versioned sources with citations for a bounded API question; conflicting sources must be reported.",
    "write": "Write short handbook updates from approved facts and a glossary; content is checked against the source list.",
    "implement": "Implement localized changes against clear acceptance tests; no architecture redesign or shared-file ownership changes.",
    "routine-review": "Review a small local change against explicit assertions and changed lines; no cross-service ambiguity.",
    "risk-review": "Review authorization boundaries spanning two services, including contradictory revisions and costly silent permission failures.",
}


def catalog(eligible=None, unknown=(), excluded=(), prices=True):
    eligible = list(MODELS) if eligible is None else eligible
    return [{"model": name, "eligibility": "eligible" if name in eligible else "unverified" if name in unknown else "excluded",
             "constraint": "not allowed in this synthetic target" if name in excluded else None,
             "alias_resolution": f"fixture-provider/{name}-test-version",
             "fixture_evidence": {k: v for k, v in info.items() if prices or k not in {"input", "output"}}}
            for name, info in MODELS.items()]


def cases():
    data = {
        "routine": {"tasks": ["extract", "run-checks"], "candidates": catalog()},
        "roles": {"tasks": ["research", "write", "implement", "run-checks", "routine-review"], "candidates": catalog()},
        "review-risk": {"tasks": ["routine-review", "risk-review"], "candidates": catalog()},
        "price-unknown": {"tasks": ["extract", "implement"], "candidates": catalog(prices=False)},
        "cheap-unverified": {"tasks": ["extract"], "candidates": catalog(["sonnet", "opus", "fable"], unknown=["haiku"])},
        "single": {"tasks": ["write", "risk-review"], "candidates": catalog(["fable"], unknown=["haiku", "sonnet"], excluded=["opus"])},
        "unknown": {"tasks": ["research"], "candidates": catalog([], unknown=list(MODELS))},
        "older-price": {"tasks": ["risk-review"], "candidates": [
            {"model": name, "eligibility": "eligible", "alias_resolution": name,
             "fixture_evidence": {"family": "Opus", "input": price, "output": price * 5, "latency": "medium", "qualified": ["risk-review"]}}
            for name, price in [("claude-opus-4-6", 9), ("claude-opus-5-5", 4)]]},
    }
    for case in data.values():
        case["work"] = {task: WORK[task] for task in case["tasks"]}
        case["synthetic_main_session_model"] = "fable"
    return data


def hashes(root, metadata=False, exclude_git=False):
    result = {}
    def fail(error):
        raise error
    for folder, dirs, names in os.walk(root, onerror=fail, followlinks=False):
        if exclude_git:
            dirs[:] = [name for name in dirs if name != ".git"]
        for name in dirs + names:
            entry = Path(folder) / name
            if entry.is_symlink() or getattr(entry.lstat(), "st_file_attributes", 0) & 0x400:
                raise ValueError(f"Linked evaluation entry: {entry}")
        for name in sorted(names):
            file = Path(folder) / name
            if "__pycache__" in file.parts:
                continue
            info = {"sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
            if metadata:
                info["mtime_ns"] = file.stat().st_mtime_ns
            result[file.relative_to(root).as_posix()] = info
    return result


def agent(name, model):
    # Deliberate BOM/CRLF, extra field and comment for model-only preservation.
    return (f"\ufeff---\r\nname: {name}\r\ndescription: Extract fixed fields from supplied tickets.\r\n"
            f"# Preserve integration comment.\r\ntools: Read, Glob, Grep\r\nmodel: {model}\r\n"
            "integrationTag: model-selection-v1\r\n---\r\n\r\n"
            "Extract only the supplied fields; report malformed input.\r\n"
            "Return blocking, caution or note findings with source paths.\r\n").encode("utf-8")


def prepare(host, output):
    root = output / "workspace"
    root.mkdir()
    project = root / "projects"
    project.mkdir()
    for key, case in cases().items():
        directory = project / key
        directory.mkdir()
        (directory / "WORK.json").write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")
    existing = project / "existing"
    (existing / ".claude/agents").mkdir(parents=True)
    for name, model in [("ticket-extractor", "fable"), ("fixed-extractor", "opus")]:
        (existing / f".claude/agents/{name}.md").write_bytes(agent(name, model))
    (existing / "WORK.json").write_text(json.dumps({"work": WORK["extract"], "candidates": catalog()}, indent=2), encoding="utf-8")
    parent = root / (".claude/skills" if host == "claude" else ".agents/skills")
    parent.mkdir(parents=True)
    shutil.copytree(SKILL, parent / "configure-subagents", ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    state = {"host": host, "root": str(root), "skill_hashes": hashes(SKILL), "fixture_hashes": hashes(project, True)}
    (output / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def prompt(state, phase):
    root = Path(state["root"])
    prefix = "/configure-subagents" if state["host"] == "claude" else "$configure-subagents"
    declaration = ("This is synthetic model-selection QA. Treat WORK.json candidate eligibility as my explicit declaration for the "
                   "SIMULATED target environment only. Prices are invented input/output units per million tokens; latency and "
                   "qualified workloads are synthetic comparison evidence, not actual account access, current list prices, or measured "
                   "real model performance. Absent price means unknown, not zero. This fixture provider accepts the listed aliases "
                   "with the recorded frozen mappings. Do not generalize them outside this fixture or browse for replacements. ")
    scope = (f"{prefix}\nUse the installed Skill. Work only within {root}. Do not delegate, invoke generated agents, "
             "read personal/global settings, install dependencies or run project programs. Inspect fixture/Skill files with native "
             "file tools or read-only local shell commands (for example Get-Content/Get-ChildItem); no remote connection is needed. "
             "Other permitted execution is limited to the installed Skill's read-only Python helpers/checker; Python with PyYAML is "
             f"{sys.executable}. Keep any candidates/backups inside this root outside discovery paths. "
             "Respond in Korean; existing Agent prose must remain English. " + declaration)
    if phase.startswith("propose"):
        request = ("Propose suitable Agent configurations separately for every project except projects/existing. "
                   "The work items are recurring responsibilities, not a mandatory Agent roster. Do not change any files. "
                   "Finish with one JSON object (no code fence) with a cases array. Each case has case (directory name), "
                   "candidate_groups (eligible, unverified, excluded arrays of model names), agents array and unknowns array. "
                   "Each proposed agent has name, model, frontmatter (YAML frontmatter string), requirement, alternative "
                   "(model name or null), reason and unknowns array. Other prose may precede the JSON. "
                   "Explain candidate comparisons and evidence; do not claim runtime access or measured savings.")
    else:
        checker = root / (".claude/skills" if state["host"] == "claude" else ".agents/skills") / "configure-subagents/scripts/validate_agents.py"
        request = ("Improve and APPLY the existing configuration in projects/existing using its work and candidate evidence. "
                   "The model of fixed-extractor is explicitly fixed to opus by me. ticket-extractor has no fixed-model instruction. "
                   "Preserve both names, tools, descriptions, comments, metadata and body verbatim; preserve BOM, CRLF and final newline. "
                   "Only justified model-field corrections are in scope; do not add or remove Agents. "
                   f"Run static validation with {checker}. Report candidate groups, each model decision, leading alternative, "
                    "preservation and unknowns. Finish with one JSON object (no code fence) with a cases array containing case existing. "
                    "Each case has case, candidate_groups (eligible, unverified, excluded arrays of model names), agents array and unknowns array. "
                    "Each agent has name, model, requirement, alternative (model name or null), reason and unknowns array.")
    file_operations = ("For this application/reassessment request, local shell commands that copy, byte-edit or compare "
                       "only the specified Agent files and in-root candidates/backups are also permitted. "
                       "This authorizes no project programs or generated-Agent calls and does not waive host approval prompts. ") if not phase.startswith("propose") else ""
    return scope + file_operations + request


def command(host, root, output, phase, host_model=None, windows_sandbox=None):
    binary = shutil.which(host)
    if not binary:
        raise FileNotFoundError(f"Host CLI not found: {host}")
    if host == "claude":
        cmd = [binary, "-p", "--output-format", "stream-json", "--verbose", "--no-session-persistence",
               "--setting-sources", "project", "--strict-mcp-config", "--no-chrome",
               "--permission-mode", "acceptEdits", "--permission-prompts", "none",
               "--tools", "Read,Glob,Grep,Skill,Edit,Write,Bash", "--allowedTools", "Read,Glob,Grep,Skill,Edit,Write"]
        scripts = root / ".claude/skills/configure-subagents/scripts"
        for helper in ("validate_agents.py", "inspect_file_bytes.py", "find_evidence.py"):
            cmd += ["--allowedTools", f'Bash("{Path(sys.executable).as_posix()}" "{(scripts / helper).as_posix()}" *)',
                    f'Bash("{Path(sys.executable).as_posix()}" -I "{(scripts / helper).as_posix()}" *)']
        if host_model:
            cmd += ["--model", host_model]
    else:
        cmd = [binary, "exec", "--ignore-user-config", "--ephemeral", "--sandbox", "workspace-write",
               "-c", 'approval_policy="never"', "--json", "-C", str(root),
               "--output-last-message", str(output / f"{phase}-final.txt")]
        if windows_sandbox:
            cmd += ["-c", f'windows.sandbox="{windows_sandbox}"']
        if host_model:
            cmd += ["--model", host_model]
        cmd.append("-")
    return cmd


def final_json(text):
    decoder = json.JSONDecoder()
    # Decode from object starts rather than a greedy regex across prose/code.
    for match in re.finditer(r"\{", text):
        try:
            value, _ = decoder.raw_decode(text[match.start():])
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get("cases"), list):
            return value
    return None


def mechanical_report_checks(report, phase):
    if not isinstance(report, dict) or not isinstance(report.get("cases"), list) or not all(
        isinstance(item, dict) and isinstance(item.get("case"), str)
        and isinstance(item.get("candidate_groups"), dict)
        and all(isinstance(item["candidate_groups"].get(group), list) and all(isinstance(name, str) for name in item["candidate_groups"][group]) for group in ("eligible", "unverified", "excluded"))
        and isinstance(item.get("agents"), list) and all(isinstance(agent, dict) for agent in item["agents"])
        for item in report["cases"]
    ):
        return {"structured_report": False}
    import yaml
    expected = cases() if phase.startswith("propose") else {"existing": {"candidates": catalog()}}
    observed = {item.get("case"): item for item in report["cases"]}
    checks = {"structured_report": True, "case_coverage": set(observed) == set(expected) and len(observed) == len(report["cases"])}
    for key, case in expected.items():
        item = observed.get(key, {})
        groups = {group: sorted(c["model"] for c in case["candidates"] if c["eligibility"] == group)
                  for group in ("eligible", "unverified", "excluded")}
        checks[f"{key}:candidate_groups"] = item.get("candidate_groups") == groups or all(
            sorted(item.get("candidate_groups", {}).get(group, [])) == values for group, values in groups.items())
        agents = item.get("agents", [])
        allowed = set(groups["eligible"]) or {"inherit"}
        checks[f"{key}:eligible_assignments"] = bool(agents) and all(a.get("model") in allowed for a in agents)
        checks[f"{key}:reasons"] = bool(agents) and all(all(a.get(field) for field in ("name", "requirement", "reason")) and "alternative" in a and isinstance(a.get("unknowns"), list) for a in agents)
        if phase.startswith("propose"):
            consistent = bool(agents)
            for entry in agents:
                try:
                    data = yaml.safe_load(str(entry.get("frontmatter", "")).strip().removeprefix("---").removesuffix("---"))
                    consistent &= isinstance(data, dict) and data.get("model") == entry.get("model") and data.get("name") == entry.get("name") and bool(data.get("description"))
                except yaml.YAMLError:
                    consistent = False
            checks[f"{key}:frontmatter_consistency"] = bool(consistent)
    return checks


def child_environment(host, account_login=False):
    env = os.environ.copy()
    removed = []
    # A standalone evaluation must not reuse its parent's desktop tool bridge
    # or task identity. This changes neither auth storage nor sandbox policy.
    names = ["CODEX_APP_TOOLS_PIPE_PATH", "CODEX_INTERNAL_ORIGINATOR_OVERRIDE", "CODEX_SESSION_ID",
             "CODEX_THREAD_ID", "CODEX_TOOL_CALL_ID", "CODEX_TASK_WORKSPACE_VERIFYING_IDENTITY"] if host == "codex" else []
    if host == "claude" and account_login:
        if any(env.get(name) for name in ("CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY")):
            raise ValueError("Account-login evaluation must not override an active third-party provider")
        names += ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"]
    for name in names:
        if name in env:
            del env[name]
            removed.append(name)
    env["PYTHONUTF8"] = "1"
    return env, removed


def run(state, output, phase, host_model=None, windows_sandbox=None, timeout=900, account_login=False, interactive=False):
    root, host = Path(state["root"]), state["host"]
    evidence = output / f"{phase}-evidence.json"
    if evidence.exists() or (output / f"{phase}.stdout.jsonl").exists():
        raise ValueError("Do not overwrite attempts; use a fresh output directory")
    if hashes(SKILL) != state["skill_hashes"] or hashes(root / (".claude/skills" if host == "claude" else ".agents/skills") / "configure-subagents") != state["skill_hashes"]:
        raise ValueError("Skill changed; prepare a fresh evaluation")
    if phase == "repeat":
        prior = output / "apply-evidence.json"
        if not prior.exists() or json.loads(prior.read_text())["status"] != "finished":
            raise ValueError("A completed apply must precede repeat")
    before = hashes(root / "projects", True)
    workspace_before = hashes(root, True, exclude_git=True)
    original = {name: (root / "projects/existing/.claude/agents" / name).read_bytes()
                for name in ("ticket-extractor.md", "fixed-extractor.md")}
    instruction = prompt(state, phase)
    (output / f"{phase}-prompt.txt").write_text(instruction, encoding="utf-8")
    cmd = command(host, root, output, phase, host_model, windows_sandbox)
    session_id = str(uuid.uuid4()) if interactive else None
    if interactive:
        if host != "claude":
            raise ValueError("Interactive mode is only implemented for Claude")
        cmd = [cmd[0], "--session-id", session_id, "--setting-sources", "project", "--strict-mcp-config", "--no-chrome",
               "--permission-mode", "acceptEdits", "--tools", "Read,Glob,Grep,Skill,Edit,Write,Bash",
               "--allowedTools", "Read,Glob,Grep,Skill"]
        if host_model:
            cmd += ["--model", host_model]
        cmd += ["--", instruction]
    version = subprocess.check_output([cmd[0], "--version"], encoding="utf-8").strip()
    started = time.monotonic()
    env, removed = child_environment(host, account_login)
    if interactive:
        (output / f"{phase}-interactive.json").write_text(json.dumps({"session_id": session_id, "root": str(root), "phase": phase}), encoding="utf-8")
        result = subprocess.run(cmd, cwd=root, env=env)
        code, status = result.returncode, "finished" if result.returncode == 0 else "host_error"
        # Read only this session's automatically written transcript, not other
        # conversations or credential files. Copy it to the permitted QA root.
        logs = list((Path.home() / ".claude/projects").rglob(f"{session_id}.jsonl"))
        if len(logs) == 1:
            (output / f"{phase}.stdout.jsonl").write_bytes(logs[0].read_bytes())
        else:
            (output / f"{phase}.stdout.jsonl").write_text("", encoding="utf-8")
    else:
        with (output / f"{phase}.stdout.jsonl").open("w", encoding="utf-8") as stdout, (output / f"{phase}.stderr.txt").open("w", encoding="utf-8") as stderr:
            try:
                result = subprocess.run(cmd, input=instruction, cwd=root, text=True, encoding="utf-8", env=env,
                                        stdout=stdout, stderr=stderr, timeout=timeout)
                code, status = result.returncode, "finished" if result.returncode == 0 else "host_error"
            except subprocess.TimeoutExpired:
                code, status = None, "timeout"
    text, model_names = "", set()
    for line in (output / f"{phase}.stdout.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if host == "claude":
            message = event.get("message", {})
            if event.get("type") == "assistant" and message.get("model") and not message["model"].startswith("<"):
                model_names.add(message["model"])
                if interactive:
                    content = "\n".join(block.get("text", "") for block in message.get("content", []) if block.get("type") == "text")
                    if content.strip():
                        text = content
            if event.get("type") == "result":
                text = event.get("result", "")
                if event.get("is_error"):
                    status = "host_error"
        elif event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            text = event["item"].get("text", "")
    final = output / f"{phase}-final.txt"
    if text:
        final.write_text(text, encoding="utf-8")
    elif final.exists():
        text = final.read_text(encoding="utf-8")
    after = hashes(root / "projects", True)
    workspace_after = hashes(root, True, exclude_git=True)
    workspace_changed = sorted(name for name in workspace_before.keys() | workspace_after.keys() if workspace_before.get(name) != workspace_after.get(name))
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    preserved = {}
    for name, previous in original.items():
        file = root / "projects/existing/.claude/agents" / name
        new = file.read_bytes() if file.exists() else b""
        preserved[name] = {"unchanged": new == previous,
                           "only_model_changed": re.sub(rb"(?m)^model: [^\r\n]+", b"model: <value>", new) == re.sub(rb"(?m)^model: [^\r\n]+", b"model: <value>", previous)}
    report = final_json(text)
    result = {"host": host, "host_version": version, "phase": phase, "status": status, "returncode": code,
              "seconds": round(time.monotonic() - started, 2), "requested_host_model": host_model,
              "observed_host_models": sorted(model_names), "model_evidence": "trace" if model_names else "actual host model unverified",
              "child_environment_omissions": removed,
              "interactive_session": session_id,
              "synthetic_target": True, "skill_hashes": state["skill_hashes"], "before": before, "after": after,
              "workspace_before": workspace_before, "workspace_after": workspace_after,
              "workspace_changed": workspace_changed, "no_workspace_mutation": not workspace_changed,
              "changed": changed, "no_project_mutation": not changed, "preservation": preserved,
              "report_checks": mechanical_report_checks(report, phase), "semantic_review": "pending independent trace/report review"}
    evidence.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"before", "after", "skill_hashes", "workspace_before", "workspace_after"}}, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=("claude", "codex"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--phase", choices=PHASES, default="propose-1")
    parser.add_argument("--run", action="store_true", help="Opt in to one paid/authenticated host session")
    parser.add_argument("--host-model", help="Optional fixed evaluation-host model; never a target-eligibility claim")
    parser.add_argument("--windows-sandbox", choices=("elevated", "unelevated"))
    parser.add_argument("--claude-account-login", action="store_true", help="Use existing Claude account login by omitting external key/token/base URL only in the child")
    parser.add_argument("--interactive", action="store_true", help="Claude only: human approvals in a visible terminal; exit with /exit to snapshot")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(REPO / ".eval-runs") or output.is_symlink():
        parser.error("Use a fresh output directory under this repository's ignored .eval-runs/")
    output.mkdir(parents=True, exist_ok=True)
    state_file = output / "state.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else prepare(args.host, output)
    if state["host"] != args.host:
        parser.error("Output belongs to another host")
    try:
        if args.run:
            run(state, output, args.phase, args.host_model, args.windows_sandbox, account_login=args.claude_account_login, interactive=args.interactive)
        else:
            print(json.dumps({"prepared": state, "prompt": prompt(state, args.phase)}, ensure_ascii=True))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Evaluation unavailable: {error}\n")


if __name__ == "__main__":
    main()
