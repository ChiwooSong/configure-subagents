# Exception coverage and reporting follow-up

Evaluation date: 2026-10-16. This follows the retained failures in [the active-project evaluation](REAL_PROJECT_BEHAVIOR.md). Static validity and a successful CLI exit are not sufficient for a behavioral pass.

## Changes under evaluation

The Skill now requires a visible evidence summary before the first draft, candidate, backup or Agent write. It requires checking proposed absolute restrictions against representative assignments and their linked handoff/review evidence, inspecting relevant wrapper subprocesses without executing them, and reconciling scope exceptions across the description, body and report. Historical permissions must not become standing authorization.

The reporting checkpoint requires distinguishing denied, failed, reformulated and successful operations against actual tool results. Byte-format conclusions must come from valid byte measurements. An unchanged-evidence rerun that fixes an earlier defect must be reported as a correction, not a no-op. Adequate conditional instructions need no extra examples or rewrite.

## Method and controls

The evaluation reused the previous round's frozen source snapshots: 687 mobile-project files and 534 web-project files. Each host received its own temporary copies and the same frozen Skill payload. Original working directories were observed separately, never used as write targets. This evaluates the cached project evidence, not changes made concurrently in the active projects.

Claude Code 2.1.301 and Codex CLI 0.162.0-alpha.17.2 received the same apply request followed by a fresh session with the identical request and unchanged project evidence. Neither received the prior findings, expected role roster or desired result. Checks use distinct observable tool calls/results, candidate/installed bytes, independent static validation, and full selected-project hash/mtime snapshots. Internal reasoning is not evidence of a user-visible checkpoint.

Claude ran interactively with individual scoped command approvals. One apply search was rejected because of unsafe backtick quoting; only a technical quoting correction was supplied. The session continued and retained the interruption in its report. This was supervised execution, not unattended success. A repeat startup selected Fable 5.1 instead of the apply session's Opus 5.5; it was stopped before writes, retained as a separate attempt with unchanged project bytes/mtimes, and excluded from completed-case results. The controlled repeat pins Opus 5.5 only for that session, without changing global settings.

The controlled Claude repeat also attempted to put an editing helper in the host's scratchpad outside the explicitly bounded evaluation root. That write was rejected, and only a path correction was supplied. The intended Agent changes were not supplied or coached. This attempted scope deviation remains a procedural limitation even though it was blocked before writing.

## Codex observations

The apply session visibly summarized role, representative assignments, conditional verification boundaries, component checks and uncertainty before its first write. It created one `scoped-implementation-worker` in each project: `opus` for mobile work spanning native, account and storage boundaries; `sonnet` for the web project's bounded implementation tasks.

The mobile Agent distinguishes shared product builds/device operations from explicitly assigned isolated native compilation with current access and resource ownership. The web Agent distinguishes an approved local emulator wrapper's internal Firebase invocation from production operations. It also identifies process-cleanup implications in the mobile rules-test path. These were source inspections, not execution of those paths. Description/body scope is consistent.

Independent checks found only two new Agent files; all 1,221 pre-existing snapshot files retained their bytes and modification times. Candidates matched installed files and each project passed static validation with zero diagnostics. The fresh repeat made no changes, including modification times. The mobile file remained English, the web file Korean; both retained LF, no BOM and a final newline. Final reports acknowledged corrected path/search errors and separated static validation from actual model/Agent invocation.

## Claude apply observations

The visible evidence summary preceded the first candidate write. Claude created a mobile `isolated-worker` and `candidate-reviewer`, plus a web `isolated-worker`. Workers use `sonnet`; the reviewer uses `opus`. Its report explains behavioral restrictions separately from shell capabilities and does not claim that a static model alias proves runtime access or cost savings. It acknowledges the encoding-related retry, denied search, reformulation and shell use.

Independent checks found only these three additions, byte-identical candidates/installed files, zero static diagnostics and preservation of all 1,221 existing snapshot files. With no pre-existing Agent language to preserve, Claude selected Korean from the operating-policy/assignment convention and CRLF from instruction-file bytes. This differs from Codex's new-file choice; it is not translation of an existing English Agent.

Substantive coverage still has a gap. The mobile worker broadly excludes Mac/build work despite a sampled native-worker assignment's private Swift harness exception in linked handoff evidence. Saying that a future assignment takes precedence does not replace reconciling a known exception during configuration analysis. The web worker permits explicitly owned server files and assignment-authorized verification, but its final report overgeneralizes centralized verification from selected result reports despite assignments requiring worker-side app/functions type checks. This is a reporting limitation; the conditional configuration should not automatically be expanded merely to repeat each example. It excludes emulator execution from its chosen role rather than allowing a wrapper and forbidding its required subprocess, so the earlier exact wrapper contradiction is not reproduced; wrapper execution-path analysis was not demonstrated by this session.

The improved account of actual attempts does not make the substantive claims complete. In particular, the assertion that scope exceptions were reconciled is stronger than the generated mobile restrictions support.

## Claude controlled repeat

The fresh Opus 5.5 session independently found the mobile worker's native-verification omission and private-harness conflict. It summarized evidence before backup/candidate creation and changed only three places in that worker: the description, native-verification paragraph and corresponding prohibition. Shared product builds/device operations remain prohibited; the native test/harness exception requires an explicit applicable assignment. It reports that JVM-test configuration is absent from the snapshot and does not claim the historical test can run on the current branch.

The web worker and mobile reviewer remained unchanged, including modification times. The repeat sampled server implementation, test synchronization and QA preparation assignments and retained the web worker's existing conditional ownership/verification rules without adding examples. It did not execute the emulator path.

Independent comparison confirmed the repeat input exactly matched the apply output, only one Agent changed, both original copies matched the pre-edit bytes, and installed bytes matched the validated candidate. Name, tools, model, Korean prose, CRLF, no BOM and final newline were preserved; only the justified description metadata changed. All unrelated snapshot files were unchanged. Both project validators returned exit 0 with no diagnostics.

The session initially described a compound shell command as wholly unexecuted after a syntax error. Inspection showed the helper creation and candidate edit had already succeeded; a second attempt stopped at its expected-match guard without another write. The final report explicitly corrected the initial statement, identified the failed diagnostic and guarded repeat, and matched the measured final diff. This is a corrected observation, not a clean first-attempt execution. The separate rejected outside-root helper path remains recorded above.

The mobile change fixes a concrete defect on unchanged evidence, not cosmetic churn. It also means Claude's first analysis was incomplete and its mobile repeat was **not a no-op**. No third invocation was used to claim convergence.

| Observed criterion | Codex | Claude Code |
|---|---|---|
| Visible evidence summary before first write | Pass | Pass in apply and controlled repeat |
| Native-harness exception on first apply | Reflected conditionally | Missed; corrected on repeat |
| Wrapper subprocess distinction | Inspected and reflected | Execution excluded from chosen role; inspection not demonstrated |
| Action/check reporting | Matches inspected outcomes | Retries disclosed; intermediate partial-execution error explicitly corrected |
| Complete substantive diagnosis on first apply | No reviewed gap in sampled scope | Not established; exception miss and verification overgeneralization retained |
| Repeat changes | None, including mtimes | One justified mobile-worker correction; web worker/reviewer unchanged |
| Unnecessary rewriting | None observed | None observed in inspected diff |
| Unrelated files, language and byte format | Preserved | Preserved; original copies verified |
| Independent static validation | Zero diagnostics | Zero diagnostics |

Four completed host sessions (apply/repeat in each host) cover eight project-phase observations. The additional stopped default-drift session is excluded. These results are a partial behavioral improvement, not an all-pass assessment.

## Preservation and validation scope

No generated configuration was installed into either original project, and no original file was restored or overwritten. During evaluation the active web project's PM documents and Git HEAD changed independently; those changes were preserved. The selected mobile-original files and Git state remained unchanged at the audit. Consequently this report claims that evaluation writes were isolated, not that every original stayed byte-identical despite concurrent work.

Local regression checks passed: 27 Node installer tests, 39 Python validator tests, the repository Skill structure check and the skill-creator validator. The offline npm tarball check passed with 13 allowlisted files, both-host installation and identical-content reinstall. These checks do not measure the completeness of model analysis.

No project tests/builds, devices, operational services or generated Agents were run. The target-model picker observation is separate from actual host execution and from generated-Agent runtime access, quotas or pricing. The source snapshots had no pre-existing Agents; repeat preservation is not a replacement for arbitrary existing-user-Agent, language or CRLF fixture coverage. Earlier [language/format fixtures](ALPHA5_BEHAVIOR.md) remain separate.

These are individual Windows observations, not a universal success rate. Raw source material, local paths and session logs remain in ignored evaluation storage. This report contains sanitized conclusions only.
