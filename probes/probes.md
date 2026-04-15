# Adversarial Probe Library — Oracle Forge / BLOOM Team

**Format:** Query | Failure Category | Expected Failure | Observed Failure | Fix Applied | Post-fix Score

---

## Category 1: Ill-Formatted Join Keys

### Probe 001
**Query:** Q1, Q2, Q4 (Yelp) — any query joining MongoDB business to DuckDB review
**Failure category:** Ill-formatted join keys
**Expected failure:** Agent joins on raw `business_id` / `business_ref` → zero rows or TypeError
**Observed failure:** `TypeError: list indices must be integers` and wrong answers (3.86 instead of 3.55)
**Fix applied:** Strip `businessid_` / `businessref_` prefix, cast to int, join on integer key
```python
df_business['id'] = df_business['business_id'].str.replace('businessid_', '').astype(int)
df_reviews['id'] = df_reviews['business_ref'].str.replace('businessref_', '').astype(int)
merged = pd.merge(df_reviews, df_business, on='id')
```
**Post-fix score:** Q1 ✅, Q2 ✅ (57.1% overall on Yelp)

---

### Probe 002
**Query:** Q1 (Yelp) — average rating of businesses in Indianapolis
**Failure category:** Ill-formatted join keys
**Expected failure:** AVG(rating) returns integer-truncated result
**Observed failure:** Agent returned 3.86 instead of correct 3.547 — BIGINT truncation
**Fix applied:** `CAST(rating AS FLOAT)` before computing AVG
```sql
SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)
```
**Post-fix score:** Q1 ✅

---

### Probe 003
**Query:** Q2 (Yelp) — state with highest number of reviews
**Failure category:** Ill-formatted join keys + domain knowledge
**Expected failure:** Agent hits MongoDB default 5-document limit, misses 3 of 8 Indianapolis businesses
**Observed failure:** Wrong state returned (MO instead of PA) due to incomplete data
**Fix applied:** Always set MongoDB query limit to 10000
```json
{"collection": "business", "filter": {}, "limit": 10000}
```
**Post-fix score:** Q2 ✅

---

### Probe 004
**Query:** bookreview Q1-Q3 — join books (PostgreSQL) with reviews (SQLite)
**Failure category:** Ill-formatted join keys
**Expected failure:** Agent attempts direct join on `book_id` vs `purchase_id` without verifying format match
**Observed failure:** Empty result or wrong answer when formats differ
**Fix applied:** Verify both sides have same format before joining; use `pd.merge` on normalized key
```python
df_books['id'] = df_books['book_id']
df_reviews['id'] = df_reviews['purchase_id']
merged = pd.merge(df_reviews, df_books, on='id')
```
**Post-fix score:** bookreview Q2 ✅, Q3 ✅

---

### Probe 005
**Query:** Any dataset — agent joins PostgreSQL integer ID with MongoDB string ID
**Failure category:** Ill-formatted join keys
**Expected failure:** `WHERE user_id = userId` returns zero rows — type mismatch
**Observed failure:** Empty result, agent reports "no matching records"
**Fix applied:** Cast both sides to same type before join; strip prefix if present
**Post-fix score:** Resolved in join-key-glossary.md KB doc

---

## Category 2: Multi-Database Integration

### Probe 006
**Query:** Q1 (Yelp) — requires MongoDB (business location) + DuckDB (ratings) in same query
**Failure category:** Multi-database integration
**Expected failure:** Agent queries only DuckDB, ignores MongoDB location data
**Observed failure:** Agent returned `businessref_9 with average rating 4.0` — used raw ref instead of business name
**Fix applied:** Agent must query MongoDB first for location filter, then DuckDB for ratings, merge in Python
**Post-fix score:** Q1 ✅ after hints + corrections injected

---

### Probe 007
**Query:** Q6 (Yelp) — business with highest average rating in a date range
**Failure category:** Multi-database integration
**Expected failure:** Agent returns category name instead of business name — wrong table used
**Observed failure:** Returned `Restaurants, Breakfast & Brunch` instead of `Coffee House Too Cafe`
**Fix applied:** Clarify in hints that business name comes from MongoDB business collection, not DuckDB category field
**Post-fix score:** Q6 ✅

---

### Probe 008
**Query:** Q7 (Yelp) — top 5 business categories by review count
**Failure category:** Multi-database integration
**Expected failure:** Agent passes list where string path expected when reading stored results
**Observed failure:** `TypeError: expected str, bytes or os.PathLike object, not list`
**Fix applied:** Check type before passing to `open()` — use `json.dumps()` if result is already dict/list
**Post-fix score:** Q7 partially resolved

---

### Probe 009
**Query:** crmarenapro — requires PostgreSQL (core CRM) + DuckDB (sales pipeline) in same query
**Failure category:** Multi-database integration
**Expected failure:** Agent queries only one database, misses cross-DB join requirement
**Observed failure:** No runs completed yet — identified as gap
**Fix applied:** Pending — db_config.yaml shows 4 databases; agent must route sub-queries correctly
**Post-fix score:** Pending

---

### Probe 010
**Query:** Any dataset — agent uses `list_db` but then queries wrong database type
**Failure category:** Multi-database integration
**Expected failure:** Agent calls `list_db`, sees multiple databases, queries PostgreSQL for data that lives in MongoDB
**Observed failure:** Empty result or schema error
**Fix applied:** KB domain docs map which data lives in which database per dataset
**Post-fix score:** Mitigated by dab_schema_descriptions.md injection

---

## Category 3: Unstructured Text Transformation

### Probe 011
**Query:** Q2 (Yelp) — extract US state from business description field
**Failure category:** Unstructured text transformation
**Expected failure:** Agent treats `description` as opaque text, cannot extract state
**Observed failure:** Wrong state returned — agent did not parse the `City, ST ZIPCODE` pattern
**Fix applied:** Regex extraction in hints: `df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})\s*\d{5}')`
**Post-fix score:** Q2 ✅

---

### Probe 012
**Query:** Q3 (Yelp) — businesses offering parking or bike parking
**Failure category:** Unstructured text transformation
**Expected failure:** Agent looks for a `parking` column — none exists; attributes stored as nested dict in `attributes` field
**Observed failure:** "None of the businesses offered parking" — agent did not parse nested attributes
**Fix applied:** Hints document that `attributes` field is a nested dict requiring `ast.literal_eval()` or JSON parsing
**Post-fix score:** Q3 ✅ after hints added

---

### Probe 013
**Query:** Q4 (Yelp) — businesses accepting credit cards
**Failure category:** Unstructured text transformation
**Expected failure:** Agent looks for `accepts_credit_card` column — stored inside `attributes` nested dict
**Observed failure:** "No businesses accept credit card" — agent did not parse attributes dict
**Fix applied:** Same as Probe 012 — attributes field parsing documented in hints
**Post-fix score:** Q4 inconsistent — further investigation needed

---

### Probe 014
**Query:** bookreview — extract category from `categories` field stored as string representation of list
**Failure category:** Unstructured text transformation
**Expected failure:** Agent treats `categories` as plain string, cannot filter by category
**Observed failure:** Wrong category match or empty result
**Fix applied:** `ast.literal_eval()` to parse string-encoded list fields in bookreview PostgreSQL table
**Post-fix score:** bookreview Q2 ✅, Q3 ✅

---

## Category 4: Domain Knowledge Gaps

### Probe 015
**Query:** Q5 (Yelp) — state with highest average rating (requires knowing rating is per-review, not per-business)
**Failure category:** Domain knowledge gaps
**Expected failure:** Agent averages `review_count` from MongoDB (a count field, not a rating) instead of `rating` from DuckDB
**Observed failure:** Wrong state or wrong number returned
**Fix applied:** Hints explicitly state: "Always compute average ratings from the DuckDB review table's rating field, not from MongoDB review_count metadata"
**Post-fix score:** Q5 inconsistent — model-dependent

---

### Probe 016
**Query:** Any dataset — agent interprets "active customer" as any customer with a row
**Failure category:** Domain knowledge gaps
**Expected failure:** Agent counts all customers as active — no domain definition applied
**Observed failure:** Inflated active customer count, wrong churn rate
**Fix applied:** domain_term_definitions.md injected — defines active customer as previously transacting, not just present in table
**Post-fix score:** Mitigated by KB v2 domain_term_definitions.md

---

### Probe 017
**Query:** Any dataset — agent uses calendar year Q3 when fiscal Q3 is different
**Failure category:** Domain knowledge gaps
**Expected failure:** Agent assumes Q3 = July-September; dataset uses different fiscal calendar
**Observed failure:** Wrong period filter, wrong aggregation result
**Fix applied:** domain_term_definitions.md documents fiscal year boundary ambiguity — agent must check dataset metadata
**Post-fix score:** Mitigated by KB v2 injection

---

## Summary

| Probe | Dataset | Failure Category | Status |
|---|---|---|---|
| 001 | Yelp | Ill-formatted join keys | Fixed ✅ |
| 002 | Yelp | Ill-formatted join keys | Fixed ✅ |
| 003 | Yelp | Ill-formatted join keys | Fixed ✅ |
| 004 | bookreview | Ill-formatted join keys | Fixed ✅ |
| 005 | Generic | Ill-formatted join keys | Mitigated ✅ |
| 006 | Yelp | Multi-database integration | Fixed ✅ |
| 007 | Yelp | Multi-database integration | Fixed ✅ |
| 008 | Yelp | Multi-database integration | Partial ⚠️ |
| 009 | crmarenapro | Multi-database integration | Pending 🔲 |
| 010 | Generic | Multi-database integration | Mitigated ✅ |
| 011 | Yelp | Unstructured text transformation | Fixed ✅ |
| 012 | Yelp | Unstructured text transformation | Fixed ✅ |
| 013 | Yelp | Unstructured text transformation | Partial ⚠️ |
| 014 | bookreview | Unstructured text transformation | Fixed ✅ |
| 015 | Yelp | Domain knowledge gaps | Partial ⚠️ |
| 016 | Generic | Domain knowledge gaps | Mitigated ✅ |
| 017 | Generic | Domain knowledge gaps | Mitigated ✅ |

**Total: 17 probes across all 4 DAB failure categories.**
