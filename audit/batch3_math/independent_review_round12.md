# Mathematical Sciences Building — Independent R12 Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Grade:** **8.1/10 — meets the 8.0 project threshold.**  
**Method:** Five `AGENT.md` criteria, each worth 2 points. This is an independent, read-only review. R12 made no geometry changes.

## Criteria

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9/2 | Purdue's own Statistics page labels its image as Purdue's Math Building, while the 2009 Flickr image independently identifies the building. GIS FID 227 and the prior footprint comparison support the plan envelope. The existing approximate local geographic transform and AABB comparison are not survey control or a wall-by-wall footprint verification. |
| Position, orientation, and scale/dimensions | 1.9/2 | Retained R8 master-registration evidence records one expected `Placement_math_sciences` instance at the manifest origin within 0.02 m, zero rotation, unit scale, and a relative asset path. R12 did not repeat a fresh master check; the coordinate transform remains approximate. |
| Evidence-backed height, floors, and roof form | 0.9/2 | Historical Purdue evidence supports the ten-story identity, and R11/R12 images support only a qualitative parapet and raised roof-edge silhouette. Modeled shell, roof slab, and coping top out at 33.2 m, 33.4 m, and 36.5 m, respectively, while the R10 DSM-minus-DTM surface statistics remain higher. Those broad 5-ft raster returns do not identify which modeled roof object or story is responsible. Exact roof elevations and component attribution remain unresolved. |
| Facade, entrances, and distinctive architecture | 1.6/2 | The official department image and independent Flickr photograph corroborate the building's red-brick tower, repeated vertical window groups, simpler end/corner bays, lighter lower entrance zone, and raised/parapet roof edge. The saved exterior renders reproduce these broad motifs. However, the sources do not establish compass bearing or tie the photographed elevations to a model cardinal face; they do not verify present-day condition, exact openings, calibrated colors, or the exact entrance arrangement. The model's broad blank wall zones therefore remain only partly verified. |
| Modular export, portability, and complete evidence | 1.8/2 | Blender 5.2.3 reopened the saved asset with the expected collection, 550 direct / 593 inclusive objects, stable recorded bounds, no unpacked images, and zero R12 geometry changes. The photo inventory and evidence log preserve URLs, observations, dates, and uncertainty. The current master placement check is retained from R8, and no direction-registered current elevation or as-built interior plan is present. |
| **Total** | **8.1/10** | **Meets the threshold, narrowly.** |

## Independent source checks

The [Purdue Statistics Getting Started page](https://www.stat.purdue.edu/external_relations/statcom/getting_started.html) labels the embedded photo “Purdue's Math Building - Home of Department of Statistics.” I inspected the linked [departmental image](https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg) directly. It shows a brick elevation with tall vertical glazed/window strips, simpler side bays, and a pale lower entrance level. The source does not state when the image was captured.

I independently opened the [Flickr page](https://www.flickr.com/photos/ataindy/4062109632/) and inspected the available original image. The owner's page caption states **taken September 26, 2009** and uploaded October 31, 2009; Flickr labels the image **All rights reserved**. The downloaded original is 2384 × 3526 px. Its embedded EXIF `DateTime` is **2009:10:29 14:29:19**, which conflicts with the owner's stated capture date. I report both values and treat September 26 as the owner's claim, not as independently proven capture time; the EXIF value likewise cannot settle the true capture date. The original has no GPS metadata. Its oblique view supports the broad facade/roof-edge motifs but cannot establish direction, dimensions, current condition, or component heights.

The image evidence improves the qualitative facade check over R11. It does **not** resolve either the camera bearing/model-face correspondence or roof elevations. The R12 source and validation records accurately retain those limitations. The saved interior render is visibly schematic; no as-built interior route or partition plan was found, so circulation and room layout remain unverified.

## Decision

**R12 scores 8.1/10 and meets the threshold.** This narrowly passing grade reflects stronger independent corroboration of facade vocabulary and a fully documented, successfully reopened standalone asset. It does not certify precise height or roof geometry, map photographed facades to compass faces, establish current openings, or verify the interior. No unsupported geometry change is recommended. The evaluator function and machine-readable result are in `independent_review_round12_evaluate.py` and `independent_review_round12_scorecard.json`.
