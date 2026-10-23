# Rawls Hall independent review — round 5

## Result

**Independent rating: 6.7/10.** The round 5 south wall repair follows the eight existing south-facing pane quads and adds true masonry openings, brick returns, and narrow perimeter bars. The file reopens cleanly in Blender 5.2.3 LTS. The north and south glazing both read as blue-gray glass in the supplied façade renders. The largest remaining gap is the interior: the core-only plan is sparse, the atrium views show structure without usable circulation, and the saved glass still gives little convincing interior depth. Source and site placement remain approximate.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 7.7/10 | South openings now match the measured two-bay by four-band pane pattern. Masonry reveals and slim dark frames read clearly in close-up. The evidence covers only the short south-facing wall segment with eight panes; other elevations and window areas remain simplified. |
| Materials and texturing | 6.8/10 | The south close-up shows plausible brick scale and blue-gray panes. Glass is saved at transmission 0.18, roughness 0.16, metallic 0.08, but the north/south elevation views show mostly reflected sky and little room depth. Mortar remains strongly contrasted and repetitive at close range. |
| Interior completeness | 5.2/10 | The entry cutaway communicates the main door group. The core plan view is very sparse, and the atrium column/rail section does not establish stairs, landings, or circulation. The handoff appropriately avoids presenting these areas as verified current fit-out. |
| Technical integrity and placement | 8.8/10 | Reopened the saved asset in Blender 5.2.3 LTS. Confirmed 722 objects, eight south glass quads, 192 south frame faces, 824 wall faces, and the north counts recorded in the audit. The root is identity and unparented; no missing images are reported. GIS placement and the Plan1086 edge remain unresolved. |
| Evidence and source fit | 5.8/10 | The round 5 handoff is careful about the 2024 plan, historical atrium photos, and missing reproducible Google Maps capture. The evidence is useful for checking the changed south segment, but there is no dated current façade reference or dimensioned survey tie to resolve exact exterior fit. |

Weighted using the prior review formula (exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%): **6.69/10, rounded to 6.7/10**.

## South openings and measured geometry

I reopened `modular/buildings/rawls_hall.blend` in Blender 5.2.3 LTS. Its `RAWL_South_Windows_South_Glass` mesh contains eight quads: two x positions (approximately -10.704 to -8.904 m and -6.894 to -5.094 m) repeated over four z bands (1.1–3.6, 6.586–9.086, 11.677–14.177, and 16.767–19.267 m). This matches the measured pane mesh; it does not rely on mirroring the east-facing glazing. The rebuilt outer wall strip spans x -12.708 to -3.088 m and brackets those pane bounds. Its 55 mm aperture allowance is consistent with the frame bars.

The new south render shows blue-gray panes with dark perimeter edges and masonry surrounding each opening. The close-up confirms reveal depth. The adjacent east-facing glazed object is a separate 12-quad mesh and was left alone, which matches the stated scope. Do not extrapolate the south pattern to that adjacent wall without evidence.

There is a record mismatch worth cleaning up: `round5_checks.json` has detailed rays that pass through each tested south pane and encounter core partitions or the opposite shell. The later `round5_aperture_ray_checks.json` reports the same four south first hits but has `next_hit: null` for every sample (and also for its north samples). Use the detailed multi-hit trace as the geometry evidence and regenerate or remove the contradictory abbreviated ray file.

## Glazing, core, atrium, and placement

The north exterior image reads as repeated cool panes and repaired brick surrounds. The south close-up also reads as glass. However, both are largely uniform reflections; the north cutaway trial shows bright, broad reflections rather than a believable view into a lit room. The saved transmission value of 0.18 is an improvement over round 4 but does not by itself demonstrate useful transparency.

The core plan image is mostly blank space with a few isolated lines and rails. The entry cutaway is more legible, though its pale shell and floor bands obscure some door context. The atrium views show columns and rails across levels, but provide no verified stair or bridge connections; the section-cut view additionally has a large foreground floor obscuring much of the vertical void. A clean, source-oriented interior cutaway would make the existing work easier to evaluate without inventing unsupported detail.

The notes preserve a 1–2 m GIS registration uncertainty and an unresolved Plan1086 boundary. The asset remains technically modular and reopens without missing images, but these records do not establish exact survey placement.

## Prioritized fixes

1. Regenerate `round5_aperture_ray_checks.json` with the same multi-hit method as `round5_checks.json`, or remove it, so the handoff and evidence do not disagree.
2. Improve the core and atrium review views: show the supported plan in a legible orientation, and frame the atrium void without the foreground slab blocking it. Add circulation geometry only with source support.
3. Tune the saved glazing and interior lighting together, then show one representative view through a pane into a visibly modeled room. The current renders establish a glass-like blue reflection, not room depth.
4. Reduce mortar contrast while retaining the current plausible brick scale.
5. Resolve overall GIS registration and the Plan1086 edge when dimensioned control or a reproducible current map reference is available.

The south aperture work is a solid targeted improvement, but the sparse interior, limited evidence of glass depth, and unresolved site/source fit keep this below a 9/10 rating.

## Reviewed evidence

- `audit/batch4_rawls/south_elevation_round5.png`
- `audit/batch4_rawls/south_glazing_closeup_round5.png`
- `audit/batch4_rawls/north_glazing_interior_round5.png`
- `audit/batch4_rawls/north_interior_depth_cutaway_round5.png`
- `audit/batch4_rawls/core_partitions_ink_plan_round5.png`
- `audit/batch4_rawls/atrium_columns_railwork_round5.png`
- `audit/batch4_rawls/atrium_section_cutaway_round5.png`
- `audit/batch4_rawls/north_entry_cutaway_round5.png`
- `audit/batch4_rawls/round5_checks.json`
- `audit/batch4_rawls/round5_aperture_ray_checks.json`
- `audit/batch4_rawls/round5_model_changes.json`
- `audit/batch4_rawls/round5_handoff.md`

Asset modified: **no**.

