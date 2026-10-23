# Independent follow-up review — Mathematical Sciences Building (MATH)

**Review date:** 2026-10-23  
**Asset inspected:** `modular/buildings/math_sciences.blend`  
**Export collection:** `Asset_math_sciences`  
**Result:** **7.0/10 — still below 9/10**

I inspected the saved geometry summary and current evidence, including the overall and four orthographic exterior renders, the third-floor renders, the 2022 Board plan and overlay, the 2025 Purdue Libraries photo, the GIS edge overlay and metrics, and the opening checks. I did not edit the asset or master.

## Rating

| Area | Rating | Finding |
|---|---:|---|
| Identity and placement | 8.5/10 | MATH identity and address match Purdue listings. The existing local placement marker is preserved. The marker and map pin are contextual; neither is a surveyed entrance coordinate. |
| Footprint and plan scale | 8.0/10 | The reconstructed wall envelope retains its source frame and is close to GIS FID 227. The updated two-way wall-centerline comparison reports median offsets around 0.09 m, P95 of 0.84 m from GIS boundary to shell and 1.07 m in the other direction, with maxima of 1.54 m and 1.95 m. This is a useful footprint check, but it is not polygon IoU or survey accuracy. |
| Exterior form and detail | 6.5/10 | The east and south faces now have repeated true openings, glazing, surrounds, mullions, vertical pale bands, and an entrance. The west and north views still show broad blank wall areas and exposed/intermittent floor plates with little verified facade articulation. The references do not substantiate those sides well enough to accept their current appearance as accurate. |
| Materials and texturing | 7.0/10 | The updated lighting makes the masonry easier to read and is a clear improvement. Brick, pale stone, metal, and glazing are differentiated. The brick pattern still reads mainly as fine surface noise rather than clearly modeled or textured coursing, and the saved render is lighter/pinker than the source photo. No external texture dependencies were found in the evidence. |
| Third-floor interior | 5.8/10 | The new partition segments track the labeled 2022 library-zone divisions more closely; room 352 is represented as a small windowless room with a desktop, consistent with Purdue's 2025 report. Three group-study enclosures and their exact dimensions/locations, furniture positions, and circulation remain inferred. The top-down render shows the new layout but is shadow-heavy and sparse relative to the photographed library. The 2022 drawing is a renovation plan, not a current as-built plan. |
| Upper floors and vertical dimensions | 4.5/10 | The nine added slabs create a plausible floor stack, but slab spacing, office layouts, and the 33.2 m wall height and 42.9 m maximum extent remain estimates. Purdue Archives calls MATH ten stories; the GIS attributes list 12 levels but publish no field definitions or measurement method, so they cannot settle the height. |
| File and evidence integrity | 8.5/10 | The asset reopens; the expected export collection is retained. The reported 81 window-center rays are clear through the tested wall/infill, and six wall-control rays hit brick. This verifies the sampled wall cuts, not glazing/frame placement or every part of every facade. |

## What changed successfully

- The 2022 plan overlay now gives useful evidence for the third-floor zone partitions and core relationship. Compared with the earlier 6.5 review, this is a real improvement in the room-plan basis.
- The GIS comparison is stronger than the prior AABB-only note. It samples the official FID 227 boundary and 50 source wall-prism centerlines at 0.25 m or finer intervals and states the centerline and survey limitations.
- The reopened render set covers four nominal elevations, and the higher neutral fill shows the brick and windows more clearly than the earlier dark render.
- The opening-ray check is internally consistent with the stated 81 window centers (54 east and 27 south); the six controls strike the brick infill.

## Remaining issues that keep the score below 9

1. **Two elevations remain weakly verified.** The source photo supports red-brown brick, narrow vertical windows, and pale vertical framing on the visible face. The west and north renders reveal blank wall runs and extensive exposed floor edges, without matching source views or elevation drawings. The 2013 Purdue text describes a breezeway underneath the building, which supports a ground-level passage but does not verify repeated open floors up the tower.
2. **The opening test is not a full facade validation.** It samples assumed window-center coordinates through brick/shell objects and uses only six solid-wall controls. It does not verify that all glazing panes and frames fit their openings, nor that the generated bay dimensions match a measured elevation.
3. **Library geometry is still illustrative.** The partitions follow broad 2022 plan zones; no dimensions or current as-built boundaries were found. The 2025 article verifies group rooms and a windowless testing room, but not the three group-room locations, exact partitioning, furniture count, or circulation. Preserve those objects' inferred status.
4. **Height and rooftop remain uncertain.** The 3.25 m floor interval, 33.2 m wall top, 42.9 m overall bound, and simple penthouse/roof treatment are not supported by measured elevations. Keep them explicitly estimated.
5. **Visual finish is improved but not source-matched.** The brick relief is subtle in the renders, with little visible coursing. The material should be judged under neutral daylight and compared against additional exterior photos before claiming a close match.

## Evidence checked

- Saved asset and renders: `modular/buildings/math_sciences.blend`; `exterior_after.png`; `exterior_east_after.png`; `exterior_west_after.png`; `exterior_north_after.png`; `exterior_south_after.png`; `library_after.png`; `third_floor_core_after.png`.
- Plan and footprint evidence: `plan_third_floor.png`; `plan_layout_overlay.png`; `structural_edge_overlay.png`; `structural_edge_comparison.json`; `geometry_checks.json`; `asset_geometry.json`.
- Purdue Libraries, “Mathematical Sciences Library (MATH) reopened with a refresh and new testing room,” 2025-09-09: https://blogs.lib.purdue.edu/news/2025/09/09/mathematical-sciences-library-math-partially-reopened-with-refresh-and-a-new-testing-room/ . It confirms carpet, furniture, rearranged shelves, group-study rooms, and a small windowless room 352 with a desktop; it does not provide a dimensioned as-built plan.
- Purdue Board of Trustees, *Libraries Study Space Renovation*, Exhibit B, third-floor plan, 2022-09-28: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf . The sheet identifies 2,884 GSF affected and shows the plan/core context; it is not evidence of current exact furniture placement.
- Purdue Statistics exterior photo: https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg . The available image supports the visible brick/window/pale-frame treatment but not all elevations or measured dimensions.
- Purdue Department of Mathematics direction text, 2013: https://www.math.purdue.edu/~lipeijun/conference/wip2013/directions.html . It describes the light-red-brick building and a breezeway underneath.
- Purdue GIS BuildingShapes, FID 227, EPSG:4326: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0 . Public campus building polygon; feature survey date and attribute measurement semantics are unspecified in the supplied metadata.
- Purdue Archives building record: https://archives.lib.purdue.edu/agents/corporate_entities/672 . Supports a ten-story count, not measured heights.
- Google Maps place page: https://www.google.com/maps/place/Purdue+Mathematical+Sciences+Building/@40.4261348,-86.915642,17z/ . Used for identity/context only; the pin is not a surveyed entrance coordinate.

**Verdict:** The saved revision is more reviewable and better supported than the first pass, especially for the library zoning and footprint comparison. The incomplete/unsupported side elevations, inferred current interior layout, and estimated vertical geometry prevent a 9/10 rating. Current independent rating: **7.0/10**.
