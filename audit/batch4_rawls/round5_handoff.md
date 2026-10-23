# Rawls Hall round 5 handoff — 2026-10-23

## Saved asset and scope

`modular/buildings/rawls_hall.blend` was saved and reopened in Blender 5.2.3. Round 5 modifies the south-facing façade segment only, using its existing eight pane quads. The adjacent east-facing glazed wall was inspected separately and left unchanged; no mirrored or inferred opening pattern was added. The project master, manifest, shared scripts, and other buildings were not edited.

## South façade repair

The measured south-facing pane quads occupy two bays across four floor bands. Masonry wall faces 90 and 91 were the continuous outer and inner skins directly behind those panes. They were rebuilt into masonry around the eight measured openings, with brick reveal returns. The wall’s adjacent bottom/end faces and material assignments remain intact. The south mullion mesh had eight solid box blockers (48 faces); those were replaced with four narrow perimeter bars per pane (192 faces). Existing glass and sills were preserved. The separate southeast/east-facing glazing object was not changed.

`round5_checks.json` records four south-facing pane-center rays and nine north-facing pane-center rays. Each begins by hitting the corresponding glass object. South rays then enter modeled core partitions or continue to the opposite shell; north rays encounter the modeled NW vestibule/core partitions or the opposite shell. The first-floor partition hits are real modeled surfaces, so the evidence does not claim clear views through every room.

## Reopen and technical checks

After reopening, the export collection contains 722 objects / 714 mesh objects. The asset root remains unparented at the origin with unit scale, and there are no missing image dependencies. The masonry mesh has 824 faces; north glazing remains 60 quads with 1,440 frame faces; south glazing remains 8 quads with 192 perimeter-frame faces. Shared glass transmission is 0.18.

## Visual evidence

- `south_elevation_round5.png` and `south_glazing_closeup_round5.png` show the repaired measured south bays with blue-gray panes and masonry reveals.
- `north_glazing_interior_round5.png` shows the saved material and current exterior lighting. `north_daylight_depth_test_round5.png`, `north_transparent_depth_trial_round5.png`, and `north_interior_depth_cutaway_round5.png` are render-only tests with temporary material/lighting changes; they were not saved to the asset. They show that stronger transmission creates large reflections and still does not provide a convincing room-depth view through the north windows, where the current interior shell/partitions occlude the sightline.
- `core_partitions_ink_plan_round5.png` isolates the existing first-floor core partitions, headers, and jambs. The modeled core remains sparse and the plan view is correspondingly simple; no unsupported partitions were invented.
- `atrium_columns_railwork_round5.png` isolates the existing structural columns and evidence-informed railwork. It is a structural section view, not a verified current atrium fit-out. No unsupported stairs or bridges were added.
- `north_entry_cutaway_round5.png` shows the modeled entry door group in the first-floor cutaway context.

## Evidence limits retained

The 2024 Purdue first-floor plan supports the broad first-floor core, vestibule, and room layout; it does not verify current upper-floor partitions, finishes, or atrium circulation. Historical atrium photographs support broad multilevel character and the estimated column/rail palette only. Google Maps still has no saved reproducible capture date in the audit; the earlier access limitation remains. The approximate GIS registration uncertainty remains 1–2 m, and the Plan1086 edge remains unresolved.

The asset is ready for an independent round 5 review. No 9/10 rating is claimed.
