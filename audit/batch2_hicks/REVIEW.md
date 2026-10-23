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
