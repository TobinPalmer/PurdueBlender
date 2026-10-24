# Mackey Arena — independent full-building review, round 3

**Grade: 8.0/10 — passes the 8/10 threshold narrowly.** I assessed the saved R3 asset and its R3 renders, registration overlay, and Blender reopen validation directly, then checked the source/uncertainty records for GIS segmentation, placement, heights, facades, and interior program. The arena remains recognizable, and R3 adds a more source-grounded SDAC facade/lobby plus visible low-roof additions. The GIS footprint is a composite envelope, so the internal split and some program/height details remain inferred rather than surveyed.

Each criterion is scored out of 2 (12 raw points total), then normalized to 10.

| Criterion | Score |
| --- | ---: |
| Identity and footprint segmentation | 1.7/2 |
| Campus placement, orientation, and scale | 1.7/2 |
| Height, floors, and roof | 1.3/2 |
| Facade, entrances, and distinctive architecture | 1.7/2 |
| Interior and circulation | 1.3/2 |
| Technical portability and evidence | 1.9/2 |
| **Raw points** | **9.6/12 = 8.0/10** |

## Evidence and findings

- **Identity and footprint segmentation — 1.7/2:** The main circular arena and stepped dome are readily recognizable in the saved oblique/top renders. R3 adds the northern SDAC mass and two low-roof perimeter traces. The orthophoto registration overlay shows the arena shell and those roof masses against their visible 2023 roof outlines; the yellow SDAC seam and lime/magenta low-roof traces appear broadly aligned with the aerial. However, Purdue GIS FID 873 is one composite arena/additions envelope; it does not provide separately surveyed polygons for the arena shell, SDAC, or perimeter additions. R3's SDAC and low-roof segmentation is therefore based on visible photo roof seams and project descriptions, not on a measured GIS split. Evidence: `evidence_r3.json`, `R3_source_comparison.md`, `orthophoto_registration_overlay.png`, `north_sdac_registration_detail.png`, and `mackey_footprint_source.json`; sources: [Purdue BuildingShapesZip4 FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), [Purdue Athletics Mackey Arena](https://purduesports.com/facilities/mackey-arena), and [DLZ Mackey Arena expansion](https://dlz.com/projects/purdue-university-mackey-arena-expansion/).
- **Campus placement, orientation, and scale — 1.7/2:** The asset keeps its manifest placement origin `(-209.5900039673, 671.8374938965)` m and local coordinates; R3 generated parts are parented to the existing asset root. The orthophoto overlay uses the exact 2023 export extent and pixel size and shows north orientation, scale bar, composite outline, arena circle, and photo-traced roof seams. This provides a useful visual site-registration check. It is not a survey: the project-local lon/lat conversion is approximate, the overlay is a visual inspection without ground-control fitting or residuals, and the composite GIS outline cannot establish exact addition boundaries. Evidence: `modular/manifest.json`, `evidence_r3.json`, `R3_source_comparison.md`, `orthophoto_export_metadata.json`, and `orthophoto_registration_overlay.png`.
- **Height, floors, and roof — 1.3/2:** The saved shell bounds extend to Z=27.9 m. The SDAC is modeled as three levels to a 14.3 m occupied roof; rooftop units extend to about 15.62 m. The one-story perimeter additions are estimated at 4.6 m. Purdue Athletics supports a three-level development center, while the GIS feature lists `NUM_LEVELS=3` and `Extrution=47`; the schema does not publish units or vertical-field semantics, so the 14.3 m height is a plausible estimate, not a verified datum. The supplied evidence has no LiDAR/DSM or measured elevation test for either the dome or new wings. Evidence: `validation_r3.json`, `evidence_r3.json`, `R3_source_comparison.md`, and `mackey_footprint_source.json`.
- **Facade, entrances, and distinctive architecture — 1.7/2:** R3's close facade views show a red-brick, three-level wing with broad lower glazing, alternating single/pair vertical upper windows, horizontal courses, and an east-end two-story curved glass lobby. A visible two-flight stair and south-facing paired entry are modeled behind/in the curtain wall. This arrangement is directionally consistent with the two HNTB project photographs, which show the long brick wing and curved glazed lobby near Mackey. The brick mapping and facade material read coherently at the supplied render scale. The images are oblique rather than measured elevations; exact bay spacing, lobby arc, stair route, entry dimensions, and current finish colors remain illustrative. The larger arena's stepped roof, glazed concourse, radial support rhythm and lower brick band are represented, but the saved renders are pale/overexposed enough to limit material/color judgement. Evidence: `after_oblique.png`, `after_facade_south.png`, `after_facade_detail.png`, `R3_source_comparison.md`, and `evidence_r3.json`; sources: [HNTB Mackey Athletics Complex project](https://www.hntb.com/projects/purdue-university-mackey-athletics-complex/), [Purdue-2 exterior photograph](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-2.jpg), and [Purdue-3 lobby photograph](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-3.jpg).
- **Interior and circulation — 1.3/2:** The original arena collection contains a modeled Keady Court and seating bowls. R3 represents the SDAC's source-backed full-size practice court plus three breakout shooting bays, and the curved lobby contains a visible stair. The roof-hidden `after_practice_interior.png` confirms the broad practice-space volume and surrounding glazing. The court orientation and breakout bay placement are acknowledged estimates. There are no source-registered partitions or verified routes connecting the SDAC, arena, lobby, courts, and other programs; the renders do not establish a complete internal circulation plan. Evidence: `after_practice_interior.png`, `validation_r3.json`, `evidence_r3.json`, and `R3_source_comparison.md`; program references: [Purdue Athletics Mackey Arena](https://purduesports.com/facilities/mackey-arena) and [DLZ expansion description](https://dlz.com/projects/purdue-university-mackey-arena-expansion/).
- **Technical portability and evidence — 1.9/2:** Blender 5.2.3 reopened the current saved asset. `validation_r3.json` reports 391 objects, 14 SDAC objects, four one-story perimeter components, all new parts parented to `AssetRoot_mackey_arena`, expected materials and structural objects present, metre-aligned brick UVs, and zero linked libraries. Fresh exterior, facade, top, practice-interior, and orthophoto-registration views are retained. The R3 records clearly distinguish photo-traced components and program-level interpretations from verified geometry. Validation confirms saved-file integrity, not an as-built architectural match. Evidence: `validation_r3.json`, `validate_after_reopen.py`, `evidence_r3.json`, and the R3 renders.

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
            "the main arena, north SDAC, and visible low-roof additions are differentiated, but their plan boundaries are photo-interpreted inside composite GIS FID 873",
            "orthophoto supports broad location/orientation; the approximate transform and no-fit visual check do not establish survey accuracy",
            "three SDAC levels and 14.3 m height are source-consistent estimates, not measured elevations",
            "HNTB photos support facade/lobby character and court program sources support use, while exact room layout and circulation remain unverified",
        ],
    }

result = evaluate({
    "identity_footprint_segmentation": 1.7,
    "placement_orientation_scale": 1.7,
    "height_floors_roof": 1.3,
    "facade_entrances": 1.7,
    "interior_circulation": 1.3,
    "technical_portability_evidence": 1.9,
})
# result: score 8.0, max_score 10, criteria sum 9.6/12, passed True
```

**Decision: Pass (8.0/10), narrowly.** R3 demonstrates a coherent arena/SDAC complex and materially improves the SDAC facade, lobby, and addition segmentation using primary project photos and a no-fit aerial comparison. Keep the uncertainties explicit: FID 873 is a composite polygon, the SDAC/perimeter boundaries are photo-traced, heights are estimates, and full circulation is not verified. No model, builder, master, manifest, README, shared index, or other building file was changed for this review.
