# Yelp Dataset -- Corrections Log

## Purpose

This document logs query failures from the Yelp dataset runs so the agent does not repeat the same mistakes. Each entry describes what went wrong, why, and what the agent should do differently.

**RULE:** Before running a Yelp query, check this log for known failure patterns. If the query matches a previous failure, apply the correction before executing.

## Query Corrections

### Q1: Wrong average rating (3.86 vs expected 3.55)

**Error:** Agent returned incorrect average rating.
**Root cause:** Agent used MongoDB `business.stars` (pre-aggregated average) instead of calculating the average from individual review records in DuckDB `review.stars`. Both columns are valid schema fields, but `business.stars` is a summary while `review.stars` has per-review ratings.
**Correction:** When a query asks for an average calculated from reviews, aggregate from DuckDB `review.stars`. Use MongoDB `business.stars` only when the query explicitly asks for the business-level rating.

### Q2: Wrong state (MO vs expected PA)

**Error:** Agent returned Missouri instead of Pennsylvania.
**Root cause:** Agent counted the `review_count` summary field in MongoDB instead of counting actual review records in DuckDB. Also, state info was extracted from the `description` field using string parsing, not a dedicated `state` column.
**Correction:** Count actual records in DuckDB `review` table. Extract state with: `df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})')`.

### Q2 (later runs): Answer format rejected

**Error:** Answer was technically correct but validator rejected it.
**Root cause:** The state abbreviation (PA) was more than 50 characters away from the number in the response string.
**Correction:** Keep answer values close together. Format: "PA with 4,523 reviews" not a long explanation with values separated by paragraphs.

### Q4: Wrong average (3.57 vs expected 3.633)

**Error:** Agent returned incorrect average for credit-card-accepting businesses.
**Root cause:** Agent averaged all businesses instead of filtering to credit-card-accepting ones first.
**Correction:** Apply filters BEFORE aggregation. Check the `attributes` field in MongoDB for `BusinessAcceptsCreditCards: True` before joining to DuckDB for rating calculation.

### Q1, Q2, Q4, Q7: Wrong join key

**Error:** Agent joins DuckDB review table with MongoDB business collection using wrong key format.
**Root cause:** DuckDB uses `business_ref` (e.g. `businessref_9`), MongoDB uses `business_id` (e.g. `businessid_9`). Agent attempted direct join without resolving the prefix difference.
**Correction:** Strip prefixes before joining:
```python
df_reviews['id'] = df_reviews['business_ref'].str.replace('businessref_', '').astype(int)
df_business['id'] = df_business['business_id'].str.replace('businessid_', '').astype(int)
merged = pd.merge(df_reviews, df_business, on='id')
```

## Key Patterns

| Pattern | Frequency | Fix |
|---|---|---|
| Used pre-aggregated field instead of raw records | Q1, Q2 | Aggregate from DuckDB review table, not MongoDB summary fields |
| Filter applied after aggregation | Q4 | Apply WHERE/filter before GROUP BY |
| Join key prefix mismatch | Q1, Q2, Q4, Q7 | Strip `businessid_`/`businessref_` prefixes, join on integer |
| Answer format too spread out | Q2 | Keep values within 50 chars of each other |

## Yelp-Specific Rules

1. **DuckDB `review` table is authoritative for review-level data** -- use for counting and averaging individual reviews
2. **MongoDB `business` collection is authoritative for business attributes** -- location, categories, credit card acceptance, pre-aggregated stats
3. **Join key:** MongoDB `business_id` (`businessid_` prefix) maps to DuckDB `business_ref` (`businessref_` prefix) -- strip prefixes, join on integer
4. **State extraction:** Use `description` field with regex `r',\s*([A-Z]{2})'` -- no dedicated state column in all contexts
5. **Filter before aggregate** -- apply all conditions before GROUP BY
6. **Keep answers compact** -- validator checks proximity of values in response

---

## Operational Notes

These are not agent reasoning corrections but infrastructure/tooling issues observed during runs.

- **Q5:** Non-deterministic results -- same query passes/fails across runs. LLM limitation, no KB fix. Consider temperature=0.
- **Q7:** `TypeError: expected str not list` -- agent passed list where file path expected. Code-level fix in result handling.
- **gemini-2.5-flash:** Produces no tool calls. Too weak for this task. Use gemini-2.0-flash minimum.
- **Rate limiting:** 250 requests/day quota on Gemini free tier. Plan evaluation runs accordingly.
