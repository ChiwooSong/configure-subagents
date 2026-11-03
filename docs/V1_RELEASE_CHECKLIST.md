# 1.0.0 release checklist

Updated: 2026-11-03 (Asia/Seoul). **RC published; installed-artifact behavior evaluation is in progress. Stable publication requires a separate maintainer decision.** This replaces the earlier three-flawless-pairs gate following the maintainer's product decision. Historical failures remain evidence, not retroactively passed tests.

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

- [ ] Each host: two fresh proposals (default/cross target), two synthetic apply/repeat pairs (default/both), two real-project apply/repeat pairs (default/both), one validation-only session (both).
- [ ] Inputs and installed Skill bytes frozen; host versions, requested/observed models, commands, identities/bytes/mtimes, failures and approvals recorded.
- [x] Default target and cross-target protected application success plus a same-state no-change repeat observed in each host's synthetic pairs. Authentication/permission blocks are not passes; this does not close real-project coverage.
- [ ] Real-project source capture includes relevant module wrappers and supporting source. Initial inputs omitted `.mjs`/`.mts`; harness fixed with 116 passing Python tests, corrected cohort decision/evaluation still pending. Retain old outcomes as partial-input evidence.
- [ ] Both real-project sources preserved; ignored evaluation copies exclude secrets, runtime data and dependencies. External source changes are reported without rollback.
- [ ] All 22 outcomes retained and classified: tool defect, model/host judgment limit, permission/authentication block or harness defect. No rerun-until-green policy.
- [ ] Known R8 first-pass/cross-review failures remain disclosed; no intrinsic-model-cause claim, runtime-use claim or cost-saving claim is inferred.

## Compatibility, publication and stable decision

- [ ] Public CLI arguments/paths/outcomes, checker JSON schema/exit codes, parser dependencies, target controls and manual recovery/merge workflows documented.
- [x] Package scope/owner, MIT, repository/migration links and Git/tarball contents audited.
- [x] RC published to next; registry integrity/metadata and fresh artifact install/update/conflict/no-op tests pass. `latest` was left at its prior alpha.2 value. [RC release and exact-artifact receipts](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0-rc.1).
- [ ] Public RC result/limitation ledger complete with commit, CI, installed hashes and exact artifact verification. Host behavior is Windows evidence; cross-platform CI is static evidence.
- [ ] Maintainer separately approves stable publication after reviewing results.
- [ ] Final 1.0.0 metadata/docs/latest channel, exact-commit CI and public artifact verified. A Skill payload change returns to affected RC evaluation; metadata-only promotion does not imply new host runs.

Prior baselines: [alpha.8 model selection](../evals/MODEL_SELECTION_BEHAVIOR.md), [R8 source retrieval](../evals/RETRIEVAL_AUDIT_BEHAVIOR.md), [updates](../evals/UPDATE_COMMAND.md). They do not substitute for the installed RC campaign.
