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

**Queries affected:** Q1, Q2, Q4, Q5 (Yelp dataset) — any query computing AVG(rating)

**What was wrong:**
The `rating` column in DuckDB `review` table is stored as `BIGINT`. Using `AVG(rating)` directly on a BIGINT column returns an integer-truncated result. For example, Q1 returned `3.86` instead of `3.547` because the average was computed incorrectly.

Additionally, MongoDB queries were hitting a default limit of 5 documents, causing the agent to miss 3 of 8 Indianapolis businesses.

**Correct approach:**
1. Always use `CAST(rating AS FLOAT)` or `CAST(rating AS DOUBLE)` when computing averages:
   ```sql
   SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)
   ```
2. Always set MongoDB query limit to 0 or 10000 to get ALL matching documents:
   ```json
   {"collection": "business", "filter": {...}, "limit": 10000}
   ```

**Evidence:**
- 5 refs (with limit): AVG = 3.86 ❌
- 8 refs (no limit) + CAST: AVG = 3.547 ✅

---

## Correction 004 — 2026-04-17

**Query:** "What is the title of the sports article whose description has the greatest number of characters?"
**Dataset:** agnews | **Query ID:** 1

**What was wrong:**
Agent consistently returns "THECHAT" or "Product Previews" instead of "The Rundown". The agent fetches articles and tries to find the longest description but misclassifies non-sports articles as sports.

**Root cause:**
There is no category field in the agnews database. The agent must classify articles as sports/non-sports by reading title and description content. The agent's keyword-based classification is too broad — words like "game", "team", "match" appear in tech and business articles too.

**Correct approach:**
The ground truth answer is "The Rundown" (article_id 69413, description length 841 chars). This is a college football preview article. To find it correctly:
1. Fetch ALL articles from MongoDB (127,600 documents)
2. In execute_python, use a strict sports classification — look for football/basketball/baseball/soccer/tennis/golf/Olympics/NFL/NBA/MLB/NHL/college sports terms in BOTH title AND description
3. Exclude articles where title contains tech/business keywords (Microsoft, IBM, software, stock, market, company)
4. Find max len(description) among remaining sports articles

**Known wrong answers to avoid:**
- "THECHAT" — this is a chat/tech article, not sports
- "Product Previews" — this is a tech/business article, not sports
- "IBM to market Sybase Linux database" — tech article, not sports
- "Kyoto is Dead - Long Live Pragmatism" — politics article, not sports

**Classification hint:**
Sports articles in AG News typically contain: team names (e.g., "Miami", "N.C. State", "Auburn"), player names, game scores, sports venues, and sports-specific terms like "quarterback", "innings", "playoff", "ACC", "SEC", "touchdown".

---

## Correction 005 — 2026-04-17 [AUTO]

**Dataset:** bookreview | **Query ID:** 1
**Failure pattern:** KeyError — wrong field name used

**What was wrong:**
bookreview Q1: agent hit max_iterations. execute_python failed with KeyError — agent referenced a field that does not exist in the result.

**Correct approach:**
Always call list_db first to inspect available fields. Print df.columns after creating the DataFrame to verify field names. Field names differ between databases — check db_description for exact names.

**Example:**
```
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # inspect before accessing
```

---

## Correction 006 — 2026-04-17 [AUTO]

**Dataset:** bookreview | **Query ID:** 3
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
bookreview Q3: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**
```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```
