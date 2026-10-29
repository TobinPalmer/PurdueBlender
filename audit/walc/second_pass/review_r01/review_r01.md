# WALC second pass, review r01 (quick review, exterior only)

- **Asset:** `modular/buildings/walc.blend`, SHA-256 `eccc73f0…3f395` (verified)
- **Score:** **5.75 / 10**, not accepted (threshold 9.9)

| Criterion | Max | Awarded |
| --- | --- | --- |
| Windows | 3.0 | 1.6 |
| Signature architecture | 2.5 | 1.25 |
| Proportions / roof | 2.0 | 1.45 |
| Material / colour | 1.5 | 0.85 |
| Consistency | 1.0 | 0.6 |

## Render note

The r1 renders put the ground plane at the basement floor (z = −5). Every photo-matched view therefore shows a 5 m blank plinth, and the eye-height cameras sit 6.7 m above the render ground. I re-rendered the views with the ground at grade: `rv_G_*.png`, made with `review_render_grade.py` and `cams_review_r01.json`. The script is a copy of `review_render.py` with an `RR_GROUND_Z` override.

## Missing or wrong, in priority order

1. **End-block windows: frames.** The photos show white frames with transoms and divided lights. The model has dark frames and plain panes.
2. **Diaper brickwork.** The diagonal pattern on the end-block upper floors is missing.
3. **West ground floor.** The photos show a recessed arcade: free-standing piers, storefront set back, brick between the bays, and double doors. The model has flush storefront.
4. **Holes in the exterior shell.** White interior walls show through at the NW and SW glazed-range junctions, at the south-face ground floor and at the south-block east junction. The stair-tower vertical window strips are missing.
5. **End-block eaves.** The exposed brackets/rafter tails and the thin bronze gutter are missing. The eave reads as a thick flat slab.
6. **Stone courses.** There is a spurious band between floors 2 and 3. The string course above the floor-3 heads and the frieze/architrave are missing.
7. **Window stone heads and sills.** These are missing, along with the stone transom panels on the ground-floor windows.
8. **South face window schedule.** It copies the north face's tall two-storey units. The photo shows punched windows on each floor plus end pavilions.
9. **Name band.** The lettering is hidden behind the piers and cut off. It should run as one continuous bronze line across the frieze.
10. **Downpipes.** They float about 1.5 m off the wall, hanging from the eave corners. In the photos they are fixed to the wall at the pilaster lines.
11. **Pilasters.** The projecting brick corner and bay pilasters are missing.
12. **North-face ground storey.** It juts out and steps; the photo shows a flush face.
13. **Glazed-range bays.** They are too shallow and lack the small-pane upper lights. The W brackets are simplified, and the west soffit shows tile.
14. **Colours.** The brick is too warm and pink (the photos show red-brown with dark headers). The roof tile is dull compared with the orange terracotta. The fascia is grey where the photos show bronze or copper.

Details and the required corrections are in `review_r01.json`.
