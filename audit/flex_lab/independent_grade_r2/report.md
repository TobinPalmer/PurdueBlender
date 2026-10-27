# Independent Flex Lab R2 grade

**Result: 8.4/10 — PASS** (threshold: 8.0/10)

- Frozen asset: `modular/buildings/flex_lab.blend`
- SHA-256: `523426ab0f460b4bb7eca72aaf1f85a822300930388cba9e52ba6fa8620b82e9`
- Fresh open: Blender 5.2.3 LTS, separate background process; exact hash confirmed.
- Review scope: standalone asset facade, entry, curtainwall, canopy, GIS identity/outline, modularity and evidence. No project files were changed by the grader outside this directory.

## Criterion scores

| Criterion | Score | Findings |
|---|---:|---|
| Identity / footprint | 2.0/2 | Purdue campus GIS identifies FID 909 as Flex Laboratories. The 170-vertex shell is unchanged from its saved baseline. Comparing the 85 unique model boundary vertices, translated by the manifest origin, with the official GIS polygon ring gives 0.0973 m symmetric Hausdorff distance. The source is a campus-map outline, not a certified survey. |
| Position / orientation / scale | 1.8/2 | The manifest origin exactly matches the source polygon's AABB center. GIS rectangle is approximately 98.45 × 32.51 m, oriented 90.06° east-CCW. Asset coordinates remain local and metric. I did not independently finish loading the full master file to verify its live placement marker, so this is not full credit. |
| Floors / roof | 1.5/2 | Three above-grade floors and a basement have source support. The modeled 14.8 m shell height, exact story heights and high-bay roof monitor remain estimates/interpretations. |
| Facade / entrances / architecture | 1.5/2 | R2 opens the south entry and 11 long-facade bays, with floor-level lites, mullions, spandrels, projecting fins, brick planes and a recessed vestibule. One canopy measures 6.10 m in projection, corresponding to the published 20 ft dimension. Photos substantiate the broad composition, not exact bay dimensions. The facade and canopy framing are simplified; the reviewed renders are dark/diagrammatic. Interior furniture and room organization are schematic, not plan-verified. |
| Modular export / portability / evidence | 1.6/2 | The saved file fresh-opens as `Scene` with linked `Asset_flex_lab` (407 objects); initial library-link list is empty and there are no missing external images. Evidence includes Ennead, CE Solutions, Purdue and official GIS. Credit is reduced because the R2 source register says the GIS snapshot/CRS was not retained, while the official reference snapshot and manifest do document retrieval date 2026-10-22 and the approximate coordinate transform. Also, the local AW07 file is an interior view although R2 lists it as facade support. |
| **Total** | **8.4/10** | **PASS** |

## Source checks and remaining uncertainty

The GIS evidence identifies official Purdue ArcGIS BuildingShapesZip4 layer 0, feature 909. `official_building_references.json` records a 2026-10-22 retrieved snapshot, local east/north/up metric conversion, and polygon geometry. The service does not provide an edit date or survey tolerance. Its coordinate frame is explicitly an approximate project-local geographic conversion, not a projected survey CRS; therefore the sub-decimeter boundary comparison measures agreement with that stored snapshot, not survey accuracy or actual wall offset.

Ennead Architects' AW19 entry and AW06 curtainwall images support the recessed glass entry, shifting curtainwall, projecting brick planes and facade rhythm. CE Solutions' project page/photo supports the three-story-plus-basement program, steel vestibule, and 20 ft canopy cantilever. None of these public images provides dimensioned elevations. Purdue Engineering supports facility identity and research use, not facade measurements. The local AW07 reference is an interior photograph, not exterior-facade evidence.

Primary source links: [Ennead Architects — Purdue](https://www.ennead.com/work/purdue/), [CE Solutions — Flex Lab](https://www.cesolutionsinc.com/flex-lab-1), [Purdue Engineering — Flex Lab](https://engineering.purdue.edu/FlexLab), [Purdue ArcGIS BuildingShapesZip4 layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0).

## Reproducible artifacts

- `probe.py` / `probe.json`: separate fresh-open Blender probe and its exact hash/asset inspection.
- `source_comparison.py` / `gis_comparison.json`: GIS polygon-to-shell boundary comparison and the recorded frame caveat.
- `result.json`: machine-readable score and criterion findings.
