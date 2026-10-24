# MSEE R5 Independent Full-Building Review

**Asset reviewed:** `modular/buildings/materials_science_and_electrical_engineering_msee.blend`  
**Evidence reviewed:** `materials_science_and_electrical_engineering_msee_R5_sources.json`, `materials_science_and_electrical_engineering_msee_R5_validation.json`, R5 overview and entrance-detail renders, GIS feature 646 snapshot, and the two Purdue ECN photographs referenced in the source record.  
**Result:** **7.7/10 — below the 8.0 pass threshold.** This is an independent assessment of the saved R5 state, not a model edit.

## Category scores

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.9/2.0 | Building identity is supported by the Purdue ECN page and GIS FID 646. The four-corner footprint is retained; the reopened shell bounds are about 74.18 × 80.13 m. GIS area is 4,494 m². The shell is a simple prism with a documented two-storey atrium cut. |
| Position, orientation, and scale | 1.5/2.0 | The original asset origin and local frame are preserved, and the footprint came from the campus building layer. The evidence explicitly says the local tangent-plane conversion is approximate rather than a surveyed CRS transform. This standalone review does not establish that the collection is correctly registered against neighboring campus assets in the master scene. |
| Height, floors, and roof | 1.2/1.5 | The saved shell spans z=0.3–15.0 m (14.7 m), and the GIS record reports four levels, a 36 ft extrusion attribute, and floor elevations. Four facade window courses visually read as multiple levels. No authoritative elevation or roof drawing verifies the modeled height, roof form, or individual floor heights; the broad flat roof and small monitor remain interpretive. |
| Facade, entrance, and distinctive features | 1.4/2.0 | The dark red-brown brick, central glazed entrance, semicircular fanlight, and arch are recognizable against Purdue ECN’s exterior photograph. R5 removes the punched windows from the atrium face and makes a real opening in the shell. However, the render has highly repetitive blue window panels, a visually crowded overlap between the fanlight and adjacent window course, and an entry door panel/frame that reads as an opaque cyan rectangle. The source photo shows a darker, more integrated entrance with an arch above the doors. Window dimensions, course spacing, exact entrance dimensions, and facade orientation details remain estimates from an un-georeferenced perspective photo. |
| Interior and circulation | 0.5/1.0 | The atrium is now open through the near shell and a few table/seat cues are visible through the glazing. The archive supports a two-storey glass atrium, and the ECN interior photo supports a historic corridor only. There is no verified as-built floor plan, circulation connection, stair, skyway, or room layout represented in this R5 evidence package; the three table groups and six seats are illustrative. |
| Modular portability and evidence | 1.2/1.5 | The stable asset collection and origin are retained. R5 validation confirms reopen, 1,198 collection objects, no external image dependencies, and a watertight shell (0 non-manifold edges). The source JSON records URLs, provenance, and uncertainty. The validation pass is a technical integrity check rather than a fidelity result; it does not verify registration in the master or provenance/accuracy of the procedural facade palette. |
| **Total** | **7.7/10** | **Does not pass.** |

## Main evidence and limitations

- The official Purdue ECN exterior photograph identifies the building and supports the red-brown brick, central glazed entrance, and semicircular fanlight. It is not georeferenced, has no published capture date, and is a perspective view, so it does not support surveyed facade dimensions.
- GIS feature 646 supports the four-corner footprint and source-reported floor attributes. The model preserves the footprint bounds and origin. The feature record reports 4 levels and a 36 ft extrusion attribute; neither resolves the exact as-built roof/elevation from the provided evidence.
- Purdue Archives supports the building identity, 1988 construction, two-storey glass atrium, laboratories, and two pedestrian skyways. Those details are not enough to infer the internal floor plan or exact atrium depth.
- R5 documents the atrium opening as approximately 22.25 m wide by 8.30 m high and the 18 m cut depth as interpretive. The near-shell cut is real and watertight, but the full interior/circulation plan remains unverified.
- The rendered entry detail reveals the key visual shortfall: the fanlight is aligned over the atrium glazing but visually collides with a horizontal window band, while the central door block reads opaque and flat. These are visible in the saved R5 render, not inferred from the validation JSON.

## Recommended next corrections

1. Refine the entry assembly from the Purdue exterior reference: clarify door leaves, reduce the cyan block appearance, and resolve the fanlight/window-band overlap while keeping dimensions labeled as estimated.
2. Compare the facade bay proportions and window appearance against the same official exterior photo; avoid claiming exact dimensions from it.
3. Keep interior circulation and room programming explicitly schematic until a credible plan or section is found.
4. For a complete placement score, verify the standalone collection’s master-scene registration against the retained GIS footprint in the master without changing that shared file during this review.
