# Alpha.4 lifecycle behavior evaluation

Evaluation date: 2026-10-15 (Asia/Seoul).
Skill source: `508f6410b06c9499c64317ea617a889c5f4ba1fc`, published as `0.1.0-alpha.4`.
The Skill payload was not edited during evaluation. Evaluation tooling was improved separately.

## Scope and method

The same synthetic project starts with an undecided local-tool purpose and one documentation reviewer. The next stage adds an API, an independently deployed worker, a shared event contract, a declared test workflow, evidence of recurring compatibility-review omissions, and a new user instruction about glossary terminology. A third invocation repeats the same improvement request without changing project evidence.

Both hosts were told to preserve the reviewer's name, metadata, comment, severity labels, and explicit `model: inherit` choice. This deliberately tests preservation, not autonomous model optimization. Generated agents and project tests were not invoked. Each host used its installed copy of the actual Skill and its references.

External snapshots record project-file SHA-256 and modification times. Host traces and resulting files were reviewed independently; process exit code 0 alone is not a pass. Raw paths, account details, transcripts, and snapshots stay in ignored `.eval-runs/` directories.

## Results

| Check | Claude Code | Codex CLI |
|---|---|---|
| Read actual Skill references and project files | Passed | Passed |
| Sparse-project proposal avoids unnecessary new roles | Passed: retain the existing reviewer | Passed: retain the existing reviewer |
| Initial proposal preserves all project bytes and modification times | Passed | Passed |
| Reassess after project growth | Passed: extend existing reviewer for cross-service compatibility | Passed: extend existing reviewer for cross-service compatibility |
| Preserve existing body, custom glossary instruction, name, model, comment, and metadata | Passed | Passed |
| Limit project changes to the existing reviewer file | Passed | Passed |
| Static checks of baseline, candidate, and installed configuration | Passed after scoped approvals | Passed |
| Identical-state repeat invocation leaves files unchanged | Passed: all project bytes and modification times unchanged | **Failed in this run**: appended more review criteria |

All successful static checks reported the expected warning for the preserved custom `integrationTag`; they did not establish runtime compatibility of that extension.

## Findings

### Repeat-invocation stability needs improvement

Claude reread the current project and reviewer, ran the static validator, and concluded the existing compatibility-review instructions were sufficient. It created no new Agent, candidate, or backup. Independent before/after snapshots confirmed that all project bytes and modification times stayed identical.

Codex recognized that the existing reviewer already covered shared-event compatibility, but appended a further section about missing versus null fields, old/new producer-consumer combinations, and API/integration-test gaps. Those details were derived from the same unchanged files and largely elaborated coverage already present. The existing content remained intact, but both bytes and modification time changed. The strict unchanged-rerun acceptance criterion therefore failed; the added detail should not be counted as proof of necessary improvement.

Before 1.0, strengthen the distinction between a demonstrable role/configuration defect and optional elaboration. A completed configuration should remain unchanged when the request, evidence, constraints, and substantive coverage are already adequate. Retest against the same frozen fixtures after any Skill change; do not retroactively mark this alpha.4 run as passed.

### Preservation and recovery-copy limits

Claude's successful interactive application preserved CRLF formatting and the original body verbatim. Its fresh original copy matched the independent pre-application hash. Its earlier noninteractive attempt could not make a byte-identical backup or apply the sensitive Agent file because approval requests were denied; that attempt was recorded as incomplete, not passed.

Codex preserved the original body bytes but appended LF text to the existing CRLF file, producing mixed line endings. Its trace includes original-hash checks, candidate validation, and pre-write rereading. The sandbox-created `evaluation-records` directory was not readable by the independent observer account, so independent byte verification of those backup files remains unavailable. The installed reviewer and all pre-existing project files were readable and independently checked. No ACLs were changed to work around this limitation.

## Execution conditions

- Claude Code `2.1.300`; the session identified `claude-opus-5-5`. An inherited invalid API key initially caused HTTP 401. A child-process-only environment change omitted that key and used the existing Claude login. No stored credential or global environment setting was changed.
- Claude's noninteractive runner denies permission requests, including sensitive Agent-file edits. Application was subsequently evaluated in the interactive CLI, reviewing and approving individual fixture reads, backup/candidate operations, validation, and the one Agent-file application. No bypass or automatic-approval mode was enabled. Workspace trust was accepted only for the generated evaluation project.
- Codex CLI `0.162.0-alpha.17.2`. Ignoring user configuration also omitted the PC's configured Windows sandbox backend and blocked reads. Supplying the existing `windows.sandbox="elevated"` setting restored execution while retaining `workspace-write`; global settings and approval rules were not changed.
- Remote Desktop Commander was initially offline, then connected. Its file access and an independent read-only validator invocation on the PC succeeded. It is a file/terminal transport, not evidence of a separate host-model run.

## Reproduction and remaining coverage

Use `evaluate_lifecycle.py` and the instructions in [EVALUATION.md](EVALUATION.md). Use a fresh output directory for new attempts and review each phase before advancing. The Windows path-separator mismatch in the early growth check was an evaluator bug: the actual changed path was only `lifecycle/.claude/agents/reviewer.md`. The runner now normalizes separators and refuses incomplete filesystem snapshots instead of silently skipping unreadable directories.

This is one Windows lifecycle fixture per host, not certification across all project types, operating systems, languages, or models. General model-selection quality, actual generated-agent discovery/invocation, concurrent-edit recovery, and the wider representative-project matrix remain separate evaluations. The failures and limits above prevent treating this run as completion of all 1.0 readiness criteria.
