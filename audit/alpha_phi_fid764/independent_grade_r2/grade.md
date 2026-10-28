# Independent grade — Alpha Phi (FID 764)

**Reviewed:** 2026-10-28  
**Artifact:** `modular/buildings/massing_house_301841331_735e92f.blend`  
**Result:** **7.6 / 10 — below the 8.0 pass threshold**

This grade evaluates the saved asset and the supplied evidence packet. I did not edit the asset, its build scripts, or existing evidence. The main strength is faithful reproduction of the named Purdue GIS feature. The main deductions are the unsupported and geometrically discordant roof, low-confidence elevations, a schematic interior whose preview omits building context, and visible technical/presentation limits.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Basis |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.5 | 1.90 | Live Purdue GIS feature is Alpha Phi at 801 David Ross Rd; chapter identity and the rights-aware house illustration provide corroborating context. Retrieval, source ID, CRS, and raw response are documented. The GIS ring itself is not independently verified against a survey or current aerial. |
| Plan and placement | 20% | 8.4 | 1.68 | The asset wall base follows all 16 transformed ring vertices with reported maximum error 0.000058 m / RMS 0.000041 m, no correction, and 40.16 × 28.57 m bounds. This is a by-construction check against the supplied ring, not proof the ring is the current wall line or independent ground-control validation. |
| Exterior | 20% | 6.8 | 1.36 | Brick-colored walls, windows, entrance, stairs, and a recognizable house mass are present. The drawing supports only qualitative cues. Wall/story height, window rhythm, gable size/form/direction, and chimney are estimates. The broad 28.4 × 23.5 m gable dominates the irregular footprint; its estimated ridge axis (53.13°) differs 42.06° from footprint PCA (11.07°), with no source resolving the conflict. The exterior preview is readable but noticeably dark and the sign is not legible at this view. |
| Materials | 10% | 7.5 | 0.75 | Procedural/native brick, stone, glass, roof, wood, and interior materials are named and packed without external texture dependencies. Only brick/building identity and an entrance are supported by the drawing; trim, shutters, glazing color, and palette details are interpretive. |
| Interior | 15% | 5.5 | 0.83 | Upper bedrooms and a lounge/furnishing scheme are clearly marked as illustrative and are placed inside the source polygon. No floor plan or room arrangement is verified. The saved top-down preview isolates two bedroom modules on a dark field, without the building outline or location context, so it does not communicate an integrated cutaway well. |
| Technical presentation | 15% | 7.2 | 1.08 | Independently opened the saved file with Blender 5.2.3: expected scene/collection/object names, one mesh object, identity transform, 4,019 vertices, 5,965 edges, and 2,881 faces. The reported 451 boundary/non-manifold edges were reproduced; the composite mesh is not watertight or fabrication-ready. Exterior framing is adequate, but lighting/material separation is dark; the interior view lacks a context frame. |
| **Total** | **100%** |  | **7.60 / 10** | **FAIL — below 8.0** |

Weighted calculation: (9.5 × 0.20) + (8.4 × 0.20) + (6.8 × 0.20) + (7.5 × 0.10) + (5.5 × 0.15) + (7.2 × 0.15) = **7.60**.

## Independent checks and evidence inspected

- Read `modular/AGENTS.md`, `audit/alpha_phi_fid764/review_handoff.md`, `evidence.json`, `plan_comparison.json`, `fresh_open_validation.json`, `source_observation.json`, the live GIS response and layer metadata snapshots, and the supplied renders.
- Queried Purdue's current BuildingShapesZip4 layer for FID 764 and layer metadata directly. The live query returned exactly one feature (`BUILDING_N=Alpha Phi`, `ADDRESS=801 David Ross Rd`, `NUM_LEVELS=1`, `Shape__Area=945.6015625`) and spatial reference 102100/latestWkid 3857; its JSON matched the retained live-response snapshot. The layer metadata identifies `BuildingShapes`, polygon geometry, and the same CRS. The source contains `Level_=8`, `NUM_LEVELS=1`, and `CountOfFlo=1`; `Level_` semantics are unclear, so this is a source-field ambiguity, not evidence of an eight-story building.
- Independently opened the `.blend` via Blender 5.2.3 background mode without saving. The saved file contains one scene object and one asset collection as expected. Mesh health agrees with the recorded counts.
- Reviewed the Etsy listing's text and accessible image description. It identifies a pen-and-ink reproduction of the Purdue Alpha Phi house, describes a brick building with Alpha Phi sign and entry stairs, and states the images may not be duplicated. No source image was copied or retained. This is qualitative, non-measured exterior evidence only.
- The source polygon has 16 unique vertices. Its ring-to-wall overlay establishes model-construction fidelity to that ring, not independent geospatial accuracy, surveyed wall placement, floor count, dimensions, or current as-built state.

## Limitations that remain

- `NUM_LEVELS=1` and `CountOfFlo=1` conflict with the modeled two-level interpretation; `Extrution=12` has undocumented semantics/units, and `Level_=8` is ambiguous. The modeled 7.4 m wall and 10.0 m ridge heights are estimates.
- The main roof form, footprint coverage, ridge orientation, eaves, gable ends, chimney, fenestration, entry location, and facade details are unverified. The footprint PCA/ridge disagreement is material, not an independently validated correction target.
- Interior partitions, room count, bedroom/lounge placement, circulation, and furnishings are invented representative inserts; no floor plan is retained.
- There is no georeferenced orthophoto, survey, CAD wall plan, verified elevation, or current street-level photograph in the packet. An exact overlay to the GIS ring cannot establish that the GIS ring is a current wall footprint.
- The mesh has 451 boundary/non-manifold edges, due to open/intersecting composite and decorative geometry. It is acceptable only as a visual architectural composite, not a closed solid.
- The exterior and interior renders are serviceable evidence but underlit/context-poor. The upper-room image does not show how the schematic inserts relate to the full footprint.

## Corrections needed for a pass-quality revision

1. Add independent current geometry evidence if available (survey/CAD or georeferenced aerial) and compare the GIS polygon with the visible wall footprint before describing plan/placement as verified.
2. Resolve the roof orientation and coverage using a dated elevation/aerial/CAD source. Until then, revise the single broad roof so its axes and coverage are consistent with the footprint's principal wall directions, or use a deliberately conservative roof mass rather than asserting a detailed gable. Retain the uncertainty either way.
3. Re-render the exterior with brighter, neutral fill and a view that makes the entrance/sign and major roof planes readable. For the interior, show the full footprint or an exterior cutaway context around the room modules and label the floor/rooms schematic.
4. Keep the two-level/interior interpretation explicitly estimated until a floorplan or other authoritative evidence resolves the source fields. If a clean solid is needed for downstream use, separate or close intentionally open components and recheck mesh health; the current mesh is not watertight.

## References

- Live feature endpoint: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D764&outFields=*&returnGeometry=true&outSR=3857&f=pjson`
- Live layer metadata: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson`
- Purdue Panhellenic chapter page: `https://www.purduepanhellenic.com/cost/alpha-phi`
- HUBERart listing: `https://www.etsy.com/listing/237335509/alpha-phi-sorority-house-purdue`
