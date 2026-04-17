# agnews Dataset — Schema and Domain Knowledge

## Overview

AG News — news articles with metadata (authors, regions, publication dates). Two databases:

- **Articles DB (MongoDB)** — article content
- **Metadata DB (SQLite)** — authors and article metadata

**Join key:** `article_id` (integer on both sides — no prefix stripping needed)

## Schema

### MongoDB — articles collection

| Field | Type | Notes |
|---|---|---|
| _id | ObjectId | MongoDB default |
| article_id | int | Unique identifier, joins to SQLite |
| title | str | Article title |
| description | str | Article description / body |

### SQLite — authors table

| Field | Type | Notes |
|---|---|---|
| author_id | int | Primary key |
| name | str | Full author name |

### SQLite — article_metadata table

| Field | Type | Notes |
|---|---|---|
| article_id | int | Links to MongoDB articles.article_id |
| author_id | int | Links to authors.author_id |
| region | str | Geographic publication region |
| publication_date | str | Format: YYYY-MM-DD |

## Authoritative Sources

- **Article content (title, description)** → MongoDB `articles` collection
- **Author info, region, date** → SQLite `authors` + `article_metadata`

## Cross-Database Join Strategy

**MongoDB ↔ SQLite** — no native JOIN. Query each separately, merge in Python:

```python
import pandas as pd

# MongoDB side
articles = list(mongo_db.articles.find({}, {"_id": 0}))
df_articles = pd.DataFrame(articles)

# SQLite side — join metadata and authors
df_metadata = pd.read_sql(
    "SELECT m.article_id, m.author_id, m.region, m.publication_date, a.name "
    "FROM article_metadata m JOIN authors a ON m.author_id = a.author_id",
    sqlite_conn
)

# Merge on article_id (integer, both sides)
merged = pd.merge(df_articles, df_metadata, on='article_id')
```

**Join key format:** `article_id` is integer on both sides. Direct comparison works — no prefix stripping like Yelp.

## Known Failure Patterns to Watch

1. **Text search on wrong side** — article text is in MongoDB (`title`, `description`), not SQLite.
2. **Author names not in MongoDB** — the articles collection has no author field. Must join to SQLite.
3. **Date format** — `publication_date` is string format `YYYY-MM-DD`, not a DATE type. Use string comparison or parse before filtering.
4. **Region is free-text** — not normalized. Same region may appear with slight variations.

## Query Volume

4 queries in DAB benchmark for this dataset.
