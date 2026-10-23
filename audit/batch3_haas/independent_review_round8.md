# Felix Haas Hall — independent review round 8

**Reviewed:** `modular/buildings/felix_haas_hall.blend`, opened independently in Blender 5.2.3 on 2026-10-23. Export collection `Asset_felix_haas_hall` contains 1,050 direct objects. The GIS wall envelope reopens at `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m; both roof objects retain scale 1 and zero rotation. I inspected the saved full exterior, entrance close-up, all four orthographic elevations, and first-floor plan. The 17 entrance treads are present. This confirms file continuity and reported geometry, not survey accuracy.

## Score: 7.6/10 — below 9/10

Round eight materially improves the east facade: the limestone-colored wall skin now runs across the central projection and flanking wings, with red brick surround details on the wings. Removing the unsupported north-end glazing also cleaned up the shell silhouette. The composition still reads as simplified colored panels rather than the masonry architecture in Purdue’s reference image. Important facade surfaces remain flat and nearly featureless; the brick surrounds are thin, detached-looking strips with no visible masonry courses or jamb depth. The elevation views also reveal unresolved projecting white strips/beams and a small blue artifact, while the oblique roof continues to have strong inconsistent plane shading.

| Area | Score | Findings |
|---|---:|---|
| Massing, roof, and GIS envelope | 8/10 | The footprint silhouette is coherent and the reported shell envelope and roof transforms survive reopening. Roof pitch, height/profile, and tile scale are still estimates. The oblique render has pronounced triangular tone shifts across adjoining roof planes; this may be mesh normals, material, or lighting, but it reads as a model defect. |
| East/front facade | 7/10 | Limestone coverage now spans the front wings as well as entry bay; red brick panels/surrounds add contrast. The wall reads as smooth pale plaster with clean red bars, rather than integrated limestone masonry and brick panels. Window trim and brick surround depth/coursing are too shallow to convincingly read as construction. Reference perspective does not establish exact wing limits, so keep those dimensions labeled estimated. |
| North, south, and west elevations | 6.5/10 | The four views expose inconsistent facade color from side to side and an unexplained thin white projection extending horizontally well beyond the side wall on both end views. A blue streak remains at the small side projection/junction in one view. The projections and terminal details need source validation or removal; north-end pane removal alone did not clear all edge artifacts. |
| Materials and roof shading | 7/10 | Brick and stone are now warmer and more distinct than in the earlier rounds, but fields remain too uniform and low-detail. The roof tile pattern is visible; faceted broad tonal shifts across roof planes are distracting. Recheck with neutral, even lighting and verify material continuity across roof facets. |
| Entrance and 17 steps | 8/10 | The paired doors, landing, and 17 treads are legible and align with the front projection. Tread count is supported by the Purdue timeline, but tread/riser dimensions are estimated. The pale stair/entry treatment is visually overbright relative to the warmer reference stone. |
| Interior plan | 7/10 | The plan view has labeled rooms, partitions, desk/furniture indications, stairs, elevator, and a clear schematic warning. It remains a nondimensional first-floor diagram. The supplied plan supports room names and broad adjacency, not metric registration, door locations, swings, upper stories, or current fit-out. |
| Evidence and file integrity | 8.5/10 | Asset reopens with expected collection/count, stable envelope and roof transforms, and current render set. Evidence is candid about estimated inlay geometry and nondimensional interior. GIS evidence cannot establish facade, height, roof, or interior truth. |

## Priority fixes

1. Rework the full east facade at camera scale so limestone piers/bands and red brick infill read as a single masonry composition. Add restrained courses, actual inset returns/jambs, and surface depth; do not extend exact dimensions beyond what the photo can support.
2. Inspect the thin white side projections on the north/south views and the blue mark at the junction. Identify the responsible exported objects and source them to a reference; if unsupported artifact geometry, remove it. Re-render each affected elevation afterward.
3. Resolve roof plane shading variation under neutral lighting. Check normals and material assignments across facets before tuning texture contrast. Record roof profile and tile scale as estimates.
4. Tune facade and stair materials against the Purdue photo with neutral white balance. The current east elevation has a chalky surface and the end elevations shift pink/brown; reduce this mismatch and make stone/brick distinction come from material plus geometry, not overexposure.
5. Keep the interior schematic limitation visible in its presentation and add no unsupported door placements or metric claims.

## Evidence reviewed and limits

- Purdue Events’ [Felix Haas Hall page](https://events.purdue.edu/felix_haas_hall) and the preserved `audit/batch3_haas/exterior_reference.jpg` support the qualitative Bedford-limestone/red-brick facade language, arched lower windows, central entry, stairs, and red roof. The perspective photograph does not provide measured facade extents, elevations, or inlay dimensions.
- Purdue CS’s [HAAS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports room names and broad adjacency only. It is nondimensional and does not verify door placement/swings or upper floors.
- The evidence record reports 17 steps based on Purdue historical context. The saved renders show the count but cannot independently validate tread dimensions.
- GIS shell bounds verify the current envelope only. They do not verify height, roof silhouette, facade details, or interior layout.

**9/10 decision: No.** The facade coverage and north-end cleanup are meaningful improvements, but the masonry still reads as shallow graphic overlays, side projections/artifacts remain unresolved, and roof shading undermines the overall presentation.

