# configure-subagents

A project-aware Skill for designing and improving Claude Code subagents. Run the Skill from **Claude Code or Codex**; the generated configuration targets **Claude Code**.

The host AI reads your project, decides whether separate agents are useful, and proposes roles, models, tools, and handoffs. It can also update existing project agents while preserving unrelated instructions and metadata. A small Python checker validates the generated files without executing them.

**Alpha preview.** End-to-end host behavior and language-by-language performance remain unverified. Successful installation is distinct from successful Skill discovery or execution.

## What it does

- Grounds recommendations in project instructions, structure, tests, and existing agent configuration.
- Reuses existing capabilities when enough; no additional agent is a valid recommendation.
- Proposes a minimal configuration when evidence is limited, identifies provisional choices, and reassesses existing agents as the project progresses.
- Separates proposal, application, static validation, and explicitly requested runtime checks.
- Selects models for the target Claude Code environment, even when Codex runs the Skill.
- Limits configuration changes to the selected project's `.claude/agents/` directory.

It does not configure Codex agents, orchestrate project work, call generated agents by default, or grant system permissions.

## Installation

Requires Node.js 22 or newer. Install for both supported tools, using the same scoped-package and `--agent all` convention as HTMLEdit:

```sh
npx --yes @woody_s/configure-subagents@next install --agent all
```

Choose one tool or another project:

```sh
npx --yes @woody_s/configure-subagents@next install --agent claude
npx --yes @woody_s/configure-subagents@next install --agent codex
npx --yes @woody_s/configure-subagents@next install --agent all --project ./my-project
```

The npm package is [@woody_s/configure-subagents](https://www.npmjs.com/package/@woody_s/configure-subagents), owned by `woody_s`; the source repository remains `ChiwooSong/configure-subagents`. This is still an alpha, so the documented channel is `@next`. For a fixed version use `@0.1.0-alpha.4`. `--yes` skips npm's download confirmation; it does not authorize the Skill to change project agents. If the expected version is unavailable or ownership differs, stop instead of substituting another package.

The installer copies the Skill only. It does not invoke models, generate agents, install Python dependencies, or change global settings. One of `--agent` or `--host` is required; `--project` defaults to the current directory. Identical installations succeed unchanged; different contents are reported as conflicts without overwriting. `--help`, `--version`, and no arguments only display information.

### Migrating from the unscoped package

Starting with `0.1.0-alpha.2`, new releases use **`@woody_s/configure-subagents`**. The old `configure-subagents@0.1.0-alpha.1` remains available for existing users; it is not deleted or silently redirected. Its npm deprecation notice points to this migration. Switch the package name in saved commands and scripts. The old version does not support `--agent`.

| Earlier option | Preferred option in the scoped package |
|---|---|
| `--host claude` | `--agent claude` |
| `--host codex` | `--agent codex` |
| `--host both` | `--agent all` |

All three `--host` options remain supported by the new package. Use one selector per command; combining `--host` and `--agent` is an error, even when they identify the same tools. `all` means Claude Code and Codex, the two supported hosts.

The installed folders and invocation names **do not change**: `.claude/skills/configure-subagents`, `.agents/skills/configure-subagents`, `/configure-subagents`, and `$configure-subagents`. Alpha.2 had the same Skill payload as alpha.1. **Alpha.4 changes the Skill instructions**, so installation over alpha.1 or alpha.2 reports a conflict rather than silently upgrading. Existing `.claude/agents` files are untouched.

If you customized an installed Skill, the installer stops with a conflict. Keep your copy, compare it with the new package in a separate temporary project, and merge deliberately. Do not delete the customized directory just to make installation pass. An npm-installed CLI dependency is separate from these Skill folders: update its dependency name explicitly if you installed the old CLI locally or globally. For npx-only CLI usage, switch the package name in the command; existing copied Skills still need the update procedure below.

### Updating an existing Skill to alpha.4

Downloading the new npm CLI does not update an already copied Skill. Create a separate temporary project directory and install the pinned alpha.4 package there. Compare its Skill with your existing installation. Back up the existing Skill outside `.claude/skills` and `.agents/skills`, then merge the reviewed changes into the original location, preserving custom instructions. The changed Skill files are `SKILL.md`, `references/project-analysis.md`, and `references/role-and-model-selection.md`. There is no force-overwrite or automatic upgrade option.

Alpha.4 asks the AI to select models by role, task difficulty, and verified availability without a routine cost/quality questionnaire. It asks about a model ceiling only when a material unresolved limit prevents a suitable assignment. `inherit` is a fallback, not a claim of completed model optimization. These are Skill instructions, not automatic runtime model routing, and their host behavior has not yet been independently evaluated.

It also keeps sparse-project proposals minimal, explains assumptions and what evidence would justify revisiting them, and improves existing agents on later invocations without unnecessary rewrites. Evidence quality matters more than project age or code volume. Alpha.4 includes the model-selection work prepared for alpha.3; alpha.3 was tagged as a draft but was not published to npm.

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
$configure-subagents Improve and apply this project's Claude Code reviewer configuration.
```

| Request | Result |
|---|---|
| Propose | Read-only project analysis and a reasoned configuration proposal |
| Create or apply | Scoped edits, preservation checks, and static validation |
| Validate existing agents | Diagnostics and recommendations, without automatic edits |
| Test an actual invocation | A small runtime check only when explicitly requested |

## Languages

Responses follow your requested language. Generated agent instructions follow your explicit language choice, then project conventions, then the conversation language. The analysis workflow is not tied to a programming language: scripts, service-based projects, and documentation projects can use it. This is a design capability, not a claim that all languages have been tested. CLI and checker diagnostics are currently English.

## Static validation

The checker requires Python 3.10+ and PyYAML. Use a virtual environment and install `configure-subagents/requirements.txt` into it. Then, from this source tree:

```sh
python configure-subagents/scripts/validate_agents.py --project-root /path/to/project --format json
```

Exit codes: `0` means no static errors, `1` means invalid configuration, and `2` means an unavailable or incomplete check. Warnings do not change exit code 0.

The checker reports YAML errors, field types, duplicate names, tool-list conflicts, and unknown values. It also flags hooks, MCP servers, and permission modes requiring capability review. **A `passed` result is not a security approval.** The checker does not execute hooks or servers, prove model access, or verify every nested setting.

Project files, existing agent prompts, and diagnostic text are untrusted data. Text appearing in JSON output must not be treated as instructions. Preserving an existing field does not endorse or authorize its execution.

## Development checks

With Node.js 22+, Python 3.10+, and PyYAML available:

```sh
npm test
npm run test:python
npm run check:skill
npm run test:package
```

`test:package` packs a local tarball and installs it offline into a temporary project with lifecycle scripts disabled. It never publishes or downloads this package from the registry.

The installer tests cover conflicts, repeated installation, partial failure, preservation of concurrently modified files, and linked paths. These checks are not an OS-level defense against a hostile writer changing parent directories between filesystem calls.

Detailed evaluation and security follow-up reports are in the source repository's `evals` directory; they are not included in the npm payload. Authenticated Claude Code evaluation was blocked by an API authentication error; Codex CLI evaluation was blocked by local read policy. Neither has been reported as passed.

## Road to 1.0

The proposed stable-release criteria are:

- Demonstrate proposal, application, validation, and repeat-invocation behavior in both hosts using small, service-based, documentation, and existing-agent projects, including sparse information and later project growth.
- Verify read-only proposals, preservation of user edits and unrelated fields, meaningful model choices within verified constraints, and no unnecessary rewrites. Resolve material security or data-loss issues.
- Establish a documented compatibility contract for CLI options, installation paths, validator output and exit codes, and a tested update procedure that preserves customized Skills.
- Pass the supported OS/Python CI matrix and published-package installation checks, then test a release candidate without unresolved release-blocking regressions.

These are readiness criteria, not completed evaluations or a promise to support every language or model. Actual generated-agent invocation remains a separately requested check. Version 1.0.0 will mark the supported interface and behavior as stable, following [Semantic Versioning](https://semver.org/).

## License

[MIT](LICENSE), copyright 2026 Chiwoo Song.
