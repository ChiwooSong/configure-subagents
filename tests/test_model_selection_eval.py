"""Evaluation-mechanics tests, not model-selection quality tests or model calls."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("model_eval", ROOT / "evals/evaluate_model_selection.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class ModelEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.base = ROOT / ".eval-runs"
        self.base.mkdir(exist_ok=True)
        self.output = Path(tempfile.mkdtemp(prefix="model-test-", dir=self.base))

    def tearDown(self):
        target = self.output.resolve()
        self.assertTrue(target.is_relative_to(self.base.resolve()))
        self.assertTrue(target.name.startswith("model-test-"))
        self.assertFalse(self.output.is_symlink())
        shutil.rmtree(target)

    def test_case_coverage_and_frozen_cost_counterexample(self):
        cases = evaluation.cases()
        self.assertEqual(len(cases), 8)
        old, new = cases["older-price"]["candidates"]
        self.assertEqual(old["fixture_evidence"]["qualified"], new["fixture_evidence"]["qualified"])
        self.assertGreater(old["fixture_evidence"]["input"], new["fixture_evidence"]["input"])
        self.assertTrue(all("input" not in c["fixture_evidence"] for c in cases["price-unknown"]["candidates"]))
        self.assertEqual([c["model"] for c in cases["single"]["candidates"] if c["eligibility"] == "eligible"], ["fable"])

    def test_prepare_isolated_payload_and_originals(self):
        state = evaluation.prepare("codex", self.output)
        root = Path(state["root"])
        self.assertEqual(evaluation.hashes(root / ".agents/skills/configure-subagents"), evaluation.hashes(evaluation.SKILL))
        self.assertEqual(len(list((root / "projects").iterdir())), 9)
        data = (root / "projects/existing/.claude/agents/ticket-extractor.md").read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
        self.assertEqual(json.loads((self.output / "state.json").read_text())["host"], "codex")

    def test_fresh_repeat_uses_identical_apply_request(self):
        state = evaluation.prepare("claude", self.output)
        self.assertEqual(evaluation.prompt(state, "apply"), evaluation.prompt(state, "repeat"))
        self.assertEqual(evaluation.prompt(state, "propose-1"), evaluation.prompt(state, "propose-2"))
        self.assertNotIn("expected", evaluation.prompt(state, "propose-1").lower())

    def test_frontmatter_consistency_and_eligibility(self):
        rows = []
        for key, case in evaluation.cases().items():
            groups = {group: sorted(c["model"] for c in case["candidates"] if c["eligibility"] == group) for group in ("eligible", "unverified", "excluded")}
            model = next(iter(groups["eligible"]), "inherit")
            rows.append({"case": key, "candidate_groups": groups, "agents": [{"name": "sample", "model": model,
                         "frontmatter": f"---\nname: sample\ndescription: test\nmodel: {model}\n---",
                         "requirement": "sample", "alternative": None, "reason": "test data", "unknowns": []}]})
        report = {"cases": rows}
        self.assertTrue(all(evaluation.mechanical_report_checks(report, "propose-1").values()))
        rows[0]["agents"][0]["model"] = "unavailable-choice"
        checks = evaluation.mechanical_report_checks(report, "propose-1")
        self.assertFalse(checks["routine:eligible_assignments"])
        self.assertFalse(checks["routine:frontmatter_consistency"])

    def test_duplicate_cases_do_not_pass_coverage(self):
        row = {"case": "unknown", "candidate_groups": {"eligible": [], "unverified": [], "excluded": []}, "agents": []}
        checks = evaluation.mechanical_report_checks({"cases": [row, row]}, "propose-1")
        self.assertFalse(checks["case_coverage"])

    def test_malformed_report_is_diagnostic_not_exception(self):
        for value in (None, [], {}, {"cases": ["bad"]}, {"cases": [{"case": "unknown", "candidate_groups": []}]}):
            self.assertFalse(evaluation.mechanical_report_checks(value, "propose-1")["structured_report"])

    def test_json_extraction_ignores_earlier_objects(self):
        value = evaluation.final_json('Text {"unrelated": true}\n```json\n{"cases": []}\n```')
        self.assertEqual(value, {"cases": []})

    def test_snapshot_checks_mtime_and_content(self):
        path = self.output / "sample.txt"
        path.write_text("original")
        before = evaluation.hashes(self.output, True)
        path.write_text("changed")
        self.assertNotEqual(before, evaluation.hashes(self.output, True))

    def test_workspace_snapshot_includes_backups_but_can_exclude_git(self):
        (self.output / ".git").mkdir()
        (self.output / ".git/config").write_text("automatic")
        (self.output / "backups").mkdir()
        (self.output / "backups/copy.md").write_text("task artifact")
        snapshot = evaluation.hashes(self.output, True, exclude_git=True)
        self.assertNotIn(".git/config", snapshot)
        self.assertIn("backups/copy.md", snapshot)

    def test_refuses_reusing_evidence_before_host_launch(self):
        state = evaluation.prepare("codex", self.output)
        (self.output / "propose-1-evidence.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            evaluation.run(state, self.output, "propose-1")

    def test_skill_drift_blocks_launch(self):
        state = evaluation.prepare("claude", self.output)
        (Path(state["root"]) / ".claude/skills/configure-subagents/SKILL.md").write_text("changed")
        with self.assertRaisesRegex(ValueError, "Skill changed"):
            evaluation.run(state, self.output, "propose-1")

    def test_child_environment_omits_bridge_without_mutating_parent(self):
        with patch.dict(evaluation.os.environ, {"CODEX_APP_TOOLS_PIPE_PATH": "fixture", "CODEX_THREAD_ID": "parent", "ANTHROPIC_API_KEY": "fixture-key"}, clear=True):
            env, removed = evaluation.child_environment("codex")
            self.assertNotIn("CODEX_APP_TOOLS_PIPE_PATH", env)
            self.assertIn("CODEX_THREAD_ID", removed)
            self.assertEqual(evaluation.os.environ["CODEX_THREAD_ID"], "parent")
            env, removed = evaluation.child_environment("claude", account_login=True)
            self.assertNotIn("ANTHROPIC_API_KEY", env)
            self.assertEqual(evaluation.os.environ["ANTHROPIC_API_KEY"], "fixture-key")

    def test_account_login_does_not_override_third_party_provider(self):
        with patch.dict(evaluation.os.environ, {"CLAUDE_CODE_USE_BEDROCK": "1"}, clear=True):
            with self.assertRaisesRegex(ValueError, "third-party"):
                evaluation.child_environment("claude", account_login=True)


if __name__ == "__main__":
    unittest.main()
