# Schema: CRMARENA_PRO

- **DAB folder:** `query_CRMARENA_PRO`
- **Domain:** Customer Relationship Management (CRM) / Sales Pipeline
- **DB systems:** SQLite (core_crm, products_orders, territory), DuckDB (sales_pipeline, activities), PostgreSQL (support)
- **Cross-DB join key:** Various ID fields (AccountId, ContactId, LeadId, etc.) — Salesforce-style 18-character IDs with possible corruption

---

## DB 1 — core_crm (SQLite)

### User

| Column | Type | Notes |
|---|---|---|
| Id | str | User ID — join key |
| FirstName | str | User's first name |
| LastName | str | User's last name |
| Email | str | User's email |
| Phone | str | User's phone |
| Username | str | User's username |
| Alias | str | User's alias |
| LanguageLocaleKey | str | Language locale |
| EmailEncodingKey | str | Email encoding |
| TimeZoneSidKey | str | Time zone |
| LocaleSidKey | str | Locale |

### Account

| Column | Type | Notes |
|---|---|---|
| Id | str | Account ID — cross-DB join key |
| Name | str | Account name |
| Phone | str | Account phone |
| Industry | str | Industry sector |
| Description | str | Account description (unstructured text) |
| NumberOfEmployees | int | Number of employees |
| ShippingState | str | Shipping state (may be abbreviated) |

### Contact

| Column | Type | Notes |
|---|---|---|
| Id | str | Contact ID — cross-DB join key |
| FirstName | str | Contact's first name |
| LastName | str | Contact's last name |
| Email | str | Contact's email |
| AccountId | str | Associated account ID |

---

## DB 2 — sales_pipeline (DuckDB)

### Contract

| Column | Type | Notes |
|---|---|---|
| Id | str | Contract ID |
| AccountId | str | Account ID — join key |
| Status | str | Contract status |
| StartDate | date | Contract start date |
| CustomerSignedDate | date | Customer signature date |
| CompanySignedDate | date | Company signature date |
| Description | str | Contract description (unstructured text) |
| ContractTerm | int | Contract term in months |

### Lead

| Column | Type | Notes |
|---|---|---|
| Id | str | Lead ID — cross-DB join key |
| FirstName | str | Lead's first name |
| LastName | str | Lead's last name |
| Email | str | Lead's email |
| Phone | str | Lead's phone |
| Company | str | Company name |
| Status | str | Lead status |
| ConvertedContactId | str | Converted contact ID |
| ConvertedAccountId | str | Converted account ID |
| Title | str | Lead's title |
| CreatedDate | date | Creation date |
| ConvertedDate | date | Conversion date |
| IsConverted | bool | Conversion flag |
| OwnerId | str | Owner user ID |

### Opportunity

| Column | Type | Notes |
|---|---|---|
| Id | str | Opportunity ID |
| ContractID__c | str | Contract ID |
| AccountId | str | Account ID — join key |
| ContactId | str | Contact ID — join key |
| OwnerId | str | Owner user ID |
| Probability | float | Win probability (0-100) |
| Amount | float | Deal amount |
| StageName | str | Sales stage (e.g., 'Qualification', 'Discovery', 'Quote', 'Negotiation', 'Closed') |
| Name | str | Opportunity name |
| Description | str | Opportunity description (unstructured text) |
| CreatedDate | date | Creation date |
| CloseDate | date | Expected close date |

### OpportunityLineItem

| Column | Type | Notes |
|---|---|---|
| Id | str | Line item ID |
| OpportunityId | str | Opportunity ID |
| Product2Id | str | Product ID |
| PricebookEntryId | str | Pricebook entry ID |
| Quantity | float | Quantity |
| TotalPrice | float | Total price |

### Quote

| Column | Type | Notes |
|---|---|---|
| Id | str | Quote ID |
| OpportunityId | str | Opportunity ID |
| AccountId | str | Account ID — join key |
| ContactId | str | Contact ID — join key |
| Name | str | Quote name |
| Description | str | Quote description (unstructured text) |
| Status | str | Quote status |
| CreatedDate | date | Creation date |
| ExpirationDate | date | Expiration date |

### QuoteLineItem

| Column | Type | Notes |
|---|---|---|
| Id | str | Quote line item ID |
| QuoteId | str | Quote ID |
| OpportunityLineItemId | str | Opportunity line item ID |
| Product2Id | str | Product ID |
| PricebookEntryId | str | Pricebook entry ID |
| Quantity | float | Quantity |
| UnitPrice | float | Unit price |
| Discount | float | Discount amount |
| TotalPrice | float | Total price |

---

## DB 3 — support (PostgreSQL)

### Case

| Column | Type | Notes |
|---|---|---|
| id | str | Case ID |
| priority | str | Case priority |
| subject | str | Case subject (unstructured text) |
| description | str | Case description (unstructured text) |
| status | str | Case status |
| contactid | str | Contact ID — join key |
| createddate | date | Creation date |
| closeddate | date | Closure date |
| orderitemid__c | str | Order item ID |
| issueid__c | str | Issue ID |
| accountid | str | Account ID — join key |
| ownerid | str | Owner user ID |

### knowledge__kav

| Column | Type | Notes |
|---|---|---|
| id | str | Knowledge article ID |
| title | str | Article title |
| faq_answer__c | str | FAQ answer (unstructured text) |
| summary | str | Article summary (unstructured text) |
| urlname | str | URL name |

### issue__c

| Column | Type | Notes |
|---|---|---|
| id | str | Issue ID |
| name | str | Issue name |
| description__c | str | Issue description (unstructured text) |

### casehistory__c

| Column | Type | Notes |
|---|---|---|
| id | str | Case history ID |
| caseid__c | str | Case ID |
| oldvalue__c | str | Old value |
| newvalue__c | str | New value |
| createddate | date | Creation date |
| field__c | str | Changed field |

### emailmessage

| Column | Type | Notes |
|---|---|---|
| id | str | Email ID |
| subject | str | Email subject (unstructured text) |
| textbody | str | Email body (unstructured text) |
| parentid | str | Parent case ID |
| fromaddress | str | From email address |
| toids | str | To email addresses |
| messagedate | date | Message date |
| relatedtoid | str | Related to ID |

### livechattranscript

| Column | Type | Notes |
|---|---|---|
| id | str | Chat transcript ID |
| caseid | str | Case ID |
| accountid | str | Account ID — join key |
| ownerid | str | Owner user ID |
| body | str | Chat body (unstructured text) |
| endtime | datetime | Chat end time |
| livechatvisitorid | str | Visitor ID |
| contactid | str | Contact ID — join key |

---

## DB 4 — products_orders (SQLite)

### ProductCategory

| Column | Type | Notes |
|---|---|---|
| Id | str | Category ID |
| Name | str | Category name |
| CatalogId | str | Catalog ID |

### Product2

| Column | Type | Notes |
|---|---|---|
| Id | str | Product ID — cross-DB join key |
| Name | str | Product name |
| Description | str | Product description (unstructured text) |
| IsActive | bool | Active flag |
| External_ID__c | str | External ID |

### ProductCategoryProduct

| Column | Type | Notes |
|---|---|---|
| Id | str | Mapping ID |
| ProductCategoryId | str | Category ID |
| ProductId | str | Product ID |

### Pricebook2

| Column | Type | Notes |
|---|---|---|
| Id | str | Pricebook ID |
| Name | str | Pricebook name |
| Description | str | Pricebook description (unstructured text) |
| IsActive | bool | Active flag |
| ValidFrom | date | Valid from date |
| ValidTo | date | Valid to date |

### PricebookEntry

| Column | Type | Notes |
|---|---|---|
| Id | str | Pricebook entry ID |
| Pricebook2Id | str | Pricebook ID |
| Product2Id | str | Product ID |
| UnitPrice | float | Unit price |

### Order

| Column | Type | Notes |
|---|---|---|
| Id | str | Order ID |
| AccountId | str | Account ID — join key |
| Status | str | Order status |
| EffectiveDate | date | Effective date |
| Pricebook2Id | str | Pricebook ID |
| OwnerId | str | Owner user ID |

### OrderItem

| Column | Type | Notes |
|---|---|---|
| Id | str | Order item ID |
| OrderId | str | Order ID |
| Product2Id | str | Product ID |
| Quantity | float | Quantity |
| UnitPrice | float | Unit price |
| PriceBookEntryId | str | Pricebook entry ID |

---

## DB 5 — activities (DuckDB)

### Event

| Column | Type | Notes |
|---|---|---|
| Id | str | Event ID |
| WhatId | str | Related object ID |
| OwnerId | str | Owner user ID |
| StartDateTime | datetime | Start date/time |
| Subject | str | Event subject (unstructured text) |
| Description | str | Event description (unstructured text) |
| DurationInMinutes | int | Duration in minutes |
| Location | str | Location |
| IsAllDayEvent | bool | All-day flag |

### Task

| Column | Type | Notes |
|---|---|---|
| Id | str | Task ID |
| WhatId | str | Related object ID |
| OwnerId | str | Owner user ID |
| Priority | str | Task priority |
| Status | str | Task status |
| ActivityDate | date | Activity date |
| Subject | str | Task subject (unstructured text) |
| Description | str | Task description (unstructured text) |

### VoiceCallTranscript__c

| Column | Type | Notes |
|---|---|---|
| Id | str | Call transcript ID |
| OpportunityId__c | str | Opportunity ID |
| LeadId__c | str | Lead ID — join key |
| Body__c | str | Call transcript body (unstructured text) |
| CreatedDate | date | Creation date |
| EndTime__c | datetime | Call end time |

---

## DB 6 — territory (SQLite)

### Territory2

| Column | Type | Notes |
|---|---|---|
| Id | str | Territory ID |
| Name | str | Territory name |
| Description | str | Territory description (unstructured text) |

### UserTerritory2Association

| Column | Type | Notes |
|---|---|---|
| Id | str | Association ID |
| UserId | str | User ID — join key |
| Territory2Id | str | Territory ID |

---

## Cross-Database Join Patterns

| From DB.Table.Column | To DB.Table.Column | Notes |
|---|---|---|
| core_crm.Account.Id | sales_pipeline.Contract.AccountId | Account linkage |
| core_crm.Account.Id | sales_pipeline.Opportunity.AccountId | Account linkage |
| core_crm.Account.Id | sales_pipeline.Quote.AccountId | Account linkage |
| core_crm.Account.Id | products_orders.Order.AccountId | Account linkage |
| core_crm.Account.Id | support.Case.accountid | Account linkage |
| core_crm.Account.Id | support.livechattranscript.accountid | Account linkage |
| core_crm.Contact.Id | sales_pipeline.Opportunity.ContactId | Contact linkage |
| core_crm.Contact.Id | sales_pipeline.Quote.ContactId | Contact linkage |
| core_crm.Contact.Id | support.Case.contactid | Contact linkage |
| core_crm.Contact.Id | support.livechattranscript.contactid | Contact linkage |
| core_crm.User.Id | sales_pipeline.Lead.OwnerId | User ownership |
| core_crm.User.Id | sales_pipeline.Opportunity.OwnerId | User ownership |
| core_crm.User.Id | products_orders.Order.OwnerId | User ownership |
| core_crm.User.Id | support.Case.ownerid | User ownership |
| core_crm.User.Id | support.livechattranscript.ownerid | User ownership |
| core_crm.User.Id | activities.Event.OwnerId | User ownership |
| core_crm.User.Id | activities.Task.OwnerId | User ownership |
| core_crm.User.Id | territory.UserTerritory2Association.UserId | Territory assignment |
| sales_pipeline.Lead.Id | activities.VoiceCallTranscript__c.LeadId__c | Lead activities |
| sales_pipeline.Opportunity.Id | activities.VoiceCallTranscript__c.OpportunityId__c | Opportunity activities |
| products_orders.Product2.Id | sales_pipeline.OpportunityLineItem.Product2Id | Product linkage |
| products_orders.Product2.Id | sales_pipeline.QuoteLineItem.Product2Id | Product linkage |
| products_orders.OrderItem.Id | support.Case.orderitemid__c | Order support |

**Merge in Python.** Query each database separately, then join on shared ID fields. Use pandas.merge() with how='inner' for required joins, 'left' for optional.

---

## Valid Intra-Database Joins

**SQLite — core_crm:**

| Join | Key | Type |
|---|---|---|
| Contact → Account | AccountId | INNER |

**DuckDB — sales_pipeline:**

| Join | Key | Type |
|---|---|---|
| Opportunity → Account | AccountId | INNER |
| Opportunity → Contact | ContactId | INNER |
| Opportunity → Contract | ContractID__c | LEFT |
| OpportunityLineItem → Opportunity | OpportunityId | INNER |
| Quote → Opportunity | OpportunityId | INNER |
| Quote → Account | AccountId | INNER |
| Quote → Contact | ContactId | INNER |
| QuoteLineItem → Quote | QuoteId | INNER |
| Lead → User | OwnerId | LEFT |

**PostgreSQL — support:**

| Join | Key | Type |
|---|---|---|
| Case → Account | accountid | INNER |
| Case → Contact | contactid | INNER |
| Case → User | ownerid | LEFT |
| emailmessage → Case | parentid | LEFT |
| livechattranscript → Case | caseid | LEFT |
| livechattranscript → Account | accountid | LEFT |
| livechattranscript → Contact | contactid | LEFT |
| livechattranscript → User | ownerid | LEFT |

**SQLite — products_orders:**

| Join | Key | Type |
|---|---|---|
| Product2 → ProductCategoryProduct | Id | LEFT |
| ProductCategoryProduct → ProductCategory | ProductCategoryId | LEFT |
| PricebookEntry → Pricebook2 | Pricebook2Id | INNER |
| PricebookEntry → Product2 | Product2Id | INNER |
| Order → Account | AccountId | INNER |
| Order → Pricebook2 | Pricebook2Id | LEFT |
| Order → User | OwnerId | LEFT |
| OrderItem → Order | OrderId | INNER |
| OrderItem → Product2 | Product2Id | INNER |
| OrderItem → PricebookEntry | PriceBookEntryId | LEFT |

**DuckDB — activities:**

| Join | Key | Type |
|---|---|---|
| Event → User | OwnerId | LEFT |
| Task → User | OwnerId | LEFT |
| VoiceCallTranscript__c → Lead | LeadId__c | LEFT |
| VoiceCallTranscript__c → Opportunity | OpportunityId__c | LEFT |

**SQLite — territory:**

| Join | Key | Type |
|---|---|---|
| UserTerritory2Association → User | UserId | INNER |
| UserTerritory2Association → Territory2 | Territory2Id | INNER |

---

## Known Query Patterns (13 queries)

1. **Lead Qualification (BANT)**: Check VoiceCallTranscript__c.Body__c for missing BANT factors (Budget, Authority, Need, Timeline) to determine qualification status.
2. **Policy Violation Detection**: Search Case.description and knowledge__kav.faq_answer__c for policy violations, return relevant article ID if found.
3. **Sales Stage Analysis**: Find Opportunity with StageName = 'Negotiation' based on activity patterns.
4. **Monthly Aggregation**: Identify month (November) with highest activity or sales from Event.StartDateTime or Opportunity.CreatedDate.
5. **Issue Resolution**: Match Case.description to issue__c.description__c, return matching issue ID.
6. **Knowledge Article Lookup**: Find knowledge__kav.id based on Case.subject or description similarity.
7. **Support Escalation**: Identify knowledge article for policy violation cases in Case.description.
8. **Agent Assignment**: Find User.Id (agent) with most cases in Case.ownerid for a specific account.
9. **Geographic Analysis**: Extract state abbreviation (MI) from Account.ShippingState for regional insights.
10. **Performance Metrics**: Identify top-performing agent User.Id based on Opportunity.Amount and Case resolution.
11. **Product Recommendations**: Find Product2.Id based on Order history and Case.description mentions.
12. **Ownership Transfer**: Determine correct User.Id (agent) for Case reassignment based on Territory2 associations.
13. **Resource Allocation**: Find User.Id (agent) with capacity based on current Task and Event assignments.

- **ID corruption:** ~25% of ID fields have leading '#' (e.g., '#001Wt00000PFj4zIAD'). Strip '#' before joins.
- **Text corruption:** ~20% of text fields have trailing whitespace. Use TRIM() or strip() in queries.
- **Case sensitivity:** ID fields are case-sensitive; text searches may be case-insensitive.
- **Date formats:** Dates are stored as strings; cast to DATE type for comparisons.
- **Missing joins:** Not all entities have complete linkage; use LEFT joins for optional relationships.
- **Unstructured extraction:** Text fields (description, body, subject) require NLP for structured data extraction.
- **State abbreviations:** ShippingState may use abbreviations (e.g., 'MI' for Michigan); expand for consistency.
- **BANT factors:** Lead qualification uses Budget, Authority, Need, Timeline (BANT) framework.
- **Sales stages:** Opportunities progress through Qualification → Discovery → Quote → Negotiation → Closed.
- **Knowledge articles:** Support cases reference knowledge__kav articles for resolution.
- **Voice transcripts:** Call logs in VoiceCallTranscript__c contain unstructured conversation text.