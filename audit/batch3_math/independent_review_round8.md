# Mathematical Sciences Building — Independent R8 Review

**Reviewed:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Result:** **7.7/10 — below the 8.0 target.**  
**Scope:** Saved source, R8 validation/evidence, both R8 library renders, current exterior/elevation renders, and a read-only check of the on-disk master placement. No model, master, or shared index was changed.

## Category scores

| Category | Score / 10 | Finding |
|---|---:|---|
| Identity and footprint | 9.1 | Purdue Archives supports the ten-story MATH identity. GIS feature 227 is identified and the shell’s bounding edges differ from GIS bounds by at most 0.00434 m. The separate bidirectional structural-edge comparison is less exact at isolated portions: medians are about 0.09 m, but maxima reach 1.54–1.95 m. These are not survey tolerances. |
| Placement and orientation | 9.6 | Read-only inspection of `purdue_campus_master.blend` found one `Placement_math_sciences` instance linked to `Asset_math_sciences`; its resolved library is the assigned source file, translation is `[-181.119995, -126.904999, 0]` m, scale is `[1,1,1]`, and rotation is zero. Translation matches the manifest within 0.02 m. |
| Roof and height | 4.8 | The archive supports ten stories, but the 33.2 m shell height, 42.9 m total bound, floor intervals, rooftop penthouse/monitor, and parapet profile lack measured elevation evidence. The exterior renders show a broad, simple roof mass that remains unverified. |
| Exterior and texturing | 6.5 | The modeled main facade has red brick, pale vertical reveals/piers, and repeated narrow window bays consistent with the available Purdue Statistics photo. The material reads as a fairly uniform pale pink in the overview, and large blank wings plus weakly supported north/west elevations remain visible. The photo does not identify its elevation or validate the full window schedule. |
| Interior and circulation | 7.0 | R8 fixes the previous vertical disconnect: the library finish now meets the modeled F03 slab at z=6.58 m, and the plan render shows a continuous inferred connector toward the elevator core. The 2022 plan supports core/zones, while the 2025 article supports library use and finish types. The R8 oblique remains hard to read at overview scale; room boundaries, corridor width, furniture positions, stair geometry, and exact current layout remain partly schematic. |
| Technical integrity and verification | 9.3 | Blender reopened the saved asset. The expected collection is present, the 249-object vertical adjustment is documented, the east sign is absent, 81 selected pane-center rays clear and six solid-wall controls hit brick, and there are no unpacked image dependencies. These checks verify the saved asset and selected geometry, not full building fidelity. |

Overall score is the arithmetic mean of the six category scores, rounded to one decimal place: **7.7/10**.

## R8-specific finding

The vertical alignment correction is successful as an internal consistency change: the modeled third-floor library finish top and F03 slab top both reopen at z=6.58 m; stairs span z=6.605–9.545 m; elevator doors span z=6.685–8.885 m; and the narrow core connector spans z=6.582–6.600 m. The renovation plan supports a library-to-core relationship, but not these absolute elevations or corridor dimensions. This materially improves circulation readability and removes the prior multi-meter floor mismatch. It does not establish as-built accessibility or exact circulation.

The plan render communicates the room bands, furniture, and route more clearly than the earlier cutaway. The oblique render still presents the whole floor as a small cluster of low-contrast gray geometry, so it is weak as a standalone interior-fidelity view. This is a presentation limitation as well as an evidence gap; it is not evidence that the underlying layout is measured.

## Remaining evidence-based fixes

1. Find a surveyed elevation, facilities drawing, or reliable height source before changing the shell height, floor spacing, penthouse, roof, or mast. Ten stories alone cannot set metric elevations.
2. Locate dated, identifiable photos or elevations for the north and west sides before filling in the blank facade wings. The current exterior photo supports only the visible photographed facade.
3. Improve the material/render comparison for brick color, window reveals, and roof finish using a larger, direction-identified source image; the current overview appears much flatter and paler than the brick reference.
4. Keep the 2022 floor-plan geometry and inferred corridor width labeled as schematic until an as-built plan is found. A clearer close interior view would make the R8 changes easier to judge, but would not replace plan evidence.
5. Preserve the current master transform: the read-only check passes. The GIS-edge outliers should be investigated only against structural wall geometry and source polygon shape, not by scaling the whole asset to its bounding box.

## Evidence consulted

- R8 validation: `round8_validation.json`; R8 alignment record: `round8_vertical_alignment.json`; model history and limitations: `REVIEW.md`.
- R8 renders: `library_plan_round8.png`, `library_oblique_round8.png`; exterior set: `exterior_after.png` and the four directional `exterior_*_after.png` files.
- Footprint comparison: `structural_edge_comparison.json` (bidirectional sampled structural-centerline-to-GIS-boundary distances; not polygon IoU or a survey).
- Master registration, inspected read-only: `independent_review_round8_registration.json`.
- [Purdue Statistics exterior photo](https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg), [Purdue Archives MATH record](https://archives.lib.purdue.edu/agents/corporate_entities/672), [2022 Purdue Board third-floor renovation plan](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf), and the [Purdue Libraries 2025 reopening article](https://blogs.lib.purdue.edu/news/tag/general/page/6/).
