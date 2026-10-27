# Frieda Parker Hall R2 independent grade

**Result: 8.5/10 — PASS** (threshold: 8/10)  
**Asset:** `modular/buildings/frieda_parker_hall.blend`  
**Inspected SHA-256:** `cc27ae34084d14dc845a3cb29dbaed42a465dbef96e4efb2877dad57f5b85949`  
**Inspection:** fresh open in a separate Blender 5.2.3 LTS process.

## Scores

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 1.8/2 | Official Purdue GIS FID 409 identifies Frieda Parker Residence Hall. The retained upper shell has 0.8986 IoU against its transformed plan polygon; the unsupported north upper block is absent. |
| Position, orientation, and scale | 1.7/2 | Root transform is identity. Shell envelope edges are within about 0.06–1.74 m of the transformed GIS envelope and centroids are about 1.06 m apart. Absolute placement was not checked against a fresh-opened master. |
| Floors and roof | 1.4/2 | Purdue Housing documents six stories; model height is 25.8 m and the inspected roof masses are plausible. Exact elevations and roof dimensions are not sourced. |
| Facade, entrance, and architecture | 1.6/2 | Brick wings, horizontal pale bands, repetitive residential windows, glazed active ground floor and connector broadly match architect photos. Some elevations are blank/schematic and bay/mullion details remain interpreted. |
| Modular export, portability, and evidence | 2.0/2 | Expected scene and scene-linked asset collection; 541 objects / 540 meshes; identity root; no linked libraries, file-backed images, or missing images. Building-specific source and review evidence is present. |
| **Total** | **8.5/10** | **PASS** |

## GIS comparison and uncertainty

The official Purdue ArcGIS BuildingShapesZip4 layer feature FID 409 has 42 unique perimeter vertices, area 2,315.24 m², and transformed local-frame bounds X[-35.413, 24.464], Y[-48.867, 49.575]. I compared the three retained upper-shell mesh bounding footprints, unioned in XY, with that polygon: model union 2,401.98 m², intersection 2,232.65 m², outside 169.33 m², and IoU 0.89860. The modeled shell area is 92.95% inside the GIS polygon. Its envelope edges differ from the GIS bounds by roughly 0.05–1.74 m.

The local conversion follows the project source register: `X=(lon+86.9137)*84810.60416539927`, `Y=(lat-40.4274)*111040`, then subtract project origin `[-499.7250061,97.475]`. This is an approximate local linear transform, not a surveyed georeference. The GIS service gives no positional accuracy and may generalize wall edges; the residual 169.33 m² outside the footprint therefore merits attention but is not, by itself, proof of a geometric error.

## Limits and evidence

R2 corrects the major prior footprint problem (R1 IoU 0.692) by removing the unsupported upper block while retaining the three shells that substantially overlap FID 409. No unsupported global rescale or origin change was found. Story count has a primary source, but total height, floor-to-floor elevations, roof profile, and detailed facade dimensions remain visual estimates. This independent asset review did not open the campus master or validate its placement marker.

Detailed machine-readable evidence is in `result.json`, `fresh_open_probe.json`, and `gis_comparison_r2.json`. The Blender inspection and comparison scripts are `probe_asset.py` and `compare_gis_r2.py`; the evidence views and source register are in the parent `audit/frieda_parker_hall/` directory.

Only files under `audit/frieda_parker_hall/independent_grade_r2/` were written. The blend asset and shared project files were not modified.
