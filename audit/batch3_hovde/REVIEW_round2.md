# Hovde Hall — round 2 building-side update

**Self-review: 7.0/10. Independent round 2 review requested.** The file now addresses the round 1 portico, roof, glazing, and room-scale findings. The model remains an interpretive visualization; room layouts and dimensions are not source-verified. Do not record a 9/10 rating until an independent reviewer confirms it.

## Round 2 changes

- Rebuilt `HOVD_Portico_Pediment_Base` as an extruded limestone triangle with its 13.6 m facade width aligned to the actual local facade axis. The front orthographic render now shows a triangular pediment.
- Retained the six existing column positions, hid the narrow square shaft objects from display/export render, and added six round limestone shafts, bases, and capitals (`HOVD_Classical_Column_1..6`, `HOVD_Column_Base_1..6`, `HOVD_Column_Capital_1..6`). The independent reference supports six substantial columns; exact profile/diameter remains estimated.
- Changed `Hovde_Roof_Membrane` to a matte red clay-tile color and added 32 broad tile-course hints (`HOVD_Roof_TileHint_*`). This is supported by the campus master-plan material description in SAH Archipedia and the Hovde exterior photo, but the roofing system has not been verified from a dimensioned or roof-specific Hovde source. The roof remains modeled as a flat slab; its silhouette is unresolved.
- Changed `Solar_Ribbon_Glass` to blue-gray reflective glazing so window openings read as glass in the exterior image. Separate muntins/sash geometry is still minimal.
- Scaled the office and boardroom room/furniture groups to 72% around their original room centers to reduce the empty floor area. Scaled the separately named boardroom chairs and guest chairs with the groups.
- Added full-height plaster interior wall segments, open door gaps, headers and door leaves around the presidential office and trustees' boardroom. The room cutaway renders omit selected walls/ceilings so reviewers can read the layouts; the visible source-faithful room shapes and circulation remain unverified estimates. Furniture remains illustrative.
- The existing `HOVD_Root` transform, asset collection, scene, entrance correction and master placement marker were not edited. No master, manifest or shared status file was touched.

## Evidence after save/reopen

The saved canonical file reopened in Blender 5.2.3. `final_asset_check.json` records scene `Building_hovde_hall`, export collection `Asset_hovde_hall`, 702 objects / 690 mesh objects, no unmaterialed meshes, and the unchanged internal root scale `[1,1,1]`. The root's internal location remains `[-62.85,93,0]`, z rotation `0.689754 rad`; this is not the campus marker. `final_check_round2.log` records successful reopen and exit.

- `exterior_round2.png` — front facade, six-column entry, triangular pediment, visible glazing and roof color.
- `presidential_office_round2.png` — scaled office furniture/floor section; walls/ceiling are selectively hidden to reveal the desk and guest seating.
- `trustees_boardroom_round2.png` — board table and chair layout; walls/ceiling are selectively hidden.
- `round2_edit.py`, `round2_parent_fix.py`, `round2_refine.py`, `round2_scale_seating.py`, and `render_interior_round2.py` preserve the edit/evidence procedure.

## Sources / limits

- [Wikimedia Commons: Julian Herzog Hovde Hall exterior, photo dated 2016-09-18 and geotagged 40.428660,-86.913958](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg) supports the portico silhouette and facade appearance; it is a perspective photograph, not a measured elevation.
- [SAH Archipedia, Elliott Hall / campus design context](https://sah-archipedia.org/buildings/IN-01-157-0079), checked 2026-10-23, describes the Hovde-era campus palette as red brick, Indiana limestone and a red clay tile roof. That passage gives useful campus-context support for the color/material choice, not a Hovde roof survey.
- [Purdue Archives, Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573), checked 2026-10-23, supports the historic four-story administration building and trustees' room/office functions; it does not establish this reconstructed interior arrangement.
- Footprint/placement remain tied to Purdue public GIS feature 618, WGS84 source snapshot retrieved 2026-10-22 at `audit/official_purdue_buildings_wgs84.json`; current marker: `[-49.8026928902,78.2442455292]`. This building-side pass did not generate a fresh master/footprint overlay, and root must certify master placement.
- The historic 70×230 ft description is broad context, not a surveyed current elevation. Penthouse height, exact roof structure, room geometry, facade details, stair dimensions and all furniture layouts remain estimates.

**Independent reviewer:** please assess the three round 2 renders and inspect the saved `.blend`, especially pediment orientation, column scale, roof treatment, room enclosure and alignment with the Hovde shell. A high rating should wait until the room layout and roof silhouette are accepted or improved.
