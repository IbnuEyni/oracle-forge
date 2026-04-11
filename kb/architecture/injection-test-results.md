# KB v1 Injection Test Results

**Author:** Nebiyou Abebe, BLOOM Team — Intelligence Officer
**Date:** 2026-04-09
**Method:** Each document was pasted into a fresh AI session with no prior
context. The test question was sent as a follow-up message. Responses were
evaluated against three criteria: correct (matches document), complete
(covers all key points), no hedging (answers directly).

**Test environment:** claude.ai — no project attached, no prior conversation.
Documents 1 and 2 were also tested in Claude Code CLI (noted where relevant).

---

## Document 1: claude-code-context-layers.md

**Test question:**
> How does Claude Code assemble its system prompt? What is each layer?

**Response received:**
> Claude Code assembles its system prompt in 5 layers, stacked in this order
> before every response:
>
> **Layer 1 — Static Instructions**
> Hard-coded, never-changing rules (always do X, never do Y).
> Source: src/constants/prompts.ts. These are the agent's non-negotiables.
>
> **Layer 2 — Dynamic Context**
> Runtime environment injected at session start: OS, shell, current directory,
> git branch. Source: src/context.ts. Changes every session based on
> where/how the agent is running.
>
> **Layer 3 — Tool Descriptions**
> Auto-generated text describing every registered tool. The model reads these
> descriptions to decide which tool to call — tool names alone are not enough.
> Source: src/Tool.ts. Vague or similar descriptions cause the wrong tool to
> be selected.
>
> **Layer 4 — Memory (CLAUDE.md / MEMORY.md)**
> Persistent project knowledge loaded before the user speaks.
> Three sub-levels, loaded in order:
> - User-level ~/.claude/CLAUDE.md
> - Project-level CLAUDE.md
> - Auto-memory MEMORY.md index
> Hard limit: 200 lines / 25 KB — anything beyond is silently dropped.
>
> **Layer 5 — User Context**
> Per-session config and preferences (overrides).
> Source: src/context.ts → getUserContext().
>
> The key takeaway from the document: the model's raw capability is less
> important than what you put in the context. The same model goes from 38%
> to full performance on DataAgentBench purely through proper context assembly
> across these 5 layers.

**Verdict: PASS**
- Correct: all 5 layers match the document including source file paths
- Complete: captured the 200-line / 25 KB hard limit and the 38% DAB figure
- No hedging: answered directly with no gaps filled from pretraining

---

## Document 2: claude-code-query-engine.md

**Test question:**
> What happens step by step when a user message is submitted to QueryEngine?

**Response received:**
> Based on the document:
>
> 1. Assemble system prompt — fetchSystemPromptParts() runs; auto-memory
>    prompt is injected if configured.
> 2. Process user input — slash commands are handled, permissions checked,
>    message normalized.
> 3. Call the model — query() in src/query.ts streams the response.
> 4. Yield messages — assistant text, tool_use blocks, and system status
>    messages are streamed back to the caller one turn at a time.
> 5. Execute tools — each tool_use block is checked via canUseTool(), then
>    run; the result is appended to mutableMessages. Denied tools are recorded
>    in permissionDenials[], not silently skipped.
> 6. Loop — if the model produced more tool_use blocks, go back to step 3.
>    The loop exits when stop_reason = end_turn or maxTurns is hit (which
>    yields a subtype: 'max_turns' system message).
>
> API errors that are retryable are handled automatically — the engine yields
> api_retry status messages and retries without user intervention.

**Verdict: PASS**
- Correct: exact sequence, correct field names (permissionDenials[],
  subtype: 'max_turns', stop_reason = end_turn)
- Complete: covered all 6 steps plus retry behavior
- No hedging: no hallucination, no added detail beyond the document

---

## Document 3: claude-code-memory.md

**Note:** First test run on Claude Code CLI failed — the model supplemented
the document with its own pretraining knowledge about the memory system,
missing the 25,000-byte cap and incorrectly stating truncation is silent.
The document was revised to make both limits unambiguous. Retest was
conducted on claude.ai with a clean session.

**Test question:**
> What are the hard limits on MEMORY.md and how does truncation work?

**Response received (claude.ai, after document revision):**
> **Two hard limits (both baked into the source code):**
>
> 1. **200 lines maximum.** If your index grows beyond that, the system
>    truncates it and appends a warning.
> 2. **25KB maximum** — a separate byte cap for edge cases where individual
>    lines are unusually long.
>
> **How truncation works:**
> When you hit either limit, the content is cut and a warning is appended to
> the truncated file. The warning is visible in the file itself. Claude sees
> the truncated content — memories past the cutoff are not loaded, and no
> signal is sent mid-session that truncation occurred.
>
> **Practical implications:**
> Keep MEMORY.md under 150 lines as a safety margin. Each entry should be
> one line (~150 chars). Detailed content goes in topic files, not inline
> in the index. The index is pointers only; topic files hold the knowledge.

**Verdict: PASS**
- Correct: both caps present (200 lines AND 25 KB), warning behavior correct
- Complete: covered the safety margin recommendation and index-as-pointers pattern
- No hedging: direct answer from document

**Document revision made:** Clarified that both line cap AND byte cap apply
independently, and that a warning is appended (not a silent drop).

---

## Document 4: claude-code-agent-spawning.md

**Test question:**
> What is the difference between fork mode and worktree mode for sub-agents?

**Response received:**
> **Fork mode** gives the child the parent's full conversation history and
> system prompt, and it operates in the same working directory as the parent.
> It's optimized for parallel analytical tasks — the children share
> byte-identical prompts for cache efficiency, report back a short summary,
> and are blocked from spawning further sub-agents.
>
> **Worktree mode** runs the child in a separate git worktree — same repo,
> but an isolated working copy. The child's file changes don't affect the
> parent's files or any sibling agent's files. You use it when parallel
> sub-agents need to write to disk without creating race conditions or merge
> conflicts.
>
> In short: fork mode shares the workspace and is best for read-heavy or
> analytical parallelism; worktree mode isolates the workspace and is best
> for write-heavy parallelism where file conflicts would otherwise be
> a problem.

**Verdict: PASS**
- Correct: shared workspace vs. isolated worktree distinction accurate,
  cache optimization noted, recursive fork prevention noted
- Complete: covered both modes, the use-case distinction, and the
  read vs. write parallelism summary
- No hedging: clean direct answer

---

## Summary

| Document | Test Question | Verdict | Notes |
|---|---|---|---|
| claude-code-context-layers.md | How does Claude Code assemble its system prompt? What is each layer? | PASS | First attempt |
| claude-code-query-engine.md | What happens step by step when a user message is submitted to QueryEngine? | PASS | First attempt |
| claude-code-memory.md | What are the hard limits on MEMORY.md and how does truncation work? | PASS | Failed first attempt on CLI; document revised; passed on claude.ai |
| claude-code-agent-spawning.md | What is the difference between fork mode and worktree mode for sub-agents? | PASS | First attempt |

**Overlap check:** All four documents were pasted together into a single
session. Asked "which documents mention MEMORY.md?" — only Document 3
(claude-code-memory.md) was identified. No duplication found.

**KB v1 status: COMPLETE -- all documents injection-tested and verified.**

---
---

# KB v2 Injection Test Results

**Author:** Intelligence Officers, BLOOM Team
**Date:** 2026-04-11
**Method:** Same as KB v1 -- each document pasted into a fresh claude.ai session with no prior context. Test question sent in the same message. Evaluated against: correct, complete, no hedging.

**Test environment:** claude.ai -- no project attached, no prior conversation.

---

## Document 5: unstructured-field-inventory.md

**Test question:**
> Based on the document above: A query asks "how many cancellations were pricing-related?" but there is no cancellation_reason column. What should the agent do?

**Response received:**
> The agent should check unstructured text fields -- specifically `customers.notes` and `interactions.transcript` -- using pattern matching (`ILIKE '%cancel%'` combined with `ILIKE '%pric%'` or `ILIKE '%expensive%'`). It should not report "data not available." The result should be qualified as approximate since it's based on keyword matching.

**Verdict: PASS**
- Correct: named the right fields (`customers.notes`, `interactions.transcript`)
- Complete: included pattern matching method and confidence caveat
- No hedging: answered directly from document, no pretraining fill

---

## Document 6: join-key-glossary.md

**Test question:**
> Based on the document above: How do I join user data between PostgreSQL and MongoDB when user_id is 'USR-1042' in PostgreSQL and userId is 1042 in MongoDB?

**Response received:**
> Strip the `USR-` prefix first, then cast to integer. Warned that `CAST('USR-1042' AS INTEGER)` would error if you skip the strip step. Also noted the field name mismatch (`user_id` vs `userId`).

**Verdict: PASS**
- Correct: strip prefix then cast, correct order of operations
- Complete: covered the pitfall (cast before strip = error) and field name casing
- No hedging: direct answer from document

---

## Document 7: dab-failure-categories.md

**Test question:**
> Based on the document above: What are the 4 DAB failure categories and why does the ill-formatted join keys category cause agent failures?

**Response received:**
> Named all 4 categories: multi-database integration, ill-formatted join keys, unstructured text transformation, domain knowledge gaps. Explained that join keys fail because the same entity has different ID formats across databases (e.g., `USR-1042` vs `1042`), so a raw join returns zero rows. Referenced the KB v2 glossary as the mitigation.

**Verdict: PASS**
- Correct: all 4 categories named, join key failure mechanism accurate
- Complete: included the zero-rows consequence and normalization fix
- No hedging: answered from document only

---

## KB v2 Summary

| Document | Test Question | Verdict | Notes |
|---|---|---|---|
| unstructured-field-inventory.md | Cancellation query with no structured column | PASS | First attempt |
| join-key-glossary.md | Join user data across PostgreSQL and MongoDB | PASS | First attempt |
| dab-failure-categories.md | Name 4 failure categories + explain join key failures | PASS | First attempt |

**KB v2 status (Nebiyou's sections): COMPLETE -- all 3 documents injection-tested and verified.**
