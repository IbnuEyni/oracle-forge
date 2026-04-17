# Corrections Log
*Written by Driver after every observed agent failure. Read by agent at session start.*

---

## Correction 001 — 2026-04-11

**Query:** "Which U.S. state has the highest number of reviews, and what is the average rating of businesses in that state?"
**Dataset:** yelp | **Query ID:** 2

**What was wrong:**
Agent successfully retrieved MongoDB business data but then failed 9 times generating Python code to process it. Errors: `TypeError: list indices must be integers` and `SyntaxError: unterminated string`. The agent was treating the JSON result as a nested list and using integer indices instead of dictionary key access.

**Correct approach:**
- MongoDB query results are returned as a list of dictionaries
- Access fields with `record['field_name']` not `record[0]`
- When processing MongoDB results in execute_python, always use `pd.DataFrame(records)` first, then operate on the DataFrame
- State information in the Yelp dataset is extracted from the `description` field in the business collection using string parsing, not a dedicated `state` field

**Example correct code pattern:**
```python
import pandas as pd
# records is a list of dicts from MongoDB
df = pd.DataFrame(records)
# description field contains location info like "City, State"
df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})')
```

---

---

## Correction 002 — 2026-04-11

**Queries affected:** Q1, Q2, Q4, Q7 (Yelp dataset)

**What was wrong:**
Agent joins DuckDB `review` table with MongoDB `business` collection using wrong key.
- DuckDB `review` table uses `business_ref` field (e.g. `businessref_9`)
- MongoDB `business` collection uses `business_id` field (e.g. `businessid_9`)
- Agent attempts direct join without resolving the format difference → wrong results or TypeError

**Correct approach:**
Strip the prefix before joining:
- `business_ref` → remove `businessref_` prefix → get integer ID
- `business_id` → remove `businessid_` prefix → get integer ID
- Then join on the integer ID

**Example correct Python code:**
```python
import pandas as pd
# df_reviews from DuckDB, df_business from MongoDB
df_reviews['id'] = df_reviews['business_ref'].str.replace('businessref_', '').astype(int)
df_business['id'] = df_business['business_id'].str.replace('businessid_', '').astype(int)
merged = pd.merge(df_reviews, df_business, on='id')
```

**Q7 additional issue:**
TypeError: expected str, bytes or os.PathLike object, not list
— agent passes a list where a string path is expected when reading stored results.
Fix: always check type before passing to open() — use json.dumps() if result is already a dict/list.

---

## Correction 003 — 2026-04-15

**Queries affected:** Yelp queries that compute averages over review ratings or rely on large MongoDB result sets

**What was wrong:**
The `rating` column in DuckDB `review` table is stored as `BIGINT`. Using `AVG(rating)` directly on a BIGINT column loses decimal precision. In the same failure mode, MongoDB queries were using a small default document limit, so the agent sometimes averaged an incomplete subset of businesses.

**Correct approach:**
1. Always use `CAST(rating AS FLOAT)` or `CAST(rating AS DOUBLE)` when computing averages:
   ```sql
   SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)
   ```
2. Always set MongoDB query limit high enough to return all matching documents:
   ```json
   {"collection": "business", "filter": {...}, "limit": 10000}
   ```

**Evidence:**
- Precision is preserved only after casting the rating column.
- Full document retrieval requires overriding the small default MongoDB limit.

---

## Data Leakage Policy

**This file must never contain:**
- Ground truth answer values, expected answers, or validator outputs
- Query IDs mapped to specific expected outputs
- "Correct" vs "wrong" values for any query

**This file may contain:**
- Structural failure patterns
- Correction approaches
- Schema references
- Normalization patterns and safe configuration rules

If a correction would mention a specific answer value, rewrite it to describe the failure mechanism instead.
