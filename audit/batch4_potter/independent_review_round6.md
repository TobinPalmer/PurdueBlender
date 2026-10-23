# Independent Round 6 Review — Potter Engineering Center

Review date: 2026-10-23  
Asset reopened independently in Blender 5.2.3: `modular/buildings/potter_engineering.blend`  
Scope: no-edit review. The `.blend` was opened in background mode for inspection and was not saved or modified.

## Score: 7.3/10

| Category | Score | Evidence |
|---|---:|---|
| Source alignment and honesty | 8/10 | The 2016 p.45 plan shows the T-shaped Room 401 and the small rooms at its stem. The round-6 checks explicitly describe cross-page affine placement as approximate, not surveyed. Current-use and historical evidence limitations are acknowledged in the report. |
| Penthouse orientation and adjacency | 8/10 | Room 401 has the plan’s T orientation. Room 401A is represented between Room 401 and 4S04, correcting the previously direct adjacency. The three centerline doorway rays pass through their intended interfaces and side-control rays hit walls. |
| Room-area correspondence | 6/10 | The plan labels are 3,547 sf / 100 sf / 183 sf (329.53 / 9.29 / 17.00 m²). The model’s Room 401 was uniformly scaled to the 3,547 sf target, while 401A and 4S04 dimensions were set from their labelled areas. This is internally consistent area matching, not an independent dimensional measurement from the drawing; 4S04 wall bounds are larger than its nominal clear area, as expected. |
| Stairs, landings, and aperture | 7/10 | Saved checks show a 0.174 m final tread-to-landing rise, XY overlap, and roof rays clear at the stair center but blocked just outside the opening. The landing overlaps the 4S04 entrance region. These are useful geometric checks, but the rendered stair has awkward rail diagonals/crossings and the checks do not prove a continuous human-clear route through full width or validate code dimensions. |
| Reopen and file integrity | 9/10 | Independently reopened the saved file. Root is `(0,0,0)`, envelope is 58.4515 × 67.4320 m, collection contains 500 objects, and no un-packed external image dependency was reported. This confirms reopening and basic asset integrity, not every object’s correctness. |
| Exterior, facade, and interior finish | 6/10 | Exterior is a coherent recognizable mass with brick/precast/window treatment, but the broad unverified roof dominates the render and the repeated facade reads procedurally uniform. The isolated stair evidence is legible but visually rough. The reviewed materials do not establish complete building-wide interiors or current room fitout. |

## Findings

- **Plan orientation:** The source crop/full p.45 plan and the revised model agree on Room 401’s T shape and its stem-side relationship to the smaller spaces. The revised sequence reads as Room 401 → Room 401A → 4S04, with the S03 stair entering 4S04. This is consistent with the plan’s intermediate 401A label/location and fixes the earlier direct 401-to-4S04 shortcut.
- **Registration:** Reusing the registered p.44 affine for p.45 is explicitly called approximate in the check data/report. The drawing-based orientation is more supportable than precise geographic placement, door widths, or wall offsets. The model should keep this caveat attached to any exported presentation of the penthouse.
- **Areas:** Nominal areas match the three printed labels by construction: Room 401 = 329.53 m², 401A = 9.29 m², 4S04 = 17.00 m². Because the dimensions were fitted to those areas, they should be described as area-matched estimates, not a measured validation. The plan image is low-resolution and not a dimensioned survey.
- **Doorways:** The saved centerline/side-control raycasts support openings at all three interfaces. They show a center ray passing and a nearby ray striking a wall, but do not record actual clear width/height or sweep a person-sized path. Door dimensions remain estimates.
- **Stair arrival:** The landing bounds overlap the final tread in XY; the landing top sits 173.7 mm above the highest tread. This is a plausible last riser and the landing lies within the roof aperture/4S04 area. A full path clearance test from stair to 401A and into Room 401 was not independently established. The circulation render shows rails that project across each other and a top rail that appears detached/overshoots; refine rail geometry and improve the view before treating it as polished.
- **Evidence:** The 2016 study supports historic plan labels and approximate footprint relationships. The current Purdue facility page supports only the stated current uses (Room 160, 114, and 127); it does not verify current Room 205 or these penthouse room boundaries. Exterior references do not verify a particular photographed elevation, roof equipment, or exact facade allocation. These limits are appropriately disclosed.

## Priorities

1. Improve rail endpoints and reduce misleading crossings in the stairwell render; show the top landing and all three door openings from a useful angle.
2. Add measured clear-width/height and person-clearance checks at the 401/401A/4S04 interfaces, including a path trace across the landing and door turns.
3. Keep the penthouse location and dimensions marked approximate; avoid implying the exact 401A/4S04 geometry is dimensionally recovered from the plan.
4. Reduce the dominance of the flat roof plane and add facade variation only where photographic or drawing evidence supports it.
5. Expand interior coverage only with current or clearly historical evidence; do not imply the Room 205 vignette is current.

The corrected adjacency and successful fresh reopen materially improve the asset. Remaining evidence and circulation-detail limits keep it below 9/10.
