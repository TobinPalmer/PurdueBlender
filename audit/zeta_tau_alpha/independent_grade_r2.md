# Independent Zeta Tau Alpha R2 Grade

**Score: 8.20/10 — passes the 8.0 threshold**
**Exact reviewed SHA-256:** `1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af`  
**Fresh reopen:** Blender 5.2.3 LTS
**Review date:** 2026-10-26

## Scorecard

| Criterion | Score | Evidence |
|---|---:|---|
| Identity and source-backed footprint | 2.00/2.00 | Purdue ArcGIS BuildingShapesZip4 FID 773 identifies Zeta Tau Alpha at 118 Waldron St (SOZTA). I independently inverse-projected the raw EPSG:3857 ring and transformed it with the repository local approximation, then rebuilt the saved shell base ring from the fresh Blender extraction. Shape IoU=0.999999969, area 744.706199 vs 744.706208 m², centroid error 0.00000003 m. This verifies transfer of the public GIS ring, not a surveyed structural wall line. |
| Campus position, orientation, and scale | 1.50/2.00 | The model keeps campus-coordinate geometry and records origin XY [-320.5144435379624, -187.07450048567304] m, within 0.000000 m of the transformed GIS centroid. The outline supports the plan dimensions; facade direction is plausible from the chapter-house photo and saved reference, but the standalone candidate has not yet been checked as an installed instance in the current master. The local geographic conversion is approximate. |
| Evidence-backed height, floors, and roof | 1.40/2.00 | Fresh asset bounds give a maximum Z of 11.91 m; the R2 report now correctly describes this as the model's estimated peak, removing the former 12.5 m discrepancy. ArcGIS Extrution=12 is undocumented, while NUM_LEVELS and CountOfFLO are 1, so actual stories/height remain unverified. The 2022 official photo supports a pitched dark roof and portico silhouette; the multiple dormers/roof layout are modeled interpretation. |
| Facade, entrances, and distinctive details | 1.50/2.00 | The R2 front render now shows the ZTA mark on the outward-facing pediment plane, resolving the R1 occlusion. Red brick, pale trim, a white columned portico, cross-muntin windows, and dark pitched roof broadly match the official 2022 chapter-house photo. The model is stylized, has fewer/simpler facade details than the photo, and its windows are layered over a continuous shell rather than cut-through openings. |
| Technical integrity, materials, interior, and evidence | 1.80/2.00 | Fresh Blender 5.2.3 LTS process reopened the exact SHA 1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af. The stable scene/collection has 563 objects (562 meshes plus the ZTA lettering), 13 named materials, no materialless meshes, and 4 image dependencies, all packed. The interior collection has 112 schematic objects including three floor plates, a corridor, dining furniture, bedrooms/stair furniture; no measured plan or bathrooms/partition layout is verified. |

**Total: 8.20/10. Pass (required 8.0).**

## Findings

- The R2 lettering correction is visible in the saved front review render and its text bounds lie on the outward-facing side of the pediment.
- R2 corrected the height statement to match the actual 11.91 m asset maximum, explicitly an estimate rather than a measured elevation.
- The shell follows the GIS ring nearly exactly; this does not establish a surveyed wall line.
- Final master placement/orientation remains unverified until the coordinator replaces/reloads the massing library and checks the campus instance.
- Interior remains schematic and the roof dormer arrangement is not fully established by the available photo evidence.

## Independent checks

- Blender 5.2.3 fresh-process reopen: 563 objects, 562 meshes, 13 materials, all image dependencies packed.
- FID773 shell base vs transformed GIS ring: IoU 0.999999969; mean/P95/Hausdorff boundary residual 0.000000/0.000000/0.000001 m. This is a direct ring transfer and not survey evidence.
- Source-ring centroid vs asset origin: 0.00000003 m; origin XY [-320.5144435379624, -187.07450048567304].
- Fresh mesh bounds: X [-16.232135772705078, 13.844943046569824], Y [-21.712425231933594, 19.65256118774414], Z [-0.004999995231628418, 11.910000801086426] m. R2 identifies max Z 11.91 m as estimated peak; GIS height fields remain ambiguous.
- R2 pediment-text world Y bounds: [19.38056182861328, 19.404560089111328]; pediment outward Y max recorded by independent builder reopen: 19.272560119628906 m; text lies outside the pediment face.
- Interior inventory: 112 objects including three floor plates, corridor, furniture and bedroom/stair elements; layout is schematic and lacks an available measured plan.

## Sources

- [Purdue ArcGIS BuildingShapesZip4 FID 773](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/773?f=pjson)
- [Purdue ArcGIS BuildingShapesZip4 layer metadata](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson)
- [Alpha Theta celebrates 101 years at Purdue, Zeta Tau Alpha official article and photo](https://zetataualpha.org/news/alpha-theta-celebrates-101-years-at-purdue)
- [Google Maps Street View reference (builder archived URL; this page was not independently rendered by web reader)](https://www.google.com/maps/place/118+Waldron+St,+West+Lafayette,+IN+47906/@40.4255967,-86.91789,3a,75y,65.05h,90t/data=!3m5!1e1!3m3!1s8sVKIehKbcyb50bjkmpU1Q!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3D8sVKIehKbcyb50bjkmpU1Q%26yaw%3D65.04872)

## Evidence

- `audit/zeta_tau_alpha/independent_grade_r2_extract.py`
- `audit/zeta_tau_alpha/independent_grade_r2_extract.json`
- `audit/zeta_tau_alpha/independent_grade_r2_extract.log`
- `audit/zeta_tau_alpha/independent_grade_r2_metrics.json`
- `audit/zeta_tau_alpha/independent_grade_r2_interior.py`
- `audit/zeta_tau_alpha/independent_grade_r2_interior.json`
- `audit/zeta_tau_alpha/candidate_front_review_r2.png`
- `audit/zeta_tau_alpha/official_2022_centennial_house_photo.jpg`
- `audit/zeta_tau_alpha/gis_fid773_raw.json`
- `audit/zeta_tau_alpha/gis_layer_metadata.json`

## Limitations

- GIS footprint is a generalized map polygon, not a survey.
- GIS Extrution units and level-count fields are inconsistent/undocumented; actual height and floor count are estimated/unverified.
- The Google Maps Street View page could not be rendered independently through this evaluator; it relies on the source URL and archived official photograph for facade comparison.
- No master placement marker check was made during this asset-only grade.
