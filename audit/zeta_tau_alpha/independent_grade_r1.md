# Independent Zeta Tau Alpha R1 Grade

**Score: 7.90/10 -- below the 8.0 threshold**
**Exact reviewed SHA-256:** `795eef2993264674747768df2bd29ff6bdef3ff7ab48d33299c03060691b67d6`  
**Fresh reopen:** Blender 5.2.3 LTS
**Review date:** 2026-10-26

## Scorecard

| Criterion | Score | Independent evidence |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2.00 | Purdue ArcGIS feature FID 773 names Zeta Tau Alpha at 118 Waldron St (SOZTA). I independently transformed the raw EPSG:3857 ring and reconstructed the shell base ring from saved mesh side faces. IoU=0.999999969; area 744.706 vs 744.706 m2; centroid error 0.00000003 m. This establishes exact transfer of the public GIS ring, not surveyed wall accuracy. |
| Position, orientation, and scale/dimensions | 1.50/2.00 | The local shell bounds reproduce the transformed GIS ring within sub-millimeter rounding; the asset records placement origin [-320.5144435379624, -187.07450048567304] m, independently matching the source-ring centroid. The current master reopen (3367f16ddd3e2a941c1358076158b8381132eba88653c21bfed54653721bc1f6) contains only the old direct massing object named Zeta Tau Alpha; there is no detailed placement marker or instance for this candidate, so its final campus placement/orientation in master has not yet been verified. |
| Evidence-backed height, floors, and roof form | 1.25/2.00 | Saved shell vertical span is 0.15-8.18 m and the complete asset maximum is 11.91 m. GIS Extrution is 12, but GIS NUM_LEVELS and CountOfFLO both read 1 and the field semantics/units are not documented. The build report says about 12.5 m although this exact file reaches 11.91 m. Official 2022 imagery supports a pitched dark roof and roof silhouette, but no measured elevation or floor plan was found; the three interior plates are schematic. |
| Facade, entrances, and distinctive architecture | 1.35/2.00 | The model visibly reproduces the red-brick shell, light trim, central white columned portico and pediment, hipped dark roof, dormers, and window rhythm visible in the official ZTA chapter-house photograph. The front review render does not show the distinctive ZTA mark seen on the source pediment. The saved FONT object has body ZTA but its world Y bounds (18.661-18.685 m) sit about 0.6 m behind the pediment outward face at Y about 19.27 m, so it is occluded. Windows are layered over a continuous shell rather than openings; facade proportions/details are approximate. |
| Modular export, portability, and evidence | 1.80/2.00 | Blender 5.2.3 fresh-process reopen passed for exact SHA 795eef2993264674747768df2bd29ff6bdef3ff7ab48d33299c03060691b67d6: stable scene/collection present, 563 exported objects (562 meshes), 13 named materials, all meshes have material assignments, no broken images, and all four brick texture maps are packed. The asset is isolated from the master and its source record documents CRS, feature, sources, transformation, and limitations. The three-floor interior is only schematic and not based on floor plans; windows do not permit normal exterior views into it. |

**Total: 7.90/10. Fail (required 8.0).**

## Main findings

- Move the raised ZTA lettering and backing plaque onto the outward-facing side of the pediment; rerender to confirm the mark is legible.
- Reconcile the 12.5 m height statement with the exact file maximum of 11.91 m; keep it explicitly estimated unless measured elevation evidence is added.
- Before acceptance/integration, have the coordinator replace the old direct massing link with the detailed library and verify its new placement marker against the saved campus origin and facade orientation.
- Keep the interior explicitly schematic; if more fidelity is required, add documented room partitions/bathrooms and produce an interior cutaway. No measured floor plan was found.

## Independent measurements

- FID 773 is Zeta Tau Alpha at 118 Waldron St; layer metadata confirms Web Mercator WKID 102100/latest 3857.
- Source/model base area: 744.706199/744.706208 m2; independently computed IoU 0.999999969.
- Symmetric mean/P95/Hausdorff boundary residuals: 0.000000/0.000000/0.000001 m. These tiny values reflect the shell use of the public GIS ring and are not survey evidence.
- Candidate local origin metadata: [-320.5144435379624, -187.07450048567304] m. No detailed placement marker exists in the current master; it still contains one direct massing object named `Zeta Tau Alpha`.
- Exact file maximum asset Z is 11.910 m, while its build report says about 12.5 m. GIS Extrution=12 is suggestive but is not documented as a measured elevation.
- Four brick PBR images are packed. Remaining materials are procedural/simple nodes; export opens without external image dependencies.
- Interior contains three schematic floor plates, repeated dining/lounge furniture, bedrooms on upper levels, and stair treads. It has no measured partitions or bathrooms, and windows are overlays, so normal views do not expose the interior.

## Sources

- [Purdue ArcGIS BuildingShapesZip4 FID 773](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/773?f=pjson)
- [Purdue ArcGIS BuildingShapesZip4 layer metadata](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson)
- [Zeta Tau Alpha: Alpha Theta celebrates 101 years at Purdue](https://zetataualpha.org/news/alpha-theta-celebrates-101-years-at-purdue)
- [Google Maps: 118 Waldron St, West Lafayette](https://www.google.com/maps/place/118+Waldron+St,+West+Lafayette,+IN+47906)

## Evidence files

- `independent_grade_r1_evaluator.py` -- runnable evaluator function returning score, criteria, evidence, and findings.
- `independent_grade_r1.json` -- machine-readable result.
- `independent_grade_r1_extract.json` and `independent_grade_r1_metrics.json` -- fresh Blender extraction and independent GIS comparison.
- `independent_grade_r1_master_check.json` -- read-only master inspection.
- `candidate_front_review.png` and `official_2022_centennial_house_photo.jpg` -- compared views.

## Limitations

- Purdue GIS polygon is a mapped footprint rather than a surveyed structural wall line; near-perfect IoU only verifies faithful transfer of that ring.
- The Google Maps Street View page was not independently accessible through the page reader; the 2026 image date/view direction is taken from the builder record. The facade comparison here uses the archived official 2022 photo.
- Master integration is pending; the candidate has not been graded as an installed campus instance.
