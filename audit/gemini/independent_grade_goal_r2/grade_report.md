# Independent grade — Gemini Cooperative, Purdue GIS FID 825

**Result: 7.2/10 — below the 8/10 threshold.** The evaluator freshly reopened the specified standalone asset with Blender 5.2.3 LTS. SHA-256 was `dd9789003b208747d2f80d4c4af35d27900ce2f7debcfea18c4f1a473f5c25a8` before loading, after loading, and after evaluation.

| Criterion | Score | Independent assessment |
|---|---:|---|
| Identity and official footprint | 2.00/2.00 | FID 825 is Gemini at 172 Littleton St. The reopened 14-point slab outline matches the converted GIS ring to 0.00001 m rounding. This validates the slab outline, not the facade offset or campus master placement. |
| Scale and placement | 1.15/1.50 | Metric units, centroid-local geometry, and slab dimensions align with the outline. Ridge/story heights are photo estimates; the master placement marker was not part of this isolated-asset review. |
| Roof form and height evidence | 1.25/2.00 | Three ranges, two front cross-gables, dormer elements, and three chimneys improve the silhouette. The current model still reads as a broad continuous roof, with shallow block dormers and schematic gable intersections. Heights are not surveyed. |
| Facade and entrance | 1.25/2.00 | The brick base, pale siding, windows, and covered entry recall the reference. The current photo shows distinct wings, an asymmetric opening rhythm, and a recessed central porch with a broad stair/landing and continuous railing; those proportions and facade rhythm are not yet convincing in the model. |
| Materials, interior, and portability | 1.55/2.50 | Named materials are present and every mesh has a material. Three schematic levels include room partitions, corridor walls, and common-room props, but are not based on an authoritative plan. A fresh open found 936 meshes, 10 materials, no linked libraries, and no unpacked external images. |
| **Total** | **7.20/10.00** | **Below threshold** |

## Evidence and limits

- **GIS:** Purdue University GIS BuildingShapesZip4, FID 825, EPSG:4326, retrieved 2026-10-27. The raw feature is in [`../fid825.geojson`](../fid825.geojson). The evaluator applies the project's approximate lon/lat-to-local-meter conversion and compares the 14 XY vertices of the freshly reopened slab. Approximate GIS transformation and possible differences between mapped outlines and wall faces remain limitations.
- **Photo:** current official Gemini Cooperative exterior photo, retrieved 2026-10-27 from the official site's Wix CDN: [official house page](https://www.geminicooperative.com/about). The source image is [`../official_home_exterior.jpg`](../official_home_exterior.jpg). It supports the identity, brick/siding composition, stepped roof ranges, gables, dormers, chimneys, and entrance comparison; it does not establish surveyed dimensions.
- **Height and interior:** the asset reaches approximately 13.62 m including chimneys. Roof and story heights remain visual estimates. The GIS attributes `NUM_LEVELS=1` and `CountOfFLO=1` conflict with the photo's apparent multi-level exterior; their meaning is unclear. No authoritative floor plan or measured elevation was available.
- **Portability:** the exact blend was loaded in Blender 5.2.3 LTS; expected scene and collection were present, all mesh objects had material assignments, and no external linked library or unpacked image dependency was found.

## Fixes to reach 8/10

1. Match the photo's separated, stepped wing roof silhouette with clearly intersecting gables/valleys and varied eave heights while preserving the mapped wall outline. Keep heights labeled estimated until measured evidence exists.
2. Rework the front composition around the recessed center porch: increase its visual depth, show the broad landing and stair, and carry a continuous railing across the approach.
3. Vary the window sizes and positions by wing to follow the asymmetrical reference facade instead of the more regular grid.
4. Give dormers visible pitched caps and cheeks, and revise their spacing and size variety to match the photo.
5. Keep interior geometry explicitly schematic unless a reliable floor plan is found; use a clear cutaway/floor inspection view if interior review matters.

Detailed measurements, criterion data, source metadata, fresh-open results, and SHA checks are in [`result.json`](result.json); the runnable evaluator is [`evaluator.py`](evaluator.py).
