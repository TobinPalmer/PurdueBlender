# South Hall R2 independent review

**Score: 8.2/10 — meets the 8.0 asset review threshold.**  
**Asset reviewed:** `modular/buildings/south_hall.blend`  
**SHA-256:** `89fbdcf4959174fc91f9477822084de73b38149cfda55cb6ad17348a9289ed06`  
**Fresh reopen:** Blender 5.2.3 LTS; 25 collection objects, 24 meshes, 29 materials; identity root; no materialless meshes or external image dependencies.

## Scorecard

| Criterion | Score | Assessment |
|---|---:|---|
| Identity, footprint, and local frame | 1.9/2.0 | The GIS FID 528 outline and reopened base mesh agree to about 2.24 µm, and the root transform is identity. This is a strong transformation check against the same polygon, not independent verification of the exterior wall survey or master campus marker. |
| Vertical massing, connector, and roof | 1.45/2.0 | Eight-level residential massing and the low north dining/link arm are clearer and follow Purdue's broad site-plan distinction. The actual split, connector endpoint, absolute height, floor-to-floor dimensions, and roof construction remain estimates or unverified. Roof seams are restrained but the large flat roof still reads as a simple plane. |
| Facade, entrance, and materials | 1.55/2.0 | Brick, framed windows, glazed lower level, and the new multistory glazed corner provide a more recognizable, source-informed South Hall facade. Window widths now vary, although the elevation still reads as regular repeated modules. The construction reference shows an exposed/recessed multilevel atrium with visible balcony structure; the model represents it as a simpler glazed bay, and its exact location on the footprint is not georegistered. |
| Interior and amenities | 1.0/1.5 | R2 corrects the prior disconnected-sample problem by linking entry, lobby/dining, and game/lounge diagram zones with continuous paths. The path and carpets are now constrained to the GIS envelope (0.000 m² residual area outside). The cutaway remains a diagram: large blank floor areas dominate, room partitions, doors, stairs/cores, and vertical circulation are not legible, and the available sources do not verify room adjacencies. |
| Source evidence and uncertainty | 1.4/1.5 | The build record includes the Purdue GIS feature identity/raw response and CRS, Trustees site plan, university housing sources, and construction imagery, with dates and clear limits. It correctly distinguishes outline agreement from wall-survey accuracy and labels height, partition, facade placement, and interior assumptions. |
| Saved asset and portability | 0.9/1.0 | I independently reopened the exact file in Blender 5.2.3. The expected collection and root are present, no mesh lacks materials, and no external file-backed images are used. The standalone review did not validate the master placement marker. |
| **Total** | **8.2/10** | **Passes the asset review threshold.** |

## R1 response and remaining limitations

R2 responds to the R1 findings by adding a multistory glazed facade bay, varying window module widths, adding restrained roof seam variation, and connecting the public-space diagram. The public-space clipping and fresh asset reopen are supported by current evidence. This is enough to clear the asset threshold, but the model remains a schematic representation rather than an as-built architectural model.

The source photo's atrium reads as a recessed/open stack with visible intermediate structure, while R2 uses a simplified curtain-wall-like bay. I treated that as a partial visual match rather than an exact atrium reconstruction. The roof and eaves remain under-detailed, and the cutaway does not show a complete or sourced interior layout. The available floor and site plans do not georeference internal room locations or establish exact height dimensions.

At master integration, independently check `Placement_south_hall` against the manifest and reopen the complete master. This review grades the standalone building asset and does not claim campus placement has been verified.

## Evidence inspected

- `BUILD_RECORD_R2.md`, `validation_r2.json`, and `public_geometry_r2.json`.
- `independent_reopen_r2.json`, created by a fresh Blender 5.2.3 reopen of the exact file hash above.
- `official_footprint_vs_asset_r2.png` and the R2 entry, oblique, and cutaway renders.
- The retained Purdue 2026 exterior/interior photos and 2023 Trustees site-plan image.
- `independent_grade_r1.md` and its R1 scorecard for the prior findings.

The GIS boundary is generated from the same source polygon and is an envelope check rather than independent wall-survey evidence. Height, connector placement, roof assembly, facade bay location/dimensions, and interior adjacencies remain estimated or unverified.
