# Independent Evans Scholars House review

## Verdict: 8.4/10 — Pass

Reviewed the exact asset SHA-256 `4f14bbdf897f8416d1b1e67c0d2e8b5041c9c3e7376efcf371e9266260f62cb7`. The model is a strong, portable representation of the Evans Scholars house at 1001 Hilltop Drive. It is ready for master integration. The main limits are estimated roof/elevation details and an illustrative rather than documented interior plan.

## Criteria

| Category | Score | Review |
| --- | ---: | --- |
| Identity and footprint | 1.9 / 2.0 | Purdue FID 755 identifies Evans Scholars at 1001 Hilltop Dr. Chapter gallery signage corroborates the identity. An independent parse of the reopened foundation slab against the saved FID 755 ring gives IoU 0.99999996 and symmetric boundary Hausdorff error 0.0000011 m. This ring originated the model, so the check confirms coordinate/serialization fidelity, not a survey. |
| Placement and scale | 1.8 / 2.0 | The local frame is centered at the documented GIS centroid (−811.959417, 865.137355) m. The 54.33 m by 39.84 m mapped envelope and the building's orientation are preserved; the south approach/front elevation agrees with the parking apron in the aerial image and chapter photos. The final master marker still needs coordinator verification. |
| Floors, height, and roof | 1.5 / 2.0 | A one-story exterior is consistent with the GIS level count and chapter photos. The long main gable, cross wings, cupola, and shingle appearance are recognizable in both source imagery and model. Exact eave height, ridge heights, pitch, and roof intersections remain estimated. |
| Facade and entrance | 1.7 / 2.0 | Red brick, light trim, divided windows, two-column pedimented entrance, round green emblem/signage, flagpoles, and patio canopy match the chapter gallery well. The render is simplified: brick texture is regular, and some window rhythm, roof junctions, and small exterior features are inferred or omitted. |
| Interior, portability, and evidence | 1.5 / 2.0 | Fresh-open Blender 5.2.3 check found 202 objects, 198 meshes, 16 materials, no linked libraries, and no external image dependencies. Kitchen/dining, study, lounge, laundry, and recreation functions have a schematic representation supported by chapter photos, but the plan and furniture placement are not measured. |
| **Total** | **8.4 / 10** | **Pass (threshold 8.0)** |

## Remaining uncertainty

Purdue's GIS record and address, the chapter's front-entry signage photos, and the aerial roof outline consistently identify the house. The GIS extrusion field does not provide a trustworthy vertical unit or datum, so it was not used for height. The chapter gallery is valuable but most visible exterior imagery dates to 2017. The exact roof pitch, hidden elevations, window spacing, and interior plan remain unverified. Keep those details labeled estimated.

## Evidence files

- `fresh_open_probe.json` and `fresh_open.log`: independent reopen, SHA, dependency, material, and geometry summary.
- `geometry_probe.json` and `probe_asset.py`: independently extracted structural mesh inventory and foundation ring vertices.
- `gis_comparison.json` and `compare_gis.py`: reproducible GIS ring comparison and transform notes.
- `result.json`: machine-readable independent grade.
