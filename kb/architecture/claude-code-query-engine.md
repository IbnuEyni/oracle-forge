# Claude Code: QueryEngine — Stateful Orchestrator

Source: `src/QueryEngine.ts` (1,297 lines)
Entry point: `async *submitMessage()` — an async generator that yields
`SDKMessage` objects turn-by-turn.

## The Core Loop

Every user message triggers this sequence:

1. **Assemble system prompt** — calls `fetchSystemPromptParts()`, injects
   memory mechanics prompt if auto-memory is configured.
2. **Process user input** — slash commands, permission checks, message
   normalization.
3. **Call the model** — streams response via `query()` in `src/query.ts`.
4. **Yield messages** — streams assistant text, tool_use blocks, and system
   status messages back to the caller via `yield`.
5. **Execute tools** — for each `tool_use` block, invokes `canUseTool()` then
   runs the tool; result is appended to `mutableMessages`.
6. **Loop** — if the model emits more `tool_use` blocks, repeat from step 3.
   Loop exits when `stop_reason = end_turn` or `maxTurns` is reached.

## Retry Behavior

API errors that are retryable trigger `api_retry` system messages (yielded to
caller with `attempt`, `max_retries`, `retry_delay_ms`). The engine retries
automatically without user intervention.

## Permission Model

Every tool call passes through `canUseTool()`. Denials are tracked in
`permissionDenials[]` and reported in the SDK response. The engine does NOT
silently skip denied tools — it records and surfaces them.

## maxTurns Guard

Configurable via `QueryEngineConfig.maxTurns`. When hit, the engine yields a
system message with `subtype: 'max_turns'` and halts. Default is not fixed in
QueryEngine itself — callers set it (FORK_AGENT sets 200).

---

FOR OUR AGENT: Oracle Forge's self-correction loop maps directly to this
pattern. If a SQL query fails, the agent receives the error as a tool_result,
then loops back to the model with the error in context. No special retry code
needed — the tool loop handles it. Set maxTurns high enough for multi-step
analytical queries (suggest 50+).
