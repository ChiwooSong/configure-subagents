# Role and model selection

## Split roles when the handoff is worthwhile

Propose separate agents for recurring specialized work, summarizing large investigations, or independent review when the benefit exceeds coordination cost. Reuse the main AI or existing agents when sufficient. Researcher, Planner, and Implementer are examples, not a mandatory roster.

- Small script: first consider whether the main AI or existing review capability is enough.
- Multiple services: use actual service boundaries, shared code, and dependencies.
- Documents: consider research, drafting, and fact-checking; do not force implementation or test roles.
- Existing configuration: identify overlapping descriptions/outputs and missing verification responsibilities. Explain consolidation benefits and compatibility with existing invocation names.

For each proposed role specify purpose, evidence of need, invocation/non-invocation conditions, inputs, output format, completion criteria, responsibility boundaries, model, tools, and selection reasons. State handoff outputs and when failures should be reported to the main AI. Do not imply that automated retries, orchestration, or enforced budgets have been implemented.

Recommend sequential work for roles editing the same files. Instructions are not hard isolation. Do not add worktree isolation or similar features without checking version support and relevance.

## Select models for the target environment

The target is **Claude Code**, even if Codex runs this Skill. Do not copy Codex model names, reasoning options, or API identifiers into Claude agent configuration.

1. Respect an explicitly requested model and inspect existing settings. Preserve an existing choice when justified.
2. Use verified target version, provider configuration, and model policies. A documented alias does not prove account access.
3. Consider faster models for simple, structured investigations and stronger reasoning for complex or high-impact decisions, using evidence from that environment. Do not hardcode current prices or model rankings into the core workflow.
4. If availability cannot be established, use `model: inherit` for new agents. Preserve existing model settings without unsupported changes; report optimization as unverified.

Inheritance means the **future Claude Code main session's model**, not the Codex host model. Environment variables, invocation options, and policies may affect the actual model. Without runtime evidence, do not claim verified model use or cost savings.

## Select tools

Explicitly list the tools needed by a new agent. `Read, Glob, Grep` illustrates a source-reading role; check actual host support separately. An agent with editing, shell, or external-write tools is not read-only.

For a test-running role, identify the supported shell tool, commands, working directory, and failure reporting. Instructions do not technically prevent other shell operations. Tool lists and permission modes do not grant new OS or account permissions. For unknown MCP tools, explain required functionality and what access remains to be checked.
