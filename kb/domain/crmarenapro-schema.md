# crmarenapro Dataset — Schema and Domain Knowledge

## Overview

Salesforce CRMArenaPro — 6 integrated databases covering CRM, sales, support, products, activities, and territory management. Highest-value dataset with **13 queries**.

**Database types:** PostgreSQL + SQLite + DuckDB (all 3 working databases in one dataset)

## The 6 Databases

### 1. Core CRM (SQLite) — `core_crm.db`

Foundation data — users, accounts, contacts from Salesforce.

| Table | Purpose |
|---|---|
| User | Sales team info (reps, managers) |
| Account | Company/customer data |
| Contact | Individual contacts within accounts |

### 2. Sales Pipeline (DuckDB) — `sales_pipeline.duckdb`

Deal management — opportunities through to contracts.

| Table | Purpose |
|---|---|
| Lead | Potential customers before qualification |
| Opportunity | Active deals in the pipeline |
| OpportunityLineItem | Line items on opportunities |
| Quote | Pricing quotes for opportunities |
| QuoteLineItem | Line items on quotes |
| Contract | Signed agreements |

### 3. Support (PostgreSQL) — `crm_support`

Customer support and knowledge base.

| Table | Purpose |
|---|---|
| Case | Support tickets |
| casehistory__c | Case status change history |
| knowledge__kav | Knowledge base articles |
| issue__c | Known issues tracked |
| emailmessage | Email communications |
| livechattranscript | Live chat records |

### 4. Products & Orders (SQLite) — `products_orders.db`

Product catalog and order management.

| Table | Purpose |
|---|---|
| ProductCategory | Category hierarchy |
| Product2 | Product catalog |
| ProductCategoryProduct | Many-to-many product/category mapping |
| Pricebook2 | Pricing books |
| PricebookEntry | Product prices within pricebooks |
| Order | Customer orders |
| OrderItem | Line items on orders |

### 5. Activities (DuckDB) — `activities.duckdb`

Tasks, events, and call logs.

| Table | Purpose |
|---|---|
| Event | Calendar events |
| Task | Activity tasks |
| VoiceCallTranscript__c | Voice call recordings/transcripts |

### 6. Territory (SQLite) — `territory.db`

Sales territory assignments.

| Table | Purpose |
|---|---|
| Territory2 | Territory definitions |
| UserTerritory2Association | Sales rep to territory mapping |

## Authoritative Sources by Query Type

| Query About | Go to |
|---|---|
| Active deals, pipeline value | DuckDB `sales_pipeline.Opportunity` |
| Customer company info | SQLite `core_crm.Account` |
| Sales rep info | SQLite `core_crm.User` |
| Support ticket details | PostgreSQL `crm_support.Case` |
| Product catalog | SQLite `products_orders.Product2` |
| Order history | SQLite `products_orders.Order` + `OrderItem` |
| Call logs, meetings | DuckDB `activities.Event` / `Task` / `VoiceCallTranscript__c` |
| Territory assignments | SQLite `territory.Territory2` + `UserTerritory2Association` |

## Cross-Database Join Strategy

**6 databases, 3 database types** — no single SQL JOIN works. Always query each side separately, merge in Python.

**Common join paths:**

| From | To | Join Key |
|---|---|---|
| Core CRM User | Sales Pipeline Opportunity | `OwnerId` on Opp = `Id` on User |
| Core CRM Account | Sales Pipeline Opportunity | `AccountId` on Opp = `Id` on Account |
| Core CRM Account | Support Case | `AccountId` on Case = `Id` on Account |
| Core CRM User | Territory Association | `UserId` in mapping table |
| Products & Orders Product2 | Pipeline OpportunityLineItem | `Product2Id` on LineItem = `Id` on Product |

## Salesforce Object Naming Convention

- **`__c` suffix** — custom objects (e.g., `issue__c`, `casehistory__c`, `VoiceCallTranscript__c`)
- **`__kav` suffix** — knowledge article version (`knowledge__kav`)
- **Standard objects** — no suffix (Account, Contact, User, Case, Order)

## Known Failure Patterns to Watch

1. **Wrong database for deal data** — opportunities live in **DuckDB**, not PostgreSQL. Agent often defaults to PostgreSQL.
2. **Wrong database for support** — cases live in **PostgreSQL** (`crm_support`), not SQLite.
3. **Activities confusion** — tasks, events, and call transcripts all in **DuckDB** `activities.duckdb`.
4. **Territory requires join** — rep-to-territory mapping needs BOTH `Territory2` AND `UserTerritory2Association` tables.
5. **Custom vs standard objects** — `issue__c` is different from a standard Issue. Always check the `__c` suffix.
6. **Product pricing requires 3 tables** — Product2 + PricebookEntry + Pricebook2 to get the full price for a product in a specific pricebook.

## Query Volume

**13 queries** in DAB benchmark for this dataset — highest volume of any dataset. High priority for correct context injection.
