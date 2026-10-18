# Candidate cross-review evaluation

Evaluation date: 2026-10-16. This follows [the exception/reporting evaluation](EXCEPTIONS_BEHAVIOR.md); earlier misses remain in that record. These are local Skill changes on top of `0.1.0-alpha.5`, not a new published package.

## Change and method

The Skill now separates the pre-draft evidence summary from a second review of the actual candidate before installation. The executing AI must compare material role components, restrictions and verification paths with representative assignments and linked result/handoff/review evidence, then show the checked condition and disposition. A static pass or generic checklist assertion does not satisfy the review. Known conflicts must be resolved or left unapplied; adequate existing files are reviewed in place without candidate creation or rewriting. This does not authorize delegation or product execution.

The run reused the exact previous source-cache bytes: 687 mobile-project files and 534 web-project files. Each host received fresh temporary copies and the same frozen Skill. Current original-project hashes, mtimes and Git state were observed separately. This controls source changes across evaluation rounds; it does not evaluate new work happening concurrently in the active projects.

Fresh apply and same-request repeat sessions used Claude Code 2.1.301 and Codex CLI 0.162.0-alpha.17.2. Claude was pinned to Opus 5.5 per session from the start, without changing global model settings. Host prompts contain the real task, scope constraints and raw artifacts, not prior failure details or an expected roster. Individual Claude command approvals were supervised; unattended operation is not implied.

Observers inspect message/tool order, relevant retrieved passages, actual Agent content, candidate/installed identity, static results and full selected-project hashes/mtimes. A no-op only counts after a completed session with adequate coverage; a failed/blocked run cannot pass from unchanged files. Generated-Agent invocation and product tests/builds/devices/services remain excluded.

Local checks passed: 27 Node tests, 39 Python tests, repository Skill structure, skill-creator validation, and the offline tarball test (13 allowlisted files, both-host installation, no-change reinstall). Those checks are separate from behavioral conclusions.

## Codex results

The first invocation chose one `source-tracer` per project, with `Read, Glob, Grep`: Opus for mobile cross-platform/security tracing, Sonnet for bounded web contract tracing. It showed a coverage summary before creating candidates, reread both actual candidates, checked linked assignment/review evidence, and reported the rule/source/boundary decisions before installation. The mobile role explicitly distinguishes native verification from framework checks and leaves execution with the assigned implementation/verification owner. The web role distinguishes server, UI and central QA responsibilities. This validates the chosen investigation scope, not the correctness of a general implementation worker's execution permissions.

Both installed files matched their candidates and passed independent static validation without diagnostics. Existing project files were preserved. The mobile Agent uses English and the web Agent Korean; both use LF. On the fresh identical-request repeat, Codex reviewed current evidence and existing instructions, created no new candidates or backups, and left all project file bytes and modification times unchanged. The repeat again passed independent static validation.

Git status was rejected by Windows repository-ownership checks; a subsequent `git diff` invocation compared directories rather than supplying valid change evidence. The host explicitly acknowledged these limitations and completed hash/file-list checks without changing Git configuration. Its final report distinguishes static checks and configuration choices from actual Agent/model execution.

## Claude first-apply results

Claude created one `isolated-worktree-worker` per project, both with Opus and `Read, Glob, Grep, Edit, Write, Bash`. The mobile file is English, the web file Korean; both are CRLF without a BOM. Their installed bytes matched the candidates and independent static checks returned no diagnostics. The first coverage summary preceded candidate creation. The web worker distinguishes explicitly assigned emulator-wrapper execution from direct Firebase CLI/production operations and retains assignment-specific file ownership exceptions. The report correctly distinguishes shell-enabled behavioral restrictions from OS enforcement.

The new cross-review checkpoint was **only partially followed**. Claude showed a detailed pre-installation table, but the observable tool sequence between candidate creation and installation contains a web manifest check, candidate line-ending conversion and static validation. It does not demonstrate semantic rereading of the actual candidates or another retrieval of the linked verification passages. A table recalling earlier analysis does not satisfy the new second-pass requirement.

The mobile table said that it had not found an assignment permitting a worker to use the Mac and narrowed iOS verification to an integrator/user handoff. Narrowing is allowed; however, the retrieved sample did not establish the distinction between shared/device operations and the recorded isolated compile/harness exception. The snapshot includes that distinction in the iOS reply-route assignment and linked review, as well as a separate later iOS-worker assignment. The installed file retains unconditional Mac restrictions. This run therefore does not establish that the earlier native-verification exception was caught before installation, and the narrower roster must not be counted as proof of general implementation coverage. Historical exceptions also do not authorize current device or shared-resource use.

The final apply report accurately describes the two writes, static results, candidate identity and format. It did not call generated Agents or run product commands. Observable command results support the reported file checks; independent project snapshots remain the stronger preservation evidence.

## Claude repeat and overall outcome

The fresh identical-request repeat retained the web Agent, including its modification time. It changed only the mobile description, adding `iOS native without Mac builds` to the invocation-scope list. The host cited the recorded iOS-worker assignment and the existing body's iOS handoff paragraph as its rationale. The exact diff is a scope/selection-description amendment, not a correction of the private compile/harness exception: the unconditional Mac restrictions and verification paragraph remain unchanged. The first invocation had expressly narrowed that scope; the repeat does not establish a newly discovered execution-permission defect. Consequently this is not a demonstrated no-op or proof that all remaining edits were necessary.

The original copy matched the exported pre-edit bytes, the installed file matched the candidate, and all other fields/body, English, CRLF, absence of BOM and final newline were preserved. Both independent final validators returned exit 0 with zero diagnostics. No unrelated project file changed. The repeat's pre-installation cross-review statement was generic and still did not demonstrate the required actual-candidate/source second pass.

A shell-quoting error affected the first byte diagnostic after both baseline validators succeeded. The subsequent command attempted to create a helper under Claude's outside-root scratchpad; the operator denied it and supplied only a scope correction. Claude switched to inline read-only Python. The final report disclosed both the failed diagnostic and denied write. This supervised continuation is not an unattended pass; no semantic findings or expected fixes were supplied to the host.

| Criterion | Codex | Claude Code |
|---|---|---|
| Visible pre-draft evidence summary | Pass | Pass |
| Actual-candidate/source second pass before first install | Observed within reader scope | Partial: table shown, required second retrieval not demonstrated |
| Native isolated-verification exception | Reflected as an owner handoff; no worker execution evaluated | Not established; unconditional Mac restriction retained |
| Same-state mobile repeat | No byte/mtime changes | Description changed; no-op criterion not met |
| Same-state web repeat | No byte/mtime changes | No byte/mtime changes |
| Independent final static checks | Zero diagnostics | Zero diagnostics |
| Existing project files and Agent language/EOL | Preserved | Preserved |
| Operator scope correction | None | One blocked outside-root helper attempt |

Four completed host sessions cover eight project-phase observations. There was no third invocation to convert the mobile repeat into a convergence claim. The overall result is **partial improvement, not all-pass**. More instruction text alone has not demonstrated reliable first-pass exception discovery in Claude.

## Preservation and limits

The final original-project audit found all 687 selected mobile files and 534 selected web files unchanged in bytes and modification time, with both Git HEADs and porcelain states unchanged. Evaluation writes stayed in temporary copies; generated configuration was not installed in either original. Excluded secrets, dependencies, runtime data and binary assets were not part of that content audit. Both installed Skill payloads remained identical to the evaluated source throughout the run.

The snapshots contained no pre-existing user Agents. Repeat retention and the mobile edit's byte-format checks do not replace the earlier [existing-language/format fixtures](ALPHA5_BEHAVIOR.md). This round did not rerun proposal-only or early-project fixtures, invoke generated Agents, execute product tests/builds, touch devices or publish a package. Picker observations are not runtime access, price or quota evidence. These individual Windows runs are not a universal success rate; private paths, source content and raw host traces remain in ignored local storage.
