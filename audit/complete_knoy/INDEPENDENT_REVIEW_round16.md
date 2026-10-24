# Knoy Hall — independent full-building review, round 16

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** I reopened the current saved `modular/buildings/knoy_hall.blend` directly in Blender 5.2.3 and inspected the R16 validation, evidence and entrance render, together with the full-building and interior previews. This score evaluates the entire building, not only the updated brick shader.

## Scoring

I use the same six-category weighted rubric as the R14 and R15 reviews: identity/footprint, placement/scale, height/roof, exterior/entrances, and interior/circulation are each out of 2; technical/evidence is out of 1. The raw sum is 8.6/11, normalized to **7.8/10**.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.7/2 |
| Placement, orientation and scale | 1.6/2 |
| Height, floors and roof | 1.2/2 |
| Exterior and entrances | 1.4/2 |
| Interior and circulation | 1.7/2 |
| Technical and evidence quality | 1.0/1 |
| **Normalized total** | **7.8/10** |

## Findings and evidence

### Identity and footprint — 1.7/2

The stepped building form is consistent with Knoy Hall’s campus identity and the Purdue GIS footprint. The 2018 Gateway typical Levels 2–4 plan supports its interior plan shape, while the 2023 orthophoto with GIS overlay supports the broad campus context. Registration of the typical plan is hand-affine at approximately ±1 m; the local geographic conversion is approximate. These sources support identity and general footprint better than exact wall-face dimensions.

### Placement, orientation and scale — 1.6/2

The manifest uses local coordinates and places the asset at approximately (218.390 m, 44.120 m); prior master review found the marker consistent with this origin. The 2023 orthophoto/GIS overlay is a useful independent visual placement check. No survey control establishes exact orientation or scale, and R16 reports no transform or placement changes. I therefore retain the previous placement assessment.

### Height, floors and roof — 1.2/2

Purdue’s 2018 planning sheet labels Levels 1–4 at approximately 14 ft 8 in floor-to-floor, which is closely reflected in the model. The 3DEP surface comparison suggests a roof-like elevation near the L5 datum but cannot separate roofs, stepped levels and equipment or establish whether L5 is occupied. The separate L5 slab, roof deck, penthouse and PV layout remain uncertain; the GIS 48 ft extrusion attribute conflicts with the other height evidence. R16 does not change height or roof geometry.

### Exterior and entrances — 1.4/2

The entrance view shows brick, pale trim, dark glazing, canopy and light “KNOY HALL OF TECHNOLOGY” lettering, broadly consistent with Purdue entrance photos. The R16 brick palette is darker and the mortar is narrower/dimmer than in R15; its new render shows the intended improvement. The remaining visible brick grid is very regular, and the wall still looks more uniform than the photograph. Exact color, mortar dimensions, bond, facade cadence and face-by-face materials are not measurable from the available perspective photos. The overall exterior remains schematic; R16 changes only shader values, not facade geometry or assignments.

### Interior and circulation — 1.7/2

The saved source includes a first-floor thesis-plan trace and typical L2–L4 partitions, 45 door panels, 39 fixture proxies and six stair-run objects. R13 plan and stair previews make these source interpretations inspectable. R14/R16 evidence correctly distinguishes the two named basement zones and approximate first-floor elevator vicinity from unsupported geometric claims. However, the 2018 plan is a manually registered planning raster, fixtures are interpreted without a legend, and stair sections remain illustrative. There is no verified continuous route through the basement, L1–L5 and roof. Most rooms lack as-built finishes and contents. R16 does not alter interior geometry.

### Technical and evidence quality — 1.0/1

Direct saved-source reopen found `Building_knoy_hall`, 64 direct asset objects, 157 descendants / 156 meshes, no linked libraries and no file-backed image dependencies. R16 validation passes and confirms the expected 3 partition meshes, 6 stair assemblies, 45 doors and 39 fixture stand-ins. It reports that all 156 mesh geometries and world matrices match R15; the fingerprint is `43a19a6313c06e188082cb547847f583573bafe7f6d9e9ec6da52706b36de5b4`. The saved source itself contains the R16 brick values (colors 0.12/0.032/0.013 and 0.055/0.013/0.005 linear; mortar 0.10/0.08/0.06, estimated width 0.002 m). The evidence records their qualitative, uncalibrated basis and explicitly states that no geometry changed.

## Remaining uncertainty and decision

No newly found source supplied measured facade elevations, current roof/penthouse/PV layout, as-built interior plans or stair sections. The archive records and Exponent index are research leads only; no scanned drawings or photos were inspected. Basement/elevator text confirms location/use cues but not geometry. R16 improves the material preview while leaving the significant facade, roof and circulation questions open.

**Decision: Fail.** The full Knoy Hall asset scores **7.8/10**, below the required **8/10** threshold.

