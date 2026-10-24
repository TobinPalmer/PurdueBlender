# Knoy Hall — independent full-building review, round 13

**Grade: 7.7/10 — below the 8/10 acceptance threshold.** I inspected the saved `modular/buildings/knoy_hall.blend` directly in Blender 5.2.3, the R13 validation and evidence records, and the saved-source previews. R13 improves review visibility but reports no saved building-geometry changes, so the score reflects the full asset rather than the new renders alone.

## Scoring

The six categories use a weighted 11-point rubric (five building criteria at 2 points each, plus technical/evidence at 1 point). I normalize the sum to 10: **8.5/11 × 10 = 7.7/10**.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.7/2 |
| Placement, orientation and scale | 1.6/2 |
| Height, floors and roof | 1.2/2 |
| Exterior and entrances | 1.4/2 |
| Interior and circulation | 1.7/2 |
| Technical and evidence quality | 0.9/1 |
| **Normalized total** | **7.7/10** |

## Evidence and findings

### Identity and footprint — 1.7/2

The asset is identified as Knoy Hall, and its broad, stepped massing is consistent with the Purdue GIS footprint and the 2018 Gateway typical-plan/elevation sheet. The 2023 Indiana orthophoto with GIS overlay supports the building outline at site scale. Registration relies on approximate project-local geographic conversion and a hand-affine plan alignment (about ±1 m); neither is survey control. The model reads as the right building, but the alignment and face-level footprint fidelity are not established to survey precision.

### Placement, orientation and scale — 1.6/2

The modular manifest specifies a local-coordinate asset and a placement origin of approximately (218.390 m, 44.120 m). Its recorded world bounds are consistent with the campus-scale GIS placement metadata, and the 2023 orthophoto provides an independent visual footprint check. However, the source package does not contain independent surveyed control points, and the GIS/local conversion is explicitly approximate. This is good map-placement evidence, not proof of exact orientation or scale.

### Height, floors and roof — 1.2/2

The 2018 Purdue planning sheet supports Levels 1–4 with 14 ft 8 in floor-to-floor intervals; the modeled L1–L4 datums closely match those intervals. Indiana 3DEP surface and bare-earth samples suggest a roof-like surface around the inherited L5 datum, but the measurements combine stepped roofs, edges and equipment. The model retains a fifth slab, separate roof deck, penthouse and solar array whose exact presence, level meaning, heights and placement are not fully verified. The GIS 48 ft extrusion field also conflicts with the raster-derived estimate. These uncertainties materially limit height accuracy.

### Exterior and entrances — 1.4/2

The overall stepped volume, ribbon glazing, horizontal pale bands, red/brown brick sign wall, canopy and light entrance lettering are plausible and the material preview makes the brick/glazing choices inspectable. The Purdue-hosted entrance photo supports those broad cues only. The rendered model is still schematic: the long window/mullion rhythm is highly regular, face-specific cadence and assignments lack measured elevations, and the canopy/sign dimensions are not calibrated to the photo. The roof preview shows a simple, unregistered 4×7 PV display and an unverified penthouse mass.

### Interior and circulation — 1.7/2

The saved hierarchy includes typical-level partition traces, 45 illustrative door panels, 39 fixture stand-ins and six stair-run objects across L2–L4. The full-floor R13 plan renders make the traced plan and proxy locations more legible, and the Core B profile shows a two-level stair proxy. These help verify where source symbols were interpreted; they do not make the interior as-built. The source plan is a 2018 planning raster, manually registered at approximately ±1 m, without fixture legend or measured stair sections. Door leaf sizes/poses, fixtures, stair treads/landings and circulation continuity remain illustrative; no continuous route through basement, L1, L5 and roof is established. The plan renders also show largely empty floors rather than furnished, finished interior spaces.

### Technical and evidence quality — 0.9/1

Direct Blender reopen of the saved source found scene `Building_knoy_hall`, 157 objects / 156 meshes in the asset hierarchy, no external library links, and no file-backed image dependencies. R13 validation reports 64 direct asset objects, 157 descendants, the expected partition/stair/door/fixture child counts, and an unchanged fingerprint for 62 pre-existing shell meshes. The evidence package clearly distinguishes source-supported facts from estimates and records important limitations. One embedded root property is stale: `evidence_plan_trace_status` says the upper-floor partitions “are not yet traced,” although R13 shows them as modeled and validated. That metadata inconsistency slightly reduces technical confidence.

## Uncertainty and disposition

The main remaining unknowns are current measured elevations and roof/L5 semantics, calibrated all-sided facade documentation, surveyed placement controls, and as-built interior/stair details. R13's additional plan and stair renders are useful audit evidence, but the R13 scope and the unchanged shell hash show that they do not resolve these building-geometry uncertainties.

**Decision: Fail.** Knoy Hall scores **7.7/10**, below the required **8/10** threshold.
