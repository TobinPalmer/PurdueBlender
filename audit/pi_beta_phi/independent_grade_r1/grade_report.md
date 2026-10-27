# Independent Pi Beta Phi Grade R1

Result: 8.5/10 - PASS (threshold: 8.0/10)

Frozen asset SHA-256: `8c1684ed6e4486fe2200af68600821c6c1f739db8939dd495ac5bdfe5b8e58c7`

Fresh open: Blender 5.2.3 LTS; scene `Building_massing_house_301838781_891384f`; 698 objects; 696 meshes; 8 material families; no linked libraries or file-backed images.

Independent GIS comparison: IoU 0.9999999752, symmetric Hausdorff 0.000000903 m, centroid delta [2.7071973564171463e-08, 1.1699825151804418e-07] m.

| Criterion | Score | Evidence and finding |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.0/2.0 | GIS FID 774 names Pi Beta Phi at 1012 State St; chapter sources support Indiana Delta identity. Fresh-open shell vs GIS: IoU 0.9999999752, symmetric Hausdorff 0.000000903 m. FID 841 is a distinct smaller mapped feature, explicitly excluded; its relationship remains unresolved. |
| Position, orientation, and scale/dimensions | 1.8/2.0 | The GIS-derived local shell matches the source ring; the asset origin is based on the source feature center and its local bounds have plausible scale. The local-coordinate asset has not yet been checked through the master Placement marker. |
| Evidence-backed height, floors, and roof form | 1.3/2.0 | Two primary facade levels, small upper openings, continuous white parapet/cornice and screened flat roof are represented; total bounds height is 8.66 m. Exact floor heights, foundation datum, roof height/construction are unsupported; the roof/attic and three interior floor plates are estimates. |
| Facade, entrances, and distinctive architecture | 1.7/2.0 | Inspected renders show red brick, regular sash windows, white classical portico/columns, curved balcony rail, double doors/transom, address number and stairs. Rear/side roof and terrace-like surfaces are simplified; facade details are not dimensioned; Greek-letter sign is small and low contrast. |
| Modular export, portability, and complete evidence | 1.7/2.0 | Fresh-open Blender 5.2.3 LTS confirmed expected scene/collection, 698 objects, 696 meshes, eight material families, no links or external image dependencies; evidence and renders are present. Shared manifest conversion and master placement marker still need root integration and fresh-open validation. |

## Findings

- Passes the 8/10 building-candidate threshold.
- Roof/story height and room plan remain estimates or conceptual interpretation.
- Root must integrate through Placement_massing_house_301838781_891384f and verify campus-world placement.
- Do not merge the separate FID 841 polygon without confirming its identity.

## Visual review

The front and three-quarter renders show a coherent brick facade, regular windows, white portico and columns, curved entry rail, doors, address and stairs. The interior cutaway includes floor plates, partitions and room-use cues, but is schematic rather than a verified plan. Flat roof, parapet, facade dimensions and exact vertical arrangement remain estimates.

The local asset opens and is self-contained. Master placement through the expected Placement marker remains pending root integration.
