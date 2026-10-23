# Independent review — Mathematical Sciences Building, round 3

**Review date:** 2026-10-23  
**Asset reviewed:** `modular/buildings/math_sciences.blend`  
**Rating:** **7.2/10**  
**9/10 threshold:** Not met; do not mark complete.

I inspected the round 3 saved-file reopen checks, geometry/material logs, the overall and four-side exterior renders, the brick close-up, and the interior/cutaway and plan-reading images. I did not edit the asset or master file. This is a visual and evidence review of the supplied artifact; the renders are the evidence for the current model state.

## Scorecard

| Area | Score | Assessment |
|---|---:|---|
| Identity, registration, footprint | 8.0 | Building identity and the preserved GIS-derived footprint/frame are well documented. The bidirectional edge samples are useful context, with stated offsets and limitations; they are not a survey or footprint IoU. |
| Exterior massing and facade | 6.2 | Repeated east/south windows and pale framing make the supported elevations more legible. The overall render still reads as a simplified block model: a large blank wall volume, broad roof/penthouse slab, weak ground-level passage, and sparse north/west faces dominate. Those less-supported elevations remain visibly unfinished. |
| Materials and textures | 7.8 | The close brick/window render now clearly shows stretcher courses and mortar, and glazing, pale surrounds, and brick are distinct. This is a clear improvement over round 2. The overall view still looks washed-out pink and smooth at normal viewing distance; masonry dimensions/color and the other facade finishes have not been verified against a dated, multi-side reference. |
| Third-floor library/interior | 6.0 | The 2022 plan overlay helps locate the core and broad zones. The 2025 Purdue Libraries source confirms refreshed carpet/furniture, added group rooms, rearranged shelves, and windowless room 352 with a desktop. The model includes those kinds of elements, but the current room divisions, three group-room placements, furniture count, and circulation are inferred. Rendered furniture and partitions remain schematic and the cutaway has distracting shadow/occlusion. |
| Upper floors and vertical form | 4.5 | Nine intermediate slabs communicate a ten-story stack, but the floor heights, 33.2 m wall height, 42.9 m maximum extent, rooftop/penthouse, and upper-floor plans are estimates without measured elevations. The flat, oversized rooftop treatment is visually prominent. |
| Saved-file / geometry checks | 8.5 | Separate Blender logs show the saved asset reopened, with the expected `Asset_math_sciences` collection. The stated 81 pane-center rays pass through the tested shell/infill and six controls hit brick. These checks do not validate glass/reveal placement or the assumed window schedule against an elevation source. |

## What improved in round 3

- The close brick detail now shows a recognizable running bond with visible mortar, unlike the subtle surface pattern in round 2. Material values are embedded in the file and no external texture dependency is reported.
- The facade opening geometry remains robustly checked at its sampled centers and solid-wall controls.
- Shelves were moved into the labeled library zone and the plan-reading diagram makes the 2022 renovation-plan relationship easier to inspect.
- The maker documented uncertainties rather than presenting inferred room/floor geometry as measured.

## Findings that still prevent 9/10

1. **The full exterior is not yet convincing or fully evidenced.** The overall view exposes large blank wall runs, incomplete north/west articulation, a conspicuous roof slab/penthouse, and a barely readable ground-level land bridge. Improve the massing and composition using additional actual photos or elevations; do not invent window patterns on the unsupported sides.
2. **A close-up does not resolve the facade match.** The brick course is now clear at close range, but the building still appears pale/pink and nearly smooth in the overall render. Compare against a source photo under neutral lighting and adjust the material only with that visual evidence. The procedural brick unit dimensions are explicitly estimates.
3. **Interior quality is still schematic.** The actual library uses are source-confirmed, but current partition geometry and furniture positions are not. The cutaway has occlusion and shadow that make circulation and room boundaries difficult to judge. Use the plan only for its labeled zones and core, keep the 2025 occupancy claims distinct from inferred placements, and make the interior view more readable.
4. **Vertical dimensions and roof remain unsupported.** The sources establish ten stories, not the modeled floor intervals, roof shape, or metric height. A dated elevation, archival photo, or reliable measurement is needed before treating those dimensions as accurate.

## Source-verified versus inferred

- **Source verified:** MATH identity/address and current department uses; 2025 library refresh, group-study rooms, rearranged shelves, and a small windowless desktop testing room 352; 2022 plan's renovation area and visible third-floor core/zones; the public GIS footprint polygon as the source for the existing horizontal shell reference; repeated brick/window/pale-frame treatment on the side visible in Purdue's exterior photo; 10-story count per Purdue Archives as reported in the asset notes.
- **Inferred or unverified:** exact facade bay spacing and window dimensions; all north/west facade details; brick unit/mortar specifications; current library partitions and furniture coordinates/counts; group-room dimensions and precise locations; floor-to-floor intervals, wall and overall heights, upper-floor plans, penthouse/roof composition, and the land-bridge geometry beyond the fact that a ground-level passage exists.
- **Geometry-check scope:** 81 rays verify passage through modeled shell/infill at chosen pane centers, with six solid-wall controls. They do not establish that those chosen coordinates match the real facade, nor that every pane and reveal is correctly seated.

## Evidence inspected

- `exterior_after.png`, `exterior_east_after.png`, `exterior_west_after.png`, `exterior_north_after.png`, `exterior_south_after.png`
- `brick_detail_after.png`
- `library_after.png`, `library_plan_diagram.png`, `third_floor_core_after.png`, `plan_layout_overlay.png`
- `geometry_checks.json`, `structural_edge_comparison.json`, `material_check_round3.log`, `build_round3.log`, `render_round3.log`
- Purdue Libraries 2025 reopening article: https://blogs.lib.purdue.edu/news/2025/09/09/mathematical-sciences-library-math-partially-reopened-with-a-refresh-and-a-new-testing-room/
- Purdue Board of Trustees 2022 third-floor renovation plan: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf
- Purdue Statistics exterior photo: https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg
- Purdue Department of Mathematics building page: https://www.math.purdue.edu/about/building
- Purdue GIS BuildingShapes FID 227: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Purdue Admissions campus tour page supporting the existence of the land bridge only: https://ontour.admissions.purdue.edu/daily-visits/

**Verdict:** Round 3 improves the brick material and evidence presentation, so I rate it **7.2/10**, up modestly from round 2. It does **not** meet 9/10. The broad unsupported elevations, simplified roof/massing, and inferred/schematic interior remain substantial quality gaps.
