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
exec(open('{DAB_PATH}/run_agent.py').read())
"""

result = subprocess.run(
    [sys.executable, "-c", bootstrap] + sys.argv[1:],
    env=env,
    cwd=DAB_PATH
)
sys.exit(result.returncode)
