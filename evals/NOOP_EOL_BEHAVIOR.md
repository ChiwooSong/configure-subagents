# No-op and line-ending preservation follow-up

Evaluation date: 2026-10-15 (Asia/Seoul). Candidate: local changes on top of `0.1.0-alpha.4`; not a published version.

## Changes under evaluation

- Require a specific unmet requirement or concrete defect before editing. Optional examples, stylistic refinements, and narrower restatements of existing coverage are not defects.
- When coverage is adequate, validate in place and preserve bytes and modification times. Do not create candidates or backups merely to produce a change.
- Preserve encoding/BOM, CRLF/LF, and final-newline presence; use byte-identical backups and compare the installed bytes with the validated candidate. Do not normalize an already mixed file without a request.
- A previously missed concrete defect may still be corrected without new project evidence. The no-op rule does not prohibit necessary fixes.

## Method

Fresh isolated fixtures used the same initial/growth/repeat prompts and project data as the [alpha.4 evaluation](ALPHA4_BEHAVIOR.md). The prompts did not reveal the earlier failure or prescribe the no-op outcome. Each host received the revised Skill and references, then independently inspected the project. The Skill remained frozen throughout these runs.

The initial project contains an existing documentation reviewer with user metadata and comments. Growth introduces an API, an independently deployed worker, recurring event-compatibility review needs, and a user glossary instruction. Repeat uses the identical growth request with unchanged project evidence. External SHA-256 and nanosecond modification-time snapshots cover all project files. Original reviewer bytes are UTF-8 without BOM, 15 CRLF terminators, and a final CRLF at the growth boundary.

Claude Code uses the existing account login in a child process without the inherited invalid API key. Initial proposal runs noninteractively; mutation and repeat use interactive CLI permissions. One long candidate command was denied because its approval display was truncated, then retried after its full transcript was reviewed. This was operator assistance for permission inspection, not feedback on the intended configuration or pass criteria. Codex retains the configured Windows sandbox with workspace-write restrictions. No global credentials, permissions, or ACLs were changed.

## Results

| Check | Claude Code | Codex CLI |
|---|---|---|
| Sparse-project minimum configuration and no project writes | Passed | Passed |
| Necessary improvement after project growth | Passed: extended existing reviewer | Passed: extended existing reviewer |
| Existing body, metadata, comment, name, model and glossary instruction | Passed | Passed |
| CRLF, UTF-8 without BOM, final newline preserved | Passed: 24 CRLF, zero bare LF or CR | Passed: 22 CRLF, zero bare LF or CR |
| Unchanged-evidence repeat preserves bytes and modification times | Passed | Passed |
| Baseline/candidate/applied static validation | Passed; expected custom-field warning | Passed; expected custom-field warning |

## Limits and additional observations

Claude's original backup matched the external pre-application bytes, and its installed reviewer matched the validated candidate byte for byte. Both hosts changed only the existing reviewer inside the project; neither added an Agent during growth. Both repeat sessions inspected current substantive coverage, ran the validator in place, and completed with no project-file byte or modification-time changes. Their traces contain no repeat-stage candidate, backup, or Agent writes.

Skill structure/frontmatter and local-reference checks passed, as did `git diff --check` and UTF-8 decoding checks. The installer and validator implementation did not change; their full unit suites were not rerun for this instruction-only change.

The Codex backup directory is inaccessible to the independent observer under the sandbox-created ACL. Its execution trace checks original-copy equality and candidate/application hashes; the installed file and original project snapshots were independently verified. Independent backup-file verification remains unavailable; no ACL workaround was used.

Codex added Korean instructions to an originally English Agent, although the prompt requested Korean responses and did not explicitly request changing the Agent language. This does not invalidate the no-op or byte-format checks, but is a separate language-convention consistency issue to evaluate before broader multilingual claims.

This run covers one CRLF lifecycle fixture per host on Windows. LF-only files, pre-existing mixed endings, BOM-bearing files, no-final-newline files, concurrent editing, model-selection quality, and generated-Agent runtime invocation are not established by these results. The explicit `inherit` constraint tests preservation, not automatic model optimization. Earlier alpha.4 failures remain recorded rather than replaced by the follow-up results.
