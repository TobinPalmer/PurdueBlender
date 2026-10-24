# Mathematical Sciences Building — Independent R10 Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Grade:** **7.9/10 — below the 8.0 target.**  
**Scope:** Reopened/validated R10 source evidence, checked the R10 DSM/DTM analysis and retained roof geometry, and visually reviewed the saved exterior and third-floor library views against the available Purdue photo and Board plan. No Math asset or shared project files were edited for this review.

## Category scores

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 9.1/10 | Purdue GIS FID 227 is used for the footprint mask and the ten-story identity is supported by the Purdue Archives record. The modeled shell bounding box closely follows the GIS bounds, but the approximate edge comparison is not survey control and does not prove every wall edge. |
| Placement and orientation | 9.6/10 | The R8 read-only master registration check still shows one `Placement_math_sciences` instance referencing the expected relative asset path, at the manifest translation within 0.02 m, zero rotation, and unit scale. R10 makes no master or placement edits. |
| Roof and height | 5.2/10 | R10 adds reproducible 2018 3DEP evidence: 5-ft DSM minus same-tile resampled bare-earth DTM gives footprint p50 36.92 m, p90 40.25 m, and p95 40.43 m above terrain. The modeled roof slab is only 33.2–33.4 m and coping top 36.5 m. This exposes a material 3.5–3.9 m mismatch, but the raster mask includes roof equipment/edges and cannot say whether the shell, penthouse, or another component is low. No geometry changed, and the ten-story count does not establish these elevations. |
| Exterior and texturing | 7.0/10 | The embedded red-brown brick shader and repeated window bays read coherently in the exterior views. The one available Statistics photo is not direction-registered or color-calibrated and cannot validate the broad blank elevations, exact bay layout, roof, or brick color. The north and west views retain substantial blank wall faces; no source supports filling them yet. |
| Interior and circulation | 7.1/10 | The third-floor view presents the library/core and visible furnishing layout. The 2022 Board plan supports major third-floor zones/core relationships, and the 2025 library photo supports material and program cues. Exact current partitions, circulation widths, furniture positions, and complete stair/elevator continuity remain schematic; no current as-built plan was available. |
| Technical integrity and evidence | 9.5/10 | Blender 5.2.3 reopened the saved asset; R10 validation reports 550 direct and 593 total collection objects, expected shell/roof/penthouse bounds, required provenance annotations, no unpacked images, and no master/shared edits. The new analysis names the tile, acquisition date, source CRS, URLs, checksums, raster resolutions, footprint, method, and uncertainty. The measured heights remain approximate rather than architectural elevations. |
| **Mean** | **7.9/10** | **Below target.** The R10 evidence improves the diagnosis of height uncertainty, but does not correct the shell/roof or resolve the missing facade and interior source evidence. |

## R10 findings

The height workflow is materially better documented than the R9 record. It identifies the 2018 Indiana 3DEP tile and the matching bare-earth product, preserves their checksums, and avoids assigning the observed upper surface to a story or roof component. The central result should be treated as a height conflict: the median normalized lidar surface is about 36.9 m while the current shell roof slab is about 33.2 m. The high tail is not proof of a specific penthouse outline or antenna. The analysis notes the 5-ft cell size, footprint contamination, and unverified vertical datum, so geometry should not be shifted on these statistics alone.

R10 does not alter facade or interior geometry. Exterior renders still show an incomplete surface treatment on the broad blank north/west faces, while source imagery is too poorly registered to support invented windows. Interior plan/render pairing is useful for review, but the render is not evidence of a fully as-built circulation network. These unresolved items hold the visual-fidelity categories below the finish threshold.

## Next evidence-led steps

- Obtain an inspected, direction-identified elevation or calibrated current exterior image before changing blank facade faces, opening cadence, or roof shape.
- Resolve the roof-height mismatch with a measured elevation or a spatially aligned roof survey; do not map the DSM percentile directly to a particular story, parapet, mast, or penthouse component.
- Keep the third-floor scheme labeled illustrative until a current as-built plan can be reviewed through an authorized source.

## Files reviewed

- `evidence_round10.json`, `round10_validation.json`, `math_roof_dsm_r10.json`, and `math_source_inventory_r10.json`.
- `exterior_after.png`, cardinal exterior views, `brick_detail_after.png`, `library_after.png`, `third_floor_core_after.png`, and `math_dsm_roof_height_r10.png`.
- 2018 Indiana 3DEP DSM/DTM source links and the 2022 Purdue Board library renovation plan linked in the evidence record.
- `independent_review_round8_registration.json` for the existing master placement check.

The new grade is independent of the R10 agent's prior R9 score. R10 demonstrates better source accounting, but the saved building remains below 8.0/10 because height, roof, facade coverage, and interior circulation are still unresolved.
