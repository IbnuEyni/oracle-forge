# AGENT.md — Oracle Forge

## Architecture
Oracle Forge extends the DAB built-in DataAgent with 3 context layers:

1. **Schema & Metadata** — loaded via `--use_hints` (db_description_withhint.txt per dataset)
2. **Domain Knowledge** — KB documents in kb/domain/ (join keys, failure categories, field inventory)
3. **Corrections Memory** — kb/corrections/corrections.md injected at session start via kb_injector.py

## Key Design Decisions
- Base: DAB built-in DataAgent (common_scaffold/DataAgent.py)
- LLM: google/gemini-3.1-pro-preview via OpenRouter (instructor-approved)
- Databases: PostgreSQL (Docker, port 5432), MongoDB (system), SQLite, DuckDB
- KB injection: monkey-patch on DataAgent.__init__ appends all 3 layers to db_description
- KB injection confirmed: `[Oracle Forge] KB injected: 16044 chars added to db_description` printed on every run

## How to Run

### With OpenRouter (current — instructor-approved API)
```bash
cd ~/DataAgentBench && source .venv/bin/activate
# google/ prefix routes to OpenRouter automatically (DataAgent.py line 76)
python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints

# bookreview (PostgreSQL + SQLite)
python ~/oracle-forge/agent/oracle_run.py --dataset bookreview --query_id 1 \
  --llm google/gemini-3.1-pro-preview --iterations 20 --use_hints
```

## Score History

| Date | Model | API | Hints | KB Injected | Dataset | Score |
|------|-------|-----|-------|-------------|---------|-------|
| 2026-04-11 | gemini-2.5-flash | Gemini direct | No | No | yelp | 0/7 = 0% |
| 2026-04-11 | gemini-3.1-pro-preview | Gemini direct | Yes | No | yelp | 2/7 = 28.6% |
| 2026-04-13 | gemini-3.1-pro-preview | Gemini direct | Yes | Yes | yelp | 4/7 = 57.1% |
| 2026-04-15 | google/gemini-3.1-pro-preview | OpenRouter | Yes | Yes | yelp | in progress |
| 2026-04-15 | google/gemini-3.1-pro-preview | OpenRouter | Yes | Yes | bookreview | in progress |

## What Worked
- Structural hints (join key patterns, state extraction regex)
- gemini-3.1-pro-preview significantly better than gemini-2.5-flash
- --use_hints flag essential — without it agent makes no tool calls
- KB Layer 2 (domain knowledge): join-key-glossary.md directly caused Q1/Q2 to pass after being added — agent stopped hallucinating businessref_ join and used correct normalization pattern
- KB Layer 3 (corrections): score jumped 28.6% → 57.1% after corrections.md was injected — CAST AS FLOAT fix resolved Q1 rating precision, MongoDB limit=10000 fix resolved Q2 state detection
- KB injection confirmed wired: 16044 chars injected on every run via kb_injector.py monkey-patch
- OpenRouter: google/ and anthropic/ prefixes route automatically — no openrouter/ prefix needed

## What Did Not Work
- gemini-2.5-flash: MALFORMED_FUNCTION_CALL errors
- Answer-specific hints: overfitting — reverted
- 10 iterations: insufficient for complex multi-DB queries, 20 needed
