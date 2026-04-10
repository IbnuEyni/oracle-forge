# Claude Code: Memory System

Source: `src/memdir/memdir.ts`

## How Memory Loads

On every `submitMessage()` call, `loadMemoryPrompt()` is invoked. It reads
`MEMORY.md` as an index, then loads the files it points to.

Two hard limits enforced in code — BOTH must be satisfied:
- **Line cap: 200 lines** — content is truncated at line 200; a warning is appended to the truncated content
- **Byte cap: 25,000 bytes** — if the file exceeds 25 KB, content is cut at the last newline before the cap; a warning is appended
- Whichever limit hits first applies. A file with 150 long lines can hit the byte cap before the line cap.

## Memory File Format

Each memory file uses YAML frontmatter:

```
---
name: topic name
description: one-line hook used to judge relevance
type: user | feedback | project | reference
---

Content here.
```

`MEMORY.md` is an index of one-liners pointing to topic files:
```
- [Title](file.md) — one-line description
```

## Three Persistence Levels

| Level | Location | Scope |
|---|---|---|
| User | `~/.claude/CLAUDE.md` | All projects |
| Project | `CLAUDE.md` in project root | This project |
| Auto-memory | `MEMORY.md` + topic files in `.claude/memory/` | This project |

Session-level state (conversation history) is NOT written to disk — it
lives only for the duration of one session.

## Auto-Memory Path Override

When `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` env var is set, memory mechanics
are injected into agent sessions that use a custom system prompt. This is
how SDK-spawned sub-agents get memory awareness.

---

FOR OUR AGENT: Keep `MEMORY.md` under 150 lines with a safety margin.
Each KB document should be its own topic file, not inlined into MEMORY.md.
Schema descriptions, table glossaries, and query patterns belong in topic
files — not in the 200-line index.
