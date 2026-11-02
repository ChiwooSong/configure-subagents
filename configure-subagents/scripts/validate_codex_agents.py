#!/usr/bin/env python3
"""Read-only validation of project-scoped standalone Codex agent TOML files."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

REQUIRED = {"name", "description", "developer_instructions"}
STRINGS = REQUIRED | {"model", "model_reasoning_effort", "model_reasoning_summary", "model_verbosity"}
IGNORED = {"sandbox_mode", "approval_policy", "model_provider", "mcp_servers", "service_tier"}
FEATURES = {"shell_tool", "apps", "plugins", "memories", "request_permissions_tool"}
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
CLAUDE_MODELS = {"inherit", "haiku", "sonnet", "opus", "fable"}


class ArgumentError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(message)


def issue(file, field, severity, code, message):
    return dict(file=str(file), field=field, severity=severity, code=code, message=message)


def linked(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def files(directory, diagnostics):
    if linked(directory):
        raise OSError(f"Linked directory was not followed: {directory}")
    for path in sorted(directory.iterdir()):
        if linked(path):
            diagnostics.append(issue(path, "path", "unavailable", "linked_path", "Linked entry was not followed."))
        elif path.is_dir():
            yield from files(path, diagnostics)
        elif path.suffix.lower() == ".toml":
            if path.is_file():
                yield path
            else:
                diagnostics.append(issue(path, "path", "unavailable", "not_regular_file", "Expected a regular file."))


def validate_file(path):
    diagnostics = []

    def add(field, severity, code, message):
        diagnostics.append(issue(path, field, severity, code, message))

    try:
        data = tomllib.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        add("file", "error", "toml", f"Expected UTF-8 TOML without BOM: {exc}")
        return None, diagnostics
    except OSError as exc:
        add("file", "unavailable", "read_error", str(exc))
        return None, diagnostics
    for key in sorted(REQUIRED - data.keys()):
        add(key, "error", "required", "Required field is missing.")
    for key, value in data.items():
        if key in STRINGS:
            if not isinstance(value, str) or not value.strip():
                add(key, "error", "field_type", "Expected a non-empty string.")
        elif key in IGNORED:
            add(key, "warning", "parent_setting", "This setting does not override the parent from a custom agent file. Review effective parent policy; preserve existing content.")
        elif key == "features":
            if not isinstance(value, dict):
                add(key, "error", "field_type", "Expected a table of boolean feature values.")
            else:
                for feature, enabled in value.items():
                    if type(enabled) is not bool:
                        add(f"features.{feature}", "error", "field_type", "Expected a boolean.")
                    if feature not in FEATURES:
                        add(f"features.{feature}", "warning", "unknown_field", "Verify this feature against the target client version.")
        elif key == "skills":
            if not isinstance(value, dict):
                add(key, "error", "field_type", "Expected a skills table.")
            else:
                for field, item in value.items():
                    if field == "include_instructions":
                        if type(item) is not bool:
                            add("skills.include_instructions", "error", "field_type", "Expected a boolean.")
                    elif field == "bundled":
                        if not isinstance(item, dict) or type(item.get("enabled")) is not bool:
                            add("skills.bundled", "error", "field_type", "Expected a table with boolean enabled.")
                        elif set(item) - {"enabled"}:
                            add("skills.bundled", "warning", "unknown_field", "Verify additional fields against the target version.")
                    elif field == "config":
                        if not isinstance(item, list) or any(not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry["path"].strip() or type(entry.get("enabled")) is not bool for entry in item):
                            add("skills.config", "error", "field_type", "Expected entries with a non-empty path and boolean enabled.")
                        elif any(set(entry) - {"path", "enabled"} for entry in item):
                            add("skills.config", "warning", "unknown_field", "Verify additional entry fields against the target version.")
                    else:
                        add(f"skills.{field}", "warning", "unknown_field", "Verify this field against the target version.")
        else:
            add(key, "warning", "unknown_field", "Unrecognized custom-agent field; verify spelling and target version. Preserve existing content.")
    model = data.get("model")
    if isinstance(model, str):
        if model in CLAUDE_MODELS or model.startswith("claude-"):
            add("model", "warning", "target_model_review", "Not an established Codex model selection. Codex inherits by omission, not the literal inherit value. Verify provider eligibility.")
        else:
            add("model", "info", "model_access_unverified", "Static syntax does not establish model access, effort compatibility or actual runtime selection.")
    if data.get("model_reasoning_effort") is not None:
        effort = data["model_reasoning_effort"]
        if isinstance(effort, str) and effort not in EFFORTS:
            add("model_reasoning_effort", "warning", "unverified_value", "Verify effort support for the selected model and target client.")
    if "tools" in data or "disallowedTools" in data:
        add("tools", "warning", "claude_field", "Claude tool lists are not Codex feature controls; do not infer runtime restrictions.")
    if "hooks" in data or "mcp_servers" in data:
        add("capabilities", "warning", "execution_review", "Review executable configuration and provenance. This checker never starts hooks or servers.")
    name = data.get("name")
    if isinstance(name, str) and name.strip():
        if name in {"default", "worker", "explorer"}:
            add("name", "warning", "builtin_override", "This custom name can override a built-in agent; confirm intent.")
    else:
        name = None
    return name, diagnostics


def finish(result):
    severities = {d["severity"] for d in result["diagnostics"]}
    code = 2 if "unavailable" in severities else 1 if "error" in severities else 0
    result.update(exit_code=code, status={0: "passed", 1: "invalid", 2: "unavailable"}[code])
    return result


def validate(project_root, agents_dir=None):
    root = Path(os.path.abspath(project_root))
    directory = Path(agents_dir) if agents_dir is not None else root / ".codex/agents"
    if not directory.is_absolute():
        directory = root / directory
    result = dict(schema_version=1, project_root=str(root), agents_dir=str(directory), files_checked=0, diagnostics=[])
    if tomllib is None:
        result["diagnostics"].append(issue(directory, "dependency", "unavailable", "missing_dependency", "Python 3.10 requires tomli; use an approved environment with the Skill requirements."))
        return finish(result)
    try:
        if not root.is_dir():
            raise OSError(f"Project root is not a directory: {root}")
        # Check every existing component under the explicit root/candidate path.
        current = directory
        while True:
            if current.exists() or current.is_symlink():
                if linked(current):
                    raise OSError(f"Linked path was not followed: {current}")
            if current == root or current.parent == current:
                break
            current = current.parent
        if not directory.exists() and agents_dir is None:
            result["diagnostics"].append(issue(directory, "path", "info", "no_agents", "No project agents directory; empty configuration."))
        elif not directory.is_dir():
            raise OSError(f"Agent directory does not exist: {directory}")
        else:
            names = {}
            for path in files(directory, result["diagnostics"]):
                name, diagnostics = validate_file(path)
                result["files_checked"] += 1
                result["diagnostics"].extend(diagnostics)
                if name is not None:
                    if name in names:
                        result["diagnostics"].append(issue(path, "name", "error", "duplicate_name", f"Same-scope name also occurs in {names[name]}."))
                    names[name] = str(path)
    except (OSError, ValueError, RuntimeError) as exc:
        result["diagnostics"].append(issue(directory, "path", "unavailable", "scan_error", str(exc)))
    return finish(result)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = Parser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--agents-dir")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    output_format = "json" if "json" in argv or "--format=json" in argv else "text"
    try:
        args = parser.parse_args(argv)
        output_format = args.format
        result = validate(args.project_root, args.agents_dir)
    except (ArgumentError, OSError, ValueError) as exc:
        result = finish(dict(schema_version=1, project_root=None, agents_dir=None, files_checked=0,
                             diagnostics=[issue("", "arguments", "unavailable", "arguments", str(exc))]))
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(f"{result['status']}: {result['files_checked']} file(s); exit {result['exit_code']}")
        for item in result["diagnostics"]:
            print(f"{item['severity']} {item['file']} [{item['field']}/{item['code']}] {item['message']}")
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
