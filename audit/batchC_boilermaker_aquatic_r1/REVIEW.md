# Morgan J. Burke Boilermaker Aquatic Center — R1 Source Review

**Date:** 2026-10-24  
**Asset:** `modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend`  
**Scope:** This asset and the dedicated Aquatic Center R1 evidence folder only. The master, README, manifest, shared scripts/indexes, and other buildings were not edited.

## R1 work

The source model had 565 objects but omitted any opaque exterior wall shell. Its 57 facade panes extended nearly the full 9 m wall height and were nearly transparent, so the saved exterior looked like an all-glass pavilion. The one large competition basin also sat nearly 1.8 m above the deck; its deck slab covered both basins once the water surface was corrected to deck level. Several lane ropes, diving platforms, and seat accents reused the brick material.

R1 made these source-supported corrections:

- Added an opaque, GIS-aligned brick and concrete perimeter envelope. The exposed north elevation is based on a geotagged July 2023 Google Street View panorama showing the brick high-bay hall, a lower glazing band, central entry/canopy, and the building name. The model's 57 separate facade panes were resized into 1.8 m high ribbon windows and changed to reflective blue-gray glazing. Window lengths/divisions and side/rear elevations remain schematic.
- Added a north-facing entry portal, glazed leaves, small canopy, and building-name lettering from the same panorama. The generic threshold/name cue on the opposite end was removed.
- Replaced the full footprint interior slab with seven clipped floor sections surrounding separate basins. The 8-lane, 50 m competition pool is at a plausible 0.19 m waterline above local ground with an estimated 2.2 m basin depth. These dimensions beyond the published pool length/lane count remain schematic.
- Added a separate 6-lane, 26-yard diving well with the documented 17 ft depth (5.1816 m), diving platforms at 1, 3, 5, 7.5 and 10 m, and four springboards. The well's 14 m width and precise location are estimated because no dimensioned as-built plan was available.
- Added the documented 12-person spa at a schematic deck location. Existing spectator tiers remain schematic and are not a measured seating plan; Purdue sources differ between 625 and 700 published seat counts.
- Corrected brick-colored pool hardware and seating accents, added a connected gold material, preserved procedural materials, and added exterior/daylight and interior cutaway review cameras.

## Evidence and limits

**Exterior reference:** Google Street View panorama `y0c6EFsDkT7g2ak3hsZh5A`, image capture July 2023, camera position 40.4289496, -86.9232244, heading approximately 180 degrees. The view distinguishes the brick Aquatic Center hall from the adjoining glazed CoRec. It supports the north-side exterior feature categories and their approximate arrangement, but it does not provide measured dimensions, hidden elevations, or a roof section.

**Purdue facility facts:** The current RecWell fact sheet identifies the Aquatic Center as accessed through the CoRec and lists an 8-lane, 50 m pool, a diving pool with four springboards and five platforms, spa, spectator seating and mezzanine. The RecWell Aquatics page lists a six-lane 26-yard dive pool at 17 ft deep, 1/3/5/7.5/10 m platforms and 625 seats. The older Athletics story reports 700 permanent seats, so the actual capacity is left unresolved and the modeled seating is schematic. No public dimensioned as-built plan was found.

**Footprint:** Purdue BuildingShapesZip4 FeatureServer layer 0, FID 896, abbreviation AQUA, official building name match. Raw response is retained in `../batchC_boilermaker_aquatic_official_footprint.json`. The response geometry is EPSG:4326; the project uses its documented approximate local tangent transform around 40.4274, -86.9137 and centers the GIS bbox at local origin. The new wall envelope bounds match the transformed polygon at `[-30.098, 30.098] × [-51.252, 51.252] m`. This is a GIS alignment check, not survey control.

The GIS record has two official levels and `Extrution=12`, but field units/meaning are not documented by the layer schema. The 12 m wall datum and 12.3 m roof bound are therefore estimates, not measured heights. The existing pitched high-bay roof geometry was preserved because the inspected street view and aerial footprint do not resolve the roof section. The exact interior layout, circulation, locker rooms, lobby/mezzanine organization, platform supports, side/rear fenestration, facade course pattern, and pool/deck widths remain schematic or unverified.

## Reopen and validation

`validation.json` records a fresh reopen and render in Blender 5.2.3. The exported collection remains `Asset_morgan_j_burke_boilermaker_aquatic_center`; the local GIS-centered footprint remains unchanged; all meshes have assigned materials; and there are no external image dependencies. Validation confirms 57 ribbon panels at 1.8 m height, water at deck level, the 17 ft diving basin, and all five platform heights. It generated:

- `aquatic_r1_north_exterior.png`
- `aquatic_r1_interior_cutaway.png` (roof/wall/framing hidden for plan inspection only; those visibility changes were not saved)
- `aquatic_r1_interior_detail.png` (same temporary cutaway presentation)

R1 is ready for an independent full-building review. No self-score is claimed.
