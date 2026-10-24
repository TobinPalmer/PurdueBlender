# Aquatic Center R2 — revision and evidence notes

**Asset:** `modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend`  
**Date:** 2026-10-24  
**Scope:** Aquatic asset and its dedicated audit folder only. No master blend, README, manifest, shared index, or other building was changed. No commit was made.

## Response to R1 independent score (7.6/10)

The reviewer marked exterior/roof (6.8), render/material (6.4), and height/detail (7.0) as the weakest categories. R2 adds facade depth and bay rhythm, fixes the shell-to-gable roof silhouette, removes the inherited wrong-elevation roof/sign bars, improves entry sign scale, adds visible seating and a mezzanine gallery, and uses stronger brick, concrete, roof, and glazing shaders. Interior review views now hide the exterior shell, roof, structure and trusses temporarily so pool and spectator features read clearly.

## R2 work

- The north exterior remains tied to the July 2023 Google Street View observation from R1. Added eight masonry piers, water-table/belt/eave courses, and framed ribbon panes. The north entry name now has a dark plaque and readable gold letters. The plaque’s exact size is presentation-scale estimation; only its centered location/name placement is source supported.
- Corrected a major inherited geometry issue: R1's continuous shell rose to 12m along every edge, making the building appear to have raised walls standing above the roof. It now follows the existing shallow gable estimate (9.2m eave to 12.2m ridge). The roof was extended slightly past the footprint and gained a ridge cap and eave gutters. These do not claim an as-built roof survey; Purdue's mechanical-project document confirms roof work but does not publish the roof section.
- Built representative individual seating blocks, one east-side bank of 300 visible seats, and a schematic mezzanine/guardrail/stairs. Purdue publishes 625 seats and a mezzanine; the exact layout, height, and circulation are not publicly dimensioned. The model therefore represents part of the published capacity and does not invent a claimed full 625-seat plan.
- Added subtle procedural relief/color variation to brick, concrete, roof metal, and glazing; refreshed exterior daylight and pool-hall soft lighting. All shaders remain procedural, with no external images.
- Removed the inherited gold sign/fascia from the opposite elevation; it was visibly floating across the pool and did not match the observed north entrance.

## Sources and confidence

- [Google Street View north approach, panorama y0c6EFsDkT7g2ak3hsZh5A, July 2023](https://www.google.com/maps/@?api=1&map_action=pano&pano=y0c6EFsDkT7g2ak3hsZh5A): supports north elevation brick, ribbon glazing, centered entrance and building-name sign. Does not measure wall/roof heights or hidden elevations.
- [Purdue RecWell Aquatics](https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php): supports the 8×50m competition pool, 6×26-yard dive pool, 17-ft depth, five platform heights, four springboards, spa and 625 spectator seats.
- [Purdue Recreation Facility Fact Sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php): supports spectator seating, mezzanine, and offices/lobby/meet management/lounge/classroom/locker-room program. No room placement plan found.
- [Purdue Athletics facility page and gallery](https://purduesports.com/facilities/morgan-j.-burke-aquatic-center/12): confirms opened in 2001, location west of CoRec, and published official pool/dive imagery. The page does not provide an as-built exterior elevation drawing.
- [Purdue Treasurer project description (2025–26)](https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Burke-Boilermaker-Aquatic-Center-Mechanical-B-1-24-4-15-1.pdf): confirms planned roof replacement work, but no roof geometry or elevation dimensions.
- [Official BuildingShapesZip4 footprint snapshot, FID 896](../batchC_boilermaker_aquatic_official_footprint.json): preserves footprint geometry. GIS alignment is not survey control. `Extrution=12` field units and definition are undocumented; heights remain estimated.

## Validation and renders

`validation_r2.json` records a fresh reopen in Blender 5.2.3 and passed checks. The perimeter validator compares all 70 transformed GIS boundary edges with all 70 shell segments in both directions (11 samples per GIS segment and 3 per shell segment); maximum sampled mismatch is 0.000002m. It also verifies 57 framed ribbon panes, material assignment, 300 representative seat blocks, mezzanine, the published 17-ft dive depth and all five platform elevations. This validates source alignment and object presence; it does not prove surveyed elevation or an as-built interior plan.

R2 renders:
- `aquatic_r2_north_three_quarter.png` — building mass, north entry, north facade rhythm and shallow gable.
- `aquatic_r2_north_entry_sign_detail.png` — readable sign and window frame detail.
- `aquatic_r2_interior_seating_cutaway.png` — both pool areas, dive tower and representative spectator seating.
- `aquatic_r2_interior_feature_detail.png` — closer pool/tower review.

The cutaway-only hide flags were restored after rendering; the saved asset remains a complete building. Independent R2 review is pending; no self-score claimed.
