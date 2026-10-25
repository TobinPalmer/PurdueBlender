# Stewart Center independent grade — R3

**Score: 7.7/10 — below the 8.0/10 pass threshold.**  
**Asset reviewed:** `modular/buildings/stewart_center.blend`  
**SHA-256:** `cf2e4c541f98329bf475229d702bc48178078571ba97b1136c9c0c5c9996535d`  
**Fresh Blender reopen:** Blender 5.2.3; `Asset_stewart_center` contains 1,966 objects (1,954 meshes), 28 materials, no materialless meshes, and no missing external images. The root matrix is identity.

This review is independent of the R3 builder. It assesses the standalone building asset. It does not verify the master placement marker.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and GIS footprint fidelity | 1.8/2 | Purdue GIS OBJECTID 615 identifies Stewart Center. The rendered footprint overlay shows the 53-vertex shell trace following the source ring, and the saved validation records a 10,197.47 m² transformed area. The trace is a campus GIS footprint, not a surveyed facade wall line; the metric local conversion is approximate. |
| Placement, orientation, scale, and interior layout | 1.4/2 | `AssetRoot_stewart_center` reopens at identity and the established manifest origin is retained. The 2024 Road School diagrams support broad room adjacencies, and the module bounding boxes are inside the GIS outline. Those diagrams have no scale or north arrow; the Ringel/HSSE relative offset and module placement remain approximate. The master marker was not independently reopened. |
| Floors, height, and roof form | 1.0/2 | Purdue Archives supports three floors in the central portion. Wall height (16.5 m), overall height (22.5 m), roof elevation, and rooftop objects remain estimates. The oblique render still shows a large, nearly featureless flat roof with a few generic raised blocks; no dimensioned elevation or roof source supports these forms. |
| Facade, entrances, and distinctive identity | 1.7/2 | R3 resolves the main R2 issue: the entrance now reads as a recessed glazed vestibule with visible door sets behind the six-column portico, and the brick/window backdrop is restored above it. However, the front view still looks schematic beside the Purdue photo: the central stone/glass composition and column detailing are simplified, the upper facade repeats small dark windows, the pediment is a broad shallow triangle, and the stair rails/posts still read awkwardly from the front. Brick and glass are recognizable but flat/repetitive. |
| Modular integrity, portability, and evidence quality | 1.8/2 | My fresh reopen matches the requested asset hash, collection, object counts, identity root, material coverage, and image portability. GIS data, exterior photo, floor-map snapshots, uncertainty notes, and renders are preserved. No R3 cutaway/interior render was supplied, so this review cannot validate room-by-room interior quality; exact interior offsets remain unverified. |
| **Total** | **7.7/10** | **Does not meet the 8.0/10 pass threshold.** |

## R3 visual comparison

Compared `south_entry_r3.png` and `south_oblique_r3.png` with the saved Purdue Events exterior reference `source_purdue_entrance.jpg`. The R3 vestibule, divided glazing, visible door frames, six columns, and restored masonry above the entry materially improve the earlier doorway hole/window-grid problem. The entrance source is an uncalibrated single photograph, so the modeled 34 m opening and other proportions are not measured. From the saved front render, the stair rail reads mainly as separate short posts along the treads; the continuous sloped rail is not clearly legible at this camera angle.

The oblique and top renders show a generic full roof plane and large plain rooftop blocks. This is an unresolved visual accuracy issue even though the build record correctly labels roof equipment and elevations as estimates. I did not infer height from the GIS outline or treat an estimated 3D form as verified.

## Corrections needed before a pass

1. Refine the portal against additional current photographs: improve the multi-story stone/glass surround, column capitals/proportions, and the transition to the flanking brick wings without claiming photo-scaled dimensions are surveyed.
2. Make continuous stair handrails visually clear from both frontal and oblique views, with the supports attached to the rails and landing rather than reading as isolated tread posts.
3. Add facade material depth and opening variation visible in source imagery; reduce the repeated near-black window rhythm and flat appearance while retaining uncertainty where a source does not resolve a detail.
4. Find roof/elevation evidence or visibly qualify the roof and rooftop masses as low-confidence placeholders. Do not claim the current roof profile or 16.5/22.5 m heights are measured.
5. Provide a cutaway review render for the existing interior modules. Keep the Road School map limitations explicit and do not present approximate module offsets as georeferenced.
6. In a later coordinator integration pass, reopen the master and separately verify its Stewart placement marker; that check is outside this standalone grade.

## Evidence reviewed

- Independent fresh reopen: `independent_reopen_r3.json`, generated by `independent_reopen_r3.py` from the exact asset saved above.
- Builder validation and source record: `building_validation.json`, `structural_wall_probe.json`, and `REMEDIATION_R3.md`.
- Visuals: `south_entry_r3.png`, `south_oblique_r3.png`, `north_oblique.png`, `top.png`, `footprint_overlay.png`, and `source_purdue_entrance.jpg`.
- Plan sources: `roadschool_maps_2024.pdf` and its floor snapshots. The plan is schematic and lacks scale/north arrow.
- Purdue GIS feature OBJECTID 615 and Purdue Archives source are cited in `REMEDIATION_R3.md`.

R2's 7.3/10 review remains historical. R3 improves the entrance but does not meet the project pass threshold. The coordinator should hold this asset out of the finished list and master integration until another independent review reaches at least 8.0/10.
