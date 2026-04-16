"""
Oracle Forge Evaluation Harness
Runs DAB queries, validates against ground truth, produces pass@1 score log.
On failure, auto-diagnoses the root cause and writes a new correction entry
to kb/corrections/corrections.md — live self-correction without human intervention.

Usage:
    python eval/harness.py --dataset yelp --queries 1,2,3,4,5,6,7 \
        --llm google/gemini-3.1-pro-preview --iterations 20
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DAB_PATH = Path(__file__).parent.parent / "DataAgentBench"
ORACLE_RUN = Path(__file__).parent.parent / "agent" / "oracle_run.py"
SCORE_LOG = Path(__file__).parent / "score_log.jsonl"
CORRECTIONS = Path(__file__).parent.parent / "kb" / "corrections" / "corrections.md"
VENV_PYTHON = DAB_PATH / ".venv" / "bin" / "python"


def get_python():
    """Use venv python if available, else fall back to current interpreter."""
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def get_latest_log(dataset: str, query_id: int) -> dict | None:
    log_dir = DAB_PATH / f"query_{dataset}" / f"query{query_id}" / "logs" / "data_agent"
    if not log_dir.exists():
        return None
    runs = sorted(log_dir.iterdir(), reverse=True)
    if not runs:
        return None
    try:
        with open(runs[0] / "final_agent.json") as f:
            return json.load(f)
    except Exception:
        return None


def get_tool_calls(dataset: str, query_id: int) -> list[dict]:
    """Read tool_calls.jsonl from the latest run."""
    log_dir = DAB_PATH / f"query_{dataset}" / f"query{query_id}" / "logs" / "data_agent"
    if not log_dir.exists():
        return []
    runs = sorted(log_dir.iterdir(), reverse=True)
    if not runs:
        return []
    tool_log = runs[0] / "tool_calls.jsonl"
    if not tool_log.exists():
        return []
    calls = []
    for line in tool_log.read_text().strip().split("\n"):
        if line.strip():
            try:
                calls.append(json.loads(line))
            except Exception:
                pass
    return calls


def validate_query(dataset: str, query_id: int, llm_answer: str) -> tuple[bool, str]:
    validate_path = DAB_PATH / f"query_{dataset}" / f"query{query_id}" / "validate.py"
    if not validate_path.exists():
        return False, "No validate.py found"
    ns = {}
    exec(validate_path.read_text(), ns)
    return ns["validate"](llm_answer)


def diagnose_failure(dataset: str, query_id: int, answer: str,
                     terminate_reason: str, validate_reason: str) -> dict:
    """
    Analyse the tool call log and answer to produce a structured diagnosis.
    Returns a dict with: pattern, what_was_wrong, correct_approach, example_code
    """
    tool_calls = get_tool_calls(dataset, query_id)
    errors = []
    for c in tool_calls:
        result = str(c.get("result", ""))
        if "success" in result and "False" in result:
            errors.append(result[:300])

    error_text = " ".join(errors).lower()
    answer_lower = answer.lower() if answer else ""

    # Pattern matching on known failure signatures
    if terminate_reason == "max_iterations":
        if "nan" in error_text or "nameerror" in error_text:
            return {
                "pattern": "NaN/NameError in execute_python",
                "what_was_wrong": (
                    f"Agent hit max_iterations on {dataset} Q{query_id}. "
                    "execute_python failed repeatedly with NameError: name 'nan' is not defined. "
                    "Agent used bare `nan` instead of `float('nan')` or `pd.NA`."
                ),
                "correct_approach": (
                    "Never use bare `nan` in execute_python. Use `float('nan')`, `pd.NA`, or `numpy.nan`. "
                    "Always import numpy before using numpy.nan."
                ),
                "example_code": (
                    "import numpy as np\nimport pandas as pd\n"
                    "# Use np.nan not bare nan\ndf = df.replace(float('nan'), np.nan)"
                ),
            }
        if "typeerror" in error_text or "list indices" in error_text:
            return {
                "pattern": "TypeError on MongoDB results",
                "what_was_wrong": (
                    f"Agent hit max_iterations on {dataset} Q{query_id}. "
                    "execute_python failed with TypeError — agent used integer indices on dict results."
                ),
                "correct_approach": (
                    "Always wrap MongoDB results in pd.DataFrame() before accessing fields. "
                    "Use df['field'] not result[0]."
                ),
                "example_code": (
                    "import pandas as pd\ndf = pd.DataFrame(records)\nvalue = df['field_name']"
                ),
            }
        return {
            "pattern": "max_iterations — root cause unclear",
            "what_was_wrong": (
                f"Agent hit max_iterations on {dataset} Q{query_id} ({terminate_reason}). "
                f"Validate reason: {validate_reason}. "
                f"Last errors: {error_text[:200] if error_text else 'none recorded'}."
            ),
            "correct_approach": (
                "Increase --iterations. Check tool_calls.jsonl for the repeating error pattern. "
                "Add dataset-specific hints to db_description_withhint.txt."
            ),
            "example_code": "",
        }

    if "wrong" in validate_reason.lower() or "not found" in validate_reason.lower():
        if "category" in validate_reason.lower():
            return {
                "pattern": "Wrong category returned",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent returned wrong category. "
                    f"Validate: {validate_reason}. Answer: {answer[:100]}"
                ),
                "correct_approach": (
                    "Check which field contains the category. In Yelp, categories are in the "
                    "MongoDB business 'categories' field as a list. "
                    "Do not use DuckDB category fields — they may be stale or differently formatted."
                ),
                "example_code": (
                    "# MongoDB business categories field\n"
                    "df['categories'] = df['categories'].apply(lambda x: x if isinstance(x, list) else [])\n"
                    "all_cats = df.explode('categories')['categories'].value_counts()"
                ),
            }
        if "number" in validate_reason.lower() or "value" in validate_reason.lower():
            return {
                "pattern": "Wrong numeric value returned",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent returned wrong number. "
                    f"Validate: {validate_reason}. Answer: {answer[:100]}"
                ),
                "correct_approach": (
                    "Check CAST: DuckDB rating is BIGINT — always CAST(rating AS FLOAT) before AVG. "
                    "Check MongoDB limit: always set limit=10000 to avoid missing documents. "
                    "Check join key normalisation: strip businessref_/businessid_ prefixes before joining."
                ),
                "example_code": (
                    "-- DuckDB\nSELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)\n"
                    "-- MongoDB\n{\"collection\": \"business\", \"filter\": {}, \"limit\": 10000}"
                ),
            }
        if "name" in validate_reason.lower() or "missing" in validate_reason.lower():
            return {
                "pattern": "Expected name/value missing from answer",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: expected value not found in answer. "
                    f"Validate: {validate_reason}. Answer: {answer[:100]}"
                ),
                "correct_approach": (
                    "Agent may have queried the wrong database or field. "
                    "Verify which database holds the required field using list_db first. "
                    "For Yelp state extraction: use description field regex, not a dedicated state column."
                ),
                "example_code": (
                    "# State extraction from Yelp MongoDB description field\n"
                    "df['state'] = df['description'].str.extract(r',\\s*([A-Z]{2})\\s*\\d{5}')"
                ),
            }

    return {
        "pattern": "Unknown failure",
        "what_was_wrong": (
            f"{dataset} Q{query_id}: failed with terminate_reason={terminate_reason}. "
            f"Validate: {validate_reason}. Answer: {answer[:100] if answer else 'EMPTY'}"
        ),
        "correct_approach": "Inspect tool_calls.jsonl manually to identify the root cause.",
        "example_code": "",
    }


def write_correction(dataset: str, query_id: int, diagnosis: dict):
    """Append a new correction entry to corrections.md if this pattern is not already logged."""
    existing = CORRECTIONS.read_text() if CORRECTIONS.exists() else ""

    # Skip if this exact dataset+query pattern already exists
    marker = f"{dataset} Q{query_id}"
    if marker in existing and diagnosis["pattern"] in existing:
        print(f"  [self-correct] Correction for {marker} already exists — skipping")
        return

    # Get next correction number
    nums = re.findall(r"## Correction (\d+)", existing)
    next_num = (max(int(n) for n in nums) + 1) if nums else 1

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"""
---

## Correction {next_num:03d} — {date} [AUTO]

**Dataset:** {dataset} | **Query ID:** {query_id}
**Failure pattern:** {diagnosis['pattern']}

**What was wrong:**
{diagnosis['what_was_wrong']}

**Correct approach:**
{diagnosis['correct_approach']}
"""
    if diagnosis["example_code"]:
        entry += f"\n**Example:**\n```python\n{diagnosis['example_code']}\n```\n"

    with open(CORRECTIONS, "a") as f:
        f.write(entry)

    print(f"  [self-correct] ✍️  Correction {next_num:03d} written for {dataset} Q{query_id}: {diagnosis['pattern']}")


def run_harness(dataset: str, query_ids: list[int], llm: str, iterations: int = 20):
    print(f"\n{'='*60}")
    print(f"Oracle Forge Evaluation Harness")
    print(f"Dataset: {dataset} | Model: {llm} | Queries: {query_ids}")
    print(f"{'='*60}\n")

    python = get_python()

    # Run agent on each query via oracle_run.py (KB injection + hints)
    for qid in query_ids:
        print(f"Running Q{qid}...")
        subprocess.run(
            [python, str(ORACLE_RUN),
             "--dataset", dataset,
             "--query_id", str(qid),
             "--llm", llm,
             "--iterations", str(iterations),
             "--use_hints"],
            cwd=str(DAB_PATH),
        )

    # Collect, validate, and auto-correct
    results = []
    passed = 0

    for qid in query_ids:
        log = get_latest_log(dataset, qid)
        if not log:
            results.append({"query_id": qid, "passed": False,
                            "reason": "no log found", "answer": ""})
            print(f"  Q{qid}: ❌ NO LOG")
            continue

        answer = log.get("final_result", "")
        terminate = log.get("terminate_reason", "")
        llm_calls = log.get("llm_call_count", 0)

        is_valid, reason = validate_query(dataset, qid, answer)
        if is_valid:
            passed += 1

        results.append({
            "query_id": qid,
            "passed": is_valid,
            "reason": reason,
            "answer": answer[:100] if answer else "EMPTY",
            "terminate_reason": terminate,
            "llm_calls": llm_calls,
        })

        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"  Q{qid}: {status} | {terminate} | calls={llm_calls} | {reason}")

        # Live self-correction: diagnose and write correction for every failure
        if not is_valid:
            diagnosis = diagnose_failure(dataset, qid, answer, terminate, reason)
            write_correction(dataset, qid, diagnosis)

    # Score
    total = len(query_ids)
    score = round(passed / total * 100, 1) if total else 0

    print(f"\n{'='*60}")
    print(f"SCORE: {passed}/{total} = {score}% pass@1")
    print(f"{'='*60}\n")

    # Append to score log
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset,
        "llm": llm,
        "total": total,
        "passed": passed,
        "pass_at_1_pct": score,
        "results": results,
    }
    with open(SCORE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Score logged to {SCORE_LOG}")
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="yelp")
    parser.add_argument("--queries", default="1,2,3,4,5,6,7")
    parser.add_argument("--llm", default="google/gemini-3.1-pro-preview")
    parser.add_argument("--iterations", type=int, default=20)
    args = parser.parse_args()

    query_ids = [int(q) for q in args.queries.split(",")]
    run_harness(args.dataset, query_ids, args.llm, args.iterations)
