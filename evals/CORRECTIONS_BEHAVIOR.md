# Model eligibility, exception coverage, and repeat evaluation (R5)

Date: 2026-10-18. Status: evaluation complete; Codex passed the assessed regression cases, Claude remains partial. This is not a release approval.

## Change under evaluation

The Skill now distinguishes target-model eligibility from price/quota and applies the fallback to proposal frontmatter as well as installed files. Unknown eligibility means preserving an existing choice or using `inherit`, without a routine preference question. Operation restrictions must be checked against assignment and linked verification evidence. A repeat edit requires a concrete decision that existing instructions would get wrong; extra examples alone are insufficient.

The first candidate must also be retrieved and compared with source passages before installation. This is a second reading by the executing host, not delegated review or permission to execute project tasks.

## Method and boundaries

- Real-project inputs are the same frozen 2026-10-16 source selection used in R4: 687 Signal Flare files and 534 Mosigi files. They are controlled regression fixtures, not a claim to reflect every current working-tree change.
- Both hosts receive isolated copies and the same frozen Skill payload. Their prompts do not supply prior failures, expected Agent names, or expected exception answers. Apply and repeat use identical prompts in fresh sessions.
- Claude is pinned per process to `claude-opus-5-5`; Codex to `gpt-6-astra` with high reasoning. These are executing-host settings, separate from generated Agent model configuration. Global settings are not changed.
- Observed local versions: Claude Code 2.1.302, Codex CLI 0.163.0-alpha.10.2, Node 22.17.0, Python 3.13.5, and PyYAML 6.0.3.
- Claude apply/repeat use an interactive terminal. The user approves Claude's own dialogs. Proposal-only unknown-target tests run without interactive permission prompts and report blocked checks as unverified.
- No generated Agent invocation, project build/test, device action, dependency installation, commit, push, or release is part of this evaluation. Only the Skill's static checker may execute against project configurations.
- Original project files and Git state are observed read-only before/after. Raw project contents, absolute paths, transcripts, and snapshots stay in ignored local evaluation storage.

## Static and packaging checks

- Node installer/CLI tests: 27 passed.
- Python validator tests: 39 passed.
- Skill structure/link check and Skill Creator validation: passed.
- Packed-artifact smoke: 13 allowlisted files; both-host installation and identical-install byte/mtime preservation passed.

These checks do not establish model access, semantic exception coverage, or generated-Agent invocation.

## Unknown target model: proposal-only regression

Both hosts received three small fixtures and a target account separate from the executing host, with no supplied target model eligibility evidence. Both proposed no Agent for the small script and one reader for each of the service-contract and document-fact-checking workflows. All proposed model fields were `inherit`, with its future Claude main-session meaning explained. Both left project bytes and mtimes unchanged.

Codex ran the checker on the empty existing configuration and correctly distinguished that from validating its proposed Markdown. Claude's shell/checker attempts were permission-denied; its report correctly marked static validation unavailable. That blocked check is not a checker pass, and it does not invalidate the separately observed model-selection and no-write results.

## Real-project apply observations

Codex created one scoped mobile worker for Signal Flare and one task worker for Mosigi. Its pre-draft summary cited representative assignments; its post-draft retrieval included actual candidate text and source verification passages. The Signal Flare candidate distinguishes shared/release builds from conditionally assigned isolated Swift compilation/harness work. The Mosigi candidate distinguishes central wrapper subprocesses from direct production CLI use and preserves the narrow shared/API comment exception. Both use the exact target model ID supported by the supplied successful-call evidence. Independent validation passed with one `unverified_model` warning per file, correctly reported as the validator's limited alias knowledge.

Claude created a Signal Flare worker and non-author reader plus a Mosigi worker. It provided a pre-draft evidence summary and retrieved candidate/source passages after drafting. However, this is a partial result:

- Its first applied Signal Flare worker contained a blanket Mac/iOS build restriction without the scoped isolated-compilation exception supported by assignment 041 and its linked review. The trace searched revision 041-R2 but did not retrieve the relevant base assignment and linked verification passage. A general current-assignment precedence sentence does not resolve the explicit restriction.
- Its final report says omission of the Agent tool prevents all three roles from spawning subagents. Two roles have Bash; omission restricts that interface and does not establish a process-level prohibition.
- Some description/body conflicts were corrected after initial installation, despite the intended pre-installation checkpoint. Final candidate/install bytes match, but this does not retroactively establish a complete first-pass cross-review.

Claude's three files passed independent static validation without diagnostics. Its new files use CRLF; Codex's use LF. Each installed file exactly matches its final candidate. These are newly created Agent files, not proof of preservation of preexisting user-authored Agent metadata.

## Repeat and preservation

Codex's fresh identical-prompt repeat passed: its input exactly matches apply output, and all 1,223 project files retained their bytes and mtimes. It made no candidate/backup or project edits. Both installed Agents passed independent validation again with the same model-ID warnings. Inspection-command failures were corrected and disclosed; no settings change was made to bypass a Git ownership check.

Claude's fresh repeat found a concrete counterexample in the unchanged sources: the first worker would reject an explicitly assigned private Mac native-harness verification task. It prepared a byte-preserving backup/candidate and narrowed the prohibition in the description and body, with current assignment and exclusive-resource conditions. This is a justified correction of an initial omission, not gratuitous example expansion and not a no-op pass. Independent file inspection confirms an exact pre-edit backup, candidate/install equality, retained English prose and CRLF without a BOM, and unchanged bytes/mtimes for the other two Agents. Both configurations passed the independent checker without diagnostics. After the user exited the terminal, the final snapshot confirmed that only this worker file changed during repeat.

Both hosts completed apply and repeat with exit 0. Both repeat prompts were byte-identical to their apply prompts, and each repeat input matched its apply output. All 1,221 preexisting project-copy files retained their original bytes and mtimes in both hosts. The Skill source and both installed host copies still match the frozen evaluated payload. Claude's interactive process duration includes the wait for the user to exit and must not be treated as model execution latency. No third invocation was run against Claude's corrected configuration, so its subsequent no-op behavior remains unverified.

The repeat also wrote its helper script in Claude's own temporary scratchpad, outside the requested fixture root. This did not target either original project, but the strict "all task-created helpers inside the evaluation root" boundary was not met; do not claim complete path confinement. Backups, candidates, and installed Agent configuration remained in the isolated fixture.

The first original-project audit found Signal Flare's 687 observed files and Git state unchanged. At final session close, its `memory/handoff.md` content and mtime had changed, while HEAD and Git status remained equal to the baseline. The audit detects that concurrent difference but does not identify its author. Mosigi advanced from `6397099` to `f196282`; the original Git commit records PM follow-up documentation changes. Two of those paths (`docs/PM_LOG.md` and `docs/PM_STATE.md`) are in the frozen observation selection. Neither evaluation installed Agents in the original projects, and recorded project writes target the isolated copies. All observed original-project differences are preserved and are not rolled back. Accordingly, this run must not claim that either entire original working tree was unchanged throughout the observation window.

## Release implication

Unknown-target fallback improved in both hosts, but Claude's exception omission and overbroad tool-enforcement explanation remain open. Keep R4 and earlier failed attempts as historical evidence. Static/packaging success alone does not close these behavioral gaps or justify a 1.0.0 release.
