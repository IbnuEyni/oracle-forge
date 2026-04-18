# Join Key Glossary

## Purpose

This document lists known ID format mismatches across databases in the DAB benchmark. When the agent needs to JOIN data across databases, it MUST consult this glossary to apply the correct normalization before joining.

**RULE:** Never assume IDs match across databases. Always check this glossary first. If a join key is not listed here, sample 5 rows from each side and compare formats before joining.

## Known Format Mismatches

### User IDs

| Database | Field Name | Format | Example |
|---|---|---|---|
| PostgreSQL | `user_id` | Prefixed string | `USR-1042` |
| MongoDB | `userId` | Integer | `1042` |
| SQLite | `user_id` | String (no prefix) | `"1042"` |
| DuckDB | `user_id` | Integer | `1042` |

**Normalization:** Strip `USR-` prefix, cast to integer for comparison.

```sql
-- PostgreSQL side
CAST(REPLACE(user_id, 'USR-', '') AS INTEGER)
-- SQLite side
CAST(user_id AS INTEGER)
```

### CRM Entity IDs (Salesforce-style)

| Database | Field Name | Format | Example |
|---|---|---|---|
| SQLite (core_crm) | `Id` | 18-char string, may have leading '#' | `001Wt00000PFj4zIAD` or `#001Wt00000PFj4zIAD` |
| DuckDB (sales_pipeline) | `AccountId`, `ContactId`, etc. | 18-char string, clean | `001Wt00000PFj4zIAD` |
| PostgreSQL (support) | `accountid`, `contactid` | 18-char string, may have leading '#' | `001Wt00000PFj4zIAD` or `#001Wt00000PFj4zIAD` |
| SQLite (products_orders) | `AccountId` | 18-char string, clean | `001Wt00000PFj4zIAD` |
| DuckDB (activities) | `WhatId`, `OwnerId` | 18-char string, clean | `001Wt00000PFj4zIAD` |
| SQLite (territory) | `UserId` | 18-char string, clean | `001Wt00000PFj4zIAD` |

**Normalization:** Strip leading '#' if present, case-sensitive comparison.

```sql
-- All sides
TRIM(LEADING '#' FROM id_field)
```

### Device IDs

| Database | Field Name | Format | Example |
|---|---|---|---|
| PostgreSQL | `device_id` | UUID | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| MongoDB | `deviceId` | String (short) | `DEV-a1b2c3d4` |

**Normalization:** This is a dataset-specific mapping verified against the DAB data. The MongoDB short ID (`DEV-` + first 8 hex chars) corresponds to the UUID prefix in PostgreSQL. To join: strip `DEV-` from MongoDB, then match against the first 8 characters of the PostgreSQL UUID (`SUBSTRING(device_id, 1, 8)`). Verify with a sample before bulk joins -- prefix collisions are possible in large datasets.

### Transaction IDs

| Database | Field Name | Format | Example |
|---|---|---|---|
| PostgreSQL | `transaction_id` | Sequential integer | `50231` |
| MongoDB | `txnId` | Prefixed string | `TXN-50231` |

**Normalization:** Strip `TXN-` prefix from MongoDB, cast to integer.

### Timestamp Formats

| Database | Field Name | Format | Example |
|---|---|---|---|
| PostgreSQL | `created_at` | ISO 8601 with timezone | `2024-03-15T14:30:00+00:00` |
| MongoDB | `createdAt` | ISODate object | `ISODate("2024-03-15T14:30:00Z")` |
| SQLite | `created_at` | String (no timezone) | `2024-03-15 14:30:00` |
| DuckDB | `created_at` | TIMESTAMP | `2024-03-15 14:30:00` |

**Normalization:** Convert all to UTC, strip timezone info for comparison. Use `strftime` in SQLite, `AT TIME ZONE 'UTC'` in PostgreSQL.

## Common Pitfalls

1. **Field name casing:** PostgreSQL uses `snake_case`, MongoDB uses `camelCase`. The same field is `user_id` in one and `userId` in another.
2. **NULL vs missing:** PostgreSQL has `NULL`, MongoDB may omit the field entirely. Check for both.
3. **String vs integer:** `"1042"` (string) != `1042` (integer). Always cast to the same type before comparing.
4. **Prefix stripping order:** Strip prefix FIRST, then cast type. `CAST('USR-1042' AS INTEGER)` will error -- strip prefix first.

## How to Handle Unknown Join Keys

If you encounter a join key not listed in this glossary:

1. Query 5 sample values from each database
2. Compare formats visually
3. Write normalization logic
4. Log the mismatch in the corrections log (KB v3, created after first agent failures)
5. Never guess -- always verify with actual data
