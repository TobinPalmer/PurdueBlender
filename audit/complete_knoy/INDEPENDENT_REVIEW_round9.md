# Knoy Hall — independent full-building review, round 9

**Grade: 7.7/10 — below the 8/10 acceptance threshold.** Reviewed read-only on 2026-10-24 against the saved source asset, current Knoy evidence, round 9 validation, and the project’s whole-building categories. No Knoy geometry or shared/master files were edited for this review.

| Category | Score |
| --- | ---: |
| Footprint/GIS registration and placement | 8.8/10 |
| Exterior massing, facade and materials | 7.0/10 |
| Floors, height and roof form | 6.4/10 |
| PV and roof equipment | 8.2/10 |
| Interior plan fidelity | 7.5/10 |
| Doors and circulation | 6.3/10 |
| Evidence/reopen/technical integrity | 9.4/10 |

## Findings

Round 9 is a careful, source-limited material pass, not a building-geometry revision. The Purdue profile photo supports broad red/brown masonry, dark recessed glazing and light horizontal trim, but it is a single undated, uncalibrated perspective. It does not establish exact face correspondence, mortar color, material specification or full facade cadence. The lighter mortar is a render estimate; the saved asset geometry fingerprint is unchanged. Reopen validation passes, and the builder material functions were exercised in an unsaved Blender audit scene. These are good technical/provenance practices, but the exterior remains a repetitive, simplified facade with limited source coverage and no calibrated comparison.

Footprint and placement remain comparatively strong at screening level: the retained 2023 Indiana orthophoto and GIS footprint overlay support the roof/building context and outline. They are not proof of a surveyed shell registration or individual facade dimensions. The withdrawn cyan PV-bounds overlay is excluded from this grade and must not be used as alignment evidence.

Vertical evidence is plausible but not definitive. The 2018 3DEP DSM median of 680.94 ftUS minus 21 sampled bare-earth DEM values with a median of 621.06 ft gives about 59.9 ft. The 5 ft DSM’s broad p10–p90 spread is about 30.4–63.9 ft AGL. Because the DSM mixes roof levels, edges and rooftop objects, while bare earth is interpolated beneath the building, this is a rough height cross-check, not an as-built roof survey. It is consistent with a roof-like surface near the retained L5 slab datum (~58.8 ft), but does not establish an occupied fifth floor, exact roof/penthouse height, or resolve the conflicting GIS 48 ft field. L5 remains explicitly unverified.

The 2017 Purdue report supports a historical count of 28 solar modules; the 2023 orthophoto shows a panel-like installation somewhere in the south roof zone. Neither source verifies the model’s exact array layout, transform, tilt, equipment height or continued presence in 2026. Keep the array schematic and the cyan alignment overlay retracted.

Interior plan evidence is useful but bounded. L2–L4 traces are compared with a 2018 typical-floor plan and have approximately ±1 m registration uncertainty; L1 traces come from a separate thesis plan and are approximate. The green registration overlays compare the source raster with geometry traced from that same raster, so they demonstrate trace consistency rather than independent as-built agreement. Current plan cutaways are thin and sparse, without verified furnishings or finishes. Candidate L1 door gaps remain unresolved; test collisions only reject the specific trial positions. Three illustrative stair cores do not demonstrate a continuous verified route from basement to roof. Emergency-plan room labels support some floor-use labels, not plan geometry or circulation.

## Highest-value next work

1. Seek measured/as-built facade or section sources to resolve exterior cadence, story/roof levels and the GIS height conflict; keep L5 and the penthouse explicitly uncertain until then.
2. Improve exterior resemblance only where additional source views support the change; avoid treating the single profile photo as a full facade elevation.
3. Make interior evidence easier to read at whole-floor scale and add furnishings only when supported by plan/photo evidence. Resolve candidate doors and vertical circulation only from stronger source material.
4. Keep the 28-module count historical, PV placement schematic, and the invalid cyan overlay marked withdrawn.

## Evidence reviewed

- `modular/buildings/knoy_hall.blend`
- `audit/complete_knoy/facade_material_review_r9.json`
- `audit/complete_knoy/facade_material_validation_r9.json`
- `audit/complete_knoy/builder_material_validation_r9.json`
- `audit/complete_knoy/roof_height_validation_r8.json`
- `audit/complete_knoy/INDEPENDENT_REVIEW_round8.md`
- `audit/complete_knoy/knoy_south_facade_source_review_r9.png`
- Retained Purdue profile photo, 2017 Purdue PV report, 2023 Indiana orthophoto/GIS context, 2018 Gateway plan/height reference, thesis L1 plan and the documented 2018 3DEP/DEM analysis.
