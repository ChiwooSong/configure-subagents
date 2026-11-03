# 1.0.0 release checklist

Updated: 2026-11-03 (Asia/Seoul). **Maintainer approved stable 1.0.0, accepted the documented unverified scopes/model limitations and chose to skip rc.2.** Original 22 outcomes remain 21 native final receipts plus one reconciled final report with an unverified native exit. Acceptance does not make blocked/unverified operations pass. The 14 installed Skill files remain unchanged from evaluated rc.1. Historical failures remain evidence, not retroactively passed tests.

## Product contract

- [x] A reviewable project-aware configuration tool, not a promise of error-free AI analysis.
- [x] Both execution hosts and both configuration targets are in scope. Default target is the executing host; explicit Claude/Codex/both requests override it.
- [x] Generated-Agent invocation, benchmarks, global settings and automatic orchestration are excluded.
- [x] File-tool damage, unauthorized deletion, path escape, conflict overwrite and incorrect recovery are release blockers. AI semantic omissions/review skips/unnecessary revisions are classified and disclosed; no perfect semantic pass rate is required.

## Coding and automated gates

- [x] Claude interface unchanged; standalone Codex TOML checker and target-specific model/capability guidance verified.
- [x] Guarded prepare/check/apply covers both targets, exact deletion allowances, formatting, stale originals/candidates, no-op replay and conditional recovery.
- [x] Negative/fault tests pass for mid-application failure, another writer's changes, incomplete writes/task records, links/junctions and unavailable dependencies.
- [x] Installer/update preserve customized Skills and both Agent trees; captured public alpha.8 upgrade fixtures pass.
- [x] Exact tarball includes only intended CLI/Skill/docs/license files and exercises the installed checker/application scripts.
- [x] Complete Node/Python/Skill checks and all six OS/Python CI combinations pass on the [RC commit](https://github.com/ChiwooSong/configure-subagents/actions/runs/41463247317). No live models run in CI. Baseline: 64 Node tests, 115 Python tests; platform-specific tests may be skipped where inapplicable.

## Installed RC behavior campaign

The [RC report](../evals/RC1_BEHAVIOR.md) separates target, host, tool result, structured report and semantic assessment. The 22 sessions are bounded evidence, not a success-rate guarantee.

- [x] Original 22 sessions attempted: each host has two proposals, two synthetic apply/repeat pairs, two real-project pairs and one validation-only outcome. Claude validator permission blocks and the last missing exit receipt are explicitly distinguished from passes.
- [x] Inputs and installed Skill bytes frozen; host versions, requested/observed models, commands, bytes/mtimes, failures and approvals recorded where available. Seven native repeat bindings verified; the last repeat's final report/current files observed, with native start/end binding and return code unverified.
- [x] Default target and cross-target protected application success plus a same-state no-change repeat observed in each host's synthetic pairs. Authentication/permission blocks are not passes; this does not close real-project coverage.
- [x] Module-inclusive real-project behavior explicitly accepted as unverified in the November 3 stable decision. Initial inputs omitted `.mjs`/`.mts`; harness fixed with 116 passing Python tests. No corrected-cohort model runs occur. Retain original real outcomes as partial-input evidence, not passed full-context evaluations.
- [x] Evaluation writes scoped to copies, not original projects; conservative filename/header screening and runtime/dependency exclusions documented. Concurrent original changes observed without rollback; no OS-wide tracing claim.
- [x] All 22 outcomes retained and classified, including capture/evidence gaps. No rerun-until-green policy or replacement model session for the closed last window.
- [x] Known R8 and current workflow/memory-scope first-pass/cross-review failures remain disclosed; no intrinsic-model-cause, runtime-use or cost-saving claim.
- [x] Missing last native exit receipt and Claude validation-only permission block explicitly accepted as unverified in the November 3 stable decision. Reconciled current file equality is not a successful process-exit claim; no additional model sessions authorized or launched for promotion.

## Compatibility, publication and stable decision

- [x] Public CLI arguments/paths/outcomes, checker JSON schema/exit codes, parser dependencies, target controls and manual recovery/merge workflows documented.
- [x] Package scope/owner, MIT, repository/migration links and Git/tarball contents audited.
- [x] RC published to next; registry integrity/metadata and fresh artifact install/update/conflict/no-op tests pass. On November 3, `latest` moved from alpha.2 to alpha.8 at the maintainer's request; `next` remains rc.1. The alpha tag is not stable approval. [RC release and exact-artifact receipts](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0-rc.1).
- [x] Public RC result/limitation ledger includes all 22 outcomes, native evidence gaps, source/CI links, installed hashes and exact artifact verification. Host behavior is Windows evidence; cross-platform CI is static evidence.
- [x] Maintainer separately approved GitHub and npm latest publication of 1.0.0 after reviewing results, accepting documented limits and skipping rc.2.
- [ ] Final 1.0.0 metadata/docs/latest channel, exact-commit CI and public artifact verified. A Skill payload change returns to affected RC evaluation; metadata-only promotion does not imply new host runs.

Prior baselines: [alpha.8 model selection](../evals/MODEL_SELECTION_BEHAVIOR.md), [R8 source retrieval](../evals/RETRIEVAL_AUDIT_BEHAVIOR.md), [updates](../evals/UPDATE_COMMAND.md). They do not substitute for the installed RC campaign.

## Whether to create rc.2

An rc.2 is needed when a new distributable change warrants another candidate, not merely because rc.1 evaluation ended. No release-blocking shipped file-tool defect was observed in this bounded campaign. The module-capture correction changes development QA, not the 14 installed Skill files.

1. Close and publish the result/limitation ledger, distinguish model judgment limits from reproducible tool defects, and decide what concrete payload change (if any) is needed. Keep the documented incomplete-input and native-exit scopes visible.
2. If changing the Skill, add verified pristine rc.1 upgrade fingerprints, keep customization/Agent preservation, run all automatic/CI/tarball gates, and evaluate the affected behavior using the new installed candidate. Do not inherit old behavior results for changed Skill bytes or require flawless AI semantics. No further model calls are authorized by this checklist alone.
3. Publish a changed candidate as rc.2 to `next`, verify registry/artifact installation and disclose its evidence. If shipping payload changes are unnecessary, the maintainer may instead review rc.1 for stable promotion while explicitly accepting unverified scopes; rc.2 is not a mandatory milestone.

Stable readiness depends on accepted evidence and final checks, not a fixed waiting period or a required number of RCs. The maintainer chose metadata/documentation-only promotion from rc.1 on November 3. Stable metadata, final exact-commit CI and tarball/registry verification remain required; publication receipts are attached to the [1.0.0 release](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0).
