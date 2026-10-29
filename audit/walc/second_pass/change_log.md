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
