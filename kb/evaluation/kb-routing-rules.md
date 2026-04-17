# KB Routing Rules

## Purpose

Selective KB injection. Match the query to only the KB documents it needs. Do not inject the entire KB by default.

**RULE:** Default injection is minimal. Add documents based on keyword matches, dataset, and query structure. Total injected KB should stay under 8,000 characters per session.

## Always Inject (Base Context)

These documents inject on every query regardless of content:

| Document | Reason |
|---|---|
| `kb/architecture/agent-rules.md` | Non-negotiable safety and boundary rules |
| `kb/corrections/self-check-protocol.md` | Final verification before answer submission |
| `kb/corrections/{dataset}-corrections.md` | Dataset-specific known failures (e.g. yelp-corrections.md) |

## Query-Type Routing

Match keywords in the user query. Inject the mapped documents. If multiple patterns match, inject all matched docs.

### Pattern 1: Join / Cross-Database Questions

**Keywords:** `join`, `across`, `combine`, `merge`, `both`, `and the`, `relate`

**Inject:**
- `kb/domain/join-key-glossary.md`
- `kb/architecture/oracle-forge-schema.md` (schema section for the dataset)

**Why:** Cross-database joins fail on prefix format mismatches. Agent needs normalization patterns.

### Pattern 2: Aggregation Questions

**Keywords:** `average`, `sum`, `count`, `total`, `highest`, `lowest`, `most`, `least`, `top`, `rank`

**Inject:**
- `kb/corrections/{dataset}-corrections.md` (filter-before-aggregate patterns)
- `kb/domain/dab-failure-categories.md` (aggregation failure modes)

**Why:** Filter-order errors and wrong-table errors cluster on aggregation queries.

### Pattern 3: Unstructured Text Questions

**Keywords:** `reason`, `why`, `complaint`, `feedback`, `review`, `mention`, `describe`, `category`

**Inject:**
- `kb/domain/unstructured-field-inventory.md`

**Why:** Agent must extract from free-text fields when no structured column exists.

### Pattern 4: Business Term Questions

**Keywords:** `churn`, `revenue`, `fiscal`, `quarter`, `segment`, `active`, `customer`, `power user`

**Inject:**
- `kb/domain/domain_term_definitions.md`

**Why:** Business definitions vary. Agent must use our documented definitions, not pretraining guesses.

### Pattern 5: Schema Discovery Questions

**Keywords:** `what field`, `which table`, `what column`, `does the database`, `is there a`

**Inject:**
- `kb/architecture/oracle-forge-schema.md` (full schema)
- `kb/domain/dab_schema_descriptions.md`

**Why:** Agent needs complete schema to answer discovery questions correctly.

### Pattern 6: State / Location Questions

**Keywords:** `state`, `city`, `location`, `address`, `country`, `region`

**Inject:**
- `kb/corrections/{dataset}-corrections.md` (state extraction patterns)

**Why:** State info may be buried in `description` field, not a dedicated column. Agent needs regex extraction pattern.

## Dataset-Specific Overrides

### Yelp

- Always inject `kb/corrections/yelp-corrections.md`
- Key failure modes: `businessid_`/`businessref_` join prefix, MongoDB stars vs DuckDB review.stars, state extraction from description

### bookreview

- Always inject `kb/corrections/bookreview-corrections.md` (when created)
- Key database types: PostgreSQL + SQLite

### All Other Datasets

- If no dataset-specific corrections file exists yet, inject `kb/domain/dab-failure-categories.md` as generic fallback

## Budget Caps

| Component | Max chars |
|---|---|
| Base context (always inject) | 2,500 |
| Query-type matches (per query) | 4,000 |
| Dataset-specific corrections | 1,500 |
| **Total per session** | **8,000** |

If the matched documents exceed 8,000 chars total, drop in this priority order:
1. Keep: corrections for this dataset
2. Keep: self-check protocol
3. Keep: highest-confidence query-type match
4. Drop: lower-priority query-type matches
5. Drop: agent-rules.md (last resort only)

## Pseudocode for Amir

```python
def select_kb_for_query(query_text: str, dataset: str) -> str:
    docs = []
    query_lower = query_text.lower()

    # Always inject
    docs.append(read("kb/architecture/agent-rules.md"))
    docs.append(read("kb/corrections/self-check-protocol.md"))

    # Dataset-specific corrections
    dataset_file = f"kb/corrections/{dataset}-corrections.md"
    if exists(dataset_file):
        docs.append(read(dataset_file))
    else:
        docs.append(read("kb/domain/dab-failure-categories.md"))

    # Pattern matching
    join_keywords = ["join", "across", "combine", "merge", "both", "relate"]
    if any(k in query_lower for k in join_keywords):
        docs.append(read("kb/domain/join-key-glossary.md"))

    agg_keywords = ["average", "sum", "count", "total", "highest", "lowest", "most", "least", "top", "rank"]
    if any(k in query_lower for k in agg_keywords):
        docs.append(read("kb/domain/dab-failure-categories.md"))

    text_keywords = ["reason", "why", "complaint", "feedback", "review", "mention", "describe"]
    if any(k in query_lower for k in text_keywords):
        docs.append(read("kb/domain/unstructured-field-inventory.md"))

    term_keywords = ["churn", "revenue", "fiscal", "quarter", "segment", "active", "customer"]
    if any(k in query_lower for k in term_keywords):
        docs.append(read("kb/domain/domain_term_definitions.md"))

    schema_keywords = ["what field", "which table", "what column", "does the database"]
    if any(k in query_lower for k in schema_keywords):
        docs.append(read("kb/architecture/oracle-forge-schema.md"))
        docs.append(read("kb/domain/dab_schema_descriptions.md"))

    location_keywords = ["state", "city", "location", "address", "country", "region"]
    if any(k in query_lower for k in location_keywords):
        pass  # Already covered by dataset corrections

    # Dedupe
    docs = list(dict.fromkeys(docs))

    # Budget enforcement
    combined = "\n\n".join(docs)
    if len(combined) > 8000:
        combined = enforce_budget(docs, max_chars=8000)

    return combined
```

## Validation

Before deploying:
1. Run 3 queries from different pattern types
2. Log which KB docs were injected for each
3. Confirm total chars stays under 8,000
4. Confirm previously-passing queries still pass after switch from full-KB to selective

If previously-passing queries regress, the routing is missing something. Check injection logs for missing context.

## Why This Exists

Full KB injection is 25,000+ characters and growing. Our Run 4 regression (57% → 28% on Yelp) correlates with the switch from hints-only to full-KB injection. Selective injection hypothesis: the agent was overloaded with irrelevant context, crowding out reasoning space.

This routing reduces injected context by 60-70% per query while keeping the relevant docs. Test this against the Run 4 regression: if selective injection restores the 57% baseline, context overload was the cause.
