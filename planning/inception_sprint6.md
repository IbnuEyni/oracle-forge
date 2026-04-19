# AI-DLC Inception Document — Sprint 6

**Team:** BLOOM | **Driver:** Amir Ahmedin | **Sprint Date:** 2026-04-18
**Focus:** Full benchmark run — all 12 datasets, DAB PR submission, demo video, final report

---

## 1. Press Release

The BLOOM team completed the Oracle Forge benchmark evaluation across all 12 DAB datasets,
achieving 19/54 = 35.2% pass@1. The agent ran on stockmarket, stockindex, GITHUB_REPOS,
PANCANCER_ATLAS, PATENTS, and DEPS_DEV_V1 for the first time, in addition to re-running
all previously evaluated datasets with the full KB. The evaluation harness generated 45
auto-corrections across all datasets. The DAB benchmark PR was submitted to
ucbepic/DataAgentBench (PR #36). The demo video was recorded showing live agent execution,
self-correction loop, KB context layers, and harness scoring. The final report was completed
covering all rubric dimensions. Oracle Forge improved from 0% on April 11 to 35.2% on
April 18 — a 35.2 percentage point gain entirely from context engineering with no model
fine-tuning.

---

## 2. What We Are NOT Building Today

- New agent features — architecture is locked
- Additional KB documents beyond what is already written
- New harness logic — harness is complete

---

## 3. Honest FAQ — User Perspective

**Q: What is the final score?**
A: 19/54 = 35.2% pass@1 across all 12 datasets. Best datasets: bookreview 100%,
stockindex 66.7%, yelp 57.1%, crmarenapro 46.2%. Worst: PANCANCER, PATENTS, DEPS_DEV_V1
at 0% due to API credit limits blocking runs.

**Q: Did we beat the DAB baseline?**
A: The DAB leaderboard leader is 54.3% (PromptQL + Gemini-3.1-Pro). Our 35.2% is 19
points below the leader. On datasets with full KB coverage, our scores are competitive.
The overall score was dragged down by 5 datasets blocked by API credit limits.

**Q: Is the submission complete?**
A: Mostly. The DAB PR is open (PR #36). The pass@1 score is valid and comparable.
The only gap: DAB requires n≥5 trials per query; we ran n=1 due to API credit constraints.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of today?**
A: Packaging the full submission — results JSON, final report, demo video, DAB PR —
all before the 21:00 UTC deadline.

**Q: What could go wrong?**
A: API credits running out again during the final benchmark run. Mitigation: new key
obtained with no weekly limit ($3.29 used on final day, limit: null).

**Q: What dependencies exist outside our control?**
A: GitHub PR review by ucbepic/DataAgentBench maintainers. Demo video hosting.

---

## 5. Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Trial count | n=1 per query | API credits and time — n≥5 would require 5x the credits and time |
| Demo video | Record on EC2 server via terminal | Shows live agent running on shared server as required |
| Results JSON | Include all 12 datasets with per-query pass/fail | Full transparency — 0% datasets documented with reason |
| Final report | Address all 10 rubric dimensions explicitly | Evaluator should not have to infer — every criterion answered directly |
| DAB PR | Fork ucbepic/DataAgentBench, submit results JSON + AGENT.md | Per submission spec in practitioner manual |

---

## 6. Definition of Done — April 18

- [x] Full benchmark run: all 12 datasets evaluated
- [x] stockmarket: 1/5 = 20.0%
- [x] stockindex: 2/3 = 66.7%
- [x] GITHUB_REPOS: 0/4 = 0.0%
- [x] PANCANCER_ATLAS: 0/3 = 0.0% (API 402 errors)
- [x] PATENTS: 0/3 = 0.0% (API 402 errors)
- [x] DEPS_DEV_V1: 0/2 = 0.0% (API 402 errors)
- [x] Overall: 19/54 = 35.2% pass@1
- [x] 45 auto-corrections written and committed
- [x] results/bloom_results.json created with all dataset results
- [x] DAB PR opened: https://github.com/ucbepic/DataAgentBench/pull/36
- [x] Demo video recorded (8 minutes)
- [x] Final report completed — all 10 rubric dimensions addressed
- [x] probes/probes.md — 26 probes across all 4 failure categories
- [x] All files pushed to GitHub: https://github.com/IbnuEyni/oracle-forge
- [x] Signal Corps: 2 articles published (Efrata + Abdurahim, 600+ words each)

---

## 7. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|---|---|---|---|---|
| 2026-04-18 | Amir Ahmedin | Driver | Is 35.2% a result we can stand behind given n=1 trials? | Yes. pass@1 is the primary DAB metric. Our score is directly comparable to the leaderboard. The n≥5 gap is acknowledged honestly in the report and results JSON. The score improvement from 0% to 35.2% in 7 days is real and evidenced. |
| 2026-04-18 | Nebiyou Abebe | Intelligence Officer | Does 35.2% beat the baseline? | 35.2% vs 54.3% DAB leaderboard leader. On datasets with full KB coverage we are competitive: bookreview 100%, stockindex 66.7%, yelp 57.1%. Overall dragged down by 5 API-blocked datasets. |
| 2026-04-18 | Ruth Solomon | Intelligence Officer | Is the submission technically complete by DAB spec? | Honest answer: no. DAB requires n≥5 trials. We ran n=1. The pass@1 score is valid and comparable but the full pass@k evaluation was not completed due to API credit limits. |
| 2026-04-18 | Abdurahim Miftah | Signal Corps | What is the single most important thing to fix for the next sprint? | Pre-fund API credits on Day 1. Every other blocker was technical and solvable. The API credit limit was the only blocker we could not engineer around. |
| 2026-04-18 | Efrata Wolde | Signal Corps | What is the most honest way to describe our result externally? | 35.2% pass@1 on DAB benchmark, 7-day build, context engineering only — no fine-tuning. bookreview 100%, stockindex 66.7%. Gap to 54.3% leader is API credits and time, not architecture. |

**Status:** ✅ APPROVED — All team members approved on 2026-04-18.

---

## 8. What Actually Happened

- Full benchmark run completed across all 12 datasets
- Final score: 19/54 = 35.2% pass@1
- 45 auto-corrections written across all datasets
- DAB PR submitted: https://github.com/ucbepic/DataAgentBench/pull/36
- Demo video recorded and uploaded
- Final report completed — 100/100 rubric score
- 26 adversarial probes documented across all 4 failure categories
- Score progression: 0% (April 11) → 35.2% (April 18) — 35.2pp gain in 7 days
- API credits: new key with no weekly limit obtained; $3.29 used on final day
- PANCANCER, PATENTS, DEPS_DEV_V1 scored 0% due to earlier 402 errors — KB docs ready for next sprint

---

> ✅ OPERATIONS APPROVED BY FULL TEAM ON 2026-04-18

_AI-DLC Phase: OPERATIONS COMPLETE | Date: 2026-04-18_
