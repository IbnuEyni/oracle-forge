# Claude Code: System Prompt Assembly (5 Layers)

Before every response, Claude Code assembles a system prompt in this order:

## Layer 1 — Static Instructions
Hard-coded behavioral rules (never do X, always do Y).
Source: `src/constants/prompts.ts` → `getSystemPrompt()`

FOR OUR AGENT: Put Oracle Forge's non-negotiable rules here — always validate
SQL before execution, never return raw credentials, always cite source table.

## Layer 2 — Dynamic Context
Runtime environment injected at session start: OS, shell, git branch, cwd.
Source: `src/context.ts` → `getSystemContext()` + `getUserContext()`

FOR OUR AGENT: Inject active database name, schema version, and current user
role here so the agent always knows which data environment it is operating in.

## Layer 3 — Tool Descriptions
Auto-generated descriptions for every registered tool. The model reads these
to select which tool to call — it does NOT rely on tool names alone.
Source: `src/Tool.ts`, registered in `fetchSystemPromptParts()`

FOR OUR AGENT: Each MCP Toolbox database connection must be a named tool with
a precise, distinct description. If two tools have vague descriptions, the
agent will pick the wrong one.

## Layer 4 — Memory (CLAUDE.md / MEMORY.md)
Persistent project knowledge loaded before the user speaks.
Source: `src/memdir/memdir.ts`
Three levels (loaded in this order):
- User-level: `~/.claude/CLAUDE.md`
- Project-level: `CLAUDE.md` in project root
- Auto-memory: `MEMORY.md` index (max 200 lines / 25 KB before truncation)

FOR OUR AGENT: The KB documents you inject live here. Keep MEMORY.md under
200 lines or entries after line 200 are silently dropped.

## Layer 5 — User Context
Config, preferences, session-level overrides.
Source: `src/context.ts` → `getUserContext()`

FOR OUR AGENT: Use this layer for per-session state: active analyst ID, query
budget, output format preference.

---

KEY INSIGHT: Intelligence comes from context assembly, not model capability.
The same model scores 38% on DataAgentBench with a bare prompt. A complete
5-layer context is the entire engineering intervention.
