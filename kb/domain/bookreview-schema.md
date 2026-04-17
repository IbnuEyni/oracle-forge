# bookreview Dataset — Schema and Domain Knowledge

## Overview

Book catalog with customer reviews. Two databases:

- **Books DB (PostgreSQL)** — book catalog and metadata
- **Review DB (SQLite)** — individual review records

**Join key:** `book_id` (PostgreSQL) ↔ `purchase_id` (SQLite)

## Schema

### PostgreSQL — books_info table

| Field | Type | Notes |
|---|---|---|
| book_id | str | Unique book identifier — join key to SQLite review.purchase_id |
| title | str | Book title |
| author | str | Book author(s) |
| price | float | Book price |
| (additional fields) | — | Product details and descriptions |

### SQLite — review table

| Field | Type | Notes |
|---|---|---|
| rating | float | Rating on 1.0-5.0 scale |
| text | str | Review text content |
| purchase_id | str | Links to books_info.book_id |

## Authoritative Sources

- **Book metadata (title, author, price)** → PostgreSQL `books_info` table
- **Review content and ratings** → SQLite `review` table

## Cross-Database Join Strategy

**No native JOIN across PostgreSQL and SQLite.** Query each separately, merge in Python:

```python
import pandas as pd

# PostgreSQL side
df_books = pd.read_sql("SELECT * FROM books_info", pg_conn)

# SQLite side
df_reviews = pd.read_sql("SELECT * FROM review", sqlite_conn)

# Merge on the join key — PostgreSQL book_id == SQLite purchase_id
merged = pd.merge(
    df_reviews,
    df_books,
    left_on='purchase_id',
    right_on='book_id',
    how='inner'
)
```

**Key naming convention:** PostgreSQL calls it `book_id`, SQLite calls it `purchase_id`. Same values, different column names. Use `left_on` / `right_on` in `pd.merge`, or rename one side before joining.

## Key Distinctions: Per-Book vs Per-Review Data

| Query asks about | Source |
|---|---|
| Average rating per book | Aggregate `SQLite review.rating` grouped by `purchase_id`, then join to `books_info` |
| Book price | `PostgreSQL books_info.price` |
| Review text search | `SQLite review.text` (not PostgreSQL) |
| Book title or author | `PostgreSQL books_info` |
| Total review count per book | `COUNT(*)` on `SQLite review` grouped by `purchase_id` |

## Known Failure Patterns to Watch

1. **Wrong join column** — `book_id` is NOT the same column name in both databases. PostgreSQL uses `book_id`, SQLite uses `purchase_id`. Must use `left_on` / `right_on` or rename before merging.
2. **Rating type handling** — rating is `float` (1.0-5.0), not integer. No BIGINT truncation issue like Yelp, but still cast to FLOAT defensively.
3. **Text search on wrong side** — review text is in SQLite, not PostgreSQL. Author names are in PostgreSQL, not SQLite.
4. **Nested list fields** — the books_info table may have list-encoded fields (like categories) stored as string representations. Use `ast.literal_eval()` to parse before filtering.
5. **Aggregation boundary** — when computing per-book statistics from reviews, GROUP BY `purchase_id` in SQLite BEFORE joining to PostgreSQL, or the merge will explode row counts.

## Query Volume

3 queries in DAB benchmark for this dataset.

## Additional Notes

- Two database types only (PostgreSQL + SQLite) — no MongoDB, no DuckDB for this dataset
- File-based SQLite means no connection service needed — agent picks up the file directly
- PostgreSQL requires `CREATE DATABASE` and SQL import before running (as confirmed in Amir's Sprint 2 notes)
