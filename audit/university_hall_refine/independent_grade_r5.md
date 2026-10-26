# Independent R5 grade: University Hall

**Reviewed file:** `modular/buildings/university_hall.blend`  
**Exact SHA-256:** `8f10d54f13262fb4f4c847e41072df28ed2f607d2715171db4a2ff3789e0c05b`  
**Result: 7.4/10 — below the 8.0/10 threshold.**  
**Review date:** 2026-10-25

I freshly reopened the frozen R5 file in Blender 5.2.3 and confirmed the exact requested SHA before reviewing the four R5 renders. Reopen evidence is in [independent_grade_r5_reopen.json](independent_grade_r5_reopen.json). I reviewed Purdue's public restoration and renovation sources and the prior GIS footprint comparison. This grade does not inspect the master scene or certify surveyed geometry.

## Reopen and integrity

The exported collection contains 1,387 objects (1,375 meshes), with 20 used materials and an identity root. There are no materialless meshes, invalid material slots, missing external images or linked libraries. The evaluated bounds are approximately `[-19.105, 19.075] × [-22.300, 22.300] × [0, 29.535]` m. These checks support portability and geometric integrity; they do not prove architectural fidelity.

## Visual review

R5 improves on R4. In the oblique and elevation renders, the steeper lower mansard, slate courses, ten dormers, taller square lantern and narrow spire now read as an institutional historic building and make University Hall recognizable. The five recovered-column display assemblies reflect Purdue's reported count and locations. The hood moulds, restrained keystones, eave detail, entry moulding, and brick/slate variation add useful relief. These are material improvements, though all roof and facade dimensions remain image estimates.

The entry still reads as a generic portico: a broad plain pediment, simple cylindrical columns, and generic doors. The window grid remains very regular; repeated pale hoods and mullions stand out as applied trim. Slate is patterned, but its repeated tiles and uniform long roof planes remain schematic. The brick, glass and limestone show better relief than R4 but still lack the tonal depth and detail visible in the reference image.

The interior cutaway is the main reason R5 does not pass. It shows two gallery edges and their railings around a central opening, plus the reclaimed columns. However, the detached stair flight on the left has a visible gap from the gallery rings. The viewer cannot follow a continuous route from the stairs to either gallery level. The floors and railings are simplified schematic rings, so the cutaway does not establish the actual two-story gallery geometry or connected circulation. The handoff itself calls out the unresolved gap. Purdue documents the two-story opening and the five recovered columns, but the public sources do not provide a measured interior plan. The model should therefore show any guessed stair connection as schematic and separate it clearly from verified facts.

The prior plan comparison remains against campus-map FID 213: IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, and maximum sampled residual 2.470 m. This polygon is not a surveyed wall outline. Master placement was not reviewed.

## Scorecard

| Category | Weight | Score | Rationale |
|---|---:|---:|---|
| Placement and footprint evidence | 15% | 7.5/10 | Existing local root and plan evidence are documented, but the map polygon is not a survey and master placement was outside this review. |
| Massing and architectural silhouette | 20% | 8.0/10 | R5 meaningfully improves the mansard, dormers, lantern and spire silhouette; dimensions remain estimated. |
| Facade and entrance | 15% | 7.4/10 | Better hood moulds and entry relief, but uniform openings and generic portico remain conspicuous. |
| Roof and tower fidelity | 15% | 7.6/10 | A recognizable slate mansard and tower are present; dormer proportions, eaves and upper roof/crown remain approximate. |
| Materials and lighting | 10% | 7.5/10 | Slate/brick variation and directional light improve R4, but surfaces still appear flat and repetitive in the renders. |
| Interior gallery coherence | 20% | 6.2/10 | Two gallery levels appear, but the staircase is visibly disconnected and the cutaway does not explain the circulation route. |
| Asset integrity and portability | 5% | 9.5/10 | Exact-SHA fresh reopen, identity root, valid materials and no missing dependencies. |

**Weighted score: 7.44/10 (7.4/10 rounded). R5 does not pass.**

## Priority fixes for R6

1. Rebuild the cutaway around a single clear sightline through the two-story void. Connect visible stair flights to actual gallery landings, show the landing transitions, and remove or hide ring surfaces that obscure that connection. Keep the route labeled schematic where no plan supports it.
2. Keep the five recovered display columns separate from any guessed structural supports. Check the five distinct modeled assemblies, not just their component-mesh count, against Purdue's stated two ground-floor, two third-floor, one south-stair locations.
3. Refine the entrance beyond a generic pediment-and-cylinder portico, and vary window head treatment only where the reference supports it. Integrate hoods and surrounds with jambs and wall reveals.
4. Improve depth and tonal range in the slate, brick, glass and limestone; inspect neutral material and daylight views to ensure the roof surfaces remain legible.
5. Reopen and grade the next exact SHA. Do not mark finished until the new independent grade reaches at least 8/10.

## Sources reviewed

- [Purdue Stories: University Hall restoration](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — two-story central gallery, new roof support beams, and five recovered columns with stated display locations.
- [Purdue CLA: University Hall renovation and preservation](https://cla.purdue.edu/news/college/2025/university-hall-renovation-and-preservation.html) — corroborates the gallery, recovered columns, and current interior program.
- [Purdue Stories: 2025 exterior photograph](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg) and [Purdue CLA steeple photograph](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) — visual references, not measured drawings.
- [Purdue BuildingShapesZip4 feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — FID 213 campus-map polygon only; not a certified as-built survey.

