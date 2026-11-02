# 1.0.0-rc.1 behavior campaign

Status: **not started** as of 2026-11-02 (Asia/Seoul). Implementation and automated testing precede RC publication. No current-RC authenticated host pass or generated-Agent invocation is claimed.

Prepublication local baseline: **64 Node tests, 114 Python tests**, Skill structure and skill-creator checks, and the **21-file tarball** install/update/guarded-application/replay smoke pass. This is not cross-platform CI or authenticated host evidence. Independent bounded review reproduced and closed a checked-digest substitution issue and source-screening/repeat-input harness issues; retained reproductions remain in ignored QA storage. Existing failures were not relabeled as passes.

## Method

Use the exact registry-installed RC Skill, isolated fixtures and frozen sanitized copies of the two authorized development projects. Keep raw inputs/transcripts/local paths in ignored evaluation storage. Each repeat is a new process with the same request and starts from its apply result. Each independent pair gets a fresh source copy; do not provide expected answers or prior failures.

Record requested/observed execution model separately from configured target models. Classify mechanical preservation/application, private JSON reporting and semantic findings independently. No flawless semantic pass-rate gate applies, but file-tool defects block release. A denied/unavailable operation is not a pass or a successful no-op.

## Planned sessions

| Per-host job | Target | Claude | Codex |
|---|---|---|---|
| propose-default | executing host | Pending | Pending |
| propose-cross | other host | Pending | Pending |
| synthetic-default apply/repeat | executing host | Pending / Pending | Pending / Pending |
| synthetic-both apply/repeat | both | Pending / Pending | Pending / Pending |
| real-default apply/repeat | executing host | Pending / Pending | Pending / Pending |
| real-both apply/repeat | both | Pending / Pending | Pending / Pending |
| validate-both | both | Pending | Pending |

Total: 11 sessions per host, 22 sessions. The four host-to-target combinations are assessed separately. Keep retained attempts and any affected-RC reruns distinct; do not overwrite prior evidence.

## Reproduction

Use an approved Python with Skill parser dependencies. `capture` copies selected project files into ignored storage without running code or modifying the source. Filename/directory and private-key-header screening is deliberately conservative, not a universal secret detector; inspect the capture manifest and exclusions before exposing a snapshot to a host.

```text
python evals/evaluate_release_candidate.py capture --output .eval-runs/rc1-example --project-source signal_flare "<authorized-source>" --project-source mosigi "<authorized-source>"
python evals/evaluate_release_candidate.py session --output .eval-runs/rc1-example --host codex --job propose-default --skill-source "<registry-installed-package>/configure-subagents"
```

The second command prepares and prints a request without a model call. Add `--run` for one authenticated session; select a job from the table's expanded apply/repeat names. Use `--interactive` from a visible terminal for Claude apply/repeat and type `/exit` after the final report. A new invocation is a fresh process. Windows Codex uses the already configured `--windows-sandbox elevated|unelevated`; no sandbox weakening is used. Record artifact origin/integrity alongside the campaign, and use a new campaign after Skill changes. Never overwrite an attempt.

## Limits and decision

Prior [alpha.8 evidence](MODEL_SELECTION_BEHAVIOR.md) and [R8 failures](RETRIEVAL_AUDIT_BEHAVIOR.md) remain separate historical observations. Final publication requires the [release checklist](../docs/V1_RELEASE_CHECKLIST.md) and a separate maintainer decision. Actual generated-Agent discovery/invocation, measured performance/savings and untested OS/model/provider combinations remain outside this campaign.
