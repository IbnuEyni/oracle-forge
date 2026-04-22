#!/bin/bash
# run_submission.sh
# Runs all 54 DAB queries 5 times each and collects results in submission format
# Output: results/bloom_team_results.json
# Format: [{dataset, query, run, answer}, ...] — 270 entries total

cd ~/DataAgentBench && source .venv/bin/activate

LLM='google/gemini-3.1-pro-preview'
ITER=20
RESULTS_FILE=~/oracle-forge/results/bloom_team_results.json

# Start fresh results file
echo '[]' > $RESULTS_FILE

declare -A QUERIES=(
  [yelp]='1,2,3,4,5,6,7'
  [bookreview]='1,2,3'
  [agnews]='1,2,3,4'
  [googlelocal]='1,2,3,4'
  [stockmarket]='1,2,3,4,5'
  [stockindex]='1,2,3'
  [DEPS_DEV_V1]='1,2'
  [GITHUB_REPOS]='1,2,3,4'
  [music_brainz_20k]='1,2,3'
  [PANCANCER_ATLAS]='1,2,3'
  [PATENTS]='1,2,3'
  [crmarenapro]='1,2,3,4,5,6,7,8,9,10,11,12,13'
)

for dataset in yelp bookreview agnews googlelocal stockmarket stockindex \
               DEPS_DEV_V1 GITHUB_REPOS music_brainz_20k \
               PANCANCER_ATLAS PATENTS crmarenapro; do

  IFS=',' read -ra query_list <<< "${QUERIES[$dataset]}"

  for q in "${query_list[@]}"; do
    for run in 0 1 2 3 4; do
      echo "Running $dataset Q$q run $run..."

      python3 ~/oracle-forge/agent/oracle_run.py \
        --dataset $dataset \
        --query_id $q \
        --llm $LLM \
        --iterations $ITER \
        --use_hints \
        --root_name "submission_run${run}" 2>/dev/null

      # Read the answer from the latest log
      log_dir=~/DataAgentBench/query_${dataset}/query${q}/logs/data_agent
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

      # Append to results JSON
      python3 << PYEOF
import json
from pathlib import Path

results_file = Path('$RESULTS_FILE')
results = json.loads(results_file.read_text())
results.append({
    "dataset": "$dataset",
    "query": "$q",
    "run": "$run",
    "answer": """$answer"""
})
results_file.write_text(json.dumps(results, indent=2))
PYEOF

      echo "  -> $dataset Q$q run $run done"
    done
  done
done

echo ""
echo "========================================"
total=$(python3 -c "import json; print(len(json.load(open('$RESULTS_FILE'))))")
echo "DONE: $total entries written to $RESULTS_FILE"
echo "Expected: 270 (54 queries x 5 runs)"
echo "========================================"
