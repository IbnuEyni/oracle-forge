# Schema: music_brainz_20k

- **DAB folder:** `query_music_brainz_20k`
- **Domain:** Music / entertainment analytics
- **DB systems:** SQLite (tracks) + DuckDB (sales)
- **Cross-DB join key:** `track_id` (integer, appears clean — no prefix issues)

---

## DB 1 — tracks_database (SQLite)

### tracks

| Column | Type | Notes |
|---|---|---|
| track_id | int | Primary identifier for this DB |
| source_id | int | Which source the record came from — duplicates possible across sources |
| source_track_id | str | Original ID from the source system; NOT unique |
| title | str | Track title |
| artist | str | Artist or band name |
| album | str | Album name |
| year | str | Publication year — stored as string, not integer |
| length | str | Track duration — stored as string (seconds or formatted); parse before numeric ops |
| language | str | Language of the track |

**Gotcha:** `year` and `length` are strings. Cast before filtering or sorting numerically.
**Gotcha:** Duplicate track records exist across different `source_id` values. If counting or aggregating tracks, decide whether to deduplicate by `source_track_id` first.

---

## DB 2 — sales_database (DuckDB)

### sales

| Column | Type | Notes |
|---|---|---|
| sale_id | int | Primary key for this table |
| track_id | int | Foreign key → tracks_database.tracks.track_id |
| country | str | Country where sale occurred |
| store | str | Store or platform (e.g. streaming service) |
| units_sold | int | Units sold in this transaction |
| revenue_usd | double | Revenue in USD |

---

## Cross-Database Join

| From | Key | To |
|---|---|---|
| sales_database.sales.track_id | integer (clean) | tracks_database.tracks.track_id |

**Merge in Python.** Query each database separately and join on `track_id` in a DataFrame.

```python
import pandas as pd
# tracks from SQLite, sales from DuckDB
df = pd.merge(tracks_df, sales_df, on="track_id", how="inner")
```

---

## Valid Intra-Database Joins

None confirmed within tracks_database (single table).
None confirmed within sales_database (single table).

---

## Known Failure Patterns

- Treating `year` or `length` as numeric without casting → TypeError or wrong results.
- Aggregating sales without joining tracks first → missing artist/album context.
- Counting unique tracks using `track_id` alone without accounting for source duplicates.
- Assuming all track_ids in sales exist in tracks (orphan sales records may exist).
