# Independent grade — Life Science Ranges Greenhouse and Service Building

**Result: 7.5/10 — revision required**  
Asset reviewed: `modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend`  
SHA-256: `5A33EFE401C37523D184430A692AD10FEA04A3F71F098E083B488D5064C38B1C` (matches expected candidate hash).

The evaluator is `evaluate.py`; its returned object is saved in `grade_result.json`. It follows the five 2-point criteria in the repository's `AGENT.md` and independently checks the asset hash, GIS identity, projected GIS envelope dimensions, candidate bounds from the fresh-open report, and required evidence-file presence. The score is below the repository's 8/10 threshold.

## Criteria

| Criterion | Score | Evidence and assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | Purdue GIS feature/FID 915 identifies BLDG_ABBR `LSR`, Life Science Ranges, 180 S Russell Street. The official GIS polygon and orthophoto identify the greenhouse complex; the 2022 Purdue board exhibit names the greenhouse ranges. The builder traces the GIS perimeter and lays out range blocks from imagery. |
| Position, orientation, and scale/dimensions | 1.5/2 | Projected GIS envelope is 94.75 m east-west by 122.18 m north-south. Asset bounds are 95.10 by 122.40 m, only +0.35/+0.22 m different. Axis orientation agrees with the aerial. The saved overlay compares the GIS shape with the *legacy massing* outline; it does not overlay this candidate geometry. Master placement marker application is also not verified here. |
| Evidence-backed height, floors, and roof form | 1.0/2 | GIS lists two levels and `Extrution=12`, but the saved source metadata does not explain that field's units or meaning. Aerials and Purdue photos support multi-span pitched greenhouse roofs and the service wing. Candidate eave/ridge/service heights (3.65/5.95/6.8 m) are estimates without dimensioned section or elevation evidence. |
| Facade, entrances, and distinctive architecture | 1.5/2 | Purdue's exterior photo supports glazed greenhouse framing, an opaque base, brick/service portion and facility sign. The conveyor photo supports the phenotyping-equipment concept. The model has visible frames, translucent glazing, a service facade, doors, louvers, sign, benches and plants. Some service facade proportions and interior details are plausible reconstruction rather than source-measured. |
| Modular export, portability, and complete evidence | 1.5/2 | Hash matches; fresh-open validation passes with 49 objects, 17 materials and no unpacked external image dependencies. Expected scene and collection are present. The source packet and review renders are substantial. Per-source URL/provider, retrieval date, source date, CRS, method and uncertainty are not consistently recorded. |

## Concrete revision requests

1. Add a candidate-asset top-down overlay against GIS FID 915. The current `gis_footprint_overlay.jpg` is clearly captioned as the old massing outline and is not proof of this candidate's registration. Include the proposed origin and verify it against the master `Placement_...` marker, or note that the master owner must apply and validate the origin.
2. Support the height values with an authoritative elevation/section if available. Otherwise keep them explicitly labeled estimates, explain their basis, and resolve or explicitly mark the units/meaning of GIS `Extrution=12` as unknown.
3. Complete provenance for each source: exact URL, provider, retrieval date, source date where available, CRS, measurement method and uncertainty. The audit README's reported 0.876 hand-traced IoU is not independently reproducible from the supplied report alone; document the calculation or provide its reproducible method/results.

## Remaining uncertainty

No dimensioned as-built elevation/section was found in the inspected packet. Greenhouse bay heights, interior bench/crop arrangement and equipment locations are interpretive. The master placement instance was outside this independent asset-grade run.
