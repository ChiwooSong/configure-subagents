"""Filesystem application contracts, fault injection, and conditional recovery."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "configure-subagents/scripts/apply_agents.py"
spec = importlib.util.spec_from_file_location("guarded_apply", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def claude(name="reviewer"):
    return (f'\ufeff---\r\nname: {name}\r\ndescription: Review\r\n# Keep comment\r\ntools: Read, Grep\r\nmodel: inherit\r\nintegrationTag: keep\r\n---\r\nReview only.\r\n').encode()


def codex(name="reviewer"):
    return f'name="{name}"\ndescription="Review"\ndeveloper_instructions="Review only."\nintegrationTag="keep"\n'.encode()


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="guarded-agents-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "한글 project"
        self.root.mkdir()
        self.paths = {n: self.root / scope[0] for n, scope in guard.SCOPES.items()}
        for n, folder in self.paths.items():
            folder.mkdir(parents=True)
            (folder / ("reviewer" + guard.SCOPES[n][1])).write_bytes(claude() if n == "claude" else codex())
            (folder / "keep.txt").write_bytes(b"unrelated\r\n")

    def begin(self, target="both", deletes=()):
        result = guard.prepare(self.root, target, deletes)
        self.task = result["transaction"]
        self.transaction = self.root / guard.STORAGE / self.task
        return self.transaction / "candidate"

    def check(self, target="both"):
        t, m, j = guard.load(self.root, target, self.task)
        return guard.inspect_candidate(self.root, t, m, j)[0]

    def apply(self, target="both"):
        return guard.apply(self.root, target, self.task, self.check(target)["candidate_digest"])

    def project_snapshot(self):
        return {n: guard.comparable(guard.snapshot(self.root, p)) for n, p in self.paths.items()}

    def edit(self, candidate, target):
        p = candidate / target / ("reviewer" + guard.SCOPES[target][1])
        p.write_bytes(p.read_bytes().replace(b"Review only.", b"Review supplied changes only."))

    def test_both_minimal_edit_formats_warnings_and_replay(self):
        before = self.project_snapshot()
        candidate = self.begin()
        self.edit(candidate, "claude")
        self.edit(candidate, "codex")
        check_before = guard.comparable(guard.snapshot(self.root, self.transaction))
        checked = self.check()
        self.assertEqual(check_before, guard.comparable(guard.snapshot(self.root, self.transaction)))
        self.assertEqual(len(checked["changes"]), 2)
        self.assertTrue(any(d["code"] == "unknown_field" for d in checked["diagnostics"]))
        result = self.apply()
        self.assertEqual(result["status"], "applied", result)
        for name in self.paths:
            filename = "reviewer" + guard.SCOPES[name][1]
            self.assertEqual((self.paths[name] / filename).read_bytes(), (candidate / name / filename).read_bytes())
            self.assertEqual(before[name]["keep.txt"], self.project_snapshot()[name]["keep.txt"])
        after = guard.comparable(guard.snapshot(self.root, self.root))
        repeated = guard.apply(self.root, "both", self.task, checked["candidate_digest"])
        self.assertEqual(repeated["status"], "unchanged")
        self.assertEqual(after, guard.comparable(guard.snapshot(self.root, self.root)))

    def test_create_from_absent_namespaces_and_target_isolation(self):
        new_root = self.root / "new"
        new_root.mkdir()
        r = guard.prepare(new_root, "codex")
        task = r["transaction"]
        candidate = Path(r["candidate_paths"]["codex"])
        (candidate / "new.toml").write_bytes(codex("new"))
        t, m, j = guard.load(new_root, "codex", task)
        checked, _ = guard.inspect_candidate(new_root, t, m, j)
        self.assertEqual(guard.apply(new_root, "codex", task, checked["candidate_digest"])["status"], "applied")
        self.assertFalse((new_root / ".claude").exists())
        self.assertEqual((new_root / ".codex/agents/new.toml").read_bytes(), codex("new"))

    def test_noop_missing_scope_does_not_create_agent_directory(self):
        root = self.root / "empty"
        root.mkdir()
        r = guard.prepare(root, "claude")
        t, m, j = guard.load(root, "claude", r["transaction"])
        c, _ = guard.inspect_candidate(root, t, m, j)
        self.assertEqual(guard.apply(root, "claude", r["transaction"], c["candidate_digest"])["status"], "unchanged")
        self.assertFalse((root / ".claude").exists())

    def test_single_target_preserves_other_target(self):
        before = self.project_snapshot()["claude"]
        candidate = self.begin("codex")
        self.edit(candidate, "codex")
        self.apply("codex")
        self.assertEqual(before, self.project_snapshot()["claude"])

    def test_delete_and_rename_require_exact_allowance(self):
        candidate = self.begin(deletes=[("claude", "reviewer.md")])
        old = candidate / "claude/reviewer.md"
        new = candidate / "claude/review-renamed.md"
        new.write_bytes(old.read_bytes().replace(b"name: reviewer", b"name: review-renamed"))
        old.unlink()
        (candidate / "codex/reviewer.toml").unlink()
        before = self.project_snapshot()
        with self.assertRaisesRegex(guard.Rejected, "Deletion not allowed"):
            self.check()
        self.assertEqual(before, self.project_snapshot())
        (candidate / "codex/reviewer.toml").write_bytes(codex())
        self.assertEqual(self.apply()["status"], "applied")
        self.assertFalse((self.paths["claude"] / "reviewer.md").exists())
        self.assertTrue((self.paths["claude"] / "review-renamed.md").is_file())

    def test_non_agent_and_directory_replacement_refused(self):
        candidate = self.begin()
        (candidate / "claude/keep.txt").write_bytes(b"modified")
        with self.assertRaisesRegex(guard.Rejected, "Non-Agent"):
            self.check()
        (candidate / "claude/keep.txt").write_bytes(b"unrelated\r\n")
        (candidate / "claude/reviewer.md").unlink()
        (candidate / "claude/reviewer.md").mkdir()
        with self.assertRaisesRegex(guard.Rejected, "File/directory"):
            self.check()

    def test_both_static_preflight_rejects_before_first_write(self):
        candidate = self.begin()
        self.edit(candidate, "claude")
        (candidate / "codex/reviewer.toml").write_bytes(b'name="bad"\nname="duplicate"\n')
        before = self.project_snapshot()
        with self.assertRaises(guard.Rejected):
            self.apply()
        self.assertEqual(before, self.project_snapshot())

    def test_encoding_newline_and_final_newline_changes_rejected(self):
        candidate = self.begin("claude")
        p = candidate / "claude/reviewer.md"
        data = p.read_bytes()
        for changed in [data[3:], data.replace(b"\r\n", b"\n"), data[:-2], data.replace(b"Review only.\r\n", b"Review only.\n"), b"\xff" + data]:
            with self.subTest(changed=changed[:8]):
                p.write_bytes(changed)
                with self.assertRaises(guard.Rejected):
                    self.check("claude")

    def test_codex_new_bom_and_mixed_format_refused(self):
        candidate = self.begin("codex")
        for data in [b"\xef\xbb\xbf" + codex("new"), codex("new").replace(b'description="Review"\n',b'description="Review"\r\n')]:
            (candidate / "codex/new.toml").write_bytes(data)
            with self.assertRaises(guard.Rejected):
                self.check("codex")

    def test_original_change_and_replacement_are_not_overwritten(self):
        self.begin()
        p = self.paths["claude"] / "reviewer.md"
        data = p.read_bytes()
        replacement = p.with_suffix(".replacement")
        replacement.write_bytes(data)
        os.replace(replacement, p)
        with self.assertRaisesRegex(guard.Rejected, "Original changed"):
            self.check()
        self.assertEqual(p.read_bytes(), data)

    def test_candidate_change_after_check(self):
        candidate = self.begin()
        checked = self.check()
        self.edit(candidate, "codex")
        before = self.project_snapshot()
        with self.assertRaisesRegex(guard.Rejected, "digest"):
            guard.apply(self.root, "both", self.task, checked["candidate_digest"])
        self.assertEqual(before, self.project_snapshot())

    def test_candidate_change_during_validation(self):
        candidate = self.begin("codex")
        original = guard.validator
        def race(name, root, tree):
            result = original(name, root, tree)
            self.edit(candidate, "codex")
            return result
        with patch.object(guard, "validator", race):
            with self.assertRaisesRegex(guard.Rejected, "while validating"):
                self.check("codex")

    def test_candidate_and_installed_race_cannot_change_checked_receipt(self):
        candidate = self.begin("codex")
        self.edit(candidate, "codex")
        original = guard.publish_entry
        def race(root, path, data, mode, record):
            original(root, path, data, mode, record)
            unchecked = data.replace(b"Review supplied changes only.", b"Unchecked replacement.")
            path.write_bytes(unchecked)
            (candidate / "codex/reviewer.toml").write_bytes(unchecked)
        with patch.object(guard, "publish_entry", race):
            result = self.apply("codex")
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertEqual(result["exit_code"], 2)
        self.assertIn(b"Unchecked replacement.", (self.paths["codex"] / "reviewer.toml").read_bytes())
        self.assertEqual((self.transaction / "originals/codex/reviewer.toml").read_bytes(), codex())

    def test_completed_candidate_change_is_not_silently_ignored(self):
        candidate = self.begin()
        self.apply()
        self.edit(candidate, "codex")
        with self.assertRaisesRegex(guard.Rejected, "Candidate changed after"):
            self.check()

    def test_second_target_failure_restores_original_bytes_and_times(self):
        candidate = self.begin()
        self.edit(candidate, "claude")
        self.edit(candidate, "codex")
        before = self.project_snapshot()
        original = guard.publish_entry
        def fail(root, path, data, mode, record):
            if ".codex" in path.parts:
                raise OSError("Injected second-target failure")
            return original(root, path, data, mode, record)
        with patch.object(guard, "publish_entry", fail):
            result = self.apply()
        self.assertEqual(result["status"], "failed", result)
        self.assertEqual(result["exit_code"], 2)
        for name in before:
            for relative, info in before[name].items():
                if not info["directory"]:
                    self.assertEqual(info, self.project_snapshot()[name][relative])
        with self.assertRaisesRegex(guard.Rejected, "cannot be reused"):
            self.check()

    def test_concurrent_first_output_is_retained_during_recovery(self):
        candidate = self.begin()
        self.edit(candidate, "claude")
        self.edit(candidate, "codex")
        original = guard.publish_entry
        def fail(root, path, data, mode, record):
            if ".codex" in path.parts:
                (self.paths["claude"] / "reviewer.md").write_bytes(b"Another writer's change")
                raise OSError("Failure after concurrent edit")
            return original(root, path, data, mode, record)
        with patch.object(guard, "publish_entry", fail):
            result = self.apply()
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertTrue(result["unrecovered"])
        self.assertEqual((self.paths["claude"] / "reviewer.md").read_bytes(), b"Another writer's change")
        self.assertEqual((self.transaction / "originals/claude/reviewer.md").read_bytes(), claude())

    def test_destination_appearing_after_withdrawal_is_preserved(self):
        candidate = self.begin("codex")
        self.edit(candidate, "codex")
        def race(root, path, data, mode, record):
            path.write_bytes(b"Concurrent destination")
            raise FileExistsError("Destination appeared")
        with patch.object(guard, "publish_entry", race):
            result = self.apply("codex")
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertEqual((self.paths["codex"] / "reviewer.toml").read_bytes(), b"Concurrent destination")

    def test_partial_write_is_retained_and_reported(self):
        candidate = self.begin("codex")
        self.edit(candidate, "codex")
        def partial(root, path, data, mode, record):
            with path.open("xb") as f:
                record["output_identity"] = guard.identity(os.fstat(f.fileno()))
                f.write(b"partial")
            raise OSError("Partial write")
        with patch.object(guard, "publish_entry", partial):
            result = self.apply("codex")
        self.assertEqual(result["status"], "recovery_required", result)
        self.assertEqual((self.paths["codex"] / "reviewer.toml").read_bytes(), b"partial")

    def test_tampered_and_interrupted_records_refuse_reuse(self):
        self.begin()
        p = self.transaction / "manifest.json"
        data = p.read_bytes()
        p.write_bytes(data.replace(b'"schema_version":1', b'"schema_version":9'))
        with self.assertRaisesRegex(guard.Rejected, "Damaged"):
            self.check()
        p.write_bytes(data)
        guard.write_record(self.root, self.transaction / "journal.json", {"state":"applying"})
        with self.assertRaisesRegex(guard.Rejected, "cannot be reused"):
            self.check()

    def test_wrong_target_or_unsafe_delete_does_not_prepare(self):
        for deletes in [[("codex", "../reviewer.toml")], [("claude", "reviewer.md")], [("codex", "keep.txt")]]:
            with self.subTest(deletes=deletes):
                with self.assertRaises(guard.Rejected):
                    guard.prepare(self.root, "codex", deletes)
        self.assertFalse((self.root / guard.STORAGE).exists())
        self.begin("claude")
        with self.assertRaises(guard.Rejected):
            self.check("codex")

    def test_dependency_unavailable_does_not_apply(self):
        self.begin()
        before = self.project_snapshot()
        with patch.object(guard, "validator", return_value={"exit_code":2,"diagnostics":[{"code":"missing_dependency"}]}):
            with self.assertRaises(guard.Unavailable):
                self.check()
        self.assertEqual(before, self.project_snapshot())

    def test_links_and_junctions_are_not_followed(self):
        candidate = self.begin()
        outside = self.root / "outside"
        outside.mkdir()
        link = candidate / "codex/external"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                self.skipTest("Cannot create link")
            r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],capture_output=True)
            if r.returncode:
                self.skipTest("Cannot create junction")
        try:
            with self.assertRaises(guard.Rejected):
                self.check()
            self.assertEqual(list(outside.iterdir()), [])
        finally:
            if link.is_symlink():
                link.unlink()
            else:
                os.rmdir(link)

    def test_cli_json_contract_and_readonly_check(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "prepare", "--project-root", str(self.root), "--target", "both"],capture_output=True,text=True)
        r = json.loads(result.stdout)
        self.assertEqual(result.returncode,0,r)
        self.assertEqual(r["schema_version"],1)
        p = subprocess.run([sys.executable,str(SCRIPT),"check","--project-root",str(self.root),"--target","both","--transaction",r["transaction"]],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout)
        self.assertTrue(json.loads(p.stdout)["candidate_digest"])
        (Path(r["candidate_paths"]["codex"])/"bad.toml").write_text('name="a"\nname="b"\n')
        invalid = subprocess.run([sys.executable,str(SCRIPT),"check","--project-root",str(self.root),"--target","both","--transaction",r["transaction"]],capture_output=True,text=True)
        self.assertEqual(invalid.returncode,1)
        self.assertTrue(any(d.get('field')=='file' and d.get('code')=='toml' for d in json.loads(invalid.stdout)['diagnostics']))
        p = subprocess.run([sys.executable,str(SCRIPT),"apply","--project-root",str(self.root),"--target","both"],capture_output=True,text=True)
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(p.stdout)["status"],"rejected")

    @unittest.skipUnless(os.name=='nt','Windows short-path normalization')
    def test_windows_short_spelling_is_not_a_link(self):
        import ctypes
        api=ctypes.windll.kernel32.GetShortPathNameW
        buffer=ctypes.create_unicode_buffer(32768)
        size=api(str(self.root),buffer,len(buffer))
        if not size or not buffer.value or buffer.value.lower()==str(self.root).lower():
            self.skipTest('8.3 name not available for fixture')
        root=guard.project_root(buffer.value)
        self.assertEqual(root,self.root)
        prepared=guard.prepare(root,'both')
        self.assertEqual(prepared['status'],'prepared')


if __name__ == "__main__":
    unittest.main()
