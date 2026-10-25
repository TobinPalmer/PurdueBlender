# Independent review: Neil Armstrong Hall R12.9

**Score: 8.0/10 — pass threshold met narrowly**  
Asset SHA-256: `d8c78374b047fa1248d6d304db0cba1e7f39ff97d133ccc06d774eabf7558bf7`

| Criterion | Score |
|---|---:|
| Identity and source-backed footprint | 1.5/2 |
| Position, orientation, scale | 1.8/2 |
| Height, floors, roof | 1.5/2 |
| Facade and distinctive architecture | 1.5/2 |
| Modular export and evidence | 1.7/2 |

## Findings

The R12.9 NW folded canopy apex is localized and the upper curtain-wall band, mullions/transom, and horizontal sunshade fins bring the model closer to the 2016 project photographs. The facade and roof still read as schematic in places: long generic brick faces remain, while glazing bays, fin cadence/depth, and entrance connections lack dimensioned evidence.

The 2023 orthophoto and overlay support the roof/eaves plan only; they do not establish structural wall lines, the atrium boundary, or wall-to-eaves offsets. The building's four-level organization has support from Purdue OEP and FRP sources. The 21.5 m peak and roof warp remain inferred; the 21.6 m LiDAR value is only a coarse ceiling, not a measured building elevation.

A fresh Blender 5.2.3 reopen matched the requested asset hash and found the expected export collection (446 objects, 416 meshes), origin root, materials on all meshes, no null material slots, and no missing external images. The shared manifest still reports 445 objects. The present review did not reopen the current master blend, so the coordinator should reconcile the count and verify the link/placement there.

## Score rationale and limits

The score gives credit for source-supported identity, visible R12.9 improvements, origin-based modularity, and self-contained reopening. It withholds points for unverified structural footprint and dimensions, inferred roof height/profile, approximate facade details, stale manifest inventory, and no current master recheck. The asset passes at 8.0/10, but it is not fully dimensionally verified. Source photos are not calibrated views, and no public dimensioned as-built plan, facade schedule, or roof elevation was found.

Machine-readable criterion scores and evidence: [independent_grade_r12_9.json](independent_grade_r12_9.json). Evaluation script: [independent_evaluator_r12_9.py](independent_evaluator_r12_9.py).
