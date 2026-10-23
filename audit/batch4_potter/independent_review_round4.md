# Potter Engineering Center — Independent Round 4 Review

**Reviewed asset:** `modular/buildings/potter_engineering.blend`  
**Review date:** 2026-10-23  
**Independent score:** **6.9/10** (up from 6.7/10; roof/stair evidence discipline improved, but circulation remains ungrounded)

## Review method

I freshly reopened the saved asset in Blender 5.2.3 LTS and inspected its export collection, root, stair/landing object extents, roof slab, penthouse mass and material assignments. I compared the penthouse/core evidence against the retained 2016 Existing Penthouse plan (printed p.45) and inspected the round-4 cutaway and available exterior render. I made no edits to the blend file.

## What improved

- The exterior shell now stops at the estimated penthouse level (z=13.4112 m), while the T-shaped Room 401 mass is explicitly identified as a 2016-plan estimate scaled to the plan’s 3,547 sf label. This is a more informative roof profile than the previous undifferentiated tall shell.
- Round 4 removed the unsupported S01/S02 stair continuations above the main roof. The retained roof aperture corresponds to the S03/4S04 core shown on the 2016 Existing Penthouse plan. The roof uses an explicitly estimated membrane material. No unsupported rooftop mechanical equipment is asserted.
- The basement now has three visible floor-level landing objects. The limitations are candidly stated: landing locations, core registration and access remain unverified.
- Fresh Blender reopen succeeded. `Asset_potter_engineering` has 503 objects; the asset root remains at `(0,0,0)`, and shell XY dimensions remain about `58.4515 × 67.4320 m`. No missing external image dependencies were found.
- The round-4 report correctly preserves uncertainty around the facade direction: the available exterior photo is not assigned to a particular elevation, and the entrance/canopy remain unmodeled.

## Remaining issues

### Basement stair route remains unresolved

Adding landing objects does not yet ground the basement route. For S03, the landing bounds end at x=8.80 m while the lowest flight begins at x=9.1425 m, leaving about a 0.34 m horizontal gap in their axis-aligned bounds; its y range matches. The other two landings are similarly offset relative to their lowest flights. These bounds alone do not prove all mesh surfaces are disconnected, but they expose a likely interface gap that should be checked at mesh level. More decisively, no basement corridor, door, or connection to the surrounding basement plan is modeled, and the author’s evidence report says exact lower-level core matching remains unverified. Therefore the route from the building’s basement circulation to these stairs is still **not grounded**. The added landings are a visual placeholder, not evidence of an accessible route.

The cutaway shows isolated stair assemblies and cropped copies of slab regions. It does not show corridor walls, doors, or a connected floor context. Center-ray checks establish that a point at each of the three upper-level apertures is clear; they do not verify the full opening perimeter, stair-to-landing interfaces, approach routes or walkable circulation. No architectural/code compliance conclusion is warranted.

### The 4S04 enclosure does not yet prove a penthouse connection

The separate six-piece enclosure is a useful cue from the historic label, but its wall dimensions and door are estimated. The cutaway hides the enclosure, and the report does not demonstrate that its doorway remains physically open into Room 401 rather than facing overlapping penthouse mass geometry. The T-shaped penthouse footprint’s scale/placement are also approximate because the historic plan registration is not exact. The available image supports the historic T-shaped outline and area label, not current measured roof geometry.

### Roof and facade evidence

The roof material has a reasonable provenance label, but the broad full-footprint surface and roof build-up remain estimates. The exterior image visible in the audit folder predates round 4 (the report says it reflects round 2), so it should not be used to judge the current roof openings or stair projections. A fresh round-4 exterior render is needed to make the current roof reviewable. The 2016 roof plan is a useful historic basis, but it is not current roof photography or a measured roof survey.

The facade still reads as repeated, evenly spaced brick piers, pale panels and small dark windows. Those material choices are documented as estimates; the available undirected photo is correctly not used to claim which facade has the entry. Current, orientation-known views and more detailed elevation references are needed for further fidelity.

### Historic interiors and partitions

Room 205 remains a small historical vignette, not a verified current space. Raster-derived partitions remain dense and fragmentary in the asset. The report keeps them labeled historic, but the model still lacks a connected current interior plan, door/corridor network and elevator shaft.

## Scorecard

| Category | Score / 10 | Reason |
|---|---:|---|
| Footprint, placement and massing | 7.0 | GIS footprint/root remain stable; historic penthouse outline and elevation are documented estimates. |
| Exterior form and facade fidelity | 5.8 | Distinctive rounded corner and material vocabulary help, but repetitive bays and missing verified entry composition remain. |
| Materials and surface detail | 6.8 | Brick, precast, glazing frames and estimated roof membrane are more legible; roof surface remains broad and unverified. |
| Interior completeness and circulation | 5.2 | Upper slab apertures and stairs are depicted, but flight/landing interfaces and basement/corridor access are not established. |
| Architectural details and rooftop | 6.8 | T-shaped 2016 penthouse and S03/4S04 aperture improve the roof story; dimensions, membrane and enclosure remain estimated. |
| Technical health and modular export | 9.0 | Fresh reopen, stable root and export collection, no missing image dependencies. |
| Evidence and source discipline | 8.2 | Historic/current/future limits are clearly separated; available exterior image is not assigned a facing; current exterior render is stale. |

**Overall: 6.9/10**

## Highest-value remaining work

1. Resolve the basement landing and lowest-flight interface against the historic lower-level plan, then show its connection to an actual corridor/door if the source supports it. If it cannot be verified, keep the termination explicitly unresolved and do not present it as continuous circulation.
2. Check all floor-to-flight and flight-to-landing interfaces and full aperture perimeters. Replace center-ray-only checks with actual clearance and connection checks.
3. Render the current round-4 asset’s exterior and stair cutaway with enough surrounding geometry to assess the roof and landings. Confirm the 4S04 doorway is open to Room 401 without overlap.
4. Use connected, current interior evidence and dated, orientation-known exterior references to improve interior organization and elevation-specific detail.

## Fresh-reopen evidence

- Blender 5.2.3 LTS freshly reopened the saved file successfully.
- Export collection: `Asset_potter_engineering`, 503 objects; root `(0, 0, 0)`.
- Shell XY dimensions: approximately `58.4515 × 67.4320 m`; shell height: `13.4112 m`.
- Round-4 checks report ten stair-flight meshes, three basement landing objects, one roof opening at the retained S03 core, and no missing external images.
- The roof slab ray checks show the two unsupported S01/S02 positions closed and the S03/4S04 center open. These are center-point checks, not full-perimeter clearance validation.
- Axis-aligned object bounds for the S03 basement landing and lowest flight leave about `0.3425 m` in x. No basement corridor or door is present, so the basement route remains ungrounded.
- The penthouse/membrane render currently available is from round 2 and is stale for the round-4 roof change.
