SCORES = {
    "identity_and_gis_footprint_fidelity": 1.8,
    "placement_orientation_scale_and_interior_layout": 1.4,
    "floors_height_and_roof_form": 1.0,
    "facade_entrances_and_distinctive_identity": 1.7,
    "modular_integrity_portability_and_evidence": 1.8,
}

TOTAL = round(sum(SCORES.values()), 1)
PASS_THRESHOLD = 8.0

assert TOTAL == 7.7
assert TOTAL < PASS_THRESHOLD
print({"total": TOTAL, "pass_threshold": PASS_THRESHOLD, "passed": TOTAL >= PASS_THRESHOLD})
