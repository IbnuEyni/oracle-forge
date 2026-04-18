# Oracle Forge — BLOOM Team

**TRP1 FDE Programme · April 2026**

A production-grade natural language data analytics agent evaluated on the
DataAgentBench (DAB) benchmark — 54 queries, 12 datasets, 9 domains.

## Team

| Name             | Email                     | Role                 |
| ---------------- | ------------------------- | -------------------- |
| Amir Ahmedin     | shuaibahmedin@gmail.com   | Driver               |
| Nebiyou Abebe    | nebiyouabebe6@gmail.com   | Intelligence Officer |
| Ruth Solomon     | ruthsoll87@gmail.com      | Intelligence Officer |
| Efrata Wolde     | ephratawolde990@gmail.com | Signal Corps         |
| Abdurahim Miftah | abdugreat3@gmail.com      | Signal Corps         |

## Live Agent

- Server: `bloom.10academy.org`
- Connect: `ssh trp-bloom`
- Shared session: `tmux attach -t oracle-forge`

## Architecture

```
User Query (natural language)
        |
        v
  oracle_run.py          <-- Oracle Forge wrapper
        |
        | injects KB context (~16KB) via kb_injector.py
        |   Layer 1: schema hints  (--use_hints flag)
        |   Layer 2: domain knowledge  (kb/domain/*.md)
        |   Layer 3: corrections memory  (kb/corrections/corrections.md)
        v
  DataAgent  (DAB scaffold)
        |
   +---------+-----------+
   |         |           |
query_db  execute_python  return_answer
   |         |
   v         v
MongoDB    DuckDB         (Yelp dataset)
PostgreSQL SQLite         (other datasets)
        |
        v
  eval/harness.py        <-- scores pass@1, appends to score_log.jsonl
```

## Score Progression

| Date | Dataset | Model | Score |
| ---- | ------- | ----- | ----- |

| 2026-04-11 | yelp | gemini-3.1-pro-preview | 2/7 = 28.6% |
| 2026-04-13 | yelp | gemini-3.1-pro-preview | 4/7 = 57.1% |
| 2026-04-18 | bookreview | gemini-3.1-pro-preview | 3/3 = 100% |
| 2026-04-18 | stockindex | gemini-3.1-pro-preview | 2/3 = 66.7% |
| 2026-04-18 | crmarenapro | gemini-3.1-pro-preview | 6/13 = 46.2% |
| 2026-04-18 | googlelocal | gemini-3.1-pro-preview | 1/4 = 25.0% |
| 2026-04-18 | agnews | gemini-3.1-pro-preview | 1/4 = 25.0% |
| 2026-04-18 | stockmarket | gemini-3.1-pro-preview | 1/5 = 20.0% |
| 2026-04-18 | music_brainz_20k | gemini-3.1-pro-preview | 1/3 = 33.3% |

**Overall: 19/54 = 35.2% pass@1 — DAB leaderboard leader is 54.3% (PromptQL + Gemini-3.1-Pro)**

## Setup

```bash
git clone https://github.com/IbnuEyni/oracle-forge.git
cd oracle-forge
git clone https://github.com/ucbepic/DataAgentBench.git
cd DataAgentBench
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
cp ../.env.example .env  # fill in OPENROUTER_API_KEY
```

## Run

```bash
# Single query
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints

# Full harness
python ~/oracle-forge/eval/harness.py --dataset yelp \
  --queries 1,2,3,4,5,6,7 --llm google/gemini-3.1-pro-preview
```

## Project Structure

```
oracle-forge/
├── agent/          # oracle_run.py, kb_injector.py, AGENT.md
├── kb/             # Knowledge Base (architecture, domain, evaluation, corrections)
├── eval/           # Evaluation harness + score_log.jsonl
├── probes/         # Adversarial probe library
├── planning/       # AI-DLC Inception documents
├── utils/          # join_key_resolver, mongo_helper, score_logger
├── signal/         # Signal Corps engagement log
└── results/        # DAB results JSON
```

## Benchmark Target

- Benchmark: DataAgentBench (54 queries, 12 datasets)
- Best published score: 54.3% (PromptQL + Gemini-3.1-Pro)
- Our target: Approach 54.3% leaderboard leader through context engineering
