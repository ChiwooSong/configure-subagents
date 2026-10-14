#!/usr/bin/env python3
"""Read-only validation of one Claude Code project agent tree. Python 3.10+."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys

try:
    import yaml
except ImportError:
    yaml = None


if yaml is not None:
    class UniqueSafeLoader(yaml.SafeLoader):
        """Reject explicit duplicate keys; preserve standard YAML merge overrides."""

        def construct_mapping(self, node, deep=False):
            seen = set()
            for key_node, _ in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    key = "<<"
                else:
                    key = self.construct_object(key_node, deep=True)
                try:
                    duplicate = key in seen
                    seen.add(key)
                except TypeError as exc:
                    raise yaml.constructor.ConstructorError(
                        None, None, "unhashable mapping key", key_node.start_mark
                    ) from exc
                if duplicate:
                    raise yaml.constructor.ConstructorError(
                        None, None, f"duplicate key: {key!r}", key_node.start_mark
                    )
            return super().construct_mapping(node, deep=deep)


STRINGS = {"name", "description", "model", "permissionMode", "memory", "effort",
           "isolation", "color", "initialPrompt"}
BOOLEANS = {"background", "omitClaudeMd"}
MAPPINGS = {"hooks", "experimental"}
KNOWN_FIELDS = STRINGS | BOOLEANS | MAPPINGS | {
    "tools", "disallowedTools", "maxTurns", "skills", "mcpServers"
}
ENUMS = {
    "permissionMode": {"default", "manual", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"},
    "memory": {"user", "project", "local"},
    "effort": {"low", "medium", "high", "xhigh", "max"},
    "isolation": {"worktree"},
    "color": {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"},
}
MODEL_ALIASES = {"inherit", "sonnet", "opus", "haiku", "fable"}
# A diagnostic vocabulary, not an exhaustive runtime tool allowlist.
FAMILIAR_TOOLS = {"Read", "Glob", "Grep", "Write", "Edit", "Bash", "PowerShell",
                  "WebFetch", "WebSearch", "NotebookEdit", "Skill", "Agent", "Task",
                  "TodoWrite", "TaskCreate", "TaskGet", "TaskList", "TaskUpdate"}
TOOL_TOKEN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]*(?:\([^\r\n]*\))?$")


class ArgumentError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(message)


def issue(file, field, severity, code, message, line=None):
    result = dict(file=str(file), field=field, severity=severity, code=code, message=message)
    if line is not None:
        result["line"] = line
    return result


def linked(path):
    """Include Windows junctions, even on Python 3.10 without Path.is_junction."""
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def agent_files(directory, diagnostics):
    try:
        if linked(directory):
            diagnostics.append(issue(directory, "path", "unavailable", "linked_path", "Linked directory was not followed."))
            return
        with os.scandir(directory) as entries:
            items = sorted(entries, key=lambda item: item.name)
        for entry in items:
            path = Path(entry.path)
            if linked(path):
                diagnostics.append(issue(path, "path", "unavailable", "linked_path", "Linked entry was not followed."))
            elif entry.is_dir(follow_symlinks=False):
                yield from agent_files(path, diagnostics)
            elif path.suffix.lower() == ".md":
                if entry.is_file(follow_symlinks=False):
                    yield path
                else:
                    diagnostics.append(issue(path, "path", "unavailable", "not_regular_file", "Agent entry is not a regular file."))
    except OSError as exc:
        diagnostics.append(issue(directory, "path", "unavailable", "read_error", str(exc)))


def split_tools(value):
    # Commas in a tool specifier belong to that specifier, not to the list.
    if isinstance(value, str):
        return re.split(r",(?![^()]*\))", value)
    return value


def validate_file(path):
    diagnostics = []

    def add(field, severity, code, message, line=None):
        diagnostics.append(issue(path, field, severity, code, message, line))

    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        add("file", "error", "encoding", f"Expected UTF-8: {exc}")
        return None, diagnostics
    except OSError as exc:
        add("file", "unavailable", "read_error", str(exc))
        return None, diagnostics

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        add("frontmatter", "error", "frontmatter", "Expected opening --- on the first line.", 1)
        return None, diagnostics
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        add("frontmatter", "error", "frontmatter", "Missing closing ---.", 1)
        return None, diagnostics
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=UniqueSafeLoader)
    except (yaml.YAMLError, RecursionError, ValueError) as exc:
        mark = getattr(exc, "problem_mark", None)
        add("frontmatter", "error", "yaml", str(exc), mark.line + 2 if mark else None)
        return None, diagnostics
    if not isinstance(data, dict):
        add("frontmatter", "error", "mapping_required", "Frontmatter must be a YAML mapping.", 2)
        return None, diagnostics

    for field in ("name", "description"):
        if field not in data:
            add(field, "error", "required", "Required field is missing.")
    for field, value in data.items():
        if not isinstance(field, str):
            add(str(field), "error", "field_name", "Field names must be strings.")
        elif field not in KNOWN_FIELDS:
            add(field, "warning", "unknown_field", "Unrecognized field; verify spelling and target version. Preserve existing content.")
        elif field in STRINGS:
            if not isinstance(value, str) or (field != "initialPrompt" and not value.strip()):
                add(field, "error", "field_type", "Expected a non-empty string (initialPrompt may be empty).")
            elif field in ENUMS and value not in ENUMS[field]:
                add(field, "warning", "unverified_value", "Value is outside the documented vocabulary; check target version.")
        elif field in BOOLEANS and type(value) is not bool:
            add(field, "error", "field_type", "Expected a boolean.")
        elif field in MAPPINGS and not isinstance(value, dict):
            add(field, "error", "field_type", "Expected a mapping.")
        elif field == "maxTurns" and (type(value) is not int or value <= 0):
            add(field, "error", "field_type", "Expected a positive integer, not a boolean.")
        elif field == "skills":
            if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
                add(field, "error", "field_type", "Expected a list of non-empty skill names.")
        elif field == "mcpServers":
            if not isinstance(value, list) or any(
                not ((isinstance(x, str) and x.strip()) or (isinstance(x, dict) and x and all(
                    isinstance(k, str) and k.strip() and isinstance(v, dict) for k, v in x.items()
                ))) for x in value
            ):
                add(field, "error", "field_type", "Expected a list of server names or inline server mappings.")

    # Capabilities worth reviewing, even when the documented schema accepts them.
    # Presence warnings deliberately include empty or malformed values; type
    # diagnostics above still apply and no hooks/servers are ever executed here.
    if "hooks" in data:
        add("hooks", "warning", "executes_commands", "Hooks can execute commands independently of the agent tool list. Review each hook and its source before use.")
    if "mcpServers" in data:
        add("mcpServers", "warning", "external_servers", "MCP servers may start processes or access the network. Review server configuration and provenance before use.")
    permission_mode = data.get("permissionMode")
    permission_warnings = {
        "bypassPermissions": "Requests skipped permission prompts when the parent session permits this mode; review effective policy before use.",
        "acceptEdits": "May automatically accept file edits and filesystem operations; review the allowed scope before use.",
        "auto": "Uses automated permission decisions rather than manual prompts; review effective policy before use.",
    }
    if isinstance(permission_mode, str) and permission_mode in permission_warnings:
        add("permissionMode", "warning", "permission_review", permission_warnings[permission_mode])

    name = data.get("name")
    if isinstance(name, str) and name.strip():
        if len(name) > 256 or ":" in name or name.startswith("-"):
            add("name", "error", "invalid_name", "Names must be at most 256 characters, without ':' or a leading '-'.")
        elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            add("name", "warning", "name_convention", "New names should use lowercase kebab-case; check existing name compatibility.")
    else:
        name = None
    model = data.get("model")
    if isinstance(model, str) and model.strip() and model not in MODEL_ALIASES:
        add("model", "warning", "unverified_model", "Model ID is not a known alias; verify target provider and account access. It may be valid.")

    parsed = {}
    for field in ("tools", "disallowedTools"):
        if field not in data:
            continue
        value = split_tools(data[field])
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
            add(field, "error", "field_type", "Expected a comma-separated string or a list of non-empty strings.")
            continue
        parsed[field] = set()
        for item in value:
            token = item.strip()
            base = token.split("(", 1)[0]
            parsed[field].add(base)
            if not TOOL_TOKEN.fullmatch(token):
                add(field, "warning", "unverified_tool_syntax", f"Check tool syntax: {token!r}.")
            elif base not in FAMILIAR_TOOLS:
                add(field, "warning", "unverified_tool", f"Check tool availability: {base!r}.")
            if field == "disallowedTools" and "(" in token:
                add(field, "warning", "whole_tool_denial", f"Specifier may deny all of {base}, not only the specified command.")
    if "tools" not in data:
        add("tools", "warning", "tools_inherited", "Omitted tools inherits available tools; review whether that matches the role.")
    elif data["tools"] == []:
        add("tools", "warning", "empty_tools", "Empty tool list: verify target runtime behavior.")
    overlap = parsed.get("tools", set()) & parsed.get("disallowedTools", set())
    if overlap:
        add("tools", "warning", "tool_overlap", "Denied tools remove allowed tools: " + ", ".join(sorted(overlap)))
    if not "\n".join(lines[end + 1:]).strip():
        add("body", "warning", "empty_body", "No role instructions; check whether this is intentional.")
    return name, diagnostics


def validate(project_root, agents_dir=None):
    diagnostics = []
    root = Path(os.path.abspath(project_root))
    directory = Path(agents_dir) if agents_dir is not None else root / ".claude" / "agents"
    if not directory.is_absolute():
        directory = root / directory
    directory = Path(os.path.abspath(directory))
    result = dict(schema_version=1, project_root=str(root), agents_dir=str(directory), files_checked=0, diagnostics=diagnostics)
    if yaml is None:
        diagnostics.append(issue(directory, "dependency", "unavailable", "missing_dependency", "PyYAML is required; use the skill requirements.txt in an approved Python environment."))
    else:
        try:
            if not root.is_dir():
                raise OSError(f"Project root is not a directory: {root}")
            claude_dir = root / ".claude"
            if agents_dir is None and (claude_dir.exists() or claude_dir.is_symlink()) and linked(claude_dir):
                raise OSError("Default .claude directory is linked; scope was not scanned.")
            if not directory.exists() and not directory.is_symlink() and agents_dir is None:
                diagnostics.append(issue(directory, "path", "info", "no_agents", "No project agents directory; empty configuration."))
            elif not directory.is_dir() and not directory.is_symlink():
                raise OSError(f"Agent directory does not exist or is not a directory: {directory}")
            else:
                names = {}
                for path in agent_files(directory, diagnostics):
                    name, found = validate_file(path)
                    result["files_checked"] += 1
                    diagnostics.extend(found)
                    if name is not None:
                        if name in names:
                            diagnostics.append(issue(path, "name", "error", "duplicate_name", f"Same-scope name {name!r} also occurs in {names[name]}."))
                        else:
                            names[name] = str(path)
        except (OSError, ValueError, RuntimeError) as exc:
            diagnostics.append(issue(directory, "path", "unavailable", "scan_error", str(exc)))
    return finish(result)


def finish(result):
    severities = {d["severity"] for d in result["diagnostics"]}
    code = 2 if "unavailable" in severities else 1 if "error" in severities else 0
    result.update(exit_code=code, status={0: "passed", 1: "invalid", 2: "unavailable"}[code])
    return result


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = Parser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--agents-dir", help="Complete candidate tree; relative paths are relative to project root.")
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
            line = f":{item['line']}" if "line" in item else ""
            print(f"{item['severity']} {item['file']}{line} [{item['field']}/{item['code']}] {item['message']}")
    return result["exit_code"]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())
