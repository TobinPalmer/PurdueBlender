# Independent review — Mathematical Sciences Building, round 4

**Review date:** 2026-10-23  
**Asset reviewed:** `modular/buildings/math_sciences.blend`  
**Rating:** **7.1/10** (round 3: 7.2/10)  
**9/10 threshold:** Not met; continue revision.

I reviewed the saved round-four asset, reopened it in Blender 5.2.3, inspected the round-four exterior/interior renders, the 2022 plan comparison, the brick detail and material checks, and the recorded geometry/reopen checks. I also compared the supported facade treatment against Purdue Statistics' exterior photo and attempted to open the recorded Google Maps place listing; Maps imagery was inaccessible in this environment. I did not edit the asset, scripts, or master.

## Scorecard

| Area | Score | Assessment |
|---|---:|---|
| Identity, registration, footprint | 8.0 | FID 227 and the existing local frame are retained. The saved round-four geometry check reopened the expected export collection. The GIS comparison is explicit about its sampling method and limitations; it is not a survey or polygon IoU. |
| Exterior massing and facade | 5.9 | The east/south elevations have a recognizable repeated window rhythm and pale vertical framing consistent with the available Purdue photo. Large unarticulated wall wings remain, especially in the overall and side views. The passage is still not visibly resolved, the roof/penthouse is a large estimated slab, and a gold building-name label crosses the lower facade/windows in the render. |
| Materials and texturing | 7.6 | The close view reads as running-bond brick with mortar and the material is embedded. The overall facade is still pink/pale under the current lighting, and the brick unit scale/color are estimates. Window surrounds have conspicuous dark corner blocks in the close-up. |
| Third-floor library/interior | 6.3 | Hiding 33 legacy objects removes some duplication, and `library_plan_round4.png` makes the 2022 zones easier to compare. The cutaway is still difficult to read: broad ceiling/roof surfaces occlude views, wall/furniture contrast is weak, and groups/partitions are schematic. It does not yet show a convincing, source-grounded interior. |
| Upper floors and vertical form | 4.5 | The ten-story identity is supported, but modeled floor intervals, 33.2 m wall top, 42.9 m overall extent, and rooftop form are still explicitly estimated. The dominant penthouse/roof remains visually unresolved. |
| Saved-file and geometry checks | 8.5 | I independently reopened the `.blend`; it has `Asset_math_sciences` with 551 direct objects. The saved-file logs report 81 clear sampled pane-center rays and all 6 brick controls hit. These checks do not verify that the assumed window schedule matches the building or that glazing/reveals are correctly seated. |

## Round-four changes and effect

- **Useful cleanup:** 33 legacy library items are hidden, reducing overlapping study furniture. The operation is recorded as reversible and leaves the library floor and perimeter walls visible.
- **Clearer plan evidence:** the source-labeled top-down render distinguishes 2022 room/core zones and the modeled furniture more clearly than the oblique interior view. It remains a schematic layout, not proof of current as-built partitions or furniture coordinates.
- **Uncertainty is documented better:** roof, penthouse, and slab objects now identify their estimated status. This improves provenance but does not improve geometric accuracy.
- **Exterior improvement is mostly camera framing:** the campus-eye render reduces roof-face dominance; the shape, blank elevations, passage, and unverified roof profile remain. The gold `MATH_Signage_East` text object is at `(17.5, -3.8, 4.65)` with dimensions about `(6.03, 0.25, 0.08)` m and visibly overlays the facade/window area. Move it to a verified sign location or remove it from the facade render until sourced.
- The latest visual/check set was rendered after reopening the saved file. I found no evidence that the round-four edits establish the missing roof/elevation details or a correctly placed passage.

## Findings that prevent 9/10

1. **Resolve the facade label and window details.** `MATH_Signage_East` visually runs through the lower facade and panes. The window surrounds also show dark corner blocks in `brick_detail_after.png`; inspect their placement/material and correct the seam artifacts. Compare those details against a clearer, larger source image.
2. **Finish source-supported massing on every visible side.** The open wall wings and slab/penthouse dominate the overall render. Find multi-side photos, elevations, or dated archival imagery before adding facade details; keep unknown walls identified as unknown rather than presenting the block as finished.
3. **Make the passage legible and place it from evidence.** Purdue sources support a land bridge/passage, but the retained `passage_round4.png` frames the entrance facade rather than showing the opening. It cannot validate location, width, or supports. Use a verifiable view or plan and render the actual opening in context.
4. **Improve interior readability and source alignment.** Use the 2022 plan for its shown zones/core and label every inferred gap. A cutaway/plan view should expose the floor, partitions, furniture, and circulation without the broad occluding surfaces. The 2025 library photo supports furniture and finishes, not the exact current arrangement.
5. **Keep vertical claims provisional.** Current sources do not validate metric floor heights, the 33.2 m wall height, 42.9 m maximum, or roof/penthouse profile. A measured elevation or a defensible reference is needed before those proportions can score as accurate.

## Evidence inspected

- `exterior_round4.png`, `exterior_after.png`, `exterior_east_after.png`, `exterior_west_after.png`, `exterior_north_after.png`, `exterior_south_after.png`
- `brick_detail_after.png`, `library_after.png`, `library_plan_round4.png`, `library_plan_diagram.png`, `third_floor_core_after.png`, `passage_round4.png`
- `geometry_checks_round4.log`, `geometry_checks.json`, `render_round4.log`, `render_exterior_round4.log`, `hide_legacy_round4.log`, `legacy_interior_visibility_round4.json`, `structural_edge_comparison.json`, `material_check_round3.log`
- Local source photo: `audit/next_math/reference.jpg`
- Purdue Statistics exterior photo: https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg
- Purdue Libraries 2025 reopening article: https://blogs.lib.purdue.edu/news/2025/09/09/mathematical-sciences-library-math-partially-reopened-with-refresh-and-a-new-testing-room/
- Purdue Trustees 2022 third-floor plan: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf
- Purdue Daily Visit Tours, land-bridge mention: https://ontour.admissions.purdue.edu/daily-visits/
- Google Maps listing attempt: https://www.google.com/maps/place/Purdue+Mathematical+Sciences+Building/@40.4261348,-86.915642,17z/ — inaccessible through the available web reader; no Maps imagery was inspected.

**Verdict:** Round four modestly improves evidence clarity and removes duplicate interior objects, but does not materially resolve the exterior or interior quality blockers. The round-four rating is **7.1/10**, below the requested **9/10** threshold. Do not mark this asset complete.
