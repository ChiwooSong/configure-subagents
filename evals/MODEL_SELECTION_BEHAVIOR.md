# Model-selection improvement evaluation

Evaluation started: 2026-11-01, completed on 2026-11-02 (Asia/Seoul). Included in the **alpha.8 prerelease**; publication and exact-commit CI receipts are linked from its [GitHub release](https://github.com/ChiwooSong/configure-subagents/releases/tag/v0.1.0-alpha.8). **1.0.0 remains on hold.**

## Method and boundaries

`evaluate_model_selection.py` copies the complete Skill and synthetic fixtures into a fresh directory under this repository's ignored `.eval-runs/`. It never runs as part of the installed Skill. There are eight proposal cases: routine extraction/check execution, research/writing/implementation/test/review responsibilities, routine versus high-risk review, unknown prices, cheaper-but-unverified eligibility, one eligible model, no established eligible models, and an older Opus version with a higher synthetic price.

Candidate eligibility is an explicit **simulated target declaration** in the evaluation request. Fixture prices, latency and qualified workloads are invented comparison inputs, not a real account allowlist, current API pricing or measured model performance. The main simulated target session is Fable; the actual evaluation-host model is recorded separately. Expected decisions and prior failures are not supplied to the host.

Each host gets two independent fresh proposal sessions, then an application and a fresh-session repeat on an existing-configuration fixture. Existing Agents use English, UTF-8 BOM/CRLF, comments and extra metadata. One model may be reconsidered; the other has a separate explicit user instruction fixing Opus. Independent checks compare file bytes and modification times, not only host exit codes or self-reported results. JSON report checks are mechanical; candidate/task reasoning requires trace and report review.

No generated Agent is invoked. No active development project or stored credentials/global settings are modified. Raw transcripts, local paths, fixture copies and account metadata remain ignored and are not distribution artifacts. Installation/validator/package success does not prove model access, measured savings, actual runtime routing or broad host reliability.

All completed behavioral sessions below used the same frozen Skill bytes. `SKILL.md` SHA-256: `12f1742b71c1dfc57f7b7eb877b1b56655ec708b67a9ec243cbed6d540df6453`. Complete ten-file Skill manifest SHA-256: `aefc6e1c9a21b1c773109955f81319b5eb9b75b1d2964fdcbde7da0aa3bcf040` (hash the UTF-8 JSON file-hash mapping with sorted keys and compact separators). Run directories retain exact prompt text alongside per-phase receipts containing requested and observable host models, file snapshots and failed attempts. The fixture inputs and prompt generator are in the evaluation script; neither contains an expected model assignment.

## Retained setup/blocked attempts

- Initial Claude proposal: inherited external API key failed before analysis. Its error trace used the placeholder `<synthetic>`; that is not an observed model. Subsequent account-login sessions omit external key/token/base URL only in the child process, without changing stored credentials.
- Initial Codex proposal and the next two proposals: offline remote file-tool calls prevented fixture inspection. The first child also inherited desktop integration/task identity. Omitting that bridge in the child exposed native execution, but a too-narrow evaluator prompt still disallowed local shell reading. The corrected evaluator permits read-only local inspection; these blocked attempts are retained, not counted as behavioral passes.
- Noninteractive Claude application: selected the appropriate model correction but required host approval for sensitive Agent edits. No approval surface existed, so it did not apply. Repeated denied write attempts are retained as a partial execution/reporting finding, not a successful no-op.
- First Codex application: selected the correction but could not preserve CRLF through its edit interface under an evaluator restriction on shell writes. It removed its candidates and left original bytes/mtimes unchanged. The evaluator now explicitly permits scoped file-copy/byte-edit/compare commands for apply/repeat while retaining workspace sandboxing and normal host approvals.

## Behavioral results

Proposal sessions completed on Claude Code 2.1.316 (observed `claude-opus-5-5`) and Codex CLI 0.166.0-alpha.5.1 (`gpt-6-astra` explicitly requested; actual returned model identity is not exposed by the captured Codex JSON events).

Both independent proposals per host covered all eight cases, kept project files unchanged, classified eligibility consistently and produced frontmatter matching reported choices. They used Haiku for bounded extraction/check execution, Sonnet for suitable ordinary research/writing/implementation/review, Opus for high-risk review, and the newer Opus in the higher-priced-old-version counterexample. Unknown price did not force inheritance; unverified cheaper models stayed outside assigned frontmatter; a single eligible Fable was retained and all-unverified choices fell back to inheritance. Agent grouping varied without requiring a fixed roster.

Codex application on a fresh corrected fixture changed only `ticket-extractor`'s model from `fable` to `haiku`. English prose, comments, custom metadata, tools, UTF-8 BOM, CRLF and final newline stayed byte-identical apart from that model value; `fixed-extractor`'s explicit `opus` assignment and modification time were unchanged. Originals and a complete candidate stayed within the evaluation root. The host ran candidate and installed static checks successfully with only the two expected pre-existing `integrationTag` warnings.

A new Codex session received the identical application request. Project files and all observed non-Git workspace files, including original copies and candidates, retained hashes and modification times; no extra backup files or write calls were observed. The host reported no change, reran static validation, and retained `haiku`/`opus`. Its short final JSON omitted the evaluator's full candidate-group/reason schema, so the mechanical structured-report check remains false for apply/repeat. The independent file checks and prose/command trace establish the bounded behavior; they do not establish compliance with that private report schema.

Claude's approved interactive application completed on a fresh corrected fixture. It changed only `ticket-extractor`'s model from `fable` to `haiku`; the separately fixed `opus` assignment retained its bytes and modification time. Independent comparisons confirmed the English instructions, tools, comments, extra metadata, UTF-8 BOM, CRLF and final newline were preserved apart from the one model value. Original copies and candidates stayed inside the evaluation root, and candidate/installed static checks passed with the same two expected warnings. Its final JSON also omitted the private evaluator schema; the prose, commands and file evidence support the bounded behavior, not a structured-report pass.

Claude's new session received the identical application request. Its opening snapshot exactly matched the prior application's closing snapshot, and its closing snapshot preserved all **25 observed non-Git workspace files**, including both installed Agents, Skill files, fixture evidence, original copies and candidates. Hashes and modification times were unchanged, no new files appeared, and the trace contained only inspection/static-validation calls (seven Read, one Grep, four Bash). It retained `haiku`/`opus`, accurately distinguished the prior correction from this session's no-op, and reported the two pre-existing metadata warnings. No generated Agent was called.

A trust-waiting interactive launch was replaced before model work when the evaluator's write scope was corrected; its cancelled record is retained separately. The user approved Claude's local prompts and selected Auto mode for the interactive sessions. The evaluator did not change stored/global permission settings. Interactive elapsed seconds include human approval and exit waits and must not be treated as inference latency or a performance benchmark.

| Check | Claude Code | Codex CLI |
|---|---|---|
| Two fresh proposals, eight cases each | Passed bounded reasoning/frontmatter checks; no project mutation | Passed bounded reasoning/frontmatter checks; no project mutation |
| Model-only correction in apply mode | `fable` to `haiku`; fixed `opus` and other bytes preserved | `fable` to `haiku`; fixed `opus` and other bytes preserved |
| Identical request in a new session | No observed content/mtime changes or new files | No observed content/mtime changes or new files |
| Actual evaluation-host identity | Observed `claude-opus-5-5` | Requested `gpt-6-astra`; returned identity unverified |
| Apply/repeat private JSON schema | Not passed | Not passed |

The original application/repeat prompt referred to the proposal schema without defining it in the new session. Both hosts supplied useful prose and incomplete JSON; Claude explicitly identified the missing schema. This is an evaluator limitation, not evidence of a model-selection failure or a structured-report pass. The evaluator now includes the schema in each application/repeat request for future runs. The mechanics tests still pass, including identical apply/repeat requests; **no host run of the corrected JSON request is claimed**. The installed Skill and fixture evidence were unchanged. File preservation and selection findings above come from the saved original requests, reports and independent snapshots.

Local regression checks currently pass: **63 Node tests**, **69 Python tests** (56 existing and 13 evaluation-mechanics tests), Skill structure/reference checks, skill-creator validation, and the 17-file offline package install/update/repeat smoke. These are not CI or authenticated host-behavior results.

## Reproduction

Use an existing Python 3.10+ environment with PyYAML. Preparation alone does not invoke a model:

```text
python evals/evaluate_model_selection.py --host codex --output .eval-runs/model-selection-example --phase propose-1
```

Add `--run` to opt in to a paid/authenticated session. Run phases `propose-1`, `propose-2`, `apply`, `repeat`; each launches a fresh session. `--host-model` pins the evaluation-host request; it is not target-model eligibility evidence. On Windows use the already configured backend through `--windows-sandbox elevated|unelevated`. Do not overwrite attempts or reuse a root after Skill changes.

For Claude account-login evaluation, `--claude-account-login` omits conflicting external authentication overrides only in the child; it refuses to override an active third-party provider mode. If sensitive edits require approval, use a fresh output and `--interactive` from a visible terminal, inspect approval prompts, and type `/exit` after the final report so snapshots can be collected. It copies only that generated session's automatic transcript into the QA directory. No bypass flag or global permission change is used.

Normal tests never invoke a host or registry. `tests/test_model_selection_eval.py` checks fixture preparation, evidence preservation, report parsing, candidate eligibility/frontmatter consistency, snapshot coverage and per-child environment isolation. These tests do not assess model reasoning. Existing installer/update tests cover verified published alpha.6/7 fingerprints and customized-Skill refusal as well.

The [R8 limitations](RETRIEVAL_AUDIT_BEHAVIOR.md) and [stable-release gates](../docs/V1_RELEASE_CHECKLIST.md) remain open. This targeted evaluation cannot close them.
