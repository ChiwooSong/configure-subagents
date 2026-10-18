# Alpha.6 update-command evaluation

Date: 2026-10-19 (Asia/Seoul). Scope: local Node CLI, filesystem preservation and package distribution. No authenticated Claude/Codex model sessions or generated-Agent calls were run. Original development projects were not used or edited.

## Contract

`update --agent claude|codex|all` (or the compatible `--host` selector) updates only complete installed Skill trees matching bundled fingerprints of a recognized previous release. Current payloads are no-ops. Missing, customized, incomplete and unknown trees stop all selected hosts before mutation. The package does not trust an editable version marker or download a prior package while updating.

Published unscoped alpha.1 and scoped alpha.2/4/5 were downloaded as data from the public npm registry. The capture tool verified each SHA-512 tarball integrity before reading Skill files without extracting/running package code. Exact bytes are recorded in `tests/fixtures/released-skills.json`; corresponding SHA-256 fingerprints and registry integrity values ship in `lib/released-skills.json`. Alpha.1 and alpha.2 have indistinguishable Skill payloads, so the CLI reports both matching versions rather than guessing the installation's origin. A maintainer must explicitly review new captures; normal CI is offline for these fixtures.

## Observed local checks

- Node: **59 passed** (27 existing installer/CLI tests, 32 update tests).
- Python: **56 passed** in the existing project virtual environment. The first attempt with system Python could not load PyYAML; rerunning with the existing dependency-equipped environment passed without global installation.
- Skill structure/reference checks and skill-creator validation: passed.
- Actual offline npm tarball: **17 allowlisted files**; fresh both-host installation; alpha.5-to-alpha.6 both-host update; full payload byte comparisons; repeated install/update preserve file bytes and modification times; existing Agent bytes/mtime unchanged.
- Published alpha.1/2/4/5 fixtures upgrade with exact original backups. A mixed-version pair also upgrades.
- User edits, added/deleted files, extra directories, line-ending edits and spoofed version markers stop before changing either host. Customized current and unknown payloads are also refused.
- Staging failure and second-host replacement failure preserve/restore originals. Concurrent original edits, identical-byte inode replacement, concurrent changes to installed content/backups, and recovery permission failures retain the affected data and report recovery paths.
- Unicode/space paths, selectors, help/error exit codes, missing selected installations, symbolic links/junctions and repeat no-op behavior are covered.

The exact release commit's six CI results and public-registry smoke receipt are attached/linked from the [alpha.6 GitHub release](https://github.com/ChiwooSong/configure-subagents/releases/tag/v0.1.0-alpha.6). Local results alone do not imply those external checks succeeded.

## Recovery and limits

Staging and original backups live under `.configure-subagents-updates/<transaction>/`, outside Skill discovery. Replacements use same-filesystem directory moves. Handled failures conditionally restore originals; changed destinations/backups are preserved and reported. The command never recursively deletes a tree. Backups/staging are retained for inspection and later deliberate cleanup.

Two-host replacement is not crash-atomic. Process termination or power loss may leave an original in its backup with a missing live directory; no automatic crash recovery is claimed. Path checks do not provide OS isolation against a hostile writer racing directory changes. Customized Skills require manual merging; the command does not partially upgrade around them.

Agent design rules are unchanged; only an explicit package-update explanation was added to the host-usage reference. The [R8 host limitations](RETRIEVAL_AUDIT_BEHAVIOR.md) remain. Passing installer tests does not prove Skill discovery, model selection, first-pass semantic completeness or runtime Agent behavior. **1.0.0 remains on hold.**
