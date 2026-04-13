# AI-DLC Inception Document — Sprint 1

**Team:** BLOOM | **Driver:** Amir Ahmedin | **Date:** April 2026

---

## 1. Press Release (What We Are Building)

The BLOOM team has built Oracle Forge — a production-grade natural language data analytics
agent that answers complex business questions across heterogeneous databases. Oracle Forge
connects to PostgreSQL, MongoDB, SQLite, and DuckDB simultaneously, resolves inconsistently
formatted join keys automatically, extracts structured facts from unstructured text fields,
and returns verifiable answers with full query traces. When a query fails, the agent detects
the failure, diagnoses the root cause, retries with a fix, and logs the correction for future
sessions. It is evaluated against the DataAgentBench benchmark (54 queries, 12 datasets,
9 domains) and achieves a measurable pass@1 score that improves between Week 8 and Week 9.
The agent runs on the BLOOM team's shared EC2 server and is accessible to all team members
from any device.

---

## 2. What We Are NOT Building

- A web UI or chat interface — interaction is command line only this sprint
- A general-purpose SQL assistant — Oracle Forge is scoped to DAB datasets only
- A fine-tuned model — we use Gemini API as-is, no model training

---

## 3. Honest FAQ — User Perspective

**Q: What can I ask Oracle Forge?**
A: Complex business questions that require data from multiple databases simultaneously.
Example: "What is the average rating of businesses in Indianapolis?" — the agent queries
MongoDB for business locations and DuckDB for ratings, joins the results, and returns
a verified answer.

**Q: What does it NOT do yet?**
A: It does not yet handle all 12 DAB datasets. Sprint 1 targets the Yelp dataset first,
then expands. It also does not have a web interface — interaction is via command line.

**Q: How do I know the answer is correct?**
A: Every answer comes with a query trace — the exact queries run against each database,
in order. You can verify the answer by re-running the queries manually.

---

## 4. Honest FAQ — Technical Perspective

**Q: What is the hardest part of this sprint?**
A: Cross-database join key resolution. Business IDs are formatted differently across
MongoDB and DuckDB in the same dataset. The agent must detect and resolve format
mismatches before attempting joins — without being told explicitly.

**Q: What could go wrong?**
A: Gemini API rate limits will slow down evaluation runs. PostgreSQL is running in Docker
(not system-level) — if the container stops, PostgreSQL goes down. The DuckDB user_database
file for Yelp appears corrupted and needs re-downloading before queries 2-7 can pass.

**Q: What dependencies exist outside our control?**
A: Gemini API availability and quota limits. The DAB repository structure. The EC2 server
uptime managed by 10 Academy.

---

## 5. Self-Correction Loop

Every agent failure must follow this pattern:

```
detect → diagnose → retry → log
```

| Step     | What happens                                                                       |
| -------- | ---------------------------------------------------------------------------------- |
| detect   | Agent receives an error or empty result from a tool call                           |
| diagnose | Agent identifies failure type: wrong DB, bad join key, missing field, data quality |
| retry    | Agent reformulates the query with the fix applied                                  |
| log      | Failure + fix written to kb/corrections/ for future sessions                       |

This loop is the mechanism by which the agent improves without retraining.

---

## 6. Key Decisions

| Decision              | Choice                                         | Reason                                                      |
| --------------------- | ---------------------------------------------- | ----------------------------------------------------------- |
| LLM provider          | Gemini (gemini-3.1-pro-preview)                | Best available model, confirmed working with DAB built-in agent |
| PostgreSQL deployment | Docker container with --restart unless-stopped | System-level install broken; Docker is reliable fallback    |
| Agent base            | DAB built-in DataAgent                         | Faster to extend than build from scratch                    |
| Pass@1 target         | 30% Sprint 1, improve by Sprint 2              | Beats GPT-5-mini baseline (30%); realistic given current 0% |

---

## 7. Definition of Done

### Interim Milestone — April 14

- [ ] Agent running on server, handling minimum 2 database types
- [ ] Basic natural language to query working
- [ ] KB v1 and KB v2 committed with injection test results
- [ ] Evaluation harness producing baseline score with query trace
- [ ] GitHub repo has all required folders with content
- [ ] Signal Corps has minimum 3 posts live with links in engagement_log.md
- [ ] PostgreSQL Docker container running with --restart unless-stopped

### Final Milestone — April 18

- [ ] Agent handling all 4 database types
- [ ] Self-correction demonstrated — failure + diagnosis + recovery logged in kb/corrections/
- [ ] KB v2 domain documents complete and injection-tested (all 6 sections)
- [ ] 15+ adversarial probes documented with fixes applied in probes/probes.md
- [ ] Score improvement shown from baseline to final (target: 30% pass@1)
- [ ] GitHub PR submitted to ucbepic/DataAgentBench
- [ ] Demo video live (max 8 minutes, no login required)

---

## 8. Mob Session Approval Record

| Date       | Approved by   | Role                 | Hardest question asked                                                            | Answer                                                                |
| ---------- | ------------- | -------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 2026-04-09 | Nebiyou Abebe | Intelligence Officer | Have we confirmed the join keys and formats in KB, or are we assuming they match? | We have confirmed them through actual agent failures, not assumption. |

Here's the evidence:
The agent failed Q1, Q2, Q4, Q7 with wrong answers or TypeErrors
We inspected the tool call logs and saw the agent trying to join on raw business_id and business_ref without resolving the prefix difference
We then queried the actual MongoDB and DuckDB data and confirmed:
MongoDB: businessid_1, businessid_2...
DuckDB: businessref_1, businessref_2...
We added the resolution pattern to the hints file and the queries started passing
So yes — confirmed by failure and fix, not assumption
However — this is only confirmed for the Yelp dataset. For other datasets like bookreview, crmarenapro, googlelocal we have not confirmed the join key formats yet. That's a gap.
|
| 2026-04-09 | Ruth Solomon | Intelligence Officer | Does the agent correctly identify and route queries that require data from both PostgreSQL and MongoDB in a single request? | Not yet tested — this is an honest gap.
Our current testing has only covered Yelp, which uses MongoDB + DuckDB. We have not run any dataset that requires PostgreSQL + MongoDB in the same query

The agent's routing is handled by DAB's QueryDBTool which reads db_config.yaml per dataset. It should work in theory — but we haven't proven it with a passing query yet. |
| 2026-04-09 | Abdurahim Miftah | Signal Corps | What changes do we need to make to our current Yelp-based agent architecture to support querying and combining data from a second database? | Our agent already handles multiple databases within one dataset — Yelp uses both MongoDB and DuckDB simultaneously. So the multi-DB capability exists.

To support a new dataset, we need three things:

Hints file — each dataset needs its own db_description_withhint.txt with its specific join key patterns and schema quirks

KB domain doc — Intelligence Officers add a schema document for the new dataset to kb/domain/

Run the agent — python run_agent.py --dataset bookreview just works, no code changes needed

The agent code, harness, and Docker setup don't change. The only work is dataset-specific knowledge — which is exactly what the KB is for.

Honest gap: The KB isn't being injected into the agent yet. Right now only the hints file is read.
|
| 2026-04-09 | Efrata Wolde | Signal Corps | If Gemini API goes down during final submission, what is our fallback? | We don't have one yet. We will add a backup API key (OpenAI or Anthropic) to .env before the final submission run. |
| 2026-04-13 | Amir Ahmedin | Driver | Our score is 57% on Yelp. What do we think our real pass@1 will be across all 54 queries? | Honestly lower — maybe 20-30%. Yelp is one dataset and we have tuned hints for it. Other datasets need their own hints and KB docs. The 57% proves the approach works. Week 9 is about scaling it to all 12 datasets. |

**Status:** ✅ APPROVED — All team members approved on 2026-04-13. Construction phase begins.

---

> ✅ CONSTRUCTION APPROVED BY FULL TEAM ON 2026-04-13

---

_AI-DLC Phase: CONSTRUCTION | Inception approved: 2026-04-13_
