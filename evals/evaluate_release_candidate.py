#!/usr/bin/env python3
"""Opt-in 22-session installed-RC QA. Never runs from the installed Skill.

Run capture once for authorized real-project sources, then session for each
host/job. No generated Agent invocation, account probe or benchmark.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

import evaluate_model_selection as base

REPO = Path(__file__).resolve().parents[1]
JOBS = ("propose-default", "propose-cross", "synthetic-default-apply", "synthetic-default-repeat",
        "synthetic-both-apply", "synthetic-both-repeat", "real-default-apply", "real-default-repeat",
        "real-both-apply", "real-both-repeat", "validate-both")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "build", "dist", ".dart_tool", ".gradle", "Pods",
             ".next", ".nuxt", "coverage", ".cache", ".eval-runs", ".release", "logs", ".firebase", ".idea", ".vscode",
             ".ssh", ".aws", ".azure", ".gcloud", ".secrets", ".credentials",
             ".configure-subagents-work", ".configure-subagents-updates", "__pycache__"}
EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".jsx", ".ts", ".tsx",
              ".dart", ".swift", ".kt", ".kts", ".java", ".c", ".h", ".cpp", ".gradle", ".xml", ".plist",
              ".sh", ".ps1", ".html", ".css", ".sql", ".rules", ".lock", ".rst"}
SKIP_NAMES = {".npmrc", "settings.json", "settings.local.json", "google-services.json",
              "googleservice-info.plist", "auth.json", "tokens.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def checked_output(value):
    root = Path(value).absolute()
    if root.resolve() != root or not root.is_relative_to(REPO / ".eval-runs"):
        raise ValueError("Use an unlinked output directory under this repository's ignored .eval-runs/")
    root.mkdir(parents=True, exist_ok=True)
    return root


def secret_name(path):
    name = path.name.lower()
    return (name.startswith(".env") or name in SKIP_NAMES or (name == "config.toml" and path.parent.name.casefold() == ".codex") or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
            or any(term in name for term in ("credential", "serviceaccount", "service-account", "private-key", "secret", "adminsdk")))


def git_state(root):
    def query(args):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, encoding="utf-8")
        return result.stdout.strip() if result.returncode == 0 else None
    return {"head": query(["rev-parse", "HEAD"]), "status": query(["status", "--porcelain=v1"])}


def file_fact(path):
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    if (before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_ino, after.st_mtime_ns, after.st_size):
        raise ValueError(f"Source changed during read: {path}")
    return {"sha256": hashlib.sha256(data).hexdigest(), "mtime_ns": after.st_mtime_ns}


def capture(output, sources):
    record = output / "sources.json"
    if record.exists() or (output / "sources").exists():
        raise ValueError("Do not overwrite frozen source captures")
    if len(sources) != 2 or {name for name, _ in sources} != {"signal_flare", "mosigi"}:
        raise ValueError("Supply the two authorized names signal_flare and mosigi")
    (output / "sources").mkdir()
    records = {}
    for name, source in sources:
        root = Path(source).resolve(strict=True)
        destination = output / "sources" / name
        destination.mkdir()
        files, excluded = {}, []
        before_git = git_state(root)
        for folder, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d.casefold() not in {n.casefold() for n in SKIP_DIRS} and not (Path(folder) == root and d.casefold() in {"data", "runtime", "tmp", "temp"}) and not (Path(folder) / d).is_symlink()
                             and not getattr((Path(folder) / d).lstat(), "st_file_attributes", 0) & 0x400)
            for filename in sorted(names):
                path = Path(folder) / filename
                relative = path.relative_to(root).as_posix()
                if (secret_name(path) or path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400
                        or not path.is_file() or path.suffix.lower() not in EXTENSIONS or path.stat().st_size > 2 * 1024 * 1024):
                    excluded.append(relative)
                    continue
                initial = path.stat()
                data = path.read_bytes()
                if re.search(rb"-----BEGIN [^\r\n-]*PRIVATE KEY[^\r\n]*-----", data):
                    excluded.append(relative)
                    continue
                files[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "mtime_ns": initial.st_mtime_ns}
                if file_fact(path) != files[relative]:
                    raise ValueError("Source changed after content screening; use a new campaign")
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                os.utime(target, ns=(initial.st_atime_ns, initial.st_mtime_ns))
                if file_fact(target) != files[relative] or file_fact(path) != files[relative]:
                    raise ValueError("Source changed while copying; use a new campaign")
        if git_state(root) != before_git:
            raise ValueError("Source Git state changed while capturing; use a new campaign")
        if any(file_fact(root / relative) != info for relative, info in files.items()):
            raise ValueError("Source files changed before capture completed; use a new campaign")
        records[name] = {"source": str(root), "git": before_git, "files": files, "excluded": excluded,
                         "frozen_hashes": base.hashes(destination, True)}
    write_json(record, records)
    print(json.dumps({"captured": {name: len(item["files"]) for name, item in records.items()}}))


def source_observation(output):
    records = json.loads((output / "sources.json").read_text())
    result = {}
    for name, entry in records.items():
        root = Path(entry["source"])
        changed = []
        for relative, info in entry["files"].items():
            try:
                if file_fact(root / relative) != info:
                    changed.append(relative)
            except OSError:
                changed.append(relative)
        result[name] = {"selected_files_changed": changed, "git_unchanged": git_state(root) == entry["git"]}
    return result


def target_for(host, job):
    if "both" in job:
        return "both"
    return ("codex" if host == "claude" else "claude") if job == "propose-cross" else host


def fixture_catalogs():
    data = base.cases()
    mapping = {"haiku": "gpt-fixture-light", "sonnet": "gpt-fixture-general", "opus": "gpt-fixture-deep", "fable": "gpt-fixture-frontier",
               "claude-opus-4-6": "gpt-fixture-older", "claude-opus-5-5": "gpt-fixture-newer"}
    result = {}
    for name, case in data.items():
        codex = json.loads(json.dumps(case))
        for candidate in codex["candidates"]:
            candidate["model"] = mapping[candidate["model"]]
            candidate["alias_resolution"] = candidate["model"] + "/frozen-fixture"
            candidate["fixture_evidence"].pop("family", None)
            candidate["fixture_evidence"]["supported_efforts"] = ["low", "medium", "high"]
        codex["synthetic_main_session_model"] = "gpt-fixture-frontier"
        result[name] = {"claude": case, "codex": codex}
    return result


def seed_agent(directory, target, name, model=None, korean=False):
    directory.mkdir(parents=True, exist_ok=True)
    text = "문서를 확인하고 근거를 보고한다." if korean else "Extract fixed ticket fields and report malformed input."
    description = "프로젝트 문서 검토" if korean else "Extract fields from supplied tickets."
    if target == "claude":
        lines = ["---", f"name: {name}", f"description: {description}", "# Preserve integration comment.", "tools: Read, Glob, Grep", f"model: {model or 'inherit'}", "integrationTag: rc-fixture", "---", "", text, ""]
        data = "\n".join(lines).encode("utf-8")
        if not korean:
            data = b"\xef\xbb\xbf" + data.replace(b"\n", b"\r\n")
        suffix = ".md"
    else:
        lines = [f'name = "{name}"', f'description = "{description}"', "# Preserve integration comment.", f'developer_instructions = "{text}"', 'integrationTag = "rc-fixture"']
        if model:
            lines += [f'model = "{model}"', 'model_reasoning_effort = "high"']
        lines += ["[features]", "shell_tool = false", ""]
        data = "\n".join(lines).encode("utf-8")
        if korean:
            data = data.replace(b"\n", b"\r\n")
        suffix = ".toml"
    (directory / (name + suffix)).write_bytes(data)


def prepare_session(output, host, job, skill):
    group = job.rsplit("-", 1)[0] if job.endswith(("-apply", "-repeat")) else job
    folder = output / host / group
    state_path = folder / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state["host"] != host or state["skill_hashes"] != base.hashes(skill):
            raise ValueError("Frozen Skill/host mismatch")
        return folder, state
    if job.endswith("-repeat"):
        raise ValueError("Run and review apply before its fresh repeat")
    folder.mkdir(parents=True)
    root = folder / "workspace"
    root.mkdir()
    projects = root / "projects"
    projects.mkdir()
    installation = root / (".claude/skills" if host == "claude" else ".agents/skills") / "configure-subagents"
    installation.parent.mkdir(parents=True)
    shutil.copytree(skill, installation, ignore=shutil.ignore_patterns("__pycache__"))
    if job.startswith("real-"):
        sources = json.loads((output / "sources.json").read_text())
        for name, entry in sources.items():
            source = output / "sources" / name
            if base.hashes(source, True) != entry["frozen_hashes"]:
                raise ValueError("Frozen real-project snapshot changed")
            shutil.copytree(source, projects / name)
    elif job.startswith("propose"):
        for name, catalogs in fixture_catalogs().items():
            project = projects / name
            project.mkdir()
            write_json(project / "WORK.json", catalogs)
        for name, text in {"sparse": "An early project with undecided scope and no established recurring tasks.",
                           "services": "A web client and API service have separate ownership; shared schema edits need coordination. Each service has documented unit checks.",
                           "documents": "A documentation project updates versioned policy notes, checks citations and maintains a glossary. No program implementation is needed."}.items():
            project = projects / name
            project.mkdir()
            (project / "README.md").write_text(text + "\n", encoding="utf-8")
    else:
        for project_name, korean in [("growth", False), ("korean", True)]:
            project = projects / project_name
            project.mkdir()
            for target in ("claude", "codex"):
                agent_dir = project / (".claude/agents" if target == "claude" else ".codex/agents")
                if korean:
                    seed_agent(agent_dir, target, "doc-reviewer", korean=True)
                else:
                    for name, model in [("ticket-extractor", "fable" if target == "claude" else "gpt-fixture-frontier"),
                                        ("fixed-extractor", "opus" if target == "claude" else "gpt-fixture-deep"), ("obsolete-extractor", None)]:
                        seed_agent(agent_dir, target, name, model)
                (agent_dir / "integration.txt").write_bytes(b"Preserve unrelated integration bytes\r\n")
            write_json(project / "WORK.json", {"current_work": "Check document source citations and chapter identifiers; report missing evidence without editing documents." if korean else base.WORK["extract"] + " Current process also requires reporting each malformed ticket's identifier.",
                                              "candidate_pools": fixture_catalogs()["routine"]})
        if job == "validate-both":
            (projects / "growth/.claude/agents/bad.md").write_text("---\nname: broken\nname: duplicated\ndescription: [bad\n---\n", encoding="utf-8")
            (projects / "growth/.codex/agents/bad.toml").write_text('name="a"\nname="b"\n', encoding="utf-8")
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    package = skill.parent / "package.json"
    state = {"host": host, "root": str(root), "python": sys.executable, "skill_source": str(skill), "skill_hashes": base.hashes(skill),
             "package_version": json.loads(package.read_text())["version"] if package.is_file() else None,
             "initial_snapshot": base.hashes(root, True, exclude_git=True)}
    write_json(state_path, state)
    return folder, state


def prompt(state, job):
    host, root = state["host"], Path(state["root"])
    target = target_for(host, job)
    prefix = "/configure-subagents" if host == "claude" else "$configure-subagents"
    p = (f"{prefix}\nUse the installed Skill for projects below {root}. Work only within this evaluation root. "
         "Do not delegate, invoke generated Agents, launch another AI CLI, read personal/global settings or credentials, install dependencies, or execute project programs. "
         "Native local file inspection and the installed Skill's Python helpers (including guarded prepare/check/apply in apply mode) are permitted. "
         f"Use the existing Python with parser dependencies at {state['python']}. Respond in Korean and preserve existing Agent languages. "
         "Keep task-authored outputs within this root and outside Agent discovery paths except authorized installed Agent edits. ")
    if job == "propose-cross" or "both" in job:
        p += f"Configure {'both Claude Code and Codex' if target == 'both' else 'Claude Code' if target == 'claude' else 'Codex'} Agents. "
    if not job.startswith("real-"):
        p += ("This is synthetic QA. WORK.json candidate eligibility is my explicit declaration for the simulated target only. "
              "Fixture model IDs/mappings, prices, qualified work and latency are invented comparison evidence, not actual access, current pricing or measured performance. "
              "Use the supplied frozen provider mappings for this fixture; do not browse for replacement models or test access. ")
    if job.startswith("propose"):
        p += "Propose configurations separately for every project. Do not change any files. Tasks are responsibilities, not a mandatory roster. "
    elif job == "validate-both":
        p += "Validate the existing configurations in all projects, report diagnostics and limitations. Do not fix or write any files. "
    elif job.startswith("real-"):
        p += ("Analyze signal_flare and mosigi, including their current policy/assignment evidence and different execution/review responsibilities. "
              "Improve and APPLY appropriate project Agent configurations where justified; reuse existing Agents or main-session capabilities where sufficient. "
              "Do not resume project work. Preserve source, existing customizations, other target files, base settings and unrelated files. ")
    else:
        p += ("The projects have progressed. Improve and APPLY the selected Agent configurations against current WORK.json evidence. "
              "fixed-extractor's current model is explicitly fixed by me. Other model fields may be reassessed. "
              "Remove obsolete-extractor from the selected target(s); that deletion is explicitly requested. Preserve all other Agent identities, integration comments/fields and unrelated files. ")
    p += ("Separate facts, inferences, unknowns and actual actions. Finish with one JSON object containing cases (array). "
          "Each case has project, target (claude or codex), status, agents (array), diagnostics (array), unknowns (array). "
          "Each proposed/retained Agent has name, model (string or null when omitted), reasoning_effort (string or null), configuration (string), requirement, alternative (string or null), reason, unknowns (array). "
          "Keep unverified performance/access claims separate. Prose may precede the JSON.")
    return p


def final_text(host, events):
    text, models = "", set()
    for event in events:
        message = event.get("message", {})
        if host == "claude" and event.get("type") == "assistant":
            model = message.get("model")
            if model and not model.startswith("<"):
                models.add(model)
            blocks = message.get("content", [])
            if isinstance(blocks, list):
                value = "\n".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
                if value.strip():
                    text = value
        if host == "claude" and event.get("type") == "result":
            text = event.get("result", text)
        if host == "codex" and event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            text = event["item"].get("text", "")
    return text, sorted(models)


def structured_report_ok(report):
    if not isinstance(report, dict) or not isinstance(report.get("cases"), list) or not report["cases"]:
        return False
    for case in report["cases"]:
        if (not isinstance(case, dict) or not isinstance(case.get("project"), str) or case.get("target") not in {"claude", "codex"}
                or not isinstance(case.get("status"), str) or not isinstance(case.get("agents"), list)
                or not isinstance(case.get("diagnostics"), list) or not isinstance(case.get("unknowns"), list)):
            return False
        for agent in case["agents"]:
            if not isinstance(agent, dict) or not all(isinstance(agent.get(k), str) for k in ("name", "configuration", "requirement", "reason")):
                return False
            if any(k not in agent or (agent[k] is not None and not isinstance(agent[k], str)) for k in ("model", "reasoning_effort", "alternative")) or not isinstance(agent.get("unknowns"), list):
                return False
    return True


def independent_static_checks(skill, root, targets):
    result = {}
    for target in targets:
        filename = "validate_agents.py" if target == "claude" else "validate_codex_agents.py"
        spec = importlib.util.spec_from_file_location(f"rc_independent_{target}", skill / "scripts" / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for project in sorted((root / "projects").iterdir()):
            if project.is_dir():
                result[f"{project.name}:{target}"] = module.validate(project)
    return result


def session(output, host, job, skill, run=False, interactive=False, model=None, windows_sandbox=None):
    if run and host == "claude" and job.endswith(("-apply", "-repeat")) and not interactive:
        raise ValueError("Claude application/repeat requires --interactive for native approvals; headless apply is not supported")
    folder, state = prepare_session(output, host, job, skill)
    root = Path(state["root"])
    installation = root / (".claude/skills" if host == "claude" else ".agents/skills") / "configure-subagents"
    if base.hashes(installation) != state["skill_hashes"]:
        raise ValueError("Installed frozen Skill changed")
    instruction = prompt(state, job)
    if not run:
        print(json.dumps({"root": str(root), "target": target_for(host, job), "prompt": instruction}, ensure_ascii=True))
        return
    receipt = folder / (job + "-evidence.json")
    trace = folder / (job + ".stdout.jsonl")
    if receipt.exists() or trace.exists():
        raise ValueError("Do not overwrite attempts; use a fresh campaign/attempt")
    before = base.hashes(root, True, exclude_git=True)
    previous = None
    if job.endswith("-repeat"):
        previous = json.loads((folder / (job.replace("-repeat", "-apply") + "-evidence.json")).read_text())
        if previous["status"] != "finished":
            raise ValueError("A completed apply must precede repeat; independently review it")
        frozen = json.loads((folder / (job.replace("-repeat", "-apply") + "-input.json")).read_text())
        if hashlib.sha256(frozen["prompt"].encode()).hexdigest() != frozen["sha256"] or previous.get("input_sha256") != frozen["sha256"]:
            raise ValueError("Saved application request is damaged")
        if frozen["prompt"] != instruction or state["python"] != sys.executable or previous["requested_host_model"] != model:
            raise ValueError("Repeat request/interpreter/model differs from the frozen application")
        if before != previous["after"]:
            raise ValueError("Repeat start snapshot differs from the application output")
        instruction = frozen["prompt"]
    write_json(folder / (job + "-input.json"), {"prompt": instruction, "sha256": hashlib.sha256(instruction.encode()).hexdigest()})
    cmd = base.command(host, root, folder, job, model, windows_sandbox)
    session_id = None
    if host == "codex":
        cmd[-1:-1] = ["-c", "agents.enabled=false"]
    elif interactive:
        session_id = str(uuid.uuid4())
        cmd = [cmd[0], "--session-id", session_id, "--setting-sources", "project", "--strict-mcp-config", "--no-chrome",
               "--permission-mode", "acceptEdits", "--tools", "Read,Glob,Grep,Skill,Edit,Write,Bash", "--allowedTools", "Read,Glob,Grep,Skill", "--model", model, "--", instruction]
        write_json(folder / (job + "-interactive.json"), {"session_id": session_id, "root": str(root)})
    else:
        for helper in ("validate_codex_agents.py",):
            path = installation / "scripts" / helper
            cmd += ["--allowedTools", f'Bash("{Path(sys.executable).as_posix()}" "{path.as_posix()}" *)',
                    f'Bash("{Path(sys.executable).as_posix()}" -I "{path.as_posix()}" *)']
    env, removed = base.child_environment(host, account_login=host == "claude")
    version = subprocess.check_output([cmd[0], "--version"], encoding="utf-8").strip()
    if previous is not None and version != previous["host_version"]:
        raise ValueError("Host version changed between application and repeat")
    started = time.monotonic()
    if interactive:
        result = subprocess.run(cmd, cwd=root, env=env)
        code = result.returncode
        logs = list((Path.home() / ".claude/projects").rglob(f"{session_id}.jsonl"))
        trace.write_bytes(logs[0].read_bytes() if len(logs) == 1 else b"")
    else:
        with trace.open("w", encoding="utf-8") as stdout, (folder / (job + ".stderr.txt")).open("w", encoding="utf-8") as stderr:
            try:
                result = subprocess.run(cmd, input=instruction, cwd=root, env=env, encoding="utf-8", text=True, stdout=stdout, stderr=stderr, timeout=1800)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = None
    events = []
    for line in trace.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except ValueError:
            pass
    text, models = final_text(host, events)
    (folder / (job + "-final.txt")).write_text(text, encoding="utf-8")
    after = base.hashes(root, True, exclude_git=True)
    changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    targets = [host] if target_for(host, job) == host else [target_for(host, job)] if target_for(host, job) != "both" else ["claude", "codex"]
    def allowed(path):
        if not path.startswith("projects/"):
            return False
        relative = "/".join(path.split("/")[2:])
        return relative.startswith(".configure-subagents-work/") or any(relative.startswith((".claude/agents/" if t == "claude" else ".codex/agents/")) for t in targets)
    report = base.final_json(text)
    status = "finished" if code == 0 else "timeout" if code is None else "host_error"
    if any(e.get("type") == "result" and e.get("is_error") for e in events):
        status = "host_error"
    evidence = {"host": host, "job": job, "target": target_for(host, job), "status": status, "returncode": code,
                "host_version": version, "requested_host_model": model, "observed_host_models": models,
                "input_sha256": hashlib.sha256(instruction.encode()).hexdigest(),
                "actual_model_unverified": not bool(models), "seconds_including_human_waits": round(time.monotonic()-started, 2),
                "skill_hashes": state["skill_hashes"], "package_version": state["package_version"], "interactive_session": session_id,
                "child_environment_omissions": removed, "before": before, "after": after, "changed": changed,
                "outside_selected_scope": [p for p in changed if not allowed(p)], "no_workspace_mutation": not changed,
                "structured_report": structured_report_ok(report), "semantic_review": "pending independent trace/report review",
                "installed_skill_unchanged": base.hashes(installation) == state["skill_hashes"],
                "independent_static_checks": independent_static_checks(skill, root, targets)}
    if job.startswith("real-"):
        evidence["original_source_observation"] = source_observation(output)
    write_json(receipt, evidence)
    print(json.dumps({k:v for k,v in evidence.items() if k not in {"before","after","skill_hashes"}}, ensure_ascii=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "session", "observe-sources"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--project-source", nargs=2, action="append", default=[])
    parser.add_argument("--host", choices=("claude", "codex"))
    parser.add_argument("--job", choices=JOBS)
    parser.add_argument("--skill-source", type=Path)
    parser.add_argument("--host-model")
    parser.add_argument("--windows-sandbox", choices=("elevated", "unelevated"))
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        output = checked_output(args.output)
        if args.action == "capture":
            capture(output, args.project_source)
        elif args.action == "observe-sources":
            print(json.dumps(source_observation(output), ensure_ascii=True))
        else:
            if not args.host or not args.job or not args.skill_source:
                raise ValueError("session requires host, job and installed skill-source")
            if args.interactive and args.host != "claude":
                raise ValueError("Interactive mode is Claude only")
            model = args.host_model or ("claude-opus-5-5" if args.host == "claude" else "gpt-6-astra")
            session(output, args.host, args.job, args.skill_source.resolve(strict=True), args.run, args.interactive, model, args.windows_sandbox)
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        parser.exit(2, f"Evaluation unavailable: {exc}\n")


if __name__ == "__main__":
    main()
