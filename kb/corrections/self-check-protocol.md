# Self-Check Protocol

## Purpose

Before submitting any final answer, run through this checklist. If any check fails, revise the answer before submitting.

This doc is injected on every query (base context). It adds zero API calls — it is a verification step inside the existing agent prompt.

## Pre-Submission Checklist

### Check 1: Source of Truth

- Did I query the correct table for the data type I need?
- Review-level data (individual ratings, per-review info) → DuckDB `review` table
- Business-level attributes (location, category, credit card acceptance) → MongoDB `business` collection
- Pre-aggregated summary fields like `business.stars` are NOT substitutes for per-record aggregation

### Check 2: Join Key Normalization

- Before joining across databases, did I strip prefixes?
- MongoDB: `business_id` → `businessid_9` format → strip `businessid_`
- DuckDB: `business_ref` → `businessref_9` format → strip `businessref_`
- Join on the integer, not the prefixed string

### Check 3: Filter Before Aggregate

- Did I apply WHERE/filter conditions BEFORE the GROUP BY or aggregation?
- Filtering after aggregation produces wrong averages and wrong counts
- Example: if the query asks for "credit-card-accepting businesses," filter by `BusinessAcceptsCreditCards: True` FIRST, then compute the average

### Check 4: Cross-Database Merge

- If the query spans multiple databases, did I query each separately and merge in Python?
- There is no native cross-database JOIN across PostgreSQL / MongoDB / SQLite / DuckDB
- Use `pd.merge()` after loading each side into a DataFrame

### Check 5: Answer Format

- Is my answer compact enough for the validator?
- Keep related values (state name and count, number and entity) within 50 characters of each other
- Avoid long explanatory paragraphs between the number and the label

### Check 6: Data Type Handling

- Did I cast DuckDB BIGINT to FLOAT before computing averages? (`AVG(CAST(rating AS FLOAT))`)
- Did I set MongoDB query limit high enough? (default is 5, use `limit: 10000` for aggregations)
- Did I handle NULL / missing fields explicitly?

### Check 7: Known Corrections

- Before submitting, did I check if this query matches a known failure pattern in the corrections log?
- If yes, have I applied the documented fix?

## How to Apply

When answering any query, silently run through these 7 checks before emitting the final answer.

If the answer fails any check:
1. Do not submit it.
2. Identify which check failed.
3. Reformulate the query or recompute the result.
4. Re-run the checks.
5. Submit only when all 7 checks pass.

The user does not see this checklist. It is internal verification, not user-facing output.

## Why This Exists

Our agent's failures cluster into predictable patterns. Each pattern has a known fix. Running this 7-point check catches the most common mistakes before the answer reaches the validator.

This is free insurance — no extra API calls, no extra latency beyond a few tokens of prompt text.
