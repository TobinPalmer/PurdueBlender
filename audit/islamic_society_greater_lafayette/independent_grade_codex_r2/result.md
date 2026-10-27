# Independent Exact-Hash Grade — Islamic Society of Greater Lafayette

**Result: 7.9/10 — below the 8.0 threshold.** This evaluation applies only to SHA-256 `c84126f5b1f549db17faa7282e449fc6de171e632b6e627062ad46379247c39b`. I reopened the exact file in Blender 5.2.3 LTS; the fresh-open passed. Details are in [fresh_open_probe.json](fresh_open_probe.json).

## Strengths

- The model uses the returned Purdue FID 771 ring without scale changes; my fresh-open comparison found the 11 shell-ring points within 0.00001437 m of base vertices.
- The facade captures the prominent brick walls, two visible bands of openings, pale entry surround, and small domed canopy in the available labeled photo. The roof-plan snapshot supports two intersecting hip-roof volumes.
- Six portable materials are present; the file has no external image or linked-library dependencies.

## Why it is below threshold

FID 771 is labeled “Muslim Student Association / 1021 FIRST ST.” while the current ISGL page and labeled image identify ISGL at 1022 1st St. Purdue’s 2022 event page connects the site with MSA activity, so the physical-site match is strong, but the official GIS identity/address crosswalk remains unresolved. This uncertainty limits the identity score.

The roof planes, pitch and overall height are estimates, and the single available facade image is cropped and not georeferenced. The facade and materials read cleanly but remain simplified at close scale. No interior is modeled; the prior evidence package did not find a reliable floor plan. A schematic gathering/prayer-room interior could be labeled clearly as an interpretation rather than a measured plan.

## Weighted review

| Criterion | Score | Weight |
| --- | ---: | ---: |
| Identity and source attribution | 7.8 | 10% |
| Structural footprint and campus placement | 9.8 | 22% |
| Roof silhouette, floors, and height | 7.0 | 15% |
| Facade and entrance character | 7.5 | 18% |
| Materials and texturing | 7.8 | 12% |
| Interior representation | 4.0 | 8% |
| Geometry detail and visual finish | 7.5 | 5% |
| Portability, reopen, and evidence | 9.5 | 10% |

Weighted total: **7.917/10**, reported as **7.9/10**.

## Highest-value revisions

1. Resolve or keep the GIS name/address caveat explicit in the README and manifest; do not call FID 771 an exact formal ISGL crosswalk.
2. If the project requires interior detail, add a modest, clearly labeled schematic interior without implying it comes from a floor plan.
3. Improve subtle brick and slate relief/roughness, and refine roof/facade forms only when a suitable source supports the change.
4. Keep roof/floor heights and unseen elevations labeled estimated until stronger evidence is available.
