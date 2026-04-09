# AI-DLC Inception Document — Sprint 1
**Team:** BLOOM | **Driver:** Amir Ahmedin | **Date:** April 2026

---

## 1. Press Release (What We Are Building)

The BLOOM team has built Oracle Forge — a production-grade natural language data analytics
agent that answers complex business questions across heterogeneous databases. Oracle Forge
connects to PostgreSQL, MongoDB, SQLite, and DuckDB simultaneously, resolves inconsistently
formatted join keys automatically, extracts structured facts from unstructured text fields,
and returns verifiable answers with full query traces. It is evaluated against the
DataAgentBench benchmark (54 queries, 12 datasets, 9 domains) and achieves a measurable
pass@1 score that improves between Week 8 and Week 9. The agent runs on the BLOOM team's
shared EC2 server and is accessible to all team members from any device.

---

## 2. Honest FAQ — User Perspective

**Q: What can I ask Oracle Forge?**
A: Complex business questions that require data from multiple databases simultaneously.
Example: "What is the average rating of businesses in Indianapolis?" — the agent queries
MongoDB for business locations and DuckDB for ratings, joins the results, and returns
a verified answer.

**Q: What does it NOT do yet?**
A: It does not yet handle all 12 DAB datasets. Sprint 1 targets the Yelp dataset first,
then expands. It also does not yet have a web interface — interaction is via command line.

**Q: How do I know the answer is correct?**
A: Every answer comes with a query trace — the exact queries run against each database,
in order. You can verify the answer by re-running the queries manually.

---

## 3. Honest FAQ — Technical Perspective

**Q: What is the hardest part of this sprint?**
A: Cross-database join key resolution. Business IDs are formatted differently across
MongoDB and DuckDB in the same dataset. The agent must detect and resolve format
mismatches before attempting joins — without being told explicitly.

**Q: What could go wrong?**
A: Gemini API rate limits on the free tier will slow down evaluation runs. PostgreSQL
is running in Docker (not system-level) which adds a dependency on the Docker daemon
staying healthy. If the Docker container stops, PostgreSQL goes down.

**Q: What dependencies exist outside our control?**
A: Gemini API availability and quota limits. The DAB repository structure — if UC Berkeley
changes the dataset format, our agent interface breaks. The EC2 server uptime managed
by 10 Academy.

---

## 4. Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| LLM provider | Gemini (gemini-2.0-flash) | Free tier available, supported by DAB built-in agent |
| PostgreSQL deployment | Docker container | System-level install broken due to debconf lock; Docker is reliable fallback |
| Agent base | DAB built-in DataAgent | Faster to extend than build from scratch; already handles multi-DB routing |

---

## 5. Definition of Done (Verifiable Checklist)

1. Agent runs `python run_agent.py --dataset yelp --query_id 1 --llm gemini-2.0-flash`
   and returns a non-empty `final_result` in `final_agent.json`
2. Agent handles at least 2 DAB database types (MongoDB + DuckDB confirmed working)
3. Evaluation harness produces a pass@1 score against at least 5 Yelp queries
4. Score log has at least 2 data points showing progression
5. PostgreSQL Docker container starts automatically on server reboot
6. All team members can SSH into the server and attach to `oracle-forge` tmux session
7. README on server documents setup steps a new team member can follow from scratch
8. DAB results JSON exists for at least the Yelp dataset

---

## 6. Mob Session Approval Record

| Date | Approved by | Role | Hardest question asked | Answer |
|------|-------------|------|----------------------|--------|
| 2026-04-09 | Nebiyou Abebe | Intelligence Officer 1 | | |
| 2026-04-09 | Ruth Solomon | Intelligence Officer 2 | | |
| 2026-04-09 | Abdurahim Miftah | Signal Corps 1 | | |
| 2026-04-09 | Efrata Wolde | Signal Corps 2 | | |
| | Ermiyas Bitew | — | Did not attend | — |

**Status:** ⏳ Pending team approval — fill in hardest question and answer for each member.

---

*AI-DLC Phase: INCEPTION | Next phase: CONSTRUCTION (requires full team approval above)*
