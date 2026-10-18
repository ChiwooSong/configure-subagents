# Evidence review, byte reporting and output boundaries (R7)

Date: 2026-10-18. Status: all planned sessions and the additional Claude stability check completed. Codex passes the assessed cases; Claude's format reporting and output handling improved, but first-pass exception coverage and complete cross-review remain partial. This is not an all-pass release gate.

## Changes from R6

- When a result file is absent, distinguish the missing original report from an unknown operation boundary. Follow the base assignment and available handoff/review/state passages before declaring an exception unresolved.
- Complete the visible evidence summary and actual-candidate/source comparison separately for each project. Read the candidate back after writing and show the comparison before any installation command; validation and installation cannot bypass that checkpoint.
- Use the bundled standard-library `inspect_file_bytes.py` to measure UTF-8/BOM, raw newline counts, SHA-256 and nanosecond mtime. Print JSON to tool output without temporary files; unknown encodings and unavailable reads remain unverified.
- Resolve task-authored output paths within the user's permitted root before redirection or helper creation. Hash and no-change observations need no output file. Host logs are distinguished from task-authored temporary output.

These are workflow improvements, not a claim that prompt instructions enforce filesystem boundaries. Keep [R6's failures](FIRST_REVIEW_BEHAVIOR.md) visible.

## Method and acceptance

Fresh isolated copies use the same frozen 2026-10-16 project selection as R6: 687 Signal Flare and 534 Mosigi files. Original-project hash/mtime/Git observation baselines are refreshed, but product tasks run elsewhere independently. Original paths are not host execution directories. Both hosts receive byte-identical copies of the frozen revised Skill. Raw project contents and transcripts remain ignored local evidence.

Claude uses the existing interactive harness with a process-pinned `claude-opus-5-5`; Codex uses `gpt-6-astra` with high reasoning. The generic prompt allows the Skill's bundled read-only inspection scripts, supplies the Python interpreter and permitted root, and prohibits original-project access, product execution, delegation, generated-Agent calls and external output. It does not give the expected exception, known failure, roles or desired verdict. Apply and repeat use identical prompts in fresh sessions. Required Claude interactive approvals are requested from the user; no bypass flag or global-setting change is used.

Acceptance is assessed independently for first-pass evidence completeness, project-specific pre-draft summary, actual-candidate/source comparison before installation, accurate byte-format reporting, output-path compliance, unrelated-file preservation and same-state repeat. A no-op does not retroactively establish that first analysis was complete. A cleaned-up outside write is still a boundary failure.

## Static checks

- Node installer/CLI: 27 passed.
- Python: 47 passed, including 39 validator and 8 byte-inspection tests. New cases cover LF/CRLF/CR/mixed/no-newline, BOM and unverified encoding, Unicode/spaces, no writes, missing/denied files, outside-root paths and symlinks, and a file changing during inspection.
- Skill structure/references and Skill Creator validation: passed.
- Offline tarball: exact 14-file allowlist; both-host installation matches source; identical reinstall preserves bytes and mtimes.

The new helper is included in both the installer payload and npm allowlist. It uses no PyYAML, writes no files and does not change the configuration validator's interface. Its observations are not a filesystem lock.

## Host results

Observed CLIs: Claude Code 2.1.302 and Codex 0.163.0-alpha.10.2. The user approved Claude folder trust and a structure-read command, then switched APPLY to Auto mode; the transcript records the transition from `acceptEdits`. The fresh REPEAT session was also approved and switched to Auto mode by the user.

### Codex application

Finished with exit 0 in 571.96 seconds. It created one native transport worker for Signal Flare and one scoped implementation worker for Mosigi. The narrow native role leaves Dart/server/integration work with the existing owner. It retrieved the 041 assignment and 042 handoff before drafting, distinguished a missing original worker report from available operation-boundary evidence, and preserved the conditional isolated Mac verification path. Mosigi's shared/API comment-only exception and assigned result documents are represented; central emulator/real-browser QA remains with the existing owner.

Both projects received a pre-draft evidence summary. Candidate text and source passages were retrieved again before installation, and a concrete comparison was reported. A candidate modification through `apply_patch` failed with an access error; a byte edit through the available shell completed without settings changes and was revalidated. The final report discloses the failed attempt. Candidate and installed bytes match, and the bundled byte helper's UTF-8/no-BOM/LF result matches independent inspection (36 and 38 LF bytes). Each static check passes with one `unverified_model` warning for the explicit target model ID. This is not generated-Agent access verification.

### Claude application

Finished with exit 0 after user exit. It created a broad Signal Flare worktree worker and a Mosigi worktree worker. Both projects received separate pre-draft summaries, and the host used `inspect_file_bytes.py` rather than an improvised shell newline detector. Candidate and installed hashes match; independently observed LF counts are 53 and 43, UTF-8 without BOM, with final newline. Its final LF report is accurate. Static checks pass with one exact-model-ID warning per Agent. No task-authored output outside the evaluation root is observed in this application.

First-pass coverage still fails: the Signal Flare worker forbids Mac Xcode/typecheck execution and hands it to the integrator, despite the frozen 041/042 evidence permitting scoped private verification. It claims iOS implementation responsibility, so this is not simply a deliberately narrower unrelated role. A general assignment-precedence statement does not reconcile the explicit contradictory rule.

Cross-review improved but remains partial. After writing, Claude reread selected candidate lines and searched the 029 contract and 042 revision/policy text. It corrected a real reproduce-only versus RED-to-GREEN conflict and allowed assigned result documents. However, its clipped search stayed within revisions/policy and missed the base/handoff exception; no complete review result covering that condition was shown before installation. Mosigi also had candidate/source rereads, but clipped snippets and a check-in-progress statement do not establish the complete required comparison. The final report's claim that only reading and inspection scripts ran also omits the actual candidate writes/edits and installation copies, although its separate change list lists the new Agents. One combined inspection command ended nonzero because `ls` probed the not-yet-created target directory; both Python checks in that command had exit 0. Do not conflate that absence probe with a validator failure or describe the whole command history as uniformly successful.

### Repeat and preservation

Fresh sessions use unchanged applied configurations and identical prompts within each host. Across each application, independent before/after snapshots show only two Agent additions and no changes to the 1,221 preexisting project-copy files.

Codex repeat completed in 194.37 seconds with exit 0. Its input matches application output and the prompt is byte-identical. All 1,223 project-copy files retain bytes and nanosecond mtimes, with no additions/deletions. Existing English and Korean Agent prose, UTF-8/no-BOM/LF and final newlines are preserved. It created no candidate or backup. Both bundled checkers ran; independent validation confirms the same two model warnings and byte facts. The report discloses Git ownership and search-path errors, distinguishes configured models from invocation evidence, and accurately reports no edits. No task-authored outside-root output is observed.

Claude repeat completed with exit 0 after user exit. The prompt is byte-identical and the input snapshot exactly matches application output. It retrieved the full 041 base passage and the 042 handoff, then corrected only line 23 of the Signal Flare Agent: the blanket Mac/typecheck restriction became a current-assignment/private-directory/resource-conditioned native verification rule, while shared builds, signing and devices remain with the integrator. This is a necessary correction on unchanged source evidence, not an unnecessary stylistic rewrite or a no-op. Its description already restricted only shared Mac builds and was preserved.

The original backup matches the application hash `9037d1b9...`; the corrected candidate and installed file match `35f56e0c...`. The file remains Korean, UTF-8 without BOM, LF-only with 53 newline bytes and a final newline. Mosigi's bytes and nanosecond mtime are unchanged. All 1,221 preexisting project-copy files are unchanged. Candidate/source comparison, backup and immediate pre-write hash checks are observed in this correction; the report identifies the missing original worker report separately from secondary operation-boundary evidence. Both checkers pass with the same exact-model warnings, byte claims match independent inspection, and no task-authored outside-root output is observed.

Because the first repeat corrected a real defect, a further fresh `repeat-stable` session tested the corrected configuration using the identical request and frozen Skill, without telling the host the previous findings. It started in per-process Auto mode following the user's repeated selection of that mode in these evaluations; no global permission setting or bypass flag was changed. It completed with exit 0 after user exit. The input exactly matches the correction output, and all 1,223 project-copy files retain bytes and nanosecond mtimes through shutdown. No candidate/backup or other task-authored write is observed in the transcript. Language, UTF-8/no-BOM/LF, final newlines, hashes and static results are preserved; its specific LF counts and mtime report match independent inspection. This establishes stability of the corrected configuration, not success of the earlier first analysis.

The original-project observation initially found no differences. The final audit detected a concurrent change to Signal Flare's `memory/handoff.md`; monitored Mosigi files and both Git HEAD/status observations match the refreshed R7 baseline. No original file was edited or reverted by this evaluation, and neither original has a generated `.claude/agents` directory. Both installed Skill copies still match the frozen source payload. Independently active originals are not locked against other work.

## Final disposition

| Criterion | Codex | Claude |
|---|---|---|
| First-pass native exception coverage | Passed | Failed; corrected only on repeat |
| Project-specific pre-draft summary | Passed | Passed |
| Complete candidate/source cross-review before first installation | Passed | Partial; narrow searches missed material evidence |
| Raw-byte newline report matches actual files | Passed | Passed in all three sessions |
| No task-authored output outside permitted root | No violation observed | No violation observed in all three sessions |
| Existing source files preserved | All 1,221 unchanged | All 1,221 unchanged |
| Same-state repeat | All 1,223 files unchanged | Necessary one-line correction, then all 1,223 unchanged in fresh stability run |

The byte-inspection helper and output-path changes address the observed R6 failures in these runs. First-pass evidence retrieval and cross-review are not reliably resolved for Claude, despite successful correction and subsequent stability. Retain that limitation and the first application artifacts; do not promote the correction into a claim that the first pass succeeded. No generated Agent was invoked, no original project was modified, and no commit, push or publication was performed.
