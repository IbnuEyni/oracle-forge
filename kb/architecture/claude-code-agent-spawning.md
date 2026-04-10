# Claude Code: Sub-Agent Spawning

Source: `src/tools/AgentTool/forkSubagent.ts`, `src/tools/AgentTool/loadAgentsDir.ts`

## Two Spawn Modes

### Fork Mode (implicit)
Triggered by calling the Agent tool without a `subagent_type`.
Feature-flagged via `FORK_SUBAGENT`.

The child receives:
- Parent's full conversation history
- Parent's exact system prompt (byte-identical, for prompt cache reuse)
- A per-child directive appended as the final user message
- `permissionMode: 'bubble'` — permission prompts surface to parent terminal
- `model: 'inherit'` — same model as parent
- `maxTurns: 200`

Child rules (injected via `FORK_BOILERPLATE_TAG`):
- Do NOT spawn further sub-agents (recursive fork prevention)
- Do NOT converse — use tools silently, report once at end
- Report must begin with `Scope:`, stay under 500 words
- Commit file changes before reporting; include commit hash

Prompt cache optimization: all fork children share byte-identical tool_result
placeholders (`'Fork started — processing in background'`) so only the final
directive text differs. This maximizes cache hits across parallel forks.

### Worktree Mode (isolated)
Child runs in a separate git worktree — same repo, different working copy.
Child is told its worktree path and the parent's original cwd.
Changes are isolated and do not affect parent's files.

Use when: parallel tasks that modify files and must not conflict with each other.

## Guard: No Recursive Forking
`isInForkChild()` checks conversation history for `FORK_BOILERPLATE_TAG`.
If found, fork attempts are rejected at call time.

## Coordinator Mode
Mutually exclusive with fork mode. Coordinator has its own orchestration model
and owns the delegation role when enabled.

---

FOR OUR AGENT: Use fork mode for parallel analytical sub-tasks (e.g., query
three databases simultaneously). Use worktree mode if sub-agents need to write
results to files without race conditions. Never nest fork children — structure
tasks so the parent orchestrates and leaf agents execute.
