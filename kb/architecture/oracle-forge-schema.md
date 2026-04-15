# Oracle Forge: Database Schema & Valid Joins

Source: `tenai_repo/webapp/db.py`, `tenai_repo/scripts/conductor/watcher_db.py`

> **Note:** Sections marked PROVISIONAL are based on the public Yelp/DataAgentBench dataset
> structure and have not been verified against a live database. Update this document once
> actual databases are running and schemas are confirmed.

## Webapp DB (`~/.tenai/tenai.db`)

### devices
| Column | Type | Notes |
|---|---|---|
| name | TEXT | PRIMARY KEY |
| ip | TEXT | |
| user | TEXT | |
| type | TEXT | default: 'server' |
| capabilities | TEXT | JSON array stored as text |
| last_seen | TEXT | ISO timestamp |
| online | INTEGER | 0 or 1 |

### settings
| Column | Type | Notes |
|---|---|---|
| key | TEXT | PRIMARY KEY |
| value | TEXT | |
| updated_at | TEXT | ISO timestamp |

---

## Device DB (`~/.tenai/devices/{name}.db`)

### organizations
| Column | Type | Notes |
|---|---|---|
| name | TEXT | PRIMARY KEY |
| github_url | TEXT | |
| ssh_host_alias | TEXT | |
| ssh_key | TEXT | |
| default_branch | TEXT | default: 'main' |
| created_at | TEXT | ISO timestamp |
| updated_at | TEXT | ISO timestamp |

### repos
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| org | TEXT | FOREIGN KEY → organizations(name) |
| name | TEXT | |
| default_branch | TEXT | default: 'main' |
| description | TEXT | |
| pushed_at | TEXT | |
| last_synced | TEXT | |

UNIQUE constraint: (org, name)

### jobs
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| device | TEXT | |
| org | TEXT | |
| repo | TEXT | |
| cli | TEXT | |
| action | TEXT | |
| branch | TEXT | |
| task_id | INTEGER | |
| command | TEXT | |
| tmux_session | TEXT | |
| status | TEXT | pending / running / done / failed |
| connect_cmd | TEXT | |
| vt_session_id | TEXT | |
| vt_url | TEXT | |
| worktree_md | TEXT | |
| agent_prompt | TEXT | |
| started_at | TEXT | ISO timestamp |
| ended_at | TEXT | ISO timestamp |

### job_logs
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| job_id | INTEGER | FOREIGN KEY → jobs(id) |
| line | TEXT | |
| timestamp | TEXT | ISO timestamp |

### tasks
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| number | INTEGER | |
| title | TEXT | |
| repo | TEXT | |
| org | TEXT | |
| branch | TEXT | |
| base_branch | TEXT | default: 'main' |
| slug | TEXT | |
| description | TEXT | |
| instruction | TEXT | |
| verification | TEXT | |
| context_type | TEXT | |
| context_ref | TEXT | |

### subtasks
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| task_id | INTEGER | FOREIGN KEY → tasks(id) ON DELETE CASCADE |
| title | TEXT | |
| phase | TEXT | |
| status | TEXT | pending / running / done |
| ordinal | INTEGER | ordering within task |
| checkpoint | TEXT | |
| evidence | TEXT | |
| created_at | TEXT | ISO timestamp |
| updated_at | TEXT | ISO timestamp |

---

## Watcher DB

### watches
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| tsid | TEXT | |
| repo | TEXT | |
| branch | TEXT | |
| pr_number | INTEGER | |
| commit_sha | TEXT | |
| push_type | TEXT | |
| message | TEXT | |
| pushed_at | TEXT | ISO timestamp |
| expires_at | TEXT | ISO timestamp |
| cycles | INTEGER | |
| max_cycles | INTEGER | default: 3 |
| last_ci_status | TEXT | |
| seen_reviews | TEXT | JSON array as text |
| status | TEXT | active / expired |
| created_at | TEXT | ISO timestamp |

### actions
| Column | Type | Notes |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| watch_id | INTEGER | FOREIGN KEY → watches(id) |
| tsid | TEXT | |
| action_type | TEXT | |
| body | TEXT | |
| delivered | INTEGER | 0 or 1 |
| created_at | TEXT | ISO timestamp |

---

## MongoDB — Yelp Business DB (`yelp_db.business`) — PROVISIONAL

Source: DataAgentBench Yelp dataset.

### business

| Field | Type | Notes |
|---|---|---|
| business_id | String | Primary identifier, prefixed format e.g. `businessid_9`. Strip `businessid_` prefix to get integer ID for cross-DB joins |
| name | String | Business name |
| address | String | Street address |
| city | String | |
| state | String | 2-letter state code |
| postal_code | String | |
| latitude | Double | |
| longitude | Double | |
| stars | Double | Average rating, 1.0–5.0 in 0.5 steps |
| review_count | Integer | Total number of reviews |
| is_open | Integer | 0 = closed, 1 = open |
| categories | String | Comma-separated category list |
| attributes | Object | Nested key-value pairs (for example WiFi, Parking) |
| hours | Object | Nested open and close times by day of week |

**No SQL joins apply.** Use `find()` or an aggregation pipeline.
Cross-database references via `business_id` are resolved in application code.
**Join Key Warning:** MongoDB `business_id` uses `businessid_` prefix (e.g. `businessid_9`).
DuckDB `business_ref` uses `businessref_` prefix (e.g. `businessref_9`).
Strip both prefixes to integer before joining.

---

## DuckDB — Yelp Review DB (`yelp_review.parquet` or equivalent) — PROVISIONAL

Source: DataAgentBench Yelp dataset.

### review

| Column | Type | Notes |
|---|---|---|
| review_id | VARCHAR | PRIMARY KEY, 22-char string |
| user_id | VARCHAR | References PostgreSQL users.user_id |
| business_ref | VARCHAR | Prefixed format e.g. `businessref_9`. Strip `businessref_` prefix to get integer ID. References MongoDB business.business_id |
| stars | INTEGER | Rating 1–5 |
| useful | INTEGER | Useful votes received |
| funny | INTEGER | Funny votes received |
| cool | INTEGER | Cool votes received |
| text | VARCHAR | Full review text |
| date | VARCHAR | ISO timestamp of review |

**No DuckDB-internal joins apply.** Cross-database references via `business_ref` and
`user_id` are resolved in application code. Strip `businessref_` prefix from `business_ref`
and `businessid_` prefix from MongoDB `business_id` to get matching integer IDs.

---

## PostgreSQL — Yelp User/Social DB — PROVISIONAL

Source: DataAgentBench Yelp dataset.

### users

| Column | Type | Notes |
|---|---|---|
| user_id | VARCHAR | PRIMARY KEY, 22-char string |
| name | VARCHAR | Display name |
| review_count | INTEGER | Number of reviews written |
| yelping_since | VARCHAR | ISO timestamp of account creation |
| friends | TEXT | Comma-separated list of friend user IDs |
| useful | INTEGER | Total useful votes given |
| funny | INTEGER | Total funny votes given |
| cool | INTEGER | Total cool votes given |
| fans | INTEGER | Number of fans |
| elite | VARCHAR | Comma-separated years of Elite status |
| average_stars | DOUBLE PRECISION | Average rating across all reviews |
| compliment_hot | INTEGER | |
| compliment_more | INTEGER | |
| compliment_profile | INTEGER | |
| compliment_cute | INTEGER | |
| compliment_list | INTEGER | |
| compliment_note | INTEGER | |
| compliment_plain | INTEGER | |
| compliment_funny | INTEGER | |
| compliment_writer | INTEGER | |
| compliment_photos | INTEGER | |

### tip

| Column | Type | Notes |
|---|---|---|
| user_id | VARCHAR | FOREIGN KEY → users(user_id) |
| business_id | VARCHAR | References MongoDB business.business_id — see Join Key Warning |
| text | TEXT | Tip text |
| date | VARCHAR | ISO timestamp |
| compliment_count | INTEGER | |

### checkin

| Column | Type | Notes |
|---|---|---|
| business_id | VARCHAR | References MongoDB `business.business_id` |
| date | TEXT | Comma-separated list of ISO datetime strings for each checkin event |

**Design note:** `checkin` has no `user_id`; checkins belong to the business only.

---

## Valid Joins — SQLite Databases

ONLY these joins are confirmed in the schema. Do not attempt any other join.

| Join | Key | Type |
|---|---|---|
| repos → organizations | repos.org = organizations.name | INNER/LEFT |
| job_logs → jobs | job_logs.job_id = jobs.id | INNER/LEFT |
| subtasks → tasks | subtasks.task_id = tasks.id | INNER/LEFT |
| actions → watches | actions.watch_id = watches.id | INNER/LEFT |

**Cross-database joins (Webapp DB ↔ Device DB) are NOT valid via SQL.**
The two databases are separate SQLite files. They cannot be joined in a single
query. Queries must be run separately and results merged in application code.

---

## Valid Joins — PostgreSQL (Yelp) — PROVISIONAL

| Join | Key | Type |
|---|---|---|
| tip → users | tip.user_id = users.user_id | INNER/LEFT |

All other cross-table references in the Yelp databases involve `business_id`. Those are
not valid SQL joins.

---

## JOIN KEY WARNING — business_id Format Mismatch

`business_id` appears in four places across three databases:

| Database | Table/Collection | Field | Format Note |
|---|---|---|---|
| MongoDB | business | business_id | 22-char alphanumeric string |
| DuckDB | review | business_id | **Confirmed inconsistent with MongoDB** |
| PostgreSQL | tip | business_id | Format unverified |
| PostgreSQL | checkin | business_id | Format unverified |

**Confirmed by the challenge brief:** `business_id` values are formatted inconsistently
between MongoDB and DuckDB. The agent must not assume a direct match.

**Not confirmed:** Whether the PostgreSQL `tip` and `checkin` columns share the same
format.

Resolution approach:
1. Query each database separately
2. Inspect actual `business_id` samples from each source
3. Apply only the transformations the data requires
4. Merge results in Python using the confirmed key

---

## BOUNDARY RULE

If a query requires a join not listed above, respond:
"I cannot confirm this join is valid — it is not in the schema document.
Please verify the relationship before I attempt this query."
