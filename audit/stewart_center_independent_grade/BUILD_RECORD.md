# Stewart Center asset remediation record

## Current asset and validation

- Asset: `modular/buildings/stewart_center.blend`
- Fresh-open SHA-256: `a3d7e9aba5cf2d32aa0aef5d458dfb6225841126c6a43c272bb60011fe310249`
- Export collection: `Asset_stewart_center`; root `AssetRoot_stewart_center` remains at identity/local origin.
- Fresh-open collection: 1,940 objects (1,927 meshes); 0 materialless meshes; 0 missing external image paths.
- Structural shell: 52 perimeter wall objects following a cleaned 53-vertex GIS outline. Local bounds are X `[-74.15335, 64.26501]` m, Y `[-49.96492, 42.05814]` m. GIS transformed bounds agree with those values to under 0.01 m.
- GIS polygon area after the stated local projection: 10,197.47 m².
- Height: 16.5 m wall top and 22.5 m overall remain estimates. Purdue Archives documents three floors in the central part, but no dimensioned elevation or roof plan was found.

## Changes

1. Replaced the eight broad rectangular wall boxes with wall segments following Purdue campus GIS feature OBJECTID 615. Added perimeter-following limestone base/courses, a subdued window rhythm, and a roof polygon bounded by the GIS trace. Window cadence, wall height, roof height, and rooftop plant are visual estimates; they are not survey/elevation measurements.
2. Kept the existing portico, entrance columns, entrance glazing, and broad stair features. Added no mural because available archival material confirms it is above the HSSE Library entrance but does not identify the precise facade/location in a way that can be safely placed from the available views.
3. Compared retained interior modules to the 2024 first-floor map and GIS outline in local coordinates. The prior HSSE module extended outside the GIS outline. Repositioned the HSSE library module to a central envelope zone and the Loeb Theater/FlyLoft module east of it. Preserved module dimensions and object detail. Loeb Theater, HSSE Library, and Ringel Gallery module bounding boxes are now contained by the GIS footprint polygon. These are layout corrections from a schematic map, not survey coordinates.
4. Left the root, manifest origin, master instance marker, and shared files untouched.

## Sources and method

### Purdue campus GIS

- URL: <https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0>
- Provider and feature: Purdue University campus GIS, layer 0, OBJECTID 615, ABBR `STEW`, `Stewart Center`.
- Retrieved: 2026-10-25. Raw response: `purdue_gis_feature_615.json`; service response is stored in EPSG:4326 after the query request (service spatial reference: EPSG:3857).
- Transformation into the existing building-local frame (meters): `X=(longitude + 86.9137) * 84810.60416539927 - 91.04999828338623`; `Y=(latitude - 40.4274) * 111040 + 253.375`. X is east, Y is north. The offsets are the existing manifest placement origin; the `AssetRoot` is not moved.
- Method: transform each ring vertex into the asset frame; remove only sub-0.12 m near-duplicate/collinear noise; construct perimeter wall segments with their outer faces on the GIS trace. GIS geometry is a campus map footprint, not a survey of facade offsets. The project-local conversion and service geometry are approximate and not survey-grade.
- Limits: GIS supports plan location/shape only. It does not establish elevations, facade composition, window spacing, roof configuration, or interior dimensions.

### Floor plan and historic identity

- URL: <https://www.roadschool.purdue.edu/maps/2024%20Stewart%20Center%20Maps.pdf>
- Provider/edition: Purdue Road School, Stewart Center first-, second-, and third-floor maps; 2024 edition; retrieved 2026-10-25. Local evidence snapshot: `roadschool_maps_2024.pdf`, raster pages `roadschool_floor-1.png` through `roadschool_floor-3.png`.
- Method: use the first-floor map's room labels and relative adjacency (Main Entrance, Fowler Hall, Loeb Theater, Humanities/Social Sciences/Education Library, Welcome Center) to check the retained modules. The plan has no scale or north arrow and is not a dimensioned architectural plan. Interior offsets are approximate and are documented as such.

- URL: <https://archives.lib.purdue.edu/agents/corporate_entities/548>
- Provider: Purdue University Archives and Special Collections; retrieved 2026-10-25. Source states construction 1954–1958, that the 1958 addition incorporated the University Library and reconstructed Fowler Hall, and that the central part has three floors. It is not a dimensioned plan/elevation.
- URL: <https://blogs.lib.purdue.edu/news/2017/08/27/from-the-archives-a-beginning/>
- Provider: Purdue Libraries and School of Information Studies, “From the Archives: A Beginning,” published 2017-08-27; retrieved 2026-10-25. Confirms incorporation of the existing University Library and reconstructed Fowler Hall; says the mural is above the entrance to the HSSE Library and was dedicated 1961. This does not safely geolocate the mural to an exterior face in the saved model.

### Exterior reference

- URL: <https://events.purdue.edu/stewart_center>
- Provider: Purdue University Events, current exterior reference; retrieved 2026-10-25. Used to retain/check the stone-framed, columned entrance and broad stair. A single view is not dimensional evidence.
- URL: <https://www.workshoparchitects.com/project/purdue-university-stewart>
- Provider: Workshop Architects; renovation project page, copyright 2022; retrieved 2026-10-25. Used for current interior renovation context only; architectural photography is by Kevin Miyazaki. It is not used to infer building dimensions.

## Evidence files

- `building_validation.json` — fresh-open hash, object count, exact wall bounds, local root, and retained-module bounds.
- `structural_wall_probe.json` — per-object wall mesh bounds from Blender.
- `reopen_probe.json` — fresh open, material and external-image portability checks.
- `footprint_overlay.png` — source GIS outline and retained interior-module bounds in local meters.
- `south_oblique.png`, `north_oblique.png`, `top.png` — fresh review renders. Render light values are temporary and were not saved to the asset.
- `build_stewart_center.py` — dedicated, repeatable shell builder. It is idempotent for generated perimeter elements and applies one-time interior layout corrections tagged on the moved objects.

## Remaining uncertainty / fresh grade request

The prior `INDEPENDENT_GRADE.md` (6.0/10) and `independent_grade_r1.md` (6.9/10) are historical grades, not grades for the current R2 file. See `REMEDIATION_R2.md` for the source-backed entrance revision, retained approximate Ringel/HSSE offsets, and unresolved height/roof uncertainty. Request a fresh independent grade of the newly reopened R2 asset. Do not treat estimated wall/roof heights, roof forms, window spacing, stair/column dimensions, or local module offsets as verified measurements. The master placement marker was not opened or changed in this asset pass.

## R2 entrance update (2026-10-25)

- Source: Purdue University Events Stewart Center page and the entrance photo snapshot `source_purdue_entrance.jpg`; source access and snapshot retrieval date 2026-10-25. The photo supports six pale stone columns, a pediment, glazed entry and broad stairs; it gives no scale or camera calibration.
- Replaced the square front piers/canopy with six round, lightly fluted limestone columns, restrained entablature/pediment, raised landing, eight broad stair risers, handrails, upper glazing and procedural Bedford-limestone grain. Estimated proportions are explicitly identified in the dedicated build script and `REMEDIATION_R2.md`.
- Kept the 53-vertex GIS trace and 52 structural shell segments unchanged. Root and manifest origin are unchanged. Ringel/HSSE offsets remain approximate because the Road School 2024 diagrams are not georeferenced or dimensioned; no relocation was made from diagram orientation alone.
- No separate Fowler Hall/library exterior volumes, mural, or roof equipment were added without source-backed extents/facade location. The Archives supports historic incorporation and three central floors only. Wall and roof heights remain estimates.
- Fresh Blender 5.2.3 reopen: SHA-256 `580f5db01d9d103c0d9bc04f39a5e79b8215dd42fecbf232f2d458aa1fa2af6b`; 1,963 collection objects, 1,951 meshes, 27 material slots/material identities counted, no materialless meshes, no missing external images. See updated `reopen_probe.json`, `building_validation.json`, and `south_entry_r2.png`.

## R3 entrance vestibule and rail correction (2026-10-25)

- Independent R2 grade: 7.3/10. Findings: doors/vestibule were not legible, brick window pattern continued behind the portico, and stair rails looked disconnected.
- Builder now removes the legacy solid entrance backing wall and splits the GIS south-recess edge 33 around a 34 m center opening. It replaces the opening with a recessed two-layer glazed vestibule, side returns, framed double-leaf door sets, and divided transoms. The upper brick wall/window pattern is restored above the entrance. Entry and stair dimensions remain photo-scaled estimates.
- Continuous stair rails now slope from the lower treads to the landing, with nine aligned posts per side. Their dimensions and spacing are estimates.
- Fresh Blender 5.2.3 reopen: SHA-256 `cf2e4c541f98329bf475229d702bc48178078571ba97b1136c9c0c5c9996535d`; 1,966 collection objects, 1,954 meshes, 28 materials; zero materialless meshes and zero missing external images. Structural wall output has 53 objects because the GIS south recess edge is split around the new entry glazing; geographic trace and area are unchanged.
- See `REMEDIATION_R3.md`, updated `building_validation.json`, `reopen_probe.json`, `structural_wall_probe.json`, and fresh `south_entry_r3.png` / `south_oblique_r3.png`. Await a fresh independent R3 score; no new score is asserted.
