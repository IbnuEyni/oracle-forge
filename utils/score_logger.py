"""
score_logger.py — Append a structured pass@1 result entry to eval/score_log.jsonl.

Usage:
    from utils.score_logger import log_score
    log_score(dataset='yelp', llm='google/gemini-3.1-pro-preview',
              results=[{'query_id': 1, 'passed': True, 'answer': '3.55'}],
              notes='OpenRouter run with KB injection')
"""
import json
from datetime import datetime, timezone
from pathlib import Path

SCORE_LOG = Path(__file__).parent.parent / 'eval' / 'score_log.jsonl'


def log_score(
    dataset: str,
    llm: str,
    results: list[dict],
    notes: str = ''
) -> dict:
    """
    Build a score entry and append it to eval/score_log.jsonl.

    Each result dict must have: query_id (int), passed (bool), answer (str).
    Optional fields: reason, terminate_reason, llm_calls.

    Returns the entry that was written.

    Example:
        log_score(
            dataset='yelp',
            llm='google/gemini-3.1-pro-preview',
            results=[
                {'query_id': 1, 'passed': True,  'answer': '3.55'},
                {'query_id': 2, 'passed': False, 'answer': 'PA', 'reason': 'Wrong state'},
            ],
            notes='Run with --use_hints and KB injection'
        )
    """
    passed = sum(1 for r in results if r.get('passed'))
    total = len(results)
    score = round(passed / total * 100, 1) if total else 0.0

    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'dataset': dataset,
        'llm': llm,
        'total': total,
        'passed': passed,
        'pass_at_1_pct': score,
        'results': results,
    }
    if notes:
        entry['notes'] = notes

    with open(SCORE_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')

    print(f'[score_logger] {passed}/{total} = {score}% logged to {SCORE_LOG}')
    return entry


if __name__ == '__main__':
    import tempfile
    tmp = Path(tempfile.mktemp(suffix='.jsonl'))
    # Temporarily override SCORE_LOG for test
    import sys
    _mod = sys.modules[__name__]
    _original = _mod.SCORE_LOG
    _mod.SCORE_LOG = tmp
    entry = log_score('test', 'test-model', [
        {'query_id': 1, 'passed': True,  'answer': '42'},
        {'query_id': 2, 'passed': False, 'answer': ''},
    ])
    assert entry['passed'] == 1
    assert entry['pass_at_1_pct'] == 50.0
    assert tmp.exists()
    tmp.unlink()
    _mod.SCORE_LOG = _original
    print('score_logger: PASS')
