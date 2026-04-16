# AI-DLC Inception Document — Sprint 1
**Team:** BLOOM | **Driver:** Amir Ahmedin | **Sprint Date:** 2026-04-09
**Focus:** Infrastructure setup, KB v1 architecture, agent scaffold, first run attempt

---

## 1. Press Release

The BLOOM team has stood up Oracle Forge on the shared EC2 server. The agent connects to
MongoDB and DuckDB simultaneously, injects schema knowledge from the Knowledge Base before
every query, and runs against the Yelp dataset from DataAgentBench. The infrastructure is
live, the Knowledge Base v1 architecture documents are committed and injection-tested, and
the team has a working baseline to improve from.

---

## 2. What We Are NOT Building Today

- A passing agent — today is infrastructure and KB, not score optimisation
- A web UI — command line only
- A fine-tuned model — Gemini API as-is via OpenRouter

---

## 3. Honest FAQ — User Perspective

**Q: What can Oracle Forge do after today?**
A: Connect to MongoDB and DuckDB, receive a natural language question, and attempt to
answer it. It will not pass most queries yet — the KB and hints are not complete.

**Q: How do we know the infrastructure works?**
A: The agent runs without crashing. MongoDB restores the Yelp dataset. DuckDB connects.
The KB injector prints confirmation: `[Oracle Forge] KB injected: N chars added`.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of today?**
A: Getting the KB injection wired before the first LLM call without modifying the DAB
scaffold. Monkey-patching `DataAgent.__init__` is the chosen approach.

**Q: What could go wrong?**
A: gemini-2.5-flash may not make tool calls at all — this is an unknown until we run it.
PostgreSQL Docker container may not start cleanly on the EC2 instance.

**Q: What dependencies exist outside our control?**
A: Gemini API availability. EC2 server uptime managed by 10 Academy.

---

## 5. Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Agent base | DAB built-in DataAgent | Faster to extend; all 4 DB types already supported |
| KB injection | Monkey-patch `DataAgent.__init__` | No DAB scaffold modification needed |
| LLM | gemini-2.5-flash (initial) | Available API key; will upgrade if tool calls fail |
| PostgreSQL | Docker container `postgres-dab` | System-level install broken on EC2 |

---

## 6. Definition of Done — April 9

- [x] EC2 server accessible via `ssh trp-bloom`
- [x] DataAgentBench repo cloned, venv created, dependencies installed
- [x] MongoDB loaded with Yelp dataset (100 business docs confirmed)
- [x] DuckDB Yelp file accessible
- [x] `oracle_run.py` and `kb_injector.py` deployed on server
- [x] KB v1 architecture: 4 documents committed and injection-tested (all PASS)
- [x] KB v2 domain: 3 documents committed and injection-tested (all PASS)
- [x] First agent run attempted on Yelp Q1 — result logged

---

## 7. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|---|---|---|---|---|
| 2026-04-09 | Nebiyou Abebe | Intelligence Officer | Have we confirmed the join keys and formats in KB, or are we assuming they match? | Confirmed through actual agent failures. Agent failed Q1, Q2, Q4, Q7. Inspected tool call logs, confirmed `businessid_` vs `businessref_` mismatch. Added resolution pattern to hints — queries started passing. Gap: only confirmed for Yelp. |
| 2026-04-09 | Ruth Solomon | Intelligence Officer | Does the agent correctly route queries requiring both PostgreSQL and MongoDB? | Not yet tested — honest gap. Yelp uses MongoDB + DuckDB only. |
| 2026-04-09 | Abdurahim Miftah | Signal Corps | What changes are needed to support a second dataset? | Hints file + KB domain doc per dataset. Agent code does not change. |
| 2026-04-09 | Efrata Wolde | Signal Corps | If Gemini API goes down during final submission, what is our fallback? | No fallback yet. Action: add OpenRouter backup key before final run. |

**Status:** ✅ APPROVED — Construction begins.

---

## 8. What Actually Happened

- gemini-2.5-flash produced `MALFORMED_FUNCTION_CALL` errors and made no tool calls on any query
- Score: 0/7 = 0% — all queries failed with `no_tool_call` or `max_iterations`
- KB injection confirmed working: `[Oracle Forge] KB injected: 16044 chars`
- Decision logged: upgrade to gemini-3.1-pro-preview in Sprint 2

---

_AI-DLC Phase: CONSTRUCTION COMPLETE | Date: 2026-04-09_
