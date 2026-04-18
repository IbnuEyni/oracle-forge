"""
Oracle Forge run_agent wrapper
Injects KB context into DataAgent then runs DAB agent via subprocess.
Usage: python ~/oracle-forge/agent/oracle_run.py --dataset yelp --query_id 1 --llm anthropic/claude-sonnet-4.5 --iterations 10 --use_hints
"""
import sys
import os
import subprocess

DAB_PATH = os.path.expanduser("~/DataAgentBench")
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set PYTHONPATH so kb_injector is importable as a sitecustomize
env = os.environ.copy()
existing_path = env.get("PYTHONPATH", "")
env["PYTHONPATH"] = f"{AGENT_DIR}:{DAB_PATH}:{existing_path}"
env["ORACLE_FORGE_KB_INJECT"] = "1"

# Run DAB agent with KB injection via sitecustomize trick
# We use -c to run a small bootstrap that imports kb_injector first
bootstrap = f"""
import sys
import os
sys.path.insert(0, '{AGENT_DIR}')
sys.path.insert(0, '{DAB_PATH}')
import kb_injector
os.chdir('{DAB_PATH}')
globals()['__file__'] = '{DAB_PATH}/run_agent.py'
exec(open('{DAB_PATH}/run_agent.py').read(), {{'__file__': '{DAB_PATH}/run_agent.py', '__name__': '__main__'}})
"""

result = subprocess.run(
    [sys.executable, "-c", bootstrap] + sys.argv[1:],
    env=env,
    cwd=DAB_PATH
)

# Post-run: show query + result + validation
try:
    import argparse, json, glob
    p = argparse.ArgumentParser()
    p.add_argument("--dataset"); p.add_argument("--query_id", type=int)
    args, _ = p.parse_known_args()
    if args.dataset and args.query_id:
        query_dir = os.path.join(DAB_PATH, f"query_{args.dataset}", f"query{args.query_id}")
        # Show query
        q = json.load(open(os.path.join(query_dir, "query.json")))
        question = q if isinstance(q, str) else q.get("query", str(q))
        print(f"\n{'='*60}")
        print(f"QUERY:  {question}")
        # Show result
        logs = sorted(glob.glob(f"{query_dir}/logs/data_agent/*/final_agent.json"), reverse=True)
        if logs:
            d = json.load(open(logs[0]))
            answer = d.get("final_result", "") or "EMPTY"
            terminate = d.get("terminate_reason", "")
            calls = d.get("llm_call_count", 0)
            print(f"ANSWER: {answer[:120]}")
            print(f"TERMINATE: {terminate} | LLM CALLS: {calls}")
            # Validate
            validate_path = os.path.join(query_dir, "validate.py")
            if os.path.exists(validate_path):
                sys.path.insert(0, DAB_PATH)
                ns = {}
                exec(open(validate_path).read(), ns)
                v = ns["validate"](answer)
                status = "✅ PASS" if v[0] else "❌ FAIL"
                print(f"RESULT: {status} | {v[1]}")
        print(f"{'='*60}\n")
except Exception:
    pass

sys.exit(result.returncode)
