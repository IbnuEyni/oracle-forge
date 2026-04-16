# AI-DLC Inception Document — Sprint 3
**Team:** BLOOM | **Driver:** Amir Ahmedin | **Sprint Date:** 2026-04-13
**Focus:** KB injection wired, corrections injected, 57.1% breakthrough on Yelp

---

## 1. Press Release

The BLOOM team has wired all three context layers into Oracle Forge and achieved 57.1%
pass@1 on the Yelp dataset — beating the 38% DAB frontier model baseline. The corrections
log from Sprint 2 is now injected at session start via `kb_injector.py`. The BIGINT CAST
fix and MongoDB limit fix resolved Q1 and Q2. The agent now passes 4 of 7 Yelp queries
on first attempt. The full team approved Construction phase at today's mob session.

---

## 2. What We Are NOT Building Today

- Multi-dataset coverage — Yelp only, bookreview starts in Sprint 4
- Adversarial probes — that is Sprint 4 work
- Demo video — final sprint

---

## 3. Honest FAQ — User Perspective

**Q: What changed between 28.6% and 57.1%?**
A: KB Layer 3 (corrections.md) was injected for the first time. The CAST fix resolved Q1.
The MongoDB limit=10000 fix resolved Q2. The join key pattern resolved Q3. Three corrections,
three new passing queries.

**Q: Is 57.1% the real score?**
A: On Yelp yes. Across all 54 DAB queries it will be lower — maybe 20-30%. Yelp is one
dataset and we have tuned hints for it. Other datasets need their own hints and KB docs.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of today?**
A: Confirming that the score improvement is caused by KB injection and not by random model
variation. We ran with and without corrections to isolate the effect.

**Q: What could go wrong?**
A: Gemini API quota exhaustion during the full 7-query run. Q4, Q5, Q7 remain inconsistent
— nested attribute parsing is not yet solved.

---

## 5. Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| KB injection timing | Before first LLM call via monkey-patch | Corrections must be present from turn 1, not added mid-session |
| Hints strategy | Structural only, no answer-specific hints | Answer-specific hints caused overfitting — reverted after one test |
| Iterations | 20 | 10 was insufficient for complex multi-DB queries |

---

## 6. Definition of Done — April 13

- [x] KB injection confirmed: 16044 chars injected per run
- [x] Correction 003 written: BIGINT CAST + MongoDB limit=10000
- [x] Score: 4/7 = 57.1% pass@1 on Yelp (Q1, Q2, Q3, Q6 passing)
- [x] Score logged to `eval/score_log.jsonl`
- [x] Inception approved by full team — Construction phase begins
- [x] bookreview hints file created for Sprint 4

---

## 7. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|---|---|---|---|---|
| 2026-04-13 | Amir Ahmedin | Driver | Our score is 57% on Yelp. What do we think our real pass@1 will be across all 54 queries? | Honestly lower — maybe 20-30%. Yelp is one dataset and we have tuned hints for it. The 57% proves the approach works. Week 9 is about scaling it to all 12 datasets. |
| 2026-04-13 | Nebiyou Abebe | Intelligence Officer | Is the score improvement from KB injection or from model randomness? | Confirmed from KB injection. We ran the same queries without corrections.md injected and got 28.6%. With corrections: 57.1%. The delta is the corrections. |
| 2026-04-13 | Ruth Solomon | Intelligence Officer | Q4, Q5, Q7 are still failing — what is the root cause? | Q4 and Q7 require parsing the MongoDB `attributes` nested dict. The agent does not handle nested dicts reliably. Q5 is model-dependent. These are Sprint 4 targets. |
| 2026-04-13 | Abdurahim Miftah | Signal Corps | Can we claim we beat the DAB baseline in our posts? | Yes — 57.1% on Yelp beats the 38% frontier model baseline from the DAB paper. We should be honest that this is one dataset, not all 54 queries. |
| 2026-04-13 | Efrata Wolde | Signal Corps | What is the plan if we can't get above 38% across all 54 queries? | The harness score log showing improvement from 0% to 57.1% is the real deliverable. Even if the full-benchmark score is lower, the engineering approach is evidenced. |

**Status:** ✅ APPROVED — All team members approved on 2026-04-13. Construction phase begins.

---

## 8. What Actually Happened

- 57.1% pass@1 on Yelp — beats 38% DAB baseline
- KB injection confirmed as the cause of improvement (isolated test)
- Q4, Q5, Q7 failures diagnosed: nested attribute parsing, model inconsistency
- bookreview hints file created — ready for Sprint 4

---

> ✅ CONSTRUCTION APPROVED BY FULL TEAM ON 2026-04-13

_AI-DLC Phase: CONSTRUCTION COMPLETE | Date: 2026-04-13_
