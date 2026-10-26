# University Hall R4 candidate handoff

**Asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `285d85bf33fb2abc6364f29eca268512fc5e299bbc0fd4f49d20fb6eae42a2f6`  
**Baseline:** R3 `3784451714a60a04b482c12031ac413ac5ed2c69d4b268d79f05e4816cf07f3b`  
**Fresh standalone reopen:** Blender 5.2.3 LTS; 1,164 objects (1,151 meshes), identity `AssetRoot_university_hall`, no materialless meshes, invalid material indices, missing images, or linked libraries. Evidence: `independent_reopen_r4.json`.

## R4 changes

- Removed the superseded R5-prefixed geometry inherited in the failed R3 file before rebuilding the roof, dormers, tower crown, entry details, columns, and stairs; this prevents coincident duplicate meshes.
- Rebuilt four continuous two-pitch mansard assemblies. The lower rise is 2.62 m over a 3.25 m horizontal run; the upper rise is 1.55 m over about 4.0 m. Added thicker lower roof shells, a defined pitch-break cornice, an inset upper deck, and ten integrated east/west dormers. Roof pitch and dormer dimensions are visual estimates from Purdue imagery, not measured drawings.
- Made the copper/slate lantern spire taller and narrower, raising the evaluated top from 27.7 m to about 29.5 m. This is image-proportioned; no measured height source was found.
- Added small limestone eave consoles and correctly registered arched limestone window-head moulds on the long elevations. The old misregistered arch curve was removed. Existing main shell and window positions remain unchanged.
- Added the two-ring gallery floors, 7.6 × 12.0 m first-level opening, 6.6 × 10.8 m academy overlook, library feature wall/book bays, railings, stepped stair flights, and display columns. The plan, furniture, structural layout, and column locations remain schematic; Purdue publishes broad program facts, not as-built interior dimensions.
- Kept the standalone local origin and root transform unchanged; did not edit master, shared indexes, or README.

## Review images

- `ground_oblique_r4.png`
- `east_elevation_r4.png`
- `entry_ground_r4.png`
- `interior_cutaway_r4.png`

The cutaway is a review view with two façades and roof elements hidden; it is not a claim that the building has open façades.

## Sources and limits

Retrieved 2026-10-25. Purdue's 2025 restoration account supports the restored two-story central gallery, student use, and historic columns: https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/. The article's official exterior photograph and Purdue CLA's steeple photograph were used for roof, spire, window-head, and trim proportions: https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg and https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg. Purdue's 2025 completion account supports the academy overlook and current gathering-space program: https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html.

The model wall shell remains unchanged. Earlier full-ring comparison against Purdue BuildingShapesZip4 FID 213 produced IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, and maximum sampled residual 2.470 m. That polygon is a campus-map outline, not a surveyed wall line. The project-local conversion from EPSG:4326 follows `X=(longitude+86.9137)*111412.84*cos(radians(40.4274))`, `Y=(latitude-40.4274)*111040`; it is approximate, not a formal projected CRS. Do not treat roof pitch, crown height, room layout, window spacing, or gallery structure as measured. Independent R4 grading is pending; this handoff does not claim a passing score.
