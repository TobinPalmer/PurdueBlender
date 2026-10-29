# Mackey Arena — second-pass change log

## r1 (2026-10-28)

Builder `modular/buildings/build_mackey_arena_second_pass.py` run on the saved library; it deletes the first-pass exterior shell (`MACK_Buttress_Pylon_*`, `MACK_Concourse_Transom_*`, `MACK_Dome_*`, `MACK_Exterior_*`, north pavilion/canopy/revolving doors, `MACK_PERIM_*`, merged `MACK_SDAC_*` facade/slab meshes, Weist plaza deck/furniture) and rebuilds the exterior as `MACK_SP_*` objects parented to `AssetRoot_mackey_arena`. Interior bowl, Keady Court, scoreboard, catwalk, practice-court floor objects are untouched. Collection, root, local frame and manifest placement are unchanged.

### Dimensions (estimates — not survey)

| Item | Value | Basis |
| --- | --- | --- |
| Drum centre / radius | (0, −14.14) m / 47.5 m | First-pass GIS registration retained; 2023 aerial roof edge radius ≈47.0–47.5 m (roof displaced ≈(3.0, −4.5) m by relief) |
| Concourse ring / additions height | 5.8 m | SW entrance door scale in 2016_02; drone_04 ratios |
| Drum top / fascia top / dome rim | 17.4 / 19.6 / 19.4 m | drone_04 drum:low-wall ratio ≈1.55 with distance factor |
| Dome apex | 27.9 m | First-pass value retained; spherical cap (R≈138 m) |
| Slot windows | 0.52 m × 9.1 m (z 7.2–16.3), 6 per slotted bay at ≈1.04 m pitch | 2016_02, drone_04 |
| Pilasters | 24 × (1.2 m wide, 0.45 m proud) | angular spacing ≈15° from MackeyA / drone_04 |
| Wing height | 14.0 m parapet; floors 0 / 5.0 / 9.6 m | 2016_01 proportions; first-pass 3-level SDAC (14.3 m) |
| Wing outline | orthophoto trace, ground-corrected by (−0.16h, +0.25h) | Relief displacement measured on the dome rim |

### Colour calibration (per modular/AGENTS.md colour rule)

Photo medians in `sources/color_samples.json` (sheet `sources/color_sample_sheet.png`; four mis-placed sample boxes flagged invalid). Base colours set so the review render under the standard review light reproduces the sunlit photo values: brick render (164,127,104) vs. photo (173,133,99)/(181,136,108); limestone render (212,206,187) vs. (224,212,188); dome render ≈(174,159,147) vs. (217,195,172) sun / (200,170,157) overcast. Masonry specular reduced (IOR level 0.15–0.2) and mortar joints thinned so the brick does not read grey-pink.

Render pipeline changed for all second-pass reviews to Eevee, *Standard* view transform, sun 2.6, sky 0.45 (`r1/r1_render_settings.json`); the baseline was re-rendered with the same settings.

### Known remaining uncertainties / simplifications

- Window counts on wing facades follow a rhythm (≈4.3 m bays), not a per-window survey.
- Glass towers are simple boxes; the curved glass bay near the east entrance seen in 2016_01 is not modelled as curved.
- SDAC lobby curvature is faceted along the traced outline.
- Drum slot pattern on north/east assumed.
- Signage reflects 2025 drone imagery (banners), not the 2016 vertical MACKEY blade sign.

## r2 (2026-10-28, recorded retroactively in r3)

r2 was built in another session and left uncommitted (builder, `.blend` SHA-256 `5ad0172207cabd3d4a347f1ce86f9be8fb0f5faefd0c8948aa32a411836406a5`, renders in `r2/`). It was never independently reviewed and had no change-log entry. This entry describes what the r2 builder does. r3 builds on it.

- **Heights from LiDAR.** Heights were rebuilt from the Indiana 2017-2019 QL2 NDHM (`sources/mackey_ndhm_2018.*`, saved in r3):
  - ring roof 4.4 m, concourse coping 5.3 m
  - fascia top 12.2 m
  - measured radial dome profile with the apex at 24.7 m and the cap at 26.0 m
  - wing roofs 10.0 / 9.5 / 8.7 m, penthouses 13.7-14.4 m, west annex 7.2 m

  Because the dome is lower than in the first pass, the interior bowl/court rig is lowered 7.5 m below grade. Each moved object records its original height in `sp_orig_z`.
- **Drum.** 36 pilaster bays of 10° (from the Purdue Athletics 2025 west aerial, saved in r3 as `sources/purdue_athletics_2025_west_aerial.jpg`) replace r1's 24 bays.
  - Two slotted bays alternate with one plain bay.
  - Each slotted bay has 5 light warm-grey louvre panels in the lower part of full-height recessed brick channels.
  - The fascia is vertically corrugated.
  - On the north side (72°-137°) the drum runs down to the ground. The north entrance storefront has lettering there.
- **Plan and wings.**
  - Outline traced from the LiDAR, without lean.
  - Concourse ring only from 137° to 262°.
  - South blocks A/B; the west annex west facade comes from the 2025 aerial.
- **East wing and P towers.**
  - East wing facade has two tiers (recessed storefront arcade, one row of upper windows with limestone heads and sills).
  - SDAC west facade has one tier of tall upper windows.
  - SE tip has a glazed corner bay in a metal surround, 4 slit windows per floor, a canopy over the arcade, and attic inlays.
  - P towers have a louvre band carrying the P, and metal-panel penthouses.
- **East entrance.** Curved east entrance with banners.
- **Lobby.** Faceted SDAC lobby in the notch between the SDAC and the drum.

## r3 (2026-10-28)

Builder `modular/buildings/build_mackey_arena_second_pass.py` (revision r3) was run headless on the r2 library. The saved file was reopened and validated (`r3/validation_r3.json`: pass, 327 objects, no unparented objects, no libraries/images/absolute paths). Asset SHA-256: `a76d53697af42587b352b03820c13753efcc325cbbb1a345ff6679dcd821dc75`.

The review set in `r3/` has 27 renders: the standard elevations, obliques and top view, the r2 close-ups, and 8 matched/new views. Camera list: `r3/closeup_cameras.json`; settings: `r3/r3_render_settings.json`. r2 was re-rendered at the new cameras in `r3/before_r2/`. Reference | r2 | r3 strips are in `comparisons_r3/` (`compare_r3.py`).

### Changes

1. **Drum proportions (r01 finding 1).** The fascia underside moves from 10.1 to 10.95 m, the louvre top from 8.45 to 9.25 m, and louvre/channel width from 0.58 to 0.62 m at 1.06 m pitch. The fascia is now 1.25 m (10.95-12.2) instead of 2.1 m.
   - **Basis:** I measured fascia : channel-above-louvre : louvre on the same slotted bays. The 2025 west aerial gives 0.31 : 0.37 : 1 and drone_04 gives 0.26 : 0.38 : 1. I solved these between the LiDAR ring roof (4.4) and fascia top (12.2), with a 0.35 m curb (`drum_heights_r3.py`). The range across the two photos is 10.83-11.02 m for the fascia underside and 9.18-9.29 m for the louvre top.
   - **Result:** drum height 6.55 m, which is 0.79 × the 10° bay chord. This matches the reviewer's photo ratio of 0.79-0.80 (r2 gave 0.69).
   - **Ground check:** with the 2016_02 camera at 90-95 m from the drum centre (pilaster-spacing fit for 36 bays), the visible drum : bay chord ratio is predicted at 0.585 against 0.606 measured.
2. **Drum colours (r01 finding 11, colour table).** The drum now has its own darker 1967 brick (`MACK_SP_Brick_Drum`); the 2011 additions keep `MACK_SP_Brick_Red`. Fascia, louvre and limestone base colours were corrected in linear space from the r2 render samples. Results in the standard `close_drum_slots` view, render median against the photo median:

   | Material | r3 render | Photo (`2016_02`, sunlit) |
   | --- | --- | --- |
   | Drum brick | 177,137,107 | 173,133,99 |
   | Fascia | 184,155,109 | 188,158,112 |
   | Louvres | 152,148,137 | 150,146,132 |
   | Limestone | 224,213,188 | 224,212,188 |
   | Dome (unchanged) | 206,183,161 | 217,195,172 sun / 201,173,161 overcast |
   | Ring roof (top view) | 177,175,170 | 167,162,154 (ortho) |

3. **East entrance (r01 finding 3).** Recomposed from a close crop of drone_05. From south to north:
   - end pier with a KEADY COURT banner
   - "44" wall segment over its own portal
   - blade pier with a vertical MACKEY ARENA banner
   - central segment with the curved MACKEY ARENA / HOME OF PURDUE BASKETBALL / P banner over two portals split by a pier, and EAST ENTRANCE on the portal-head band
   - blade pier with a vertical MACKEY ARENA banner
   - "59" segment over a portal
   - end pier with a KEADY COURT banner

   There are now four deep portals to the glazed door wall. r2 had three portals, a banner spanning almost the whole curve, and 44/59 on narrow end piers. Segment widths are photo proportions on the 33.3 m arc (±0.5 m).
4. **SDAC curved lobby (r01 finding 6).** The two-storey curtain-wall lobby now sits on the convex plan bend where the SDAC west facade turns from 12.5° to due north. It has an R 20 m arc turning 40° plus a 2.8 m straight return.
   - It is built with limestone curb, mullions at about 1 m, transoms, a metal second-floor slab band, and a projecting roof with a deep metal fascia.
   - **Basis:** the 2023 orthophoto roof edge (relief-corrected) and hntb_Purdue-2, which shows the order SDAC brick → curved glass lobby → short brick return → recessed glazed slot → drum.
   - The N-S return (x = 17.3 m, y 31-59) is now banded brick with a few narrow windows and a recessed full-height glazed slot at the drum end. That face is seen only at a grazing angle, so it is estimated.
   - r2 had put the lobby in the notch against the drum, where no plaza view sees it.
5. **Evidence saved.** r2 relied on two sources it never saved: the 2025 west aerial and the LiDAR NDHM window. Both are now in `sources/` and listed in `reference_index.json`, together with the extraction tool `ndhm.py` and the r3 check `drum_heights_r3.py`.

### Status of the r01 reviewer findings after r3 (modeller's assessment, not a score)

| r01 finding | Status | Notes |
| --- | --- | --- |
| 1 Drum / concourse / dome proportions | Addressed r2 + r3 | LiDAR heights in r2; drum re-proportioned in r3 (drum:chord 0.79; drone_04 visible drum : concourse wall 6.55/5.3 = 1.24) |
| 2 Drum slot louvres | Addressed r2 + r3 | Light louvres in the lower ~70 % of recessed channels, colour matched |
| 3 East entrance curved, separate banners, blade banners | Addressed r2 (curve) + r3 (composition) | Banner captions under 44 / 59 are not legible in any source; texts are estimates |
| 4 East wing two tiers | Addressed r2 | Bay pitch is an estimate (8.2 m pairs) |
| 5 SDAC west facade one upper tier | Addressed r2 | Wide/narrow alternation estimated from hntb_Purdue-2 |
| 6 SDAC curved lobby | Addressed r3 | Plan radius and turn are estimates (±2 m) |
| 7 SE wing corner bay, slits, canopy/arcade, inlays | Addressed r2 | — |
| 8 Fascia corrugation and colour | Addressed r2 (corrugation) + r3 (colour, height) | — |
| 9 P towers / penthouses | Addressed r2 | — |
| 10 Coverage north side; north entrance lettering/storefront | Partly | Lettering and storefront added in r2. The 2025 west aerial adds W/NW drum and annex coverage. **Still no current daylight photo** of the SDAC rounded north end, the north half of the east facade at street level, or the drum's north/east bays (gate still fails) |
| 11 Colours (ring roof, dome, brick) | Addressed r2 + r3 | See the table above; the dome is left between the sunlit and overcast samples |
| 12 Manifest object list / count / bounds | Open (coordinator) | Asset now has 327 objects; local bounds x -65.3..67.1, y -75.1..139.1, z -7.5 (below-grade bowl)..26.0 |
| Plaza monuments (gold PURDUE art panel, Weist Plaza wedge sign in hntb_Purdue-2) | Open | Positions not measurable from the single photo; not modelled rather than guessed |

### Known remaining uncertainties

- **Camera fits.** The matched-view cameras are estimates. The 2016_02 camera was moved to 92 m from the drum centre on the Commons geotag bearing, because the geotag distance (81 m) is inconsistent with the 36-bay pilaster spacing.
- **Pilaster count.** The count (36) depends on the fitted camera distance of the west aerial. 39 bays would fit that photo only with a camera about 30 m closer, and that is inconsistent with the LiDAR fascia height. 24 bays is excluded.
- **East entrance.** Exact portal widths and pier positions are unknown, and so are the banner captions.
- **North face of the lobby return.** The face between the lobby and the drum, and the rounded SDAC north end, are not seen in any daylight photo.
- **Wing windows.** Window counts on the wing facades follow photo rhythms, not a per-window survey.
