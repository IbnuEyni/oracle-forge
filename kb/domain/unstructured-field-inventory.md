# Unstructured Field Inventory

## Purpose

This document lists database fields that contain free-text or semi-structured data. When a query asks about information that has no dedicated structured column, the agent MUST check these fields before reporting "data not available."

**RULE:** If a query asks for a category, reason, or classification that does not exist as a column, search the unstructured fields listed below using pattern matching (LIKE, regex, or text functions).

## Inventory of Unstructured Fields

### PostgreSQL

| Table | Field | Content Type | Example Value |
|---|---|---|---|
| `customers` | `notes` | Support interaction notes | `"Called 2024-03-15, wants to cancel -- pricing too high"` |
| `customers` | `feedback` | Free-text survey responses | `"Love the product but UI is confusing"` |
| `tickets` | `description` | Support ticket body | `"User reports login fails after password reset"` |
| `tickets` | `resolution_notes` | Agent resolution summary | `"Reset auth token, confirmed login works"` |
| `orders` | `special_instructions` | Customer order notes | `"Ship to alternate address: 123 Main St"` |
| `products` | `description` | Product description text | `"Premium analytics dashboard with real-time alerts"` |

### CRM Arena Pro (PostgreSQL, SQLite, DuckDB)

| Database | Table | Field | Content Type | Example Value |
|---|---|---|---|---|
| PostgreSQL (support) | `Case` | `subject` | Case subject line | `"Login issues after password reset"` |
| PostgreSQL (support) | `Case` | `description` | Case description | `"User cannot access account since changing password"` |
| PostgreSQL (support) | `knowledge__kav` | `faq_answer__c` | FAQ answer text | `"To reset password, click 'Forgot Password' on login page"` |
| PostgreSQL (support) | `knowledge__kav` | `summary` | Article summary | `"Password reset process for account recovery"` |
| PostgreSQL (support) | `emailmessage` | `textbody` | Email content | `"Dear support, I need help with my order #12345"` |
| PostgreSQL (support) | `livechattranscript` | `body` | Chat transcript | `"Agent: Hello, how can I help? User: My order is delayed"` |
| SQLite (core_crm) | `Account` | `Description` | Account description | `"Tech startup in San Francisco, 50 employees"` |
| DuckDB (sales_pipeline) | `Opportunity` | `Description` | Opportunity description | `"Enterprise deal for 1000 licenses, closing Q4"` |
| DuckDB (sales_pipeline) | `Quote` | `Description` | Quote description | `"Discounted pricing for annual commitment"` |
| DuckDB (sales_pipeline) | `Contract` | `Description` | Contract description | `"3-year agreement with SLA guarantees"` |
| SQLite (products_orders) | `Product2` | `Description` | Product description | `"Cloud analytics platform with ML insights"` |
| SQLite (products_orders) | `Pricebook2` | `Description` | Pricebook description | `"Standard pricing for US market"` |
| DuckDB (activities) | `Event` | `Subject` | Event subject | `"Demo call with Acme Corp"` |
| DuckDB (activities) | `Event` | `Description` | Event description | `"Product demo and Q&A session"` |
| DuckDB (activities) | `Task` | `Subject` | Task subject | `"Follow up on quote #Q-456"` |
| DuckDB (activities) | `Task` | `Description` | Task description | `"Send updated pricing and contract terms"` |
| DuckDB (activities) | `VoiceCallTranscript__c` | `Body__c` | Call transcript | `"Discussed budget constraints and timeline requirements"` |
| SQLite (territory) | `Territory2` | `Description` | Territory description | `"West Coast enterprise accounts"` |

### MongoDB

| Collection | Field | Content Type | Example Value |
|---|---|---|---|
| `interactions` | `transcript` | Chat/call transcript | `"Agent: How can I help? User: I want to downgrade my plan"` |
| `interactions` | `summary` | Auto-generated summary | `"Customer requested plan downgrade from Pro to Basic"` |
| `reviews` | `body` | User review text | `"Great tool but too expensive for small teams"` |
| `logs` | `message` | System log message | `"ERROR: Payment failed for user 1042, card declined"` |

### SQLite

| Table | Field | Content Type | Example Value |
|---|---|---|---|
| `events` | `metadata` | JSON-as-string blob | `'{"source": "email", "campaign": "spring_2024"}'` |
| `users` | `bio` | User profile text | `"Data analyst at Acme Corp, 5 years experience"` |
| `comments` | `content` | User comment text | `"This feature doesn't work on mobile"` |

### DuckDB

| Table | Field | Content Type | Example Value |
|---|---|---|---|
| `analytics` | `raw_event` | JSON event payload | `'{"action": "click", "element": "pricing_page"}'` |
| `reports` | `narrative` | Auto-generated report text | `"Revenue increased 12% MoM driven by enterprise segment"` |

## Extraction Patterns

### Common Query Types and Where to Look

| Query Asks About | Check These Fields | Extraction Method |
|---|---|---|
| Cancellation reasons | `customers.notes`, `interactions.transcript` | `LIKE '%cancel%'` then classify |
| Pricing complaints | `customers.feedback`, `reviews.body` | `LIKE '%pric%'` or `LIKE '%expensive%'` |
| Feature requests | `tickets.description`, `reviews.body` | `LIKE '%feature%'` or `LIKE '%wish%'` or `LIKE '%would be nice%'` |
| Error types | `logs.message` | `LIKE 'ERROR:%'` then extract after colon |
| Campaign source | `events.metadata` | Parse JSON string, extract `source` field |
| User segments | `users.bio`, `analytics.raw_event` | Pattern match on job titles or actions |

### SQL Pattern Examples

```sql
-- Count pricing-related cancellations from customer notes
SELECT COUNT(*) FROM customers
WHERE notes ILIKE '%cancel%'
AND (notes ILIKE '%pric%' OR notes ILIKE '%expensive%' OR notes ILIKE '%cost%');

-- Extract error categories from log messages
SELECT
  CASE
    WHEN message LIKE '%payment%' THEN 'payment_error'
    WHEN message LIKE '%auth%' OR message LIKE '%login%' THEN 'auth_error'
    WHEN message LIKE '%timeout%' THEN 'timeout_error'
    ELSE 'other'
  END AS error_category,
  COUNT(*) AS count
FROM logs
WHERE message LIKE 'ERROR:%'
GROUP BY error_category;

-- Parse JSON-as-string in SQLite
SELECT json_extract(metadata, '$.source') AS source, COUNT(*)
FROM events
GROUP BY source;
```

## Important Notes

1. **Case sensitivity:** Use `ILIKE` (PostgreSQL) or `LOWER()` wrapper for case-insensitive matching. SQLite `LIKE` is case-insensitive by default for ASCII.
2. **Multiple keywords:** Cancellation reasons often use synonyms -- check for "cancel", "churn", "leave", "quit", "stop", "end subscription".
3. **JSON-as-string:** Some fields store JSON as plain text strings. Use `json_extract()` (SQLite), `jsonb` operators (PostgreSQL), or parse in Python.
4. **Accuracy tradeoff:** Text extraction is approximate. Always state confidence level: "Based on keyword matching in the notes field, approximately X cancellations were pricing-related."
5. **When in doubt:** If text parsing yields ambiguous results, report the count with a caveat rather than reporting "data not available."
