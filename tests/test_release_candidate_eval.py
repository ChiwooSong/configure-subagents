"""RC QA mechanics only. No paid/authenticated sessions run in these tests."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
spec = importlib.util.spec_from_file_location("rc_eval", ROOT / "evals/evaluate_release_candidate.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class ReleaseEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.base = ROOT / ".eval-runs"
        self.base.mkdir(exist_ok=True)
        self.output = Path(tempfile.mkdtemp(prefix="rc-test-", dir=self.base)).resolve()

    def tearDown(self):
        self.assertTrue(self.output.is_relative_to(self.base.resolve()))
        self.assertTrue(self.output.name.startswith("rc-test-"))
        self.assertFalse(self.output.is_symlink())
        shutil.rmtree(self.output)

    def test_session_count_and_target_matrix(self):
        self.assertEqual(len(evaluation.JOBS),11)
        for host, other in [("claude","codex"),("codex","claude")]:
            self.assertEqual(evaluation.target_for(host,"propose-default"),host)
            self.assertEqual(evaluation.target_for(host,"propose-cross"),other)
            self.assertEqual(evaluation.target_for(host,"synthetic-both-apply"),"both")

    def test_fixtures_keep_separate_model_pools_and_unknown_prices(self):
        cases=evaluation.fixture_catalogs()
        self.assertEqual(len(cases),8)
        for entry in cases.values():
            claude={c['model'] for c in entry['claude']['candidates']}
            codex={c['model'] for c in entry['codex']['candidates']}
            self.assertFalse(claude & codex)
        self.assertTrue(all('input' not in c['fixture_evidence'] for c in cases['price-unknown']['codex']['candidates']))

    def test_prepared_payload_and_repeat_request_are_identical(self):
        folder,state=evaluation.prepare_session(self.output,'codex','synthetic-both-apply',ROOT/'configure-subagents')
        before=evaluation.base.hashes(Path(state['root']),True,exclude_git=True)
        _,repeat=evaluation.prepare_session(self.output,'codex','synthetic-both-repeat',ROOT/'configure-subagents')
        self.assertEqual(before,evaluation.base.hashes(Path(state['root']),True,exclude_git=True))
        self.assertEqual(evaluation.prompt(state,'synthetic-both-apply'),evaluation.prompt(repeat,'synthetic-both-repeat'))
        for target in ['claude','codex']:
            self.assertTrue((Path(state['root'])/'projects/growth'/f'.{target if target=="codex" else "claude"}/agents').is_dir())
        self.assertEqual(evaluation.base.hashes(ROOT/'configure-subagents'),state['skill_hashes'])

    def test_skill_drift_or_repeat_without_apply_refused(self):
        with self.assertRaisesRegex(ValueError,'apply before'):
            evaluation.prepare_session(self.output,'claude','synthetic-both-repeat',ROOT/'configure-subagents')
        folder,state=evaluation.prepare_session(self.output,'claude','propose-default',ROOT/'configure-subagents')
        with patch.object(evaluation.base,'hashes',return_value={}):
            with self.assertRaisesRegex(ValueError,'mismatch'):
                evaluation.prepare_session(self.output,'claude','propose-default',ROOT/'configure-subagents')

    def test_capture_preserves_sources_excludes_dependencies_and_credentials(self):
        sources=[]
        for name in ['signal_flare','mosigi']:
            source=self.output/name
            (source/'lib/data').mkdir(parents=True)
            (source/'node_modules').mkdir()
            (source/'data').mkdir()
            (source/'.Secrets').mkdir()
            (source/'.codex/agents').mkdir(parents=True)
            (source/'lib/data/model.dart').write_text('class Model {}\n')
            (source/'README.md').write_text('Project\n')
            for file in ['.env','auth.json','service-account.json']:
                (source/file).write_text('fixture secret')
            (source/'node_modules/ignored.js').write_text('dependency')
            (source/'data/runtime.json').write_text('runtime')
            (source/'.Secrets/export.json').write_text('fixture secret')
            (source/'.codex/config.toml').write_text('token="fixture secret"\n')
            (source/'.codex/agents/config.toml').write_text('name="config"\ndescription="Role"\ndeveloper_instructions="Keep"\n')
            (source/'notes.txt').write_text('-----BEGIN OPENSSH PRIVATE KEY-----\nfixture\n-----END OPENSSH PRIVATE KEY-----\n')
            sources.append((name,str(source)))
        before={n:evaluation.base.hashes(Path(p),True) for n,p in sources}
        evaluation.capture(self.output,sources)
        for n,p in sources:
            self.assertEqual(before[n],evaluation.base.hashes(Path(p),True))
            files=evaluation.base.hashes(self.output/'sources'/n)
            self.assertEqual(set(files),{'README.md','lib/data/model.dart','.codex/agents/config.toml'})
        observed=evaluation.source_observation(self.output)
        self.assertTrue(all(not x['selected_files_changed'] for x in observed.values()))
        with self.assertRaisesRegex(ValueError,'overwrite'):
            evaluation.capture(self.output,sources)

    def test_frozen_real_snapshots_cannot_be_changed(self):
        sources=[]
        for name in ['signal_flare','mosigi']:
            source=self.output/name
            source.mkdir()
            (source/'README.md').write_text('Project\n')
            sources.append((name,str(source)))
        evaluation.capture(self.output,sources)
        (self.output/'sources/mosigi/README.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'snapshot changed'):
            evaluation.prepare_session(self.output,'codex','real-default-apply',ROOT/'configure-subagents')

    def test_capture_includes_module_sources_without_weakening_secret_filters(self):
        sources = []
        for name in ['signal_flare', 'mosigi']:
            source = self.output / name
            (source / 'scripts').mkdir(parents=True)
            (source / 'node_modules').mkdir()
            (source / 'runtime').mkdir()
            for filename in ['test-emu.mjs', 'runner.cjs', 'checks.mts', 'schema.cts']:
                (source / 'scripts' / filename).write_text('export const fixture = true;\n')
            (source / 'scripts/service-account.mjs').write_text('fixture credential\n')
            (source / 'scripts/key-material.mjs').write_text('-----BEGIN OPENSSH PRIVATE KEY-----\nfixture\n-----END OPENSSH PRIVATE KEY-----\n')
            (source / 'node_modules/dependency.mjs').write_text('fixture dependency\n')
            (source / 'runtime/session.mjs').write_text('fixture runtime\n')
            sources.append((name, str(source)))
        before = {n: evaluation.base.hashes(Path(p), True) for n, p in sources}
        evaluation.capture(self.output, sources)
        for name, source in sources:
            self.assertEqual(before[name], evaluation.base.hashes(Path(source), True))
            self.assertEqual(set(evaluation.base.hashes(self.output / 'sources' / name)), {
                'scripts/test-emu.mjs', 'scripts/runner.cjs', 'scripts/checks.mts', 'scripts/schema.cts'
            })
            record = json.loads((self.output / 'sources.json').read_text())[name]
            self.assertNotIn('scripts/test-emu.mjs', record['excluded'])
            self.assertIn('scripts/key-material.mjs', record['excluded'])

    def test_capture_cannot_substitute_unscanned_source_bytes(self):
        sources=[]
        for name in ['signal_flare','mosigi']:
            source=self.output/name
            source.mkdir()
            (source/'notes.txt').write_text('Safe fixture text\n')
            sources.append((name,str(source)))
        original=evaluation.file_fact
        changed=False
        def race(path):
            nonlocal changed
            if not changed and path.name=='notes.txt':
                changed=True
                path.write_text('-----BEGIN OPENSSH PRIVATE KEY-----\ndummy\n-----END OPENSSH PRIVATE KEY-----\n')
            return original(path)
        with patch.object(evaluation,'file_fact',race):
            with self.assertRaisesRegex(ValueError,'after content screening'):
                evaluation.capture(self.output,sources)
        self.assertFalse((self.output/'sources/signal_flare/notes.txt').exists())

    def test_final_text_ignores_string_content_and_synthetic_error_models(self):
        events=[{'type':'assistant','message':{'model':'<synthetic>','content':'error'}},
                {'type':'assistant','message':{'model':'observed-test','content':[{'type':'text','text':'Report'},{'type':'tool_use'}]}}]
        text,models=evaluation.final_text('claude',events)
        self.assertEqual(text,'Report')
        self.assertEqual(models,['observed-test'])

    def test_headless_claude_apply_refused_before_launch(self):
        with patch.object(evaluation.subprocess,'run') as process:
            with self.assertRaisesRegex(ValueError,'requires --interactive'):
                evaluation.session(self.output,'claude','synthetic-both-apply',ROOT/'configure-subagents',run=True,model='test-model')
            process.assert_not_called()

    def test_private_report_shape_is_not_a_semantic_or_static_pass(self):
        report={'cases':[{'project':'growth','target':'codex','status':'proposed','agents':[], 'diagnostics':[], 'unknowns':['No runtime claim']}]}
        self.assertTrue(evaluation.structured_report_ok(report))
        self.assertFalse(evaluation.structured_report_ok({'cases':[]}))
        report['cases'][0]['agents']=[{'name':'missing fields'}]
        self.assertFalse(evaluation.structured_report_ok(report))
        folder,state=evaluation.prepare_session(self.output,'codex','validate-both',ROOT/'configure-subagents')
        results=evaluation.independent_static_checks(ROOT/'configure-subagents',Path(state['root']),['claude','codex'])
        self.assertEqual(results['growth:claude']['exit_code'],1)
        self.assertEqual(results['growth:codex']['exit_code'],1)
        self.assertEqual(results['korean:claude']['exit_code'],0)

    def test_repeat_refuses_drift_before_host_launch(self):
        folder,state=evaluation.prepare_session(self.output,'codex','synthetic-both-apply',ROOT/'configure-subagents')
        instruction=evaluation.prompt(state,'synthetic-both-apply')
        digest=evaluation.hashlib.sha256(instruction.encode()).hexdigest()
        evidence={'status':'finished','after':evaluation.base.hashes(Path(state['root']),True,exclude_git=True),'input_sha256':digest,'requested_host_model':'test-model'}
        evaluation.write_json(folder/'synthetic-both-apply-evidence.json',evidence)
        evaluation.write_json(folder/'synthetic-both-apply-input.json',{'prompt':instruction,'sha256':digest})
        project=Path(state['root'])/'projects/growth/WORK.json'
        original=project.read_bytes()
        project.write_bytes(original+b'\n')
        with patch.object(evaluation,'source_observation'),patch.object(evaluation.base,'command') as command:
            with self.assertRaisesRegex(ValueError,'snapshot differs'):
                evaluation.session(self.output,'codex','synthetic-both-repeat',ROOT/'configure-subagents',run=True,model='test-model')
            command.assert_not_called()
        project.write_bytes(original)
        with self.assertRaisesRegex(ValueError,'model differs'):
            evaluation.session(self.output,'codex','synthetic-both-repeat',ROOT/'configure-subagents',run=True,model='different-model')


if __name__=='__main__':
    unittest.main()
