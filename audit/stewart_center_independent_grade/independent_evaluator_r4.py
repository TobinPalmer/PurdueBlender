"""Criterion sum for the independent Stewart Center R4 review."""

CRITERIA = {
    "identity_and_GIS_footprint": 1.8,
    "placement_scale_and_interior_layout": 1.5,
    "floors_height_and_roof": 1.0,
    "facade_entrance_and_identity": 1.8,
    "modular_integrity_and_evidence": 1.9,
}


def score(criteria=CRITERIA):
    return round(sum(criteria.values()), 1)


if __name__ == "__main__":
    print(f"{score():.1f}/10")
