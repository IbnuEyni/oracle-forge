# deps_dev Dataset Schema Description

## Overview
- **Domain**: Software package and dependency analytics (package metadata and GitHub project relationships)
- **Databases used**: SQLite (`package_database`) + DuckDB (`project_database`)
- **Key characteristic**: Requires matching package information with GitHub projects, using shared attributes for linking.

## Main Tables & Purpose

**1. packageinfo (SQLite - package_database)**
- Contains metadata about software packages across different ecosystems.
- Key fields:
  - `System` (str): Package ecosystem (e.g., NPM, Maven)
  - `Name` (str): Package name
  - `Version` (str): Version string
  - `Licenses`, `Links`, `Advisories`, `DependenciesProcessed`, `UpstreamPublishedAt`, `Registries`, `Purl`

**2. project_packageversion (DuckDB - project_database)**
- Maps packages to GitHub projects.
- Key fields:
  - `System`, `Name`, `Version`
  - `ProjectType`, `ProjectName` (in `owner/repo` format)
  - `RelationProvenance`, `RelationType`

**3. project_info (DuckDB - project_database)**
- Contains detailed information about GitHub projects.
- Key fields:
  - `Project_Information` (str): Textual description including stars and forks
  - `Licenses`, `Description`, `Homepage`

## Key Join Keys & Gotchas
- Main matching keys: `System`, `Name`, and `Version` (used to link `packageinfo` → `project_packageversion`)
- After matching, use `ProjectName` from `project_packageversion` to link to `project_info`
- Challenge: Exact matching on `System` + `Name` + `Version` is critical. Small differences in version strings can break joins.
- `Project_Information` field contains valuable metrics (stars, forks) but is stored as natural language text.

## Unstructured / Semi-structured Fields
- `Project_Information`: Contains mixed structured metrics and descriptive text.
- `Licenses`, `Links`, `Advisories`: Often stored as JSON-like strings.

## Known Failure Patterns
- Agent fails to join across the three tables correctly (packageinfo → project_packageversion → project_info)
- Agent attempts to join only on `Name` without using `System` and `Version`
- Agent treats `Project_Information` as simple text instead of extracting metrics
- Agent ignores version string sensitivity during matching

## Practical Guidance for the Agent
- Always join using the combination of `System`, `Name`, and `Version` to match packages between databases.
- After getting `ProjectName` from `project_packageversion`, use it to retrieve project details from `project_info`.
- When metrics like stars or forks are needed, extract them from the `Project_Information` field in `project_info`.
- Be careful with version string formatting — treat version matching as exact.
- For any query involving GitHub projects and packages, always traverse through all three tables in order.

This dataset is excellent for testing multi-table joins across different database types and handling composite keys.


