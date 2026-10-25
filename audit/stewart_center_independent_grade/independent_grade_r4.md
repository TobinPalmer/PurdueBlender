# Stewart Center independent grade — R4

**Score: 8.0/10 — meets the project threshold narrowly.**  
**Asset reviewed:** `modular/buildings/stewart_center.blend`  
**SHA-256:** `a10c5e28e0e90f83352e871c3deda5a747198d2398969f4491c756cf95a72b9a`  
**Fresh Blender reopen:** Blender 5.2.3 LTS; `Asset_stewart_center` contains 2,764 objects (2,752 meshes), 29 materials, no materialless meshes and no missing external images. `AssetRoot_stewart_center` has an identity world transform.

## Scorecard

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and GIS footprint | 1.8/2 | Purdue GIS OBJECTID 615 and the 53-vertex structural trace overlay identify Stewart Center and show the shell following the selected GIS ring. The recorded ring area is 10,197.47 m². This is a useful footprint check, not a surveyed wall line; the project's local geographic conversion is approximate. |
| Placement, scale, and interior layout | 1.5/2 | The standalone root remains at identity and the project origin is retained. The fresh standalone reopen does not inspect the master placement marker. The 2024 floor maps are schematic, with no scale or north arrow; Ringel Gallery and HSSE Library offsets remain approximate. The new cutaway clearly shows the theater, library and gallery contents and labels the layout uncertainty. |
| Floors, height, and roof | 1.0/2 | The central floor count has archival support, but 16.5 m wall height, 22.5 m overall height, the flat roof elevation and rooftop blocks remain estimates. R4 does not materially improve the broad, nearly featureless roof seen in the oblique view. |
| Facade, entrance and distinctive identity | 1.8/2 | R4 makes the six-column portico and three tall glazed entrance bays much more legible, adds larger column capitals, supported continuous stair rails, and modest window/reveal variation. These details fit the supplied Purdue entrance photo better than the R3 view. The multi-story bay treatment is qualitative: the 2024 Purdue Agriculture photo is not georeferenced to a particular face, and the repeated upper windows and extensive roof-side walls remain schematic. |
| Modular integrity and evidence | 1.9/2 | My independent reopen confirms the exact hash, collection, object counts, root transform, material coverage and portable image dependencies. GIS, source photos, floor-map limitations, validation and an interior cutaway are documented. The cutaway is a temporary scene of existing linked modules and does not prove exact room placement or the master marker. |
| **Total** | **8.0/10** | **Passes at the minimum threshold.** |

## Findings

1. R4 resolves several visible R3 problems: the entrance reads as a glazed portal behind the columns, the stone frame is deeper, capitals are more distinct, and the stair rails read continuously. The cutaway makes existing interior spaces reviewable.
2. The flat roof and generic rooftop blocks remain the largest unresolved exterior discrepancy. No measured roof plan or elevations were found, so these should remain explicitly estimated.
3. Keep the three-bay facade interpretation qualified: the contemporary photo supports large, deeply framed glass openings, but does not locate that composition on a specific compass face.
4. The GIS outline does not establish facade wall lines, height or vertical levels. The Road School floor diagrams do not establish scale, north or exact relative placement among the interior modules.
5. This grade covers the standalone R4 asset. The coordinator must separately reopen the master and check `Placement_stewart_center` before marking the building integrated.

## Evidence inspected

- Independent fresh reopen: `independent_reopen_r4.json`, generated from the saved asset in a separate Blender 5.2.3 process.
- Builder record and validation: `REMEDIATION_R4.md`, `building_validation.json`, and `structural_wall_probe.json`.
- Model views: `south_entry_r3.png`, `south_oblique_r3.png`, and `interior_modules_cutaway_r4.png`.
- Source imagery: Purdue University Events Stewart Center entrance snapshot (`source_purdue_entrance.jpg`) and Purdue Agriculture 2024 photo (`source_purdue_ag_entrance_2024.jpeg`). The latter supports qualitative window/stone detail only; its facade orientation was not established.
- GIS: Purdue GIS OBJECTID 615 in `purdue_gis_feature_615.json`, displayed in `footprint_overlay.png`.
- Interior context: Purdue Road School 2024 floor-map snapshot (`roadschool_maps_2024.pdf`); the maps lack a scale and north arrow.

R3's 7.7/10 result remains historical. R4 passes the 8/10 threshold narrowly, with roof geometry and exact interior offsets still unresolved. This review did not edit the building, master, or shared indexes.
