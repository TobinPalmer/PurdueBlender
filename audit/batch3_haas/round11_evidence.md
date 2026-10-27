# Felix Haas Hall — round 11 model update

**Asset:** `modular/buildings/felix_haas_hall.blend`
**Stable ID / export:** `felix_haas_hall` / `Asset_felix_haas_hall`
**Exact saved SHA-256:** `e333a99e9b7bbb3288329afad7af177be62d73d9077146a4a579c4b123cb1ec1`
**Saved and reopened:** Blender 5.2.3 LTS, 2026-10-27

## Evidence used

- Purdue Events, [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall), current official page and exterior image; checked 2026-10-27. The image has no published capture date, camera calibration, CRS, or measured elevations. It supports qualitative visible details: red-clay tile roof, masonry/stone palette, arched lower windows, central arched entry, and entrance stair.
- Purdue Archives and Special Collections, [Felix Haas Hall corporate-entity record](https://archives.lib.purdue.edu/agents/corporate_entities/563), checked 2026-10-27. It identifies Felix Haas Hall as the former Memorial Gymnasium and records construction in 1908.
- Purdue University Timelines, [historic Purdue timeline](https://collections.lib.purdue.edu/timelines/puhistorical), checked 2026-10-27. It records the 1909 dedication and states that 17 steps lead to the main entrance; the existing 17-tread asset detail was retained.
- Purdue Computer Science, [HAAS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf), previously preserved in this building audit. It supports first-floor room names and broad adjacencies only; it is nondimensional and does not verify openings, metric scale, upper stories, or finishes.
- The existing official GIS shell evidence and coordinates were left unchanged; the prior round-10 reopen record reports the structural shell bounds `[[-26.2203, -25.9795, 0], [12.9812, 26.7597, 11.5]]` m. This shell remains a plan-envelope reference, not evidence for wall height, roof, façade, or interior accuracy.

The local coordinate method and uncertainties remain those in the existing building evidence records. The photograph has no CRS; no geometric dimensions were inferred from its perspective. Added portal/window dimensions and the 1.8× roof-rise adjustment are explicitly estimated.

## Changes in round 11

- Added segmented limestone voussoirs, jambs, capitals, and bases to give the central entrance a deep arched surround. Added an arched glazed transom.
- Added matching segmented stone surrounds and sills around the two photo-visible lower arched windows. Recessed the existing glazing behind the new stonework.
- Archived the superseded blank portal panel, straight entry jamb/lintel and thin earlier lower-window surrounds in the hidden `Reference_Incompatible_Geometry_felix_haas_hall` collection; these objects are preserved for provenance and are excluded from the exported asset collection.
- Refined the procedural roof tile shader to a red-clay color and subtle relief based on the official image. No image texture files or external dependencies are used.
- Raised the estimated roof rise by 1.8× above the existing 11.7 m eave while retaining its plan footprint. This remains an estimate from qualitative imagery.
- Corrected brick and limestone node colors to better match the photographed warm red brick and pale stone palette.
- Preserved the original GIS shell and local XY placement. The saved export collection now contains 919 objects and 879 meshes; local mesh bounds are `[[-26.534997940063477, -26.299999237060547, -0.021764706820249557], [19.13599967956543, 27.0, 15.84000015258789]]` m. Coordinator must refresh the shared manifest object count/bounds and master-linked library when integrating.

## Validation

- Fresh-opened the exact saved file in Blender 5.2.3 LTS. SHA matches `e333a99e9b7bbb3288329afad7af177be62d73d9077146a4a579c4b123cb1ec1`.
- Rendered and inspected `exterior_round11.png`, `entrance_round11.png`, and `interior_plan_round11.png`; the entry/window voussoirs, glazing recess, and tile texture are visible.
- BVH triangle checks covered all 53 newly added meshes. They found **zero round-11 intersections with pre-existing exported meshes**. Remaining intersections are deliberate contacts between the new arch stones, capitals, jambs, impost bands, and sills. The 17-step stair remains; entry plinths were raised to remove the initial stair overlap. See [`round11_intersections.json`](round11_intersections.json).
- Reopened asset has no external images or image-texture nodes; all newly changed materials are procedural.
- Full metrics and render paths: [`round11_validation.json`](round11_validation.json).

## Remaining uncertainty

The official photo is a perspective image and does not establish roof pitch, façade stationing, opening dimensions, stone relief depth, wall heights, or unseen elevations. The interior remains a clearly labeled schematic derived from a nondimensional first-floor plan; it is not a verified full interior. No building was added to the master and no shared indexes were edited.
