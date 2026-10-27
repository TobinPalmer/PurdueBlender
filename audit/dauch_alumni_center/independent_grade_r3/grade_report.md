# Independent grade — Dauch Alumni Center R3

**Score: 8.45/10 — PASS (minimum 8.0).** Exact inspected asset SHA-256: `de1e3735f6b9f206f53cc1affb13c208ae62e96f1322eea6aeed378af9d37d14`. The file was reopened in a separate Blender 5.2.3 LTS process and its shell was independently compared with the Purdue GIS feature.

## Rubric

| Criterion | Score | Evidence and finding |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2.00 | Building identity and plan geometry are strongly and directly supported by the official Purdue GIS footprint. |
| Position, orientation, and scale/dimensions | 1.90/2.00 | Horizontal placement, orientation, and footprint scale are well supported. Decorative bounds extend beyond the GIS wall footprint as expected; height and exact architectural dimensions are separately uncertain. |
| Evidence-backed height, floors, and roof form | 1.25/2.00 | R3 fixes the incorrect winding and flat striped roof presentation, but the roof curve and vertical dimensions are not measured, and the story-count conflict remains unresolved. |
| Facade, entrances, and distinctive architecture | 1.50/2.00 | Recognizable brick-and-glass character and entrance/site identity are represented; facade details and interiors remain interpretive. |
| Modular export, portability, and complete evidence | 1.80/2.00 | The library is portable and well documented. Master linkage and shared manifest refresh are outside this isolated asset grade; the bounds report is ready for coordinator integration. |

## Fresh-open findings

- The expected scene and collection reopen with the requested SHA. The collection contains 663 objects (659 meshes).
- The official FID 71 outer ring has 109 unique points; maximum nearest-point error to the structural shell is 0.00000146 m. The local placement origin matches the transformed polygon centroid within 1e-11 m.
- The shell is watertight, has no zero-area faces, and has positive signed volume 25,313.66 m³. All 109 side faces point outward; top and bottom caps point up and down.
- The roof membrane has 1,075 vertices and rises approximately 0.90 m above the structural cap. It is a curved, neutral-gray surface, though the exact profile/elevation remains estimated.
- Used materials are node-based and no external image files are referenced.

## Remaining uncertainty

The GIS reports four levels while Purdue’s historic database says three stories; no measured section resolves this. Roof and total height, roof profile, facade bay dimensions, most unphotographed elevations, and interior room locations remain estimates or schematic. Sign and planting positions are photo-based approximations.

Probe data: `fresh_open_probe.json`; Blender log: `blender.log`; evaluator: `evaluator.py`.
