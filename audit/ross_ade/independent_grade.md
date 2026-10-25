# Ross-Ade Stadium — independent grade

**Result: 8.0/10 — passes the 8/10 minimum.**

This grade applies to the saved modular asset at `modular/buildings/ross_ade.blend`. I reopened it read-only in Blender 5.2.3 LTS, checked the manifest, checked its placement instance in the master without saving, and compared the geometry and rendered views with the saved OSM feature and published Purdue sources. The master and building asset were not changed.

## Criterion scores

| Criterion | Score | Evidence and findings |
|---|---:|---|
| Correct identity and source-backed footprint | 1.5/2 | OSM way 614516704 is explicitly Ross-Ade Stadium, operated by Purdue, and its projected outline is close to the asset’s stadium/site envelope. The OSM feature is an outer stadium/site polygon, not a surveyed wall footprint; the model XY bounds run about 3.65% wider and 3.21% longer. The shared GIS target file has no Ross-Ade feature (it contains LWSN, KRAN, KNOY, HIKS, and RAWL). |
| Position, orientation, and scale/dimensions | 2/2 | Manifest origin `(-403.2000, 805.2000)` m; master `Placement_ross_ade` matches at `(-403.2000, 805.2000, 0)`, zero rotation and unit scale, instancing `Asset_ross_ade`. OSM bounding-box center projects to `(-403.1939, 805.2177)` m: offset about 0.006 m east/west and 0.018 m north/south. The field is oriented north–south. |
| Evidence-backed height, floors, and roof form | 1/2 | Reopened geometry spans `z=-0.02` to `49.75` m, including corner floodlights; the pavilion roof is around 36 m. Purdue confirms permanent lights but publishes no measured total height, floor elevations, or section drawing in the sources reviewed. Open bowl and west pavilion form are plausible, with vertical dimensions estimated. |
| Facade, entrances, and distinctive architecture | 1.5/2 | The model contains a brick-faced west pavilion/press box, gates, Tiller Tunnel, south end zone, lights, and south video board. Purdue documents the 2018 brick facade, 2023 south-end addition/Tiller Tunnel, and 2020 video board dimensions of 150 ft 4 in by 56 ft 9 in; the model screen measures 45.82 m by 17.30 m, matching those published dimensions. Rendered bowl surfaces are nearly uniform white and obscure the seat detail; exact gate and facade locations have no source overlay. |
| Modular export, portability, and complete evidence | 2/2 | The saved file opens as scene `Building_ross_ade`, collection `Asset_ross_ade`, with 2,118 objects (2,117 meshes), the expected root at local origin, and no external image paths. The manifest retains the expected file, scene, collection and local-coordinate placement. This audit records source provider, feature ID, retrieval timestamp, CRS, projection, method and uncertainty. |
| **Total** | **8/10** | **Pass** |

## Reopen and geometry checks

- Asset evaluated bounds in local meters: X `[-112.5, 112.5]`, Y `[-152.5, 152.5]`, Z `[-0.02, 49.75]`.
- Evaluated XY bounds: `225 m × 305 m`.
- OSM way 614516704 projects to an outer bounds of `217.07 m × 295.52 m`, centered at `(-403.1939, 805.2177)` m.
- Projection uses the project’s approximate local conversion from WGS 84 / EPSG:4326 coordinates, with origin latitude `40.4274`, longitude `-86.9137`. The OSM feature is suitable for stadium/site identity and placement checks; its polygon is not a surveyed structural footprint.
- The master placement marker is an Empty at `(-403.2000, 805.2000, 0)` m, zero rotation, unit scale, referencing `Asset_ross_ade`.
- No saved geometry, manifest, README, shared index, or master-file changes were made.

## Sources

- [OpenStreetMap way 614516704](https://www.openstreetmap.org/way/614516704), provider OpenStreetMap / Overpass API. Feature extract: `audit/ross_ade/ross_ade_osm_way_614516704.json`; original Overpass response: `ross_ade_stadium.json`; base timestamp `2026-10-22T03:48:50Z`; CRS EPSG:4326. Measured by projecting its nodes with the campus conversion and comparing outer bounds and center. Positional accuracy is not survey-certified.
- [Purdue Athletics Ross-Ade facility page](https://purduesports.com/facilities/ross-ade-stadium), accessed 2026-10-25. Supports current stadium identity and history, brick facade, permanent lighting, south-end renovation, and video-board dimensions; it does not supply a measured height or section drawing.
- [Smoot Construction — Ross Ade Stadium](https://smootconstruction.com/our-work/ross-ade-stadium-purdue-university/), accessed 2026-10-25. Press-box and renovation context; project description, not a dimensioned drawing.
- [Purdue campus map](https://www.purdue.edu/campus-map/graphics/campusmap.pdf), accessed 2026-10-25. Northern-campus location context; not used for dimensions.
- [Purdue Athletics media — Tiller Tunnel](https://www.summitathletics.com/websites/purdue/index.html), accessed 2026-10-25. Promotional rendering used for a visual check of the 2023 south-end addition; not as-built survey evidence.
- [Trevor Mahlmann Ross-Ade aerial photography collection](https://photos.tmahlmann.com/Places/Purdue/Ross-Ade-Stadium), accessed 2026-10-25. Independent aerial imagery used for open-bowl form; selected image predates the 2023 south-end addition.

## Review artifacts

- Three-quarter view: [ross_ade_review_threequarter.png](ross_ade_review_threequarter.png)
- Top view: [ross_ade_review_top.png](ross_ade_review_top.png)
- Machine-readable result and evaluator: [independent_grade.json](independent_grade.json), [evaluate_ross_ade.py](evaluate_ross_ade.py)

