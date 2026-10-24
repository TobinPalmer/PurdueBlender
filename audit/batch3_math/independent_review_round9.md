# Mathematical Sciences Building (MATH) — Independent R9 Review

**Reviewed:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Result:** **7.8/10 — below the 8.0 target.**  
**Scope:** Saved asset evidence, R9 validation, R9 exterior and interior renders, R8 independent scorecard and registration record, and the stated official sources. No asset, master, or shared index was modified.

## Category scores

| Category | Score / 10 | Finding |
|---|---:|---|
| Identity and footprint | 9.1 | Purdue Archives supports MATH as a ten-story building. GIS FID 227 and the unchanged structural bounds agree closely at the bounding-box edges (max delta 0.00434 m); sampled polygon-edge maxima are still about 1.54–1.95 m and the GIS is not a survey. Identity and envelope are well supported, but the comparison does not prove every structural edge. |
| Placement and orientation | 9.6 | R8's read-only master check found one `Placement_math_sciences` instance referencing the expected relative source path, at the manifest transform within 0.02 m, zero rotation, unit scale. R9 says no master changes were made, so that evidence remains applicable. |
| Roof and height | 4.8 | R9 did not change the roof or height. The archive supports story count only; the 33.2 m shell height, 42.9 m maximum extent, floor spacing, penthouse/monitor, parapets, and mast remain estimates without measured elevations. The broad penthouse panels are visually prominent and unsupported by a direction-identified source. |
| Exterior and texturing | 7.0 | R9's restrained red-brown brick is visibly closer to the limited Purdue Statistics photo than R8's paler pink result, and the material reopens at its documented values. The adjustment is qualitative, not calibrated. The 196×258 photo is not georeferenced and does not identify the modeled elevation; it cannot validate the full opening schedule, blank wings, reveals, roof, or exact brick/mortar color. |
| Interior and circulation | 7.1 | The R9 oblique view is more legible than R8 and displays the aligned library/core relationship. The 2022 Board plan supports third-floor zones/core relationships and the 2025 Libraries article supports a refreshed library use. The walls, furniture, stairs, exact corridor, room dimensions, positions, and as-built arrangement remain schematic. The R9 view is a presentation improvement; it does not add interior evidence or detail. |
| Technical integrity and verification | 9.3 | Blender reopened the saved R9 asset, expected collection and 550 direct/593 total object counts are recorded, shell bounds are unchanged from R8, the connector remains, material values reopen, and no unpacked image dependencies were found. These checks support file integrity, not full architectural fidelity. |

**Scoring method:** Arithmetic mean of the six category scores, rounded to one decimal: (9.1 + 9.6 + 4.8 + 7.0 + 7.1 + 9.3) / 6 = **7.8/10**.

## R9 assessment and remaining fixes

The brick change is a real visual improvement: the close exterior render now reads as red-brown rather than pale pink, consistent with the direction of the available Purdue Statistics exterior image. It does not resolve the principal blockers from R8. The roof and overall vertical envelope remain unverified; the large rooftop panel arrangement and shell/story proportions still lack measured elevation evidence. The visible exterior still contains broad blank wall areas and inferred facade details that the current photo cannot validate. The interior view is easier to inspect but its geometry and circulation remain illustrative rather than as-built.

The 8.0 threshold is not reached. Evidence-supported next steps are: locate a measured elevation or building drawing before altering heights/roof; find dated, direction-identified photos of the north and west elevations before adding openings; and locate an as-built third-floor plan before changing partitions, passage dimensions, or room arrangement. Keep the current red-brown treatment labeled qualitative unless a calibrated or better-identified color reference is found.

## Evidence reviewed

- `round9_validation.json` and `evidence_round9.json`.
- R9 renders: `exterior_brick_r9.png`, `library_oblique_round9.png`.
- R8 prior independent scorecard: `independent_review_round8_scorecard.json`; master placement check: `independent_review_round8_registration.json`.
- Purdue Statistics exterior photo: https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg — supports a red-brown brick appearance and repeated narrow window bays on one unidentified facade; date, orientation, and color calibration unknown.
- Purdue Archives MATH record: https://archives.lib.purdue.edu/agents/corporate_entities/672 — supports the ten-story identity, not metric height.
- Purdue Board third-floor library plan: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf — supports core/zones, not an as-built measured arrangement.
- Purdue Libraries 2025 reopening article: https://blogs.lib.purdue.edu/news/tag/general/page/6/ — supports current library-use context and finish/furnishing types, not exact placement.

No changes were made to MATH, master, or shared project files. The score is an independent review of the evidence provided and is not a claim that the building is fully verified.
