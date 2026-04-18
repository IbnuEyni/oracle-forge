# Corrections Log

_Written by Driver after every observed agent failure. Read by agent at session start._

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
The `rating` column in DuckDB `review` table is stored as `BIGINT`. Using `AVG(rating)` directly on a BIGINT column returns an integer-truncated result — the computed average is wrong.

Additionally, MongoDB queries were hitting a default limit of 5 documents, causing the agent to miss businesses that should be included in the calculation.

**Correct approach:**

1. Always use `CAST(rating AS FLOAT)` or `CAST(rating AS DOUBLE)` when computing averages:
   ```sql
   SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)
   ```
2. Always set MongoDB query limit to 10000 to get ALL matching documents:
   ```json
   {"collection": "business", "filter": {...}, "limit": 10000}
   ```

---

## Correction 004 — 2026-04-17

**Dataset:** agnews | **Query ID:** 1

**What was wrong:**
Agent misclassifies non-sports articles as sports when searching for the longest description. There is no category field in the agnews database — the agent must classify articles by reading title and description content. Keyword-based classification is too broad — words like "game", "team", "match" appear in tech and business articles too.

**Correct approach:**

1. Fetch ALL articles from the database — do not filter before classification
2. Use strict sports classification — require sports-specific terms in BOTH title AND description: football, basketball, baseball, soccer, tennis, golf, Olympics, NFL, NBA, MLB, NHL, playoff, quarterback, innings, touchdown, and specific league/conference names
3. Exclude articles where the title contains clear non-sports signals: software, stock, market, company names, political terms
4. Among classified sports articles, find the one with the maximum `len(description)`
5. Return only the article title — not the description or length

---

## Correction 005 — 2026-04-17 [AUTO]

**Dataset:** bookreview | **Query ID:** 1
**Failure pattern:** Multiple execute_python errors cycling

**What was wrong:**
bookreview Q1: agent hit max_iterations cycling through four errors:

- `NameError: name 'var_call' is not defined` — agent references a result variable that was never stored
- `ValueError: DataFrame constructor not properly called` — agent passes wrong type to pd.DataFrame()
- `TypeError: expected str, bytes or os.PathLike object, not list` — agent passes list to open()
- `AttributeError: 'Series' object has no attribute 'value_collapse'` — agent calls non-existent pandas method

**Correct approach:**

- Always use the exact key name returned in the tool result message, not a guessed name like `var_call`
- Check available keys with `print(list(env.keys()))` before referencing stored results
- Always pass a list of dicts to `pd.DataFrame()`: `pd.DataFrame(records)` where records is the query result
- Use `df.value_counts()` not `df.value_collapse()` — the correct pandas method is `value_counts()`
- When a stored result is a file path (string ending in .json), read it with `json.load(open(path))`

**Example:**

```python
import pandas as pd, json
# Check what keys are available
print(list(env.keys()))
# Read stored result correctly
result = env.get('var_KEYNAME')  # use exact key from tool result
if isinstance(result, str) and result.endswith('.json'):
    data = json.load(open(result))
else:
    data = result
df = pd.DataFrame(data)  # data must be list of dicts
print(df.columns.tolist())  # verify columns before use
counts = df['column'].value_counts()  # not value_collapse
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

---

## Correction 007 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 2
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
yelp Q2: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 008 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 3
**Failure pattern:** Incorrect numeric computation

**What was wrong:**
yelp Q3: agent returned a numeric answer but the value was computed incorrectly — likely due to integer truncation or incomplete data.

**Correct approach:**
Always CAST numeric columns to FLOAT before computing AVG in DuckDB: AVG(CAST(column AS FLOAT)). Always set MongoDB query limit to 10000 to avoid missing documents. Verify join key normalisation: strip prefixes before merging DataFrames.

**Example:**

```
-- DuckDB: cast before averaging
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)

-- MongoDB: always set explicit limit
{"collection": "business", "filter": {}, "limit": 10000}
```

---

## Correction 009 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 4
**Failure pattern:** Wrong category field used

**What was wrong:**
yelp Q4: agent returned an answer but the category field was sourced from the wrong table or collection.

**Correct approach:**
In Yelp, business categories are stored in the MongoDB business collection as a list in the 'categories' field — not in DuckDB. Explode the list before counting. Do not use DuckDB category fields — they may be stale or differently formatted.

**Example:**

```
import pandas as pd
# MongoDB business categories field is a list
df['categories'] = df['categories'].apply(
    lambda x: x if isinstance(x, list) else []
)
all_cats = df.explode('categories')['categories'].value_counts()
```

---

## Correction 010 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 5
**Failure pattern:** NaN/NameError in execute_python

**What was wrong:**
yelp Q5: agent hit max_iterations. execute_python failed repeatedly with NameError — bare `nan` used instead of a valid null representation.

**Correct approach:**
Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). Always add `import numpy as np` before using np.nan.

**Example:**

```
import numpy as np
import pandas as pd
# correct null handling
df = df.replace(float('nan'), np.nan)
df = df.dropna(subset=['required_column'])
```

---

## Correction 011 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 7
**Failure pattern:** TypeError — integer index used on dict result

**What was wrong:**
yelp Q7: agent hit max_iterations. execute_python failed with TypeError — agent accessed a list-of-dicts result using integer indices instead of field names.

**Correct approach:**
Always wrap tool results in pd.DataFrame() before field access. Use df['field_name'] not result[0]. Check result type with type(result) before processing.

**Example:**

```
import pandas as pd
# records is a list of dicts from query_db
df = pd.DataFrame(records)
# now access fields by name
value = df['field_name']
```

---

## Correction 012 — 2026-04-17 [AUTO]

**Dataset:** yelp | **Query ID:** 7
**Failure pattern:** max_iterations — no tool errors recorded

**What was wrong:**
yelp Q7: agent hit max_iterations with no recorded tool errors. The agent may have been looping on query reformulation without making progress.

**Correct approach:**
Increase --iterations to 30. Add dataset-specific hints to db_description_withhint.txt to guide the first query. Check that the correct database type is being queried for this dataset.

---

## Correction 013 — 2026-04-18 [AUTO]

**Dataset:** googlelocal | **Query ID:** 1
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
googlelocal Q1: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 014 — 2026-04-18 [AUTO]

**Dataset:** googlelocal | **Query ID:** 2
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
googlelocal Q2: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 015 — 2026-04-18 [AUTO]

**Dataset:** googlelocal | **Query ID:** 3
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
googlelocal Q3: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 016 — 2026-04-18 [AUTO]

**Dataset:** agnews | **Query ID:** 1
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
agnews Q1: agent returned an answer that did not pass validation. Terminate reason: return_answer. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 017 — 2026-04-18 [AUTO]

**Dataset:** agnews | **Query ID:** 2
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
agnews Q2: agent returned an answer that did not pass validation. Terminate reason: return_answer. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 018 — 2026-04-18 [AUTO]

**Dataset:** agnews | **Query ID:** 3
**Failure pattern:** NaN/NameError in execute_python

**What was wrong:**
agnews Q3: agent hit max_iterations. execute_python failed repeatedly with NameError — bare `nan` used instead of a valid null representation.

**Correct approach:**
Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). Always add `import numpy as np` before using np.nan.

**Example:**

```
import numpy as np
import pandas as pd
# correct null handling
df = df.replace(float('nan'), np.nan)
df = df.dropna(subset=['required_column'])
```

---

## Correction 019 — 2026-04-18 [AUTO]

**Dataset:** music_brainz_20k | **Query ID:** 1
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
music_brainz_20k Q1: agent returned an answer that did not pass validation. Terminate reason: return_answer. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 020 — 2026-04-18 [AUTO]

**Dataset:** music_brainz_20k | **Query ID:** 3
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
music_brainz_20k Q3: agent returned an answer that did not pass validation. Terminate reason: return_answer. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 021 — 2026-04-18 [AUTO]

**Dataset:** DEPS_DEV_V1 | **Query ID:** 2
**Failure pattern:** KeyError — wrong field name used

**What was wrong:**
DEPS_DEV_V1 Q2: agent hit max_iterations. execute_python failed with KeyError — agent referenced a field that does not exist in the result.

**Correct approach:**
Always call list_db first to inspect available fields. Print df.columns after creating the DataFrame to verify field names. Field names differ between databases — check db_description for exact names.

**Example:**

```
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # inspect before accessing
```

---

## Correction 022 — 2026-04-18 [AUTO]

**Dataset:** GITHUB_REPOS | **Query ID:** 1
**Failure pattern:** Incorrect numeric computation

**What was wrong:**
GITHUB_REPOS Q1: agent returned a numeric answer but the value was computed incorrectly — likely due to integer truncation or incomplete data.

**Correct approach:**
Always CAST numeric columns to FLOAT before computing AVG in DuckDB: AVG(CAST(column AS FLOAT)). Always set MongoDB query limit to 10000 to avoid missing documents. Verify join key normalisation: strip prefixes before merging DataFrames.

**Example:**

```
-- DuckDB: cast before averaging
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)

-- MongoDB: always set explicit limit
{"collection": "business", "filter": {}, "limit": 10000}
```

---

## Correction 023 — 2026-04-18 [AUTO]

**Dataset:** PANCANCER_ATLAS | **Query ID:** 1
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
PANCANCER_ATLAS Q1: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 024 — 2026-04-18 [AUTO]

**Dataset:** PATENTS | **Query ID:** 1
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
PATENTS Q1: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 025 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 1
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
crmarenapro Q1: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 31570. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 026 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 2
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
crmarenapro Q2: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 31570. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 027 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 3
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
crmarenapro Q3: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 028 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 4
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
crmarenapro Q4: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 029 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 7
**Failure pattern:** NaN/NameError in execute_python

**What was wrong:**
crmarenapro Q7: agent hit max_iterations. execute_python failed repeatedly with NameError — bare `nan` used instead of a valid null representation.

**Correct approach:**
Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). Always add `import numpy as np` before using np.nan.

**Example:**

```
import numpy as np
import pandas as pd
# correct null handling
df = df.replace(float('nan'), np.nan)
df = df.dropna(subset=['required_column'])
```

---

## Correction 030 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 8
**Failure pattern:** KeyError — wrong field name used

**What was wrong:**
crmarenapro Q8: agent hit max_iterations. execute_python failed with KeyError — agent referenced a field that does not exist in the result.

**Correct approach:**
Always call list_db first to inspect available fields. Print df.columns after creating the DataFrame to verify field names. Field names differ between databases — check db_description for exact names.

**Example:**

```
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # inspect before accessing
```

---

## Correction 031 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 10
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
crmarenapro Q10: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 51735. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 032 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 12
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
crmarenapro Q12: agent returned an answer that did not pass validation. Terminate reason: return_answer. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 033 — 2026-04-18 [AUTO]

**Dataset:** crmarenapro | **Query ID:** 13
**Failure pattern:** NaN/NameError in execute_python

**What was wrong:**
crmarenapro Q13: agent hit max_iterations. execute_python failed repeatedly with NameError — bare `nan` used instead of a valid null representation.

**Correct approach:**
Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). Always add `import numpy as np` before using np.nan.

**Example:**

```
import numpy as np
import pandas as pd
# correct null handling
df = df.replace(float('nan'), np.nan)
df = df.dropna(subset=['required_column'])
```

---

## Correction 034 — 2026-04-18 [AUTO]

**Dataset:** stockindex | **Query ID:** 3
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
stockindex Q3: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 035 — 2026-04-18 [AUTO]

**Dataset:** stockmarket | **Query ID:** 2
**Failure pattern:** TypeError — integer index used on dict result

**What was wrong:**
stockmarket Q2: agent hit max_iterations. execute_python failed with TypeError — agent accessed a list-of-dicts result using integer indices instead of field names.

**Correct approach:**
Always wrap tool results in pd.DataFrame() before field access. Use df['field_name'] not result[0]. Check result type with type(result) before processing.

**Example:**

```
import pandas as pd
# records is a list of dicts from query_db
df = pd.DataFrame(records)
# now access fields by name
value = df['field_name']
```

---

## Correction 036 — 2026-04-18 [AUTO]

**Dataset:** stockmarket | **Query ID:** 3
**Failure pattern:** Incorrect numeric computation

**What was wrong:**
stockmarket Q3: agent returned a numeric answer but the value was computed incorrectly — likely due to integer truncation or incomplete data.

**Correct approach:**
Always CAST numeric columns to FLOAT before computing AVG in DuckDB: AVG(CAST(column AS FLOAT)). Always set MongoDB query limit to 10000 to avoid missing documents. Verify join key normalisation: strip prefixes before merging DataFrames.

**Example:**

```
-- DuckDB: cast before averaging
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)

-- MongoDB: always set explicit limit
{"collection": "business", "filter": {}, "limit": 10000}
```

---

## Correction 037 — 2026-04-18 [AUTO]

**Dataset:** stockmarket | **Query ID:** 4
**Failure pattern:** TypeError — integer index used on dict result

**What was wrong:**
stockmarket Q4: agent hit max_iterations. execute_python failed with TypeError — agent accessed a list-of-dicts result using integer indices instead of field names.

**Correct approach:**
Always wrap tool results in pd.DataFrame() before field access. Use df['field_name'] not result[0]. Check result type with type(result) before processing.

**Example:**

```
import pandas as pd
# records is a list of dicts from query_db
df = pd.DataFrame(records)
# now access fields by name
value = df['field_name']
```

---

## Correction 038 — 2026-04-18 [AUTO]

**Dataset:** stockmarket | **Query ID:** 5
**Failure pattern:** TypeError — integer index used on dict result

**What was wrong:**
stockmarket Q5: agent hit max_iterations. execute_python failed with TypeError — agent accessed a list-of-dicts result using integer indices instead of field names.

**Correct approach:**
Always wrap tool results in pd.DataFrame() before field access. Use df['field_name'] not result[0]. Check result type with type(result) before processing.

**Example:**

```
import pandas as pd
# records is a list of dicts from query_db
df = pd.DataFrame(records)
# now access fields by name
value = df['field_name']
```

---

## Correction 039 — 2026-04-18 [AUTO]

**Dataset:** GITHUB_REPOS | **Query ID:** 2
**Failure pattern:** TypeError — integer index used on dict result

**What was wrong:**
GITHUB_REPOS Q2: agent hit max_iterations. execute_python failed with TypeError — agent accessed a list-of-dicts result using integer indices instead of field names.

**Correct approach:**
Always wrap tool results in pd.DataFrame() before field access. Use df['field_name'] not result[0]. Check result type with type(result) before processing.

**Example:**

```
import pandas as pd
# records is a list of dicts from query_db
df = pd.DataFrame(records)
# now access fields by name
value = df['field_name']
```

---

## Correction 040 — 2026-04-18 [AUTO]

**Dataset:** GITHUB_REPOS | **Query ID:** 3
**Failure pattern:** NaN/NameError in execute_python

**What was wrong:**
GITHUB_REPOS Q3: agent hit max_iterations. execute_python failed repeatedly with NameError — bare `nan` used instead of a valid null representation.

**Correct approach:**
Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). Always add `import numpy as np` before using np.nan.

**Example:**

```
import numpy as np
import pandas as pd
# correct null handling
df = df.replace(float('nan'), np.nan)
df = df.dropna(subset=['required_column'])
```

---

## Correction 041 — 2026-04-18 [AUTO]

**Dataset:** GITHUB_REPOS | **Query ID:** 4
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
GITHUB_REPOS Q4: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 40493. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 042 — 2026-04-18 [AUTO]

**Dataset:** PANCANCER_ATLAS | **Query ID:** 2
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
PANCANCER_ATLAS Q2: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 34711. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.

---

## Correction 043 — 2026-04-18 [AUTO]

**Dataset:** PANCANCER_ATLAS | **Query ID:** 3
**Failure pattern:** Incorrect numeric computation

**What was wrong:**
PANCANCER_ATLAS Q3: agent returned a numeric answer but the value was computed incorrectly — likely due to integer truncation or incomplete data.

**Correct approach:**
Always CAST numeric columns to FLOAT before computing AVG in DuckDB: AVG(CAST(column AS FLOAT)). Always set MongoDB query limit to 10000 to avoid missing documents. Verify join key normalisation: strip prefixes before merging DataFrames.

**Example:**

```
-- DuckDB: cast before averaging
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)

-- MongoDB: always set explicit limit
{"collection": "business", "filter": {}, "limit": 10000}
```

---

## Correction 044 — 2026-04-18 [AUTO]

**Dataset:** PATENTS | **Query ID:** 2
**Failure pattern:** Required entity name missing from answer

**What was wrong:**
PATENTS Q2: agent returned an answer but a required entity name or identifier was absent — likely queried the wrong field or database.

**Correct approach:**
Verify which database and field holds the entity name for this dataset. Use list_db to inspect available collections and tables before querying. For Yelp: business names are in MongoDB business collection 'name' field. For bookreview: book titles are in PostgreSQL books_info 'title' field.

**Example:**

```
# Always verify field existence before selecting
import pandas as pd
df = pd.DataFrame(records)
print(df.columns.tolist())  # confirm 'name' or 'title' field exists
```

---

## Correction 045 — 2026-04-18 [AUTO]

**Dataset:** PATENTS | **Query ID:** 3
**Failure pattern:** Answer returned but failed validation

**What was wrong:**
PATENTS Q3: agent returned an answer that did not pass validation. Terminate reason: llm_response_failed (APIStatusError): Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 31570. To increase, visit https://openrouter.ai/settings/keys and create a key with a higher weekly limit', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'org_3B7LqR6KG0MSzOr4fEskO8X8zKr'}. The failure category could not be automatically classified from tool call logs.

**Correct approach:**
Inspect the tool_calls.jsonl log for this query to identify which step produced the incorrect intermediate result. Check join keys, field names, and database routing.
