import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "configure-subagents/scripts/find_evidence.py"
spec = importlib.util.spec_from_file_location("find_evidence", SCRIPT)
finder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finder)


class EvidenceInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, path, data):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def test_independent_scopes_unicode_literal_or_and_no_changes(self):
        a = self.write("계획/base.md", b"Default\r\nSDK compile\r\n")
        b = self.write("handoffs/result.md", "전용 시험\nSDK compile\n".encode())
        before = [(p, p.read_bytes(), p.stat().st_mtime_ns) for p in (a, b)]
        out = finder.inventory(self.root, ["계획", "handoffs", "계획/base.md"], ["sdk", "전용", ".*"])
        self.assertEqual(out["matching_files"], 2)
        self.assertEqual(out["searched_files"], 2)
        self.assertEqual(out["errors"], [])
        self.assertFalse(any(h["term"] == ".*" for m in out["matches"] for h in m["hits"]))
        self.assertEqual([(p, p.read_bytes(), p.stat().st_mtime_ns) for p in (a, b)], before)

    def test_pagination_does_not_silently_hide_later_sources(self):
        for name in ("a", "b", "c"):
            self.write(name + ".md", b"verify\nverify\n")
        first = finder.inventory(self.root, ["."], ["verify"], limit=1)
        self.assertEqual(first["matching_files"], 3)
        self.assertEqual(first["next_offset"], 1)
        rest = finder.inventory(self.root, ["."], ["verify"], offset=1, limit=2)
        self.assertEqual([m["path"] for m in first["matches"] + rest["matches"]], ["a.md", "b.md", "c.md"])
        self.assertIsNone(rest["next_offset"])

    def test_missing_and_outside_scopes_are_incomplete_not_empty_success(self):
        out = finder.inventory(self.root, ["missing", "../outside"], ["verify"])
        self.assertEqual(len(out["errors"]), 2)

    def test_reparse_ancestor_not_followed(self):
        self.write("linked/sub/evidence.md", b"verify")
        original = finder.linked
        with patch.object(finder, "linked", side_effect=lambda p: p.name == "linked" or original(p)):
            out = finder.inventory(self.root, ["linked/sub"], ["verify"])
        self.assertEqual(out["searched_files"], 0)
        self.assertEqual(len(out["errors"]), 1)

    def test_sensitive_names_excluded_without_reading(self):
        self.write("docs/a.md", b"verify")
        self.write("docs/.env.json", b"verify SECRET")
        self.write("docs/node_modules/a.md", b"verify")
        out = finder.inventory(self.root, ["docs"], ["verify"])
        self.assertEqual(out["searched_files"], 1)
        self.assertEqual(len(out["excluded"]), 2)

    def test_unreadable_encoding_and_oversized_files_are_reported(self):
        self.write("bad.md", b"\xff")
        self.write("large.md", b"a" * (finder.MAX_BYTES + 1))
        self.write("utf16.md", b"a\0")
        out = finder.inventory(self.root, ["."], ["a"])
        self.assertEqual(len(out["errors"]), 3)
        self.assertEqual(out["searched_files"], 0)

    def test_denied_read_is_not_no_match(self):
        self.write("a.md", b"verify")
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            out = finder.inventory(self.root, ["."], ["verify"])
        self.assertEqual(len(out["errors"]), 1)
        self.assertEqual(out["matching_files"], 0)

    def test_cli_readonly_output_and_incomplete_exit(self):
        self.write("a.md", b"verify")
        before = list(self.root.iterdir())
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = finder.main(["--root", str(self.root), "--scope", ".", "--scope", "absent", "--term", "verify"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stream.getvalue())["matching_files"], 1)
        self.assertEqual(list(self.root.iterdir()), before)

    def test_json_survives_windows_legacy_stdout_encoding(self):
        self.write("기록 🔎.md", "검토\n".encode())
        env = dict(os.environ, PYTHONIOENCODING="cp949", PYTHONUTF8="0")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root),
             "--scope", ".", "--term", "검토"],
            env=env, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(data["matches"][0]["path"], "기록 🔎.md")
        self.assertEqual(data["matches"][0]["hits"][0]["term"], "검토")


if __name__ == "__main__":
    unittest.main()
