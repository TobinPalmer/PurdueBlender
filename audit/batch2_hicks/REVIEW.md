# Hicks Library evidence — 2026-10-22

Source file: modular/buildings/hicks_library.blend. Export Asset_hicks_library. Backup before.blend. Local frame, building envelope and inherited underground levels preserved; master placement is unchanged.

Sources retrieved 2026-10-22:
- https://schooldesigns.com/Projects/purdue-university-hicks-undergraduate-library/ — publisher AS&U School Designs, architect GMB; built August2013 interior refurbishment, historical not confirmation of2026 layout. Raw HTML schooldesigns.html. Photographs Tony Frederick Photography a and b viewed in browser at https://schooldesigns.com/wp-content/uploads/2019/09/1408asu078a-1.jpg and1408asu078b-1.jpg. Supports offwhite collaborative table tops, green seats, rust lounge seats, timber computer supports, compact computer rows, pendant/ceiling lights and carpet finish. Table dimensions and all furnishing positions are estimates, not measured.
- https://www.google.com/maps/search/Hicks+Undergraduate+Library+Purdue — resolved John W.Hicks Undergraduate Library,40.4245248,-86.9126242, Ground504WStateSt. Map visibly places library south of Stewart and north WState; Maps place pin is not surveyed wall geometry. Header photograph visually shows open collaborative tables with grey chairs, brown carpet and suspended ceiling lights. Photo date unavailable. No dimensions derived from photo; source CRS WGS84 for pin only.
- Existing official GIS reference FID197 inherited; source raw snapshots audit/official_purdue_buildings_wgs84.json and audit/official_building_references.json. No new exterior scale or height claim. Existing basement slab triangulation, skylight shapes and spiral stairs remain unverified.

Changes:
- Added photo-supported study furniture categories: collaborative tables/chairs, bistro counter, computer desks/posts/monitors/keyboard, rust lounge seats and side tables, carpet zones, linear luminaires. Locations and dimensions approximate, clearly tagged per object. Existing wall shell, slabs and atrium were retained.
- Fixed brick node default Scale5 to1 so inherited meter UV220x75mm bricks no longer render44x15mm. Mortar4mm. Existing brick UV mapping uses distance and elevation meters.
- Added procedural meter-coordinate micro bump to upholstery/carpet/maple; no external texture dependencies. Viewport material colors mirror shader values.
- Review cameras/lights live outside export collection. Interior and exterior Cycles shader renders are evidence views, not Workbench.

Limitations: This is a furnished interpretive model. Complete current floor plans, room boundaries, public access stair/elevator connection, exact facade/skylight details and roof/vertical measurements remain unresolved. It cannot honestly qualify as9/10 architectural reconstruction yet. Do not label the historical2013 furniture placement current verified.

Further repair: shader inspection exposed missing triangular regions from inherited ad-hoc triangle fans in roof and Ground slab. Rebuilt both as closed constrained-triangulated slabs, preserving perimeter and intended central opening. Roof180mm thickness is estimated. Before/after source planes unchanged; local origin unchanged. Reopened shader views regenerated.

Final saved source exports250objects including functional computer-desk legs and luminaire suspension cables. Reopened technical.json confirms both repaired slabs have zero nonmanifold edges, no missing external images. Final shader renders regenerated after supports. Independent child review6.6/10; unavailable current plans/vertical measurements prevent9/10.

## R2 refinement — 2026-10-27

Revised the Hicks asset after the prior 6.6/10 review, preserving its source-local coordinate frame, manifest placement, `Building_hicks_library` scene and `Asset_hicks_library` export collection. New geometry is isolated in `HIKS_R2_Sloped_Masonry_Envelope`; interpretive lounge/interior furnishings are isolated in `HIKS_R2_2013_Furnishing_Details`; the cameras and review lights are outside the exported asset in `HIKS_R2_Review`.

- Added a 20-face GIS-perimeter loft for the four sloped masonry apron walls, following official FID 197 plan geometry. The existing brick material’s linked color ramp was neutral grey and made the new walls render pale, so the ramp is now warm red/brown to match the material swatch and official exterior photo. The upper wall contact elevation (2.438 m) follows the supplied GIS roof extrusion attribute; lower ring scale and slope remain estimates from the exterior photo and plaza fit. No measured wall section was found.
- Added an interpreted 2013 lounge composition with divided rust banquette cushions, dark seat pads, circular tripod bistro tables, acoustic screens with supports, standing quick-access computer counters/monitors, and an iDesk. Purdue’s 2013 announcement and renovation photo support the categories/material cues, but not dimensions, exact locations, or current as-built layout.
- Added separated, soft review lighting for the interior. The current interior image is intentionally an evidence view: furniture and atrium are visible, but shadows and uneven brightness remain; it is not a measured lighting study.
- Fresh-open validation read the saved `.blend` in Blender 5.2.3 LTS, confirmed scene/collection names, 343 objects in `Asset_hicks_library`, the 40-vertex/20-face sloped wall mesh nested in the asset collection, and no missing external image dependencies. The validation script rendered both saved exterior/interior evidence views after reopening.
- Frozen asset SHA-256: `3fc4a157b3ee6ce863edcb74155c1463706f75e7b7fb9170e2849b25cde48cf0` (`modular/buildings/hicks_library.blend`). Structured evidence: `evidence_r2.json`; fresh-open output: `fresh_open_validation_r2.json`; fresh-open render views: `fresh_open_exterior.png`, `fresh_open_interior.png`.

The Indiana Commission agenda describes a planned 2026 project to repair/repoint four sloped masonry walls and add metal covers. This is cited as evidence that the four sloped masonry faces exist, not as proof that the planned covers are installed. The Purdue Libraries 2023 master plan is also a proposed-project source; its Hicks partition and basement seating recommendations are not represented as completed construction. Current private floorplans/as-built sections remain unavailable, so basement room/floor topology, exact wall slopes and current furniture positions are uncertain. This iteration is ready for independent grading; it has not yet received a new grade.


## Independent R2 grade and master integration

Independent R2 review passed at 8.5/10 for exact asset SHA `3fc4a157b3ee6ce863edcb74155c1463706f75e7b7fb9170e2849b25cde48cf0`; see `audit/batch2_hicks/independent_grade_r2/result.json`. A fresh-open grader matched the GIS FID 197 shell within 0.00003 m and the sloped masonry upper perimeter within 0.00063 m. Roof and height, lower-wall slope, and exact furniture positions remain estimated. The coordinator refreshed the library link and is validating the master placement.
