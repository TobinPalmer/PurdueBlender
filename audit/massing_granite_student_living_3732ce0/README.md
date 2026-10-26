# Granite Student Living (North by Northwest)

Assigned stable asset: `massing_granite_student_living_3732ce0`.

The operator, architect, county market survey, and county-hosted 2014 plan set identify North by Northwest at 225 Northwestern Avenue. Sheets A100/A105 document the proposed five-story project, 64 ft overall height, first-floor and upper-floor shell dimensions, and north-south long axis. A200/A201 provide floor elevations, truss bearing, brick/siding/stone facade palette, balcony and window rhythm, and the hip/gable roof design.

The saved asset has the stable collection `Asset_massing_granite_student_living_3732ce0`, 1,088 mesh objects, and total collection bounds X `[454.0112, 474.6333]`, Y `[-236.4506, -190.1207]`, Z `[0, 19.5072]` m. Reopen validation found no external libraries or textures. The first-floor shell matches A105 within 0.00002 m. The upper-floor width matches within rounding, while its north-south length is 2 in longer than the A105 upper-floor dimension because the model retains the first-floor length for the upper levels.

The independent r2 review scored the asset **8.55/10 (pass)**. The 2014 drawings are proposed design documents, not verified as-built records. No direct building-footprint polygon was found. Address and parcel data support plausible placement but do not establish a surveyed centroid or wall line; parcel alignment varies by a few tenths of a meter with the local coordinate approximation. Facade stationing and roof intersections remain simplified.

Evidence and raw snapshots are in `source_register.json` and `sources/`. Plan dimensions, parcel alignment, final validation, and the independent review are recorded in `official_plan_measurement.json`, `parcel_site_plan_alignment.json`, `reopen_validation.json`, and `independent_grade_r2/result.json`. Preview renders are `preview_exterior.png` and `preview_end_view.png`; the build record is `build_report.json`.
