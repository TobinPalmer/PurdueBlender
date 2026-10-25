# Stewart Center refinement R4

## Saved asset and fresh reopen

- Asset: `modular/buildings/stewart_center.blend`
- SHA-256: `a10c5e28e0e90f83352e871c3deda5a747198d2398969f4491c756cf95a72b9a`
- Blender 5.2.3 fresh reopen: 2,764 collection objects / 2,752 meshes / 29 materials.
- Reopen checks: zero materialless meshes, zero missing external image paths, no collection-instance duplicates, identity `AssetRoot_stewart_center` retained.
- GIS shell: 53 structural wall objects after splitting the south recess around the vestibule; local bounds and the 53-vertex/10,197.4696 m² GIS outline remain unchanged.
- The wall height of 16.5 m, maximum assembly height of 22.5 m, roof/equipment forms, and interior module offsets remain explicitly estimated or approximate. No master file or placement marker was changed.

## R4 improvements

The south entrance portal now reads as three tall glazed bays inside a continuous limestone surround. Each bay has full-height stone jambs, a heavy lintel and base, multi-level glass, and framed double-leaf doors. The six-column portico has slimmer shafts, stronger fluted transitions, larger capitals and clear square abaci. The stair rails remain continuous from the lower treads through the landing, and posts meet the rail while resting on the stair profile.

Facade windows outside the portal now vary modestly in width and height by row, use alternating blue-green glazing, and have consistent thin limestone jambs, heads and projecting sills. The central portal replaces the uniform dark window pattern immediately behind the columns. The frame and window dimensions are qualitative visual estimates, not measurements.

## Source evidence and limits

1. Purdue Agriculture, [Moving at the speed of technology: Purdue to host the 2025 Pest Management Conference](https://ag.purdue.edu/news/2024/11/moving-at-the-speed-of-technology-purdue-to-host-the-2025-pest-management-conference.html), published November 2024; accessed 2026-10-25. The local image snapshot is `source_purdue_ag_entrance_2024.jpeg` (image URL: `https://ag.purdue.edu/news/2024/11/_media/stewartcenter.jpeg`). It shows Stewart Center brick wall, three deep limestone surrounds, large multi-story divided glazing and lower glazed doors. The image does not identify the facade's compass side or provide scale; it is used for material and qualitative opening variation only.
2. Purdue University Events, [Stewart Center](https://events.purdue.edu/stewart_center), entrance photo snapshot `source_purdue_entrance.jpg`; accessed 2026-10-25. It supports the six pale stone columns, pediment and broad stair, not dimensions.
3. Purdue GIS feature OBJECTID 615, WKID/EPSG:4326, local snapshot `purdue_gis_feature_615.json`; the previously documented local transform and 53-vertex shell are unchanged.
4. Purdue Road School, [2024 Stewart Center Maps](https://www.roadschool.purdue.edu/maps/2024%20Stewart%20Center%20Maps.pdf), local snapshot `roadschool_maps_2024.pdf`; accessed 2026-10-25. It has no north arrow, scale, CRS or registration points. No Ringel/HSSE offsets were changed or inferred as exact.
5. Purdue Archives, [Stewart Center](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1343/), accessed 2026-10-25. This undated item is catalogued as an interior photograph, so it was not used as facade evidence.

Because the contemporary facade photo is not georeferenced, the R4 window variation and three-bay portal treatment are reported as source-informed interpretation rather than a verified assignment to a specific compass facade. Heights, roof and equipment remain unverified estimates.

## Interior cutaway

`interior_modules_cutaway_r4.png` is a temporary-scene render of the existing Loeb Theater, HSSE Library and Ringel Gallery modules. The temporary scene links only those modules and hides the exterior shell and roof; it is not saved into the asset. The view demonstrates existing interiors and relative local arrangement, not surveyed placement. The 2024 floor maps are schematic and do not establish scale or north, so internal relative offsets remain approximate.

## Validation and grade status

- `reopen_probe.json` records the exact fresh-open hash, object counts/types, root matrix, material coverage and external-image portability.
- `structural_wall_probe.json` records current GIS wall object bounds.
- `building_validation.json` contains R4 hash, count, wall, source and uncertainty fields.
- `south_entry_r3.png` and `south_oblique_r3.png` are fresh renders of the R4 asset; the filenames are retained for compatibility with the R3 render workflow.
- `render_interior_cutaway_r4.py` generates the cutaway from existing modules without modifying the saved asset.
- The independent R3 grade was 7.7/10. A fresh independent R4 grade is pending; no R4 score is claimed.
