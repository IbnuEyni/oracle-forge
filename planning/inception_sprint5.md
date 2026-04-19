# AI-DLC Inception Document — Sprint 5

**Team:** BLOOM | **Driver:** Amir Ahmedin | **Sprint Date:** 2026-04-17
**Focus:** Full benchmark expansion — KB schemas for 5 new datasets, crmarenapro, googlelocal, agnews

---

## 1. Press Release

The BLOOM team expanded Oracle Forge from 2 datasets to 7, adding KB schema documents for
music_brainz_20k, DEPS_DEV_V1, GITHUB_REPOS, PANCANCER_ATLAS, and PATENTS. The agent ran
against crmarenapro (13 queries), googlelocal (4 queries), and agnews (4 queries) for the
first time. crmarenapro achieved 46.2% pass@1 (6/13) on first run with full KB injection.
bookreview reached 100% pass@1 (3/3) — the first perfect dataset score. The self-correction
loop generated 20+ new corrections across all new datasets. Combined score across 7 datasets:
17/44 = 38.6% pass@1, matching the DAB frontier model baseline.

---

## 2. What We Are NOT Building Today

- Full 54-query run — that is Sprint 6 (April 18)
- Demo video — Sprint 6
- DAB GitHub PR — Sprint 6
- Harness changes — architecture is locked

---

## 3. Honest FAQ — User Perspective

**Q: Why add 5 new KB schema documents in one day?**
A: The benchmark has 12 datasets. Without dataset-specific KB docs, the agent has no
knowledge of field names, join key formats, or known failure patterns for those datasets.
Adding schema docs before running queries is the correct order — we learned this from
Yelp where we ran first and added KB docs after failures.

**Q: What does crmarenapro 46.2% mean?**
A: 6 out of 13 queries passed on first attempt. crmarenapro is the largest dataset in DAB
(13 queries) and uses Salesforce CRM data across PostgreSQL and DuckDB. 46.2% on first run
with KB injection is strong evidence the architecture generalises to enterprise CRM data.

**Q: Why did bookreview reach 100%?**
A: The corrections from Sprint 4 (join key normalization, field name verification) were
injected at session start. The agent applied the fixes automatically — no code change required.
This is the self-learning loop working as designed.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of today?**
A: Writing 5 KB schema documents that pass injection tests before running any queries.
Each document must be specific enough to guide the agent without leaking answer values.

**Q: What could go wrong?**
A: API credit limits. The OpenRouter weekly limit was hit during the previous run.
Mitigation: monitor usage after every 5 queries, pause if approaching limit.

**Q: What dependencies exist outside our control?**
A: OpenRouter API credits. EC2 server uptime. MongoDB restore time per query (~30s).

---

## 5. Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| KB docs before queries | Write schema docs first, run queries second | Learned from Yelp — running without KB docs wastes API credits on predictable failures |
| crmarenapro first | Run largest dataset first | 13 queries gives most signal about architecture generalisation |
| Iterations | 20 per query | Confirmed sufficient in Sprint 4; increasing to 30 for complex queries |
| New dataset KB format | Same structure as existing docs | Consistency — kb_injector.py loads all domain docs in same priority order |

---

## 6. Definition of Done — April 17

- [x] KB schema docs written and injection-tested for all 5 new datasets
- [x] schema-crmarenapro.md — INJECTION TEST: PASS
- [x] schema-music-brainz.md — INJECTION TEST: PASS
- [x] schema-deps-dev.md — INJECTION TEST: PASS
- [x] schema-github-repos.md — INJECTION TEST: PASS
- [x] schema-pancancer.md — INJECTION TEST: PASS
- [x] schema-patents.md — INJECTION TEST: PASS
- [x] crmarenapro: 6/13 = 46.2% pass@1
- [x] bookreview: 3/3 = 100% pass@1
- [x] googlelocal: 1/4 = 25.0% pass@1
- [x] agnews: 1/4 = 25.0% pass@1
- [x] 20+ new auto-corrections written
- [x] All KB docs pushed to GitHub
- [x] Server synced via git pull

---

## 7. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|---|---|---|---|---|
| 2026-04-17 | Amir Ahmedin | Driver | Are we confident the new KB schema docs won't leak answer values? | Yes. Each doc describes field names, join key formats, and known failure patterns only. No query-specific expected values. Injection tests confirm the agent answers structural questions correctly from the doc alone. |
| 2026-04-17 | Nebiyou Abebe | Intelligence Officer | Why is crmarenapro scoring 46.2% when we just added the KB doc today? | The schema doc gave the agent the Salesforce ID formats and table routing. Q6, Q9, Q11, Q13 passed because the agent knew which PostgreSQL table held the entity it needed. Without the doc, it would have queried the wrong table. |
| 2026-04-17 | Ruth Solomon | Intelligence Officer | bookreview hit 100% — is that reliable or a lucky run? | Reliable. The corrections from Sprint 4 are structural fixes (join key normalization, field name verification). They apply to every bookreview run. The agent reads them before its first tool call. |
| 2026-04-17 | Abdurahim Miftah | Signal Corps | What should we post about today? | bookreview 100% and crmarenapro 46.2% on first run. The claim: KB injection generalises across database types and domains. |
| 2026-04-17 | Efrata Wolde | Signal Corps | Are we on track for the final submission tomorrow? | Yes. 7 datasets running. 5 more need KB docs and runs. API credits are the main risk. |

**Status:** ✅ APPROVED — All team members approved on 2026-04-17.

---

## 8. What Actually Happened

- 6 new KB schema documents written, injection-tested, and committed
- bookreview: 3/3 = 100% — first perfect dataset score
- crmarenapro: 6/13 = 46.2% — largest dataset, first run
- googlelocal: 1/4 = 25.0%
- agnews: 1/4 = 25.0%
- 20+ new auto-corrections generated
- API credits hit limit mid-run — new key obtained for Sprint 6
- Combined score across 7 datasets: 17/44 = 38.6%

---

> ✅ CONSTRUCTION APPROVED BY FULL TEAM ON 2026-04-17

_AI-DLC Phase: CONSTRUCTION COMPLETE | Date: 2026-04-17_
