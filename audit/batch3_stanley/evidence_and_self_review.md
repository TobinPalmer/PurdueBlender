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
