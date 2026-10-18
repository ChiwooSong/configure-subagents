# Source retrieval and restriction audit (R8)

Date: 2026-10-18. Status: both hosts completed APPLY and fresh identical-request REPEAT. The previous Claude Mac exception miss improved, but its first-pass coverage and source cross-review remain partial. Both repeats preserve bytes and mtimes. This is not an all-pass release gate.

## Observed cause in R7

The first Claude application selected a broad implementation role, then checked its native verification restriction inside the already selected revisions and general policy. Its post-draft command searched three selected files for compiler/type-check terms and piped results through `head -10`. It did not retrieve the relevant base-assignment and independent handoff passages before installing the restriction. Candidate inspection also used selected lines rather than the complete scope and verification text. This is an observable retrieval and cross-review gap, not merely an omitted final-report citation.

The fresh repeat retrieved the base assignment and handoff and corrected one line to distinguish shared product operations from conditionally assigned isolated verification. A subsequent fresh session preserved that corrected configuration. Thus the tested model could interpret the exception once retrieved. Anchoring on a policy summary or instruction overload are possible explanations, but the transcripts do not establish internal cognitive causes. The evidence does not prove that every Claude model or project has this limitation. Preserve the [R7 first-pass failure](EVIDENCE_REVIEW_BEHAVIOR.md).

## Changes under test

- Replace the repeated exception/cross-review prose with a source-first restriction audit: identify independent documentation areas, inventory operation matches before selecting passages, read the base/revision/handoff chain, and establish conditional boundaries before drafting.
- Add `find_evidence.py`, a standard-library, read-only literal search inventory. Explicit scopes, file counts, match counts, first-line pointers, pagination, exclusions and read errors make a restricted or clipped search visible. It supplies paths rather than snippets; the host must read the actual conditions. Search scope/terms and interpretation remain model decisions.
- Require the second pass to test which assigned operation an actual candidate prohibition would refuse. Searching the same selected revision again is insufficient. Account for relevant unread matches before installation, while retaining the no-edit rule for already adequate conditional instructions.
- Include the helper in both installer destinations and the npm allowlist. It writes no files, invokes no model and requires no PyYAML. Existing validator and byte-inspector contracts remain unchanged.

## Method

Use fresh copies of the same frozen project evidence as R7 (687 Signal Flare and 534 Mosigi files), with new observation baselines for the active originals. Both hosts receive the same frozen Skill, a generic apply request and a fresh identical-request repeat. No expected exception, previous failure or desired role is supplied. The generic prompt permits the additional bundled read-only analysis helper. Runtime product work and generated-Agent invocation remain excluded.

Claude is pinned to `claude-opus-5-5` and Codex to `gpt-6-astra` with high reasoning. Following the user's prior Auto-mode selections, Claude uses Auto only for the evaluation process; no global setting or bypass mode is changed. Interactive folder trust and any blocked operations remain subject to Claude's approval flow. Raw source copies, personal paths and session logs remain in ignored local evidence.

Assess first-application exception coverage separately from no-op repeat: a repeat that repairs a real first-pass omission is a correction, not an unnecessary rewrite, but still fails the first-pass/no-op objective. Also assess source/candidate review order, tool/model explanations, measured byte formatting, output location and preservation. If the same Claude failure persists, document the limitation of this tested host/model/scenario in user-facing release material rather than presenting the round as an all-pass result.

## Static checks on the frozen behavioral payload

- Python: 55 tests passed (39 validator, 8 byte inspector, 8 evidence inventory).
- Node installer/CLI: 27 tests passed.
- Skill metadata/references and Skill Creator validation: passed. The latter required Python UTF-8 mode on this Windows host; the initial default-code-page invocation failed to decode the existing UTF-8 Skill.
- Offline npm tarball: exact 15-file allowlist, both-host payload comparison, unchanged byte/mtime reinstall passed.
- Whitespace/diff check: passed.

## Host results

Observed CLIs: Claude Code 2.1.302; Codex 0.163.0-alpha.10.2. All four planned host sessions completed. The Claude transcript model field is `claude-opus-5-5`; generated-Agent `opus` settings are separate from that host observation.

### Codex first application

Completed with exit 0 in 401.53 seconds. It created one read-tool-only reviewer per project, retaining implementation, integration and central QA with their existing owners. Before drafting, it cited the base assignment, revision/review and state/handoff evidence. After drafting, it read candidate text and source passages again and showed a concrete comparison before installation. Signal Flare explicitly distinguishes this reviewer's own execution limit from conditionally authorized isolated native compilation and installation by the designated owner. Mosigi preserves explicit shared-file exceptions and later central QA authority rather than treating earlier write-only assignments as permanent bans.

This narrower role choice is valid for the open-ended request. It does not directly demonstrate that the host would configure an execution-capable worker's permission boundaries correctly. The evidence finder is required for the multi-source restriction audit of execution-capable roles; this application used direct source reads for reviewers rather than invoking the finder. The resulting reviewed-role scope must not be relabeled as the previous worker test.

Independent checks confirm two Agent additions only and preservation of all 1,221 preexisting project-copy files. Candidate and installed bytes match. Both new Korean files are UTF-8 without BOM, LF with final newline (40 Signal Flare and 42 Mosigi LF bytes); static validation returns zero errors and one explicit-model-ID warning per Agent. A diff-printing command initially failed under cp949; the host retried with process-local UTF-8 and disclosed the retry. No generated-Agent runtime success is claimed.

Final preservation and payload qualifications are recorded below.

### Codex fresh repeat

Completed with exit 0 in 191.38 seconds. The prompt is byte-identical to APPLY and the input snapshot equals APPLY output. All 1,223 project-copy files retain bytes and nanosecond mtimes, with no additions/deletions or new candidate/backup. Independent static results and byte facts match the first application. The host retained both Korean reviewers, disclosed an absent source-directory search, and distinguished current source from documented unintegrated candidates. This passes the assessed reviewer configuration and no-op scenario, not generated-worker execution.

### Claude first application

Completed with exit 0 after user exit (920.36 seconds including trust/exit waiting). It created a Signal Flare worker and reviewer and a Mosigi worker, all Korean with `model: opus`. Independent validation passes with zero diagnostics; this known alias result does not prove generated-Agent access. Candidates and installed bytes match, UTF-8 without BOM, LF with final newline (64 worker, 35 reviewer and 61 Mosigi LF bytes). Only the three Agent additions changed the 1,221-file project snapshots. Both projects received a pre-draft summary. The final tool explanation correctly separates Bash process capability from behavioral no-delegation instructions and leaves runtime enforcement unverified.

**Retrieval improved for the previous Mac miss.** Claude used the finder across assignment and memory areas, retrieved the next Signal Flare inventory page, and cited the independent worker-specific handoff before the first candidate write. The installed worker permits the assigned isolated directory and purpose while excluding shared build/signing/product operations. This covers the previously missed conditional boundary without turning historical assignment into unconditional access.

**Cross-review still fails.** Between the Signal Flare candidate write and installation, the trace shows an edit to the assigned-document clause, a clipped `grep` of candidate restrictions, static/byte checks and installation. It does not show the required fresh source retrieval or concrete candidate/source comparison before installation. Mosigi likewise receives candidate adjustments and static checks without the complete source-comparison checkpoint. A final report labeling those edits as cross-review does not supply the missing evidence pass. The finder searches were mainly generic worker terms; operation-specific selection and interpretation still depend on the host.

**A coverage contradiction remains.** The broad Signal Flare worker covers test-only and document-only assignments but prescribes reproduction → minimal fix → green in its workflow and report. The 029 source assignment explicitly requires reproduction/design without product changes and permits accurately reported expected failures. The generated general assignment-precedence sentence leaves this specific workflow conflict unreconciled. The independent review therefore does not treat first-pass exception coverage as complete even though the Mac condition improved. No observer correction or known defect was supplied to the repeat session.

The host fixed a YAML description-colon error in the Mosigi candidate before installing it and disclosed it. Its LF/BOM/hash report agrees with independent inspection. Its `find -newer` claim is weaker than a complete preservation comparison, which is supplied by the harness. Automatic tool-result logs outside the evaluation root are host logs, not task-authored output violations. No task-authored outside-root write was found in the reviewed commands.

The finder also exposed a Windows output portability issue: non-ASCII JSON emitted under a legacy code page was garbled by the shell transport, and a Mosigi pipeline initially returned a binary-stream message before being reformulated. A focused CP949/Unicode-path test reproduces this as a tool issue, not a model defect. The frozen behavioral payload is retained; the output-only fix and separate validation are recorded below.

### Claude fresh repeat

Completed with exit 0 after user exit (282.59 seconds). APPLY and REPEAT prompts are byte-identical, and repeat input equals apply output. All 1,224 project-copy files retain bytes and nanosecond mtimes; no additions/deletions or new candidates/backups occurred. Independent validation and byte inspection reproduce all three initial Agent hashes and LF counts. The host preserves Korean prose and the existing model settings, accurately distinguishes behavioral rules from Bash capability, and leaves alias resolution and generated-Agent invocation unverified.

The repeat retained the Mac condition but did not identify or correct the 029 reproduction-only versus universal red-to-green conflict. Therefore no unnecessary rewriting was observed, while semantic completeness remains partial. An unchanged second opinion is not independent proof of correctness. The host disclosed a failed `--term "--check"` argument attempt and corrected it to `--term=--check`. Its assertion that mtimes were unchanged was based on making no writes rather than its own before/after measurement; the independent harness supplies that measurement. No task-authored outside-root write is observed.

## Final preservation and output portability fix

At host completion, both installed Skill copies matched the frozen source payload. Final observed originals retain all 687 Signal Flare and 534 Mosigi selected files' hashes/mtimes, HEAD and Git status. No Agent directory was installed into either original project. These observations cover the selected source files and Git state, not a universal monitor of the entire PC. Runtime data and excluded files were never evaluation targets.

After completing the frozen sessions, we changed only `find_evidence.py` JSON serialization to ASCII escapes, preserving Unicode values when parsed. This avoids legacy Windows stdout code-page corruption without changing search results. A CP949 stdout test with a Korean/emoji filename failed before the fix and passes after it. Searches on the frozen real-project copies also produce identical parsed JSON before/after: 251 files searched and 183 matched in Signal Flare, 192 searched and 167 matched in Mosigi, with no errors or additional pages. No model was rerun after this output-only change; the final Skill differs from the behavioral snapshot only in this helper's output serialization and explanatory comment.

Final checks on the development payload: Python 56 passed (39 validator, 8 byte inspector, 9 evidence finder), Node 27 passed, Skill structure and Skill Creator validation passed, and offline 15-file tarball installation/source comparison/unchanged reinstall passed. The package and installed payload include the fixed helper. No GitHub push, npm publish, generated-Agent invocation or product execution was performed in this round.

## Decision and user-facing limitation

| Check | Claude Code / Opus 5.5 | Codex / Astra |
|---|---|---|
| Prior isolated-Mac exception | Reflected before first draft and in installed worker | Preserved as an existing-owner condition in a narrower reviewer |
| First-pass complete exception coverage | Partial: reproduction/design-only workflow conflict remains | Assessed reviewer scope passes; executable-worker configuration not exercised |
| Candidate/source cross-review before installation | Failed: selected candidate snippets and checks replaced the fresh source comparison | Passed in the assessed reviewer scope |
| Same-input repeat | No edits, all 1,224 bytes/mtime entries preserved; remaining defect not discovered | No edits, all 1,223 bytes/mtime entries preserved |
| Original projects | Selected files and Git state preserved | Same original-project observation |

Retain this as a documented reliability limit of the tested Windows Claude Code 2.1.302 / `claude-opus-5-5` workflow. The evidence shows incomplete retrieval/review execution and a remaining policy-generalization conflict; it does not isolate an intrinsic model cause or establish that every Claude model fails. The README now explains the limitation, the need to compare generated restrictions with assignment/handoff evidence, and why a static pass or no-op repeat cannot certify completeness. Do not hide this round behind earlier alpha results or call it a full 1.0 readiness pass.
