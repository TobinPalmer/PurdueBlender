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
