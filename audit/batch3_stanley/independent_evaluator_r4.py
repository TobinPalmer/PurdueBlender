"""Reproducible criterion-weight sum for independent Stanley Coulter Hall R4 review."""

CATEGORIES = {
    "identity_and_full_gis_footprint": (1.9, 2.0),
    "placement_orientation_and_asset_scale": (1.6, 2.0),
    "floors_height_and_roof_form": (1.2, 2.0),
    "facade_entrance_and_materials": (1.25, 2.0),
    "saved_asset_interior_evidence_and_portability": (1.65, 2.0),
}
PASS_THRESHOLD = 8.0


def evaluate(scores=CATEGORIES):
    total = sum(score for score, _maximum in scores.values())
    maximum = sum(maximum for _score, maximum in scores.values())
    return {
        "score": round(total * 10.0 / maximum, 2),
        "max_score": 10.0,
        "passed": total * 10.0 / maximum >= PASS_THRESHOLD,
        "pass_threshold": PASS_THRESHOLD,
    }


if __name__ == "__main__":
    print(evaluate())
