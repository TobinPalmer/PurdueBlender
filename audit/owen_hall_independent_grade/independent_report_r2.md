# Owen Hall independent regrade — GIS footprint revision

**Score: 7.8/10 — below the project’s 8/10 completion threshold.** This review grades the saved Owen Hall asset at SHA-256 `a2d3b7814eac1adc0a8b28af989df25c7ab3c6a1129da90c40e9bd7871a5d7dc`, after reopening it in Blender 5.2.3. It replaces the old 7/10 evaluation for the earlier 799-object revision; it does not change the asset.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Purdue GIS OBJECTID 38 identifies Owen Hall. The reopened base mesh matches the 20-point GIS outline exactly in the project’s approximate coordinate frame (IoU 1.000, equal 87.623 × 107.558 m envelopes). Purdue’s report also describes a four-story H-shaped residence hall. |
| Placement, orientation, and scale | 2.0/2 | The rebuilt shell is aligned to the transformed source outline; the validation records 0.0 m envelope-center error and a local asset root at (0, 0, 0). This relies on the project’s approximate WGS84-to-meter conversion, not surveyed control. |
| Height, floors, and roof | 1.5/2 | The H plan and four-story use are supported. The model’s 3.8 m floor rhythm and 16.0 m parapet elevation remain estimates; neither the report nor GIS supplies measured elevations. The flat parapet is broadly consistent with the official exterior image. |
| Facade and material finish | 1.0/2 | Brick, pale limestone/concrete bands, and repeated vertical windows capture the broad residential character. The comparison render remains simplified: window divisions and louvered portions, large glazed bays, entrance steps/rails, and facade depth are not modeled to the reference level. The render also has a flat, over-bright presentation. The reopened collection uses 17 node-based materials and no external image paths, but material-node presence alone does not establish photographic accuracy. |
| Interior, portability, and integration evidence | 1.3/2 | The asset includes named lobby, recreation lounge, study-center, and dorm-room sets, with furniture, fixtures, and lights. They provide useful interior vignettes but do not document complete, source-verified interiors across all floors. The file reopens as a portable 728-object collection with no external image paths. The shared manifest still says 799 objects, so its asset inventory is inconsistent and the master-library refresh is not validated for this revision. |
| **Total** | **7.8/10** | **Not yet a pass.** |

## Evidence checked

- Reopened-asset footprint validation: [`gis_footprint_validation.json`](gis_footprint_validation.json). It identifies Purdue GIS OBJECTID 38, the base mesh, exact polygon agreement in the documented approximate project transform, zero local root translation, and the current 728-object collection.
- GIS snapshot and source history: [`sources/purdue_owen_gis_feature_38.json`](sources/purdue_owen_gis_feature_38.json), [`source_provenance.json`](source_provenance.json), and Purdue’s 2007 report at [`sources/purdue_owen_hall_ground_level_plan_report.pdf`](sources/purdue_owen_hall_ground_level_plan_report.pdf). The report supports the H-shaped plan and four stories but is not dimensioned.
- Exterior comparison: [`sources/purdue_owen_exterior.jpg`](sources/purdue_owen_exterior.jpg) and the current model view [`owen_hall_facade.png`](owen_hall_facade.png). The image supports general brick/stone materials and the residential window rhythm, not exact heights or full facade measurements.
- Plan view: [`owen_hall_gis_footprint_topdown.png`](owen_hall_gis_footprint_topdown.png).
- Direct Blender 5.2.3 inspection confirmed the named collection has 728 objects (711 meshes, 11 lights, 5 cameras, 1 empty), 17 assigned node-based materials, and no external image paths. The shared manifest entry still lists 799 objects.

## Remaining work before completion

1. Update the shared manifest object list/count from the reopened 728-object collection and verify all listed objects and bounds.
2. Refresh and reopen the master library link, then verify its placement marker and linked object count.
3. Refine facade window/glazed-bay and entrance details against the Purdue photo; improve the lighting/exposure used for review renders.
4. Keep the height and floor elevations explicitly estimated unless a measured source is found; avoid treating the four-story report as a height measurement.
5. Expand or label the interior scenes so their schematic/source-supported scope is clear and they do not imply verified as-built floor plans.

The previous 7/10 report evaluated the pre-rebuild shell and its now-superseded coarse structural-footprint proxy. This regrade uses the exact GIS-outline base validation for the new geometry and scores the separate remaining limitations above.
