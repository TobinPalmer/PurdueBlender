# University Hall R6 candidate handoff

**Asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `5fb431e4a8c6d5f47e50fc7085de981f64a2f4982b73af57830cdac162bd9da2`  
**Baseline:** R5 `8f10d54f13262fb4f4c847e41072df28ed2f607d2715171db4a2ff3789e0c05b`  
**Fresh standalone reopen:** Blender 5.2.3 LTS; 1,387 objects (1,375 meshes), identity `AssetRoot_university_hall`, 20 used materials, no materialless meshes, invalid material indices, missing images, or linked libraries. Evidence: `independent_reopen_r6.json`.

## R6 changes

- Increased the first gallery stair landing from 1.70 m to 2.35 m in the stair-run direction, and the upper landing from 1.70 m to 2.75 m. These overlap the adjoining flight ends by approximately 0.43 m and 0.56 m respectively, while meeting the gallery floor elevations. Dimensions remain schematic; Purdue does not publish a measured interior plan.
- Reworked the explanatory cutaway to show two full-thickness gallery-edge bands and a continuous L-shaped path from each stair landing along the west/south gallery edge into the ring around the two-story void. The upper path passes beside the stair flight rather than across it. All temporary cutaway floor geometry is removed after each render and is not saved into the building asset.
- Retained the five R5 reclaimed-display-column assemblies and their documented floor/stair categories. Their exact positions remain schematic.
- Preserved the R5 shell, roof, façade, materials, local frame, and identity root. No master blend, shared index, or README files were changed.

## Review images

- `ground_oblique_r6.png`
- `east_elevation_r6.png`
- `entry_ground_r6.png`
- `interior_cutaway_r6.png` — west-side cutaway angle
- `interior_cutaway_southeast_r6.png` — southeast cutaway angle
- `interior_stair_profile_r6.png` — stair-profile angle

The cutaways hide the building envelope and non-gallery interior objects. Their simplified floor-path segments are an explanatory representation, not a measured as-built circulation plan.

## Evidence, sources, and limits

Purdue's restoration account documents a two-story central gallery and five recovered display columns (two on the ground floor, two on the third floor, and one in the south stairwell), while distinguishing these from new roof supports: https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/. Purdue's 2025 exterior image and CLA steeple image inform roof and façade appearance: https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg and https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg. No measured architectural elevations or interior plan were found.

Earlier plan comparison remains against campus-map BuildingShapesZip4 FID 213: IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, maximum sampled residual 2.470 m. The source is not a certified survey. Roof profile/height, window surrounds, interior dimensions, column positions, and stair routing remain estimated. Independent R6 grading is pending; this handoff does not claim a passing score.
