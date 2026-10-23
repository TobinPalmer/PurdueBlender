# Potter Engineering Center — Independent Review, Round 5

**Review date:** 2026-10-23  
**Asset reopened:** `modular/buildings/potter_engineering.blend` in Blender 5.2.3  
**Overall rating:** **7.0/10**

## Scope and method

I independently opened the saved blend in background Blender and queried the saved collection, object bounds, root transform, dependencies, and basement landing/flight bounds. I also inspected `exterior_current.png` and `stairwell_cutaway.png`. I made no edits to the model. This review treats the 2016 study plans as approximate historic evidence, not surveyed or current documentation.

## What improved

- The exterior render reflects the current geometry/material state: it was rendered at 08:15:34, then the blend was saved at 08:16:00. The finalization script renders the exterior after setting the roof material, then saves without another geometry change. The exterior view now clearly shows a T-like penthouse profile and dark roof membrane.
- The building root remains at `(0, 0, 0)` and the structural envelope still measures approximately `58.4515 × 67.4320 m` in XY. The export collection opens with 503 objects and no unpacked external image dependencies.
- The Room 401 mass is now a hollow perimeter shell, and a ray passes through the aligned estimated opening at the shared 4S04/Room 401 wall. Rays just to either side hit the walls. This is a useful local check of that doorway geometry.
- The basement landing slabs now overlap the bounds of their lowest flights. For all three cores the landing top is at `z=-3.904 m`, while the flight starts around `z=-4.049 m`; their XY bounds overlap by about 0.56 m in one axis. This fixes the earlier gross gap.
- Stairwell cutaway is legible as a sequence of flights, landings, rails, slab openings, and the penthouse enclosure. It remains an explanatory isolated render, not proof of an accessible route through the actual building.

## Remaining blockers

1. **No verified basement route.** The landing/flight report tests axis-aligned bounding boxes, not walking-surface continuity, head clearance, stair-end alignment, or a connection to a basement corridor. The landing overlap is real, but its exact registration to a BS-labeled core is unverified. Do not claim a continuous or currently accessible route to the basement.
2. **Stair detail is still approximate.** The cutaway contains thin projecting plates and crossing rails/diagonal members that make the stair assemblies look mechanically rough at close view. Several stair runs touch/overlap by bounding boxes, but this does not prove clear, coherent walking paths between every flight and landing. The modeled set includes ten flights, not a fully verified system for every floor/core.
3. **Roof remains a broad estimate.** The large flat plane occupies nearly the entire building and dominates the exterior. The dark material gives it definition, but no measured parapet, roof equipment, drainage, or verified roof construction is shown. Room 401’s plan-derived footprint and height are still approximate.
4. **Facade composition lacks verified entrances and variation.** The brick, precast panels, recessed glazing, and bronze frames read more clearly, but the repeated window bays and blank ground-floor band remain repetitive. No entry canopy or stair is allocated to a facade because the available photograph’s elevation is unknown.
5. **Interior coverage and evidence remain limited.** The model has historic raster-derived partition meshes and a single Room 205 vignette based on the 2016 study. Current sources document other uses and do not establish Room 205 as current. Interior layouts, elevator, doors, and connected corridors remain unverified.

## Scorecard

| Category | Score | Evidence |
|---|---:|---|
| Footprint, placement, and massing | 7.4 | GIS envelope and root are stable; historic-plan penthouse gives a more readable top profile, with estimated height/registration. |
| Exterior detail and composition | 6.4 | Materials and frames improve legibility; facade remains repetitive and entrance side is unresolved. |
| Materials and texturing | 7.2 | Brick, precast, ground-floor treatment, and dark roof are coherent; glazing reads quite dark. |
| Interior and circulation | 5.0 | Visible stair system and doorway checks improve the model; no verified basement corridor or full connected circulation. |
| Roof and architectural detail | 6.4 | Penthouse profile and membrane improve silhouette; broad roof surface and equipment remain undocumented estimates. |
| Technical integrity | 9.0 | Fresh Blender reopen, 503 collection objects, stable root/GIS XY bounds, no external image dependencies. |
| Evidence and provenance | 8.2 | Report cites historic/current sources and uncertainty; rendered views are identified and dated relative to the saved blend. |

**Overall: 7.0/10.** The main objective evidence-backed gain is the penthouse silhouette and locally improved stair/door interfaces. The remaining route and roof uncertainty prevent a higher score. This is not a 9/10 result.

## Independent reopen evidence

See `round5_reviewer_reopen_checks.json` for fresh Blender observations, including bounds and render/save timestamps. The landing-flight measurements are geometric AABB overlap only; they are deliberately not interpreted as proof of a walkable or connected route.
