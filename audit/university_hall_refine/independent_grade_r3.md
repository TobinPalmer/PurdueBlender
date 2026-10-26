# Independent R3 grade: University Hall

**Reviewed asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `3784451714a60a04b482c12031ac413ac5ed2c69d4b268d79f05e4816cf07f3b`  
**Result: 5.9/10 — below the 8.0/10 acceptance threshold.**  
**Review date:** 2026-10-25

I independently reopened the exact R3 file in Blender 5.2.3 LTS and reviewed its saved structure, all four R3 views, the prior independent R2 report, Purdue's current restoration photos and project descriptions, and the complete FID 213 footprint comparison. I did not edit the Blender asset, master, or shared project files. Independent reopen details are in [independent_reopen_r3_grade.json](independent_reopen_r3_grade.json); the exact-hash check and the independent reopen both agree.

## Reopen and asset integrity

Blender reopened the candidate as scene `Building_university_hall`; collection `Asset_university_hall` contains 1,111 objects (1,098 meshes, one curve, one empty, and 11 lights). The asset root has identity transforms. The meshes use 19 materials, with no materialless meshes, invalid material indices, linked libraries, or missing external image files. This confirms a clean, self-contained asset reopen. It does not establish architectural fidelity.

## Reference review and findings

The R3 exterior is recognizable as a red-brick institutional building, and its two-pitch roof, ten dormers, stone courses, and central tower are improvements over the R2 render. The difference from Purdue's current exterior image remains substantial. In the current photo, the tower rises distinctly above the roof, with a tall, narrow spire, articulated brick stage, and louvered openings. Its roof is a steep, dark mansard with integrated dormers, patterned slate, deep white eaves, and brackets. R3 instead reads as a squat open square tower with a short cap and tiny spire over a mostly broad, shallow roof. Its lower pitch does not read as a strong, continuous mansard from the submitted elevation and oblique views; the dormers read as small repeated boxes.

The current photo also shows varied window widths and arched heads, deep pale stone surrounds, prominent eaves brackets, and more articulated brickwork. R3's windows repeat in a strict grid with nearly identical square proportions and thin white frames. The entry portico is legible but generic: its broad plain pediment and columns do not convey the building's detailed historical trim. The uniform cool slate and pale bands are readable as assigned materials, but the render does not show the slate pattern, tonal variation, and masonry detail visible in Purdue's photo. The simplified lighting and blank sky reduce material depth further.

The cutaway does show two levels of gallery slab, column rows, stair flights, landings, and railings. It is not convincing enough as a view of the completed two-story central gallery: the broad slabs dominate the void, many slim supports look like a grid of generic posts, and the stairs/landings are small and hard to follow. Some supports appear visually to meet the gallery slabs, but the image does not make a continuous, connected route and support system easy to verify. Purdue's restoration account confirms a two-story central gallery and reintroduced historic columns, but does not establish exact interior dimensions or the modeled column layout. I therefore judge legibility and evidence limits, rather than treating the schematic arrangement as a verified as-built plan.

### Full-ring footprint evidence

The FID 213 comparison is stronger than the previous R2 bounds-only check: full-ring IoU is 0.8729, symmetric difference is 121.623 m², symmetric mean sampled boundary residual is 0.916 m, 95th percentile is 2.292 m, and maximum sampled residual is 2.470 m. These are explicit residuals against a Purdue campus-map polygon. That polygon is not a surveyed wall line, and the local projection is approximate. The comparison is useful evidence of a mismatch between the rectangular modeled shell and the map ring, but it is not proof that either line is the as-built wall perimeter. The R3 choice to keep the shell pending corroborating evidence is reasonable; the remaining plan-fit uncertainty lowers the placement score.

## Scorecard

| Category | Weight | Score | Rationale |
|---|---:|---:|---|
| Placement and footprint evidence | 15% | 7.0/10 | Full-ring metrics expose a moderate discrepancy. Map geometry and approximate local projection are not survey evidence. |
| Massing and architectural silhouette | 20% | 5.5/10 | Recognizable massing, but tower hierarchy and the roof profile remain weak in both oblique and elevation views. |
| Facade and entrance | 15% | 5.5/10 | Brick and entrance are present; window rhythm, arched heads, eave detail, and portal articulation remain generic. |
| Roof and tower fidelity | 15% | 4.8/10 | Pitched roof and dormers exist, but the roof reads shallow and the tower/spire is far too squat versus Purdue's photo. |
| Materials and lighting | 10% | 5.5/10 | Assigned procedural materials are portable, but slate, stone, and trim lack the reference's pattern, contrast, and surface depth. |
| Interior gallery coherence | 20% | 5.8/10 | Both gallery levels and stairs are represented, but the cutaway does not clearly communicate the open two-story space, connected circulation, or column support logic. |
| Asset integrity and portability | 5% | 9.5/10 | Exact file reopens cleanly, with identity root, valid material assignments, and no external dependencies. |

**Weighted score: 5.9/10** (5.945 rounded to one decimal). R3 does not pass the requested 8.0 threshold.

## Prioritized R4 work

1. Rebuild the roof-and-tower silhouette against Purdue's current exterior photo. Make the mansard slope clearly steep and continuous, integrate dormers into that slope, and give the tower a taller articulated brick stage and narrow, dominant spire. Check both orthographic elevation and ground-level oblique views.
2. Replace the repetitive square window rhythm with evidence-backed variation in opening width, arched heads, surrounds, and keystones; model the deep eaves and brackets that distinguish the current facade. Strengthen the portal details without inventing unsupported historical ornament.
3. Rework the cutaway composition so the open central void, two continuous gallery/overlook levels, and stairs joining their landings read immediately. Verify every major post/column meets a support surface; label any intentionally displayed historic column elements separately from structural supports. Keep the room arrangement explicitly schematic absent as-built plans.
4. Improve slate pattern and tonal response, limestone/painted trim relief, brick variation, and daylight contrast so the architectural shape is visible without relying on bright flat trim.
5. Use the FID 213 ring as a discrepancy guide, not ground truth. Seek another independent plan/photo source before changing the wall shell, then report any corrected residuals with the same map-source limitation.
6. Re-render the same four views and submit a new exact SHA for independent review.

## Sources reviewed

- [Purdue Stories, restoration and current use](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — two-story gallery, restoration philosophy, recovered columns, and current student-centered program.
- [Purdue CLA, University Hall rededication](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html) — completed gallery and academy overlook.
- [Purdue CLA current exterior photo](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg) — current tower, roof, dormers, eaves, and facade details.
- [Purdue CLA steeple photo](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) — close view of tower and slate roof.
- [FID 213 feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — campus-map polygon only, not a certified as-built survey.

This report and the independent reopen script/JSON are the only new files written under `audit/university_hall_refine/` for this review. No model, master blend, shared index, or Git history was changed.
