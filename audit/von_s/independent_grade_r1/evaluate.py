"""Independent Von's grading result for the frozen asset SHA in result.json."""
import json
from pathlib import Path

RESULT = Path(__file__).with_name("result.json")


def evaluate():
    """Return score, criteria, evidence, and findings for this exact revision."""
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if sum(c["score"] for c in result["criteria"]) != result["score"]:
        raise ValueError("Criterion sum does not match the reported score")
    return {
        "score": result["score"],
        "max_score": result["max_score"],
        "criteria": result["criteria"],
        "evidence": result["evidence"],
        "findings": result["findings"],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
