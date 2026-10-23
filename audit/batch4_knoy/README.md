# Knoy Hall batch 4 review and revision

## Asset

`modular/buildings/knoy_hall.blend` was reopened after saving and remains a local asset with an identity root transform. Footprint, story elevations, shell, and placement were preserved. This revision removes the prior unverified rooftop cooling-tower geometry. The broad mechanical penthouse mass and the south-edge PV-like array remain; Google Maps satellite inspection at the displayed **50 ft** scale showed stepped roof/terrace masses and a visible strip consistent with panels. No rooftop equipment beyond those broad forms was added.

`roof_aerial_annotation.svg` is an interpretive schematic, not a satellite screenshot and not to scale. A live Google Maps screenshot was inspected in the task UI on 2026-10-23. Its attribution line reads “Imagery ©2026 Airbus, CNES / Airbus, Maxar Technologies, Map data ©2026 Google”; the imagery acquisition date is not shown. Street View opened without a usable panorama. The schematic labels exactly what was observed and should not be treated as measured roof geometry.

## Interior / circulation

The ground-level partition trace follows Liu thesis Figure 3.19(d), which is a low-resolution plan image rather than a construction drawing. The existing model had 18 provisional 1.05 m openings at inferred wall gaps. This revision adds 12 subdued door leaves in openings that do not intersect adjacent trace walls. Six openings (`09`, `13`, `17`, `18`, `20`, `24`) remain clear as pass-throughs because the mesh collision audit shows a crossing wall at each; inserting a leaf there would create a collision. All door leaves are explicitly illustrative, with swing direction unverified. They are not a verified door schedule.

No furniture, stairs, or upper-floor/basement room layouts were added: the accessible plan and photo sources do not provide enough evidence. The ground partitions have a neutral painted appearance; no room-finish schedule or interior photo verifies actual colors/materials.

## Registration and orientation

The thesis raster was aligned by manual matching to the official Purdue GIS footprint (local coordinates, centered on the saved asset). Three identifiable corners were checked:

| Corner | Plan pixel | Matched GIS local coordinate | Visual residual |
|---|---:|---:|---:|
| A | (60, 97) | (-15.416, -46.581) m | ~0.07 m |
| B | (64, 353) | (16.928, -45.998) m | ~0.05 m |
| C | (776, 261) | (5.230, 46.581) m | ~0.06 m |

These small residuals describe those selected raster points, not survey accuracy. Pixel selection is uncertain by about one source pixel (~0.13 m), and the thesis raster has no dimensions; the overall plan-to-GIS scale/layout remains approximate (prior uncertainty estimate about ±1.5 m). The plan contains no north arrow. Orientation is inferred: source-image right maps to local +Y (north), source-image down to local +X (east). See `footprint_registration_overlay.png` and `registration_nw_zoom.png`.

## Sources checked

- Official Purdue GIS building footprint used for exterior registration, cached in `gis_vertices_local.json`.
- Liu thesis, Figure 3.19(d), `audit/complete_knoy/Liu.pdf`; the traced plan image is `plan_trace_overlay.png`.
- Official Purdue Polytechnic exterior feature photo: [profile page](https://polytechnic.purdue.edu/profile/rnawroc), image `Knoy-featured.jpg`. It supports brick, horizontal window bands, and facade character; no capture date is stated.
- Purdue Archives [Knoy Hall records](https://archives.lib.purdue.edu/repositories/2/resources/1490) lists a 1984 floor-plan record, but the catalog record is physical-only and did not expose a downloadable plan.
- Purdue Provost [classroom plans](https://www.purdue.edu/provost/academic-facilities-classrooms/) lists Knoy B029 and B041. The linked PDFs were not accessible during this review; their details were not extrapolated to other rooms or used to invent layouts.
- Google Maps [Knoy Hall](https://www.google.com/maps/place/Knoy+(Maurice+G.)+Hall+of+Technology,+401+Grant+St,+West+Lafayette,+IN+47907/) satellite imagery: copyright year 2026, 50 ft displayed scale, acquisition date absent.

## Material scale evidence

`KNOY_Purdue_Red_Brick` has no UV layer; it uses normal-based triplanar projections from the mesh object's local coordinates. The shell transform and root are identity at metre scale. The Brick Texture values are width **0.23 m**, course height **0.076 m**, and mortar **0.006 m**. The saved close-up render `knoy_brick_texture_closeup.png` shows individual courses and mortar at facade scale. This verifies procedural scale behavior, not the exact historical brick specification.

## Reopen and geometry audit

`reopen_validate.py` opens the saved `.blend` and checks material indices, identity root placement, main-shell bounds, and intersections of the 12 added door leaves against the traced partition meshes using Blender BVH triangle overlap. `model_validation.json` records the result. Current status: reopen PASS, 12 door leaves, no missing/bad material indices, no door-leaf/partition intersections, no cooling-tower object. The six omitted leaves are intentional collision avoidance where the source-grid trace crosses.

## Evidence images

- `knoy_exterior_roof_oblique.png` — whole-building material/render view.
- `knoy_brick_texture_closeup.png` — brick course and mortar scale.
- `knoy_interior_eye_level.png` — eye-level illustrative ground-floor opening/door view.
- `knoy_ground_plan_cutaway.png` — ground-floor trace and opening placement view.
- `footprint_registration_overlay.png`, `plan_trace_overlay.png`, `current_gap_overlay.png` — registration and source plan context.
