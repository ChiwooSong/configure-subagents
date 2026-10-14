# configure-subagents

A project-aware Skill for designing and improving Claude Code subagents. Run the Skill from **Claude Code or Codex**; the generated configuration targets **Claude Code**.

The host AI reads your project, decides whether separate agents are useful, and proposes roles, models, tools, and handoffs. It can also update existing project agents while preserving unrelated instructions and metadata. A small Python checker validates the generated files without executing them.

**Alpha preview.** End-to-end host behavior and language-by-language performance remain unverified. Install from reviewed source as described below, or follow the verified npm installation instructions in the [GitHub release](https://github.com/ChiwooSong/configure-subagents/releases). Do not infer a registry download command from this project's name.

## What it does

- Grounds recommendations in project instructions, structure, tests, and existing agent configuration.
- Reuses existing capabilities when enough; no additional agent is a valid recommendation.
- Separates proposal, application, static validation, and explicitly requested runtime checks.
- Selects models for the target Claude Code environment, even when Codex runs the Skill.
- Limits configuration changes to the selected project's `.claude/agents/` directory.

It does not configure Codex agents, orchestrate project work, call generated agents by default, or grant system permissions.

## Manual installation

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

## License

[MIT](LICENSE), copyright 2026 Chiwoo Song.
