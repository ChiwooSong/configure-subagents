# 1.0.0-rc.1 behavior campaign

Status: **in progress with a real-project input coverage gap**, 2026-11-03 (Asia/Seoul): **19/22 original-matrix final receipts** (Codex 11/11, Claude 8/11). Both hosts' synthetic/default/cross-target checks are recorded, but five real-project outcomes used a capture that accidentally omitted module sources. Three remaining original real sessions are on hold pending a corrected-cohort scope decision. Final process receipts are outcomes, not automatic behavior passes. No generated-Agent invocation is claimed. The [sanitized progress receipt](RC1_PROGRESS.json) records artifact hashes, request/receipt fingerprints and mechanical observations without raw source or transcripts.

Prepublication local baseline: **64 Node tests, 115 Python tests**, Skill structure and skill-creator checks, and the **21-file tarball** install/update/guarded-application/replay smoke pass. This is not cross-platform CI or authenticated host evidence. Independent bounded review reproduced and closed a checked-digest substitution issue and source-screening/repeat-input harness issues; retained reproductions remain in ignored QA storage. Existing failures were not relabeled as passes. The first CI run passed Linux/macOS but rejected legitimate Windows 8.3 temporary paths in artifact preparation; actual component checks replaced spelling comparison, with a Windows short-path regression. The failed [initial CI run](https://github.com/ChiwooSong/configure-subagents/actions/runs/41462355740) remains recorded; its source/tarball was not published to npm.

## Published artifact and automated gates

Published package: `@woody_s/configure-subagents@1.0.0-rc.1`, `next`. `latest` remains at the pre-existing `0.1.0-alpha.2`; stable 1.0.0 is not approved. The [GitHub prerelease](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0-rc.1) contains the exact tarball, checksums and artifact-verification receipt.

- RC source commit: `f047ff791adac4991df52683ca06d984a89ce012`.
- [Final static CI](https://github.com/ChiwooSong/configure-subagents/actions/runs/41463247317): all six Windows/Linux/macOS × Python 3.10/3.13 combinations passed, with Node 22. Platform-specific tests are conditional.
- Registry integrity: `sha512-HwPDyUrU3hspEY+j9pQUu4WeJOLzX47N+PPM48HzBBUWoitmF7HYe0cps9ePZ46aEi7255YMqhk8ffRXupvw1w==`.
- Fresh registry installation matches all 21 expected distribution files. Installed helper checks and guarded both-target application/replay, alpha.8 updates, customized-Skill refusal and existing-Agent preservation passed.

These checks establish artifact/mechanical behavior within their tested scopes; they do not establish AI analysis quality or generated-Agent discovery/execution.

## Method

Use the exact registry-installed RC Skill, isolated fixtures and frozen sanitized copies of the two authorized development projects. Keep raw inputs/transcripts/local paths in ignored evaluation storage. Each repeat is a new process with the same request and starts from its apply result. Each independent pair gets a fresh source copy; do not provide expected answers or prior failures.

Record requested/observed execution model separately from configured target models. Classify mechanical preservation/application, private JSON reporting and semantic findings independently. No flawless semantic pass-rate gate applies, but file-tool defects block release. A denied/unavailable operation is not a pass or a successful no-op.

## Planned sessions

| Per-host job | Target | Claude | Codex |
|---|---|---|---|
| propose-default | executing host | Read-only; summary-only configuration drafts | Read-only; complete TOML drafts |
| propose-cross | other host | Read-only; complete Codex TOML drafts | Read-only; complete Claude Markdown drafts |
| synthetic-default apply/repeat | executing host | Guarded apply / Bytes and mtimes unchanged | Guarded apply / Bytes and mtimes unchanged |
| synthetic-both apply/repeat | both | Guarded apply / Bytes and mtimes unchanged | Guarded apply / Bytes and mtimes unchanged |
| real-default apply/repeat | executing host | Partial-input guarded apply / On hold | Partial-input no change / Bytes and mtimes unchanged |
| real-both apply/repeat | both | On hold / On hold | Partial-input guarded apply / Bytes and mtimes unchanged |
| validate-both | both | Validators denied; manual findings only | Both validators ran; seeded errors reported; no writes |

Total: 11 sessions per host, 22 sessions. The four host-to-target combinations are assessed separately. Keep retained attempts and any affected-RC reruns distinct; do not overwrite prior evidence.

## Observed results and limits so far

Execution versions: Claude Code `2.1.316`, observed model `claude-opus-5-5`; Codex CLI `0.166.0-alpha.5.1`, requested model `gpt-6-astra`, actual returned model identity unverified. Configured fixture model IDs are separate from these execution-model observations.

**Proposals.** All four sessions selected the correct default/cross target and preserved workspace bytes and mtimes. Across 11 cases per session, Claude default proposed 19 Agents but used summaries rather than complete installable definitions; Claude cross-target provided 18 complete TOML definitions. Codex default provided 12 complete TOML definitions and cross-target 16 complete Markdown/YAML definitions. Independently parsed complete definitions had no observed syntax/required-field or reported-model mismatch. No observed assignment used an ineligible or unverified fixture candidate. Different role counts are not a quality ranking. The static results for empty installed proposal directories are not validation of proposed strings.

**Codex synthetic application.** Default and both-target sessions used the installed prepare/check/apply helper, preserved explicitly fixed models and custom integration comments/fields, made justified prompt/model changes, and removed only the explicitly authorized obsolete Agents. Unselected target files and non-Agent integration files were unchanged. Independent checks confirmed candidate/installed byte equality, UTF-8/BOM, LF/CRLF style and final-newline preservation. Both fresh repeats preserved all observed workspace file bytes and mtimes, including transaction records, without new preparation/backups. The both-target repeat encountered a native 429 and resumed through the CLI's retry; this delay remains in the retained trace.

**Claude synthetic application.** Both default and both-target pairs completed guarded application and fresh identical-request repeats. Pinned models, existing instruction languages, comments, custom fields and non-Agent files were preserved. Only explicitly requested obsolete files were deleted. Independent candidate/installed byte checks confirmed the six retained both-target Agent files kept BOM/newline style/final newline. An intermediate `sed` candidate edit normalized CRLF and missed model insertion; the host repaired the candidates before check/apply and disclosed the error. Installed files were not affected by that draft error. Both repeats preserved observed bytes and mtimes, including transaction records, without new preparation/backups.

**Codex real projects.** The default-target pair reused the main Codex PM/review role and existing Claude workers instead of adding duplicate Codex Agents. Both sessions changed no files; empty Agent directories were disclosed as `no_agents`, not runtime validation. The both-target first application minimally updated one existing Claude worker per project and added one Codex reviewer per project using two complete guarded transactions. Existing reviewers, source and unrelated workspace files were preserved. Its fresh repeat preserved workspace bytes and mtimes, including candidate/backup/journal records, and did not prepare another transaction. Some conditional resource/test-assertion and memory-policy exceptions improved. A semantic concern remains: Signal Flare's retained general red → fix → green sentence is broader than reproduction/design-only assignments that permit expected failures and no product edits. Task-specific ownership text may constrain it, but first application did not resolve the broad wording and the repeat did not report it. This is a configuration judgment concern; no unauthorized execution was performed. No-change replay is not proof of semantic completeness.

**Claude real default, partial input.** The first application used two complete guarded transactions, changing the Signal Flare reviewer's completion/account-async checklist and only the Mosigi worker's numeric memory threshold. Other Agents and source were preserved; installed static checks passed with existing model-ID warnings. The edited memory line remains generic although the source policy scopes the lower threshold to specified central serial QA roles. This is a semantic scope concern, not observed program execution. The session accurately left the absent wrapper unverified; the wrapper was omitted by the harness, not absent from the original. Its repeat has not run.

## Real-project capture correction

The original source allowlist unintentionally excluded `.mjs`, `.cjs`, `.mts` and `.cts`. The original exclusion manifest lists **24 `.mjs` and 12 `.mts` files**, including the emulator wrapper and its supporting modules. Read-only inspection confirms the wrapper exists in the original. Earlier missing-wrapper observations describe the supplied frozen input and must not be attributed to a host failing to read available source or to missing original project files. Mechanical application/replay observations remain retained, but the five completed real-project sessions have incomplete source context.

The harness now includes those module-source extensions. A new regression verifies module inclusion, source bytes/mtime preservation and continued exclusion of credential names, private-key contents, dependency directories and root runtime data. All **116 current Python tests** pass (the published RC's prepublication baseline remains 115). This harness-only change does not change the installed RC Skill or require a new npm artifact. Fresh selected captures contain **678 Signal Flare and 726 Mosigi files**, including the omitted modules. The projects also progressed between captures, so these are a new frozen cohort rather than an isolated causal benchmark of the extension fix.

A proposed bounded replacement uses eight fresh real-project sessions (both hosts × default/both target × apply/repeat), replacing the remaining three unstarted old-input sessions. The five old-input outcomes stay visible: 27 total attempts, 22 primary-matrix outcomes if the replacement is approved and completed. Additional model-use scope is awaiting the maintainer's decision; no corrected-cohort model sessions have started. Do not alter existing snapshots, splice in missing files, or rerun semantic failures until green.

**Validation and permissions.** Codex executed both installed validators: malformed growth YAML and duplicate-key TOML returned errors, Korean files passed with preserved unknown-field warnings, and the session made no writes. Claude's headless validator commands were denied by native permission checks (the generated shell loops did not match the narrow helper allowlist). Its report accurately marked execution unavailable and gave manual findings; independent external checks corroborated the seeded errors but do not turn the denied host operations into passes. Claude proposals also retained denied Bash operations while continuing with permitted read tools. Claude application/repeat evaluation requires interactive approval, not a permission bypass.

Retained Codex command failures also include a PowerShell brace-expansion parse error and incorrect/missing search paths. The host corrected the syntax/paths or left absent execution scripts/results unverified; these commands are not labeled successful. `git diff --no-index` exit 1 for intended differences is distinguished from an apply failure. All four repeat inputs matched their application requests and started at the recorded application output.

**Sources.** Initial frozen captures contain 675 selected Signal Flare and 691 selected Mosigi files, with the module-coverage limitation above. Evaluation requests and changes operate on copies. During the campaign, selected original PM/state/handoff documents differed in recorded bytes and/or mtimes, and Signal Flare Git state differed from capture. No source restoration or rollback was attempted. Preserve that observation separately from evaluator task-authored writes and from immutable-copy preservation. Workspace snapshots exclude `.git` and `__pycache__`, and are not OS-wide write tracing; host-maintained runtime logs are outside their scope. Filename/header screening is not a universal secret detector; raw source captures, local paths and transcripts remain ignored/private.

No release-blocking file-tool failure has been observed in these completed authenticated applications. Remaining Claude application evidence, final classification of all 22 outcomes and the maintainer's stable decision are still required. Historical R8 omissions remain limitations, and this partial campaign does not establish error-free exception discovery, universal model compatibility or cost savings.

## Reproduction

Use an approved Python with Skill parser dependencies. `capture` copies selected project files into ignored storage without running code or modifying the source. Filename/directory and private-key-header screening is deliberately conservative, not a universal secret detector; inspect the capture manifest and exclusions before exposing a snapshot to a host.

```text
python evals/evaluate_release_candidate.py capture --output .eval-runs/rc1-example --project-source signal_flare "<authorized-source>" --project-source mosigi "<authorized-source>"
python evals/evaluate_release_candidate.py session --output .eval-runs/rc1-example --host codex --job propose-default --skill-source "<registry-installed-package>/configure-subagents"
```

The second command prepares and prints a request without a model call. Add `--run` for one authenticated session; select a job from the table's expanded apply/repeat names. Use `--interactive` from a visible terminal for Claude apply/repeat and type `/exit` after the final report. A new invocation is a fresh process. Windows Codex uses the already configured `--windows-sandbox elevated|unelevated`; no sandbox weakening is used. Record artifact origin/integrity alongside the campaign, and use a new campaign after Skill changes. Never overwrite an attempt.

## Limits and decision

Prior [alpha.8 evidence](MODEL_SELECTION_BEHAVIOR.md) and [R8 failures](RETRIEVAL_AUDIT_BEHAVIOR.md) remain separate historical observations. Final publication requires the [release checklist](../docs/V1_RELEASE_CHECKLIST.md) and a separate maintainer decision. Actual generated-Agent discovery/invocation, measured performance/savings and untested OS/model/provider combinations remain outside this campaign.
