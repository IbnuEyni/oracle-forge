# music_brainz Dataset Schema Description

## Overview
- **Domain**: Music industry analytics (tracks, artists, albums, and sales)
- **Databases used**: SQLite (`tracks_database`) + DuckDB (`sales_database`)
- **Key characteristic**: Requires joining track metadata with sales data while performing entity resolution due to duplicate track entries.

## Main Tables & Purpose

**1. tracks (SQLite - tracks_database)**
- Primary source for track metadata.
- Contains detailed information about tracks, including duplicates from different sources.
- Key fields: `track_id`, `source_track_id`, `title`, `artist`, `album`, `year`, `length`, `language`

**2. sales (DuckDB - sales_database)**
- Contains sales transactions linked to tracks.
- Key fields: `sale_id`, `track_id`, `country`, `store`, `units_sold`, `revenue_usd`

## Key Join Keys & Gotchas
- Primary join key: `track_id`
- Major challenge: **Entity resolution** — the `tracks` table has many duplicate entries for the same real-world track (different `track_id` but similar title/artist/album/year).
- `source_track_id` is unreliable for joining.
- Minor variations in artist names, titles, or year formats are common.

## Unstructured / Semi-structured Fields
- `title`, `artist`, `album` — may have small spelling or formatting variations.

## Known Failure Patterns
- Agent joins directly on `track_id` without resolving duplicates → inflated revenue or sales counts
- Agent treats every `track_id` as a unique track → incorrect artist-level statistics
- Agent relies only on exact string matching → misses near-duplicate tracks

## Practical Guidance for the Agent
- Always perform entity resolution on the `tracks` table first by grouping on (`title`, `artist`, `album`, `year`).
- Resolve tracks to unique real-world songs **before** joining with the `sales` table.
- Apply artist filters and aggregations at the resolved track level, not on individual `track_id` rows.
- Use `revenue_usd` from the `sales` table for all revenue calculations.
- Be cautious with variations in artist names and year formats.

This dataset is excellent for testing multi-database joins combined with entity resolution.
