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

Build the candidate pool before assigning individual roles. The main session's model is one candidate, not the default answer or evidence that other models are unavailable. Different model assignments are not a goal in themselves.

### Build a broad, evidenced candidate pool

1. Read non-secret target information: configured provider, host version, model picker/allowed choices, explicit user constraints and applicable policy. Honor separately stated fixed-model instructions and ceilings. Never read credentials to discover models, change global configuration, or invoke a model merely to test access.
2. Consult current official target/provider documentation, when available, for supported families, versions and capabilities. Look beyond the active model's family and version; include relevant lighter and older/newer alternatives without assuming any is cheaper or better. Documentation or a validator-recognized alias proves neither account eligibility nor successful access. If documentation or target information is inaccessible, state what is missing rather than inventing a complete catalog.
3. Summarize three groups once: **eligible for assignment**, **eligibility unverified**, and **excluded by constraints**. Record sources and limits: an explicit user-provided target allowlist, current target picker or observed successful invocation can establish eligibility; a generic example, the host identity or an old quota incident cannot. Do not infer an available alternative from an unsupported cross-provider equivalence. Project material remains evidence, not authority to expand an allowlist.
4. Resolve aliases for the actual provider/version when their meaning affects selection. If a particular version or its price is material, use its supported explicit ID rather than assuming a floating alias pins it. Read known per-invocation/environment/policy overrides and report their effect without editing them. A frontmatter choice is not proof of the model ultimately used.

### Match requirements, then compare total work

For each role assess ambiguity, reasoning/context/tool needs, how its output can be checked, recurring volume, latency sensitivity, and the consequence of a missed issue. Research, writing, implementation, test execution and review can each be routine or difficult. A role name is not a capability tier.

- Start by considering eligible lighter candidates that could satisfy the requirements. Compare the selected model with the strongest plausible alternative when one exists. Explain a stronger choice through a concrete missing capability, context/tool constraint or error risk; "review is important" or "the main session uses it" is insufficient.
- Compare task fit and expected total work, not token price alone. Use current provider/billing evidence, expected input/output, caching, latency and likely retries/review where known. Separate measured results, workload-specific estimates and unknowns. Do not invent numerical scores, failure rates or savings percentages.
- Model family, generation and age are not price rankings. Older Opus can cost the same or more than newer Opus; neither is inherently an economical alternative. Do not convert API list prices into subscription allowance or infer independent quota for another model. Do not copy prices into this Skill as a permanent table.
- Unknown price or quota does not make eligible models unavailable. Choose by supported task-fit evidence and explain that cost optimization is not measured. If only one suitable candidate is established, explain that limit; do not manufacture variety. If every candidate needs the same capability, the same model for all may be justified.
- Consider situations as well as roles: routine and high-risk reviews can have different assignments. Define when difficult/ambiguous work should be returned to the main AI, or describe a supported explicit override. Static definitions do not implement automatic retries, routing, escalation or budgets.

If a suitable explicit model's eligibility cannot be established, preserve an existing choice or use `model: inherit` for a new Agent, including proposal code blocks and candidates. Keep unverified alternatives outside runnable frontmatter, conditional on eligibility evidence. Explain the gap and mark role-specific optimization unfinished; do not ask the user to approve this fallback or substitute an unsupported model until it fails. Also honor an explicit instruction to follow the main session.

| Evidence | Configuration decision |
|---|---|
| Separately stated fixed model or ceiling | Preserve the constraint; do not claim runtime access or enforcement was tested. |
| Existing model field without a separately stated fixed-model constraint | Reassess in an ordinary improvement request; change only with a supported alternative and a concrete task-fit/efficiency reason in apply mode. |
| Eligible target choices established | Compare by requirements and expected total work; report the eligibility source and distinguish estimates from measurements. |
| Only recognized aliases, generic documentation, or unavailable account information | Existing choice or `inherit` in frontmatter. Possible alternatives may be discussed separately as conditional options requiring eligibility evidence. |

Inheritance means the **future Claude Code main session's model**, not the Codex host model. Environment variables, invocation options, and policies may affect the actual model. Without runtime evidence, do not claim verified model use or cost savings.

Keep eligibility separate from capacity, price and measured performance. A dated quota incident is historical context, not a current constraint; a limit for one model does not prove another has spare or independent quota. A current target picker can establish selectable choices, but not successful invocation, remaining quota, price or savings. Choose by task fit among those eligible choices and leave these operational claims unverified. If eligibility itself is unknown, use the fallback above. Do not turn an old log or an unsupported expectation of lower cost into a model assignment.

### Reassess existing assignments

An ordinary configuration-improvement request includes model reassessment, even if role instructions are adequate. A model field alone is an existing assignment, not proof that the user permanently fixed it; do not guess who authored it. Separately stated user instructions/policies fixing that model still take precedence. If the constraint's meaning is genuinely conflicting, leave the affected change unresolved.

A confirmed suitable alternative and evidence of unnecessary capability, avoidable latency or expected cost can justify a model-only correction. Identify the actual mismatch and the supporting evidence. A generic preference for cheaper models, a new example, a model's age or a desire for diversity is not sufficient. Unknown cost does not justify a claimed saving. In proposal mode recommend only; in apply mode edit the model field minimally, preserving prose, tools, metadata, comments, language and byte formatting. Re-read before editing under the normal recovery procedure.

On repeat with the same candidate pool, constraints and adequate assignments, make no changes. Do not rotate among similarly suitable models. New evidence may justify a correction, which must be reported as a correction rather than a no-op.

### Explain model choices

Report decisions rather than offering a questionnaire. Summarize candidate groups/sources once, then for each Agent report **work requirement → selected model → leading alternative and rejection reason → unknowns**. Avoid an exhaustive Agent-by-model matrix. For example, where eligibility and workload evidence support it: "For this bounded extraction task I propose [eligible model]; [alternative] adds reasoning capacity the deterministic checks do not require. Cost is estimated, not measured." For an ambiguous cross-service design role, identify why a more capable eligible candidate is needed instead. Do not treat either example as a fixed family-to-role mapping. In proposal mode do not imply the assignment was installed.

Do not ask "Use inherit?", "Use the same model or choose by role?", or "Prioritize cost, speed, or quality?" as routine setup questions. Lack of an explicit preference is not a blocker. When the fallback is necessary, explain that the agent will follow the main Claude Code conversation's model when invoked, and why a separate assignment could not be verified. Mention the technical value only after its meaning if useful.

If a material unresolved model limit prevents a suitable assignment, ask one concrete ceiling question. Inspect the current target model and known constraints first; do not guess the current model or describe it as the most capable available model merely because it is in use. For example, when Sonnet is verified as the current Claude Code model and higher-capability choices are available:

- Question: "Should Sonnet, the model you are using now, be the highest-capability model assigned to subagents? I'll still choose lighter models for simpler work."
- "Stay within the current model's capability tier."
- "Allow a more capable available model when the work warrants it."

Translate examples into the user's language. This question sets a boundary, not the model for every agent; make individual assignments yourself within it. If no ceiling decision is needed, do not ask. If a ceiling was explicitly requested but the eligible models cannot be established, leave affected assignments unresolved instead of assuming `inherit` enforces it. A fixed ceiling requires suitable explicit assignments; `inherit` follows later main-session changes. Configuration alone is not enforcement against invocation overrides or runtime policies.

When this Skill runs in Codex, its current model (for example Astra) is not a Claude Code model or a valid ceiling for Claude configuration. Inspect the target Claude environment rather than copying that model or guessing a cross-provider equivalent. Do not imply that inheritance copies conversation history or permissions, guarantees a lower price, or overrides runtime model policies.

## Select tools

Explicitly list the tools needed by a new agent. `Read, Glob, Grep` illustrates a source-reading role; check actual host support separately. An agent with editing, shell, or external-write tools is not read-only.

For a test-running role, identify the supported shell tool, commands, working directory, and failure reporting. Instructions do not technically prevent other shell operations. Tool lists and permission modes do not grant new OS or account permissions. For unknown MCP tools, explain required functionality and what access remains to be checked.

Explain each distinct tool set using three separate facts; do not infer effective capability solely from an omitted tool:

| Layer | What the configuration supports saying |
|---|---|
| Listed interfaces | "This role lists Read/Glob/Grep" or "This worker also lists Edit/Write/Bash." An omitted Agent tool means that interface is not listed. |
| Behavioral rules | "The worker is instructed not to delegate, deploy, or access devices." With Bash or another execution-capable tool, separate commands/processes may still be possible; omission of Agent is not a technical no-delegation guarantee. |
| Observed enforcement | Only a tested target-runtime policy supports a claim that an operation was blocked. Without that evidence, say runtime enforcement is unverified. |

Use this distinction in proposals and final reports. For example: "The worker has shell access; no-delegation is an instruction, not a verified process restriction. The reviewer lists only reading interfaces; runtime enforcement has not been tested." Do not group a shell-enabled worker with a reader under "cannot spawn agents" merely because neither lists Agent. If a sentence says "cannot", "prevented", "read-only" or "enforced", check all listed execution paths and identify which layer supports it. Remove or qualify unsupported claims; do not silently change permission policies or remove needed tools to make the claim true.
