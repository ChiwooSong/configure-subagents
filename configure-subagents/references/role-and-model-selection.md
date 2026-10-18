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

1. Inspect existing settings and honor explicit model choices, ceilings, and other constraints already provided. Preserve an existing choice when justified; do not ask for preferences the user has already supplied.
2. Establish model eligibility before optimizing task fit. Use non-secret evidence from the target environment: an explicit user model choice/allowlist, applicable provider or managed policy, a current target model picker, or an observed successful target-model invocation. Record the source and its limits. A model name accepted by this validator, a documentation example, the host's identity, or an old quota log does not establish that a different model is available in the target account. Do not invent a capability ranking, prices, or equivalence between providers.
3. Assess each role's task difficulty, ambiguity, context needs, and consequences of mistakes. Select a model expected to meet its requirements without unnecessary cost or latency; use stronger verified reasoning capabilities when the work warrants them. Make this judgment yourself rather than asking the user to choose quality versus cost or speed. Explain each assignment with project evidence; don't manufacture different model assignments just to show variety.
4. Consider situations as well as role names. A routine review and a high-risk architectural review may need different capabilities. When useful, define distinct invocation conditions or recommend an explicit model override supported by the target environment. Do not claim that a static agent definition implements automatic model routing or escalation.
5. If a suitable explicit target model cannot be established, preserve an existing model setting or use `model: inherit` for a new Agent. This applies to proposal code blocks and candidate files as well as installed files. Do not put an unverified alias in frontmatter and defer fallback until it fails. Explain the missing eligibility evidence and mark role-specific model optimization unverified; do not ask the user to approve this routine fallback. Once eligible models are known, choose among them yourself by task fit; lack of price or quota measurements alone does not force inheritance. Also honor an explicit request to follow the main session.

| Evidence | Configuration decision |
|---|---|
| Existing user choice or applicable explicit model constraint | Preserve it unless the requested change and relevant evidence justify a correction; do not claim runtime access was tested. |
| Eligible target choices established | Assign by the role's actual difficulty and consequences of mistakes; report the eligibility source. |
| Only recognized aliases, generic documentation, or unavailable account information | Existing choice or `inherit` in frontmatter. Possible alternatives may be discussed separately as conditional options requiring eligibility evidence. |

Inheritance means the **future Claude Code main session's model**, not the Codex host model. Environment variables, invocation options, and policies may affect the actual model. Without runtime evidence, do not claim verified model use or cost savings.

Keep eligibility separate from capacity, price and measured performance. A dated quota incident is historical context, not a current constraint; a limit for one model does not prove another has spare or independent quota. A current target picker can establish selectable choices, but not successful invocation, remaining quota, price or savings. Choose by task fit among those eligible choices and leave these operational claims unverified. If eligibility itself is unknown, use the fallback above. Do not turn an old log or an unsupported expectation of lower cost into a model assignment.

### Explain model choices

Report the decisions rather than offering a model-selection questionnaire. For example: "I'll assign a lower-cost model to routine information extraction and a stronger reasoning model to complex design review, based on the models available in this Claude Code environment." Use actual verified model names and role-specific reasons when known. In proposal mode, describe proposed assignments rather than implying that settings have been applied.

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
