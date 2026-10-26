# Independent WALC grade

**Result: 6.8/10 — below the 8/10 integration threshold.**

Reviewed 2026-10-25 after independently reopening modular/buildings/walc.blend in Blender 5.2.3. No asset, master blend, manifest, README or shared files were changed. Evidence is limited to audit/walc_refine/.

| Category | Score | Finding |
|---|---:|---|
| Identity and plan footprint | 2.0/2.0 | Exported roof footprint agrees with cached Purdue GIS ring to about 0.000002 m; this is trace consistency, not survey accuracy. |
| Local frame and structure | 0.8/1.0 | AssetRoot_walc has identity transform; manifest origin is [28.9300041, -1.2199936]. Master placement marker was not checked. |
| Exterior architecture | 1.0/2.0 | Irregular overall massing is present, but facade is simplified into repeated dark ribbon glazing and broad red-brown bands. Window bays, masonry piers, entry depth and plaza details do not match the articulation visible in Purdue photos. Roof shape and elevations remain estimates. |
| Materials and finish | 0.7/1.5 | 24 used materials, no materialless meshes, and one packed artwork image. Dominant surfaces appear as flat colors with little brick, stone, glass or paving detail. Linked foliage library has an absolute machine-specific path. |
| Interior and program | 1.4/2.0 | Substantial content exists: atrium, bridges/stairs, stacks, active-learning/classroom tables, theatre seating and basement. Layouts and finishes remain simplified and unverified against plans/current photos; several inspection views are dark. |
| Reopenability and evidence | 0.9/1.5 | Clean standalone reopen: 950 objects, 878 meshes, no missing image files. No independent master placement check, validated elevations/roof survey, or authoritative floor-plan comparison. |
| **Total** | **6.8/10** | **Below threshold.** |

## Prioritized changes

1. Match facade bays, entrance, brick/limestone boundaries and roof edge to official Purdue photos; add vertical mullions/reveals and surface variation without inventing unsupported details.
2. Validate wall/roof elevations and roof form using authoritative drawings or measured references. Existing 16.7 m wall and 17 m roof levels are estimates.
3. Verify floor heights, atrium/bridge/stair arrangement, second-floor stacks, classrooms, theatre and basement against Purdue plan/room information. Label unknown areas schematic.
4. Improve brick, limestone, glazing, metal, floor and paving materials; review a properly lit material render.
5. Reopen the master and verify Placement_walc plus neighboring road/plaza overlaps. Make the linked foliage library portable and repeat the clean reopen.

## References

- [Purdue WALC emergency plan](https://www.purdue.edu/operations/emergency-preparedness/walc/) (revision 2026-04-03; four floors including one basement, program overview).
- [Purdue Chemistry building overview](https://www.chem.purdue.edu/media/news/2017/wilmeth.html) (2017; 164,000 sq ft, 27 classrooms, flexible classroom details and photos).
- [Purdue Libraries open-house photographs](https://blogs.lib.purdue.edu/news/2017/05/17/libraries-host-big-ten-academic-alliance-library-conference/).
- [Purdue campus GIS BuildingShapesZip4 layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0); cached project snapshot audit/official_building_references.json retrieved 2026-10-22. Comparison is against the cached ring, not surveyed truth.

Inspection renders: southwest.png, southeast.png, north.png, roof.png, 03_reading_room_reference.png through 09_basement.png. They are inspection images, not source evidence. Full reopen evidence, including SHA-256, Blender version, collection/material counts, bounds, root transform and GIS residual, is in independent_reopen.json. Inspected asset SHA-256: 0c9024dc0b41d8759666958837263921a7977e1042171c7fd774baa068fb3ba4.
