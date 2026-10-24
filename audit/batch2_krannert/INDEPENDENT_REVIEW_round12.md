# Krannert Building — independent full-building review, round 12

**Grade: 8.0/10 — passes the 8/10 threshold.** I reviewed the saved R12 source asset, the R12 exterior renders against the historical/current facade images, and the existing GIS/orthophoto, placement, vertical, and interior evidence. The continuous narrow glazing treatment now appears across the principal visible long facades and produces a substantially closer pier-and-slot rhythm in the saved renders. The pass is narrow: most floor interiors remain schematic and the courtyard/re-entrant seam and penthouse height are still unresolved.

Each criterion is scored out of 2 (12 raw points total), then normalized to 10.

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 1.8/2 |
| Placement, orientation, and scale | 1.8/2 |
| Height, floors, and roof | 1.5/2 |
| Facade, entrances, and distinctive architecture | 1.6/2 |
| Interior, courtyard, and circulation | 1.0/2 |
| Technical portability and evidence | 1.9/2 |
| **Raw points** | **9.6/12 = 8.0/10** |

## Evidence and findings

- **Identity and footprint — 1.8/2:** The current model presents Krannert's multi-wing office mass, broad pale piers, dark vertical glazing, recessed/darker lower story, flat roof profile, and re-entrant form. Purdue Campus GIS BuildingShapesZip4 feature FID 54 identifies the building as KRAN. The saved roof-deck boundary overlay tracks the visible footprint in the Indiana GIO 2023 orthophoto without fitting a translation, rotation, or scale. The model boundary and GIS ring are both derived from the same feature, so their tiny vertex-conversion residual verifies conversion/saved-data integrity, not measured wall accuracy. The aerial is the independent check, at broad visual scale only; roof overhang/shadow, export resolution, and approximate map projection limit precision. Evidence: `evidence_round12.json`, `asset_footprint_round8.json`, `krannert_asset_footprint_ortho_overlay_r8.png`, and `krannert_gis_fid54_4326.json`; sources: [Purdue Campus GIS BuildingShapesZip4](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) and [Indiana GIO 2023 imagery](https://di-ingov.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer).
- **Placement, orientation, and scale — 1.8/2:** The coordinator's read-only master review records `Placement_krannert_building` at `(234.5345001, -412.7189941, 0)`, zero rotation, unit scale, and a 0.0000153 m XY difference from the manifest. The source asset uses an identity local root, and the unadjusted footprint overlay supports broad site placement and orientation. These checks confirm registration values and visual site correspondence, not surveyed wall position/scale; the campus-local projection is approximate. R12 did not alter placement. Evidence: `coordinator_placement_review_20261024.json`, `evidence_round12.json`, and `asset_footprint_round8.json`.
- **Height, floors, and roof — 1.5/2:** R12 validation confirms the saved roof deck and extracted 41-vertex roof ring; the deck top is 31.791 m in asset-local coordinates. Indiana 2018 3DEP DSM samples versus interpolated bare-earth DEM give median surface difference about 106.46 ft, p25 91.61 ft, p90 106.69 ft, and maximum 107.66 ft. This broadly supports stepped roof surfaces near modeled L7, roof deck, and parapet levels. DSM sampling does not establish story labels or verify the 117 ft penthouse/elevator overrun. GIS floor and roof fields have undocumented units/semantics, and the DSM cell size can miss narrow rooftop structures. No roof/floor geometry changed in R12. Evidence: `validation_round12.json`, `roof_height_assessment_r7.json`, and `evidence_round7.json`.
- **Facade, entrances, and distinctive architecture — 1.6/2:** In the R12 saved renders, the principal long elevations now show repeated slim dark vertical openings separated by broad light piers, with fine floor-level breaks. This visibly improves the match to the October 1965 *Indiana Architect* p.32 image and the Purdue exterior photo, which both show narrow tall glazing, broad pale piers, fine transverse divisions, dark lower-level treatment, and a flat roof edge. The R12 comparison makes this correspondence inspectable, and the close north-wing view confirms that glazing is continuous between the modeled slab edges on the changed elevations. Remaining limitations: short returns/entrance faces retain the earlier per-floor window treatment, bay widths are estimated from perspective photos, the large dark re-entrant slot is unresolved, and canopy/entry detailing is modest. The reference photos are not calibrated elevations and do not prove dimensions or hidden/current facade condition. Evidence: `facade_round12_update.json`, `krannert_south_front_r12.png`, `krannert_southeast_same_corner_r12.png`, `krannert_southwest_same_corner_r12.png`, `krannert_north_long_wing_r12.png`, and `krannert_archival_facade_comparison_r12.png`; sources: [Indiana Architect, October 1965, p. 32](https://usmodernist.org/AIAIN/AIAIN-1965-10.pdf) and [Purdue Events exterior image](https://events.purdue.edu/krannert_building).
- **Interior, courtyard, and circulation — 1.0/2:** The Drawing Room and Parrish Library are identifiable furnished rooms with plausible material/furniture detail, visible in `drawingroom_r2.png` and `parrish_r2.png`. Most other floors remain empty or schematic; full-floor room placement, circulation, and the exact courtyard/re-entrant seam have not been established. Purdue emergency maps give room/stair/elevator adjacency but no scale, dimensions, date, or as-built status; the 2010 second-floor furniture plan is marked “not to scale”; tour photographs do not register rooms in plan. These sources do not support dimensionally accurate new partitions. Evidence: `evidence_round12.json`, `krannert_emergency_maps.pdf`, `krannert_mel_2f_furniture_plan_2010.pdf`, `drawingroom_r2.png`, and `parrish_r2.png`.
- **Technical portability and evidence — 1.9/2:** Blender 5.2.3 reopened the saved R12 asset. Validation reports 670 export objects / 662 meshes, identity root, 41 saved roof-ring vertices, all revised facade meshes present, no missing external images, no material-output issues, and no validator issues. R12 provides fresh saved-source renders from the front, oblique corners, and long-wing detail, plus a direct qualitative photo comparison. The evidence states that window dimensions are visual estimates and keeps unresolved faces, courtyard geometry, and roof semantics explicit. These are strong technical and auditability checks; they are not a substitute for measured as-built evidence. Evidence: `validation_round12.json`, `facade_round12_update.json`, and `evidence_round12.json`.

## Evaluator

```python
def evaluate(criteria):
    raw_points = sum(criteria.values())
    score = round(raw_points / 12 * 10, 1)
    return {
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "findings": [
            "R12's principal long facades now read with tall narrow glazing, broad piers, and fine floor breaks consistent with the photographic references",
            "GIS-derived outline plus no-fit orthophoto and coordinator marker support broad footprint/registration, not surveyed wall accuracy",
            "LiDAR supports main roof heights but cannot verify named floor datums or the penthouse",
            "two furnished rooms are supported; most floor layouts, circulation, and courtyard seam remain unresolved",
        ],
    }

result = evaluate({
    "identity_footprint": 1.8,
    "placement_orientation_scale": 1.8,
    "height_floors_roof": 1.5,
    "facade_entrances": 1.6,
    "interior_courtyard_circulation": 1.0,
    "technical_evidence": 1.9,
})
# result: score 8.0, max_score 10, criteria sum 9.6/12, passed True
```

**Decision: Pass (8.0/10).** The pass is marginal and reflects the R12 facade correction plus strong footprint/placement and technical evidence. Remaining uncertainties should stay visible in the project record: most interior/courtyard layout, hidden elevations, precise facade dimensions, and penthouse/roof-height semantics. No changes were made to the model, builder, master, manifest, README, shared indexes, or other buildings during this review.
