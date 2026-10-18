"""Read-only UTF-8 byte facts. Standard library only; JSON goes to stdout."""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(root, filename):
    path = (root / filename).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError("Resolved file is outside the supplied root")
    if not path.is_file():
        raise ValueError("Expected a regular file")
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if identity(before) != identity(after) or len(data) != after.st_size:
        raise ValueError("File changed during inspection; retry before claiming preservation")
    encoding = "utf-8-bom" if data.startswith(b"\xef\xbb\xbf") else "utf-8"
    try:
        data.decode("utf-8-sig")
        # UTF-16/32 ASCII can decode as UTF-8 with NULs; do not mislabel it.
        if b"\0" in data:
            encoding = "unverified"
    except UnicodeDecodeError:
        encoding = "unverified"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    styles = [name for name, count in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if count]
    style = styles[0] if len(styles) == 1 else "mixed" if styles else "none"
    return {
        "path": str(path.relative_to(root)),
        "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "mtime_ns": after.st_mtime_ns, "encoding": encoding,
        "utf8_bom": data.startswith(b"\xef\xbb\xbf"),
        "crlf_bytes": crlf, "lone_lf_bytes": lf, "lone_cr_bytes": cr,
        "newline_style": style if encoding != "unverified" else "unverified",
        "final_newline": data.endswith((b"\n", b"\r")) if encoding != "unverified" else None,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Explicit permitted read boundary")
    parser.add_argument("files", nargs="+", help="Explicit paths, relative to root or absolute")
    args = parser.parse_args(argv)
    result = {"files": [], "errors": []}
    try:
        root = Path(args.root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Root must be a directory")
    except (OSError, ValueError, RuntimeError) as exc:
        result["errors"].append({"path": args.root, "message": str(exc)})
    else:
        for filename in args.files:
            try:
                result["files"].append(inspect(root, filename))
            except (OSError, ValueError, RuntimeError) as exc:
                result["errors"].append({"path": filename, "message": str(exc)})
    result["exit_code"] = 2 if result["errors"] else 0
    print(json.dumps(result, ensure_ascii=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
