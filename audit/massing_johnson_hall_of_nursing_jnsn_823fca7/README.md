# Johnson Hall of Nursing (JNSN)

Stable ID: `massing_johnson_hall_of_nursing_jnsn_823fca7`  
Owner: Rossen  
Asset: `modular/buildings/massing_johnson_hall_of_nursing_jnsn_823fca7.blend`  
GIS identity: Purdue BuildingShapesZip4 FID 218, `JNSN`, Helen R. Johnson Hall Of Nursing.

## r2 evidence-backed build checkpoint

The former asset was a generic box-like shell about 42.74 × 43.41 × 16 m with a footprint close to, but not matching, the Purdue FID 218 ring. The rebuild uses the twelve unique FID 218 source vertices in the documented project local campus approximation, preserves campus-coordinate placement, and uses the manifest collection/scene IDs. The object remains a single joined mesh in the named asset collection.

A 3-level shell is built to the 8.135 m median main-roof height measured from the official 2018 Tippecanoe 3DEP LiDAR COPC. The central estimate uses 2,497 class-1 surface returns inside a 3 m eroded FID 218 footprint, relative to median class-2 ground returns in a 5 m exterior buffer; interior p95 is 8.181 m. This tile has no class-6 building returns, so class 1 is described as surface returns. Three levels are reported by Purdue GIS; floor spacing (2.712 m) is derived from height/levels, not measured. The GIS `Extrution=24` remains unused because its units are undocumented. Indiana's 2018 orthophoto supports a broad flat roof with small raised objects. No archival facade image/elevation is digitized online; the 2007 panorama is used as secondary corroboration only. Facade iteration: Purdue's official historic database for JNSN lists brick as a material and supplies no image. An identity-matched September 2007 Google Street View panorama (pano A9uia6rcKZF_CDi5NSntjQ) corroborates an upper horizontal window ribbon on the visible southwest-facing long wall. The view is tree-obstructed and does not establish lower-story openings or the entrance. The model therefore uses brick, a single ribbon only on that side, and omits the previously inferred entrance, canopy, limestone trim, and unsupported openings on other sides. The eight rendered panes are an explicitly approximate visual subdivision, not a measured count or dimension. Purdue Archives catalogs additional Johnson Hall slides in UA 149, Box 2, Folder 5 (1984–2000), but they are not digitized in the public record.

## Footprint assessment

The Purdue response contains one closed ring with 13 coordinates (12 unique vertices); local shoelace area is 984.01 m². The stored GIS `Shape__Area=1701.02` conflicts with the ring geometry. OpenStreetMap way 117146488 (`Johnson Hall of Nursing (JNSN)`, address number 502) independently gives 1005.86 m² and a boundary Hausdorff difference of 0.876 m from the Purdue ring. This close outline corroborates use of the Purdue vertices; the `Shape__Area` value is treated as inconsistent and is not used to scale the shell.

Purdue's graduate handbook and historical timeline say the original Nursing and Allied Health building was ready for occupancy/completed in 1977 and renamed for Helen R. Johnson in 1991. A 2023 project authorization proposed demolishing it for the replacement Nursing and Pharmacy Education Building. This asset represents the legacy JNSN / FID 218 identity, not the new Darr-Chaney facility; demolition completion at the current date is not asserted.

## Validation and renders

- `review/reopen_validation.json` records a direct Blender reopen, source-ring match, source-backed brick material, facade feature scope, and omitted unsupported entrance/trim.
- `sources/jnsn_lidar_height_measurement.json` records the height statistic, filters, units, and caveats; `review/measure_lidar_height.py` documents the reproducible point-cloud calculation.
- `sources/indiana_2018_ortho_jnsn_bbox.jpg` is the official overhead image used to inspect roof form. It does not support facade claims.
- `renders/johnson_hall_nursing_exterior_preview.png` shows the source-footprint massing and supported facade feature.
- `renders/johnson_hall_nursing_plan_preview.png` shows the plan silhouette/orientation.
- `renders/johnson_hall_nursing_southwest_facade.png` shows the single panorama-matched upper-story ribbon; it contains no inferred entrance.
- `sources/purdue_historic_building_record_jnsn.html` is a raw snapshot of the Purdue Archives building record supporting brick.
- `source_record.json` and `sources/source_catalog.json` document the official material record, archive lead, Street View pano identity/date, observation, and limitations.

The lower facade, entrance, hidden walls, and precise window bay dimensions remain unverified and are not modeled.

