# Active-project behavior follow-up

Evaluated on 2026-10-16 (Asia/Seoul), using local Skill changes on top of `0.1.0-alpha.5`. This report does not represent a new published package version.

The subsequent [exception and reporting evaluation](EXCEPTIONS_BEHAVIOR.md) records further Skill changes and fresh apply/repeat sessions. The failures below remain part of the record.

## Method

The user authorized evaluation against two active projects: a mobile application with native transport boundaries and a web application with server, shared-contract and UI work. Each host received isolated snapshots of 687 and 534 source/documentation files, including selected uncommitted work. Credentials, local settings, dependencies, build outputs and operational data were excluded. Original project files were never evaluation write targets.

Fresh Claude Code and Codex sessions received the Skill, project evidence and scoped proposal/apply requests. They were not given previous findings or a desired role/model roster. The prompt explicitly bounded side effects and requested autonomous model decisions and Korean reports; these results are not a minimal-prompt benchmark. No project code, tests, builds, devices, services or generated Agents were executed. Independent observers recorded hashes and modification times, checked installed bytes against candidates and ran the static validator. Codex-created files were observed through a separate Python process in the existing read-only sandbox profile, without changing ACLs.

Actual hosts were Claude Code 2.1.301 and Codex CLI 0.162.0-alpha.17.2 on Windows. The provided target-model evidence was a same-day observation of the Claude Code 2.1.300 account model picker, not successful model invocation or quota/price evidence. Each evaluation round used a frozen installed Skill payload. The second round reused the identical source cache in new workspaces. Original PM documents and Git state changed concurrently during the evaluation; those changes were observed and left untouched. Claims about snapshot preservation must not be read as a claim that the independently active original repositories stayed unchanged.

Claude's interactive apply run used individual approvals for scoped commands. One search command was rejected because its backtick quoting could allow shell substitution; the session was resumed with a quoting/read-only reminder, without supplying coverage findings or a desired configuration. This assisted execution is not an unattended-run result. No persistent permission allowance or global setting was changed.

## First revision: failures retained

The first revision added representative-assignment cross-checking, precise tool-boundary explanations and separation of historical quota incidents from current model availability.

- Both proposal sessions preserved project bytes and modification times.
- Codex applied three justified roles, preserved all existing snapshot files and retained every byte and modification time on repeat. Its assignments covered server/UI verification and task-specific ownership exceptions; reports separated task-fit choices from actual model access, quota and costs.
- Claude's proposal covered server/UI work and explained shell capabilities, but still used `Read-only` in a shell-enabled reviewer's description. A caveat elsewhere did not make that label consistent.
- Claude's apply session created a general worker whose server-directory prohibition and app-only verification reflected a UI assignment. That contradicted actual server-worker assignments. Static validation passed, demonstrating that schema validity is not evidence of substantive coverage. The apply result preserved unrelated files and matched its validated candidate, but failed coverage review. A repeat of this already-failing revision was not used to turn it into a pass.
- Claude proposal checker attempts were permission-blocked. It correctly reported unverified validation, but its statement that it did not retry conflicted with the tool trace. This reporting limitation is preserved rather than treating its completion text as authoritative.

## Final revision

The entrypoint now requires a compact role/assignment/ownership/verification summary before drafting, resolution of blanket prohibitions that conflict with sampled assignments, and agreement between Agent descriptions, bodies and report claims about tools. A role derived only from UI work must be narrowed or checked against the other responsibilities it claims to cover. This is a configuration-analysis requirement, not permission to resume project tasks.

Codex's final-revision apply session created one source-reading `change-reviewer` per project (`opus`, `Read, Glob, Grep`). It summarized representative assignments and component checks before drafting. The web-project reviewer distinguishes server/UI/shared ownership and authorized exceptions, and covers both app and functions verification evidence. The mobile reviewer covers native, application, storage/account and available cloud boundaries. Reports explain task-fit model choices without asserting current quota, price or invocation success.

Independent checks found only those two new Agent files: all 1,221 pre-existing snapshot files were preserved. Installed files matched the candidates, and both static checks passed with zero diagnostics. A fresh repeat session made no file changes; hashes and modification times, including the generated Agents, were unchanged. The mobile Agent remained English and the web Agent Korean. Both new files used LF without a BOM. Codex proposal mode was evaluated in the first revision; the final revision specifically reran apply and repeat.

Claude's final-revision proposal preserved all snapshot files, covered server/UI verification and ownership exceptions, and used only reading tools for its proposed read-only reviewer. Its permission-blocked checker was correctly marked unverified, but the same inaccurate claim about not retrying remained.

Claude's apply session created one `worktree-worker` per project (`opus`, reading/editing tools and `Bash`). The mobile instructions cover app, native, rules/server and documentation work; the web instructions cover app/functions/shared/scripts, scoped ownership exceptions and component checks. Both the final report and tool configuration distinguish shell capabilities from behavioral prohibitions and separate historical quota data from current model evidence. Independent checks found only two added Agent files, preservation of all 1,221 existing snapshot files, byte-identical candidates and installed files, and zero static diagnostics. The mobile Agent is English and the web Agent Korean, both LF without a BOM.

Two Claude process/reporting issues remain: coverage was summarized in the final report rather than before drafting as required, and the claim that only `Grep/Read` were used after the interrupted search conflicts with subsequent shell calls for reading, installation and validation. The command trace and independent observations take precedence. The substantive coverage improvement does not make these procedure/reporting checks pass.

Claude's same-state repeat was **not a no-op**. It found two further contradictions in its first-pass output: a blanket Mac SSH prohibition omitted an assigned private Swift harness described in handoff evidence, and the web worker's blanket Firebase CLI prohibition conflicted with an explicitly allowed emulator wrapper that internally invokes that CLI. The repeat changed three mobile-Agent lines and one web-Agent line to make the exceptions conditional and narrow. No remote command or emulator was executed. The private-harness evidence was historical handoff/review material; the underlying worker report was absent, and future use still depends on an explicit assignment and resource ownership.

Independent comparison confirmed byte-identical pre-edit backups and installed candidates, unchanged frontmatter, language and LF/BOM/final-newline conventions, zero static diagnostics, and preservation of all unrelated snapshot files. These were evidence-backed corrections, not cosmetic rewriting, but they demonstrate that first-pass coverage was still incomplete. The mobile description still broadly excludes Mac builds while the body permits an assigned private Swift harness, leaving a wording ambiguity to review. There was no third invocation to claim convergence. An intermediate claim that the edit tool had converted LF to CRLF was corrected by the host after detecting a quoting error in its own check; final LF preservation was independently measured.

| Final-revision criterion | Codex | Claude Code |
|---|---|---|
| Previously observed server/UI coverage and tool/model explanation | Improved in apply and repeat | Improved, with further exceptions missed on first apply |
| Unrelated snapshot files preserved | Pass | Pass |
| Independent static validation | Pass | Pass |
| Same-state repeat | No changes, including modification times | Two Agent files corrected; no-op/convergence not established |
| Language and byte-format preservation | Pass | Pass |
| Pre-draft evidence summary and report accuracy | Observed in apply | Residual failures; not a complete pass |

Local regression checks passed: 27 Node installer tests, 39 Python validator tests, the repository Skill structure check and the skill-creator validator. The final Skill also passed the offline npm tarball check: 13 allowlisted files, installation for both hosts, and identical-content reinstall without modification. These checks are separate from model behavior results.

## Limits

No pre-existing project Agents were present in the source snapshots. Repeat checks evaluate preservation of generated configuration, not the full existing-user-Agent matrix. The earlier [language and CRLF fixture evaluation](ALPHA5_BEHAVIOR.md) remains separate. Role rosters and model choices can vary across independent sessions; these observations do not establish optimal cost, runtime model access, generated-Agent quality, all languages, all platforms or a universal success rate.

Raw project material, local paths, account observations and session logs remain in ignored local evaluation storage. Only this sanitized report belongs in the source repository.
