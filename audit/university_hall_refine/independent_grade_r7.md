# Independent University Hall R7 grade

**Exact asset SHA-256:** `7ed748bb216108115986f276cb5558a445559be75245be95639158221d8538c1`  
**Weighted score:** **8.005/10 (8.0/10 rounded) — passes the 8.0 threshold narrowly**  
**Review date:** 2026-10-25  
**Blender:** 5.2.3 LTS

## Fresh reopen and asset integrity

I reopened the exact saved R7 file in a fresh Blender 5.2.3 process and recomputed the requested SHA. `Asset_university_hall` contains 1,377 objects (1,364 meshes, one curve, one empty and 11 lights) with an identity `AssetRoot_university_hall`. The export uses 20 materials. There are no empty meshes, materialless meshes, invalid material slots, missing external images, or linked libraries. The detailed reopen report is [independent_reopen_r7.json](independent_reopen_r7.json); the exact-SHA geometry inventory is [independent_grade_r7_structure.json](independent_grade_r7_structure.json).

## Exterior and materials

The reviewed oblique and elevation renders show a recognizable symmetrical, historic academic hall with red brick, slate roof, dormers, lantern and narrow spire. In R7 the portico is better integrated: the pediment return reaches the east façade, the architrave/cornice seats on the column capitals, and the layered entry surround and divided transom complete the composition. The portico still reads as simplified and its proportions are visually estimated.

The east and close entry views show stronger ground-floor segmental window hoods and keys, with shallower upper hoods. The window openings remain unchanged, and the named R7 hood/detail geometry is present in the freshly reopened file. This makes the floor hierarchy more intentional, though the repeated window rhythm remains prominent.

The brick shader now defines separate orientation branches for east-west and north-south walls, nominal 24 cm × 7.5 cm brick courses, mortar variation and subtle bump relief. Brick courses read in a horizontal orientation on both façade directions in the inspection views. The limestone has finer, warmer relief; glazing is less mirror-like; slate remains procedural. The rendered finish is legible but stylized: these previews use Workbench, and the used materials have no image-texture nodes. A final render-engine lighting pass was not part of this review.

## Gallery, stairs and historic column display

The exact-SHA geometry inventory contains two saved stair flights, two saved landings, eight saved gallery-floor pieces, and five distinct display-column assemblies: two ground-floor, two third-floor and one south-stairwell assembly. The saved lower stair bounds overlap the first landing by about 0.42 m along the run; the upper stair overlaps the second landing by about 0.56 m. Both meet the landing elevations. These are geometry-continuity checks, not measured circulation dimensions.

The explanatory R7 cutaways make the open gallery and both levels easier to read. The `gallery_actual_floors_r7.png` view shows the saved floors but their broad slabs hide some stair detail. The cutaways use temporary schematic bands for explanation; they should not be mistaken for saved floor slabs or verified plan geometry. Purdue documents a two-story gallery and five recovered historic columns in the stated display locations; exact interior dimensions and placements remain unverified.

## Placement and source limits

The retained campus-map comparison uses BuildingShapesZip4 FID 213 and reports IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, and maximum sampled residual 2.470 m. This is a map polygon comparison, not a surveyed wall outline. The standalone asset grade did not open the campus master, so master marker placement and neighboring alignment are not scored. Roof pitch/height and the exact façade, window and interior dimensions also remain photo-estimated or schematic.

## Scorecard

Weights and categories follow the R6 grading model. The weighted sum is 8.005/10; rounded to one decimal it is 8.0/10.

| Category | Weight | Score | R7 assessment |
|---|---:|---:|---|
| Placement and footprint evidence | 15% | 7.5/10 | Existing map-polygon comparison is useful but not surveyed; master position was not reviewed. |
| Massing and architectural silhouette | 20% | 8.0/10 | Roof, dormers, lantern and steeple create a recognizable outline; exact proportions remain unmeasured. |
| Facade and entrance | 15% | 8.3/10 | Integrated portico and floor-hierarchical hood geometry materially improve the façade; grid and porch detailing remain simplified. |
| Roof and tower fidelity | 15% | 7.6/10 | Roof/tower remain recognizable, but R7 changes little here and relies on photos for proportions. |
| Materials and lighting | 10% | 8.2/10 | Course direction, mortar and limestone response improve; final-render shading and photographic finish remain unverified. |
| Interior gallery coherence | 20% | 8.0/10 | Saved stairs, landings, floor pieces and five display-column groups are retained and connected in the schematic; evidence views need clearer separation of saved geometry from overlays. |
| Asset integrity and portability | 5% | 9.5/10 | Exact-SHA Blender reopen, identity root, valid materials and no missing dependencies. |
| **Weighted total** | **100%** | **8.005/10** | **Pass, narrowly.** |

## Recommended R8 polish

The R7 candidate passes, so no R8 change is required for acceptance. For a later polish round:

1. Compare the tower, dormers and steeple more closely against Purdue's current exterior photograph; keep the changes reference-backed because measured elevations were unavailable.
2. Provide one section render using only saved geometry, or clearly label temporary explanatory bands so gallery floors and stair routes are not confused.
3. Review the shaders in a neutral final-render-engine view and add restrained surface variation only where the references support it.
4. Preserve the map-source caveat and obtain a surveyed/as-built outline before changing the footprint.

## Sources reviewed

- [Purdue Stories — restoring University Hall](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/), retrieved 2026-10-25. Documents the two-story central gallery, five recovered cast-iron columns and their display categories, and distinguishes them from new roof support beams.
- [Purdue 2025 University Hall exterior photograph](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg) and [Purdue CLA steeple photograph](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg), retrieved 2026-10-25. Selected visual references in the handoff; the direct image files could not be displayed by the browser tool during this review.
- [Purdue CLA rededication page](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html). The source URL was inaccessible to the browser tool in this review and is not used as a decisive grade input.
- [BuildingShapesZip4 feature service, FID 213](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), as documented in the R7 handoff. Its map polygon is not a certified as-built wall survey.
