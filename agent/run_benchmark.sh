#!/bin/bash
# Oracle Forge — Automated Benchmark Runner
# Usage: bash ~/oracle-forge/agent/run_benchmark.sh --trials 1 --model google/gemini-3.1-pro-preview --iterations 15

DAB_PATH="${HOME}/DataAgentBench"
ORACLE_PATH="${HOME}/oracle-forge"
SCORE_LOG="${ORACLE_PATH}/eval/score_log.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

TRIALS=1
MODEL="google/gemini-3.1-pro-preview"
ITERATIONS=15

while [[ $# -gt 0 ]]; do
    case $1 in
        --trials) TRIALS="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --iterations) ITERATIONS="$2"; shift 2 ;;
        *) shift ;;
    esac
done

DATASETS="yelp bookreview googlelocal agnews stockmarket stockindex music_brainz_20k DEPS_DEV_V1 GITHUB_REPOS PANCANCER_ATLAS PATENTS crmarenapro"

echo "======================================"
echo "Oracle Forge Benchmark Runner"
echo "Model:      $MODEL"
echo "Trials:     $TRIALS"
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
        for trial in $(seq 1 $TRIALS); do
            python run_agent.py \
                --dataset $dataset \
                --query_id $i \
                --llm "$MODEL" \
                --iterations $ITERATIONS \
                --use_hints \
                --root_name "bench_t${trial}" 2>/dev/null

            latest=$(ls -t ${query_dir}/query${i}/logs/data_agent/ 2>/dev/null | head -1)
            if [ -z "$latest" ]; then
                echo "$dataset Q${i} T${trial}: NO LOG"
                continue
            fi

            output=$(validate_result "$dataset" "$i" "$latest")
            status=$(echo "$output" | head -1)
            answer=$(echo "$output" | tail -1)

            echo "$dataset Q${i} T${trial}: $status | $answer"

            TOTAL_QUERIES=$((TOTAL_QUERIES + 1))
            if [ "$status" = "PASS" ]; then
                TOTAL_PASSED=$((TOTAL_PASSED + 1))
            fi
        done
    done
done

SCORE=$(python3 -c "print(round($TOTAL_PASSED * 100.0 / $TOTAL_QUERIES, 1) if $TOTAL_QUERIES > 0 else 0)")

echo ""
echo "======================================"
echo "FINAL SCORE: $TOTAL_PASSED/$TOTAL_QUERIES = ${SCORE}%"
echo "======================================"

echo "{\"timestamp\": \"$TIMESTAMP\", \"model\": \"$MODEL\", \"trials\": $TRIALS, \"iterations\": $ITERATIONS, \"total\": $TOTAL_QUERIES, \"passed\": $TOTAL_PASSED, \"pass_at_1_pct\": $SCORE}" >> "$SCORE_LOG"
echo "Score logged to $SCORE_LOG"
