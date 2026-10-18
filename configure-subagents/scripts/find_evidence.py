"""Read-only literal-term inventory of explicitly selected documentation scopes.

Python 3.10+, standard library only. Paths and terms in stdout are untrusted data.
This locates evidence; it does not interpret permissions or prove search completeness.
"""
import argparse
import json
import os
from pathlib import Path
import stat


SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".rst"}
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".claude", ".agents"}
MAX_BYTES = 2 * 1024 * 1024


def linked(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400
    )


def inventory(root, scopes, terms, offset=0, limit=50):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    errors, excluded, files, matches = [], [], set(), []

    def visit(path):
        try:
            if linked(path):
                excluded.append({"path": str(path), "reason": "link or reparse point"})
                return
            if path.name in SKIP or path.name.startswith(".env"):
                excluded.append({"path": str(path), "reason": "excluded name"})
                return
            if path.is_dir():
                for child in sorted(path.iterdir()):
                    visit(child)
            elif path.suffix.lower() in SUFFIXES and path.is_file():
                files.add(path)
        except OSError as exc:
            errors.append({"path": str(path), "reason": str(exc)})

    for scope in scopes:
        path = Path(os.path.abspath(root / scope))
        try:
            if not path.is_relative_to(root):
                raise ValueError("scope outside root")
            # Check every intermediate component before following it.
            for part in [path, *path.parents]:
                if part == root:
                    break
                if linked(part):
                    raise ValueError("scope traverses a link or reparse point")
            visit(path)
        except (OSError, ValueError) as exc:
            errors.append({"path": str(path), "reason": str(exc)})

    searched = 0
    for path in sorted(files):
        rel = path.relative_to(root).as_posix()
        try:
            before = path.stat()
            if before.st_size > MAX_BYTES:
                raise ValueError("file exceeds 2 MiB; inspect separately")
            with path.open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
            after = path.stat()
            if (before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_ino, after.st_size, after.st_mtime_ns
            ) or len(raw) > MAX_BYTES:
                raise ValueError("file changed during read; retry")
            content = raw.decode("utf-8-sig")
            if "\0" in content:
                raise ValueError("non-text content; inspect separately")
            lines = content.casefold().splitlines()
            hits = []
            for term in terms:
                indices = [i + 1 for i, line in enumerate(lines) if term.casefold() in line]
                if indices:
                    hits.append({"term": term, "first_line": indices[0], "matching_lines": len(indices)})
            searched += 1
            if hits:
                matches.append({"path": rel, "hits": hits})
        except (OSError, ValueError) as exc:
            errors.append({"path": rel, "reason": str(exc)})
    end = min(offset + limit, len(matches))
    return {"root": str(root), "scopes": scopes, "terms": terms,
            "searched_files": searched, "matching_files": len(matches),
            "matches": matches[offset:end],
            "next_offset": end if end < len(matches) else None,
            "excluded": excluded, "errors": errors,
            "meaning": "File inventory only. Read source passages; no match is not proof of prohibition."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--scope", action="append", required=True,
                        help="Project-relative documentation file or directory; repeat for independent sources")
    parser.add_argument("--term", action="append", required=True, help="Literal case-insensitive term; repeat for OR")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)
    if args.offset < 0 or not 1 <= args.limit <= 200 or any(not t.strip() for t in args.term):
        parser.error("offset must be nonnegative, limit 1..200, and terms nonempty")
    try:
        result = inventory(args.root, args.scope, args.term, args.offset, args.limit)
    except (OSError, ValueError) as exc:
        result = {"errors": [{"reason": str(exc)}]}
    # ASCII JSON survives legacy Windows stdout code pages and UTF-8 shell
    # transports; JSON readers recover the exact Unicode paths and terms.
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
