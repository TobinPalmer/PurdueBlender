# Mackey Arena — independent full-building review, round 1

**Grade: 7.3/10 — below the 8/10 completion threshold.** I reviewed the saved source asset `modular/buildings/mackey_arena.blend`, the R1 north-wing update record, the saved-asset renders, the GIS feature snapshot, the asset manifest entry, and the reopen-validation script. This is a meaningful detailed model with a clear recent addition, but its composite footprint and inferred wing split/height, limited independent site verification, and incomplete whole-complex representation keep it below the completion threshold.

Each rubric criterion is scored out of 2 (12 raw points total) and normalized to 10.

| Criterion | Score |
| --- | ---: |
| Identity and footprint | 1.5/2 |
| Campus placement, orientation, and scale | 1.5/2 |
| Height, floors, and roof | 1.4/2 |
| Facade, entrances, and distinctive architecture | 1.4/2 |
| Interior and circulation | 1.2/2 |
| Technical portability and evidence | 1.7/2 |
| **Raw points** | **8.7/12 = 7.3/10** |

## Evidence and findings

- **Identity and footprint — 1.5/2:** The saved render shows a recognizable circular Mackey Arena with stepped dome, radial exterior supports, and an attached north-side rectangular multi-level wing. The GIS source snapshot identifies feature FID 873 as Guy J. Mackey Arena (MACK), and the north addition is supported as the Student-Athlete Development Center (SDAC) by Purdue Athletics and DLZ project descriptions. However, FID 873 is a composite arena-and-additions polygon: it does not independently distinguish the SDAC from the arena shell, plaza/connector, or separate one-story additions. The builder clips the whole polygon north of project Y=735 m, then treats that lobe as one three-level SDAC. That is a documented modeling assumption, not a surveyed sub-footprint. The other reported one-story additions remain unmodeled. Evidence: `REVIEW.md`, `mackey_footprint_source.json`, `after_oblique.png`, and `after_top.png`; references: [Purdue Athletics Mackey Arena](https://purduesports.com/facilities/mackey-arena), [DLZ Mackey Arena expansion](https://dlz.com/projects/purdue-university-mackey-arena-expansion/), [Purdue BuildingShapesZip4 GIS service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0).
- **Campus placement, orientation, and scale — 1.5/2:** The base asset is in local coordinates and the manifest records a campus placement origin of `(-209.5900, 671.8375)` m. The wing builder subtracts that same origin from the GIS-derived coordinates, preserving the asset frame and placing the addition north of the existing arena. This supports internal coordinate consistency. The conversion is an approximate campus-local lon/lat projection, and the package has no unadjusted orthophoto overlay or independent surveyed control for the source-shell-to-GIS fit. The composite GIS polygon also cannot validate the precise split/connection geometry. Thus placement is plausible and consistently transformed, but not independently confirmed at site accuracy. Evidence: `modular/manifest.json`, `build_mackey_arena_north_wing.py`, `REVIEW.md`, and `mackey_footprint_source.json`.
- **Height, floors, and roof — 1.4/2:** The existing arena's modeled maximum is 27.9 m per the manifest and the saved renders show the recognizable stepped dome/cupola silhouette. The new wing is modeled at 14.3 m for three levels, with roof slab and rooftop mechanical housings. Purdue Athletics' facility description supports a multi-level development center; the GIS feature reports `NUM_LEVELS=3` and `Extrution=47`, but the GIS schema provides no units or documented vertical semantics. Interpreting 47 as feet is plausible but unverified, so the wing height and level datums remain estimates. No independent elevation model or measured roof/section comparison is supplied. Evidence: `REVIEW.md`, `mackey_footprint_source.json`, `modular/manifest.json`, and `build_mackey_arena_north_wing.py`.
- **Facade, entrances, and distinctive architecture — 1.4/2:** The arena mass has a strong identity in the dome, radial buttress rhythm, dark glazed concourse band, brick base, north pavilion, canopy, and signage. The new wing adds a three-level brick/stone/glass composition with repeated bays, mullions, and a canopy connector. The oblique render confirms that those pieces are present and visually coherent at massing distance. Surface texture and detail remain schematic: the broad wing roof reads as a largely unarticulated pale slab in the supplied render; window bays and facade joints are repetitive; entrance/connector form is not checked against a registered current photograph. Source references are cited, but the audit package has no direct before/after photo comparison of the SDAC facade. Evidence: `after_oblique.png`, `after_top.png`, `REVIEW.md`, and the source descriptions linked there.
- **Interior and circulation — 1.2/2:** The base asset records a detailed basketball court and seating bowls, and the new wing adds a full-size practice court, line markings, and backboards. These are meaningful interior features and match the official published program at a broad level. The R1 evidence includes no interior render or reopened-asset view demonstrating the practice court's fit within the wing, sightlines, access, or court orientation. Exact room layouts, breakout shooting spaces, floor-to-floor access, and connections between the wing and arena are not source-registered. The practice court is explicitly positioned from estimated coordinates, and the review acknowledges that orientation and internal room layout are undocumented. Evidence: `REVIEW.md`, `build_mackey_arena_north_wing.py`, and `modular/manifest.json`.
- **Technical portability and evidence — 1.7/2:** The update report says Blender reopened the saved file and found 387 collection objects, including 14 new SDAC objects parented to `AssetRoot_mackey_arena`, with no linked external libraries. The builder saves only the standalone asset and uses batched named geometry and local coordinates. The saved oblique and top renders provide visual evidence. The validation script is present, but its captured JSON/stdout is not included, and no render of the interior court or direct geospatial overlay is provided. The report also clearly describes the composite GIS and height limitations, which improves auditability. Evidence: `REVIEW.md`, `validate_after_reopen.py`, `render_after_oblique.py`, `after_oblique.png`, and `after_top.png`.

## Evaluator

```python
def evaluate(criteria):
    raw_points = sum(criteria.values())
    return {
        "score": round(raw_points / 12 * 10, 1),
        "max_score": 10,
        "pass_threshold": 8,
        "passed": raw_points / 12 * 10 >= 8,
        "criteria": criteria,
        "findings": [
            "FID 873 is a composite arena/additions envelope; the north-of-Y=735 m SDAC split is an informed but unverified interpretation",
            "the project-local coordinate conversion preserves frame consistency but no independent orthophoto/survey check is supplied",
            "three levels and 14.3 m height are plausible but vertical field units and semantics are undocumented",
            "arena and practice courts are represented, but whole-complex circulation and wing interior layout are unverified",
        ],
    }

result = evaluate({
    "identity_footprint": 1.5,
    "placement_orientation_scale": 1.5,
    "height_floors_roof": 1.4,
    "facade_entrances": 1.4,
    "interior_circulation": 1.2,
    "technical_evidence": 1.7,
})
# result: score 7.3, max_score 10, criteria sum 8.7/12, passed False
```

**Decision: Fail (7.3/10).** The current file is a convincing recognizable arena mass with a useful new SDAC wing, but the composite footprint does not validate the split or the unmodeled perimeter additions, site registration and heights lack independent checks, and the interior/connection evidence is incomplete. No model, builder, manifest, master file, README, shared index, or other building was edited for this review.
