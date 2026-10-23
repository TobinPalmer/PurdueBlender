# Potter Engineering Center — Independent Round 2 Review

**Reviewed asset:** `modular/buildings/potter_engineering.blend`  
**Review date:** 2026-10-23  
**Independent score:** **6.3/10** (up from 6.1/10 in round 1; still not near the requested 9/10 threshold)

## What improved

- The model now has a visible T-shaped penthouse mass in the location/orientation chosen from the 2016 Existing Penthouse plan (printed page 45). That page visibly labels Room 401 at 3,547 sf and shows a T-like gray area. The model records the historic source and its area scaling/registration uncertainty. This supports an approximate historical massing cue, not a surveyed current roof outline.
- The perimeter shell was clipped at the estimated penthouse floor and remains a closed mesh. The model's overall XY envelope and root origin remain stable.
- Three stair cores are located from S01–S03 labels on the 2016 Existing Third Floor plan; twelve-step paired flights have been added for four level transitions. This is a useful circulation placeholder and its estimate is disclosed.
- The prior material and window-frame improvements remain. The provided exterior render has visible red brick, pale precast panels, dark frame accents, repeated square windows and a rounded stair-tower corner. The model still opens cleanly in Blender 5.2.3, with no unpacked external image dependencies.

## Main findings and limits

### Roof and penthouse

The 2016 drawing supports the existence and approximate T-like plan shape of Room 401, and its 3,547 sf label supports the approximate area. The model's outline has been uniformly scaled to that area because plan registration is approximate. This is transparent, but it cannot verify true location, orientation, profile, height, material or the present-day condition. The modeled roof plate is a 2D T-shaped plane; its roofing material is an estimate.

The broad roof surface still reads as a pale, featureless full-footprint plane in the exterior render. It competes visually with the T-shaped mass and does not convincingly express a roof membrane or detailed parapet. No evidence supports rooftop equipment or mechanical penthouses, so their absence is preferable to invention.

### Stairs and circulation

The 2016 plans support labels/locations for stair cores S01–S03, but the added tread layout, widths, landings and repeated placement across levels are inferred. I verified the blend's object data and the supplied stair detail render. The three-dimensional stair objects are not integrated with the floors: the building floor slabs have no stairwell openings, and no rails, doors, verified landings or elevator shaft are present. As a result, the flights visibly terminate at intact slabs and do not form demonstrated traversable circulation. The illustrative stair image is a detail of stair geometry, not evidence of connected building circulation.

The current interior remains incomplete. The 2016 raster-derived partition objects are still present and were previously assessed as fragmented/overlapping; Room 205 remains only an expressly historical lab vignette. Current Purdue documentation cited in the asset report mentions Room 160 library uses, Room 114, and Rooms 127 PURPL/PURVAC; it does not establish Room 205 as current. No current, connected room plan was verified in this review.

### Exterior, materials and orientation

The facade is still strongly repetitive, with little elevation-specific composition or entrance hierarchy in the provided full exterior view. The provided image does not establish which facade it depicts; the model does not claim that it does. The reviewed screenshots are studio views without neighboring campus context, and they cannot validate site-facing direction. Materials and glazing have improved in legibility but remain stylized: glazing is dark and the pale wall panels, bands and repeated brick piers look unusually uniform. The available references cited in the report do not support a precise allocation of these details to every elevation.

### Envelope and technical health

A fresh headless reopen in Blender 5.2.3 succeeded. `Asset_potter_engineering` contains 476 objects; `AssetRoot_potter_engineering` remains at `(0, 0, 0)`. The structural envelope bounds are approximately 58.4515 × 67.4320 × 13.4112 m after clipping. The reported XY bounds are unchanged from the previous version, supporting preservation of the GIS envelope, though this review did not independently re-register the object against the source GIS feature. There are no unpacked file-backed images. The exterior shell and basement wall mesh were reported as closed in the asset checks; no missing dependency issue was found on reopen.

The 2016 plan and any 2026–28 renovation/concept material must remain distinguished. The proposed renovation is not evidence of existing geometry. I found no proposed future geometry represented in the inspected round-2 edits; Room 401 and stair cues are explicitly tied to 2016 existing plans.

## Scorecard

| Category | Score / 10 | Reason |
|---|---:|---|
| Footprint, placement and massing | 7.0 | Stable GIS-sized envelope and new historic penthouse cue; exact plan alignment and height remain approximate. |
| Exterior form and facade fidelity | 5.8 | Recognizable mass/material vocabulary, but repetitive elevation rhythm and no confidently located entry composition. |
| Materials and surface detail | 6.4 | Improved brick/precast/glazing frames; still flat and repetitive, with a pale roof plane and dark glazing. |
| Interior completeness and circulation | 4.5 | New estimated flights and historic Room 205 vignette; slabs remain uncut and rooms/corridors/doors/elevator are not connected. |
| Architectural details and rooftop | 6.2 | Approximate T-shaped Room 401 from an existing plan; roof surface and associated detail remain crude/uncertain. |
| Technical health and modular export | 9.0 | Fresh Blender reopen, stable root and collection, no missing image dependencies. |
| Evidence and source discipline | 8.3 | Sources and uncertainty are labeled; exact orientation, current interior and surveyed roof remain unsupported. |

**Overall: 6.3/10**

## Highest-impact fixes toward 9/10

1. Obtain or use a floor-slab representation with openings at the documented stair cores; connect the stair geometry cleanly through those apertures and add landings/guardrails only where supported. Avoid describing circulation as complete until this is shown in a cutaway.
2. Replace the pale, broad roof read with a credible roof surface treatment and reconcile the full-footprint slab with the penthouse. Preserve the approximate Room 401 cue but identify it as 2016-derived pending measured roof drawings.
3. Resolve current interiors from current, verified room-plan references. Keep the Room 205 vignette separate and historical; do not infer current function from the old study.
4. Reduce facade repetition and improve elevation-specific detail only when dated, orientation-known imagery or measured elevations can support it. Add site context and a clearly identified entrance only when its face is verified.

## Reopen evidence

- Blender 5.2.3 read `modular/buildings/potter_engineering.blend` successfully during this review.
- Collection: `Asset_potter_engineering`; object count: 476.
- Root: `(0, 0, 0)`.
- Structural envelope bounds: `58.4515 × 67.4320 × 13.4112 m`.
- File-backed images without packed content: none.
- Existing Room 401 source plan: `audit/complete_potter/page56.png` (printed page 45).
- Existing stair label source plan: `audit/complete_potter/page55.png` (printed page 44).
