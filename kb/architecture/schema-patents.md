# Schema: PATENTS

- **DAB folder:** `query_PATENTS`
- **Domain:** Intellectual property / patent analytics
- **DB systems:** SQLite (patent publications) + PostgreSQL (CPC classification hierarchy)
- **Cross-DB join key:** CPC symbol codes — extracted from `publicationinfo.cpc` JSON array, matched to `cpc_definition.symbol`

---

## DB 1 — publication_database (SQLite)

### publicationinfo

| Column | Type | Notes |
|---|---|---|
| Patents_info | str | Natural language summary of the patent (publication number, app number, status) |
| kind_code | str | Publication kind description (e.g. type of document issued) |
| application_kind | str | e.g. `utility patent application` |
| pct_number | str | PCT application number if applicable |
| family_id | str | Links related patents in the same family — stored as string |
| title_localized | str | Patent title |
| abstract_localized | str | Patent abstract |
| claims_localized_html | str | Claims section in HTML — strip tags before text analysis |
| description_localized_html | str | Description section in HTML — strip tags before text analysis |
| publication_date | str | Natural language date (e.g. `March 15th, 2020`) — must parse to datetime for sorting |
| filing_date | str | Natural language date — must parse before date comparisons |
| grant_date | str | Natural language date — must parse before date comparisons |
| priority_date | str | Natural language date — must parse before date comparisons |
| priority_claim | str | List of priority applications |
| inventor_harmonized | str | Harmonized inventor list |
| examiner | str | USPTO examiner(s) |
| uspc | str | US Patent Classification code(s) |
| ipc | str | International Patent Classification code(s) |
| cpc | str | JSON-like list of CPC objects — each has `symbol` and metadata. **Cross-DB join source.** |
| citation | str | Cited patents and non-patent literature |
| parent | str | Parent patent applications |
| child | str | Child patent applications |
| entity_status | str | e.g. `small entity`, `large entity` |
| art_unit | str | USPTO art unit |

**Gotcha:** All date fields (`publication_date`, `filing_date`, `grant_date`, `priority_date`) are natural language strings. Use `dateparser.parse()` or `pd.to_datetime(..., format='mixed')` — do NOT use `ORDER BY date_column` directly.

**Gotcha:** `claims_localized_html` and `description_localized_html` contain HTML tags. Strip with `BeautifulSoup` or `re.sub(r'<[^>]+>', '', text)` before any text analysis.

**Gotcha:** `cpc` is a JSON-like list of objects. To join with cpc_definition, parse each entry and extract `symbol`. Example:
```python
import json
cpc_entries = json.loads(row['cpc'])  # list of dicts
symbols = [entry['symbol'] for entry in cpc_entries if 'symbol' in entry]
```

---

## DB 2 — CPCDefinition_database (PostgreSQL)

### cpc_definition

| Column | Type | Notes |
|---|---|---|
| symbol | str | CPC classification code — **cross-DB join key** |
| titleFull | str | Full descriptive title of the CPC symbol |
| titlePart | str | Abbreviated title |
| definition | str | Full definition of the CPC symbol |
| level | int | Hierarchy level (1 = top, 5 = most specific) |
| parents | str | JSON-like list of parent CPC symbols |
| childGroups | str | JSON-like list of child CPC symbols at next level |
| children | str | Additional child references (JSON-like) |
| status | str | `active` or `deleted` |
| breakdownCode | bool | Whether this is a breakdown (non-allocatable) code |
| notAllocatable | bool | True if this code cannot be assigned to a patent |
| dateRevised | str | Revision date in natural language format |
| glossary | str | Glossary terms for the symbol |
| ipcConcordant | str | Mapped IPC code if applicable |
| applicationReferences | str | Informative references |
| informativeReferences | str | Additional references |
| limitingReferences | str | Scope-limiting references |
| scopeLimitingReferences | str | Additional scope limits |
| precedenceLimitingReferences | str | Precedence-limiting references |
| residualReferences | str | Residual references |
| rules | str | Interpretation rules |
| synonyms | str | Synonyms for the CPC symbol |

**Gotcha:** Only query `notAllocatable = false` and `status = 'active'` records when looking up patents' CPC codes. Breakdown and deleted codes are not assigned to real patents.

**Gotcha:** CPC hierarchy traversal (finding all patents in a subtree) requires following `childGroups` recursively — stored as JSON-like arrays. This is expensive; filter by `level` first to narrow the target subtree.

---

## Cross-Database Join

**No direct SQL join is possible.** The `cpc` field in SQLite `publicationinfo` is a JSON array of objects; the join key must be extracted in Python.

**Procedure:**
1. Query `publicationinfo` from SQLite — select relevant patents.
2. Parse `cpc` field: extract `symbol` values from each JSON object in the array.
3. Query `cpc_definition` from PostgreSQL using those symbols.
4. Merge in Python.

```python
import json, pandas as pd

# Step 1: get patents
patents_df = query_sqlite("SELECT * FROM publicationinfo WHERE ...")

# Step 2: extract CPC symbols
def extract_cpc_symbols(cpc_str):
    try:
        return [e['symbol'] for e in json.loads(cpc_str) if 'symbol' in e]
    except Exception:
        return []

patents_df['cpc_symbols'] = patents_df['cpc'].apply(extract_cpc_symbols)

# Step 3: collect all unique symbols
all_symbols = list({s for syms in patents_df['cpc_symbols'] for s in syms})

# Step 4: query cpc_definition
placeholders = ','.join(['%s'] * len(all_symbols))
cpc_df = query_postgres(
    f"SELECT symbol, titleFull, definition FROM cpc_definition WHERE symbol IN ({placeholders})",
    all_symbols
)
```

---

## Valid Intra-Database Joins

None confirmed within publication_database (single table).

Within CPCDefinition_database, hierarchy traversal uses `parents` / `childGroups` fields (JSON-like self-referential), not SQL foreign keys.

---

## Known Failure Patterns

- Sorting or filtering on date columns directly → wrong order because dates are natural language strings.
- Text-searching `claims_localized_html` without stripping HTML tags → HTML noise in results.
- Joining `cpc` field as a plain string equality to `cpc_definition.symbol` → no matches (it is a JSON array).
- Including `notAllocatable = true` or `status = 'deleted'` CPC codes → lookup of non-real classifications.
- Traversing the CPC hierarchy without filtering by `level` first → runaway recursive expansion.
