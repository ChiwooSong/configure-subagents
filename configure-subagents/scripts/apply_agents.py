#!/usr/bin/env python3
"""Guarded project Agent file application. Not a sandbox or semantic reviewer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import uuid

sys.dont_write_bytecode = True
SCOPES = {"claude": (".claude/agents", ".md", "validate_agents.py"),
          "codex": (".codex/agents", ".toml", "validate_codex_agents.py")}
STORAGE = ".configure-subagents-work"


class ToolError(Exception):
    def __init__(self, message, diagnostics=None):
        super().__init__(message)
        self.diagnostics = diagnostics


class Rejected(ToolError):
    pass


class Unavailable(ToolError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Rejected(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def exists(path):
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def identity(info):
    return [info.st_dev, info.st_ino]


def facts(path, data=None):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise Rejected(f"Linked entry: {path}")
    directory = stat.S_ISDIR(info.st_mode)
    if not directory and not stat.S_ISREG(info.st_mode):
        raise Rejected(f"Not a regular file/directory: {path}")
    if not directory and info.st_nlink != 1:
        raise Rejected(f"Hard-linked file: {path}")
    return {"directory": directory, "identity": identity(info), "mtime_ns": info.st_mtime_ns,
            "atime_ns": info.st_atime_ns, "mode": stat.S_IMODE(info.st_mode),
            "sha256": None if directory else digest(path.read_bytes() if data is None else data)}


def signature(value):
    # Reads can update atime, and recovery renames can update ctime.
    return {k: v for k, v in value.items() if k != "atime_ns"}


def guard(root, path):
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise Rejected(f"Path outside project: {path}") from exc
    current = root
    for part in ("", *relative.parts):
        if part:
            current = current / part
        if exists(current):
            info = facts(current) if current == path else facts_directory(current)
            if current != path and not info["directory"]:
                raise Rejected(f"Non-directory parent: {current}")


def facts_directory(path):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise Rejected(f"Linked or non-directory parent: {path}")
    return {"directory": True, "identity": identity(info)}


def project_root(value):
    path = Path(os.path.abspath(value))
    # Windows 8.3 spellings can differ from GetFinalPathName without being
    # links. Inspect actual components, then use the canonical spelling.
    for component in (path, *path.parents):
        facts_directory(component)
    return Path(os.path.realpath(path))


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\0" in value:
        raise Rejected("Expected a portable relative Agent path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in {".", ".."} for p in value.split("/")) or path.as_posix() != value:
        raise Rejected(f"Unsafe relative path: {value}")
    return value


def snapshot(root, tree):
    guard(root, tree)
    if not exists(tree):
        return None
    if not facts(tree)["directory"]:
        raise Rejected(f"Expected an Agent directory: {tree}")
    entries = {}

    def visit(path, relative):
        guard(root, path)
        before = facts(path)
        if before["directory"]:
            entries[relative] = before
            for child in sorted(path.iterdir()):
                visit(child, f"{relative}/{child.name}" if relative else child.name)
            if signature(facts(path)) != signature(before):
                raise Rejected(f"Directory changed during inspection: {path}")
        else:
            data = path.read_bytes()
            after = facts(path, data)
            if signature(after) != signature(before):
                raise Rejected(f"File changed during inspection: {path}")
            entries[relative] = after
    visit(tree, "")
    return entries


def comparable(tree):
    return None if tree is None else {k: signature(v) for k, v in tree.items()}


def payload(tree):
    return None if tree is None else {k: {"directory": v["directory"], "sha256": v["sha256"]} for k, v in tree.items()}


def write_record(root, path, value):
    guard(root, path)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    guard(root, temporary)
    record = {"payload": value, "sha256": digest(canonical(value))}
    with temporary.open("xb") as stream:
        stream.write(canonical(record) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    guard(root, path)
    os.replace(temporary, path)


def read_record(root, path):
    guard(root, path)
    record = json.loads(path.read_bytes())
    if not isinstance(record, dict) or set(record) != {"payload", "sha256"} or digest(canonical(record["payload"])) != record["sha256"]:
        raise Rejected(f"Damaged task record: {path}")
    return record["payload"]


def copy_snapshot(root, source, destination, tree):
    guard(root, destination)
    destination.mkdir()
    for relative, info in (tree or {}).items():
        if not relative:
            continue
        safe_relative(relative)
        target = destination / relative
        guard(root, target)
        if info["directory"]:
            target.mkdir()
        else:
            current = source / relative
            guard(root, current)
            data = current.read_bytes()
            if signature(facts(current, data)) != signature(info):
                raise Rejected(f"Original changed while preparing: {current}")
            with target.open("xb") as stream:
                stream.write(data)
            os.chmod(target, info["mode"])
            os.utime(target, ns=(info["atime_ns"], info["mtime_ns"]))


def selected(target):
    if target not in {"claude", "codex", "both"}:
        raise Rejected("Unknown target")
    return list(SCOPES) if target == "both" else [target]


def prepare(root, target, allow_delete=()):
    targets = selected(target)
    before = {name: snapshot(root, root / SCOPES[name][0]) for name in targets}
    allowed = {name: [] for name in targets}
    for name, relative in allow_delete:
        relative = safe_relative(relative)
        if name not in targets or not relative.lower().endswith(SCOPES[name][1]):
            raise Rejected("Deletion must name an Agent file in a selected target")
        info = (before[name] or {}).get(relative)
        if not info or info["directory"]:
            raise Rejected(f"Deletion must name an existing Agent file: {name}/{relative}")
        allowed[name].append(relative)
    storage = root / STORAGE
    guard(root, storage)
    storage.mkdir(exist_ok=True)
    transaction_id = uuid.uuid4().hex
    transaction = storage / transaction_id
    guard(root, transaction)
    transaction.mkdir()
    (transaction / "originals").mkdir()
    (transaction / "candidate").mkdir()
    for name in targets:
        for folder in ("originals", "candidate"):
            copy_snapshot(root, root / SCOPES[name][0], transaction / folder / name, before[name])
        if comparable(snapshot(root, root / SCOPES[name][0])) != comparable(before[name]):
            raise Rejected("Original changed during preparation; use a fresh task")
    originals = {name: payload(snapshot(root, transaction / "originals" / name)) for name in targets}
    manifest = {"schema_version": 1, "transaction": transaction_id, "root": str(root),
                "root_identity": facts_directory(root)["identity"], "targets": targets,
                "before": before, "originals": originals, "allow_delete": allowed}
    write_record(root, transaction / "manifest.json", manifest)
    write_record(root, transaction / "journal.json", {"state": "prepared"})
    return {"transaction": transaction_id, "status": "prepared", "candidate_paths": {n: str(transaction / "candidate" / n) for n in targets},
            "backup_paths": {n: str(transaction / "originals" / n) for n in targets}}


def load(root, target, transaction_id):
    if not isinstance(transaction_id, str) or not re.fullmatch(r"[0-9a-f]{32}", transaction_id):
        raise Rejected("Invalid transaction ID")
    transaction = root / STORAGE / transaction_id
    guard(root, transaction)
    manifest = read_record(root, transaction / "manifest.json")
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or manifest.get("root") != str(root)
            or manifest.get("transaction") != transaction_id or manifest.get("targets") != selected(target)
            or manifest.get("root_identity") != facts_directory(root)["identity"]):
        raise Rejected("Task record does not match this project/target")
    for name in manifest["targets"]:
        for relative in (manifest["before"][name] or {}):
            if relative:
                safe_relative(relative)
        for relative in manifest["allow_delete"][name]:
            safe_relative(relative)
        if payload(snapshot(root, transaction / "originals" / name)) != manifest["originals"][name]:
            raise Rejected("Original backup changed; manual inspection required")
    journal = read_record(root, transaction / "journal.json")
    if not isinstance(journal, dict) or journal.get("state") not in {"prepared", "applying", "complete", "failed", "recovery_required"}:
        raise Rejected("Invalid task state")
    if journal["state"] in {"applying", "failed", "recovery_required"}:
        raise Rejected("Incomplete/failed task cannot be reused; inspect originals and journal for manual recovery")
    return transaction, manifest, journal


def format_facts(data):
    try:
        data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise Rejected("Modified Agent must be UTF-8") from exc
    if b"\0" in data:
        raise Rejected("NUL/unverified encoding in modified Agent")
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    styles = [name for name, count in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if count]
    if len(styles) > 1 or cr:
        raise Rejected("Modified Agent uses unsupported mixed/CR-only newlines")
    return (data.startswith(b"\xef\xbb\xbf"), styles[0] if styles else "none", data.endswith(b"\n"))


def validator(name, root, candidate):
    path = Path(__file__).with_name(SCOPES[name][2])
    spec = importlib.util.spec_from_file_location(f"guarded_{name}_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(root, candidate)


def inspect_candidate(root, transaction, manifest, journal):
    if journal["state"] == "complete":
        candidates = {name: payload(snapshot(root, transaction / "candidate" / name)) for name in manifest["targets"]}
        if digest(canonical(candidates)) != journal["candidate_digest"]:
            raise Rejected("Candidate changed after completed task; prepare a fresh task")
        for name in manifest["targets"]:
            if comparable(snapshot(root, root / SCOPES[name][0])) != journal["after"][name]:
                raise Rejected("Installed Agent tree changed after completed task")
        return {"status": "unchanged", "candidate_digest": journal["candidate_digest"], "changes": [], "diagnostics": []}, {}
    changes, diagnostics, candidates, buffers = [], [], {}, {}
    for name in manifest["targets"]:
        live = root / SCOPES[name][0]
        if comparable(snapshot(root, live)) != comparable(manifest["before"][name]):
            raise Rejected(f"Original changed after prepare: {name}; recompute in a fresh task")
        candidate = transaction / "candidate" / name
        tree = snapshot(root, candidate)
        if tree is None:
            raise Rejected(f"Missing complete candidate tree: {name}")
        candidates[name] = payload(tree)
        previous = manifest["before"][name] or {}
        for relative, info in previous.items():
            if info["directory"] and relative not in tree:
                raise Rejected("Preserve existing directories in the complete candidate")
        for relative in sorted(previous.keys() | tree.keys()):
            old, new = previous.get(relative), tree.get(relative)
            if not relative:
                continue
            safe_relative(relative)
            if (old and old["directory"]) or (new and new["directory"]):
                if old and new and old["directory"] != new["directory"]:
                    raise Rejected("File/directory replacement is outside Agent scope")
                if not old and not any(p.startswith(relative + "/") and not i["directory"] and p.lower().endswith(SCOPES[name][1]) for p, i in tree.items()):
                    raise Rejected("New directories must contain Agent files")
                continue
            if old and new and old["sha256"] == new["sha256"]:
                continue
            if not relative.lower().endswith(SCOPES[name][1]):
                raise Rejected(f"Non-Agent file change: {name}/{relative}")
            if new is None and relative not in manifest["allow_delete"][name]:
                raise Rejected(f"Deletion not allowed: {name}/{relative}")
            action = "add" if old is None else "delete" if new is None else "modify"
            if new is not None:
                data = (candidate / relative).read_bytes()
                if digest(data) != new["sha256"]:
                    raise Rejected("Candidate changed during inspection")
                fmt = format_facts(data)
                if name == "codex" and fmt[0]:
                    raise Rejected("Codex TOML must not use a BOM")
                if old:
                    original = (transaction / "originals" / name / relative).read_bytes()
                    if format_facts(original) != fmt:
                        raise Rejected(f"Encoding/BOM/newline/final-newline change: {name}/{relative}")
                buffers[(name, relative)] = data
            changes.append({"target": name, "path": relative, "action": action})
        result = validator(name, root, candidate)
        diagnostics.extend({**d, "target": name} for d in result["diagnostics"])
        if result["exit_code"] == 2:
            raise Unavailable("Candidate validation unavailable", diagnostics)
        if result["exit_code"]:
            raise Rejected("Candidate validation failed", diagnostics)
        if payload(snapshot(root, candidate)) != candidates[name]:
            raise Rejected("Candidate changed while validating")
    buffers["checked_trees"] = candidates
    return {"status": "checked", "candidate_digest": digest(canonical(candidates)), "changes": changes, "diagnostics": diagnostics}, buffers


def make_parents(root, directory, created):
    if directory == root:
        return
    guard(root, directory)
    if not exists(directory):
        make_parents(root, directory.parent, created)
        directory.mkdir()
        created.append((directory, facts_directory(directory)["identity"]))
    elif not facts(directory)["directory"]:
        raise Rejected(f"Not a directory: {directory}")


def publish_entry(root, path, data, mode, record):
    """Exclusive create after moving any original aside; injectable in tests."""
    guard(root, path)
    with path.open("xb") as stream:
        record["output_identity"] = identity(os.fstat(stream.fileno()))
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
        if os.chmod in os.supports_fd:
            os.chmod(stream.fileno(), mode)
        else:
            guard(root, path)
            if identity(path.lstat()) != record["output_identity"]:
                raise Rejected("Output replaced before setting mode")
            os.chmod(path, mode)
        info = os.fstat(stream.fileno())
        expected = {"directory": False, "identity": identity(info), "mtime_ns": info.st_mtime_ns,
                    "mode": stat.S_IMODE(info.st_mode), "sha256": digest(data)}
    if signature(facts(path)) != expected:
        raise Rejected("Output changed before ownership could be recorded")
    record["output"] = expected


def apply(root, target, transaction_id, candidate_digest):
    transaction, manifest, journal = load(root, target, transaction_id)
    checked, buffers = inspect_candidate(root, transaction, manifest, journal)
    if candidate_digest != checked["candidate_digest"]:
        raise Rejected("Candidate digest does not match the checked candidate")
    if journal["state"] == "complete":
        return checked
    records, created = [], []
    write_record(root, transaction / "journal.json", {"state": "applying", "candidate_digest": candidate_digest, "records": []})
    try:
        # Both namespaces must still match before the first write.
        for name in manifest["targets"]:
            if comparable(snapshot(root, root / SCOPES[name][0])) != comparable(manifest["before"][name]):
                raise Rejected("Original changed immediately before application")
        for change in checked["changes"]:
            name, relative = change["target"], change["path"]
            path = root / SCOPES[name][0] / relative
            guard(root, path)
            old = (manifest["before"][name] or {}).get(relative)
            if old is None:
                if exists(path):
                    raise Rejected(f"Destination appeared: {path}")
            elif not exists(path) or signature(facts(path)) != signature(old):
                raise Rejected(f"Original changed before write: {path}")
            record = {**change, "moved": False}
            records.append(record)
            moved = transaction / "withdrawn" / name / relative
            if old:
                make_parents(root, moved.parent, created)
                guard(root, moved)
                if exists(moved):
                    raise Rejected("Recovery path already occupied")
                os.rename(path, moved)
                record["moved"] = True
                if signature(facts(moved)) != signature(old):
                    raise Rejected("Original changed while moving aside")
            if change["action"] != "delete":
                make_parents(root, path.parent, created)
                publish_entry(root, path, buffers[(name, relative)], old["mode"] if old else 0o600, record)
            write_record(root, transaction / "journal.json", {"state": "applying", "candidate_digest": candidate_digest, "records": records})
        # Check every file, including untouched files, against the candidate.
        after = {}
        for name in manifest["targets"]:
            current = snapshot(root, root / SCOPES[name][0])
            candidate = snapshot(root, transaction / "candidate" / name)
            expected = buffers["checked_trees"][name]
            if payload(candidate) != expected:
                raise Rejected("Candidate changed after the checked digest was bound")
            if current is None:
                if any(not i["directory"] for i in expected.values()):
                    raise Rejected("Installed tree missing")
            elif payload(current) != expected:
                raise Rejected("Installed bytes/tree do not match the validated candidate")
            for relative, info in (manifest["before"][name] or {}).items():
                if not info["directory"] and not any(c["target"] == name and c["path"] == relative for c in checked["changes"]):
                    if not current or signature(current.get(relative, {})) != signature(info):
                        raise Rejected("Untouched file changed during application")
            result = validator(name, root, root / SCOPES[name][0] if current is not None else None)
            if result["exit_code"]:
                raise Unavailable("Installed static validation failed", result["diagnostics"])
            if comparable(snapshot(root, root / SCOPES[name][0])) != comparable(current):
                raise Rejected("Installed tree changed during final validation")
            after[name] = comparable(current)
        write_record(root, transaction / "journal.json", {"state": "complete", "candidate_digest": candidate_digest, "after": after, "records": records})
        return {**checked, "status": "applied" if checked["changes"] else "unchanged"}
    except Exception as exc:
        unrecovered = []
        for record in reversed(records):
            name, relative = record["target"], record["path"]
            path = root / SCOPES[name][0] / relative
            moved = transaction / "withdrawn" / name / relative
            old = (manifest["before"][name] or {}).get(relative)
            try:
                guard(root, path)
                guard(root, moved)
                if exists(path):
                    # Partial/unrecorded writes are not assumed safe to remove.
                    if not record.get("output") or signature(facts(path)) != record["output"]:
                        raise Rejected("Concurrent or incomplete output retained")
                    path.unlink()
                elif record.get("output"):
                    raise Rejected("Another writer removed output; do not restore over its decision")
                if record["moved"]:
                    if signature(facts(moved)) != signature(old):
                        raise Rejected("Moved original changed")
                    os.rename(moved, path)
            except Exception:
                unrecovered.append({"target": name, "path": relative, "backup": str(transaction / "originals" / name / relative)})
        for directory, expected_id in reversed(created):
            try:
                guard(root, directory)
                if facts_directory(directory)["identity"] == expected_id and not any(directory.iterdir()):
                    directory.rmdir()
            except (OSError, Rejected):
                pass
        state = "recovery_required" if unrecovered else "failed"
        try:
            write_record(root, transaction / "journal.json", {"state": state, "candidate_digest": candidate_digest, "records": records, "unrecovered": unrecovered})
        except Exception:
            unrecovered.append({"path": str(transaction), "message": "Journal unavailable; manual inspection required"})
            state = "recovery_required"
        return {**checked, "status": state, "exit_code": 2, "diagnostics": checked["diagnostics"] + (getattr(exc, "diagnostics", None) or [{"severity": "unavailable", "message": str(exc)}]), "unrecovered": unrecovered}


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "check", "apply"))
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--target", choices=("claude", "codex", "both"), required=True)
    parser.add_argument("--transaction")
    parser.add_argument("--candidate-digest")
    parser.add_argument("--allow-delete", nargs=2, action="append", default=[], metavar=("TARGET", "RELATIVE_PATH"))
    result = {"schema_version": 1, "status": "rejected", "diagnostics": [], "unrecovered": [], "changes": [], "exit_code": 1}
    try:
        args = parser.parse_args(argv)
        result.update(operation=args.operation, target=args.target, transaction=args.transaction)
        root = project_root(args.project_root)
        if args.operation != "prepare" and args.allow_delete:
            raise Rejected("Deletion allowance belongs to prepare only")
        if args.operation == "prepare":
            if args.transaction or args.candidate_digest:
                raise Rejected("prepare creates a fresh transaction")
            value = prepare(root, args.target, args.allow_delete)
        elif args.operation == "check":
            if args.candidate_digest:
                raise Rejected("check returns the candidate digest")
            transaction, manifest, journal = load(root, args.target, args.transaction)
            value, _ = inspect_candidate(root, transaction, manifest, journal)
        else:
            if not args.candidate_digest:
                raise Rejected("apply requires the digest returned by check")
            value = apply(root, args.target, args.transaction, args.candidate_digest)
        result.update({"exit_code": 0, **value})
    except Rejected as exc:
        result.update(status="rejected", exit_code=1, diagnostics=exc.diagnostics or [{"severity": "error", "message": str(exc)}])
    except (OSError, Unavailable, ValueError, KeyError, TypeError, RuntimeError) as exc:
        result.update(status="unavailable", exit_code=2, diagnostics=getattr(exc, "diagnostics", None) or [{"severity": "unavailable", "message": str(exc)}])
    print(json.dumps(result, ensure_ascii=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
