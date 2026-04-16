# Oracle Forge — BLOOM Team Presentation

**TRP1 FDE Programme · April 2026 · Weeks 8–9**

---

## The Mission

Build a production-grade natural language data analytics agent evaluated on **DataAgentBench (DAB)** — the first benchmark for realistic enterprise data workloads.

- **54 queries** across **12 datasets** and **9 domains**
- **4 database types**: PostgreSQL, MongoDB, SQLite, DuckDB
- **Best frontier model baseline**: 38% pass@1 (Gemini 3 Pro)
- **Our target**: Beat 38% through context engineering

---

## Architecture

```
User Natural Language Query
           │
           ▼
┌─────────────────────────────────────┐
│         Oracle Forge Agent          │
│                                     │
│  ┌─────────────────────────────┐    │
│  │   Layer 1: Schema/Metadata  │    │
│  │   (db_description_withhint) │    │
│  ├─────────────────────────────┤    │
│  │   Layer 2: Domain Knowledge │    │
│  │   (kb/domain/ documents)    │    │
│  ├─────────────────────────────┤    │
│  │   Layer 3: Corrections Log  │    │
│  │   (kb/corrections/)         │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │   DAB DataAgent (base)      │    │
│  │   + kb_injector.py patch    │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │   Docker Sandbox            │    │
│  │   (python-data:3.12)        │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
           │
           ▼
  Verified Answer + Query Trace
```

**LLM:** google/gemini-3.1-pro-preview via OpenRouter  
**Server:** bloom.10academy.org (AWS EC2)  
**Infrastructure:** tenai-infra (Tailscale mesh, tmux, git worktrees)

---

## What Each Role Built

### Driver — Amir Ahmedin

**Infrastructure**

- Shared AWS EC2 server with all 5 team accounts
- tenai-infra installed (`make onboard`) — Tailscale mesh, shared tmux session
- PostgreSQL (Docker, auto-restart) + MongoDB (system service)
- Docker sandbox image `python-data:3.12`

**Custom Agent**

- `agent/oracle_run.py` — wrapper that runs DAB agent with KB injection
- `agent/kb_injector.py` — injects all 3 context layers at session start (16,044 chars)
- `agent/tools.yaml` — MCP Toolbox config for all 4 database types
- OpenRouter integration — Claude, GPT-4o, Gemini via single API key
- `agent/AGENT.md` — agent context file loaded at session start

**Evaluation Harness**

- `eval/harness.py` — runs queries, validates against ground truth, produces pass@1
- Score log with 4 data points showing progression

**Key Technical Discoveries**
| Bug | Impact | Fix |
|-----|--------|-----|
| DuckDB `rating` stored as BIGINT | `AVG(rating)` returns wrong integer-truncated result | `AVG(CAST(rating AS FLOAT))` |
| MongoDB default query limit = 5 | Agent missed 3 of 8 Indianapolis businesses | Set `limit: 10000` in all queries |
| OpenRouter proxy behavior | Same model scores differently via proxy vs direct API | Use gemini-3.1-pro-preview via OpenRouter |

---

### Intelligence Officers — Nebiyou Abebe + Ruth Solomon

**Knowledge Base — 15+ documents across 4 directories**

| Directory          | Contents                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `kb/architecture/` | Claude Code memory system, context layers, agent rules, injection test results                        |
| `kb/domain/`       | DAB failure categories, join key glossary (businessid* vs businessref*), unstructured field inventory |
| `kb/evaluation/`   | Injection test rubric, pass@1 scoring explanation                                                     |
| `kb/corrections/`  | 3 corrections logged from real agent failures                                                         |

**Corrections Log (3 entries)**

1. List index error — agent treating MongoDB results as nested lists
2. Join key mismatch — `businessid_` prefix vs `businessref_` prefix
3. BIGINT CAST bug + MongoDB limit bug (discovered Week 9)

**KB Quality Standards**

- Every document injection-tested before committing
- CHANGELOGs maintained in each directory
- KB wired into agent — injected at every session start

---

### Signal Corps — Abdurahim Miftah + Efrata Wolde

**Posts Live**
| Date | Member | Platform | Topic |
|------|--------|----------|-------|
| April 13 | Abdurahim | LinkedIn | Cross-database key clarity in enterprise data |
| April 14 | Abdurahim | X | Context engineering across databases |
| April 9 | Efrata | Reddit (r/MachineLearning) | Enterprise data integration challenges |

---

## Score Progression

### Phase 1 — Direct Gemini API (April 11–13)

Initial testing used direct Gemini API (`generativelanguage.googleapis.com`).

| Run      | Date     | Model                                   | Score           | Notes         |
| -------- | -------- | --------------------------------------- | --------------- | ------------- |
| Baseline | April 11 | gemini-2.5-flash, no hints              | 0/7 = **0%**    | No tool calls |
| Run 2    | April 11 | gemini-3.1-pro-preview + hints          | 2/7 = **28.6%** | Hints added   |
| Run 3    | April 13 | gemini-3.1-pro-preview + improved hints | 4/7 = **57.1%** | Best score    |

### Phase 2 — OpenRouter (April 14 onwards)

After discussion with instructors, switched to OpenRouter for model flexibility and to avoid single-provider dependency.

| Run   | Date     | Model                                                       | Datasets          | Score               | Notes                                  |
| ----- | -------- | ----------------------------------------------------------- | ----------------- | ------------------- | -------------------------------------- |
| Run 4 | April 15 | google/gemini-3.1-pro-preview via OpenRouter                | Yelp              | 2/7 = **28.6%**     | Proxy behavior differs from direct API |
| Run 5 | April 15 | google/gemini-3.1-pro-preview via OpenRouter + CAST fix     | Yelp              | 2/7 = **28.6%**     | BIGINT bug fixed                       |
| Run 6 | April 15 | google/gemini-3.1-pro-preview via OpenRouter + KB injection | Yelp + bookreview | 4/10 = **40.0%** ✅ | Beats 38% DAB baseline                 |

**Key insight:** Best confirmed score is 57.1% via direct Gemini API. Via OpenRouter, 40% across 2 datasets (Yelp + bookreview) beats the 38% frontier model baseline.

**Score improvement:** 0% → 57.1% (direct Gemini) | OpenRouter best: **40%** across 2 datasets ✅ beats baseline

---

## AI-DLC Governance

Oracle Forge follows the AWS AI-DLC framework — Inception → Construction → Operations with mandatory human approval gates between each phase.

### Sprint 1 — Complete ✅

| Phase        | Status                                          | Date        |
| ------------ | ----------------------------------------------- | ----------- |
| Inception    | ✅ Approved by all 5 members                    | April 13    |
| Construction | ✅ Completed                                    | April 13–15 |
| Operations   | ✅ Documented in planning/operations_sprint1.md | April 15    |

**Interim milestone (April 14) — all 7 items met ✅**

**What changed from plan during Construction:**

- Switched to OpenRouter after instructor discussion — avoids single-provider dependency
- Two critical bugs found and fixed: BIGINT CAST + MongoDB query limit
- KB injection wired into agent ahead of schedule

---

### Sprint 2 — Inception ⏳ Pending Approval

Documented in `planning/inception_sprint2.md` — pending team approval at next mob session.

**What Sprint 2 delivers:**

- All 12 DAB datasets running
- 50 trials per query for DAB leaderboard submission
- 15+ adversarial probes across 3+ failure categories
- GitHub PR to ucbepic/DataAgentBench
- Demo video (max 8 minutes)
- Signal Corps articles published

---

## What's Left (April 16–18)

| Task                                   | Owner                 | Status                           |
| -------------------------------------- | --------------------- | -------------------------------- |
| Fix Q2, Q3, Q4, Q7 failures            | Driver                | 🔄 In progress                   |
| Run all 12 datasets                    | Driver                | 🔄 2/12 done (Yelp + bookreview) |
| Adversarial probe library (15+ probes) | Intelligence Officers | ✅ 17 probes done                |
| KB v3 corrections                      | Intelligence Officers | ✅ Committed                     |
| 5 trials per query for submission      | Driver                | ❌                               |
| DAB GitHub PR                          | Driver                | ❌                               |
| Signal Corps articles published        | Signal Corps          | ❌                               |
| Demo video (max 8 min)                 | All                   | ❌                               |
| AI-DLC Operations document Sprint 2    | Driver                | ❌                               |
| Sprint 2 Inception approved            | All                   | ✅ Approved today                |

---

## Plan — April 16 to 18

### April 16 (Today)

- **Driver:** Load remaining 10 datasets on server (googlelocal, agnews, stockmarket, stockindex, crmarenapro, deps_dev, github_repos, music_brainz, pancancer, patents)
- **Driver:** Create hints files for each new dataset
- **Intelligence Officers:** KB domain docs for new datasets
- **Signal Corps:** Draft articles (600–1000 words each)

### April 17

- **Driver:** Run agent on all 12 datasets, collect results
- **Driver:** Fix remaining Yelp failures (Q2, Q3, Q4, Q7)
- **Signal Corps:** Publish articles on LinkedIn/Medium, post benchmark X thread

### April 18 — Submission Day

- **Driver:** Run 5 trials on all 54 queries
- **Driver:** Format results JSON per DAB submission spec
- **Driver:** Fork ucbepic/DataAgentBench, open GitHub PR
- **Driver:** Record demo video (max 8 minutes)
- **Driver:** Commit AI-DLC Operations document for Sprint 2
- **Signal Corps:** Post benchmark results on X, link to DAB PR
- **All:** Final submission PR to programme repository

---

---

## Agent Trial-and-Error Control

Three controls prevent excessive runtime and hallucinations:

1. **Hard iteration cap** — `--iterations 15` is a hard ceiling per query
2. **Corrections log injected at session start** — agent reads past failures before answering, doesn't repeat known mistakes
3. **Hints file as guardrails** — explicit join key patterns, CAST requirements, no-limit MongoDB per dataset

Failure detection is currently manual — Driver reads logs, diagnoses, writes correction. Automating this is a Sprint 2 stretch goal.

---

## Honest Assessment

**What worked:**

- Context engineering is the real bottleneck — hints file improved score from 0% to 40%+
- KB injection working — 16K chars of domain knowledge injected at every session start
- Team compounding — IOs built 17 probes + KB independently while Driver ran agent

**What we learned:**

- Same model behaves differently via proxy vs direct API
- DuckDB BIGINT AVG bug affects every rating query — a real enterprise data quality issue
- MongoDB default query limits silently truncate results — another real enterprise gotcha

**The gap:**

- 40% on 10 queries (2 datasets) vs unknown score on all 54 queries
- Week 9 is about scaling what works on Yelp + bookreview to all 12 datasets

---

_BLOOM Team · TRP1 FDE Programme · Tenacious Intelligence Corp · April 2026_
