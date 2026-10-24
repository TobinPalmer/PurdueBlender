# John T. McCutcheon Residence Hall — R2 Source and Reopen Review

**Updated:** 2026-10-24  
**Asset:** `modular/buildings/mccutcheon_hall.blend`  
**Collection:** `Asset_mccutcheon_hall`  
**Scope:** McCutcheon asset and its dedicated audit folder only. Master, manifest, shared indexes, and root builder were not changed. No commit or push was made.

## R2 changes

- Excluded `MCUT_Official_Footprint_Overlay` from rendered architectural views while keeping it visible in Blender's viewport. The green curve is a diagnostic GIS trace, not a physical outline painted on the building/site. It carries the source FID and source URL as object metadata.
- Replaced the concrete-pavement material on the broad `Site_Lawn_Base` with an embedded procedural green grass surface. Replaced the roof-membrane material on the two site-drive meshes with an embedded procedural dark asphalt surface. This fixes the visibly implausible gray lawn and semantically incorrect road material seen in the earlier hero render. Both new colors and microtexture remain qualitative rather than measured from a calibrated photo.
- Made no changes to the building shell, window count/spacing, entrance/canopy, roof/penthouse, interior, or tree species/positions. No primary measured elevation or direction-identified set of facade photos was found to justify those architectural edits.

## GIS footprint and position evidence

The retained local GIS snapshot is `gis_fid57_snapshot.json`, extracted from the project's official-source snapshot `audit/official_building_references.json` (snapshot date 2026-10-22). Source: Purdue BuildingShapesZip4 FeatureServer layer 0, feature FID 57 (`MCUT`, John T. McCutcheon Residence Hall), https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0.

- Source-layer coordinates are EPSG:4326. The project converted them to metre-like local XY with origin (40.4274° N, 86.9137° W), X east/Y north, and the approximation documented in `modular/AGENTS.md`. This is a local tangent-plane approximation, not survey control.
- The GIS polygon's transformed local bounds relative to the manifest placement origin `[-1215.0, -260.0] m` are X `[-37.798464, 31.556193] m`, Y `[-43.857252, 42.573459] m`. The saved base-plinth object bounds reopen at approximately X `[-37.7985, 31.5562] m`, Y `[-43.8572, 42.5735] m`. The bounding-box edge differences are below 0.0001 m at the recorded precision. This establishes coordinate registration of the model's plinth extent to the GIS envelope; it does not prove the complete structural-wall footprint or certify the source polygon as a survey.
- The GIS minimum-rotated-rectangle dimensions are about `69.054 × 86.093 m`, angle `0.344°` east counterclockwise. Use the polygon rings for shape comparison rather than the rectangle alone.
- The layer records `num_levels_attribute: 10`, but its saved metadata says height is unverified and must not be used as surveyed height. Model elevation, floor spacing, roof shape, and penthouse remain unverified.

## Other sources reviewed

1. **Purdue University Residences, McCutcheon page** — https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html (retrieved 2026-10-24). Officially identifies the hall, states it opened in 1963, describes traditional-style rooms/shared community bathrooms and common study/social spaces, and gives 400 McCutcheon Drive. It supports building identity and use, not exterior dimensions, exact facade, roof, or interior as-built layout. The sample room plan on this site is explicitly approximate and was not used to invent room geometry.
2. **American School & University, “Student slain in Purdue University residence hall”** — https://www.asumag.com/safety-security/article/21252186/student-slain-in-purdue-university-residence-hall (dated 2022-10-05; retrieved 2026-10-24). Identifies McCutcheon Hall, 730 residents, and opening in 1963, with an attached exterior image. Search preview describes red brick, vertical window strips, decorative concrete screens, and a rooftop structure; because no direction-registered facade/elevation or calibrated dimensions are published, those details are treated only as qualitative visual context, not measured instructions.
3. **Purdue Archives finding aids** — https://archives.lib.purdue.edu/repositories/2/archival_objects/5994 and https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf. These list McCutcheon postcard/construction/exterior photo holdings. The records confirm source material exists; the referenced archival images were not available as scanned, direction-identified building elevations in this pass and therefore were not used to infer exact facade geometry.

## Reopen and file validation

Blender 5.2.3 reopened the saved source asset. `mccutcheon_r2_validation.json` records:

- `Asset_mccutcheon_hall` is present with one direct root and 235 objects including children; root translation is zero and scale is one.
- The viewport-visible GIS curve is saved `hide_render=true`, `hide_viewport=false`, with FID 57 metadata.
- Lawn and both drive surfaces reopen with the intended dedicated materials.
- All 10 linked foliage-library image textures are packed. No unresolved unpacked image dependencies were found.
- `mccutcheon_r2_hero.png` rendered from the reopened saved file. It shows the qualitative grass/asphalt surface update and no diagnostic footprint line.

## Remaining uncertainty

The available source evidence verifies the identity and horizontal GIS registration far better than the building's elevations. The model still needs a reliable direction-identified exterior-photo set or measured drawing to confirm the precise window cadence, facade screen locations, entrances on each side, and rooftop forms. GIS story/level metadata and the 30.35 m asset top are not measured height evidence. Interior partitioning and exact circulation are not verified by an as-built plan. The current render's gray background is a presentation/world-lighting issue and was not changed in the standalone building source.

No independent grade is claimed in this source pass; a separate reviewer should evaluate the saved asset and this evidence.
