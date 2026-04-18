# Schema: DEPS_DEV_V1

- **DAB folder:** `query_DEPS_DEV_V1`
- **Domain:** Software supply chain / open source package analytics
- **DB systems:** SQLite (package metadata) + DuckDB (GitHub project info)
- **Cross-DB join key:** Composite — `System` + `Name` + `Version` (all three columns must match)

---

## DB 1 — package_database (SQLite)

### packageinfo

| Column | Type | Notes |
|---|---|---|
| System | str | Package ecosystem — e.g. `NPM`, `Maven`, `PyPI` |
| Name | str | Package name |
| Version | str | Version string — may include pre-release suffixes |
| Licenses | str | JSON-like array of license identifiers — must parse |
| Links | str | JSON-like list of URLs (origin, docs, source) — must parse |
| Advisories | str | JSON-like list of security advisories — must parse |
| VersionInfo | str | JSON-like object with `IsRelease`, `Ordinal` — must parse |
| Hashes | str | JSON-like list of file hashes — must parse |
| DependenciesProcessed | bool | Whether dependency resolution succeeded |
| DependencyError | bool | Whether dependency processing failed |
| UpstreamPublishedAt | float | Unix timestamp in **milliseconds** — divide by 1000 for seconds |
| Registries | str | JSON-like list of registries — must parse |
| SLSAProvenance | float | SLSA level if available; NULL for most records |
| UpstreamIdentifiers | str | JSON-like list of upstream identifiers — must parse |
| Purl | float | Package URL — NULL for most records |

**Gotcha:** Nearly every complex field is stored as a JSON-like string. Use `json.loads()` before accessing nested values.
**Gotcha:** `UpstreamPublishedAt` is milliseconds, not seconds. Convert: `pd.to_datetime(val / 1000, unit='s')`.
**Gotcha:** `Purl` is typed as float — NULL records will appear as `NaN`, not as a string.

---

## DB 2 — project_database (DuckDB)

### project_packageversion

| Column | Type | Notes |
|---|---|---|
| System | str | Package ecosystem — matches packageinfo.System |
| Name | str | Package name — matches packageinfo.Name |
| Version | str | Package version — matches packageinfo.Version |
| ProjectType | str | e.g. `GITHUB` |
| ProjectName | str | Repository path in `owner/repo` format |
| RelationProvenance | str | Source of the relationship data |
| RelationType | str | Type of relationship (e.g. source repo) |

### project_info

| Column | Type | Notes |
|---|---|---|
| Project_Information | str | Text description — may contain name and owner |
| Licenses | str | JSON-like array of license identifiers — must parse |
| Description | str | Project description (may differ from Project_Information) |
| Homepage | str | Homepage URL if available |
| OSSFuzz | float | OSSFuzz status — NULL for most records |

**Gotcha:** `project_info` has no clean join key to `project_packageversion`. The relationship is implicit via `ProjectName` ↔ `Project_Information` text content. Do NOT assume a direct column join — use `project_packageversion.ProjectName` to filter or match `project_info` records.

---

## Cross-Database Join

| From | Composite Key | To |
|---|---|---|
| package_database.packageinfo | System + Name + Version | project_database.project_packageversion |

**Merge in Python.** Query each database separately, then:

```python
import pandas as pd
df = pd.merge(
    packageinfo_df,
    project_pv_df,
    on=["System", "Name", "Version"],
    how="inner"
)
```

**Version string warning:** Version strings may not match exactly due to formatting differences (e.g. `1.0.0` vs `1.0`). Normalize before joining if counts seem low.

---

## Valid Intra-Database Joins

| Join | Key | Type |
|---|---|---|
| project_packageversion → project_info | ProjectName ~ Project_Information (fuzzy/text match) | No confirmed SQL join key |

There is no confirmed clean foreign key between `project_packageversion` and `project_info`. Do not attempt a SQL `JOIN` on these tables without first inspecting actual values.

---

## Known Failure Patterns

- Accessing `Licenses`, `Links`, `Advisories`, `VersionInfo` as plain strings → KeyError or wrong output.
- Using `UpstreamPublishedAt` directly as a timestamp without dividing by 1000 → dates in year ~52000.
- Joining on `Name` alone without `System` → cross-ecosystem collisions (same package name in NPM and Maven).
- Assuming `project_info` joins cleanly to `project_packageversion` via SQL → no confirmed key.
