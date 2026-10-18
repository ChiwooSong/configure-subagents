# 1.0.0 release checklist

Updated: 2026-10-18 (Asia/Seoul). **Decision: HOLD.** Alpha.5 can ship through `next` with explicit limitations. It is not a stable-release candidate or evidence that all behavior gates pass.

Check a gate only when its stated evidence exists for the release candidate. Preserve failed attempts; a later successful run must not erase an earlier failure. README warnings alone do not close correctness or preservation blockers.

## Established baseline

- [x] Project-local Claude Agent target and dual Skill hosts are documented; global configuration and automatic orchestration are excluded.
- [x] CLI conflicts/no-overwrite behavior and validator JSON/exit-code behavior have regression coverage.
- [x] Alpha.5 local tests pass: Python 56, Node 27, Skill structure and the 15-file offline artifact install/repeat test.
- [x] R8 isolated real-project runs preserve the selected original files and produce byte/mtime-preserving fresh repeats in both hosts.
- [x] Claude's remaining first-pass/cross-review failures are disclosed with the tested host/model/environment.

These are prior evidence, not final-RC completion. [R8](../evals/RETRIEVAL_AUDIT_BEHAVIOR.md) tests different role scopes in the two hosts; Codex's reviewer success does not establish execution-worker permission coverage.

## 1. Freeze the supported scope and acceptance matrix

- [ ] Record the RC commit, complete installed Skill hashes, host versions, per-session models and OS. Explicitly distinguish installer/validator platform support from authenticated host-behavior support. Do not advertise every language, model or OS as tested.
- [ ] Define supported behavior for propose, apply, validation-only and repeat. Keep generated-Agent runtime invocation separate unless explicitly included in the release claims.
- [ ] Use the matrix below in both hosts with realistic raw inputs, fresh sessions, isolated copies and independent snapshots. Do not put expected outcomes or known defects in host prompts.

| Case | Required outcome |
|---|---|
| Sparse script/design project | Minimal justified proposal, including no added Agent; clear assumptions and revisit conditions; no writes in proposal mode |
| Service/code project and document project | Roles follow actual work and boundaries rather than a fixed roster |
| Existing customized Agent, then project growth | Minimal necessary edit; user prose, fields, comments, explicit constraints and unrelated files preserved |
| Same-state fresh repeat | Adequate configuration unchanged in bytes and mtime; a real defect correction is reported as a correction, not a no-op |
| Validation-only | Diagnostics without configuration edits, hook execution or MCP startup |
| Unknown and verified target-model information | Preserve existing choice or use `inherit` when eligibility is unknown; autonomous task-fit choices within verified constraints; no Codex model IDs in Claude settings |
| English/Korean response and Agent conventions | Requested response language does not translate an existing Agent; explicit Agent translation is handled separately |
| LF/CRLF/BOM and concurrent changes | Measured formatting preservation and no overwrite of concurrent work |

## 2. Close first-pass exception and cross-review failures — blocking

- [ ] On the two authorized real-project snapshots, cover representative execution-capable workers and reviewers in both hosts. Record any deliberately narrower role and do not count it as testing an omitted responsibility.
- [ ] Resolve the known reproduction/design-only versus universal fix-to-green conflict. Preserve conditional isolated verification, shared-file exceptions and approved wrapper subprocess paths without inventing broader authority.
- [ ] Before first installation, demonstrate independent source-area retrieval, base/revision/handoff interpretation, the actual candidate reread and a concrete source comparison. A YAML pass or final checklist assertion is insufficient.
- [ ] Run **three independent fresh APPLY → fresh REPEAT pairs per host** for the high-risk exception scenario, with the same frozen inputs/model settings. Require zero unresolved material scope contradictions or skipped cross-review gates, and zero unjustified repeat edits. Record every attempt, including failures. Three passes are a bounded acceptance sample, not a universal reliability guarantee.
- [ ] If this remains unreliable, keep 1.0.0 on hold. A proposed reduction of the supported feature scope requires a new product decision and matching tests; do not silently redefine the feature just to turn the gate green.

## 3. Verify preservation, failure handling and reporting

- [ ] On the final RC, repeat the customized-Agent growth test with both hosts, preserving language, comments, extra fields, explicit model settings, encoding/BOM, line endings and final newline.
- [ ] Exercise an original changing after analysis and a failure during application in isolated fixtures. Confirm fresh reads, recalculated edits and conditional recovery that preserves another writer's changes. Installer rollback tests alone do not prove host editing behavior.
- [ ] Exercise missing Python/PyYAML, denied access, malformed YAML and unavailable model information. Reports must distinguish attempted, blocked, failed, retried and completed checks without permission bypasses or global dependency installation.
- [ ] Confirm tool-capability descriptions and byte-format claims match measured evidence. Keep task-authored candidates/backups/helpers within the permitted root and outside discovery paths.

## 4. Freeze the public compatibility and update contract

- [ ] Document stable CLI arguments, required host selection, install destinations, conflict behavior, exit codes and validator JSON schema/version. Decide how future incompatible changes are versioned.
- [ ] Demonstrate updating an unmodified alpha installation and a customized Skill through the documented compare/backup/merge process. No force upgrade is required; custom instructions and project Agents must survive.
- [ ] Recheck the published package's scope/owner, MIT license, repository links and migration guidance. Audit Git/tarball contents for private paths, raw evaluation logs, credentials and unrelated files.

## 5. Validate the exact RC artifact

- [ ] Pass all six static CI combinations on the exact RC commit: Ubuntu, Windows and macOS Intel with Python 3.10/3.13 and Node 22. These jobs do not prove host behavior on all three OSes.
- [ ] Publish an RC only to `next`, verify tarball integrity and metadata, install that registry artifact in fresh temporary projects for both hosts, and confirm exact payload/no-change reinstall/conflict refusal.
- [ ] Confirm Skill discovery and the supported behavior matrix from the **installed RC payload**, not merely the source checkout. Rerun affected checks after changes and explain any output-only fixes tested separately.
- [ ] Review an RC issue ledger with no unresolved correctness, preservation or security blockers in the supported scope. Close each item with evidence and a reviewer decision, not elapsed time or a higher version number.

## 6. Declare 1.0.0 only after the gates pass

- [ ] Produce a completion record linking the RC commit, CI run, evaluated Skill hashes, host matrix, retained failures and registry smoke evidence. Keep remaining non-blocking limits explicit.
- [ ] Obtain the maintainer's explicit decision to end the current 1.0.0 hold.
- [ ] Publish `1.0.0` to `latest`, create a non-prerelease GitHub release, update version/update instructions, and verify the public artifact again. Retain `next` as an intentional preview channel.

## Claims requiring additional evidence

Generated-Agent discovery/invocation and observed model/tool enforcement are not established by installation or Skill execution. If stable-release claims include them, request a separately scoped temporary-project runtime evaluation and record actual discovery, invocation, response and observable model evidence. Do not silently invoke Agents as part of ordinary setup or infer runtime success from frontmatter.

Current blockers and historical results are linked from the [evaluation index](../evals/EVALUATION.md) and [release-readiness assessment](../evals/RELEASE_READINESS_2026-10-18.md). Alpha.5 publication and CI success do not automatically check any final-RC gate above.
