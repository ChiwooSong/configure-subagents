# Release readiness: 2026-10-18

Assessment date: 2026-10-18 (Asia/Seoul). No package was published, tag changed, or source pushed during this assessment.

Follow-up: subsequent Skill corrections and their independently assessed host results are recorded in [R5 corrections evaluation](CORRECTIONS_BEHAVIOR.md) and [R6 first-analysis and repeat evaluation](FIRST_REVIEW_BEHAVIOR.md). R6 confirms same-state project-file preservation in both hosts, but Claude's first-analysis completeness, reporting accuracy and output-boundary failures remain open. The results below remain the historical baseline, not tests of those later edits.

Later [R7 evidence and byte-inspection evaluation](EVIDENCE_REVIEW_BEHAVIOR.md) confirms accurate newline reporting and no observed outside-root task output in both hosts. Codex preserves its configuration on repeat; Claude corrects a first-pass exception defect and preserves the corrected configuration in an additional fresh session. Claude's first-pass retrieval and cross-review remain incomplete, so R7 is still a partial behavioral gate.

## Published version versus development

The public npm registry was queried directly and the published alpha.4 tarball was downloaded with lifecycle scripts disabled.

| Surface | Observed state |
|---|---|
| npm `next` | `0.1.0-alpha.4` |
| npm `latest` | `0.1.0-alpha.2`; an alpha, not a stable release |
| Most recent public GitHub release | `v0.1.0-alpha.4`, prerelease |
| GitHub `main` and local HEAD | `b64b2e020d5c67c4398b337cbcb3b5d564b406c1` |
| Local package metadata | `0.1.0-alpha.5`, not published to npm |
| Additional local changes | Four Skill instruction files and evaluation reports beyond that commit |

Compared with the actual npm alpha.4 tarball, six distributable files differ: `package.json`, `README.md`, `configure-subagents/SKILL.md`, and the `claude-code.md`, `project-analysis.md`, and `role-and-model-selection.md` references. These are content differences, not just line endings. The CLI, installer, Python validator, dependency declaration, host-usage reference, and licenses are byte-identical.

The development changes cover existing Agent language and byte-format preservation, avoiding unnecessary rewrites, assignment and exception coverage, visible pre-draft evidence, candidate-to-source review, precise tool restrictions, model-choice explanations, and accurate reports of failed or denied operations.

The frozen Skill manifest SHA-256 is `d07ab9c313c6547c0f204b212c04a20505ec7e38e5f0f80f8c28e57fbad5c3c6`.

## Checks executed in this assessment

Windows; Node.js 22.17.0; Python 3.13.5; PyYAML 6.0.3.

| Check | Result |
|---|---|
| Installer and CLI suite | 27/27 passed |
| Python validator suite | 39/39 passed |
| Repository Skill metadata, references and boundaries | Passed |
| Skill Creator structural validation | Passed with `python -X utf8`; its initial default-codepage execution failed decoding UTF-8 on Windows |
| Offline npm tarball | Exact 13-file allowlist; both-host installation; repeat preserves bytes and mtimes |
| Working diff whitespace | Passed |
| Frozen installed Skill payloads | Match the development source |

The installer suite includes conflict refusal, both-destination preflight, partial-failure rollback, concurrent-file preservation, linked paths, Unicode/space paths, and the `--agent` / `--host` interfaces. The validator suite includes duplicate keys, malformed configuration, unknown fields, capability warnings, missing dependencies, untrusted diagnostic content, and read-only behavior.

The six OS/Python jobs for commit `b64b2e0` are green: Windows, Ubuntu, and macOS Intel with Python 3.10 and 3.13. [CI run](https://github.com/ChiwooSong/configure-subagents/actions/runs/38756351438). That run does **not** include the four additional local Skill edits; the final release commit still needs its own CI result.

## Fresh host evaluations

All sessions used isolated synthetic fixtures. The original active projects were not used as execution directories. No generated Agent was invoked, and no product tests, builds, devices, deployment services, dependency installation, or global settings changes were requested. Raw logs and snapshots remain in ignored local evaluation storage.

Hosts: Claude Code 2.1.301 and Codex CLI 0.163.0-alpha.10.2. Claude's successful initial session reported `claude-opus-5-5`, while growth and the separate proposal suite reported `claude-fable-5-1`. No model override was supplied by these harness runs; the observed default drift is retained and must not be presented as a controlled same-model comparison. Codex's exact runtime model was not established by the captured JSON trace. The lifecycle fixture explicitly preserves `model: inherit`; it measures preservation, not role-based model optimization.

| Scenario | Codex | Claude Code |
|---|---|---|
| Sparse project: minimal proposal and no writes | Passed | Passed after account-login retry |
| Growth: extend existing reviewer using API/worker evidence | Passed; only the existing Agent changed | Blocked by Agent-file edit permissions; 240-second timeout |
| Preserve custom comment, metadata, reporting labels and user note | Passed during application | Original retained; application preservation not established |
| English Agent, Korean response, CRLF preservation | Passed during application | Original retained; application preservation not established |
| Same-state repeat: bytes and mtimes unchanged | Passed | Not run because growth did not complete |
| Small script, services and documentation proposal suite | Passed; no writes | Partial: no writes and project-specific roles, but unavailable-model fallback criterion not met |

Codex's lifecycle trace contains a visible evidence summary before candidate creation, candidate reading and static checking, and a no-change repeat. The applied Agent remains English, UTF-8 without BOM, with 20 CRLF line endings and no bare LF. It retains the original reporting contract and adds shared-event producer/consumer and compatibility review. Independent validation passes with the expected `integrationTag` unknown-field warning.

For the separate three-project proposal suite, Codex proposed no additional Agent for the small script, a contract reviewer for services, and a source checker for documentation. It did not change project files. Its attempted static checks used a Python environment without PyYAML and were reported as unavailable. An independent check with the provided development virtual environment passes the three empty Agent trees; this is not host-executed validation or proof that proposed Agents exist.

Claude's three-project proposal session completed without writes. It proposed no Agent for the small script, a contract reviewer and test runner for services, and a fact checker for documentation. It correctly described the shell-enabled test runner as not read-only and disclosed denied static-check attempts. However, its ready-to-use frontmatter selected `sonnet` and `haiku` while explicitly stating that target account availability was unknown. Listing aliases recognized by the validator does not establish availability; offering `inherit` only if those models later prove inaccessible does not satisfy the agreed missing-information fallback. This is a model-selection instruction-following finding, not evidence that those models are actually inaccessible. No model was invoked through the proposed Agents.

Claude's first lifecycle attempt inherited an invalid external API key and failed with HTTP 401. The failed attempt is retained. A separate child process omitted that environment override and successfully used the existing account login; no stored credentials were edited. The sparse-project proposal completed without writes and reported its denied byte-inspection attempt. During growth, Claude prepared a candidate but installation edits were denied by the noninteractive permission policy. The run reached the 240-second harness limit with no project changes. An unchanged original after a blocked application is **not** a successful no-op result. Further application/repeat evaluation needs a supervised interactive permission surface, not a bypass flag.

## Known real-project failures remain open

The source payload in [the 2026-10-16 cross-review evaluation](CROSS_REVIEW_BEHAVIOR.md) is byte-identical to the Skill evaluated here. Those observations therefore remain relevant, rather than being superseded by a newer implementation:

- Claude's first installation did not demonstrate the required actual-candidate/source second pass and did not establish discovery of the scoped native-verification exception.
- Claude's same-state mobile-project repeat changed its description without demonstrating a necessary correction; the no-op criterion was not met.
- Codex's narrower reading roles passed preservation in those runs, but do not establish general implementation-worker permission coverage.

The active-project evaluation was not rerun in this assessment. The small lifecycle fixture cannot close those more demanding failures.

## Gates for the next prerelease

1. Finish supervised Claude application and repeat checks on this exact Skill payload, with a recorded, stable per-session host model. Review the actual diff, original/candidate identity, language, encoding, line endings, and byte/mtime preservation; do not use a blocked no-change result as a pass.
2. Resolve the first-pass exception, unnecessary-repeat-edit, and unavailable-model fallback findings, then repeat the relevant synthetic and two-host isolated real-project evaluations. If a prerelease intentionally retains a limitation, state it explicitly in the README and release notes and do not claim the affected behavior passes.
3. Align the README's pinned version, update instructions and validation claims with the final candidate. Alpha.5 is currently an unpublished candidate; changing the `latest` tag requires an explicit release-channel decision.
4. Commit the reviewed candidate and pass all six CI jobs on that exact commit. If the payload changes, rerun the relevant local and host checks and verify the final tarball again.
5. Publish the verified tarball to `next`, create a matching GitHub prerelease, query registry version/tag/ownership/metadata, and test a clean installation of the actual published package. Authentication and npm 2FA may be required at that stage.

The local automated gate is green. Full behavioral readiness and exact-candidate CI are not yet green. This assessment does not authorize a claim of all-pass release readiness.

## Remaining steps for 1.0.0

1. Close the first-pass coverage, same-state rewrite, and unavailable-model fallback findings. Validate a release candidate in both hosts on the simple lifecycle fixture and both isolated real-project cases, retaining failed attempts and comparing independent file snapshots. Fix the host model per controlled run and disclose any additional model coverage separately.
2. Complete the supported behavioral matrix: proposal, apply, validation-only and repeat; sparse and developed projects; scripts, services and documentation; existing customized Agents; language/format preservation; unknown model/tool information; known model constraints; and permission/error reporting. The preservation fixture's explicit `inherit` is not evidence that autonomous model selection is optimal. Test conflict/conditional recovery behavior separately from installer rollback.
3. Freeze the supported interface: CLI options and installation paths, validator JSON schema and exit codes, compatibility policy, and a tested update procedure preserving customized Skill content. Automatic force-upgrade is not required; a reproducible reviewed manual update can satisfy the contract.
4. Run the complete supported CI matrix and an installed-package RC regression on the final artifact. Keep runtime invocation, model access/cost claims, and language/platform coverage limited to observed evidence. Generated-Agent invocation remains a separately scoped test, not an implied result of Skill execution.
5. Once those gates are green, publish `1.0.0` with `latest`, create a non-prerelease GitHub release, update installation/migration documentation, and verify registry metadata and the installed public artifact. Calendar time or a version-number bump alone does not satisfy these gates.


## R8 follow-up

The [R8 retrieval audit](RETRIEVAL_AUDIT_BEHAVIOR.md) improves Claude's first-pass isolated-Mac exception coverage and records byte/mtime-preserving repeats in both hosts. Claude still skips the complete candidate/source review and retains a reproduction-only workflow conflict; the no-op repeat does not resolve it. README disclosure now scopes this reliability limitation to the tested host/model/environment. The output-only evidence-finder encoding fix passes separate regression and real-snapshot JSON-parity checks; full host sessions used the retained pre-fix snapshot. This follow-up is not an all-pass stable-release gate and does not publish a release.
