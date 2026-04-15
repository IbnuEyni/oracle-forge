# KB v2 - pass@1 Scoring Explanation

## What is pass@1?

In DataAgentBench (DAB), **pass@1** measures the percentage of queries where the agent produces a **correct answer on its first attempt**. Only the first response is scored — retries or revisions are not counted.

## How the evaluation works

- DAB contains 54 queries across 12 datasets.
- Each query is run for at least 50 independent trials (n ≥ 50).
- For every trial, only the first answer is evaluated as correct or incorrect.
- The pass@1 score is calculated as:  
  **correct first responses ÷ total trials** across all queries and trials.

## Why pass@1 is used

pass@1 reflects real-world production use: users expect a reliable answer on the first delivery. It strongly rewards high-quality context engineering, accurate tool use, and self-correction capability in a single pass.

## Current Benchmark Scores

- The best published score on the DAB leaderboard is **54.3%** (PromptQL + Gemini 3.1 Pro).
- The original DAB paper reports **38% pass@1** for the best plain frontier model (Gemini-3-Pro).

## What These Scores Mean

- **54.3%** represents the current state-of-the-art for a full engineered system.
- **38%** highlights the difficulty of the benchmark when relying only on a raw large language model without additional engineering.

A strong performance in this challenge is one that approaches or exceeds the current leaderboard benchmark of 54.3%.

## What pass@1 Measures in Practice

pass@1 tests the agent's ability to:
- Route queries correctly across heterogeneous databases
- Resolve ill-formatted join keys
- Transform unstructured text into usable facts
- Apply domain knowledge on the first attempt

It measures first-delivery reliability rather than recoverability after failures.

## Why Measurable Improvement Matters

The Oracle Forge challenge requires measurable improvement in pass@1 between runs. This demonstrates that the evaluation harness is working and that updates to the Knowledge Base and self-correction mechanisms are producing real gains in agent performance.