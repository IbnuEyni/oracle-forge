# Schema: GITHUB_REPOS

- **DAB folder:** `query_GITHUB_REPOS`
- **Domain:** Software / open source repository analytics
- **DB systems:** SQLite (repo metadata) + DuckDB (file contents, commits, file tree)
- **Cross-DB join key:** `repo_name` (format: `owner/repo` string — consistent across both DBs)

---

## DB 1 — metadata_database (SQLite)

### languages

| Column | Type | Notes |
|---|---|---|
| repo_name | str | `owner/repo` format — join key |
| language_description | str | Natural language description of languages used — NOT a structured list |

**Gotcha:** `language_description` is prose, not a parsed language list. To filter by language, use `LIKE` or text search, not equality.

### licenses

| Column | Type | Notes |
|---|---|---|
| repo_name | str | `owner/repo` format — join key |
| license | str | License identifier (e.g. `apache-2.0`, `mit`) |

### repos

| Column | Type | Notes |
|---|---|---|
| repo_name | str | `owner/repo` format — PRIMARY KEY |
| watch_count | int | Number of GitHub watchers |

---

## DB 2 — artifacts_database (DuckDB)

### contents

| Column | Type | Notes |
|---|---|---|
| id | str | File blob identifier — joins to files.id |
| content | str | File text content — may be truncated or placeholder for large/binary files |
| sample_repo_name | str | `owner/repo` format — cross-DB join key |
| sample_ref | str | Branch name or commit SHA |
| sample_path | str | File path within the repo |
| sample_symlink_target | str | Symlink target path if applicable |
| repo_data_description | str | Natural language file metadata summary |

**Gotcha:** `content` may contain placeholder text for binary or oversized files. Check `repo_data_description` for hints.

### commits

| Column | Type | Notes |
|---|---|---|
| commit | str | Commit SHA — unique identifier |
| tree | str | Tree object SHA |
| parent | str | Parent commit SHA(s) — JSON-like for merge commits |
| author | str | JSON-like object: `{name, email, timestamp}` — must parse |
| committer | str | JSON-like object: `{name, email, timestamp}` — must parse |
| subject | str | Short commit message subject line |
| message | str | Full commit message |
| trailer | str | JSON-like commit trailer metadata |
| difference | str | JSON-like file changes introduced — may be truncated |
| difference_truncated | bool | True if difference data was cut off |
| repo_name | str | `owner/repo` format — cross-DB join key |
| encoding | str | Encoding format if applicable |

**Gotcha:** `author` and `committer` timestamps are inside a JSON-like string. Parse with `json.loads()` before date filtering.
**Gotcha:** `difference` may be truncated — check `difference_truncated` before relying on it for completeness.

### files

| Column | Type | Notes |
|---|---|---|
| repo_name | str | `owner/repo` format — cross-DB join key |
| ref | str | Branch or commit SHA |
| path | str | File path within the repo |
| mode | int | File mode (regular, executable, symlink) |
| id | str | Blob identifier — joins to contents.id |
| symlink_target | str | Symlink target path if applicable |

---

## Cross-Database Join

| From | Key | To |
|---|---|---|
| metadata_database.repos.repo_name | `owner/repo` string (exact match) | artifacts_database.commits.repo_name |
| metadata_database.repos.repo_name | `owner/repo` string (exact match) | artifacts_database.files.repo_name |
| metadata_database.repos.repo_name | `owner/repo` string (exact match) | artifacts_database.contents.sample_repo_name |

**Merge in Python.** Query each database separately, then join on `repo_name`.

```python
import pandas as pd
df = pd.merge(repos_df, commits_df, on="repo_name", how="inner")
```

---

## Valid Intra-Database Joins

**SQLite — metadata_database:**

| Join | Key | Type |
|---|---|---|
| languages → repos | repo_name | INNER/LEFT |
| licenses → repos | repo_name | INNER/LEFT |
| languages → licenses | repo_name | INNER/LEFT |

**DuckDB — artifacts_database:**

| Join | Key | Type |
|---|---|---|
| contents → files | contents.id = files.id | INNER/LEFT |
| commits → files | commits.repo_name = files.repo_name | INNER/LEFT |

---

## Known Failure Patterns

- Filtering `language_description` with `= 'Python'` instead of `LIKE '%Python%'` → zero results.
- Accessing `author` or `committer` fields as plain strings without parsing the JSON → wrong name/timestamp.
- Using `difference` for file change counts without checking `difference_truncated` → undercounting.
- Joining `contents` to metadata via `repo_name` instead of `sample_repo_name` → column not found.
