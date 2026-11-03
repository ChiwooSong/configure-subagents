# 1.0.0 stable release verification

Verified: November 3, 2026 (Asia/Seoul). The maintainer accepted the documented unverified scopes/model limitations and authorized stable publication, skipping rc.2. Accepted unknowns and retained semantic failures are not passed tests.

- Package: [@woody_s/configure-subagents@1.0.0](https://www.npmjs.com/package/@woody_s/configure-subagents/v/1.0.0), MIT, owner `woody_s`.
- GitHub: [v1.0.0](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0), verified public, not draft, not prerelease, GitHub latest release.
- Exact release source/tag: [b0a7787d2483f1b686827518a94184120dd59a90](https://github.com/ChiwooSong/configure-subagents/commit/b0a7787d2483f1b686827518a94184120dd59a90).
- [Exact-source static CI](https://github.com/ChiwooSong/configure-subagents/actions/runs/41639576380): all six Windows/Linux/macOS × Python 3.10/3.13 jobs passed with Node 22. All required Node/Python/Skill/tarball steps passed. Local counts: 64 Node tests and 116 Python tests.
- npm `latest` resolves to `1.0.0`; `next` remains historical `1.0.0-rc.1`. Downloading the CLI through `npx ...@latest --version` returned `1.0.0`.

## Exact artifact

The 21-file allowlist contains only the CLI, Skill, required metadata/docs and MIT license. The tested local tarball was published directly. Registry metadata and all installed distribution bytes match; all 14 installed Skill files also match the evaluated registry RC and committed Skill bytes. CLI implementation files are unchanged from the RC.

```text
filename: woody_s-configure-subagents-1.0.0.tgz
sha256: 519a5a4c020c22d2744082658d0d950cbcdf8d3e7f95cf88c32ea8e7416bea60
integrity: sha512-EYfgrJJLZtiAvchfYqxcdvAHL43T2ydwwnBMMjMVzwrrWe3qy6bZ1RAbhHFOodOS+BVLj7Bo3kC6cboduZixvw==
```

Both the local artifact and a fresh registry installation passed:

- Installation in both hosts, identical installation repeats and byte/mtime preservation.
- Pristine alpha.8 upgrade, update repeat, preserved Claude/Codex Agent trees and refusal to overwrite customized Skills.
- Pristine rc.1 update as a no-op, without rewritten files, changed mtimes or new backup storage.
- Execution of the exact installed both-target guarded prepare/check/apply helper and unchanged completed-task replay. No generated Agent was invoked.

The [tarball](https://github.com/ChiwooSong/configure-subagents/releases/download/v1.0.0/woody_s-configure-subagents-1.0.0.tgz), [SHA256SUMS](https://github.com/ChiwooSong/configure-subagents/releases/download/v1.0.0/SHA256SUMS) and [sanitized verification receipt](https://github.com/ChiwooSong/configure-subagents/releases/download/v1.0.0/verification.json) were downloaded from GitHub after publication and matched the tested local bytes.

## Scope of the stable decision

The [RC report](../evals/RC1_BEHAVIOR.md), [README](../README.md) and [stable release notes](../releases/v1.0.0.md) retain incomplete module-source inputs in eight real outcomes, Claude's validation permission block, the last unrecovered native exit receipt, and first-pass/cross-review semantic limitations. There are 22 retained outcomes, 21 native final receipts, one reconciled final report and seven native unchanged repeats; this is not an all-pass claim.

No extra model sessions were performed for stable promotion. Model access, generated-Agent discovery/invocation, runtime enforcement, actual performance/cost savings and broad language/OS/model/provider support remain unverified. Windows authenticated behavior and cross-platform static CI are distinct evidence. Later documentation-only commits close this checklist without moving the release tag or changing published package bytes.
