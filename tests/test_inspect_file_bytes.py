import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "configure-subagents/scripts/inspect_file_bytes.py"
spec = importlib.util.spec_from_file_location("byte_inspector", SCRIPT)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


class ByteInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "한글 agent.md"

    def test_newline_variants_without_normalization(self):
        for data, style, counts, final in [
            (b"a\n", "LF", (0, 1, 0), True),
            (b"a\r\nb\r\n", "CRLF", (2, 0, 0), True),
            (b"a\r\nb\nc\r", "mixed", (1, 1, 1), True),
            (b"a\r", "CR", (0, 0, 1), True),
            (b"a", "none", (0, 0, 0), False),
            (b"", "none", (0, 0, 0), False),
        ]:
            with self.subTest(style=style, data=data):
                self.path.write_bytes(data)
                before = self.path.stat().st_mtime_ns
                result = inspector.inspect(self.root, self.path.name)
                self.assertEqual(result["newline_style"], style)
                self.assertEqual(tuple(result[k] for k in ("crlf_bytes", "lone_lf_bytes", "lone_cr_bytes")), counts)
                self.assertEqual(result["final_newline"], final)
                self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(result["mtime_ns"], before)
                self.assertEqual(self.path.read_bytes(), data)
                self.assertEqual(self.path.stat().st_mtime_ns, before)

    def test_utf8_bom(self):
        self.path.write_bytes(b"\xef\xbb\xbf" + "한글\n".encode())
        result = inspector.inspect(self.root, self.path.name)
        self.assertEqual(result["encoding"], "utf-8-bom")
        self.assertTrue(result["utf8_bom"])
        self.assertEqual(result["newline_style"], "LF")

    def test_unknown_encoding_is_not_claimed_as_utf8(self):
        for data in (b"\xff\n", "a\n".encode("utf-16-le")):
            self.path.write_bytes(data)
            result = inspector.inspect(self.root, self.path.name)
            self.assertEqual(result["encoding"], "unverified")
            self.assertEqual(result["newline_style"], "unverified")
            self.assertIsNone(result["final_newline"])

    def test_stdout_only_and_partial_failure(self):
        self.path.write_bytes(b"a\n")
        before = sorted(self.root.iterdir())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = inspector.main(["--root", str(self.root), self.path.name, "missing.md"])
        result = json.loads(stdout.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(sorted(self.root.iterdir()), before)

    def test_outside_root_and_directory_rejected(self):
        with self.assertRaises(ValueError):
            inspector.inspect(self.root, str(SCRIPT))
        with self.assertRaises(ValueError):
            inspector.inspect(self.root, ".")

    def test_outside_symlink_rejected(self):
        try:
            self.path.symlink_to(SCRIPT)
        except OSError:
            self.skipTest("Symlinks unavailable for this account")
        with self.assertRaises(ValueError):
            inspector.inspect(self.root, self.path.name)

    def test_change_during_read_is_reported(self):
        self.path.write_bytes(b"a\n")
        def changing_read(path):
            path.write_bytes(b"longer\n")
            return b"a\n"
        with patch.object(Path, "read_bytes", changing_read):
            with self.assertRaisesRegex(ValueError, "changed during inspection"):
                inspector.inspect(self.root, self.path.name)

    def test_denied_read_returns_unavailable(self):
        self.path.write_bytes(b"a\n")
        with patch.object(Path, "read_bytes", side_effect=PermissionError("denied")):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(inspector.main(["--root", str(self.root), self.path.name]), 2)
        self.assertIn("denied", json.loads(out.getvalue())["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
