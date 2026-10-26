# University Hall R5 candidate handoff

**Asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `8f10d54f13262fb4f4c847e41072df28ed2f607d2715171db4a2ff3789e0c05b`  
**Baseline:** R4 `285d85bf33fb2abc6364f29eca268512fc5e299bbc0fd4f49d20fb6eae42a2f6`  
**Fresh standalone reopen:** Blender 5.2.3 LTS; 1,387 objects (1,375 meshes), identity `AssetRoot_university_hall`, no materialless meshes, invalid material indices, missing images, or linked libraries. Evidence: `independent_reopen_r5.json`.

## R5 changes

- Replaced eight repeated gallery column assemblies with five individually detailed reclaimed cast-iron display columns, separated as two at ground level, two at the third-floor gallery, and one at the south stairwell to reflect Purdue's published count and locations. Their coordinates are schematic because no measured interior plan was found. They are display elements, not a claim that they are the new roof supports.
- Replaced the heavy semicircular window curves with shallow, segmental limestone hood moulds, restrained keystones, and jamb reveals registered against the existing east/west window bounds. Ground-floor arches are slightly more prominent; all opening locations and sizes remain unchanged.
- Added a layered entry/transom moulding and limestone inner portico mould; reduced the projection of the repetitive eave consoles.
- Added portable procedural staggered slate courses and restrained brick color/relief variation. The lantern/spire now use a distinct, subdued weathered-copper patina material based on Purdue's close reference. Review lighting uses a stronger directional key and broad fill to show material depth.
- Reframed the gallery evidence view to emphasize the two central void edges, guardrails, display columns, and stair flights. The render hides the building envelope and recreates only a narrow explanatory gallery-edge floor outline plus schematic landing bridges. The current image still shows a visual gap between the stairs and the gallery rings, so the exact circulation path should not be read as verified.
- Preserved the main shell, root transform, and local coordinate frame. No master blend, shared indexes, or README changes were made.

## Review images

- `ground_oblique_r5.png`
- `east_elevation_r5.png`
- `entry_ground_r5.png`
- `interior_cutaway_r5.png`

The cutaway is a temporary explanatory view, not an open-façade condition. The campus footprint comparison remains the R3 result: FID 213 IoU 0.872874, mean boundary residual 0.916 m, 95th percentile 2.292 m, maximum sampled residual 2.470 m. FID 213 is a campus-map outline, not a surveyed wall line.

## Sources and limits

Reviewed 2026-10-25. Purdue's restoration account documents the restored two-story central gallery and five recovered display columns (two ground floor, two third floor, one south stairwell), while separately describing new roof support beams: https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/. Purdue's 2025 exterior image and CLA steeple image informed the roof, window, eave, and trim refinement: https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg and https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg. Purdue's 2025 rededication account documents the current academy overlook/gathering use: https://cla.purdue.edu/academic/history/events/2025/university-hall-rededication-ceremony.html.

No measured architectural elevations or interior plan were found. Roof pitch, tower height, window surround profile, column shape/positions, gallery width, and the stair/landing path remain visual or program-derived estimates. The local geographic conversion and FID 213 comparison are approximate and cannot certify absolute placement. Independent R5 grading is pending; this handoff does not claim a passing score.
