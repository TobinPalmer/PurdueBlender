# Independent R6 grade: University Hall

**Reviewed asset:** `modular/buildings/university_hall.blend`  
**Exact SHA-256:** `5fb431e4a8c6d5f47e50fc7085de981f64a2f4982b73af57830cdac162bd9da2`  
**Result: 7.8/10 — below the 8.0 acceptance threshold.**  
**Review date:** 2026-10-25  
**Blender:** 5.2.3 LTS

## Fresh reopen and integrity

I opened the frozen file in an independent Blender 5.2.3 process and checked the hash before inspecting it. `Asset_university_hall` contains 1,387 objects (1,375 meshes); `AssetRoot_university_hall` has identity transforms. The evaluated local bounds are approximately `[-19.105, 19.075] × [-22.300, 22.300] × [0, 29.535]` m. The 20 used materials have no invalid material slots; there are no materialless meshes, missing external images, or linked libraries. Reopen details are in [independent_grade_r6_reopen.json](independent_grade_r6_reopen.json); evaluated stair and floor bounds are in [independent_grade_r6_stair_bounds.json](independent_grade_r6_stair_bounds.json).

## Visual and source review

R6 directly addresses the R5 review's most visible defect. In the two cutaway views, the first-to-second-floor stair and upper gallery approach now read as connected to the two gallery levels. I independently measured the saved geometry: the lower stair flight overlaps its 2.35 m landing by about 0.43 m along the run, and the upper flight overlaps its 2.75 m landing by about 0.56 m. Each landing also overlaps the saved west gallery-floor mesh at its own level. These overlaps support a continuous route in the modeled schematic. The saved gallery-floor rings and landings are real asset geometry; the render script additionally adds temporary floor strips to simplify the explanatory cutaway. No measured interior plan was found, so this is evidence of visual/model coherence, not verified as-built circulation.

The five reclaimed-column groups are present by category: two ground-floor assemblies, two third-floor assemblies, and one south-stairwell assembly. Purdue's restoration account documents those five recovered columns and distinguishes them from new structural roof beams. Their exact dimensions and locations remain schematic.

The exterior retains R5's stronger silhouette: steep slate roof, dormers, taller lantern, and narrow spire. It is recognizable in oblique and elevation views. The east elevation still uses a very regular window grid and repeated hoods; the entrance remains a generic pediment-and-column portico. Slate courses and brick variation provide surface relief, but the preview remains stylized with limited tonal depth, and the trim reads as applied repeated bands. R6 does not substantially change these exterior scores from R5.

The footprint result remains the prior campus-map FID 213 comparison: IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, and maximum sampled residual 2.470 m. That polygon is not a surveyed wall line. The local frame and master placement were not reviewed in this standalone grade.

## Scorecard

| Category | Weight | Score | Rationale |
|---|---:|---:|---|
| Placement and footprint evidence | 15% | 7.5/10 | Prior map-ring comparison and local frame are documented; the source is not survey evidence and master placement was outside scope. |
| Massing and architectural silhouette | 20% | 8.0/10 | The mansard, dormers, lantern, and spire make the building recognizable; dimensions remain estimated. |
| Facade and entrance | 15% | 7.4/10 | Window heads and masonry details improve the facade, but the opening grid and generic entrance remain conspicuous. |
| Roof and tower fidelity | 15% | 7.6/10 | Roof/tower hierarchy reads clearly, but roof details, dimensions, and dormer proportions remain image-estimated. |
| Materials and lighting | 10% | 7.5/10 | Procedural slate and brick variation are portable and visible; surface response remains stylized and somewhat flat. |
| Interior gallery coherence | 20% | 8.0/10 | Both saved landings overlap their stair flights and gallery-floor meshes; the cutaway makes the route easier to follow, though the plan and dimensions are schematic. |
| Asset integrity and portability | 5% | 9.5/10 | Exact-hash fresh reopen, identity root, valid materials, and no missing dependencies. |

**Weighted score: 7.80/10. R6 does not pass.** The outside-shell categories remain below full reference fidelity, so the improved gallery connection alone does not raise the total to 8.0.

## Highest-impact R7 work

1. Improve the entrance and the visible facade rhythm with reference-backed details: integrate the portico moulds into the wall/roof junction, and add variation only where Purdue's images support it.
2. Increase the tonal and material depth of the slate, brick, and limestone under the same neutral daylight used for the review views.
3. Render the gallery once with the saved floor rings visible and a clear section through the actual shell; keep temporary schematic path overlays distinguishable from modeled structure.
4. Keep claims about interior dimensions and circulation schematic unless a measured plan becomes available. Reopen and grade the exact next SHA.

## Sources reviewed

- [Purdue Stories: University Hall restoration](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — documents the two-story gallery, five recovered cast-iron columns, and their floor/stairwell display categories; distinguishes them from new roof supports.
- [Purdue CLA: University Hall rededication](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html) — documents the two-story gallery and academy overlook in the completed building.
- [Purdue's 2025 exterior photograph](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg) and [University Hall steeple photograph](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) — visual references, not measured elevations.
- [Purdue BuildingShapesZip4 feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — FID 213 campus-map polygon only; not a certified wall survey.
