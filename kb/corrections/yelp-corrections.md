# Yelp Dataset -- Corrections Log

## Purpose

This document logs structural query failure patterns from Yelp dataset runs so the agent does not repeat the same mistakes. Each entry describes the failure mechanism and the correction approach. **No ground truth values, no expected answers, and no correct/incorrect numeric outputs are recorded here.** Data leakage into this file would invalidate benchmark results.

**RULE:** Before running a Yelp query, check this log for known failure patterns. If the query matches a pattern, apply the correction before executing.

## Query Corrections

### Pattern A: Average computed from pre-aggregated field

**Failure mechanism:** Agent used MongoDB `business.stars` (pre-aggregated average) instead of calculating the average from individual review records in DuckDB `review.stars`. Both columns are valid schema fields, but `business.stars` is a summary while `review.stars` has per-review ratings.
**Correction:** When a query asks for an average calculated from reviews, aggregate from DuckDB `review.stars`. Use MongoDB `business.stars` only when the query explicitly asks for the business-level rating.

### Pattern B: Counting from summary field instead of actual records

**Failure mechanism:** Agent counted the `review_count` summary field in MongoDB instead of counting actual review records in DuckDB. State info must be extracted from the `description` field using string parsing, not a dedicated `state` column.
**Correction:** Count actual records in DuckDB `review` table. Extract state with: `df['state'] = df['description'].str.extract(r',\s*([A-Z]{2})')`.

### Pattern C: Answer format rejected by validator

**Failure mechanism:** Answer was structurally correct but the validator rejected it because values were spread too far apart in the response string.
**Correction:** Keep answer values close together -- within 50 characters. Avoid long explanatory paragraphs separating the number from the label.

### Pattern D: Filter applied after aggregation

**Failure mechanism:** Agent averaged across the full population instead of filtering to the subset specified in the query before aggregating.
**Correction:** Apply filters BEFORE aggregation. Check the `attributes` field in MongoDB for the relevant boolean conditions before joining to DuckDB for rating calculation.

### Pattern E: Join key prefix mismatch

**Failure mechanism:** Agent joins DuckDB `review` table with MongoDB `business` collection using raw key format. DuckDB uses `business_ref` (e.g. `businessref_N`), MongoDB uses `business_id` (e.g. `businessid_N`). Direct join without resolving the prefix difference returns zero rows.
**Correction:** Strip prefixes before joining:
```python
df_reviews['id'] = df_reviews['business_ref'].str.replace('businessref_', '').astype(int)
df_business['id'] = df_business['business_id'].str.replace('businessid_', '').astype(int)
merged = pd.merge(df_reviews, df_business, on='id')
```

## Key Patterns Summary

| Pattern | Fix |
|---|---|
| Used pre-aggregated field instead of raw records | Aggregate from DuckDB review table, not MongoDB summary fields |
| Filter applied after aggregation | Apply WHERE/filter before GROUP BY |
| Join key prefix mismatch | Strip `businessid_`/`businessref_` prefixes, join on integer |
| Answer format too spread out | Keep values within 50 chars of each other |

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

- **Non-deterministic queries:** same query passes/fails across runs. LLM limitation, no KB fix. Consider temperature=0.
- **TypeError on path reading:** agent passed list where file path expected. Code-level fix in result handling.
- **gemini-2.5-flash:** Produces no tool calls. Too weak for this task. Use gemini-2.0-flash minimum.
- **Rate limiting:** 250 requests/day quota on Gemini free tier. Plan evaluation runs accordingly.

---

## Data Leakage Policy

**This file must never contain:**
- Ground truth answer values (numeric, categorical, or textual)
- Query IDs mapped to specific expected outputs
- Validator output or comparison results
- "Correct" vs "wrong" values for any query

**This file may contain:**
- Structural failure patterns (what went wrong mechanically)
- Correction approaches (how to reason through it)
- Schema references (which table is authoritative for what)
- Normalization patterns (prefix stripping, type casting)

If a correction is written after a run, audit it before committing: does it reference any specific answer value? If yes, rewrite it to describe the pattern without the value.
