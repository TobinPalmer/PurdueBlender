# American Railway Building (RAIL)

**Asset:** `modular/buildings/american_railway_building.blend`  
**Export collection:** `Asset_american_railway_building`  
**Library scene:** `Building_american_railway_building`  
**QA date:** 2026-10-23  
**Current self-assessment:** **8.4/10**  
**Independent review:** the latest reported independent score was 8.2/10 before this visual pass; fresh independent review is pending.

## Changes and source grounding

- Replaced the inherited single extrusion with a two-storey architectural asset containing 693 mesh objects, 7,874 vertices, and 5,688 faces. The original nine-vertex GIS footprint and placement origin are retained.
- Tuned the procedural brick mapping to use world X/Z coordinates, keeping the running bond continuous across separately modeled facade bays. Reworked the upper arch heads as segmented voussoirs and retained muted limestone trim, bronze frames, blue-gray glazing, and the entry lettering.
- Added two floor slabs; lower touchdown stations; a round oak teaming table; cafe/lounge seating; an illustrative focus booth; glass screens; a stair and upper landing; and an open upper-floor desk layout. The focus booth is inside the source polygon. Room layout remains illustrative because construction plans were not successfully inspected.
- The official American Structurepoint project photos informed only visible cues: red brick, arched upper and rectangular lower window character, glazed entry, round meeting table, white desks, teal-accent seating, glass partition, and task lamps. Their exact dimensions and room positions were not inferred. Roof form and rooftop equipment remain unverified.
- The exterior render shows the finished facade. The ground and upper plan renders isolate the intended floor and show furniture, glazing, and the stair. The eye-level section hides review-only ceiling discs, booth/partitions, and upper-level components so the ground-floor workspace and stair are unobstructed. Wall cuts are for review only; saved building geometry remains intact.
- The detailed library is localized around the polygon area centroid. The master can position it at **X=83.03792572m, Y=60.04324341m** in the project campus coordinate system (east/north/up, geographic origin 40.4274, -86.9137). The collection stores the origin, local footprint vertices, and source building ID.

## Geometry and QA

| Check | Result |
| --- | --- |
| Saved file reopen | PASS; Blender 5.2.3 opened the exported asset and found the expected collection |
| Export geometry | 693 mesh objects; 7,874 vertices; 5,688 faces; all meshes have materials |
| External image dependencies | 0 unpacked images |
| Focus booth fit | PASS; all 40 vertices across five booth meshes are inside the retained footprint polygon |
| Interior fit | PASS; all 2,916 vertices across 291 interior meshes are inside the retained footprint polygon |
| Brick mapping | PASS; world X/Z mapping is shared across 99 brick meshes |
| Original massing source | Builder restores the original massing library from the saved baseline; SHA-256 is checked against `before.blend` |
| Render inspection | PASS; exterior, ground plan, upper plan, and eye-level cutaway regenerated and inspected |

The footprint area is approximately **142.83 m²**. A 2015 Purdue engineering study reports approximately **2,500 gross square feet**, while the inherited polygon implies roughly **3,074 square feet** across two floors. This study-versus-GIS discrepancy remains unresolved, so the source footprint was retained without rescaling. The **7.6m roof height** is an inherited estimate; the highest modeled point is 7.97m at the low-profile service curb. Neither is a surveyed elevation.

## Rating and remaining evidence limits

The self-rating is **8.4/10**. Compared with the previous visual pass, the facade's large color bands are replaced by readable continuous brick courses, detached upper arches no longer appear in the eye-level cutaway, floor-plan renders no longer show stray pendants above the model, and the cutaway exposes the stair and first-floor arrangement more clearly. This is a self-assessment; the previous independent 8.2/10 score applies to the pre-pass asset, and no independent score has been assigned to this revision.

The asset remains below 9/10 because exact elevations, opening dimensions, roof profile/equipment, room locations, and circulation have not been checked against retrievable construction plans or inspectable aerial imagery. Keep the footprint area discrepancy and estimated heights explicit; do not present this as survey-grade geometry.

## References

- [American Structurepoint — Purdue University American Railway Building Renovations](https://www.structurepoint.com/product-page/purdue-university-american-railway-building-renovations). Accessed 2026-10-23; project publication date not exposed. Supports 1926 origin, two storeys, and the renovation/workspace program. Official project photographs informed visible exterior and interior cues noted above.
- [Purdue OEP — RAIL building emergency plan](https://www.purdue.edu/operations/emergency-preparedness/rail/). Accessed 2026-10-23; revision 2026-03-30. Provides the address and current first-/second-floor use descriptions.
- [Purdue College of Engineering — ME-RAIL-HAMP study (PDF)](https://engineering.purdue.edu/~frosch/Renderings/Masterplans/ME-RAIL-HAMP%20Study.pdf). Accessed 2026-10-23; dated 2015-06-30, revision noted. Search-indexed text reports two storeys and approximately 2,500 gross square feet; plan images were not retrieved.
- [Google Maps — American Railway Building, 500 3rd Street](https://www.google.com/maps/place/American+Railway+Building,+500+3rd+St,+West+Lafayette,+IN+47907/@40.4279,-86.9127,19z/data=!3m1!1e3). Address/location reference only; live satellite imagery was not inspected in this builder session.
- [Purdue Archives — Campus buildings historic database](https://collections.lib.purdue.edu/campus/buildings). Accessed 2026-10-23. Historic building record notes separate 1926–1997 and 1997–present footprints.

## Files

- `modular/buildings/american_railway_building.blend` — detailed local-coordinate building library.
- `modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend` — original massing library.
- `audit/american_railway/verification.json` — machine-readable references, transform, bounds, and validation results.
- `audit/american_railway/rail_exterior_visual_final.png` — latest exterior render.
- `audit/american_railway/rail_interior_ground_visual_final.png` — latest ground-floor plan render.
- `audit/american_railway/rail_interior_upper_visual_final.png` — latest upper-floor plan render.
- `audit/american_railway/rail_interior_eye_level_visual_final.png` — latest eye-level section render (review-only wall cuts).
- `audit/american_railway/build_american_railway.py` — reproducible asset build, renders, and QA.
- `audit/american_railway/before.blend` — source library snapshot used for the build.
