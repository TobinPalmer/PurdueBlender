# Knoy Hall — independent full-building review, round 14

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** I independently reopened the current saved `modular/buildings/knoy_hall.blend` in Blender 5.2.3, inspected the R14 validation and evidence, and reviewed the R14 material render alongside the R13 whole-building and interior views. This grade assesses the full building; it does not treat the R14 source/metadata correction as a substitute for building geometry.

## Scoring

I use the six-category weighted rubric applied in the R13 review: the five building criteria score up to 2 points each and technical/evidence up to 1 point (11 raw points). The total is normalized to 10: **8.6/11 × 10 = 7.8/10**.

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

The saved asset is identifiable as Knoy Hall. Its stepped massing is consistent at a broad level with the Purdue GIS footprint, the Purdue 2018 Gateway Levels 2–4 plan, the entrance photos, and the 2023 Indiana orthophoto context. The interior plan and footprint registrations are manual estimates (about ±1 m for the typical-level plan), rather than surveyed control; the broad identity and outline are better supported than exact wall-face fit.

### Placement, orientation and scale — 1.6/2

The modular manifest places the local asset at approximately (218.390 m, 44.120 m), and the prior source review reported internal agreement between the marker and manifest. The 2023 GIS/orthophoto overlay supports the broad campus position and footprint. I retain the R13 placement score: R14 changes no placement geometry, and the asset evidence still describes approximate geographic conversion and hand-affine plan registration, not independent surveyed orientation or scale.

### Height, floors and roof — 1.2/2

The 2018 Gateway planning sheet supports L1–L4 spacing of about 14 ft 8 in, closely matched by the modeled datums. The statewide 3DEP comparison suggests a roof-like surface near the L5 datum but combines stepped roofs, edges and equipment. L5, the separate roof deck, penthouse and PV layout remain source-conflicted or approximate; the GIS 48 ft extrusion attribute is unresolved. R14 makes no height or roof change.

### Exterior and entrances — 1.4/2

The entrance view includes the red/brown brick sign wall, light lettering, dark glazing, pale trim and canopy, matching broad cues in Purdue-hosted entrance imagery. R14 darkens and roughens the existing procedural brick, lowers the mortar size and contrast, and reduces bump. The new preview is improved in material control, but brick and mortar still read as a regular procedural pattern with bright joints; their dimensions, bond, exact color and all-face mapping have not been calibrated. The whole-building exterior also retains highly regularized facade cadence. R14 does not change facade geometry or material assignments.

### Interior and circulation — 1.7/2

The saved hierarchy contains L1 thesis-plan trace segments and L2–L4 typical-plan partition meshes, 45 illustrative door panels, 39 symbol-interpreted fixture proxies and six stair-run objects. The R13 full-floor views make this partial arrangement inspectable. R14 correctly records the upper-level trace status and now describes the limits of both source plans. Purdue’s emergency plan verifies lower- and upper-basement zones, while the printer locator supports a first-floor elevator vicinity near the back entrance; neither locates basement outlines, shafts or stair sections. No geometry was added from these text-only location sources. The interior remains sparse, and continuous circulation from basements through L1–L5 and roof is not established.

### Technical and evidence quality — 1.0/1

I directly reopened the saved R14 source: scene `Building_knoy_hall`, 64 direct asset objects, 157 descendants / 156 meshes, no linked libraries and no file-backed image dependencies. `validation_round14.json` passes; it verifies 3 typical partition meshes, 6 stair assemblies, 45 doors, 39 fixtures, corrected trace metadata, documented basement/elevator limits, and equality of all 156 mesh geometries and world matrices to the pre-R14 backup. The 62 pre-existing shell-mesh hash is unchanged. R14 clearly separates source evidence from inference and does not invent basement/elevator geometry unsupported by the cited sources. The technical/evidence record is strong.

## Remaining uncertainty and decision

The model still lacks measured current elevations and all-sided facade documentation; exact L5/roof/penthouse/PV interpretation is unresolved. Interior fit-out, basement/elevator geometry and continuous circulation remain incomplete or unverified. R14 improves provenance and brick presentation, but validation explicitly confirms that no mesh geometry, placement, level, roof, stair, door or fixture geometry changed from the prior revision.

**Decision: Fail.** The full Knoy Hall asset scores **7.8/10**, below the required **8/10** threshold.

