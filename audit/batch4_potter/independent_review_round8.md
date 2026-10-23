# Independent Round 8 Follow-up — Potter Engineering Center

Review date: 2026-10-23  
Asset: `modular/buildings/potter_engineering.blend`  
Scope: read-only fresh reopen and review of Round8 mesh-overlap evidence plus the Level 1 plan and stairwell renders. The blend was not saved or modified.

## Score: 7.2/10

| Category | Score | Evidence |
|---|---:|---|
| Source and plan fit | 7/10 | The Level 1 view clearly identifies the walls as the 2016 existing plan and the orange Room 160/SW stack marker as approximate. The plan registration IoU is recorded at 0.8546. The stair cores have not been independently matched to a surveyed/current plan or door route. |
| Stair and landing geometry | 6/10 | The Round8 tests expose possible conflicts around the historic partition meshes and the S03 penthouse entrance. Several overlap types are expected near walk-surface transitions, but the current logs do not separate those from a body obstruction. Some sample locations are on the center rail divider or within a landing transition, so collision counts alone overstate route obstruction. |
| Penthouse opening and door fit | 6/10 | At the last S03 tread sample, the 0.8 m box reaches x=8.862 while the assumed roof aperture begins at x=8.9, a 38 mm overlap with modeled roof. The S03 door check uses a centerline y=35.2 and 1.2 m width; the top-flight box sample is centered at y=35.725, 525 mm off-center. A 0.8 m body box at that position extends 325 mm beyond the nominal half-width of the opening. This is a plausible real jamb/roof conflict requiring correction or clearer geometry. |
| Reopen and asset integrity | 9/10 | Fresh Blender 5.2.3 reopen succeeded. `AssetRoot_potter_engineering` is at `(0,0,0)`, the export collection is present, total object count is 500, the GIS envelope remains 58.4515 × 67.4320 m, and no missing unpacked image dependencies were found. |
| Render communication | 7/10 | The Level 1 plan is now a useful, uncluttered top-down reference and distinguishes historical walls from the approximate current-use anchor. The stairwell view shows the vertical sequence and unresolved basement tie-in, but it does not show the S03 door jamb or roof aperture close enough to validate the reported conflicts. |

## What the overlaps mean

The Round8 BVH output is a useful warning list, not a collision verdict. It reports triangle-surface intersections between an axis-aligned box at selected tread centroids and evaluated object surfaces. It does not calculate penetration depth, distinguish tangency from meaningful intrusion, or label a contact as a floor-support transition. The proxy uses an upright box at 25 unique upward-facing tread centroids, rather than a continuous path; the selected samples include center-divider/landing positions. The diagnostics cover only cores/levels `(3,0..3)`, `(1,1)`, and `(2,1)`, not every flight. The output is therefore not a complete all-flight clearance audit.

Some hits are expected or at least inconclusive: upper landing and penthouse landing triangles overlap boxes near the final tread because those surfaces adjoin the stair. Such a hit can reflect the intended step-up transition or a head/torso clash; the reported triangle pairs and centroid z ranges do not tell which. Handrail hits at a tread sample centered on the divider rail are likewise a sampling artifact unless a route through that center lane is intended.

Several other hits cannot be dismissed as supports. The Level 1 plan render projects the core 3 coordinates `(10.5, 35.2)` near the thick partition line shown at the east edge of the orange outline. The BVH logs show S03 boxes near `(10.6–11.3, 35.725)` intersecting the 2016 Plan53 wall mesh. Similar partition hits occur around the other cores and at later levels. These are potential real conflicts in the model's historic wall geometry; the plan view is not detailed enough to prove every wall crossing, doorway, or opening. Do not move stair cores from these counts alone, but check the local plan opening and route against the mesh before claiming clearance.

The most actionable Round8 warning is at S03’s penthouse approach. The assumed roof aperture is x=8.9–12.1 m; the last-tread sample at x=9.262 m uses a box extending to x=8.862 m, so it intersects the roof by roughly 38 mm. The same top-flight lane is centered at y=35.725 m, while the estimated S03→4S04 opening ray is centered at y=35.2 m and the opening is 1.2 m wide. A person-width envelope centered on the flight exceeds that estimated opening by about 0.325 m on one side. This indicates a likely top landing/door alignment problem unless the opening is changed or the approach is redirected. The north/west enclosure hits at samples `(9.712,35.725)` and `(9.488,35.725)` also need a close mesh and plan check.

Core 2 reports glazing/frame intersections at the level-1 landing approaches. Because the exact hit-pair positions and penetration depths are omitted, this remains unresolved; it should be checked against the exterior wall/opening geometry before accepting that stair location.

## Visual review

- `floor1_plan_current_library_anchor_round7.png` is legible as a top-down plan: the historic partition geometry is visible and the approximate Room 160/stack-use zone is clearly labeled. The orange marker is much larger than a room boundary claim and its caption correctly says approximate.
- `stairwell_circulation_round7.png` communicates floor sequence and stair layout, but it is an isolated schematic view. It does not reveal the width/offset between the upper S03 stair lane, 4S04 enclosure wall, roof aperture, and doorway. A close-up plan/section of that junction is needed to resolve Round8.
- The current Purdue facilities page supports the current library use and three-floor collections statement. It does not verify current room partitions or the exact orange marker boundary. The 2016 plan is historical evidence, so conflicts should be described as model-to-historic-plan conflicts unless current measured plans are found.

## Priorities

1. Resolve S03’s top approach: align the stair lane, penthouse landing, roof opening, and 1.2 m doorway in one measured plan/section. Confirm a person-width route through actual walls and opening geometry.
2. Add hit locations, contact/penetration depth, actual object surface normals, and local cropped plan/render evidence to Round8 diagnostics. Separate expected walk-surface/landing contacts from wall, rail, glazing, and roof clashes.
3. Inspect the core 1/2/3 partition intersections level by level against the 2016 plans. Verify doors/openings rather than assuming every registered wall face is continuous, and avoid repeating one high-floor core position where the lower plans differ.
4. Re-run an oriented, continuous body-envelope proxy across each flight and landing, including all ten flights; keep its status as geometric evidence and not a code/accessibility determination.
5. Produce a close S03 upper-landing view that includes the stair, both doorway jambs, 4S04 walls, roof edge, and registered plan overlay.

Round8 improves evidence honesty by exposing potential conflicts and keeping the stairs unchanged pending plan-aligned interpretation. The S03 roof-edge and doorway offsets look actionable, while many reported landing/rail overlaps are ambiguous contacts from the chosen box samples. The model is at **7.2/10** and remains below 9/10 because the stair route has unresolved wall/door/roof intersections.
