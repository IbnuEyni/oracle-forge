#!/bin/bash
# Oracle Forge — KB-Enhanced Datasets Runner
# Run only the 5 datasets that now have knowledge base data

DAB_PATH="${HOME}/DataAgentBench"
ORACLE_PATH="${HOME}/oracle-forge"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

MODEL="google/gemini-3.1-pro-preview"
ITERATIONS=20

# KB-enhanced datasets only
DATASETS="music_brainz_20k DEPS_DEV_V1 GITHUB_REPOS PANCANCER_ATLAS PATENTS"

echo "======================================"
echo "Oracle Forge KB-Enhanced Datasets"
echo "Model:      $MODEL"
echo "Iterations: $ITERATIONS"
echo "Started:    $TIMESTAMP"
echo "======================================"

TOTAL_PASSED=0
TOTAL_QUERIES=0

cd "$DAB_PATH"
source .venv/bin/activate

validate_result() {
    local dataset=$1
    local query_id=$2
    local log_dir=$3
    python3 -c "
import json, sys
sys.path.insert(0, '.')
try:
    d = json.load(open('query_${dataset}/query${query_id}/logs/data_agent/${log_dir}/final_agent.json'))
    r = d.get('final_result', '') or ''
    exec(open('query_${dataset}/query${query_id}/validate.py').read())
    v = validate(r)
    print('PASS' if v[0] else 'FAIL')
    print(r[:60].replace(chr(10),' '))
except Exception as e:
    print('ERROR')
    print(str(e)[:60])
" 2>/dev/null
}

for dataset in $DATASETS; do
    query_dir="query_${dataset}"
    [ ! -d "$query_dir" ] && echo "Skipping $dataset — not found" && continue

    queries=$(ls -d ${query_dir}/query*/ 2>/dev/null | grep -v logs | wc -l)
    [ "$queries" -eq 0 ] && echo "Skipping $dataset — no queries" && continue

    echo ""
    echo "--- $dataset ($queries queries) ---"

    for i in $(seq 1 $queries); do
        python ~/oracle-forge/agent/oracle_run.py \
            --dataset $dataset \
            --query_id $i \
            --llm "$MODEL" \
            --iterations $ITERATIONS \
            --use_hints 2>/dev/null

        latest=$(ls -t ${query_dir}/query${i}/logs/data_agent/ 2>/dev/null | head -1)
        if [ -z "$latest" ]; then
            echo "$dataset Q${i}: NO LOG"
            continue
        fi

        output=$(validate_result "$dataset" "$i" "$latest")
        status=$(echo "$output" | head -1)
        answer=$(echo "$output" | tail -1)

        echo "$dataset Q${i}: $status | $answer"

        TOTAL_QUERIES=$((TOTAL_QUERIES + 1))
        if [ "$status" = "PASS" ]; then
            TOTAL_PASSED=$((TOTAL_PASSED + 1))
        fi
    done
done

SCORE=$(python3 -c "print(round($TOTAL_PASSED * 100.0 / $TOTAL_QUERIES, 1) if $TOTAL_QUERIES > 0 else 0)")

echo ""
echo "======================================"
echo "KB-ENHANCED DATASETS SCORE: $TOTAL_PASSED/$TOTAL_QUERIES = ${SCORE}%"
echo "======================================"

echo "{\"timestamp\": \"$TIMESTAMP\", \"model\": \"$MODEL\", \"iterations\": $ITERATIONS, \"datasets\": \"KB-enhanced\", \"total\": $TOTAL_QUERIES, \"passed\": $TOTAL_PASSED, \"pass_at_1_pct\": $SCORE}" >> "$ORACLE_PATH/eval/score_log.jsonl"
echo "Score logged to $ORACLE_PATH/eval/score_log.jsonl"