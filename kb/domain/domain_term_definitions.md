# KB v2 - Domain Term Definitions for DataAgentBench

## Overview

This document provides precise definitions for frequently ambiguous business terms in DataAgentBench queries. These definitions help the agent avoid common misinterpretations when analyzing data across multiple databases.

### churn / churn rate / active customer

- **Definition**: Customers who were previously active according to the dataset's retention rules but have since stopped transacting or engaging with the service.
- **Key Distinction**: Must differentiate between "never-active/new customers" and "previously active customers who left".
- **Why it matters**: Incorrect identification inflates churn rate and mislabels healthy segments as at-risk.

### revenue

- **Definition**: The monetary value from sales or services, which may refer to gross revenue, recognized revenue, or net revenue depending on the dataset and business rules.
- **Key Distinction**: Different definitions (gross vs net, billed vs recognized) exist within the same organization.
- **Why it matters**: Using the wrong definition distorts growth calculations, segment rankings, and performance analysis.

### fiscal year boundaries and quarters

- **Definition**: Accounting periods defined by the organization's fiscal calendar, which often does not align with calendar year boundaries.
- **Key Distinction**: Fiscal quarters must be derived from dataset metadata or knowledge base rather than assumed to follow calendar months.
- **Why it matters**: Misaligned periods can reverse trend conclusions and lead to incorrect period-over-period comparisons.

### repeat purchase rate

- **Definition**: The proportion of eligible customers (or orders) that make additional purchases within a defined cohort or time window.
- **Key Distinction**: Requires correct denominator (eligible base) and observation period, not simply raw order counts.
- **Why it matters**: Incorrect calculation understates or overstates true customer loyalty.

### customer segments

- **Definition**: Groups of customers defined by explicit business rules in the dataset (e.g., revenue tier, behavior cluster, account type, or purchase history).
- **Key Distinction**: Segments follow dataset-specific logic rather than arbitrary groupings.
- **Why it matters**: Wrong segment definition leads to invalid comparisons and misleading business insights.

### support ticket volume / severity

- **Definition**:
  - Volume: Total number of support tickets in a given period.
  - Severity: Dataset-specific classification indicating business impact and priority level.
- **Key Distinction**: Tickets are not equal — severity reflects different levels of urgency and cost to the business.
- **Why it matters**: Correlating raw volume without severity can hide critical product or service issues.

## Usage Note

Inject this document when the query involves business metrics, customer behavior, temporal analysis, or segmentation.