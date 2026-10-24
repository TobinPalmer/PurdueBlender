# Knoy Hall — independent full-building review, round 15

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** I reopened the current saved `modular/buildings/knoy_hall.blend` in Blender 5.2.3 and inspected R15 validation/evidence, the R15 entrance render, and the existing full-building/interior previews. The review scores the entire building, not only the latest mortar adjustment.

## Scoring

The six categories use the R14 weighted rubric: identity/footprint, placement/scale, height/roof, facade/entrances, and interior/circulation are each out of 2; technical/evidence is out of 1. The raw score is 8.6/11 and normalizes to **7.8/10**.

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

The broad stepped massing matches Knoy Hall’s identity and the 2018 Purdue Gateway Typical Levels 2–4 plan. Purdue GIS and the 2023 Indiana orthophoto/footprint overlay support the overall site outline. Plan registration remains hand-affine at approximately ±1 m, and the project-local GIS conversion is approximate rather than surveyed. Exact wall-face alignment is therefore less certain than the building identity and broad footprint.

### Placement, orientation and scale — 1.6/2

The manifest records a local asset with placement origin about (218.390 m, 44.120 m); previous source review reports agreement of the saved master marker and manifest. The 2023 orthophoto with GIS overlay is useful independent visual context. It does not establish surveyed control or sub-meter orientation/scale accuracy, and R15 did not change placement or transforms.

### Height, floors and roof — 1.2/2

Purdue’s 2018 planning sheet supports L1–L4 intervals of about 14 ft 8 in, closely reflected in the existing model. The Indiana 3DEP comparison suggests roof-level surface near L5 but cannot distinguish stepped roofs, rooftop equipment or an occupied fifth story. The L5 slab, separate roof deck, penthouse, PV layout and conflicting GIS 48-ft extrusion field remain uncertain. R15 leaves all height and roof geometry unchanged.

### Exterior and entrances — 1.4/2

The exterior represents the stepped form, ribbon glazing, pale horizontal trim, brick sign wall, canopy and light entrance lettering. The R15 shader lowers procedural mortar brightness and width and reduces noise mixed into the brick color. In the fresh R15 render, the masonry reads more controlled than the R14 version, but the joint grid remains conspicuous and the modeled brick still looks lighter and more regular than the red/brown brick in the qualitative Purdue entrance photo. Neither source image is calibrated, so color, course dimensions, bond and face-by-face material assignment remain uncertain. The overall facade rhythm is regularized and unsupported by measured all-sided elevations. No facade geometry or material assignments changed in R15.

### Interior and circulation — 1.7/2

The saved asset contains L1 trace partitions and typical L2–L4 partition meshes, 45 plan-positioned door panels, 39 fixture stand-ins and six stair-run objects. Full-floor R13 plan views show the modeled typical-floor arrangement; the Core B profile is an illustrative two-floor interval. R14 correctly updated the stale trace-status property and documented that the emergency plan names lower and upper basement zones and Purdue IT places a printer near first-floor elevators at the back entrance. These sources do not provide basement floor plans, elevator shaft geometry or stair sections. The 2018 typical plan is manually registered at about ±1 m; fixtures, doors and stairs are schematic. Continuous basement-to-roof circulation, room finishes and most contents remain unverified. R15 made no interior changes.

### Technical and evidence quality — 1.0/1

I directly reopened the R15 source: `Building_knoy_hall`, 64 direct asset objects, 157 descendants / 156 meshes, no linked libraries, and no file-backed image dependencies. `validation_round15.json` passes and confirms the expected 3 partition meshes, 6 stair assemblies, 45 doors and 39 fixture proxies. It also confirms all 156 mesh geometries and world matrices match R14. The validation’s mesh hash is `43a19a6313c06e188082cb547847f583573bafe7f6d9e9ec6da52706b36de5b4`; roof/L5/penthouse/PV placement is unchanged. The evidence package clearly distinguishes qualitative material estimates and source limitations from measured facts.

## Remaining uncertainty and decision

Measured current elevations, calibrated all-sided facade photos, precise roof/L5/penthouse/PV configuration, as-built interior plans and stair sections are still unavailable. Basement and elevator locations have only broad textual support, not modeled geometry. R15 is a saved material refinement with no mesh geometry or placement changes, so it does not resolve the main whole-building accuracy gaps.

**Decision: Fail.** Knoy Hall scores **7.8/10**, below the required **8/10** threshold.

