"""Evaluator helper for the independent Math Sciences R12 review."""
import json
from pathlib import Path


def evaluate(scorecard_path: Path) -> dict:
    """Load rubric scores, validate each category, and return a normalized result."""
    data = json.loads(Path(scorecard_path).read_text(encoding="utf-8"))
    criteria = data["criteria"]
    expected = {
        "identity_and_source_backed_footprint",
        "position_orientation_and_scale",
        "evidence_backed_height_floors_and_roof",
        "facade_entrances_and_distinctive_architecture",
        "modular_export_portability_and_complete_evidence",
    }
    if set(criteria) != expected:
        raise ValueError("Scorecard must contain exactly the five AGENT.md criteria")
    for name, row in criteria.items():
        if row["max_score"] != 2.0 or not (0.0 <= row["score"] <= 2.0):
            raise ValueError(f"Invalid score for {name}")
    score = round(sum(row["score"] for row in criteria.values()), 1)
    if score != data["score"]:
        raise ValueError(f"Recorded score {data['score']} does not equal category sum {score}")
    return {
        "score": score,
        "max_score": 10.0,
        "criteria": criteria,
        "evidence": data["evidence"],
        "findings": data["findings"],
    }


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    print(json.dumps(evaluate(here / "independent_review_round12_scorecard.json"), indent=2))
