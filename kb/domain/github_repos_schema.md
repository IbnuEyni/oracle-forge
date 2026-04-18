
# github_repos Dataset Schema Description

## Overview
- **Domain**: GitHub repository analytics (repository metadata, licenses, languages, file contents, and commit history)
- **Databases used**: SQLite (metadata_database) + DuckDB ( rtifacts_database)
- **Key characteristic**: Requires joining repository-level metadata with artifact-level data (files, contents, commits) using 
epo_name as the canonical identifier.

## Main Tables & Purpose

**1. repos (SQLite - metadata_database)**
- Core repository information and popularity metrics.
- Key fields: 
epo_name, watch_count

**2. languages (SQLite - metadata_database)**
- Programming languages used in the repository.
- Key fields: 
epo_name, language_description (may contain multiple languages)

**3. licenses (SQLite - metadata_database)**
- License information for the repository.
- Key fields: 
epo_name, license

**4. files (DuckDB - artifacts_database)**
- File metadata at specific references (branches/commits).
- Key fields: 
epo_name, 
ef, path, mode, id, symlink_target

**5. contents (DuckDB - artifacts_database)**
- Actual file content and derived metadata.
- Key fields: id, content, sample_repo_name, sample_path, 
epo_data_description

**6. commits (DuckDB - artifacts_database)**
- Commit history and metadata.
- Key fields: commit, 
epo_name,  uthor, committer, subject, message, difference

## Key Join Keys & Gotchas
- **Primary join key**: 
epo_name (used across 
epos, languages, licenses, iles, and commits)
- **Important nuance**: The contents table uses sample_repo_name instead of 
epo_name. Must map sample_repo_name → 
epo_name carefully.
- id field links contents to iles (file/blob level), but should not be used as a repository identifier.
- language_description may list multiple languages in natural language form.

## Unstructured / Semi-structured Fields
- language_description: May contain multiple languages described in text.
- 
epo_data_description: Natural language summary of file attributes.
-  uthor, committer, message, difference, 	railer: JSON-like or free-text fields.

## Known Failure Patterns
- Agent joins contents.sample_repo_name directly without mapping to canonical 
epo_name
- Agent joins only on id expecting repository-level results
- Agent treats language_description as a single language instead of multi-valued
- Agent performs exact string matching on JSON-like fields ( uthor, difference, etc.)

## Practical Guidance for the Agent
- Use 
epo_name as the canonical key when joining metadata tables (
epos, languages, licenses) with artifact tables (iles, commits).
- When using the contents table, map sample_repo_name to 
epo_name from the metadata tables.
- To determine the primary language, analyze the language_description field (compare byte counts or prominence if multiple languages are listed).
- Parse JSON-like fields ( uthor, committer, difference) carefully when needed.
- For file-content queries, join iles.id with contents.id and filter on iles.path and contents.content.

This dataset is excellent for testing cross-database joins, handling semi-structured data, and correct use of repository identity keys.


