# Owen Hall independent grade

**Result: 7/10 — below the 8/10 passing threshold.** The grade was produced by running `evaluate_owen_hall.py` against the reopened saved library, manifest entry, and raw Purdue source snapshots. The asset was not modified.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 1/2 | Purdue GIS confirms Richard Owen Residence Hall (feature 38, OWEN), but the model's structural footprint union only overlaps 26.7% of the source polygon. |
| Position, orientation, scale and dimensions | 2/2 | Envelope center is within 0.33 m; dimensions differ by 1.2% east-west and 0.7% north-south; both are cardinally aligned in the project frame. |
| Height, floors and roof | 1/2 | Flat parapet roof profile is visually supported. The 19.1 m height and 3.8 m floor rhythm are model-derived estimates; authoritative height and exact floor count were not found. |
| Facade, entrances and distinctive architecture | 1/2 | Brick, pale base/trim and repetitive residential windows broadly match the official Purdue photo. Tall glazed bays, panel/window detailing and entry stairs/rails are simplified. |
| Modular export, portability and evidence | 2/2 | File reopens with the expected scene and `Asset_owen_hall` collection (799 objects); local root is at zero; no external image/library references or modifiers were found. Source snapshots and this scorecard are retained here. |

## Footprint measurement

Purdue's WGS 84 feature polygon was transformed into the project frame using the conversion documented in `modular/AGENTS.md`, then compared with the union of evaluated `Limestone_Base` and `GF_Wall` object bounding rectangles. The GIS envelope is 87.62 m × 107.56 m; the model envelope is 88.70 m × 108.30 m. However, polygon IoU is 0.267, and only 35.9% of the source polygon area is covered by the model proxy. The model envelope is well placed, but its detailed plan shape does not track the official footprint. Because the structural proxy uses object rectangles and the GIS service's wall-versus-overhang convention is undocumented, treat the IoU as coarse; the mismatch is still substantial enough to withhold full footprint credit.

## Remaining uncertainty

- No authoritative measured height or explicit floor count was found; model height remains an estimate.
- The facade comparison is visual and qualitative because the official image shows only one undated exterior view.
- The center and overall footprint envelope agree closely, but the plan-shape overlap is low; the structural layout needs direct review against the GIS outline before the building can pass.

## Audit files

- `evaluator_result.json` — function output including criterion evidence and findings.
- `evaluate_owen_hall.py` — deterministic evaluator implementation; run with `python evaluate_owen_hall.py` from this directory.
- `asset_inspection.json` and `inspect_asset.py` — Blender reopen measurements and inspection script.
- `owen_hall_facade.png` — render from the saved asset's documented exterior camera.
- `source_provenance.json` and `sources/` — provenance and raw Purdue GIS/page/photo snapshots.

## Builder iteration after the 7/10 baseline

The initial score above is retained as the historical independent grade. After that grade, the saved Owen library was rebuilt from Purdue GIS feature 38's complete polygon, transformed using the documented project approximation. The previous 78 massing/base/roof shell objects were replaced with seven GIS-outline extrusions: limestone base, brick shell, four limestone bands, and parapet. This corrected the plan shape to the source and retained the previous 3.8 m floor rhythm and 16.0 m parapet top as estimates. No authoritative height source was found, so height remains unverified.

The official Purdue 2007 report was added as a second independent plan-shape source. Its ground-level plan and text describe Owen as a four-story H-shaped residence hall; it is not a dimensioned drawing. The model's exact GIS-outline agreement is a source-derived reconstruction, not an independent survey measurement. The GIS layer's wall-versus-overhang convention is also undocumented.

`gis_footprint_validation.json` records the reopened asset check: exact polygon IoU 1.0 against the GIS feature, 0.0 m envelope-center error, matching 87.623 m × 107.558 m envelopes, root at local origin, expected scene and collection, and zero modifiers on the footprint base mesh. `owen_hall_gis_footprint_topdown.png` shows the rebuilt plan shell. The facade remains simplified, and no fresh independent rubric grade has been run after this iteration.

The library now contains 728 objects; the shared manifest still records 799. That shared count needs coordinator reconciliation. The initial grade's 2/2 modular score does not validate the post-iteration count against the manifest.

## Source-backed detail iteration after the 7.8/10 regrade

The saved asset was refined again from additional Purdue housing evidence. The exterior now has narrower/taller divided window assemblies, frame/transom geometry, louver panels on a subset of bays, a dark flat roof membrane with narrow limestone coping, and visible entry treads and rails. These are qualitative details observed in Purdue's exterior photo; no photogrammetric measurements or new height claims were made. The updated facade review uses a lower-exposure, wider three-quarter camera.

The official Purdue housing page links `sources/purdue_owen_standard_room_layout.svg` and publishes an approximate standard double size of 11 ft 4 in by 16 ft, closet size 3 ft 11.5 in by 2 ft 6 in, and a 77 by 36 in standard mattress. One representative dorm-room vignette was resized to those published dimensions and furnished with the listed beds, desks, dresser, closet, bookshelf, desk lights, waste baskets, network plate, towel rail, and curtain. The page explicitly says that its illustration and furnishings are approximate and can vary. The old room-216 label was removed to avoid implying an as-built assignment.

That representative room is now repeated as an illustrative module on both residential wings across all four stories (eight instances total). The 2007 Purdue first-floor diagram confirms bedrooms in both north-south wings and common/support spaces in the center; it does not verify exact room locations on the upper floors. The repeated room positions and 3.8 m floor spacing therefore remain schematic. The additions improve coverage while keeping room placement and vertical dimensions visibly uncertain.

`gis_footprint_validation.json` now records the reopened 958-object library, 240 external window units, divided-frame and louver mesh assemblies, eight standard-room modules, zero image/library dependencies, zero mesh modifiers, and exact GIS polygon agreement. `sources/purdue_owen_hall_ground_level_plan.png` is the rendered official first-floor plan page. The fresh 7.8/10 grade remains historical; no new independent score is claimed. The shared manifest still lists 799 objects and must be reconciled by the coordinator after this revision.
