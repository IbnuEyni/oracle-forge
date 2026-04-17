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
# Server has DataAgentBench at ~/DataAgentBench (sibling of oracle-forge)
# Fall back to that location if the relative path doesn't exist
if not DAB_PATH.exists():
    DAB_PATH = Path.home() / "DataAgentBench"
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
    Diagnose failure from tool call logs only.
    NEVER includes ground truth values, expected answers, or validate_reason text
    in the correction — only structural failure patterns and fix approaches.
    """
    tool_calls = get_tool_calls(dataset, query_id)
    errors = []
    for c in tool_calls:
        result = str(c.get("result", ""))
        if "success" in result and "False" in result:
            errors.append(result[:300])

    error_text = " ".join(errors).lower()

    # --- Classify failure type from structural signals only ---

    # 1. max_iterations failures — diagnose from error log
    if terminate_reason == "max_iterations":
        if "nan" in error_text or "nameerror" in error_text:
            return {
                "pattern": "NaN/NameError in execute_python",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent hit max_iterations. "
                    "execute_python failed repeatedly with NameError — "
                    "bare `nan` used instead of a valid null representation."
                ),
                "correct_approach": (
                    "Never use bare `nan` in execute_python. "
                    "Use `float('nan')`, `pd.NA`, or `np.nan` (after importing numpy). "
                    "Always add `import numpy as np` before using np.nan."
                ),
                "example_code": (
                    "import numpy as np\nimport pandas as pd\n"
                    "# correct null handling\ndf = df.replace(float('nan'), np.nan)\n"
                    "df = df.dropna(subset=['required_column'])"
                ),
            }
        if "typeerror" in error_text or "list indices" in error_text:
            return {
                "pattern": "TypeError — integer index used on dict result",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent hit max_iterations. "
                    "execute_python failed with TypeError — "
                    "agent accessed a list-of-dicts result using integer indices instead of field names."
                ),
                "correct_approach": (
                    "Always wrap tool results in pd.DataFrame() before field access. "
                    "Use df['field_name'] not result[0]. "
                    "Check result type with type(result) before processing."
                ),
                "example_code": (
                    "import pandas as pd\n"
                    "# records is a list of dicts from query_db\n"
                    "df = pd.DataFrame(records)\n"
                    "# now access fields by name\nvalue = df['field_name']"
                ),
            }
        if "keyerror" in error_text or "column" in error_text:
            return {
                "pattern": "KeyError — wrong field name used",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent hit max_iterations. "
                    "execute_python failed with KeyError — "
                    "agent referenced a field that does not exist in the result."
                ),
                "correct_approach": (
                    "Always call list_db first to inspect available fields. "
                    "Print df.columns after creating the DataFrame to verify field names. "
                    "Field names differ between databases — check db_description for exact names."
                ),
                "example_code": (
                    "import pandas as pd\n"
                    "df = pd.DataFrame(records)\n"
                    "print(df.columns.tolist())  # inspect before accessing"
                ),
            }
        if "syntaxerror" in error_text:
            return {
                "pattern": "SyntaxError in generated Python code",
                "what_was_wrong": (
                    f"{dataset} Q{query_id}: agent hit max_iterations. "
                    "execute_python failed with SyntaxError — "
                    "generated code had unterminated strings or invalid syntax."
                ),
                "correct_approach": (
                    "Keep execute_python code short and simple. "
                    "Avoid multi-line f-strings. "
                    "Use single quotes inside double-quoted strings to avoid escaping issues."
                ),
                "example_code": "",
            }
        # Generic max_iterations — no specific error pattern found
        return {
            "pattern": "max_iterations — no tool errors recorded",
            "what_was_wrong": (
                f"{dataset} Q{query_id}: agent hit max_iterations with no recorded tool errors. "
                "The agent may have been looping on query reformulation without making progress."
            ),
            "correct_approach": (
                "Increase --iterations to 30. "
                "Add dataset-specific hints to db_description_withhint.txt to guide the first query. "
                "Check that the correct database type is being queried for this dataset."
            ),
            "example_code": "",
        }

    # 2. return_answer failures — diagnose from failure category only, no values
    vr_lower = validate_reason.lower()

    if "category" in vr_lower:
        return {
            "pattern": "Wrong category field used",
            "what_was_wrong": (
                f"{dataset} Q{query_id}: agent returned an answer but the category field "
                "was sourced from the wrong table or collection."
            ),
            "correct_approach": (
                "In Yelp, business categories are stored in the MongoDB business collection "
                "as a list in the 'categories' field — not in DuckDB. "
                "Explode the list before counting. "
                "Do not use DuckDB category fields — they may be stale or differently formatted."
            ),
            "example_code": (
                "import pandas as pd\n"
                "# MongoDB business categories field is a list\n"
                "df['categories'] = df['categories'].apply(\n"
                "    lambda x: x if isinstance(x, list) else []\n"
                ")\n"
                "all_cats = df.explode('categories')['categories'].value_counts()"
            ),
        }

    if "number" in vr_lower or "value" in vr_lower or "float" in vr_lower:
        return {
            "pattern": "Incorrect numeric computation",
            "what_was_wrong": (
                f"{dataset} Q{query_id}: agent returned a numeric answer but the value "
                "was computed incorrectly — likely due to integer truncation or incomplete data."
            ),
            "correct_approach": (
                "Always CAST numeric columns to FLOAT before computing AVG in DuckDB: "
                "AVG(CAST(column AS FLOAT)). "
                "Always set MongoDB query limit to 10000 to avoid missing documents. "
                "Verify join key normalisation: strip prefixes before merging DataFrames."
            ),
            "example_code": (
                "-- DuckDB: cast before averaging\n"
                "SELECT AVG(CAST(rating AS FLOAT)) FROM review WHERE business_ref IN (...)\n\n"
                "-- MongoDB: always set explicit limit\n"
                '{"collection": "business", "filter": {}, "limit": 10000}'
            ),
        }

    if "name" in vr_lower or "missing" in vr_lower or "title" in vr_lower:
        return {
            "pattern": "Required entity name missing from answer",
            "what_was_wrong": (
                f"{dataset} Q{query_id}: agent returned an answer but a required "
                "entity name or identifier was absent — likely queried the wrong field or database."
            ),
            "correct_approach": (
                "Verify which database and field holds the entity name for this dataset. "
                "Use list_db to inspect available collections and tables before querying. "
                "For Yelp: business names are in MongoDB business collection 'name' field. "
                "For bookreview: book titles are in PostgreSQL books_info 'title' field."
            ),
            "example_code": (
                "# Always verify field existence before selecting\n"
                "import pandas as pd\n"
                "df = pd.DataFrame(records)\n"
                "print(df.columns.tolist())  # confirm 'name' or 'title' field exists"
            ),
        }

    if "no_tool_call" in terminate_reason:
        return {
            "pattern": "Agent made no tool calls",
            "what_was_wrong": (
                f"{dataset} Q{query_id}: agent terminated without calling any tools — "
                "responded directly from context without querying the databases."
            ),
            "correct_approach": (
                "Always use --use_hints flag. Without schema hints the agent does not know "
                "which databases to query and falls back to generating a text response. "
                "Verify OPENROUTER_API_KEY is set and the model supports tool calling."
            ),
            "example_code": "",
        }

    # Fallback — structural description only, no values
    return {
        "pattern": "Answer returned but failed validation",
        "what_was_wrong": (
            f"{dataset} Q{query_id}: agent returned an answer that did not pass validation. "
            f"Terminate reason: {terminate_reason}. "
            "The failure category could not be automatically classified from tool call logs."
        ),
        "correct_approach": (
            "Inspect the tool_calls.jsonl log for this query to identify which step "
            "produced the incorrect intermediate result. "
            "Check join keys, field names, and database routing."
        ),
        "example_code": "",
    }


def write_correction(dataset: str, query_id: int, diagnosis: dict):
    """Append a new correction entry to corrections.md.
    Only structural patterns and fix approaches are written — no ground truth values.
    """
    existing = CORRECTIONS.read_text() if CORRECTIONS.exists() else ""

    # Skip if this exact dataset+query+pattern already exists
    marker = f"{dataset} Q{query_id}"
    if marker in existing and diagnosis["pattern"] in existing:
        print(f"  [self-correct] Correction for {marker} ({diagnosis['pattern']}) already exists — skipping")
        return

    nums = re.findall(r"## Correction (\d+)", existing)
    next_num = (max(int(n) for n in nums) + 1) if nums else 1
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entry = f"\n---\n\n## Correction {next_num:03d} — {date} [AUTO]\n\n"
    entry += f"**Dataset:** {dataset} | **Query ID:** {query_id}\n"
    entry += f"**Failure pattern:** {diagnosis['pattern']}\n\n"
    entry += f"**What was wrong:**\n{diagnosis['what_was_wrong']}\n\n"
    entry += f"**Correct approach:**\n{diagnosis['correct_approach']}\n"
    if diagnosis["example_code"]:
        entry += f"\n**Example:**\n```\n{diagnosis['example_code']}\n```\n"

    with open(CORRECTIONS, "a") as f:
        f.write(entry)

    print(f"  [self-correct] ✍️  Correction {next_num:03d} written — {dataset} Q{query_id}: {diagnosis['pattern']}")


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
        # Skip if failure was due to API error (not an agent reasoning failure)
        if not is_valid and terminate not in ('llm_response_failed',):
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
