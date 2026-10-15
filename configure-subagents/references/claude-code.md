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

This example is not a default agent to create everywhere. Adapt responsibilities, inputs, outputs, and completion criteria to demonstrated needs. Explain model selection in the user report.

For an existing file, determine its prose language from its instructions and description before editing. Keep new prose in that language even when the user requests a report in another language. For example, improve an English reviewer in English and explain the changes to the user in Korean. Only an explicit request to translate or change the Agent's language overrides this convention. Preserve quoted terms, identifiers, and intentional multilingual sections; for a mixed file, follow the local section's convention rather than translating unrelated text. Before applying, inspect the description and every inserted section for accidental language switching.

Only `name` and `description` are required by the format. Generate explicit `tools` and `model` for new agents to avoid accidental full tool inheritance. Add other fields only when needed and supported. Do not add hooks, MCP server installation, memory, permission modes, or global environment settings by default.

Tool allow/deny fields accept comma-separated strings or string lists. Denied tools are removed from the available set. A deny entry such as `Bash(command)` may remove the entire tool; do not describe it as a command-only restriction. Independently inspect whether a purported read-only role still has shell access.

## Discovery and conflicts

Subfolders inside one `.claude/agents/` share its name space. Fix duplicates within that scope when authorized. Investigate parent/nested projects, user agents, managed settings, plugins, and session definitions separately. The checker scans one supplied tree, not the entire runtime precedence system.

The referenced documentation describes precedence among managed, session CLI, project, user, and plugin definitions. A nested project's closer definition may take precedence based on the working directory. Check behavior against the target version and report inaccessible scopes.

## Apply and recover

1. Establish a necessary change using the [reassessment criteria](project-analysis.md#reassess-as-the-project-progresses), then list intended changes, reasons, and items to preserve. When coverage is already adequate, validate in place and report no change; skip candidate/backup creation and all writes. Without deletion authorization, propose deletion, renaming, or consolidation without performing it.
2. Read original bytes before using text editors. Record hashes, file existence, encoding/BOM, line-ending style (CRLF or LF), and final-newline presence. Keep byte-identical originals outside agent discovery paths and verify their hashes. Text-mode read/write copies can normalize newlines and are not valid originals. Git HEAD is not a substitute: it omits uncommitted user changes.
3. Prepare a complete candidate tree including unchanged files in a separate temporary directory. Edit only what is needed; do not reserialize all frontmatter or discard instructions, extra fields, comments, or formatting. Preservation is not endorsement: explicitly report execution-capable hooks, MCP servers, and permission-mode warnings, review their provenance and behavior, and leave unresolved risks visible rather than calling the configuration safe. Do not run them during inspection or delete unrelated fields without authorization.
4. Preserve the original encoding/BOM, final-newline presence, and line endings in each edited file, including newly inserted lines. Use explicit newline handling or byte-preserving edits; do not rely on OS/editor defaults. For an already mixed file, retain untouched bytes and match adjacent lines for insertions; do not normalize the whole file without a request. Compare candidate bytes against originals to catch accidental conversion, mixed endings introduced into a uniform file, or formatting-only changes. If candidate bytes are identical, skip the write. Validate and distinguish existing errors from introduced errors. Fix introduced errors before applying. Report unrelated existing errors without broadening scope.
5. Immediately re-read originals and compare hashes/existence. Recompute if anything changed. Never overwrite a newly occupied path. Reject write paths escaping the selected project through symlinks or junctions.
6. Apply minimal per-file changes and record hashes of the exact written contents. Confirm installed bytes match the validated candidate, including line endings; a readable text diff or successful YAML check alone cannot prove format preservation. Revalidate the full result and inspect the diff for unrelated changes. Multiple file writes are not a transaction.
7. On failure, restore an original only if the current file still equals this operation's recorded output. Remove newly created files only under the same condition. If another writer changed a file, stop and report unrecovered files and original-copy locations. Do not use broad Git reset/checkout commands.

Report changed files, original copies, errors, warnings, and unknowns. If no meaningful change is justified, preserve files as-is.

## Runtime check (only when requested)

Prepare a temporary project with the relevant agent and minimal input. Do not blindly copy hooks, MCP configuration, or project execution commands. A configuration creation/update request does not authorize this check.

Follow the target version's reload/new-session behavior. Observe agent discovery, explicit invocation of a small task, and returned output. A newly created agents directory may require a new session. Verify actual models from tool events or session metadata, not an agent's self-description or frontmatter alone.

If authentication, permissions, or model access fails, report the cause and unperformed checks. Do not weaken permission modes, change global settings, or repeatedly retry login to obtain a pass.
