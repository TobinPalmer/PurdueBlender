"""Weighted 10-point evaluator for an independent Duhme review.

Create review_input.json after direct inspection of the final saved asset and source evidence,
then run `python evaluator.py`. Each category must contain a score from 0 to 2,
evidence, and findings. This helper aggregates scores but does not invent visual evidence.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
CATEGORIES = (
    ("identity_and_footprint", "Correct identity and source-backed footprint"),
    ("position_orientation_dimensions", "Position, orientation, and scale/dimensions"),
    ("height_floors_roof", "Evidence-backed height, floors, and roof form"),
    ("facade_and_distinctive_architecture", "Facade, entrances, and distinctive architecture"),
    ("modular_export_and_evidence", "Modular export, portability, and complete evidence"),
)


def evaluate(review):
    criteria = []
    for key, label in CATEGORIES:
        item = review["criteria"][key]
        score = float(item["score"])
        if score < 0 or score > 2:
            raise ValueError(f"{key} score must be from 0 to 2")
        if not item.get("evidence"):
            raise ValueError(f"{key} needs direct evidence")
        criteria.append({"criterion": label, "score": score, "max_score": 2,
                         "evidence": item["evidence"], "findings": item.get("findings", [])})
    total = round(sum(item["score"] for item in criteria), 2)
    return {"score": total, "max_score": 10, "criteria": criteria,
            "evidence": review.get("evidence", []),
            "findings": [finding for item in criteria for finding in item["findings"]],
            "pass": total >= 8}


def main():
    source = ROOT / "review_input.json"
    review = json.loads(source.read_text(encoding="utf-8"))
    result = evaluate(review)
    (ROOT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
