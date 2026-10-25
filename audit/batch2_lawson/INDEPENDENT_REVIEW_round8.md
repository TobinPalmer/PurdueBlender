# Lawson Hall — independent R8 review

**Grade: 8.1/10 — pass.** I independently reopened the exact saved asset in Blender 5.2.3 LTS, checked its contents/material portability, recomputed the GIS FID 59 footprint fit, and inspected the R8 facade, upper-floor, terrace, and overlay images. SHA-256: `7a190341cef8c612672c6460850abddfd0f4b1b45165ef9dcbd4e41b1e5cc0eb`.

| Rubric criterion | Score |
| --- | ---: |
| Correct identity and source-backed footprint | 2.0/2 |
| Position, orientation, and scale/dimensions | 1.7/2 |
| Evidence-backed height, floors, and roof form | 1.2/2 |
| Facade, entrances, and distinctive architecture | 1.5/2 |
| Interior, materials, modular export, and evidence | 1.7/2 |
| **Total** | **8.1/10** |

## Findings

- **Identity and footprint:** The model matches the Lawson GIS FID 59 lower plan outline. My fresh check sampled 21 points on each of 54 ordered GIS edges against the saved mesh perimeter: all 1,134 samples are within 0.10 m, with a maximum nearest-edge distance of 0.0000152 m. This does not verify wall thickness, height, or all above-grade geometry.
- **Position and scale:** The asset root reopens at identity. Registered L1/L2/L3 raster plans and overlays show north-up placement against the GIS footprint, with about 0.3 m image-pick uncertainty. The earlier master marker record is consistent with the manifest, but I did not freshly reopen the master as part of this asset grade.
- **New upper-floor and terrace evidence:** The model now includes slabs and sparse plan-derived partitions on floors 2 and 3 (75 and 87 retained long orthogonal source segments). Purdue's L3 plan labels Tolonga Terrace; Purdue's building-hours page also lists a third-floor terrace/balcony. The roof has a notch at the terrace zone. The overlays show generally good plan registration, with local source-stroke offsets up to about 0.7 m and a roughly 0.3 m raster/line-pick uncertainty. The traces are useful architectural visualization but do not reproduce every partition or doorway.
- **Height and roof:** The revised penthouse/equipment silhouette is closer to Purdue's completed/construction photos, and the whole model's maximum Z is now 19.0 m. The photo references are perspective views, not measured elevations. Roof datum, story heights, penthouse and equipment dimensions remain estimated; the GIS's five-level attribute does not establish the model's floor elevations. No complete fourth/fifth-floor or basement plan or verified stair section was found.
- **Facade and presentation:** The exterior retains brick and light stone bands, repeated windows, the curved Commons, and the photo-guided entry. The R8 roof/terrace edits improve the silhouette, but the exterior remains schematic. The roof notch is not accompanied by measured terrace guard details; window cadence and glazing dimensions lack measured elevations.
- **Interior and technical integrity:** Blender 5.2.3 reopened the asset with 619 objects and 616 meshes, 41 assigned materials, an identity root, no material-less meshes, no missing external image files, and no duplicate R8 objects. The Harris wall retains its documented 4-by-4, 16-module layout. L2/L3 interiors have plan-based partitions but little door or furniture detail; their Z positions and wall dimensions are explicitly schematic.

## Why R8 passes

The R7 revision scored 7.8/10. R8 adds meaningful source-backed coverage beyond the first-floor-only layout: separate L2/L3 room partitions, a source-indicated third-floor terrace, and photo-guided rooftop proportion corrections, while retaining the very close GIS footprint fit and portable asset validation. The score narrowly passes at 8.1. The remaining height, roof, facade and interior limitations are recorded above; this grade does not certify them as measured/as-built.

## Evidence and primary sources

- Independent Blender reopen and geometry check: `grade_reopen_r8.py` and `grade_reopen_r8.json`.
- R8 builder evidence and validation: `evidence_round8.json`, `upper_plan_registration_round8.json`, `roof_photo_refinement_round8.json`.
- Reviewed images: `exterior_round8.png`, `floor2_layout_round8.png`, `floor3_layout_round8.png`, `gis_plan_overlay_l2_round8.png`, `gis_plan_overlay_l3_round8.png`, and `plan_l3_terrace_detail_round8.png`.
- Purdue L1, L2, and L3 plans: https://www.cs.purdue.edu/resources/docs/lawson_1.PDF ; https://www.cs.purdue.edu/resources/docs/lawson_2.PDF ; https://www.cs.purdue.edu/resources/docs/lawson_3.PDF
- Purdue's building-hours listing confirms a third-floor terrace/balcony: https://www.cs.purdue.edu/resources/building-hours.html
- Purdue CS March 2006 exterior/construction reference: https://www.cs.purdue.edu/news/articles/2006/building-update-march.html
- Purdue CS 2006 dedication images: https://www.cs.purdue.edu/news/articles/2006/lawson-dedication.html
- Purdue's 2011 Harris video-wall article: https://www.cs.purdue.edu/news/articles/2011/harris-video-wall.html
- Purdue GIS FID 59 query: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D59&outFields=*&returnGeometry=true&outSR=4326&f=json
