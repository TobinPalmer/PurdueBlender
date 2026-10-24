"""Evaluator entrypoint for the independent Mechanical Engineering R2 review."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'complete_me'

def evaluate():
    scorecard=json.loads((AUDIT/'independent_review_r2_scorecard.json').read_text(encoding='utf-8'))
    validation=json.loads((AUDIT/'mechanical_engineering_r2_validation.json').read_text(encoding='utf-8'))
    if not validation.get('passed') or not validation.get('saved_file_reopened'):
        raise RuntimeError('The reviewed saved asset did not pass reopen validation')
    computed=sum(item['score'] for item in scorecard['criteria'])
    maximum=sum(item['max_score'] for item in scorecard['criteria'])
    if abs(computed-scorecard['score'])>1e-8 or abs(maximum-scorecard['max_score'])>1e-8:
        raise RuntimeError('Scorecard total does not match criterion totals')
    scorecard['evaluator_checks']={
        'saved_asset_reopened_and_validated':True,
        'criterion_total_matches_score':computed,
        'criterion_maximum_matches_max_score':maximum,
        'passed':computed>=scorecard['acceptance_target']}
    return scorecard

if __name__=='__main__':
    result=evaluate()
    print(json.dumps(result,indent=2))
