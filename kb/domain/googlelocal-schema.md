# googlelocal Dataset — Schema and Domain Knowledge

## Overview

Google Maps reviews and business metadata from US businesses (through September 2021). Two databases:

- **Review DB (SQLite)** — individual review records
- **Business DB (PostgreSQL)** — business-level metadata

**Join key:** `gmap_id` (shared across both databases)

## Schema

### SQLite — review table (per-review data)

| Field | Type | Notes |
|---|---|---|
| name | str | Reviewer name |
| time | int/str | Review timestamp |
| rating | int | 1-5 scale |
| text | str | Review text content |
| gmap_id | str | Links to business |

### PostgreSQL — business_description table (business metadata)

| Field | Type | Notes |
|---|---|---|
| name | str | Business name |
| gmap_id | str | Primary key, links to review.gmap_id |
| description | str | Business description text |
| review_count | int | Total number of reviews (pre-aggregated) |
| hours | str | Operating hours |
| misc | str | Miscellaneous details |
| status | str | "open", "closed", "temporarily closed" |

## Authoritative Sources

- **Per-review data (actual ratings, text, timestamps)** → SQLite `review` table
- **Business attributes (location, status, hours, description)** → PostgreSQL `business_description` table

**RULE:** To compute average rating, count reviews, or aggregate per-review data, query the SQLite `review` table. Do NOT substitute the PostgreSQL `review_count` summary field for counting actual records.

## Cross-Database Join

**No native JOIN exists across SQLite and PostgreSQL.** Query each separately, merge in Python:

```python
import pandas as pd

# SQLite side
df_reviews = pd.read_sql("SELECT * FROM review WHERE gmap_id IN (...)", sqlite_conn)

# PostgreSQL side
df_business = pd.read_sql("SELECT * FROM business_description WHERE gmap_id IN (...)", pg_conn)

# Merge on gmap_id
merged = pd.merge(df_reviews, df_business, on='gmap_id')
```

**Join key format:** Both sides use `gmap_id` directly. No prefix stripping required (unlike Yelp).

## Known Failure Patterns to Watch

1. **Using PostgreSQL `review_count` for counting** — wrong if the query asks for filtered review counts. Use SQLite `review` table.
2. **Text search on the wrong side** — review text is in SQLite `review.text`, not PostgreSQL. Business description is in PostgreSQL `business_description.description`.
3. **Status field values** — exact strings: "open", "closed", "temporarily closed". Match case and format exactly.

## Query Volume

4 queries in the DAB benchmark for this dataset. Q1 already passing.
