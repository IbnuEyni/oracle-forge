# Injection Test Rubric

## Scope

This package is for manual injection testing of the three KB v2 domain documents:

- `kb/domain/dab-failure-categories.md`
- `kb/domain/join-key-glossary.md`
- `kb/domain/unstructured-field-inventory.md`

## How To Run

1. Open `claude.ai` in a fresh chat.
2. Paste the entire contents of the target document as the first message.
3. Add the test question at the bottom of that same message, under a clear label such as `Test question:`.
4. Do not paste any answer key or rubric into the chat.
5. Grade the response using the global rules and the document-specific criteria below.

Use this file as a local grader only. Do not paste this file into the test chat.

## Global PASS Rules

- The answer is based on the pasted document.
- The answer is direct and does not hedge.
- The answer includes every required point.
- The answer may paraphrase as long as the meaning matches.
- The answer does not invent unsupported facts.

## Global FAIL Rules

- The answer misses a required point.
- The answer contradicts the document.
- The answer uses outside knowledge that is not in the pasted document.
- The answer says the question cannot be answered when the document provides the method.
- The answer refuses or deflects instead of answering.

## Test 1: Unstructured Field Inventory

**Target document:** `kb/domain/unstructured-field-inventory.md`

**Test question to append:**

```text
Based on the document above: A query asks "how many cancellations were pricing-related?" but there is no cancellation_reason column. What should the agent do?
```

**Required answer points:**

- The agent should check unstructured text fields before saying the data is unavailable.
- The answer should mention fields like `customers.notes` and `interactions.transcript`.
- The answer should use pattern matching or text functions, such as `ILIKE '%cancel%'` and `ILIKE '%pric%'`, or an equivalent extraction strategy.
- The answer should not stop at `data not available`.

**PASS if:**

- The answer says to inspect the unstructured fields and extract the answer from text.

**FAIL if:**

- The answer recommends only structured columns.
- The answer says the data is unavailable.
- The answer misses the pattern-matching step.

## Test 2: Join Key Glossary

**Target document:** `kb/domain/join-key-glossary.md`

**Test question to append:**

```text
Based on the document above: How do I join user data between PostgreSQL and MongoDB when user_id is "USR-1042" in PostgreSQL and userId is 1042 in MongoDB?
```

**Required answer points:**

- The answer should recognize that the values use different formats.
- The answer should strip `USR-` from the PostgreSQL value.
- The answer should normalize both values to a common comparable form, usually an integer.
- The answer should join on the normalized values rather than on the raw fields.
- If the answer mentions sampling values first, that is fine, but it is not required for PASS.

**PASS if:**

- The answer explains the normalization step and the join outcome clearly.

**FAIL if:**

- The answer joins the raw values directly.
- The answer ignores the format mismatch.
- The answer misses the normalization step.

## Test 3: DAB Failure Categories

**Target document:** `kb/domain/dab-failure-categories.md`

**Test question to append:**

```text
Based on the document above: What are the 4 DAB failure categories and why does the ill-formatted join keys category cause agent failures?
```

**Required answer points:**

- The answer should name all 4 categories:
  - Multi-Database Integration
  - Ill-Formatted Join Keys
  - Unstructured Text Transformation
  - Domain Knowledge Gaps
- The answer should explain that ill-formatted join keys fail because the same entity has different ID formats across databases.
- The answer should explain that a direct join on the raw fields returns no match or zero rows.
- The answer may describe normalization, sampling, or mapping as the fix.

**PASS if:**

- The answer identifies all 4 categories and explains the join-key failure mechanism correctly.

**FAIL if:**

- The answer lists fewer than 4 categories.
- The answer gets the failure reason wrong.
- The answer misses the direct-join mismatch explanation.

## Scoring Notes

- Treat exact wording as flexible.
- Treat equivalent SQL or equivalent normalization logic as acceptable.
- Require the core idea, not verbatim phrasing.
- If the answer adds extra details, only penalize them if they contradict the document.

## Result Log

| Document | Verdict | Notes |
|---|---|---|
| `unstructured-field-inventory.md` |  |  |
| `join-key-glossary.md` |  |  |
| `dab-failure-categories.md` |  |  |

## Short Recording Template

Use this after each test:

```text
Document:
Question:
Verdict:
Reason:
Notes:
```
