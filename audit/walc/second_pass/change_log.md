# WALC (Wilmeth Active Learning Center) — second pass change log

## r1 (2026-10-29) — asset SHA-256 `eccc73f023c3c1dd5ffdefaa679290c8fbbf57e773f5a9d420a824ffb3e7f395`

Built by `modular/buildings/build_walc_second_pass.py`. Renders are in `r1/` (cameras in `r1/cams_r1.json`, settings in `r1/r1_render_settings.json`). The asset reopens cleanly (`r1/validation_r1.json`): 43 objects, about 160k triangles, no external paths. This revision has **not been independently reviewed**.

**Scope exception (user direction, 2026-10-29).** For WALC the user asked for the interior to be modeled as well. That overrides, for this building only, the AGENT.md rule that second passes are exterior-only shells.

**Rebuilt, not patched.** The first-pass asset was a rotated 80 × 48 m massing with an interior, plus a separate misaligned shell. The builder deletes everything under the asset except `AssetRoot_walc` and rebuilds it. A backup of the first-pass file was kept outside the repository.

### Evidence used (see `sources/` and `research/second_pass/buildings/walc/`)

- **Footprint:** Purdue campus GIS FID906, converted to the local frame (`footprint_local.json`). It includes the stone pier rhythm on the west front and the angled SW bay.
- **Heights:** 2017–2019 QL2 LiDAR NDHM sampled over the site (`sources/walc_ndhm_2018.*`, made with `ndhm.py`).

  | Roof element | Height (m) |
  | --- | --- |
  | North block hipped roof, eave / ridge | 17.3 / 21.8 |
  | South block hipped roof, eave / ridge | 17.6 / 22.4 |
  | West range gable, west eave / ridge (ridge at x = −6.3) | 15.9 / 19.6 |
  | Central flat roof | 16.0 |
  | Clerestory monitor over the atrium | 19.1 |
  | One-storey lecture hall 1018 on the east | 7.0–7.7 |

- **Floor plans:** Purdue Active Learning "WALC Classroom Floor Plans" (`sources/WALC_Classroom_FloorPlans.pdf`), four furnished floors: basement, first, second and third. Each page was rendered at 130 dpi (`sources/walc_classroom_floorplans_p1-4.png`) and registered to FID906 (`plan_registration_check*.png`). On the page, east is up, west is down and north is left.
  - **Floors 1–3:** a single affine fit, about 11.6 px/m.
  - **Basement:** the same fit with a 40 px shift, matched on the stair towers.
  - **Cross-check:** Purdue Emergency Preparedness AED floor maps for floors 1 and 2 (`sources/Map-showing-AED-location-WALC-*.png`).
- **Exterior photos:** research V01–V10, with the 2026 Google satellite view used for the roof plan.
- **Interior photos:**
  - BSA LifeStructures project gallery (`sources/interior/bsa_N98…N134.jpg`): reading room, atrium stairs, stacks, theatre and lounge.
  - Turner 002–005: atrium, lounge, glass study rooms and theatre.

### Model

**Exterior**

- **End blocks:** brick, with a stone base, a belt course at floor 2 and a stone frieze under the eave.
  - North and south faces: tall two-storey window units over pairs of ground-floor windows.
  - West faces: windows grouped single, double, double, single.
  - East faces: punched windows. These are not seen in any photo.
- **Glazed west range:** six limestone piers and seven bays.
  - Ground floor: storefront glazing with doors in the central bays.
  - Floors 2–3: a projecting olive-grey framed window in each bay.
  - Also: the name band with lettering, suspended glass canopies, and paired dark "W" brackets under a deep eave.
- **Roofs:** red tile hipped roofs on both blocks and a gabled west range, with dark soffits, fascias and downpipes. The flat central roof carries the clerestory monitor, and the lecture hall has its own low roof. Floors 2–3 step back to x = 30.5 above the lecture hall.

**Interior, traced from the plans**

- **Floors:** basement, floor 1, floor 2 and floor 3 slabs, with the atrium open from floor 1 to the monitor and the reading room double height over floor 3.
- **Rooms:** every classroom, with furniture matched to the plan legend:
  - round tables for six
  - straight table rows
  - tablet-chair rows
  - curved tiered rows in 1018 and 1132
- **Theatre 1055:** about 14 raked rows of seats, a stage in the SW bay, a gold curtain and a dark ceiling soffit.
- **Library stacks** on floor 2, with study carrels along the windows.
- **Reading room** on floor 2:
  - steel king-post trusses and a wood-slat vaulted ceiling under the west-range gable
  - tall west windows and wood wainscot
  - two lines of long study tables with lamps
  - a painting on the south wall
  - glass with steel X-bracing toward the atrium and stacks, and the glass gallery front on floor 3
- **Floor 3 study pods:** a row of glass study rooms.
- **Atrium:** a long open stair with dark stringers and glass rails, glass edge railings and the historic mural.
- **West lounge on floor 1:** a wood-slat ceiling, round concrete columns, seating and red high-back pods.
- **Also:** core and mechanical rooms, office zones, three stair towers, round concrete columns, and light panels in every room.

### Known gaps for the next revision

- **West ground floor:** the real ground floor is a recessed arcade behind free-standing piers with storefront set back. r1 places the storefront in line with the piers.
- **Façade texture:** the diaper (diagonal) brick fields and the stone heads and sills of the end blocks are not modelled.
- **Windows:** north and south window counts are approximate, and the east faces have no photo coverage.
- **Interior lighting** is emissive panels only, so interior renders are dim.
- **Basement:** registration is approximate. Only the classrooms, commons and mechanical rooms are modelled.
- **Rooms not drawn:** small offices, restrooms and the rooms inside the cores are not drawn individually.
- **Surveyed rather than measured:** all heights are LiDAR or photo estimates, and the floor levels (B −5.0, 1 = 0, 2 = 5.5, 3 = 10.5, wall plate 15.6 m) are estimates.

## r2 (2026-10-29) — asset SHA-256 `ab5770593106c435466da8c8dd288054134ff986df774fb658aa79ca765ccab1`

This revision makes every exterior fix from the quick review r01 (5.75/10, `review_r01/`). The interior is unchanged apart from clipping. Renders are in `r2/` (cameras in `r2/cams_r2.json`, which adds the reviewer's ground-level `G_*` views). The asset reopens cleanly (`r2/validation_r2.json`, 179k triangles). This revision has not been re-reviewed.

- **Render ground.** `review_render.py` now puts the ground at street level (z = 0, or `RR_GROUND_Z`), not at the basement floor. Every r1 view had shown a false 5 m blank base.
- **Window frames.** The end blocks now have white frames with mullions at about 0.6 m and glazing bars at about 0.95 m (small panes), replacing dark frames with plain glass.
- **Diaper brick.** Floors 2–3 of the end blocks have a diagonal lattice of dark headers (`WALC_SP_Brick_Diaper`, about a 1.4 m module). All brick is a darker red-brown.
- **West entrance arcade.** The limestone piers now stand free with stone base blocks. Behind them, the shopfront glazing is set 2.8 m back under a stone soffit at 4.6 m. It has brick piers between the bays and double doors with leaves in the four middle bays.
- **Wall holes.** These were partition walls poking through the outer wall: traced room boxes running past the angled bays and the north ground-floor steps.
  - **Fix:** `room_walls` now keeps only the length of each wall that stays inside the building, and furniture and lights outside the floor outline are skipped.
  - **Stair-tower bays:** the short bays where the glazed range meets the blocks are now brick with one tall window strip.
- **North ground floor.** It is flush with the upper floors. The small FID906 steps on the north edge were removed, as the photo V02 shows a flush face.
- **End-block eaves:**
  - **Profile:** a thin dark soffit and fascia instead of a thick slab.
  - **Brackets:** spaced every 1.8 m.
  - **Gutter:** a bronze gutter along the edge.
  - **Frieze:** a stone frieze fills the gap between the wall plate and the eave.
- **Stone bands.**
  - **Removed:** the band between floors 2 and 3 that cut across the windows.
  - **Added:** a stone course above the floor-3 window heads and a frieze under the eave. The base and the floor-2 belt course are kept.
- **Window trim.** Every window has a stone sill and lintel. The tall ground-floor windows have a stone panel about two-thirds of the way up.
- **South faces.** Separate single and paired windows on each floor, with tall window strips near the corners, replacing a copy of the north face's tall windows.
- **Brick piers.** Shallow projecting piers at the corners and between the window groups on the north faces.
- **Downpipes.** Bronze, fixed to the wall at the piers, with goosenecks up to the gutter. Five sit on each long face. Previously they hung free from the eave corners.
- **Name.** The full "THOMAS S. AND HARVEY D. WILMETH ACTIVE LEARNING CENTER" now runs on a stone band crossing in front of the piers, readable in one line.
- **Glazed range:**
  - **Window frames:** deeper projecting frames (0.9 m), with small panes in the upper section.
  - **"W" struts:** real W-shaped dark steel struts with outriggers to the eave.
  - **Eave underside:** a stone frieze closes the eave above each pier, so no roof tile shows underneath.
- **Colours.** Roof tile brighter terracotta, stone a little less cream, gutters bronze.

### Remaining

- East faces still have no photo coverage.
- The diaper module and the window pane counts are estimates from the photos.
- Plaza planters and benches are not modelled; they are site assets.

## r3 (2026-10-29) — asset SHA-256 `77980a63dbfa2fee546efc4af74ac1ad329468e7744da8c72ca9ef3090de8688`

This revision follows the user's close-up of the west face (`sources/user_provided_brick_closeup.png`) and their note that the roof was too orange. Renders are in `r3/`, including the new view `r3_close_west_face_N_block.png`. The asset reopens cleanly (`r3/validation_r3.json`).

- **Diaper brick only in the window columns.** On floors 2–3, the crossed pattern now fills only each window column: the width of the window plus about 0.45 m each side, from the floor-2 belt course to the stone course under the eave. Piers, corners and the ground floor are plain running bond (`diaper_columns`). The pattern is a fine, low-contrast lattice of darker headers (0.6 m module), no longer bold lines.
- **Colours** are re-sampled from the close-up (`sources/color_samples_r3.json`):
  - **Brick:** browner and variegated, with light mortar.
  - **Window frames:** taupe-grey. The close-up shows the frames are not white.
  - **Stone:** warm light grey.
  - **Gutters and downpipes:** dark bronze.
- **Roof** is now a muted brown-red, matched to the aerial at sRGB ~150,120,100 in flat light. The 2017 drone photo used before is over-saturated.

## r4 (2026-10-29) — asset SHA-256 `1838582d16f0157c26dcdbf2a4c7f7efa102dded6937c0233eb71c4053284e86`

This revision follows the user's close-ups and back-of-building photos (`sources/user_provided_basketweave_closeup.jpg`, `_south_walk`, `_east_entrance`, `_east_corner`, `_aerial_west`) and the findings of quick review r03 (8.02/10, `review_r03/`). Renders are in `r4/`. The asset reopens cleanly (`r4/validation_r4.json`); both textures are packed and there are no external paths.

- **Real basketweave brick.** The overlaid diagonal "diaper" lines are replaced by an actual brick bond:
  - **Bond:** squares of three parallel bricks, each square one brick long. The direction alternates square by square, and the whole weave is turned 45°, so the squares read as small crosses.
  - **Texture:** generated by `make_brick_textures.py` (`textures/walc_brick_basketweave.png`, 1.724 m tile).
  - **Colours:** variegated red and plum bricks, from k-means clusters of the user's close-up, with buff mortar.
  - **Running bond:** a new image texture in the same palette (`textures/walc_brick_running.png`).
- **Spandrel panels.** The basketweave fills each window column on floors 2–3, at the width of the window. It runs between the floor-2 belt course, the stone sills and heads, and the stone course above the floor-3 heads, and on the end blocks also through the brick frieze under the eave. Piers and corners are running bond.
- **Roof.** Deep red-brown/maroon tile, from the user's aerial at sRGB ~110–128, 83–97, 86–98. It is no longer orange.
- **Window units on the end blocks.** Two panes wide, with a short top pane, a tall middle pane and a short bottom pane. Wide openings are pairs of units split by a heavier mullion (review r03 #3).
- **Eave.**
  - **Frieze:** now brick (with basketweave in the window columns), with a slim stone cornice under the soffit. It was a tall grey stone band.
  - **Soffit:** warm dark brown.
  - **Removed:** the extra stone band at the wall plate (review r03 #5).
- **Glazed range:**
  - **Struts:** slim dark-bronze paired struts on each pier, projecting from the pier face up to the eave edge. They replace the flat "W" letters (review r03 #4).
  - **Colours:** bronze-taupe frames, verdigris canopies and bronze lettering (review r03 #7).
  - **NW junction:** the gable roof has a dark underside so no tile shows from below, and the end bays stop at the end piers (review r03 #9).
- **Glass.** Darker and reflective (review r03 #10).
- **East side, from the back-of-building photos.**
  - **East wing walls:** the one-storey wing (lecture hall 1018) has a tall stone base, a basketweave field between plain brick corner piers, a stone band, an upper row of window triplets and a stone coping.
  - **East entrance:** two pairs of doors under a glass canopy on steel outriggers, on the east projection.
  - **NE stair tower:** the white interior wall on the courtyard side (review r03 #1) was the NE stair tower poking out of the upper-floor outline. The floors 2–3 recess now stops at y = 17.6, so the tower is inside the shell.
  - **Removed:** a stray flat-roof strip that floated over the recess.
  - **Gap filled:** the gap at x = 40 above the wing (y −18…−12.7) is filled with brick and coping.
