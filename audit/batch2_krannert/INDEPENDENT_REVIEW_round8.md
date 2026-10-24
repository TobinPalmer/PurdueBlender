# Krannert Building — independent full-building review, round 8

**Grade: 7.8/10 — below the 8/10 completion threshold.** This review assesses the current saved R4 model together with the R8 footprint/orthophoto and R7 height evidence. R8 added evidence only; it did not change the blend geometry, materials, or placement.

The six criteria are scored out of 2 each (12 raw points total); the evaluator normalizes the total to 10.

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 1.8/2 |
| Placement, orientation, and scale | 1.8/2 |
| Height, floors, and roof | 1.5/2 |
| Facade, entrances, and distinctive architecture | 1.4/2 |
| Interior, courtyard, and circulation | 1.0/2 |
| Technical portability and evidence | 1.9/2 |
| **Raw points** | **9.4/12 = 7.8/10** |

## Evidence and findings

- **Identity and footprint:** Purdue Campus GIS BuildingShapesZip4 FID 54 is identified as KRAN. The saved roof-deck perimeter follows the GIS ring, and the 41-vertex outline falls over the visible roof in the Indiana GIO 2023 orthophoto without fitting its translation, rotation, or scale. The near-zero vertex residual is expected because the model footprint was built from that GIS feature; it verifies conversion and saved-asset integrity, not as-built wall accuracy. The aerial is a useful independent visual check at screening scale, with shadows, roof overhangs, and export resolution limiting precise wall registration. Evidence: `evidence_round8.json`, `asset_footprint_round8.json`, `krannert_asset_footprint_ortho_overlay_r8.png`; source: [Purdue GIS FeatureServer layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) and [Indiana GIO 2023 imagery service](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer).
- **Placement, orientation, and scale:** The coordinator's read-only master check records `Placement_krannert_building` at `(234.5345001, -412.7189941, 0)`, zero rotation, unit scale, and a 0.0000153 m XY difference from the manifest. The library path and marker registration are sound. The unadjusted orthophoto overlay supports broad campus orientation/location, but the project conversion is approximate and no survey control independently establishes the shell's true position or scale. Evidence: `coordinator_placement_review_20261024.json` and `evidence_round8.json`.
- **Height, floors, and roof:** The 2018 Indiana 3DEP DSM compared with 22 interpolated bare-earth DEM queries gives an indicative median surface difference of about 106.46 ft, p25 about 91.62 ft, p90 about 106.69 ft, and maximum about 107.66 ft. This is broadly consistent with modeled lower stepped surfaces, the 104.3 ft roof deck, and 108 ft parapet. GIS F01–F07 values reproduce modeled floor datums only under an inferred feet/common-datum interpretation. The layer gives no units or vertical field definitions; the DSM does not verify floor labels or the modeled 117 ft penthouse. Roof/level semantics remain uncertain. Evidence: `roof_height_assessment_r7.json`, `evidence_round7.json`, and the R8 summary in `evidence_round8.json`.
- **Facade, entrances, and distinctive architecture:** The October 1965 *Indiana Architect* photo documents a flat roof edge, broad light piers, narrow vertical glazing, and a recessed darker ground level. The model captures the overall mass and a repeated window/pier rhythm, and the R4 material pass gives it a warm pale shell, dark glazing, and darker ground band. The model remains schematic: the long right-hand facade's window/spandrel rhythm differs from the narrow vertical bays in the reference, the large black re-entrant slot reads as an open void, and entry dimensions, wall finishes, and exact cadence are not measured. The archival photo is historical and perspective-distorted, not a calibrated elevation. Evidence: `evidence_round5.json`, `krannert_archival_facade_comparison_r5.png`, and the current R4 exterior renders.
- **Interior, courtyard, and circulation:** The Drawing Room and Parrish Library have recognizable furnishings and material treatment, but most floors remain empty or schematic, with no source-registered full-floor circulation. Purdue's emergency maps show broad room/stair/elevator topology from the basement through floor 7, but they are hand-drawn and lack scale, dimensions, issue date, and as-built status, so they do not justify tracing wall locations. Neither those plans nor the aerial resolves the courtyard/re-entrant seam. Evidence: `evidence_round7.json`, `krannert_emergency_maps.pdf`, `drawingroom_r2.png`, and `parrish.png`.
- **Technical portability and evidence:** Blender 5.2.3 reopened the source successfully: 670 export objects / 662 meshes, identity root, 41 saved roof-ring vertices, no missing external images, no material-output issues, and no validator issues. Evidence carefully separates GIS-derived construction alignment from independent visual and LiDAR checks and records remaining uncertainty. Evidence: `validation_round8.json`.

## Evaluator

```python
def evaluate(criteria):
    raw_points = sum(criteria.values())
    return {
        "score": round(raw_points / 12 * 10, 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": "Round 8 evidence and current saved asset reviewed directly",
        "findings": [
            "GIS/orthophoto alignment supports a broad footprint check, not surveyed wall registration",
            "DSM supports main roof surfaces but not floor names or the 117 ft penthouse",
            "Facade remains schematic and most interior floors/courtyard circulation are unresolved",
        ],
    }

result = evaluate({
    "identity_footprint": 1.8,
    "placement_orientation_scale": 1.8,
    "height_floors_roof": 1.5,
    "facade_entrances": 1.4,
    "interior_courtyard_circulation": 1.0,
    "technical_evidence": 1.9,
})
# result: score 7.8, max_score 10, criteria sum 9.4/12
```

**Decision:** Do not mark finished. The R8 orthophoto and R7 LiDAR work materially strengthen position and roof evidence, but the six-category total remains below 8/10 because the facade, roof/penthouse semantics, and most interior/courtyard geometry remain unresolved. The next useful pass should improve source-backed exterior/interior modeling where the emergency maps or other dimensioned plans support it, while keeping roof and courtyard uncertainty explicit. No model or shared files were changed by this review.
