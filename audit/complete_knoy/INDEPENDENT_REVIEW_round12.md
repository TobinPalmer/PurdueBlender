# Knoy Hall — independent full-building review, round 12

**Grade: 7.9/10 — below the 8/10 acceptance threshold.** I reviewed the current saved R12 source library directly in Blender 5.2.3, the R12 source and validation records, the R12 plan/cutaway previews, and the previous full-building evidence. The grade below is for the entire building, not only the washroom additions. The five category scores total 10 points.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.9/2 |
| Placement, orientation and scale | 1.7/2 |
| Height, floors and roof | 1.2/2 |
| Exterior and entrances | 1.5/2 |
| Interior and circulation | 1.6/2 |
| **Total** | **7.9/10** |

## Evaluator result

I implemented and ran an evaluator that sums the five category scores and returns the supporting evidence and findings:

```json
{
  "score": 7.9,
  "max_score": 10,
  "criteria": [
    {"criterion": "Identity and footprint", "score": 1.9, "max_score": 2},
    {"criterion": "Placement, orientation and scale", "score": 1.7, "max_score": 2},
    {"criterion": "Height, floors and roof", "score": 1.2, "max_score": 2},
    {"criterion": "Exterior and entrances", "score": 1.5, "max_score": 2},
    {"criterion": "Interior and circulation", "score": 1.6, "max_score": 2}
  ],
  "evidence": [
    "Purdue GIS identity/footprint and the 2018 Gateway typical-plan raster are documented; plan registration remains hand-affine at about +/-1 m.",
    "The coordinator marker agrees with the manifest to about 0.000008 m at zero rotation/unit scale, which proves internal consistency, not independent survey control.",
    "Direct Blender 5.2.3 reopen found Asset_knoy_hall with 157 objects / 156 meshes, including 45 door panels and 39 fixture proxies, with no external library links or missing image files.",
    "The R12 plan shows two fixture banks interpreted as washrooms but has no fixture legend; type, use, size and finish remain illustrative."
  ],
  "findings": [
    "R12 adds symbol-aligned washroom fixture stand-ins repeated across L2-L4.",
    "L5/roof/penthouse semantics and the GIS 48 ft conflict remain unresolved.",
    "Exterior cadence/material mapping remain schematic; interior coverage is partial and basement-to-roof circulation is unverified."
  ]
}
```

## Findings

### Identity and footprint — 1.9/2

Purdue's official GIS building feature and the 2018 Gateway study support Knoy's identity and broad stepped footprint. The study labels the upper drawing as Typical Plan Levels 2-4, making it useful for interior arrangement. The plan-to-model transform is hand-affine and stated as approximately ±1 m; the GIS/orthophoto overlay is broad context evidence rather than a survey of structural wall faces.

### Placement, orientation and scale — 1.7/2

The coordinator's placement check reports that `Placement_knoy_hall` matches the manifest within about 0.000008 m, with zero rotation and unit scale. This is good evidence that the saved master and manifest agree. It does not independently establish the building's campus position from surveyed control, and the hand-registered interior plan retains approximately ±1 m uncertainty.

### Height, floors and roof — 1.2/2

The Gateway study supports the modeled L1-L4 interval of approximately 14 ft 8 in. The prior 2018 Indiana 3DEP DSM/DEM comparison suggests a roof-like level near the inherited L5 datum, but the broad surface samples combine roof edges, stepped levels and rooftop equipment. They do not show whether L5 is occupied, determine parapet or penthouse height, or resolve the undocumented GIS 48 ft attribute. R12 leaves this geometry unchanged and unverified.

### Exterior and entrances — 1.5/2

The existing exterior reads as a stepped multi-level building with ribbon glazing, horizontal pale bands, brick strips and a flat roof. R11's photo-supported south entrance lettering is present at the reduced scale. Facade cadence and material layout remain schematic: the retained photographs are uncalibrated, and no measured all-side elevation or verified roof-equipment layout was found. R12 makes no exterior changes.

### Interior and circulation — 1.6/2

R11's 45 closed door panels remain at 15 plan-visible openings, repeated across L2-L4. R12 adds 39 simple basin/toilet-like stand-ins at the symbol centers of two compact fixture banks on the same 2018 plan, repeated on L2-L4. The plan-overlay and enlarged detail make those source locations inspectable. However, the plan has no fixture legend or schedule, so the washroom/use and fixture-type interpretation is moderate-confidence; sizes, heights, finishes, orientation and current as-built state are illustrative. The cutaway shows only a partial, largely unadorned typical-floor interior. L1 openings and continuous circulation through basement, L1, L5 and roof remain unverified.

## Technical evidence checked

- Opened `modular/buildings/knoy_hall.blend` directly in Blender 5.2.3: `Building_knoy_hall`, 157 objects / 156 meshes; the fixture collection has 39 objects and the door collection 45. No library links or missing image dependencies were reported.
- `evidence_round12.json` records the source plan, visual interpretation, approximately ±1 m plan-registration limit, fixture dimensions/status, edits, and unresolved issues.
- `fixture_validation_r12.json` reports saved-asset reopen success, all 39 fixtures in the exported hierarchy, and unchanged hashes for the 62 preexisting shell meshes.
- Visual checks: `knoy_typical_plan_fixture_overlay_r12.png`, `knoy_typical_plan_restroom_detail_r12.png`, `knoy_l2_typical_plan_rooms_r12.png`, and `knoy_washroom_cutaway_r12.png`.

## Highest-value next work

1. Obtain measured height/elevation evidence or GIS schema documentation for the L5, roof and 48 ft discrepancy.
2. Seek calibrated/current facade elevations before revising repetitive exterior cadence or assigning precise materials.
3. Improve the interior cutaway's floor-wide clarity and completeness only where source plans support it; preserve uncertainty for fixture and circulation details absent from the source.

**Decision:** R12 improves the source-referenced interior, but the whole building scores 7.9/10 and does not pass. Continue source-backed iteration and request another independent full-building review.
