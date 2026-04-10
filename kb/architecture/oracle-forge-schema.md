# Oracle Forge: Database Schema & Valid Joins

Source: `tenai_repo/webapp/db.py`, `tenai_repo/scripts/conductor/watcher_db.py`

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

## Valid Joins

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

## BOUNDARY RULE

If a query requires a join not listed above, respond:
"I cannot confirm this join is valid — it is not in the schema document.
Please verify the relationship before I attempt this query."
