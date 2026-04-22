#!/bin/bash
# run_submission_local.sh
# Runs all 54 DAB queries 5 times each on local machine
# Output: results/bloom_team_results.json

DAB_PATH=/home/shuaib/Desktop/python/10Acd/oracle-forge/DataAgentBench
ORACLE_PATH=/home/shuaib/Desktop/python/10Acd/oracle-forge
RESULTS_FILE=$ORACLE_PATH/results/bloom_team_results.json

cd $DAB_PATH && source .venv/bin/activate

# Load env
export $(grep -v '^#' $DAB_PATH/.env | xargs)

LLM='google/gemini-3.1-pro-preview'
ITER=20

echo '[]' > $RESULTS_FILE
echo "Starting 270-run submission job..."

run_query() {
  local dataset=$1
  local q=$2
  local run=$3

  python3 -c "
import subprocess, sys, os
from dotenv import load_dotenv
load_dotenv()
DAB_PATH = '$DAB_PATH'
AGENT_DIR = '$ORACLE_PATH/agent'
env = os.environ.copy()
env['PYTHONPATH'] = f'{AGENT_DIR}:{DAB_PATH}'
env['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', '')
bootstrap = f'''
import sys, os
sys.path.insert(0, \"{AGENT_DIR}\")
sys.path.insert(0, \"{DAB_PATH}\")
import kb_injector
os.chdir(\"{DAB_PATH}\")
__file__ = \"{DAB_PATH}/run_agent.py\"
exec(open(\"{DAB_PATH}/run_agent.py\").read())
'''
subprocess.run([sys.executable, '-c', bootstrap,
    '--dataset', '$dataset', '--query_id', '$q',
    '--llm', '$LLM', '--iterations', '$ITER',
    '--use_hints', '--root_name', 'sub_run${run}'],
    env=env, cwd=DAB_PATH)
" 2>/dev/null

  # Read answer from latest log
  log_dir=$DAB_PATH/query_${dataset}/query${q}/logs/data_agent
  latest=$(ls $log_dir 2>/dev/null | sort | tail -1)
  if [ -n "$latest" ]; then
    answer=$(python3 -c "
import json
d = json.load(open('$log_dir/$latest/final_agent.json'))
print(d.get('final_result','') or '')
" 2>/dev/null)
  else
    answer=""
  fi

  # Append to results
  python3 -c "
import json
from pathlib import Path
f = Path('$RESULTS_FILE')
results = json.loads(f.read_text())
results.append({'dataset': '$dataset', 'query': '$q', 'run': '$run', 'answer': '''$answer'''})
f.write_text(json.dumps(results, indent=2))
" 2>/dev/null

  echo "  $dataset Q$q run $run done — answer: $(echo $answer | head -c 60)"
}

declare -A QUERIES=(
  [yelp]='1 2 3 4 5 6 7'
  [bookreview]='1 2 3'
  [agnews]='1 2 3 4'
  [googlelocal]='1 2 3 4'
  [stockmarket]='1 2 3 4 5'
  [stockindex]='1 2 3'
  [DEPS_DEV_V1]='1 2'
  [GITHUB_REPOS]='1 2 3 4'
  [music_brainz_20k]='1 2 3'
  [PANCANCER_ATLAS]='1 2 3'
  [PATENTS]='1 2 3'
  [crmarenapro]='1 2 3 4 5 6 7 8 9 10 11 12 13'
)

for dataset in yelp bookreview agnews googlelocal stockmarket stockindex \
               DEPS_DEV_V1 GITHUB_REPOS music_brainz_20k \
               PANCANCER_ATLAS PATENTS crmarenapro; do
  echo ""
  echo "========================================"
  echo "Dataset: $dataset"
  echo "========================================"
  for q in ${QUERIES[$dataset]}; do
    for run in 0 1 2 3 4; do
      run_query $dataset $q $run
    done
  done
done

total=$(python3 -c "import json; print(len(json.load(open('$RESULTS_FILE'))))")
echo ""
echo "========================================"
echo "DONE: $total entries in $RESULTS_FILE"
echo "Expected: 270"
echo "========================================"
