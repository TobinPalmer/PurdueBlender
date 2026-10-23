# Hovde Hall — batch 3, round 1 review

**Current self-review: 6.5/10.** This is a building-side review, not an independent reviewer score. The facade materials and preview rendering are now legible and source-informed. The file still has significant unverified dimensions and interior layout, so it is not a 9/10 result.

## Changes made in this pass

- Updated the existing `Purdue_Red_Brick` material with a procedural brick-and-mortar pattern using 0.21 m brick width and 0.065 m course height. The shader selects an X/Z, Y/Z, or X/Y projection from each face normal so vertical facades get horizontal masonry courses. It is aligned in the asset's world-position frame; color and roughness are representative, not calibrated from a color chart.
- Added subtle, world-position-aligned noise and shallow bump to `Bedford_Indiana_Limestone`.
- Synchronized the solid-view diffuse color to the Principled base color for the other 23 existing material datablocks. This makes interior woods, carpet, glass, metals, stone, and roof membrane show their authored colors in the project's Workbench previews.
- Kept the prior east-side entrance correction: the portico/doors/stairs and site furnishings remain at the east long-side projection; the former south-end door infill remains. No object geometry, transform, collection, or campus placement was changed in this pass.

## Saved-file checks

`modular/buildings/hovde_hall.blend` reopened after every material save. The exported collection remains `Asset_hovde_hall` with 638 objects (626 mesh objects). All 626 meshes have at least one material; the asset scene is still `Building_hovde_hall`. Root transform and asset bounds are recorded in `final_asset_check.json`. The master placement marker and manifest were not edited.

The updated renders were produced from the reopened saved asset:

- `exterior_material_preview.png` — four-story red-brick facade, pale stone bands, east entrance, and current roof massing.
- `presidential_office_cutaway.png` — existing modeled office, shown with its ceiling hidden.
- `trustees_boardroom_cutaway.png` — existing modeled boardroom, shown with its ceiling hidden.

## Evidence and limits

| Evidence | What it supports | Limits |
|---|---|---|
| Purdue public BuildingShapesZip4 GIS, feature 618, [service layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0); retrieved 2026-10-22; source CRS EPSG:4326; raw snapshot `audit/official_purdue_buildings_wgs84.json` | Hovde footprint identity and prior east-side entrance projection correction | Source date and survey accuracy are not provided; it does not verify height, facade detail, or interior. The previous conversion used the project local approximation (origin 40.4274 N, 86.9137 W; X 84810.6041654 m/degree, Y 111040 m/degree). |
| Purdue Archives, [Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573); checked 2026-10-23 | Four stories; stated historic dimensions 70 × 230 ft; original administrative functions included a Board of Trustees room and several offices | Historic description, not a measured current plan or dimensioned floor drawing. |
| Purdue Campus Facilities and Buildings Historic Database, [Hovde entry](https://collections.lib.purdue.edu/campus/buildings/132); checked 2026-10-23 | Campus construction/history context | No usable room plan or surveyed height was found in the public record used here. |
| SAH Archipedia, [Elliott Hall / campus design context](https://sah-archipedia.org/buildings/IN-01-157-0079); checked 2026-10-23 | Red brick, Indiana limestone, and red-clay-roof material vocabulary used in this campus group | The passage describes the campus design context around Elliott and Hovde; it is not a Hovde roof survey. The existing roof membrane geometry/color was left unchanged pending a Hovde-specific roof reference. |
| Julian Herzog, [Hovde exterior photo file page](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg); photo dated 2016-09-18; geotag 40.428660, -86.913958; checked 2026-10-23 | Exterior appearance/context reference | Perspective photo; no dimensions or interior views. |
| [Google Maps Hovde place search](https://www.google.com/maps/search/Hovde+Hall+Purdue); reviewed in the WALC-neighborhood pass | Campus location and neighboring-building context | Map/place locator only; it does not establish exact building dimensions. |

## Unresolved items for independent reviewer

- Hovde is described historically as four stories and 70 × 230 ft (about 21.3 × 70.1 m). The asset's wall and roof elevations are estimated; the penthouse reaches 19.25 m. No measured vertical source was used.
- The exported modeled office and Board of Trustees floors each have a current axis-aligned extent of about 26.1 × 26.0 m; their rotation and true plan shape should be assessed against the shell before treating them as credible rooms. Their furniture and room finishes are illustrative. Historical records establish the room types, not these exact arrangements.
- The rotunda, stair runs, furniture, ceiling details, door positions, and circulation are not verified against an archival Hovde plan or interior photograph. Keep them labeled as reconstruction estimates.
- The east-side entrance is a previous evidence-based repair; the older correction record is `audit/walc_north/hovde_correction.json`. Current review reconfirms it was preserved, but I did not move or re-register it.
- The roof surface remains the inherited dark membrane. Campus-context prose mentions red clay tile but does not resolve the Hovde roof's present assembly; a direct, roof-visible Hovde reference is needed before changing it.

**Independent review readiness:** ready. Please review the three renders and confirm the measured AABB caveat above. Current Hovde asset file: `modular/buildings/hovde_hall.blend`.
