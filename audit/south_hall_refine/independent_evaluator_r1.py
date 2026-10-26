"""Transparent R1 South Hall grade aggregation."""

CRITERIA = {
    "Identity, plan footprint, and local frame": (1.9, 2.0),
    "Vertical massing, connector, and roof": (1.5, 2.0),
    "Exterior facade, entrance, and materials": (1.4, 2.0),
    "Interior and amenities": (0.9, 1.5),
    "Source evidence and uncertainty handling": (1.2, 1.5),
    "Saved file, materials, and portability": (0.9, 1.0),
}

score = sum(points for points, _maximum in CRITERIA.values())
maximum = sum(_maximum for _points, _maximum in CRITERIA.values())
assert maximum == 10.0
print({"score": score, "max_score": maximum, "passed": score >= 8.0})
