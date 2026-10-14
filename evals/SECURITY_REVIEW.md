# Security review follow-up — 2026-10-15

This records the local security follow-up before publication. The user subsequently authorized resuming release after npm identity and package ownership checks. GitHub must remain private until the first npm publication secures the package name; current release status is recorded separately.

| Finding | Local action |
|---|---|
| Unclaimed registry name referenced in execution instructions | Removed registry execution instructions from the distributed Skill. Manual installation from reviewed source is the only documented installation path until registry owner, package ownership, and exact published version/tag are verified. No scoped identity has been assumed. |
| Execution-capable settings passed without warnings | Added warning diagnostics for the presence of hooks and MCP servers, plus distinct permission-mode warnings for bypassPermissions, acceptEdits, and auto. Kept dontAsk out of this category and retained existing exit-code semantics. |
| Missing installer and packaging checks | Added filesystem behavior/fault tests, a portable Skill structure check, and an offline tarball installation test. The missing files were unfinished work at the earlier pause, not copied-away tests. |
| Trust rule only in a reference | Added a trust-boundary section directly to SKILL.md, covering agent bodies/frontmatter, attacker-controlled field names, and validator output. Preserving fields does not endorse executing them. |
| Ignore patterns missing | Added environment files, logs, private-key extensions, and local Claude settings to .gitignore. Ignore rules do not substitute for reviewing publication contents. |
| Installer check/use race | No security-boundary guarantee added. Linked-path checks and preservation tests remain useful, but this installer cannot provide OS-level isolation against a concurrent hostile writer. |

The diagnostic JSON deliberately retains unknown field names so the caller can locate a problem. These strings remain untrusted evidence. Escaping them into JSON is not an instruction-trust boundary, and the new instructions do not claim to eliminate prompt injection.

Capability warnings are schema-compatible: a valid file can still return `passed` with warnings. Reviewers must read diagnostics. Empty hooks/server fields also produce review warnings; malformed field types still produce errors.

## Verified locally

On Windows, Node.js 22.17.0, Python 3.13, and PyYAML 6.0.3:

- `npm test`: 23/23 installer tests passed, no skips. Includes both-host failure rollback, preservation of modified/replaced/partial files, unchanged repeated installs, path conflicts, Unicode paths, and actual junction tests.
- Python unittest suite: 39/39 passed, no skips. Includes the three execution-capability warnings, restricted permission-mode exclusions, malformed capability fields, and attacker-controlled field names retained as diagnostic data.
- `npm run check:skill`: metadata, links, license consistency, and the pre-publication prohibition on registry execution instructions passed.
- `npm run test:package`: an actual offline tarball contained exactly 13 allowlisted files, installed to both hosts, preserved byte equality with the source, and performed a second install without changing files or mtimes. Lifecycle scripts were disabled; no registry package was fetched.

These are local tests, not a completed Linux/macOS CI matrix or a security certification. Runtime host evaluation and external publication remain separate, pending work. No credentials or permission policies were changed as part of this follow-up.
