# AI-DLC Inception Document — Sprint 2
**Team:** BLOOM | **Driver:** Amir Ahmedin | **Sprint Date:** 2026-04-11
**Focus:** Model upgrade, first passing queries, corrections 001–002

---

## 1. Press Release

The BLOOM team has upgraded Oracle Forge from gemini-2.5-flash to gemini-3.1-pro-preview
via OpenRouter and achieved the first passing queries on the Yelp dataset. With schema hints
enabled, the agent now makes tool calls, queries MongoDB and DuckDB correctly, and returns
verifiable answers. Two queries pass (Q5, Q6). The corrections log has its first two entries
documenting the join key mismatch and the MongoDB dict-indexing failure.

---

## 2. What We Are NOT Building Today

- A high-scoring agent — today is about getting tool calls working and first corrections
- Bookreview or other datasets — Yelp only today
- KB v3 corrections injection — wiring that comes in Sprint 3

---

## 3. Honest FAQ — User Perspective

**Q: Why did we switch models?**
A: gemini-2.5-flash produced `MALFORMED_FUNCTION_CALL` on every query and never called
any tools. gemini-3.1-pro-preview resolved this immediately with `--use_hints`.

**Q: What does 28.6% mean?**
A: 2 out of 7 Yelp queries pass on first attempt. Q1 returns wrong number (3.86 vs 3.55),
Q2 returns wrong state (MO vs PA). These are data bugs, not model bugs — fixable with
corrections.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of today?**
A: Diagnosing why Q1 and Q2 return wrong answers when the agent is clearly querying the
right databases. The issue turns out to be BIGINT truncation and MongoDB 5-document limit.

**Q: What could go wrong?**
A: OpenRouter rate limits during multi-query runs. The `--use_hints` flag is essential —
without it the agent makes no tool calls regardless of model.

---

## 5. Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Model | gemini-3.1-pro-preview via OpenRouter | gemini-2.5-flash failed with MALFORMED_FUNCTION_CALL |
| Hints | Always use `--use_hints` | Without hints agent makes no tool calls |
| Corrections format | Structured markdown with query, what was wrong, fix, example | Readable by both humans and agent at injection time |

---

## 6. Definition of Done — April 11

- [x] Model upgraded to gemini-3.1-pro-preview via OpenRouter
- [x] Agent makes tool calls on all 7 Yelp queries
- [x] Score: 2/7 = 28.6% pass@1 (Q5, Q6 passing)
- [x] Correction 001 written: MongoDB dict-indexing TypeError
- [x] Correction 002 written: join key prefix mismatch `businessref_` vs `businessid_`
- [x] Score logged to `eval/score_log.jsonl`

---

## 7. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|---|---|---|---|---|
| 2026-04-11 | Amir Ahmedin | Driver | Q1 returns 3.86 instead of the correct value — is this a model error or a data error? | Data error. The `rating` column in DuckDB is BIGINT. AVG() on BIGINT truncates. Fix: CAST(rating AS FLOAT). Confirmed by running the query manually. |
| 2026-04-11 | Nebiyou Abebe | Intelligence Officer | Q2 returns wrong state — is the state field missing from MongoDB? | No dedicated state field. State is embedded in the `description` field as "City, ST ZIPCODE". Agent must extract it with regex. Added to hints. |

**Status:** ✅ APPROVED — Construction complete.

---

## 8. What Actually Happened

- 28.6% pass@1 on Yelp — first real score
- Root causes identified for Q1 (BIGINT truncation) and Q2 (MongoDB 5-doc limit + state extraction)
- Both fixes documented in corrections.md — ready to inject in Sprint 3

---

_AI-DLC Phase: CONSTRUCTION COMPLETE | Date: 2026-04-11_
