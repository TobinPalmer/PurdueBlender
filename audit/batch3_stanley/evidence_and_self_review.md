# Stanley Coulter Hall — Batch 3 handoff

**Asset:** `modular/buildings/stanley_coulter_hall.blend`  
**Evidence checked:** 2026-10-23  
**Scope:** standalone asset and this evidence folder only. Master blend and modular manifest were not edited.

## Source basis

- [Purdue CLA exterior photograph](https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg) (retrieved 2026-10-23; image itself has no date metadata visible in the page). Supports red brick, repeated windows and a rectangular pale-stone entrance surround with glazed doors. Google Maps place-card exterior photo, checked 2026-10-23, shows a similar modern framed entrance; its photo date was not exposed.
- [Purdue e-Archives record PPBUC01117](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/) and [IIIF image](https://earchives.lib.purdue.edu/digital/iiif/pbuildings/1310/full/full/0/default.jpg). The record calls it an undated photograph (digitized 2006-12-01); useful for historic massing and facade character only, not the current entrance or roof condition.
- [Purdue 2025 renovation story](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) states renovations created graduate-student hub space, an English department main office, and office/research-lab spaces in Stanley Coulter. It does not document room-by-room arrangement.
- [2022 Board of Trustees renovation plan](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf), pages 11–13 include basement/first/second-floor project plans. This is historical project scope, **not evidence of present layout**.
- [CLA image gallery](https://cla.purdue.edu/about/college-initiatives/cla-space-project-2022/image-gallery/stanley-coulter.html) was checked but returned an access error during this pass.
- [Google Maps place view](https://www.google.com/maps/place/Stanley+Coulter+Hall+(SC)/@40.4264038,-86.9143489,17z/). Satellite layer was available on 2026-10-23, attributed in UI to Airbus/CNES/Airbus and Maxar; image capture date not shown. “Street View & 360°” opened an indoor panorama by Kaho Sakaue captured Jun 2021. It is not an exterior street panorama, so exterior details were not inferred from it. The place photo and satellite layer verify general visible context, not GIS footprint dimensions.

## Geometry and placement

- Existing GIS assignment is FID 56. Prior project comparison identified polygon centroid `[-57.5958827888, -96.6482404671]` and manifest placement origin `[-57.5568952560, -99.1479358673]` in local project meters. The prior footprint comparison reports source AABB-extrema error below 0.004 m for structural masonry. Preserve the distinction: this is an approximate local conversion, not a surveyed CRS or height validation.
- `AssetRoot_stanley_coulter_hall` remains location/rotation `(0,0,0)`, scale `(1,1,1)`. I did not change the root or manifest marker.
- The reopened standalone has 824 objects in the exported asset collection after the round 2 refinements. Structural wall bounds remain approximately `[-28.115,-24.862,1.8]` to `[28.227,29.336,13.0]` local m. Height and roof dimensions are not independently verified.

## Changes and evidence — review round 2

- Kept the GIS-derived frame and hidden comparison-only ribbon out of presentation renders.
- Rebuilt the 150 window trim objects as restrained rectangular reveal/sill/lintel bars, removing unsupported oversized triangular caps.
- Adjusted the main exterior limestone shader at its connected procedural color nodes (the earlier base-color-only edit did not affect its visible output), darkened/softened slate material, lowered the roof pitch, and reduced/removed unverified dormer and rooftop details from presentation.
- Reworked the entrance to show a layered stone surround, inset-looking double glazed doors, semicircular transom glazing/arch, and slender round supports. This remains partly interpretive: the checked Purdue photo supports a pale stone-framed glazed entrance, but does not fully verify these specific classical projections. The canopy/header remains visually crowded by the upper facade window; dimensions require better current reference.
- Improved the schematic interior with a terrazzo floor patch, room partitions, reception/work desks, chairs, bookcases/stacks, laptops, monitors and task lights. The Trustees 2022 floor plans informed the schematic organization only; they are historical project plans, not confirmation of current as-built room arrangement. The 2025 story substantiates uses (graduate-student hub, English department office, offices/research labs), not exact interiors.
- Standalone saved and reopened successfully after round 2. [final_verification.json](final_verification.json) records 824 asset objects, `AssetRoot_stanley_coulter_hall` at zero location/rotation and unit scale, FID56, unchanged manifest origin, structural-wall bounds, and the prior GIS footprint comparison. Height remains unverified.
- Latest exterior hero: [SC_hero_final3.png](SC_hero_final3.png). Entrance close-up: [SC_entry_final3.png](SC_entry_final3.png). Interior cutaway: [SC_interior_cutaway_final3.png](SC_interior_cutaway_final3.png). Cutaway is a temporary presentation render that hides other collections; it does not change saved visibility.
- Google Maps context and limitations are recorded above: satellite layer checked 2026-10-23 (imagery date not exposed); checked Street View entry opened a June 2021 indoor panorama, with no street-facing panorama exposed. Thus Google Maps provides broad context and a place photo only; it is not a dimensional survey.

## Candid self-review

**Current self-rating: 7.2/10; still below the requested 9/10 and pending independent review.** Round 2 improves the materially incorrect triangular window caps, bright/flat stone, steep roof, entry composition, and nearly blank interior. However, the overall model remains stylized; the roof still reads broad and somewhat flat, and the entrance header is crowded by the facade window above. The interior is now populated, but furniture, room layout, and finishes remain schematic rather than photo-verified. Height and roof profile are not independently measured. The provided renders should be inspected at full resolution; further work should focus on roof/facade proportion and entry-to-window clearance, then receive an independent score before any 9/10 claim.


## R3/R4 revision and validation — 2026-10-25

R3 is saved into the standalone Stanley asset. R4 makes a measured-object change only to the modeled cornice depth and roof-eave vertical alignment; the official foundation and asset root remain fixed. The asset is reopened and validated in Blender 5.2.3. The latest file SHA-256 is `40c1b209881cc7eaba71b1cb0057dc6d735751dd81bf2142ba5b3e4838f03a13`.

### Source-backed changes

- Removed 39 detached bronze-frame faces at z≈20.8 m from 39 third-floor frame meshes. A fresh reopen finds the highest repaired frame vertex at 12.20 m, within the upper modeled opening band.
- Reproportioned 114 east-facade glass, frame, and limestone-trim meshes into wider groupings based qualitatively on the current Purdue CLA photograph. No measured elevation or window schedule was found, so the widths remain visual estimates.
- Shaped both entrance stair cheeks to the stair slope and added thin metal handrails with short supports, following the visible stair/rail composition in the CLA photo. Exact dimensions are estimated.
- Tuned the limestone, glazing, and roof procedural materials.
- Reduced the cornice from 0.90 m to 0.45 m vertical depth and lowered the roof assembly by 0.45 m so the eave meets the thinner cornice. The historic PPBUC01117 image supports a low hipped roof; it is undated and does not prove current roof profile or height. Those remain unverified/estimated.
- Rendered a focused interior cutaway for review. The room arrangement is explicitly schematic based on historical 2022 plans and broad current use categories, not a current as-built layout.

### Reopen and full-outline validation

`reopen_verification_r4.json` confirms 825 objects in `Asset_stanley_coulter_hall`, root location/rotation `(0,0,0)`, unit scale, repaired level-three frames, and the post-R4 roof/cornice bounds. The full-ring comparison uses all 12 vertices of official Purdue ArcGIS FID 56 and the 12 bottom vertices of the asset foundation. IoU is `0.999999899024`, symmetric-difference area `0.000286441 m²`, Hausdorff distance `0.000004506 m`. The outline match is effectively exact in the local project coordinate transform, but this is a campus-map polygon rather than a survey and does not validate walls above the foundation, facade, roof, or height. The registered plan overlay is `SC_footprint_overlay_r3.png`.

### Review renders

- Exterior: `SC_hero_r4.png`
- Entry: `SC_entry_r4.png`
- Interior schematic: `SC_interior_schematic_r4.png`
- Full foundation overlay: `SC_footprint_overlay_r3.png`

**Current candid self-assessment:** improvements address several R1 defects, but the asset remains stylized and the roof, overall elevation details, window grouping, and interior are not independently verified. The R1 score of 4.7/10 is historical; no new score is asserted here. R4 is ready for an independent grader, and it is not being represented as a 9/10 result.


## R5 revision, fresh reopen, and self-review — 2026-10-25

**R5 asset:** `modular/buildings/stanley_coulter_hall.blend`  
**SHA-256:** `d453ca6e1dacfaa3c6c23791396260e9101a5683ddab22d5cd81aaebbcd67c2c`  
**Status:** ready for independent grading; no R5 score assigned.

### R5 changes

- Reduced the east stone portal surround and header/canopy width and projection. Pulled the two round support assemblies back under the header, keeping the recessed double doors, arched transom, layered stone surround, stairs, landing, and rails visible. The CLA photograph supports these entrance features, but not their exact dimensions.
- Reproportioned 72 east-facade window meshes while preserving their opening centers. First- and second-floor units are about 2.50 m and 2.70 m wide; the upper units are about 2.90 m wide to read as a grouped glazed band. These are qualitative photo estimates; no dimensioned elevations were found.
- Applied restrained warm-brown procedural variation to the primary low hipped roof, using the undated Purdue Archives PPBUC01117 photo only as historic context. The 0.45 m pale stone eave remains visually distinct. No physical seams or new roof ornaments were added; current roof construction and height are unverified.
- Moved the 47 high dormant roof/dormer/chimney/HVAC meshes from the R4 bounds audit into the hidden scene-sibling collection `SC_Unverified_Architectural_Options_R5`, outside `Asset_stanley_coulter_hall`. Four copper ridge strips and the unsupported west-entry pediment were also isolated there, for 52 archived meshes total.
- Changed the two entry light blocks from white emission to a subdued warm amber response.
- Produced a top-down piano-nobile use/furniture schematic with an on-image warning that rooms, partitions and furniture are unverified. The render is for review and does not change the saved interior geometry.

### Fresh reopen, collections, bounds, and materials

`reopen_verification_r5.json` records a successful fresh Blender 5.2.3 reopen of the exact hash above. It confirms the expected `Asset_stanley_coulter_hall` collection (773 objects, 763 meshes), an unparented identity `AssetRoot_stanley_coulter_hall`, and a sibling archive hidden in viewport and render and excluded from the asset collection tree. All 47 high option meshes are present in the archive and zero remain in the active asset collection.

Evaluated active-collection bounds are recorded separately: **all active geometry** is X `-48.2827..52.6225 m`, Y `-31.7145..30.7869 m`, Z `-0.2000..15.8700 m`; **render-eligible/viewport-visible geometry** is X `-48.2827..52.6225 m`, Y `-31.7145..30.7869 m`, Z `-0.2000..15.7828 m`. The broad X/Y range includes sidewalks and paving and is not a building footprint. The small 0.0872 m all-geometry/render difference comes from hidden sub-eave dormer fragments still inside the asset collection. The 47 high options that had raised the R4 all-object Z bound to 21.35 m are outside the active collection in the archive.

Material checks found 24 distinct used materials, no active mesh without materials, no invalid material-slot indices, and no materials without shader nodes. Texture checks found no external image-texture nodes/files and no missing images; surfaces use procedural shader graphs.

### Full foundation-outline comparison

The refreshed `full_polygon_comparison_r3.json` compares all 12 vertices of Purdue ArcGIS FID 56 with all 12 bottom vertices of `SC_Foundation_Limestone_Plinth`. IoU is `0.999999899024`, symmetric-difference area `0.000286441 m²`, and Hausdorff distance `0.000004506 m`. The source is an official campus-map polygon in the project’s approximate local-meter conversion, not a certified survey. This comparison validates only the lower plinth outline; it does not validate wall lines, facade, roof or height. The asset root and manifest origin are unchanged.

### Render set and candid self-review

- Exterior: `SC_hero_r5.png`
- Entrance: `SC_entry_r5.png`
- Interior use schematic: `SC_interior_schematic_r5.png`
- Registered full-plan footprint overlay: `SC_footprint_overlay_r3.png`

R5 responds to the R4 grader’s portico, window-rhythm, roof-material and interior-readability comments, and removes the high roof-option objects from the exported collection bounds. The entrance still reads as a simplified architectural visualization; window widths are estimated; the roof silhouette/height has no current measured source; and the interior shows a schematic furnished area rather than verified room partitions and circulation. The master placement marker has not been checked. **R5 is ready for independent grading, but I do not claim that it passes 8/10.**

Source provenance: current Purdue CLA photograph retrieved 2026-10-25 (photo date not exposed); Purdue Archives PPBUC01117 is undated (digitized 2006-12-01); official ArcGIS FID 56 source snapshot dated 2026-10-22 and retrieved 2026-10-25; Trustees 2022 plans and 2025 renovation story were used only for historical layout/broad-use context. URLs and detailed caveats are in `build_report_r5.json`.


## R6 revision, fresh reopen, and candid self-review — 2026-10-25

**R6 asset:** `modular/buildings/stanley_coulter_hall.blend`  
**SHA-256:** `ecc5c02b4eac97d2afee19602e790b86d84f41b3fe78222b17f75f43e70cc61e`  
**Status:** ready for independent grading; no R6 score assigned.

### R6 changes

- Replaced the repetitive third-floor east/courtyard window modules with two grouped glazed runs and a center run spanning the entrance. Narrow bronze mullions follow the existing window centers, and slim limestone head/sill bands join the groups. The current Purdue CLA photograph supports the broad upper glazed composition; exact opening dimensions are estimated.
- Archived the 33 superseded individual east upper-floor trim/frame/glass objects in a hidden scene-level collection; preserved the 52 earlier high roof/entry options and 4 unsupported lantern objects in hidden audit archives outside the exported collection.
- Darkened the shared blue-gray glazing material so the glass reads as window reflections against the brick wall backing. The wall mesh remains solid behind modeled panes, so the asset does not claim view-through glass.
- Closed the two blank view-through rectangles on either side of the portal with 12 brick faces joined into the existing exterior brick mesh. The source photograph shows brick piers flanking the stone portal. The inserted extents are estimates fitted between existing window trim and the portal; they are not surveyed wall dimensions.
- Reduced the projecting stone entablature depth from 0.87 m to 0.54 m and its height from 0.47 m to 0.31 m while retaining the round supports, recessed double doors, arched transom, steps and rails. These values are mesh bounds, not surveyed measurements.
- Added a weak procedural wave bump for restrained roof-course breakup. No current roof profile or material was found; roof form, construction and total height remain unverified.
- Added an explicitly schematic public-entry-to-lobby corridor, landing and walls. Bounding-box overlap is 0.1236 × 0.9655 × 0.0100 m at the door threshold, 0.1500 × 1.7000 × 0.0480 m with the landing, and 0.2912 × 1.1091 × 0.0100 m between landing and stair shell. These are geometric connectivity checks, not proof of as-built interior routing. The plan render is labeled schematic because a current as-built interior plan was unavailable.

### Fresh reopen and checks

`reopen_verification_r6.json` records a fresh Blender 5.2.3 reopen of the exact hash above. The expected export collection contains 760 objects/750 meshes and an identity root. It reports 24 used materials, no materialless meshes, no invalid material slots, no external image textures, and no missing images. The three hidden recovery collections are outside the active export: 52 roof-option meshes, 33 superseded facade-window objects and 4 unverified lantern objects.

The R3 full foundation ring still matches Purdue ArcGIS feature 56 with IoU `0.999999899`, symmetric difference `0.000286441 m²`, and Hausdorff distance `0.000004506 m` in the project's approximate local-meter frame. R6 did not change the foundation ring. The source is the official campus-map outline rather than a certified survey; this comparison does not verify above-grade walls, facade, roof, or height.

### R6 review renders

- Exterior: `SC_hero_r6.png`
- Entry: `SC_entry_r6.png`
- Connected-circulation schematic: `SC_interior_circulation_r6.png`
- Registered full-plan footprint overlay: `SC_footprint_overlay_r3.png`

**Candid self-review:** the grouped upper glazing and restored brick piers address the most visible facade mismatches and the interior cutaway now shows a connected schematic route to the stair. The exact window grouping, entry infill and corridor are still inferred from limited references. The roof silhouette/height and room-by-room interior remain unverified. This asset-only task did not open or edit the master placement marker or the assembled campus neighborhood. **R6 is ready for independent grading; I do not claim it meets 8/10 until a separate reviewer assigns a passing score.**

Source provenance, hashes, and detailed uncertainty notes are in `build_report_r6.json`. References are the undated current-looking Purdue CLA facade photo (retrieved 2026-10-25), Purdue Archives PPBUC01117 (undated historic roof context), Trustees floor-plan sheets dated 2022-09-28, and official ArcGIS FID 56 snapshot dated 2026-10-22.
