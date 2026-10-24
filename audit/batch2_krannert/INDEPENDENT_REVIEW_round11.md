# Krannert Building — independent full-building review, round 11

**Grade: 7.9/10 — below the 8/10 completion threshold.** I assessed the current saved R11 source asset and evidence package directly. R11 makes the upper glazing visibly narrower and more vertical on selected elevations, and the saved-source renders confirm that change. The model still falls short as a full-building asset because the window cadence only partly matches the photographic references, the re-entrant/courtyard gap and most floor interiors remain unresolved, and the strongest registration/height checks have known limits.

Each criterion is scored out of 2 (12 raw points total), then normalized to 10.

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

- **Identity and footprint — 1.8/2:** The model is identifiable as Krannert from its multi-wing office mass, repeated pale piers, dark vertical glazing, dark/recessed ground level and flat roof profile. Purdue Campus GIS BuildingShapesZip4 FID 54 is identified as KRAN. The R8 source-ring extraction/Indiana GIO 2023 orthophoto overlay shows the saved GIS-derived roof outline in the visible footprint without translation, rotation or scale fitting. The ring's very small conversion residual is not an independent accuracy score: both source roof ring and reference originated from FID 54. The orthophoto provides an independent visual cross-check only at screening scale, with shadow/overhang, export resolution and projection approximation limiting wall precision. R11 did not change footprint. Evidence: `evidence_round11.json`, `asset_footprint_round8.json`, `krannert_asset_footprint_ortho_overlay_r8.png`, and the raw feature snapshot `krannert_gis_fid54_4326.json`; sources: [Purdue Campus GIS FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) and [Indiana GIO 2023 imagery](https://di-ingov.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer).
- **Placement, orientation, and scale — 1.8/2:** The saved source uses an identity asset root. The coordinator's read-only master check records `Placement_krannert_building` at `(234.5345001, -412.7189941, 0)`, zero rotation, unit scale, and 0.0000153 m XY delta against the manifest. The no-fit orthophoto overlay supports broad location and orientation. This verifies consistent project registration and broad site correspondence, not surveyed shell placement or independently measured scale; the campus coordinate transform is approximate. R11 makes no placement change. Evidence: `coordinator_placement_review_20261024.json`, `evidence_round11.json`, and `asset_footprint_round8.json`.
- **Height, floors, and roof — 1.5/2:** The current validation confirms the roof deck and 41-vertex top ring were read from the saved R11 source; deck top is 31.791 m in asset-local coordinates. The independent 2018 3DEP DSM / interpolated bare-earth comparison reports median surface difference about 106.46 ft, p25 91.61 ft, p90 106.69 ft, and max 107.66 ft. This is broadly consistent with model surfaces around the L7 datum, roof deck, and 108 ft parapet, but cannot establish named stories or verify the 117 ft penthouse. The GIS vertical field units/semantics are undocumented and the 5 ft DSM may miss narrow roof elements. R11 leaves all floor and roof geometry unchanged. Evidence: `validation_round11.json`, `roof_height_assessment_r7.json`, and `evidence_round7.json`.
- **Facade, entrances, and distinctive architecture — 1.5/2:** R11 modifies the documented south/front 10-bay facade and one photographed long wing from floor-by-floor rectangles toward narrow upper-level vertical glazing strips with transoms. In the supplied R11 head-on comparison, this helps the right-side wing show a taller, slender window rhythm than in the R9 render. However, the modeled facade still reads as stacked per-floor windows and broad horizontal spandrel bands rather than the much taller, uninterrupted narrow glazed slots divided by fine floor-level lines in the October 1965 *Indiana Architect* photo. Other visible elevations retain the earlier rectangular-window treatment. The comparison is qualitative, uses a perspective historical image, and does not calibrate dimensions or current condition. The large black re-entrant opening remains unresolved; entrance canopy and ground-floor details are simple. Evidence: `facade_round11_update.json`, `krannert_south_front_r11.png`, `krannert_southeast_same_corner_r11.png`, `krannert_southwest_same_corner_r11.png`, `krannert_north_long_wing_r11.png`, and `krannert_archival_facade_comparison_r11.png`; sources: [Indiana Architect, October 1965, p. 32](https://usmodernist.org/AIAIN/AIAIN-1965-10.pdf) and [Purdue Events exterior image](https://events.purdue.edu/krannert_building). Neither source is a measured elevation.
- **Interior, courtyard, and circulation — 1.0/2:** The Drawing Room and Parrish Library have recognizable furnishings and room-specific detail. Most floors remain empty or schematic, with no registered full-floor circulation; the courtyard/re-entrant gap remains visually open and unverified. Purdue emergency maps cover basement through floor 7 but are hand-drawn and lack scale, dimensions, date, and as-built status. The 2010 second-floor furniture plan says “not to scale,” and tour photographs do not locate partitions. These materials support room identity and adjacency but not dimensional wall/courtyard reconstruction, so leaving unsupported partitions out is appropriate but leaves substantial full-building work. Evidence: `evidence_round11.json`, `krannert_emergency_maps.pdf`, `krannert_mel_2f_furniture_plan_2010.pdf`, `drawingroom_r2.png`, and `parrish.png`.
- **Technical portability and evidence — 1.9/2:** Blender 5.2.3 reopened the saved R11 source successfully. `validation_round11.json` reports 670 export objects / 662 meshes, identity root, 41 saved roof-ring vertices, all updated facade meshes present, no missing external images, no material-output issues, and no validator issues. R11 includes four reopened-source facade renders and an archival comparison; the evidence explicitly states which source cues support the work and which dimensions/hidden faces/interiors remain uncertain. This is strong technical/evidence work but does not certify as-built architecture. Evidence: `validation_round11.json`, `facade_round11_update.json`, `evidence_round11.json`.

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
            "R11 improves vertical glazing on selected elevations, but the full visible facade still differs from the archival vertical-slot cadence",
            "GIS outline and marker support broad registration; neither verifies surveyed wall placement",
            "LiDAR supports main roof height range but does not verify floor labels or the 117 ft penthouse",
            "most floor interiors and the courtyard/re-entrant seam remain unresolved",
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
# result: score 7.9, max_score 10, criteria sum 9.5/12, passed False
```

**Decision: Fail (7.9/10).** R11 improves a distinctive facade cue with source-supported proportions, but does not sufficiently resolve the broader facade cadence, entrance and re-entrant condition, or full-building interior/courtyard layout. Height semantics remain partly uncertain. No changes were made to the model, builder, master, manifest, README, shared indexes, or other buildings during this review.
