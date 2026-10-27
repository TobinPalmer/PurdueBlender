# Independent grade — Gamma Phi Beta R1

**Asset:** `modular/buildings/gamma_phi_beta.blend`  
**SHA-256:** `c9dbc1da41f87962022c39795751d797e0f5ff2a8aa0bf64cd89fa4257f89f25`  
**Score:** **8.3/10 — PASS** (8.0 minimum)

| Criterion | Score |
|---|---:|
| Verified identity and site placement | 1.8/2 |
| Footprint and form | 1.8/2 |
| Facade, materials, and source fidelity | 1.6/2 |
| Interior | 1.1/2 |
| Portability and fresh-open validation | 2.0/2 |
| **Total** | **8.3/10** |

## Findings

I verified the asset SHA, opened the saved file directly in Blender 5.2.3 LTS, and inspected its scene, collection, objects, material assignments, and external image dependencies. It contains the expected `Building_gamma_phi_beta` scene, `Asset_gamma_phi_beta` collection, and 255 mesh objects. I found no unpacked external image textures. The supplied fresh-open record passes for the same SHA.

The preserved Purdue ArcGIS feature identifies Gamma Phi Beta (FID 759, SOGFB, 810 David Ross Rd). I independently compared the transformed GIS ring against the model's base shell vertices; the maximum nearest-vertex residual is about **0.0000052 m**. Purdue chapter listings and the official chapter/archive references reinforce the identity crosswalk. The 1979 article and archival photo support the broad flat-roofed, vertically articulated steel-clad form, grouped glazing, carved entrance door, and multilevel use.

The model includes differentiated named materials and schematic interior slabs, tables, benches, and partitions. The article supports dining, study, and upper-floor living functions, but no authoritative floor plan was found, so the interior cannot be graded as a source-accurate layout. The historical photograph is monochrome and not georegistered; the surface colors, current appearance, and exact facade dimensions remain estimates.

## Limitations

- The official GIS `Shape__Area` value (1160.34375 m²) differs materially from the documented approximate local projection's polygon area (671.1901 m²). The raw GIS ring is followed by the model, but the area/CRS discrepancy and source tolerance remain unresolved.
- GIS `NUM_LEVELS=1` conflicts with the chapter article's description of second- and third-floor living. The modeled three above-grade bands and approximately 12 m height are plausible, not verified measurements.
- Exact current exterior colors, entrance orientation, and terrain response are not supported by current georegistered imagery.

No corrections are needed to clear 8/10. Stronger evidence for the GIS area/CRS, current elevations, and interior layout would support a higher score.

## Reproducibility artifacts

- `result.json`: full per-category scores, evidence, and limitations.
- `asset_probe.json`: direct Blender inspection of the saved file and its assigned materials.
- `footprint_probe.json`: independent transformed GIS-to-shell comparison.
- `probe_asset.py` and `probe_footprint.py`: scripts used for those read-only inspections.
