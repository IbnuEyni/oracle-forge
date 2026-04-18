# KB v2 - DAB Dataset Schema Descriptions & Key Characteristics

## 1. Overview of DAB datasets

- DataAgentBench includes 54 queries over 12 datasets in 9 domains.
- Key domains: retail, telecom, healthcare, finance, anti-money-laundering (AML), plus other enterprise sectors.
- Database systems used across DAB: PostgreSQL, MongoDB, SQLite, DuckDB.
- Most DAB queries use PostgreSQL first, then SQLite, MongoDB, and DuckDB.
- Important benchmark properties:
  - multi-database integration across different DB types in the same query
  - ill-formatted join keys and inconsistent IDs
  - unstructured text fields requiring extraction
  - domain-specific definitions for terms like churn, revenue, and active customer

## 2. Per-dataset key schema notes

### Yelp dataset (recommended starting point)

- Domain: retail / local business analytics.
- Uses MongoDB and DuckDB in the same dataset.
- Known characteristics:
  - PostgreSQL is not the only source; MongoDB stores business location data and DuckDB stores ratings.
  - Nested JSON values and missing fields are common.
  - The dataset is an early validation target because it contains multi-source joins, unstructured fields, and entity resolution challenges.
- Common challenge: join MongoDB business documents to DuckDB ratings records without a clean shared key.

### CRM Arena Pro dataset

- Domain: customer relationship management (CRM) / sales pipeline.
- Uses SQLite, DuckDB, and PostgreSQL in the same dataset.
- Known characteristics:
  - Six databases: core_crm (SQLite), sales_pipeline (DuckDB), support (PostgreSQL), products_orders (SQLite), activities (DuckDB), territory (SQLite).
  - 27 tables across all databases with complex cross-database joins on AccountId, ContactId, LeadId, etc.
  - Salesforce-style 18-character IDs with ~25% corruption (leading '#').
  - Unstructured text in descriptions, transcripts, and support notes requiring extraction.
  - Domain concepts: BANT factors for lead qualification, sales stages, knowledge articles for support.
- Common challenge: multi-database joins with ID corruption and unstructured text extraction for lead qualification or support resolution.
- Known query patterns:
  - Lead qualification: Check VoiceCallTranscript__c.Body__c for BANT factors (Budget, Authority, Need, Timeline).
  - Support resolution: Match Case.description to knowledge__kav.faq_answer__c for article recommendations.
  - Sales forecasting: Aggregate Opportunity.Amount by StageName and CloseDate.
  - Customer activity: Join Account to Event/Task via WhatId for engagement history.
  - Territory performance: Join UserTerritory2Association to Opportunity via OwnerId for regional metrics.

## 3. Common cross-database entity resolution challenges

- customer_id format mismatch: integer in one source, string in another, or string with prefix/suffix.
- product ID mismatch: different code formats across systems.
- table authority: some tables are authoritative and should be preferred over deprecated or copy tables when metadata indicates it.
- database type mismatch: SQL key fields versus MongoDB document keys require different normalization.
- schema discovery is essential: the agent must inspect schema and metadata before choosing join keys.

## 4. Unstructured field inventory

- support notes / ticket descriptions
- review text / customer feedback
- product descriptions and item metadata
- free-text comments and status reason fields
- CRM notes or service logs that contain entity references and severity indicators

### Why these matter

- Unstructured text fields often contain the facts needed to answer queries, such as ticket severity, churn signals, or product issue details.
- The agent must transform these fields into structured values before joining or aggregating.
- Failing to extract from unstructured fields leads to incorrect answers even when the join keys are correct.

## 5. Practical guidance for the agent

- Always map schema names to domain terms before generating joins.
- Prefer authoritative tables when available.
- Normalize join keys across DB types using explicit rules, not assumptions.
- Treat unstructured fields as sources of structured facts, not as raw text to aggregate.
