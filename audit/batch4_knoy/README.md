# Knoy Hall batch 4 review and revision

## Asset

`modular/buildings/knoy_hall.blend` was reopened after saving and remains a local asset with an identity root transform. Footprint, story elevations, shell, and placement were preserved. This revision removes the prior unverified rooftop cooling-tower geometry. The broad mechanical penthouse mass and the south-edge PV-like array remain; Google Maps satellite inspection at the displayed **50 ft** scale showed stepped roof/terrace masses and a visible strip consistent with panels. No rooftop equipment beyond those broad forms was added.

`roof_aerial_annotation.svg` is an interpretive schematic, not a satellite screenshot and not to scale. A live Google Maps screenshot was inspected in the task UI on 2026-10-23. Its attribution line reads “Imagery ©2026 Airbus, CNES / Airbus, Maxar Technologies, Map data ©2026 Google”; the imagery acquisition date is not shown. Street View opened without a usable panorama. The schematic labels exactly what was observed and should not be treated as measured roof geometry.

## Interior / circulation

The ground-level partition trace follows Liu thesis Figure 3.19(d), a low-resolution plan raster rather than a construction drawing. Eighteen provisional 1.05 m openings were inferred from wall gaps. Twelve carry illustrative opaque leaves with an estimated neutral finish; swing direction and actual door material remain unknown. Six candidate gaps (`09`, `13`, `17`, `18`, `20`, `24`) are not modeled as doors. A 0.90 × 0.045 × 2.10 m test leaf at each inferred center overlaps another traced partition; the raster does not resolve whether a door is present or how it is placed there. See `audit/complete_knoy/door_gap_collision_audit.json` for per-gap candidate coordinates and intersecting trace names. This is a placement test, not proof that all alternative door positions are impossible, and the plan is not a verified door schedule.

### Vertical circulation and current limits

The 2018 Purdue College of Engineering Gateway Formation Study plan labels typical Levels 2–4 and contains three masked stair-symbol regions. The saved source now includes six illustrative switchback stair runs: three plan-traced cores on L2–L3 and the same three on L3–L4. These are positioned from the source symbols, but the registration remains a hand fit (about ±1 m); stair widths, risers, treads, landings, and neutral concrete appearance are estimates because the drawing does not dimension them. They do not claim verified stair connections to L1, a basement, L5, or the roof. `audit/complete_knoy/stair_reopen_validation.json` records the six reopened meshes and reports no overlap with the traced partition meshes. Core C ends within centimeters of the GIS footprint edge, so its exact boundary fit remains uncertain.

`KNOY_FloorSlab_L5` remains tagged `UNVERIFIED / SOURCE CONFLICT`: the available 2018 elevations label only Levels 1–4, and current evidence cannot determine whether this slab is a mislabeled roof slab or an unsupported fifth story. No furniture or room-specific finishes are asserted. The ground partition finish and stair material are estimates; no interior photograph or finish schedule was found. New top-down orthographic cutaway renders compare L1–L4 at a shared scale with walls cut at 1.45 m above each floor. They omit floor slabs so the traced room partitions and stairs remain visible. Near-black blue wall, orange door, amber stair, and white-background colors are temporary audit coding only and are not saved to the source asset.

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

## Newly recovered Purdue plan/elevation source (2026-10-24)

The Purdue College of Engineering's **Gateway Formation Study, Review 5.31.18** includes a drawing explicitly titled **“Typical Plan Levels 2–4”** and labels the adjacent existing Knoy elevations as **Levels 1–4, floor-to-floor 14′-8″**. This supersedes the earlier statement that no upper-floor plan source was accessible. It provides good evidence for the typical upper-floor room/corridor arrangement and four existing numbered levels; it is a 2018 planning study, not a stamped as-built set, and is not evidence of current furniture or finishes.

- Source: [2018-05-31 Massing Studies Draft Including Landscape](https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf), Purdue College of Engineering.
- Retrieval date: 2026-10-24. The source PDF identifies review date 2018-05-31. Page 24 (1-based) is saved as `audit/complete_knoy/knoy_existing_elevations-24.png`; the 700×1450 pixel typical-plan crop is `audit/complete_knoy/knoy_typical_plan_crop.png`. The complete downloaded source is `audit/complete_knoy/2018-05-31_knoy_massing_studies.pdf` (48,904,918 bytes, 46 pages).
- The plan crop was registered for reference against the official local-coordinate GIS polygon in `gis_vertices_local.json` using three manually selected outline controls: crop pixel (382,139) to local (5.230,46.581) m; (107,1253) to (-15.416,-46.581) m; and (507,1253) to (16.928,-45.998) m. These are visual picks on an architectural drawing, not surveyed controls; resulting transform is a hand registration and should be assigned at least ±1 m uncertainty. This source has no north arrow or plan scale on the reproduced page; the GIS footprint supplies horizontal scale and location, while the plan supplies internal layout.
- PDF units conversion: 14′-8″ = **4.4704 m** nominal level-to-level. Existing source asset slab center elevations are approximately 0.025, 4.356, 8.836, and 13.317 m for L1–L4; therefore the first modeled interval is about 4.331 m and the next two are about 4.480 m. This mismatch should be reconciled before calling vertical geometry verified. The model also contains a slab named `KNOY_FloorSlab_L5` and a separate roof deck; the 2018 source labels only Levels 1–4. Whether L5 is a misnamed roof slab or an unsupported fifth level remains unresolved, so it is explicitly flagged rather than asserted as correct.
- The plan is now traced into three combined mesh objects, one each for L2, L3, and L4, in child collection `KNOY_UpperLevel_TypicalPartitions_L2-L4` inside `Asset_knoy_hall`. `upper_plan_wall_trace.json` records 179 accepted centerline segments per floor, source-pixel endpoints, local XY endpoints, extraction/registration method, and exclusions. The trace retains medium/long interior wall strokes and door gaps visible in the source raster; likely perimeter strokes within 1.2 m of the GIS outline, visible stair-core boxes, and sub-1.25 m runs are excluded. It is an approximate raster trace, not CAD extraction; short fixtures, plumbing, casework, and some angled/detail lines are omitted or ambiguous.
- The three meshes use the model's local frame and begin at the saved L2, L3, and L4 slab top elevations (4.481, 8.961, and 13.442 m). Wall height is 2.8 m, copied from the existing ground-trace convention; the PDF does not provide partition heights. Registration is a three-control manual fit with approximately ±1 m uncertainty. `upper_plan_wall_trace_overlay.png` compares the detected traces to the original plan crop. `knoy_typical_plan_L2.png`, `knoy_typical_plan_L3.png`, and `knoy_typical_plan_L4.png` are top-down diagnostic renders from the saved asset.
- The same plan's three visually identifiable stair-core symbols are approximately boxed in `add_vertical_circulation.py`; each is repeated for the L2–L3 and L3–L4 intervals. `stair_reopen_validation.json` verifies all six meshes reopen, have materials, and do not overlap traced partition meshes. These are source-positioned illustrative stairs, not dimensioned as-built circulation. The `knoy_typical_plan_L2.png`–`L4.png` views now include their corresponding rendered stair runs; compare them with the source-plan overlay before accepting their exact fit.
- The inherited `KNOY_FloorSlab_L5` is now labeled `UNVERIFIED / SOURCE CONFLICT` in the saved asset and its scene metadata. The 2018 source labels existing Levels 1–4, so this slab is not counted as a verified occupied level. It remains in the source because available evidence cannot establish whether it is a misnamed roof slab or a fifth-floor modeling error; resolve against a current as-built drawing before making a geometry deletion.

## R23 Purdue campus GIS source-ID reconciliation and saved-footprint check

The saved Knoy boundary can be compared with Purdue University Libraries' live `Purdue/campus` MapServer layer 0 geometry. Its record is `OBJECTID=189`, `buildingidlong=75`, `ABBR=KNOY`; the raw response requested in EPSG:4326 is `purdue_campus_knoy_feature189_r23.json`, with retrieval details in `official_gis_provenance_r23.json`. The project cache `modular/buildings/target_buildings_gis.json` uses its own `FID=243` for the Knoy row, so that identifier is not the campus service `OBJECTID`. The cache also carries the five-level/48-ft attributes discussed below; those attributes are not fields in the live campus service response.

After reopening the saved asset, the ordered 29 unique vertices in the project cache match the footprint wire within 0.000012 m (source rounding). The same transform and ordered-vertex comparison against the live service shows a 0.177865 m maximum difference at two adjacent points; the rest agree within 0.001 m. This is recorded in `validation_r23.json`. The offset may reflect source edits or separate digitization and does not establish a structural-wall offset, so the geometry was left unchanged. The project transform remains an approximation, not survey control; position/orientation and the master marker were not independently checked in this pass.

## Material scale evidence

`KNOY_Purdue_Red_Brick` has no UV layer; it uses normal-based triplanar projections from the mesh object's local coordinates. The shell transform and root are identity at metre scale. The Brick Texture values are width **0.23 m**, course height **0.076 m**, and mortar **0.006 m**. The saved close-up render `knoy_brick_texture_closeup.png` shows individual courses and mortar at facade scale. This verifies procedural scale behavior, not the exact historical brick specification.

## Reopen and geometry audit

`reopen_validate.py` opens the saved `.blend` and checks material indices, identity root placement, main-shell bounds, and intersections of the 12 added door leaves against traced partitions using Blender BVH triangle overlap. `model_validation.json` records the ground-level result. `reopen_upper_validation.py` and `validate_stairs.py` reopen and validate the typical-level partitions and stairs. Current checks: source opens; root remains identity; upper-plan meshes preserve 179 segments each with valid indices and zero nonmanifold edges; six stair meshes have materials and no reported partition intersections; 12 illustrative ground-floor door leaves have no reported partition intersections; no cooling-tower object. Six other candidate door placements remain unresolved as documented above. These geometry checks do not verify construction dimensions or prove all room routes accessible.

## Evidence images

- `knoy_exterior_roof_oblique.png` — whole-building material/render view.
- `knoy_brick_texture_closeup.png` — brick course and mortar scale.
- `audit/complete_knoy/knoy_l1_interior_cutaway.png` — full L1 top-down wall/door cutaway with temporary high-contrast audit colors; slab omitted.
- `audit/complete_knoy/knoy_l1_door_corridor_cutaway.png` — zoomed L1 door/partition cutaway, same horizontal cut height.
- `audit/complete_knoy/knoy_l2_interior_cutaway.png`, `knoy_l3_interior_cutaway.png`, and `knoy_l4_interior_cutaway.png` — comparable top-down typical-level cutaways at the same scale with mapped stair runs highlighted; slab omitted.
- `audit/complete_knoy/knoy_upper_registration_northwest.png`, `knoy_upper_registration_central.png`, and `knoy_upper_registration_diagonal.png` — enlarged source-versus-registered-trace crops; each left half is the original Purdue plan crop and each right half overlays the accepted trace in green. These demonstrate raster fit, not as-built accuracy; registration remains approximately ±1 m.
- `audit/complete_knoy/knoy_l1_corridor_spatial_audit.png` — labeled, high-contrast eye-height section reveal of a longer arrangement of traced L1 partitions and two illustrative leaves, with adjoining open zones visible. Unrelated walls are hidden to reveal the trace. Candidate gaps 09/13 are labeled unresolved; the temporary floor patch is context only. This demonstrates estimated wall/leaf height and modeled connections, not a verified path, landing, or accessibility clearance.
- `audit/complete_knoy/upper_plan_registration_crops.json` and `corridor_spatial_audit.json` — crop registration, temporary render methods, camera framing, and limits.
- `audit/complete_knoy/interior_cutaway_render_audit.json` — render method, cut height, included objects, temporary finish status, and unresolved openings.
- `audit/complete_knoy/knoy_ground_interior_legible.png` — earlier eye-level view retained for comparison; it does not show the full plan.
- `knoy_interior_eye_level.png` — earlier eye-level render retained for comparison.
- `knoy_ground_plan_cutaway.png` — ground-floor trace and opening placement view.
- `footprint_registration_overlay.png`, `plan_trace_overlay.png`, `current_gap_overlay.png` — registration and source plan context.
