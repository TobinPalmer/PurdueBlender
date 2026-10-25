# Stewart Center refinement R2

## Build result

- Asset: `modular/buildings/stewart_center.blend`
- SHA-256 after a fresh Blender reopen: `580f5db01d9d103c0d9bc04f39a5e79b8215dd42fecbf232f2d458aa1fa2af6b`
- Collection: `Asset_stewart_center`, 1,963 objects (1,951 mesh objects)
- Portability check: zero mesh objects without materials; zero missing external image files
- Root: `AssetRoot_stewart_center`, identity transform retained
- GIS shell: same 53 cleaned trace vertices / 52 structural wall segments; area 10,197.4696 m²; shell bounds X[-74.15335, 64.26501], Y[-49.96492, 42.05814] m
- South entry render: `south_entry_r2.png`, rendered from the freshly reopened saved asset. Temporary camera, light, and world settings were not saved to the asset.

## South entrance work

The former four square front piers and flat canopy were replaced by six round, lightly fluted limestone columns, a restrained entablature and shallow pediment, a stone landing, eight broad stair risers, simple metal handrails, and upper glazed panels. Retained entry door/glazing objects were raised to the modeled landing and shifted slightly outward from the back-wall surface. A restrained procedural limestone material adds low-contrast grain without external texture dependencies.

The six-column count, stone-framed portico, entrance glazing, and broad stairs are visible in Purdue's current Stewart Center reference photo. The image supports visual character and count, not metric dimensions. Stair rise, landing height, column diameters/heights, pediment dimensions, and glazing divisions remain approximate visual proportions. No mural was added: archival text locates a mural above the HSSE Library entrance, but no available source in this pass identifies the precise exterior facade plane or surface.

## Ringel Gallery and historic volumes

The 2024 Road School floor maps support program names and broad room adjacency but have no north arrow, scale, or georeferenced control points. No dimensioned/georeferenced interior plan was located in this review. Ringel Gallery and HSSE remain at their existing asset-local placements; no move was inferred from the schematic orientation. Their exact relative/world offsets remain approximate pending a controlled plan or survey.

Purdue Archives supports the historical fact that Stewart Center incorporated the old University Library and reconstructed Fowler Hall. The available archive description does not give their separate external extents or measured facades. Their historical/program identity is retained in the building context, but no unsupported separate external massing was invented. The archive also supports three floors in the central section; the 16.5 m shell wall height and 22.5 m maximum assembled height remain estimates.

## Roof/elevation evidence

No publicly accessible dimensioned roof plan or elevation was found in this pass. The flat shell roof elevation, wall height, overall height, and rooftop forms therefore remain explicit estimates. No new rooftop equipment or clay-tile zone was positioned without a source that identifies its exact roof area.

## Source register and method

1. Purdue University Events, [Stewart Center](https://events.purdue.edu/stewart_center), current page and entrance photograph; accessed 2026-10-25. The image snapshot is `source_purdue_entrance.jpg`; the downloaded image URL is `https://localist-images.azureedge.net/photos/39883225413730/card%402x/60fde77052d4337e4859dae94db6d1ee93e2f421.jpg`. Source depicts six tall pale stone columns, a pediment, glazed entrance, and broad stairs. Image source date and camera calibration are not provided. Used only for qualitative form and count, not dimensions.
2. Purdue University Archives and Special Collections, [Stewart Center corporate entity](https://archives.lib.purdue.edu/agents/corporate_entities/548), accessed 2026-10-25. Describes construction during 1954–1958, incorporation of the University Library and reconstructed Fowler Hall, and three floors in the central portion. No dimensioned elevation or plan.
3. Purdue Libraries, [From the Archives: A Beginning](https://blogs.lib.purdue.edu/news/2017/08/27/from-the-archives-a-beginning/), published 2017-08-27, accessed 2026-10-25. Supports the historical incorporation and states a mural was dedicated above the HSSE Library entrance in 1961; does not resolve the exact facade surface in this model.
4. Purdue Road School, [2024 Stewart Center Maps](https://www.roadschool.purdue.edu/maps/2024%20Stewart%20Center%20Maps.pdf), accessed 2026-10-25; local copy `roadschool_maps_2024.pdf`. Used for room identity and approximate adjacency only. The plan has no north arrow, scale, CRS, or control points, so no metric transform was applied to internal modules.
5. Purdue GIS feature snapshot `purdue_gis_feature_615.json`, OBJECTID 615 / ABBR STEW, remains the shell source. The previously documented local transform and uncertainty are unchanged; no GIS coordinates or root/manifest origin were modified in this pass.

## Reopen validation

`reopen_probe.json` was generated by opening the saved `.blend` in Blender 5.2.3 after the builder completed. It records the hash, object types/counts, root matrix, world bounds, material count, and image-path checks. `building_validation.json` is updated with the R2 result. `independent_grade_r1.md` and its scorecard remain historical; a fresh independent grade is still required for this R2 asset.
