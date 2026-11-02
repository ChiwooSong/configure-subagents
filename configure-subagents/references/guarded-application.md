# Guarded Agent file application

The host AI authors and reviews candidates. `apply_agents.py` validates and applies file changes; it does not judge role correctness, authenticate user intent, constrain another program's writes or provide a sandbox. Use only for an authorized application request. Proposal/validation-only work never calls prepare/apply.

## Before creating a task

Identify the selected project and target (`claude`, `codex`, `both`), the concrete correction, evidence, and exact existing files to preserve/remove. If no correction is justified, validate in place without creating candidates, backups or task records. Reassessment can justify a minimal model-only edit; optional elaboration cannot.

Show the project-specific evidence summary before prepare. The task storage is `<project-root>/.configure-subagents-work/<ID>/`, outside both discovery trees. It must lie within the permitted work scope; if unavailable, leave application unapplied. Quote paths and use the same approved Python environment as the selected checker. No global dependency installation is implied.

## Prepare, author, compare, check, apply

```text
python "<skill-dir>/scripts/apply_agents.py" prepare --project-root "<project-root>" --target both
```

Prepare returns a task ID plus `candidate_paths` and `backup_paths` for the selected targets. It copies the whole existing trees byte-for-byte, retaining non-Agent files. Edit only necessary Agent files under those candidate paths; never edit originals, manifests or journals. Claude uses `.md`, Codex `.toml`. Leave unchanged files and directories in the complete candidates.

For removal explicitly included in the user's request, add repeated pairs to **prepare**:

```text
--allow-delete claude old-reviewer.md --allow-delete codex old-reviewer.toml
```

Paths are relative to that target's Agent tree, including subfolders. The helper checks the allowlist, not the conversation: supply it only when actually authorized. Renaming/consolidation includes creating/updating the destination and deleting each authorized old file; an improvement request alone does not authorize removal.

Preserve useful prose, custom fields/comments, language, explicit constraints, encoding/BOM and newline/final-newline conventions. Do not reserialize frontmatter/TOML. Changed mixed/CR-only or unverified encodings are refused. Codex BOM is unsupported. Propose format conversion separately rather than bypassing a refusal.

Reread the actual candidate and relevant source passages for the project-specific cross-review, resolve contradictions and show its concrete outcome. Then:

```text
python "<skill-dir>/scripts/apply_agents.py" check --project-root "<project-root>" --target both --transaction "<ID>"
python "<skill-dir>/scripts/apply_agents.py" apply --project-root "<project-root>" --target both --transaction "<ID>" --candidate-digest "<digest-from-check>"
```

Check is read-only and returns changes, diagnostics and the complete candidate digest. Apply requires exactly that digest, rechecks source identities/hashes/mtimes, validates every selected tree before writing, preserves identical files, and verifies installed bytes. For both, one target's error prevents the first target from being written. Errors in existing unchanged Agents are not silently waived; correct them only within scope or leave the task unapplied. Warnings remain visible and are not a security approval.

After a conflict, reread current sources and reassess in a fresh task; never alter the record or repeatedly retry the same stale plan. If candidate content changes after check, repeat the actual review and check before applying. If the tool is missing, refused, or unavailable, report the unperformed application; do not substitute direct installed-file edits or broad Git reset/checkout commands.

## Results and recovery

JSON `schema_version: 1` includes `operation`, `target`, `transaction`, `status`, `exit_code`, `changes`, `diagnostics`, and `unrecovered`. Prepare also returns candidate/backup paths; check/apply return `candidate_digest`. Originals and the journal remain in the reported task directory. Exit 0 is completed preparation/check/application or unchanged success; 1 is a rejected scope, candidate or conflict; 2 is unavailable execution or failed/recovery-required application. Do not conflate preparation/check success with application.

On an application error, only outputs still matching this task's recorded identity and bytes are withdrawn. Moved originals are restored only when the recovery path is unchanged and the destination is unoccupied. Concurrent, partial or uncertain outputs are retained and reported as `recovery_required`. Inspect backups and unresolved paths; do not overwrite another writer or auto-reuse a failed/incomplete task. Forced termination can leave partial application; backups/journal support manual recovery, not guaranteed automatic recovery.

A completed task can be replayed unchanged only if installed trees and candidates still match its receipt; replay does not rewrite files or task records. Ordinary fresh-session reassessment still starts from current evidence and should skip prepare when no change is justified. Multiple writes are not an atomic filesystem transaction, and path rechecks are not isolation against a hostile concurrent writer.

Report actual changed/preserved/removed files, static warnings, measured formatting, original-copy locations, and any unavailable or recovery-required work. Keep semantic review, file preservation, host execution and generated-Agent invocation as separate evidence.
