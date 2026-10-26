# University Hall R7 candidate handoff

**Asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `7ed748bb216108115986f276cb5558a445559be75245be95639158221d8538c1`  
**Baseline:** R6 `5fb431e4a8c6d5f47e50fc7085de981f64a2f4982b73af57830cdac162bd9da2`  
**Fresh standalone reopen:** Blender 5.2.3 LTS; 1,377 objects (1,364 meshes, one curve, one empty, 11 lights), 20 used materials, identity `AssetRoot_university_hall`; no materialless meshes, invalid indices, missing images, or linked libraries. Evidence: `independent_reopen_r7.json`.

## R7 changes

- Rebuilt the portico pediment return so it reaches the east façade at approximately X=3.60 m, tying the gable into the wall instead of leaving the prior gap. Added a shallower architrave/cornice seated at the existing column capitals, moulded pediment slopes, squared impost blocks, and a layered entry surround with divided transom. These details are proportion estimates from Purdue's current exterior imagery, not measured elevations.
- Preserved the original window openings and their symmetry. Reduced the repeated look in the stone surrounds through a floor hierarchy: stronger ground-floor segmental hoods and keys, with thinner, lower-profile upper-floor hoods/reveals. No aperture locations or sizes changed.
- Reworked the brick shader to orient brick courses correctly on both long and short elevations, added mortar relief and restrained red-brown brick variation. Warmed and varied the limestone shader at finer scale, and adjusted glass toward a subtler daylight reflection. Slate retains portable procedural courses.
- Preserved R6 landings, stair-flight overlaps, gallery-floor connections, the five documented reclaimed-column groups, shell, local coordinate frame, and root transform.
- Rendered both a focused explanatory cutaway and a second view with the saved gallery floor rings visible. The latter preserves actual saved floor geometry, though broad slabs obscure some stair detail; the focused cutaways use temporary schematic floor bands and are not saved into the asset.
- Did not edit the master blend, shared indexes, or README.

## Review images

- `ground_oblique_r7.png`
- `east_elevation_r7.png`
- `entry_ground_r7.png`
- `interior_cutaway_r7.png`
- `interior_cutaway_southeast_r7.png`
- `interior_stair_profile_r7.png`
- `gallery_actual_floors_r7.png`

## Evidence and limits

Purdue's 2025 exterior photograph and CLA steeple photograph informed the visible façade, roof, window, and portico proportions: https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg and https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg. Purdue's restoration account documents the two-story gallery and five recovered columns (two ground floor, two third floor, one south stairwell): https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/. No measured elevation or interior plan was found.

The prior campus-map comparison to BuildingShapesZip4 FID 213 remains IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, and maximum sampled residual 2.470 m. This polygon is not a surveyed wall outline. Roof pitch/height, façade details, column positions, gallery dimensions, and circulation remain visually or program-derived estimates. Independent R7 grade is pending; no pass is claimed.
