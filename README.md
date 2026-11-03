# configure-subagents

A project-aware Skill for designing and improving **Claude Code and Codex agents**. Run it from either host and explicitly target Claude, Codex or both. Without a target, it configures the host you are using.

The host AI reads your project, decides whether separate agents are useful, and proposes roles, models, tools, and handoffs. It can also update existing project agents while preserving unrelated instructions and metadata. A small Python checker validates the generated files without executing them.

**1.0.0 — first stable release, with documented evaluation limits.** This is a reviewable configuration tool, not a guarantee of perfect AI analysis. The maintainer accepted the documented unverified scopes and model/host limitations on November 3, 2026. The 14-file installed Skill payload is unchanged from the evaluated `1.0.0-rc.1`; stable promotion changes package metadata and public documentation. File-tool correctness remains a release gate. The [earlier behavior limitation](#known-behavior-limitation-in-alpha5) remains recorded. Cross-platform static checks, authenticated host behavior and generated-Agent execution are separate evidence.

## What it does

- Grounds recommendations in project instructions, structure, tests, and existing agent configuration.
- Reuses existing capabilities when enough; no additional agent is a valid recommendation.
- Proposes a minimal configuration when evidence is limited, identifies provisional choices, and reassesses existing agents as the project progresses.
- Separates proposal, application, static validation, and explicitly requested runtime checks.
- Compares eligible models and capabilities separately for each selected target, regardless of the execution host.
- Uses project `.claude/agents/*.md` for Claude and `.codex/agents/*.toml` for Codex; applies necessary changes through a guarded file helper.

It does not orchestrate project work, call generated Agents by default, edit global settings, or grant system permissions. Codex custom agents inherit parent permissions/provider/MCP; their TOML does not create an independent sandbox.

## 1.0.0: dual targets and guarded application

| Execution host | Default configuration target | Explicit targets |
|---|---|---|
| Claude Code | Claude Code | Claude, Codex, both |
| Codex | Codex | Claude, Codex, both |

The Skill announces its project and target. It does not change the other target merely because existing files are present. `--agent all` below installs the Skill for both hosts; it does not generate either Agent configuration. Project base settings and `AGENTS.md` are not edited automatically.

The new application helper stages complete candidates and original copies under `.configure-subagents-work/`, checks every selected target before writing, requires the checked candidate digest, and rejects stale originals, unsupported format changes and unapproved deletions. Rename/consolidation requires exact old-file deletion allowances from the user's request. Unchanged files keep their modification times. Partial failures use conditional recovery; uncertain/concurrently changed outputs and backups are retained for manual review. See [guarded application](configure-subagents/references/guarded-application.md).

This helper protects the path that uses it; it does not stop another program or an AI from writing directly, prove semantic correctness, or provide an atomic multi-file transaction. The Skill instructs hosts to stop rather than bypass a rejected/unavailable helper. No-op reassessment skips new candidates/backups. Existing language, comments, extensions and explicit model constraints remain preservation requirements.

The RC campaign records **22 authenticated session outcomes**, including default/cross/both-target requests and isolated copies of Signal Flare and Mosigi: 21 native final receipts and one final-report observation with an unverified process exit. Current RC results must be read from the release checklist and release report, not inferred from the earlier alpha results. Generated-Agent calls and performance/cost benchmarks are excluded.

### Earlier alpha.8 model-selection work

The Skill builds a target-model pool before assigning roles, separating eligible, unverified and excluded candidates. It compares actual work requirements and the leading alternative, rather than copying the main session's model or assigning a fixed model family to every reviewer, writer or implementer. Older generations are not assumed cheaper; price, quota, expected work and measured performance are separate evidence.

Ordinary improvement requests also reassess existing model fields. A justified model-only correction can preserve all other instructions, while separately stated fixed-model choices and ceilings remain binding. Unknown price alone does not require inheritance; unknown eligibility retains an existing choice, uses `inherit` for new Claude Agents or omits model/effort for new Codex Agents. Conditional alternatives stay outside runnable fields. No automatic routing, retries or model-access probes are added.

Alpha.8 includes these instructions and verified upgrade fingerprints for unmodified alpha.6/7 installations. Both hosts completed two fresh synthetic proposals and an application/fresh-repeat pair; model-only edits and no-change repeats were independently checked. See [selection guidance](configure-subagents/references/role-and-model-selection.md), the [bounded evaluation](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/MODEL_SELECTION_BEHAVIOR.md) and [alpha.8 release notes](https://github.com/ChiwooSong/configure-subagents/blob/v0.1.0-alpha.8/releases/v0.1.0-alpha.8.md). This does not establish actual performance or cost savings. Stable 1.0.0 retains and discloses the earlier first-pass exception/cross-review limitations.

## Installation

Requires Node.js 22 or newer. Install for both supported tools, using the same scoped-package and `--agent all` convention as HTMLEdit:

```sh
npx --yes @woody_s/configure-subagents@latest install --agent all
```

Choose one tool or another project:

```sh
npx --yes @woody_s/configure-subagents@latest install --agent claude
npx --yes @woody_s/configure-subagents@latest install --agent codex
npx --yes @woody_s/configure-subagents@latest install --agent all --project ./my-project
```

The npm package is [@woody_s/configure-subagents](https://www.npmjs.com/package/@woody_s/configure-subagents), owned by `woody_s`; the source repository remains `ChiwooSong/configure-subagents`. Use `@latest` for stable 1.0.0 or pin `@1.0.0` for reproducibility. The separate `@next` channel still identifies the historical `1.0.0-rc.1`; it is not the stable installation command. Earlier alpha releases configure Claude Agents only; stable 1.0.0 supports both configuration targets. `--yes` skips npm's download confirmation; it does not authorize the Skill to change project agents. If the expected version is unavailable or ownership differs, stop instead of substituting another package.

The installer copies the Skill only. It does not invoke models, generate agents, install Python dependencies, or change global settings. One of `--agent` or `--host` is required; `--project` defaults to the current directory. Identical installations succeed unchanged; different contents are reported as conflicts without overwriting. `--help`, `--version`, and no arguments only display information.

Already installed? Use **`update`**, not `install`:

```sh
npx --yes @woody_s/configure-subagents@latest update --agent all
```

`--version` reports the downloaded CLI's version, not the version of a previously copied project Skill. Read the update result for each selected host.

Starting with alpha.7, the first output line makes the result explicit:

| First line | Meaning |
|---|---|
| `SUCCESS: Skill installation completed.` | Installation finished; inspect `installed:` / `unchanged:` paths below it. |
| `SUCCESS: Skill update completed.` | Update finished; inspect `updated:` / `unchanged:` paths and backup locations. |
| `SUCCESS: Skill files already match this version. No changes needed.` | Successful no-op; the installed Skill files already match the CLI's bundled payload. |
| `ERROR: Skill installation failed.` / `ERROR: Skill update failed.` | Operation failed; read the details on stderr. No success banner is printed. |

Success output also shows the CLI version and the invocation command for each selected host. Invalid arguments print `ERROR: Invalid arguments.` and exit 2; operation failures exit 1; successful operations exit 0. The old warning-like sentence about discovery/execution is removed from successful CLI output. The README still distinguishes copying files from actual host discovery and Agent execution.

Alpha.7 changes CLI messages only; its Skill payload is identical to alpha.6. Updating an unmodified alpha.6 installation therefore reports a successful no-op and preserves file modification times. See the [alpha.7 release notes](https://github.com/ChiwooSong/configure-subagents/blob/v0.1.0-alpha.7/releases/v0.1.0-alpha.7.md).

### Migrating from the unscoped package

Starting with `0.1.0-alpha.2`, new releases use **`@woody_s/configure-subagents`**. The old `configure-subagents@0.1.0-alpha.1` remains available for existing users; it is not deleted or silently redirected. Its npm deprecation notice points to this migration. Switch the package name in saved commands and scripts. The old version does not support `--agent`.

| Earlier option | Preferred option in the scoped package |
|---|---|
| `--host claude` | `--agent claude` |
| `--host codex` | `--agent codex` |
| `--host both` | `--agent all` |

All three `--host` options remain supported by the new package. Use one selector per command; combining `--host` and `--agent` is an error, even when they identify the same tools. `all` means Claude Code and Codex, the two supported hosts.

The installed folders and invocation names **do not change**: `.claude/skills/configure-subagents`, `.agents/skills/configure-subagents`, `/configure-subagents`, and `$configure-subagents`. Alpha.2 had the same Skill payload as alpha.1. From alpha.6, use the scoped CLI's `update` command to upgrade recognized unmodified older installations, including the old unscoped alpha.1. Existing `.claude/agents` and `.codex/agents` files are untouched.

If you customized an installed Skill, the installer stops with a conflict. Keep your copy, compare it with the new package in a separate temporary project, and merge deliberately. Do not delete the customized directory just to make installation pass. An npm-installed CLI dependency is separate from these Skill folders: update its dependency name explicitly if you installed the old CLI locally or globally. For npx-only CLI usage, switch the package name in the command; existing copied Skills still need the update procedure below.

<a id="updating-an-existing-skill-to-alpha5"></a>

### Updating an existing Skill

Run the new CLI in your project, or supply `--project`:

```sh
npx --yes @woody_s/configure-subagents@latest update --agent all --project ./my-project
```

Use `--agent claude` or `--agent codex` if only that host is installed. `--host claude|codex|both` remains compatible. All selected hosts must already have a Skill; a missing host stops the update and directs you to `install`.

- **Unmodified known release:** the entire Skill tree matches bundled SHA-256 fingerprints for published alpha.1 (unscoped), alpha.2 or alpha.4 through alpha.8. It is upgraded to the CLI's bundled Skill. No registry access or project code execution occurs inside `update`.
- **Already current:** reports `unchanged`, preserving bytes and modification times without creating backups.
- **Customized, incomplete or unknown:** reports differing paths and stops before changing either host. Edits, additions, deletions, extra directories and line-ending changes all count. It does not guess ownership from a version marker, normalize files, merge automatically or force-overwrite. A later unrecognized release is also refused rather than downgraded.

Both hosts are checked before applying anything. Successful updates report `updated` and the original backup path under `.configure-subagents-updates/<transaction>/backups/<host>/`. This project-local directory is outside both Skill discovery paths. Backups retain original bytes and modification times; keep them until you have checked the update, then remove only the transaction folders you no longer need. Consider ignoring this folder in your project's Git configuration; the CLI does not edit `.gitignore`.

An unmodified `1.0.0-rc.1` installation already has the same 14 Skill files as stable 1.0.0. Running the stable `update` command therefore reports a successful no-op and preserves modification times. The downloaded CLI reports version 1.0.0; a no-op does not mean the upgrade command failed. User-customized Skills still require deliberate manual merging.

Updates stage the complete replacement before moving an original to its backup. If a handled failure occurs, originals are restored when the destination still belongs to this operation. Concurrent changes are never deliberately overwritten; retained backups/recovery paths are reported for manual inspection. A process termination or power loss can interrupt the moves: this is not a crash-atomic, two-host transaction. Inspect the reported storage directory and restore the appropriate backup only after checking the live destination. Symbolic links/junctions in destination paths are refused. These checks are not isolation from a hostile concurrent filesystem writer.

For a customized Skill, install into a **separate temporary project**, back up the existing Skill outside discovery folders, and compare/merge the full payload yourself. Do not delete custom instructions to make the update pass. Install and update only copy Skill files; **`.claude/agents`, `.codex/agents`, other Skills, project source and global settings stay untouched**. Restart/reload the host as needed to discover updated instructions; installation does not prove discovery or model execution.

CLI exits: `0` for successful install/update/no-op/help, `1` for filesystem conflicts or operation failure, `2` for invalid arguments. There is no force option. See the [alpha.6 release notes](https://github.com/ChiwooSong/configure-subagents/blob/v0.1.0-alpha.6/releases/v0.1.0-alpha.6.md).

Alpha.4 asks the AI to select models by role, task difficulty, and verified availability without a routine cost/quality questionnaire. It asks about a model ceiling only when a material unresolved limit prevents a suitable assignment. `inherit` is a fallback, not a claim of completed model optimization. These are Skill instructions, not automatic runtime model routing, and model-selection quality is not established across the supported matrix. Limited complex-role choices and earlier unknown-availability failures are recorded in the evaluation reports.

It also keeps sparse-project proposals minimal, explains assumptions and what evidence would justify revisiting them, and improves existing agents on later invocations without unnecessary rewrites. Evidence quality matters more than project age or code volume. Alpha.4 includes the model-selection work prepared for alpha.3; alpha.3 was tagged as a draft but was not published to npm.

Alpha.5 requires a concrete configuration gap before editing: optional elaboration is not a reason to rewrite adequate instructions. It preserves byte-level formatting, including line endings, and keeps the existing Agent language unless you explicitly request changing it. Asking for a Korean explanation does not translate an English Agent. It also adds source inventories and byte inspection, with documented remaining host limitations. See the [alpha.5 release notes](https://github.com/ChiwooSong/configure-subagents/blob/v0.1.0-alpha.5/releases/v0.1.0-alpha.5.md).

### Manual installation

Copy the `configure-subagents` folder from your reviewed source tree, including its LICENSE, to the desired project location:

| Host | Destination |
|---|---|
| Claude Code | `.claude/skills/configure-subagents/` |
| Codex | `.agents/skills/configure-subagents/` |

Compare existing content before copying. Do not overwrite an existing customized Skill. See [host usage](configure-subagents/references/host-usage.md) for discovery and checker details.

The local installer can be tested from this source tree with Node.js 22+. It has no external runtime dependencies, refuses conflicting installations, and leaves identical files untouched. Copying or installing the Skill does not prove that a host discovers it or that a generated agent executes successfully.

## Use it

In Claude Code:

```text
/configure-subagents Propose subagents for this project. Do not change files.
```

In Codex:

```text
$configure-subagents Improve and apply this project's agent configuration.
$configure-subagents Propose both Claude Code and Codex agent configurations. Do not change files.
```

| Request | Result |
|---|---|
| Propose | Read-only project analysis and a reasoned configuration proposal |
| Create or apply | Scoped edits, preservation checks, and static validation |
| Validate existing agents | Diagnostics and recommendations, without automatic edits |
| Test an actual invocation | A small runtime check only when explicitly requested |

## Languages

Responses follow your requested language. Existing Agent descriptions and instructions retain their established language unless you explicitly request changing the Agent language. For new Agents, an explicit Agent-language request takes priority, followed by project conventions and then the conversation language. The analysis workflow is not tied to a programming language: scripts, service-based projects, and documentation projects can use it. This is a design capability, not a claim that all languages have been tested. CLI and checker diagnostics are currently English.

## Static validation

Python 3.10+ is required. Claude YAML validation needs PyYAML; Codex TOML validation uses standard-library tomllib on Python 3.11+ or conditional tomli on 3.10. These parsers do not execute Agent instructions. The separate `inspect_file_bytes.py` and `find_evidence.py` helpers use only Python's standard library. They report measured file bytes and paginated source inventories without writing temporary files or executing project code; they do not require PyYAML. Use a virtual environment and install `configure-subagents/requirements.txt` into it. Then, from this source tree:

```sh
python configure-subagents/scripts/validate_agents.py --project-root /path/to/project --format json
python configure-subagents/scripts/validate_codex_agents.py --project-root /path/to/project --format json
```

Exit codes: `0` means no static errors, `1` means invalid configuration, and `2` means an unavailable or incomplete check. Warnings do not change exit code 0.

The checker reports YAML errors, field types, duplicate names, tool-list conflicts, and unknown values. It also flags hooks, MCP servers, and permission modes requiring capability review. **A `passed` result is not a security approval.** The checker does not execute hooks or servers, prove model access, or verify every nested setting.

Project files, existing agent prompts, and diagnostic text are untrusted data. Text appearing in JSON output must not be treated as instructions. Preserving an existing field does not endorse or authorize its execution.

## Development checks

With Node.js 22+ and Python dependencies from the Skill requirements available:

```sh
npm test
npm run test:python
npm run check:skill
npm run test:package
```

`test:package` packs a local tarball and installs it offline into a temporary project with lifecycle scripts disabled. It never publishes or downloads this package from the registry.

The installer tests cover conflicts, repeated installation, partial failure, preservation of concurrently modified files, and linked paths. These checks are not an OS-level defense against a hostile writer changing parent directories between filesystem calls.

Alpha.6 adds offline upgrade tests against captured published alpha.1/2/4/5 Skill bytes, both-host rollback and concurrent-edit cases. The package smoke test installs the actual tarball and upgrades an alpha.5 fixture while preserving existing Agent files. See the [update evaluation](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/UPDATE_COMMAND.md). The capture script is a maintainer-only network operation; ordinary tests and `update` use bundled fixtures/fingerprints without fetching older packages.

Detailed evaluation and security follow-up reports are in the source repository's `evals` directory; they are not included in the npm payload. Initial authentication and sandbox blockers were resolved without changing stored credentials or weakening permissions. The [alpha.4 baseline](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/ALPHA4_BEHAVIOR.md) records an unnecessary Codex rewrite and mixed line endings; the [follow-up evaluation](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/NOOP_EOL_BEHAVIOR.md) records both hosts preserving unchanged files and CRLF after instruction changes. The [earlier alpha.5 lifecycle report](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/ALPHA5_BEHAVIOR.md) records language-preservation and regression evaluation on an earlier candidate payload. These focused scenarios do not establish the full host/project matrix or generated-Agent runtime behavior. The alpha.5 [source-retrieval evaluation](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/RETRIEVAL_AUDIT_BEHAVIOR.md) is tracked separately; its status must not be inferred from the earlier alpha.5 results.

### Known behavior limitation in alpha.5

This limitation remains in alpha.6. The update command changes package installation behavior; it does not resolve the host-analysis findings below. No new authenticated model sessions were run for alpha.6.

In our Windows tests with Claude Code 2.1.302 and `claude-opus-5-5`, first-pass analysis and cross-review of exceptions spread across project documents remain unreliable. The R8 retrieval changes found the previously missed isolated-Mac verification exception before the first draft, but Claude still installed the Signal Flare configuration without the required second source comparison. A broad worker also retained a universal fix-to-green workflow despite reproduction/design-only assignments; a fresh no-edit repeat did not detect that conflict. Better retrieval is not a guarantee that every exception or review checkpoint is covered. This is a limitation observed in this host/model/scenario, not a claim about all Claude models or proof of a model-intrinsic cause.

Review generated restrictions against the applicable base assignment, revisions and handoff/result evidence before relying on them for project work. Proposal mode can make that review easier. A static validator pass or an unchanged repeat does not establish semantic completeness; rerunning may uncover a real omission. See the [R8 evidence and current status](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/RETRIEVAL_AUDIT_BEHAVIOR.md). Generated-Agent invocation and runtime enforcement remain separate, unverified checks.

### RC evidence accepted for stable 1.0.0

The [installed-RC campaign](https://github.com/ChiwooSong/configure-subagents/blob/main/evals/RC1_BEHAVIOR.md) records the original 22 outcomes: Codex has 11 native final receipts, Claude has ten plus one reconciled final-report observation. Seven fresh repeats have matching requests/start snapshots and unchanged observed bytes/mtimes, including transaction records. The last Claude real-both repeat's report and current matching apply-output bytes/mtimes were independently observed, but its window disappeared without a native exit receipt; its return code and separately persisted start/end binding remain unverified. Claude validation-only commands were permission-blocked and are not passes. Some real-project output retains overbroad workflow or memory-threshold wording despite task-specific conditions. All eight real-project outcomes used inputs omitting module sources such as `.mjs` wrappers because of a harness allowlist bug. The harness is fixed and regression-tested; the maintainer chose no additional model sessions, so module-inclusive real-project behavior remains unverified. Missing input must not be blamed on a host or described as missing original source. No release-blocking file-tool defect was observed within the tested scope. These observations do not establish semantic completeness or prove a model-intrinsic cause.

### Accepted unverified scopes and model limitations

On November 3, 2026, the maintainer explicitly accepted these limits for stable publication, without treating them as passed tests:

- Module-inclusive real-project behavior remains unverified. The original eight real outcomes used incomplete frozen source captures; the harness fix and its tests do not supply missing host behavior evidence.
- Claude validation-only helper execution was permission-blocked. Manual findings and independent checks do not establish that the host ran those commands.
- The last Claude real-both repeat has an observed final report and current matching file bytes/mtimes, but no recovered native exit code or independently persisted start/end binding.
- First-pass exception discovery and cross-review may miss conditions or preserve overbroad workflow/resource rules. Seven unchanged native repeats establish file preservation, not semantic completeness. Configured models and historical model use do not prove current account availability.
- Generated-Agent discovery/invocation, real runtime enforcement, measured performance/cost savings, all programming languages and broad OS/model/provider compatibility remain unverified. Authenticated behavior evidence is from Windows; Linux/macOS evidence is static CI.

Review the proposed rules against applicable assignments and conditional exceptions before using them for project work. The guarded helper protects file application, not the executing model's judgment or another program's direct writes. No additional model sessions were used to turn retained failures into passes.

## Stable release decision

The [release checklist](https://github.com/ChiwooSong/configure-subagents/blob/main/docs/V1_RELEASE_CHECKLIST.md) separates release-blocking installer/validator/application-tool defects from documented AI/host judgment limits. It no longer requires three flawless semantic apply/repeat pairs. Retained failures are reviewed, not erased by rerunning until green.

The maintainer approved stable 1.0.0 on November 3, 2026, accepting the disclosed limits and skipping rc.2. The installed Skill bytes remain those evaluated in rc.1. Final exact-commit CI, tarball checks and public-registry verification accompany the [1.0.0 release](https://github.com/ChiwooSong/configure-subagents/releases/tag/v1.0.0). Both-host instructions do not imply identical capability controls or provider model names.

## License

[MIT](LICENSE), copyright 2026 Chiwoo Song.
