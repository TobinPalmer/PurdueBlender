# Felix Haas Hall — independent review round 9

**Reviewed:** `modular/buildings/felix_haas_hall.blend`, independently reopened in Blender 5.2.3 on 2026-10-23. I inspected the saved overview, entrance close-up, all four elevations, interior plan, and round-nine cleanup/reopen evidence. No model or master edits were made.

## Score: 7.8/10 — below 9/10

Round nine is a real cleanup pass. The east-main and east-wing brick inlays now have closed, bevelled relief geometry (156 and 108 faces respectively), the 65 estimated side overlays are removed, and the floating formula labels are hidden from rendering. The 17 entry treads and GIS wall envelope survive reopening. The asset is cleaner and more internally consistent, but the exterior still does not yet reach a 9: its roof has obvious tonal facets, the masonry reads as thin graphic bands, and a white projection remains at the north end. The interior plan is legible as a schematic but is not a verified interior model.

| Area | Score | Findings |
|---|---:|---|
| Massing and GIS envelope | 8/10 | The saved GIS wall mesh reopens at `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m. Its envelope is unchanged. The rendered roof reaches about 14 m, 2.5 m above the GIS wall envelope; roof height/profile remain estimated and should be labeled that way. This is not evidence of a GIS-shell displacement. |
| East facade and inlays | 7.5/10 | The inlays are now closed shallow relief geometry and are cleaner than the prior flat overlays. In the close-up, the red elements still read as thin, dark, rectangular edging around pale panels rather than brick masonry integrated with the Bedford-limestone facade. Purdue’s photo shows substantial red-brick panels and strongly modeled stonework around the central entrance and large arched openings. The current facade lacks comparable depth and visual hierarchy. Exact panel limits are not measurable from the single perspective source. |
| North, south, and west elevations | 7/10 | Removing the estimated upper/lower glazing makes these elevations more honest given the lack of a reliable side-window schedule. They now look very sparse, and the north view still shows a thin pale horizontal projection extending beyond the west end. The cleanup evidence itself records this remaining artifact. There are also thin bright eave/edge strips that read as detached in the orthographic views; inspect their intersections before deciding whether they are modeled trim or render artifacts. |
| Roof and materials | 7/10 | Lower bump strength and removal of floating labels improve the material pass, but the main overview still shows large, abrupt triangular shifts in red/orange tone across roof facets. The front roof color is vivid compared with the deeper, dark red roof in the reference. Check mesh normals/material assignment and compare with neutral, even lighting before further texture tuning. The actual roof silhouette and tile scale remain unverified estimates. |
| Entrance and steps | 8/10 | Reopen confirms 17 treads; the rendered entrance reads as centered on the projecting bay and the treads descend consistently. This supports count and visual continuity, not measured rise/run or accessibility. Pale stair and entry trim is still over-bright beside the source stone. |
| Interior plan | 6.5/10 | The plan is clearly marked as an estimate and carries room labels, desks, stairs, elevator, and broad adjacency. It remains a top-down diagram with unverified room dimensions and door positions, not a detailed interior with convincing circulation/vertical connections. Keep the schematic qualification prominent and avoid implying metric accuracy. |
| File integrity and evidence | 9/10 | The saved source reopens with 881 direct export objects. Main and entrance roof transforms are unit scale and zero rotation; no `HAAS_Estimated_Side_` objects remain in the export; formula labels are render-hidden; the GIS wall bounds and 17 treads check out. These are continuity checks, not confirmation of architectural accuracy. |

## Prioritized fixes

1. Resolve the residual north-end pale projection and check the thin bright edge strips in all elevations. Remove or integrate the responsible geometry only after confirming its identity and source.
2. Correct the roof’s triangular tonal discontinuities under neutral lighting, then tune red toward the photographic reference. Preserve the roof profile as estimated unless a measured/elevation source is found.
3. Strengthen the east facade as coherent masonry: deeper jambs/returns, more convincing stone piers and lintels, and brick fields that read as masonry rather than narrow bars. Use only photo-supported qualitative placement; mark all dimensions and relief depths as estimates.
4. Retain the sparse side elevations unless reliable side references establish openings. Avoid reintroducing the removed unsupported overlays.
5. Keep the interior as an explicitly nondimensional first-floor schematic until a dimensioned/current plan is available; improve visual clarity of circulation and labels without implying verified door swings or upper floors.

## Evidence reviewed and limits

- Purdue’s [Felix Haas Hall page](https://events.purdue.edu/felix_haas_hall) and the preserved `audit/batch3_haas/exterior_reference.jpg` support the qualitative pale-stone/red-brick composition, central entry, arched lower openings, and red roof. A perspective image does not establish exact dimensions or unseen elevations.
- [HAAS Hall first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports room names and broad adjacency only; it is nondimensional and does not verify door locations, metric registration, or upper floors.
- The saved reopen check confirms the 17-tread count and unchanged local GIS wall envelope. It does not establish roof dimensions, facade accuracy, or interior measurements.

**9/10 decision: No.** Round nine improves cleanup and inlay geometry, but roof shading, facade depth, and the remaining north-end projection still need correction.
