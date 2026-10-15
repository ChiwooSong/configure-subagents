# Alpha.5 behavior evaluation

Evaluation started 2026-10-15 (Asia/Seoul). Candidate version: `0.1.0-alpha.5`.

## Change and method

Alpha.5 distinguishes the user's response language from the Agent-file language. A Korean response request must not translate an existing English Agent's description or newly inserted instructions. An explicit request to change the Agent language still takes priority. The release also includes the concrete-defect/no-op and byte-format preservation instructions evaluated in [the preceding follow-up](NOOP_EOL_BEHAVIOR.md).

Fresh isolated projects used the same `evaluate_lifecycle.py` initial, growth and repeat prompts and fixtures as the prior evaluations. The prompt requests Korean responses but does not tell the model which language to use inside the Agent: that decision comes from the Skill and the existing English file. No expected outcome or prior failure was supplied to either host. The Skill payload is frozen across all phases and its hashes are recorded locally.

Claude Code 2.1.300 uses its existing account login, with individual permission approvals for interactive mutation/repeat sessions. Codex CLI uses workspace-write with the PC's configured Windows sandbox backend. No generated Agent, project code, or test suite inside a fixture is invoked. External snapshots record project file bytes and modification times; host completion statements are checked against tool traces and resulting files.

## Results

| Check | Claude Code | Codex CLI |
|---|---|---|
| Sparse-project proposal, no speculative roles or writes | Passed | Passed |
| Growth creates necessary coverage using the existing reviewer | Passed | Passed |
| New description and instructions remain English | Passed | Passed |
| Final explanation is Korean | Passed | Passed |
| Existing instructions, metadata, comment and explicit model preserved | Passed | Passed |
| CRLF, UTF-8 without BOM and final newline preserved | Passed | Passed |
| Same-state repeat preserves project bytes and modification times | Passed | Passed |
| Static validation of candidate, installed result and repeat | Passed, expected custom-field warning | Passed, expected custom-field warning |

Independent checks confirmed 25 CRLF line endings in the Claude result and 19 in the Codex result, with no bare LF/CR. Both initial and repeat project snapshots matched in bytes and modification times; growth changed only the existing reviewer. Skill source hashes remained unchanged across all phases.

Local checks passed: 27 installer tests, 39 Python tests, Skill structure validation, and the 13-file npm tarball install/repeat check. CI results are recorded separately in the release.

## Interpretation and limits

The fixture deliberately preserves `model: inherit`; it tests preservation, not automatic model-selection quality. This is one Windows lifecycle scenario per host. It does not establish all project types, languages, operating systems, explicit Agent-translation requests, intentionally multilingual files, LF/BOM/mixed-ending variants, concurrency recovery, or generated-Agent runtime behavior.

The sandbox-created Codex backup directory denied independent read access. The Claude backup was independently confirmed byte-identical, and its installed file matched its validated candidate. Tool-side hash/equality checks and independently readable project snapshots are distinguished from an independent backup read. No ACL workaround is used. Raw host logs, local paths, helper files and account-specific evidence remain ignored under `.eval-runs/`; only this sanitized report and reusable evaluation tooling are public.
