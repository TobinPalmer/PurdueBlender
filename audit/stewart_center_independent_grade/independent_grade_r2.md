# Stewart Center independent grade — R2

**Score: 7.3/10 — below the 8.0/10 pass threshold.**  
**Asset reviewed:** `modular/buildings/stewart_center.blend`  
**SHA-256:** `580f5db01d9d103c0d9bc04f39a5e79b8215dd42fecbf232f2d458aa1fa2af6b`  
**Fresh reopen evidence:** Blender 5.2.3 probe matches this exact hash; `Asset_stewart_center` contains 1,963 objects, including 1,951 meshes. It reports 27 materials, no materialless meshes, and no missing external image paths.

This is an independent review of the R2 asset, not a review of the campus master instance. The prior R1 grade remains historical; R2 improves the south entrance but does not yet meet the project’s pass threshold.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and GIS footprint fidelity | 1.8/2 | Purdue GIS OBJECTID 615 supports the building identity and the 53-vertex/52-segment shell trace. The GIS boundary is a campus-map footprint, not a surveyed facade outline. |
| Placement, orientation, scale, and interior layout | 1.4/2 | The asset root remains at identity and its local frame is consistent with the existing placement origin. The Road School plans lack scale and north arrow; Ringel/HSSE offsets remain explicitly approximate, and the master marker was not independently reopened. |
| Floors, height, and roof form | 1.0/2 | Archival evidence supports three floors in the central portion. Wall height, overall height, roof elevation, and rooftop forms remain estimates. The saved oblique render shows a broad plain roof with conspicuous simple rooftop blocks. |
| Facade, entrances, and distinctive identity | 1.3/2 | The six-column south portico, pediment, landing, and broad stairs are a material improvement over R1. In the saved R2 render the pediment is a plain shallow canopy, the wall/window grid continues behind the columns, a glazed entrance/door is not legible, and stair-rail parts appear as isolated short posts. The complex still reads mostly as repetitive brick-and-window massing; the incorporated library and reconstructed Fowler Hall are not distinguishable. |
| Modular integrity, portability, and evidence quality | 1.8/2 | The exact asset hash was freshly reopened and checked; named collection/root, mesh material coverage, and external-image portability are documented. GIS, floor-map, exterior-photo, and render evidence are saved. The master instance marker and building-specific dimensions remain unverified. |
| **Total** | **7.3/10** | **Does not meet the 8.0/10 pass threshold.** |

## R2 entrance comparison

The Purdue Events reference photograph (`source_purdue_entrance.jpg`) shows six tall pale columns, a substantial stone entrance volume with upper glazing, a pronounced triangular pediment and cornice, and broad stairs with continuous handrails. The R2 render (`south_entry_r2.png`) now has six columns, a pediment-like top, and a wide stair/landing. It still lacks a clearly modeled glazed vestibule and door in the opening; the existing dark window grid remains visible through and behind the portico. The pediment, columns, and handrail detail are considerably more schematic than in the reference. Since the photo has no calibration, this comparison is qualitative, not dimensional.

The oblique render (`south_oblique.png`) also shows the large, nearly featureless roof and simple white rooftop masses. The build record correctly marks these forms and the 16.5 m wall / 22.5 m maximum heights as estimates; they should not be presented as verified architecture.

## Corrections needed to reach a pass

1. Make the entry read as an actual entrance: provide a recessed glazed vestibule and visible doors, remove/replace the brick-window pattern immediately behind the columns, and connect the stair handrails continuously.
2. Refine the portico from multiple exterior photos: stronger column proportions and capitals/fluting, a more convincing stone surround, and a deeper cornice/pediment. Preserve six columns where supported by the photo.
3. Replace the blank roof and generic rooftop blocks only when a source supports their locations and shapes; otherwise keep them clearly identified as low-confidence approximations and avoid giving them a finished appearance.
4. Find reliable photographs/plans that distinguish the historic library and Fowler Hall within the complex. Do not invent their dimensions or extents from the archive description alone.
5. Keep Ringel/HSSE placement qualified until a dimensioned or georeferenced plan resolves the schematic map orientation. Separately reopen the campus master and verify the Stewart placement marker before claiming campus placement is checked.

## Evidence reviewed

- `REMEDIATION_R2.md`, `BUILD_RECORD.md`, `building_validation.json`, and `reopen_probe.json`.
- `source_purdue_entrance.jpg`, `south_entry_r2.png`, `south_oblique.png`, and `footprint_overlay.png`.
- `purdue_gis_feature_615.json` and `roadschool_floor-1.png` through `roadschool_floor-3.png`.

The R2 builder’s own source register records the Purdue GIS feature, Purdue Archives, 2024 Road School maps, and Purdue Events reference with their limitations. I did not infer metric dimensions from the uncalibrated photo or the schematic maps.
