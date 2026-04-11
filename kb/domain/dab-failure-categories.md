# DAB Failure Categories

## What is DAB?

DataAgentBench (DAB) is a benchmark created by UC Berkeley to evaluate data analytics agents. It contains 54 queries across 12 real-world datasets stored in 4 database types (PostgreSQL, MongoDB, SQLite, DuckDB). As of the March 2026 paper, the best reported score is 38% pass@1 -- meaning the best agent fails on 62% of queries on the first attempt.

DAB failures cluster into 4 distinct categories. Each category represents a specific capability gap that our agent must address.

## The 4 Failure Categories

### 1. Multi-Database Integration

**What it is:** A single query requires data from multiple database types. For example, answering "What is the average revenue per churned user?" might need user data from PostgreSQL and revenue records from MongoDB.

**Why agents fail:** Most agents assume all data lives in one database. They issue a SQL query to PostgreSQL and never check MongoDB. They cannot JOIN across database engines because there is no native cross-database JOIN -- each database has its own query language and connection.

**What our agent must do:**
- Detect when a query requires data from more than one database
- Query each database separately using the correct language (SQL for PostgreSQL/SQLite/DuckDB, MQL for MongoDB)
- Combine results in application logic (Python), not in a single query
- Use MCP Toolbox to route each sub-query to the correct database

### 2. Ill-Formatted Join Keys

**What it is:** The same entity (user, device, transaction) has different ID formats across databases. For example:
- PostgreSQL stores `user_id = "USR-1042"`
- MongoDB stores `userId = 1042`
- SQLite stores `user_id = "1042"`

These all refer to the same user, but a naive JOIN on `user_id = userId` returns zero rows.

**Why agents fail:** Agents assume IDs match exactly across databases. They write `WHERE user_id = userId` and get empty results. They do not know that ID formats differ because this information is not in the schema -- it is in the data itself.

**What our agent must do:**
- Before joining, sample actual ID values from both databases
- Apply normalization: strip prefixes (`USR-`), cast types (string to int), standardize case
- Build a mapping table when formats are complex
- The Join Key Glossary (KB v2) documents known mismatches so the agent does not have to discover them each time

### 3. Unstructured Text Transformation

**What it is:** Some database fields contain free-text data that must be parsed to answer the query. For example:
- A `notes` field contains `"Customer called 2024-03-15, requested cancellation due to pricing"`
- The query asks: "How many cancellations were pricing-related?"

The answer exists in the data, but it is buried in natural language text, not in a structured column.

**Why agents fail:** Agents look for structured columns like `cancellation_reason = 'pricing'`. When no such column exists, they return "data not available" instead of parsing the text field. They do not attempt text extraction or pattern matching on unstructured fields.

**What our agent must do:**
- Identify which fields contain unstructured text (the Unstructured Field Inventory in KB v2 lists these)
- Use pattern matching (LIKE, regex) or text functions to extract structured answers from free text
- When the query implies a category that does not exist as a column, check text fields before reporting "not available"

### 4. Domain Knowledge Gaps

**What it is:** The query uses business terms that require specific definitions to answer correctly. For example:
- "What is the churn rate?" -- requires knowing the company's definition of churn (30 days inactive? 90 days? subscription cancelled?)
- "What was Q3 revenue?" -- requires knowing the fiscal year start month
- "Who are power users?" -- requires knowing the threshold (daily active? >10 sessions/week?)

**Why agents fail:** Without domain definitions, agents guess. They might define churn as "no login in 30 days" when the company defines it as "subscription cancelled." The query executes successfully but returns the wrong number. This is the hardest failure to catch because the answer looks plausible.

**What our agent must do:**
- Check the domain term definitions document (maintained separately in KB v2 by the team) before writing any query that uses business terminology
- If a term is not defined in any KB document, flag it: "Term 'power user' is not defined in the knowledge base. Using threshold of >10 sessions/week. Please confirm."
- Never silently assume a business definition -- either cite the KB source or ask for clarification

## Why This Matters for Our Agent

According to the DAB paper (March 2026), these 4 categories account for the primary failure modes. Our KB architecture directly targets each one:

| Failure Category | KB Mitigation |
|---|---|
| Multi-database integration | Schema knowledge (KB v1) maps which data lives where |
| Ill-formatted join keys | Join Key Glossary (KB v2) documents format mismatches |
| Unstructured text transformation | Unstructured Field Inventory (KB v2) lists parseable fields |
| Domain knowledge gaps | Domain term definitions (KB v2, maintained by team) provide exact definitions |

The agent that solves all 4 categories does not need to be smarter -- it needs better context injection. That is what our KB provides.
