# Windsor Halls R4 independent grade

**Result: 8.1/10 — passes the 8.0 finish gate.** This review applies to `modular/buildings/massing_windsor_halls_80aeb51.blend` at SHA-256 `c6dd5a4fa121afa0619e545de29717ab759396396654c16075ebbd7899bdd1a9` only.

## Independent file and footprint checks

I opened the asset in a fresh Blender 5.2.3 process and inspected its scene, collection, meshes, materials, linked libraries, and external image dependencies. The expected scene and collection opened with 196 objects and 195 meshes. No linked libraries or unpacked external images were found. The probe is saved in [fresh_open_probe.json](fresh_open_probe.json).

I independently extracted the four structural-shell rings from that reopened file and compared them to the raw project GIS GeoJSON for FIDs 63–66 using the documented local projection and placement origin. The four IoU scores range from **0.999999845 to 0.999999950**; the largest boundary Hausdorff error is **0.000003793 m**. The per-feature results are in [gis_comparison.json](gis_comparison.json). This validates the horizontal wall footprints; it does not validate heights or roofs.

## Weighted score

| Criterion | Score | Weight |
| --- | ---: | ---: |
| GIS identity, shell footprint, and position | 9.9/10 | 20% |
| Separate shells and component relationships | 9.5/10 | 10% |
| Roof silhouette | 6.8/10 | 20% |
| Hall-specific facades | 7.4/10 | 15% |
| Entrances | 7.0/10 | 10% |
| Materials and textures | 8.2/10 | 10% |
| Schematic interiors | 7.2/10 | 10% |
| Reopen and portability | 10.0/10 | 2.5% |
| Evidence and uncertainty disclosure | 9.5/10 | 2.5% |

Weighted total: **8.1275/10**, reported as **8.1/10**.

## Findings

R4 makes enough progress on the earlier weak areas to pass. Warren, Wood, and Vawter now have more distinct roof relief and the entry accents show more clearly; the Dining Court interior preview is legible. The texture palette separates the red-brown brick, pale masonry courses, dark windows, and slate-like roofs. Wood's central bay is distinct from Warren and Vawter. The four source GIS shell rings match at centimeter-micrometer scale under the documented projection.

The roofs still read as broad, smooth caps in the close frontage views. Warren and Vawter retain similar window grids and restrained entrance forms, and Wood's pale central gable remains oversimplified. These are meaningful refinement opportunities, but their exact geometry is not supported by surveyed elevations; conservative modeling and clearly stated uncertainty are appropriate. The interior layouts are readable schematic slices rather than measured plans. FID 66's vertical connection below the halls remains uncertain, and the asset correctly keeps its source XY footprint separate.

The current Purdue Housing page says Windsor comprises five connected buildings and places the Dining Court underneath Warren and Vawter. This asset represents the four source features FIDs 63–66; adjacent Shealy and Duhme remain separate assets. Purdue's current emergency plans identify Warren and Vawter as four-story buildings, but provide no surveyed heights or roof geometry. The architect's Wood Hall project page provides relevant exterior imagery and confirms the renovation context, but does not provide calibrated elevations. Source URLs and their scoped uses are recorded in [result.json](result.json).

The pass is for this exact frozen asset hash. The master integration still needs its own marker, relative library-path, bounds, and fresh-open verification.
