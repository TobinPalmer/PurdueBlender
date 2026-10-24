# Knoy Hall — independent full-building review, round 11

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** This is a fresh review of the saved R11 asset, using the R11 source/evidence package, reopened-asset validation, plan-overlay and interior renders, entrance close-up, the exterior render, and the prior source records. The score is not carried forward from an earlier review. The five category scores total 10 points.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.9/2 |
| Placement, orientation and scale | 1.7/2 |
| Height, floors and roof | 1.2/2 |
| Exterior and entrances | 1.5/2 |
| Interior and circulation | 1.5/2 |
| **Total** | **7.8/10** |

## Evaluator result

I implemented and ran a scoring function that sums the five category values and returns the evidence and findings. Its result was:

```json
{
  "score": 7.8,
  "max_score": 10,
  "criteria": [
    {"name": "Identity and footprint", "points": 1.9, "max_points": 2},
    {"name": "Placement, orientation and scale", "points": 1.7, "max_points": 2},
    {"name": "Height, floors and roof", "points": 1.2, "max_points": 2},
    {"name": "Exterior and entrances", "points": 1.5, "max_points": 2},
    {"name": "Interior and circulation", "points": 1.5, "max_points": 2}
  ],
  "evidence": [
    "Purdue GIS identity and the 2018 Gateway plan support the building outline and typical-floor arrangement.",
    "The coordinator's master marker check matches the manifest within about 0.000008 m, with zero rotation and unit scale; this confirms internal consistency, not independent campus control.",
    "The 2018 plan supports L1-L4 intervals; 3DEP surface comparison suggests a roof-like level near L5 but does not resolve occupied-floor or penthouse semantics.",
    "R11 adds 45 illustrative door panels at 15 plan-visible locations repeated on L2-L4 and reduces the entrance-letter scale by 20 percent.",
    "R11 reopen validation reports all 45 door panels inside the asset hierarchy and unchanged geometry hashes for the 62 preexisting direct meshes."
  ],
  "findings": [
    "The south entry and source-plan door locations are clearer in R11.",
    "L5, roof and penthouse height remain unresolved, including a conflict with an undocumented 48-foot GIS field.",
    "Facade cadence and material assignment remain schematic without calibrated elevations.",
    "The interior remains a partial typical-floor representation; L1 openings and a continuous basement-to-roof route are unverified.",
    "GIS and orthophoto comparisons are broad screening evidence, not a surveyed wall registration."
  ]
}
```

## Findings

### Identity and footprint — 1.9/2

The official Purdue building GIS feature and the retained Indiana orthophoto/plan context support the identity and broad stepped footprint. The 2018 Gateway plan also identifies Knoy and provides typical upper-level layouts. The GIS outline and orthophoto overlay use the project's approximate coordinate conversion; they do not prove survey-grade wall-to-footprint fit.

### Placement, orientation and scale — 1.7/2

The coordinator's read-only master check found `Placement_knoy_hall` consistent with the manifest to within about 0.000008 m, with zero rotation and unit scale. That proves the saved project placement agrees with its registered record, but the record itself is not independent geodetic control. The plan traces retain about ±1 m hand-registration uncertainty, and no surveyed building control was found in the evidence reviewed.

### Height, floors and roof — 1.2/2

The 2018 Gateway study supports the modeled L1-L4 interval of approximately 14 ft 8 in. The 2018 3DEP DSM/DEM comparison has an indicative median surface-above-ground difference near 59.9 ft, consistent with a roof-like surface around the inherited L5 datum, but its cells mix roof levels, edges, and equipment. It does not establish an occupied fifth floor, exact parapet/penthouse height, or resolve the conflicting GIS 48 ft value. R11 leaves these uncertain rather than inventing dimensions.

### Exterior and entrances — 1.5/2

The exterior render reads as stepped massing with ribbon glazing, pale horizontal bands, brick strips, and a flat roof. R11's photo-supported “KNOY HALL OF TECHNOLOGY” lettering is legible, and the 20% scale reduction addresses the previous relative-size concern. The photograph remains uncalibrated, and the full facade rhythm, exact material values, roof equipment positions, and opposite-side elevations are not independently dimensioned; the model remains schematic in these areas.

### Interior and circulation — 1.5/2

R11 adds 15 door panels at plan-visible door-swing openings on the 2018 typical plan, repeated across L2-L4 for 45 panels total. The overlay makes the selected positions inspectable. Door widths are raster-derived estimates; heights, thicknesses, closed poses, and finishes are illustrative. The spatial view shows partition and stair placement but remains sparse and lacks source-backed room finishes/furnishings. L1 candidates, ambiguous gaps, and continuous circulation through basement, L1, L5, and roof remain unresolved.

## Technical evidence checked

- `evidence_round11.json` identifies the source sheets, registration method, limits, edits, and review images.
- `door_model_validation_r11.json` reports that the saved asset reopened; all 45 panels are in the exported asset hierarchy; the 62 preexisting direct mesh geometries are unchanged; and roof/L5/PV/GIS-registration geometry was not altered.
- Visual checks: `knoy_typical_plan_doors_source_overlay_r11.png`, `knoy_l2_doors_stairs_spatial_r11.png`, `knoy_entrance_detail_r11.png`, and `knoy_exterior_full_r10.png`.
- The uncalibrated 2018 entrance photograph and Purdue Gateway study are useful identity/plan references, not as-built surveys.

## Highest-value next work

1. Seek a measured elevation/section or reliable GIS metadata to resolve floor/roof datums, the L5 interpretation, and the 48 ft field.
2. Obtain calibrated/current facade elevations or matched orthogonal photos before changing all-sided window cadence or material assignments.
3. Improve the interior cutaway's readability and room-level completeness where the plan supports it; keep L1 openings and vertical route uncertain until stronger sources resolve them.

**Decision:** R11 does not pass. Continue iterating and obtain a fresh independent review after the next source-supported improvement.
