# Krannert Building — independent full-building review, round 9

**Grade: 7.9/10 — below the 8/10 completion threshold.** I independently assessed the saved R9 source asset at `modular/buildings/krannert_building.blend`, its R9 validation and evidence package, and the available footprint, placement, roof-height, and interior evidence. The R9 edit materially improves the pier-and-glazing rhythm on the documented facade, but does not change the rest of the building, so the full-building grade remains just below threshold.

The six criteria below are scored out of 2 (12 raw points total), then normalized to 10. The threshold is 8/10.

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 1.8/2 |
| Placement, orientation, and scale | 1.8/2 |
| Height, floors, and roof | 1.5/2 |
| Facade, entrances, and distinctive architecture | 1.5/2 |
| Interior, courtyard, and circulation | 1.0/2 |
| Technical portability and evidence | 1.9/2 |
| **Raw points** | **9.5/12 = 7.9/10** |

## Evidence and findings

- **Identity and footprint — 1.8/2:** Purdue Campus GIS BuildingShapesZip4 FeatureServer feature FID 54 identifies KRAN. The reopened R8 source-asset roof outline overlays the Indiana GIO 2023 orthophoto without fitting translation, rotation, or scale and broadly follows the visible roof/building outline. The R8 asset footprint comparison reports sub-millimeter ring conversion residuals, but the roof ring was itself derived from this GIS feature; those residuals test conversion and saved-asset integrity, not independent measured wall accuracy. The orthophoto is an independent visual check, limited by shadows, overhangs and raster resolution. R9 did not change the footprint. Evidence: `evidence_round9.json`, `asset_footprint_round8.json`, and `krannert_asset_footprint_ortho_overlay_r8.png`; source: [Purdue Campus GIS BuildingShapesZip4](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) and [Indiana GIO 2023 imagery](https://di-ingov.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer).
- **Placement, orientation, and scale — 1.8/2:** The read-only coordinator review records `Placement_krannert_building` at `(234.5345001, -412.7189941, 0)`, zero rotation, unit scale, and only 0.0000153 m XY delta from the project manifest. The linked source library resolves and the footprint overlay supports broad orientation and campus position. The approximate campus-local coordinate conversion and lack of independent survey control prevent a stronger claim of surveyed position/scale. This R9 pass did not alter placement. Evidence: `coordinator_placement_review_20261024.json`, `evidence_round9.json`, and `asset_footprint_round8.json`.
- **Height, floors, and roof — 1.5/2:** The source validation finds the saved roof deck at 31.791 m in the asset-local coordinate frame, while the earlier R7 comparison of the 2018 3DEP DSM and interpolated bare-earth DEM estimates a median surface difference of about 106.46 ft, p25 91.61 ft, p90 106.69 ft, and maximum 107.66 ft. This is broadly compatible with stepped roof levels near the modeled seventh-floor/roof deck and parapet. DSM sampling and undocumented GIS vertical field semantics do not establish story labels or verify the modeled 117 ft penthouse/elevator overrun. R9 leaves roof and floor geometry unchanged. Evidence: `validation_round9.json`, `roof_height_assessment_r7.json`, and `evidence_round7.json`.
- **Facade, entrances, and distinctive architecture — 1.5/2:** R9 is a clear improvement: the saved-source renders now show broad pale vertical piers at bay boundaries, narrower dark glazing, reduced opaque spandrels, fine horizontal transom lines, and the dark ground band. This is qualitatively closer to the October 1965 *Indiana Architect* p.32 photograph and Purdue's current exterior image; the archival comparison is included at `krannert_archival_facade_comparison_r9.png`. The model still uses repeated individual rectangular windows, and especially on the long right wing the openings read as compact floor-by-floor rectangles rather than the source's much taller, slender vertical glazing cadence. The 1965 image is perspective-distorted and does not fix dimensions or current condition. The canopy is simple and the entrance details are not source-registered. The large dark re-entrant slot remains visually unresolved. Evidence: `facade_round9_update.json`, `krannert_south_front_r9.png`, `krannert_southeast_same_corner_r9.png`, `krannert_southwest_same_corner_r9.png`, and `krannert_archival_facade_comparison_r9.png`.
- **Interior, courtyard, and circulation — 1.0/2:** R9 explicitly leaves interior partitions, circulation, furniture, courtyard, and re-entrant seam untouched. The Drawing Room and Parrish Library interiors are recognizable furnished spaces, but most floors remain empty or schematic. Purdue emergency maps cover basement, ground, and floors 1–7 and support only diagrammatic room/corridor/stair/elevator adjacency; they have no scale, dimensions, issue date, or as-built status. The 2010 second-floor furniture plan is marked not to scale. No reliable source presently resolves the model's courtyard/re-entrant geometry or lets room layouts be registered dimensionally. Evidence: `evidence_round9.json`, `krannert_emergency_maps.pdf`, `krannert_mel_2f_furniture_plan_2010.pdf`, `drawingroom_r2.png`, and `parrish.png`.
- **Technical portability and evidence — 1.9/2:** Blender 5.2.3 reopened the R9 saved asset successfully. Validation reports 670 export objects / 662 meshes, identity source root, 41 saved roof-ring vertices, all four updated facade meshes present, no missing external images, no material output issues, and no validator issues. Fresh saved-source exterior renders and a source comparison are present. Evidence distinguishes GIS-derived coordinates from independent orthophoto checks and records architectural uncertainty. This is a strong reproducibility package, though it validates technical reopening and evidence quality rather than architectural completeness. Evidence: `validation_round9.json`, `facade_round9_update.json`, and `evidence_round9.json`.

## Evaluator

```python
def evaluate(criteria):
    raw_points = sum(criteria.values())
    return {
        "score": round(raw_points / 12 * 10, 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": "R9 saved-source renders and evidence reviewed; unchanged full-building evidence checked",
        "findings": [
            "R9 improves the broad-pier / narrow-glazing expression but the long facade remains more repetitive and squat-windowed than the archival reference",
            "GIS footprint and master marker support broad registration, not surveyed as-built wall accuracy",
            "DSM supports the main stepped roof range but not floor semantics or the modeled penthouse",
            "most interior floors and the courtyard/re-entrant circulation remain unresolved",
        ],
    }

result = evaluate({
    "identity_footprint": 1.8,
    "placement_orientation_scale": 1.8,
    "height_floors_roof": 1.5,
    "facade_entrances": 1.5,
    "interior_courtyard_circulation": 1.0,
    "technical_evidence": 1.9,
})
# result: score 7.9, max_score 10, criteria sum 9.5/12
```

**Decision: Fail (7.9/10; pass threshold 8/10).** The R9 facade correction is source-supported and improves the visible proportions, but does not resolve the remaining facade cadence/entrance details, roof and penthouse uncertainty, or limited interior/courtyard modeling. No changes were made to the asset, builder, master, shared indexes, README, or any other building file during this review.
