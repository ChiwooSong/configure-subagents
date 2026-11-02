# Claude Code configuration and application

Official references, checked 2026-10-14:

- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Skills](https://code.claude.com/docs/en/skills)

This is the minimum v1 output format. Recheck the target version and official documentation when using new or changed features. Static validation is not a compatibility guarantee for every version.

## File format

Write YAML frontmatter and Markdown instructions in the selected project's `.claude/agents/<name>.md`. Use readable lowercase kebab-case names and matching filenames for new agents. Do not rename existing files merely because their filename differs. The frontmatter `name` identifies the agent.

```markdown
---
name: change-reviewer
description: Review a completed change against the project's requirements; return findings without editing files.
tools: Read, Glob, Grep
model: inherit
---

Review the supplied change and relevant project instructions.
Input: changed paths, intended behavior, and available validation evidence.
Return actionable findings with file references, impact, and missing evidence.
Finish when the requested change is reviewed; if context is missing, report it.
Do not implement fixes or run project commands.
```

This is a format illustration with **unknown model eligibility**, so it uses `inherit`; it is neither a default Agent nor a default model decision. If `sonnet` is confirmed eligible and fits the actual requirements after comparison, `model: sonnet` is a valid explicit choice. If a verified version/price is essential, use that eligible version's supported ID. With only generic documentation or no eligible suitable model, retain the illustrated fallback and discuss unverified alternatives outside frontmatter. Do not apply an example's model without the candidate-pool assessment. Adapt responsibilities, inputs, outputs, and completion criteria to demonstrated needs.

For an existing file, determine its prose language from its instructions and description before editing. Keep new prose in that language even when the user requests a report in another language. For example, improve an English reviewer in English and explain the changes to the user in Korean. Only an explicit request to translate or change the Agent's language overrides this convention. Preserve quoted terms, identifiers, and intentional multilingual sections; for a mixed file, follow the local section's convention rather than translating unrelated text. Before applying, inspect the description and every inserted section for accidental language switching.

Only `name` and `description` are required by the format. Generate explicit `tools` and `model` for new agents to avoid accidental full tool inheritance. Add other fields only when needed and supported. Do not add hooks, MCP server installation, memory, permission modes, or global environment settings by default.

Tool allow/deny fields accept comma-separated strings or string lists. Denied tools are removed from the available set. A deny entry such as `Bash(command)` may remove the entire tool; do not describe it as a command-only restriction. Independently inspect whether a purported read-only role still has shell access.

## Discovery and conflicts

Subfolders inside one `.claude/agents/` share its name space. Fix duplicates within that scope when authorized. Investigate parent/nested projects, user agents, managed settings, plugins, and session definitions separately. The checker scans one supplied tree, not the entire runtime precedence system.

The referenced documentation describes precedence among managed, session CLI, project, user, and plugin definitions. A nested project's closer definition may take precedence based on the working directory. Check behavior against the target version and report inaccessible scopes.

## Apply and recover

Use the [shared guarded application procedure](guarded-application.md) for every necessary installed-file change. It creates byte-identical originals and complete candidates, accepts only scoped Agent changes, rechecks source/candidate fingerprints, and conditionally recovers its own outputs. Do not apply installed-file edits directly or use Git HEAD as the original: uncommitted user changes must survive.

Only edit the returned Claude candidate tree. Preserve the description/body, custom fields, comments, existing language and byte format except for justified changes. Cross-review the actual candidate against project evidence before check/apply. Warnings about hooks/MCP/permission modes remain visible; preserving them does not authorize execution. No-op reassessment skips prepare and all writes. Deletion/renaming/consolidation require actual user authorization and exact deletion allowances.

A refused, unavailable or conflicted helper means application is unperformed; never bypass it with a manual edit. Inspect retained originals/journal on failure. Multiple file writes are not an atomic transaction or an isolation guarantee. Report static validity, byte preservation and semantic review separately.

### Byte inspection

Use the bundled standard-library helper before editing existing files and after installation or a no-change validation. It reads explicit files within a supplied permitted root and prints JSON to stdout, without backups, helpers or temporary output files. Quote paths and enumerate actual files; it does not expand globs.

```text
python -I "<skill-dir>/scripts/inspect_file_bytes.py" --root "<permitted-root>" "<agent-file>" "<another-agent-file>"
```

Use the same Python interpreter as the validator; this helper does not require PyYAML. Exit 0 means inspection completed, 2 means at least one file could not be inspected. It reports SHA-256, size, nanosecond mtime, UTF-8/BOM and raw CRLF/lone-LF/lone-CR counts. `newline_style` is CRLF, LF, CR, mixed, none, or unverified; non-UTF-8 content is not classified as UTF-8. Do not substitute `grep`/`wc` counts or the operating system's convention. Keep before/after JSON in tool results and compare the exact fields without redirecting to a temporary file. If unavailable, report formatting as unverified. These observations are not a filesystem lock or a replacement for the immediate pre-write conflict check.

## Runtime check (only when requested)

Prepare a temporary project with the relevant agent and minimal input. Do not blindly copy hooks, MCP configuration, or project execution commands. A configuration creation/update request does not authorize this check.

Follow the target version's reload/new-session behavior. Observe agent discovery, explicit invocation of a small task, and returned output. A newly created agents directory may require a new session. Verify actual models from tool events or session metadata, not an agent's self-description or frontmatter alone.

If authentication, permissions, or model access fails, report the cause and unperformed checks. Do not weaken permission modes, change global settings, or repeatedly retry login to obtain a pass.
