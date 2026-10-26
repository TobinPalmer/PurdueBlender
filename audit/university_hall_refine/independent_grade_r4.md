# Independent R4 grade: University Hall

**Reviewed asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `285d85bf33fb2abc6364f29eca268512fc5e299bbc0fd4f49d20fb6eae42a2f6`  
**Result: 6.8/10 — below the 8.0/10 acceptance threshold.**  
**Review date:** 2026-10-25

I independently reopened the exact R4 asset in Blender 5.2.3 LTS and inspected its four R4 renders, geometry/asset integrity, the prior R3 full-ring footprint evidence, and Purdue's current exterior, steeple, restoration, and program sources. The exact-hash reopen is recorded in [independent_reopen_r4_grade.json](independent_reopen_r4_grade.json). This review did not edit the model, master blend, or shared files.

## Reopen and integrity

The reopened `Asset_university_hall` collection contains 1,164 objects (1,151 meshes, one curve, one empty, and 11 lights). The root remains at identity transforms. No materialless meshes, invalid material indices, missing external images, or linked libraries were found. Evaluated bounds are approximately `[-19.075, 19.075] × [-22.300, 22.300] × [0, 29.535]` m. The changed tower height and all roof dimensions remain image-estimated, not surveyed.

## Reference comparison

R4 is a real improvement over R3's failed 5.9/10. Its roof now has a visible pitch break, more substantial lower mansard slopes, ten integrated dormers, and a taller narrow spire. Arched head moulds and eave consoles add detail along the long elevations. The rendered model remains recognizably University Hall.

Several gaps remain visible in the same four R4 views. The upper roof still reads as a broad shallow plane, and the tower crown remains blocky at its base. The façade keeps almost identical window sizes and spacing; the new semicircular moulds read like thick applied trim around square openings. The entry remains a generic column-and-pediment composition. The slate is nearly uniform blue in the renders, and the bright trim and flat sky/light do not show convincing material depth.

The cutaway displays two ring-like gallery floors and an overlook, but the floors take up most of the view. The central two-story opening, stair path and support relationships are still difficult to follow. Purdue's restoration account documents a two-story central gallery and five recovered display columns: two on the ground floor, two on the third floor, and one in the south stairwell. R4's eight repetitive gallery-column supports do not correspond to that documented display-column set. They must remain labeled/treated as schematic support elements unless a stronger source establishes their function or location. Purdue also describes roof beams that resemble historical iron columns, so the recovered display columns should not be conflated with new structural supports.

R4 did not change the exterior shell or footprint evidence. The earlier comparison with campus-map FID 213 remains IoU 0.872874, symmetric mean boundary residual 0.916 m, 95th percentile 2.292 m, maximum sampled residual 2.470 m. The source polygon is not a surveyed wall outline and does not verify absolute campus placement.

## Scorecard

| Category | Weight | Score | Rationale |
|---|---:|---:|---|
| Placement and footprint evidence | 15% | 7.0/10 | The shell and root are preserved; the existing ring comparison exposes a moderate discrepancy against a nonsurvey campus polygon. Master placement was not inspected. |
| Massing and architectural silhouette | 20% | 7.0/10 | Roof break and taller spire improve the silhouette, but the broad upper plane and crown base remain too simple. |
| Facade and entrance | 15% | 6.5/10 | Added arches/consoles help, while repeated openings and generic portal detailing remain conspicuous. |
| Roof and tower fidelity | 15% | 7.0/10 | Mansard, integrated dormers, and narrower spire improve R3; slate courses, eaves, belfry articulation and pitch proportions remain estimated and simplified. |
| Materials and lighting | 10% | 6.0/10 | Portable procedural materials are present, but the renders show flat slate, bright trim and low material depth against plain lighting. |
| Interior gallery coherence | 20% | 6.0/10 | Gallery rings, overlook, feature wall, stairs and railings exist, but the void/circulation is not immediately legible and the 8-column representation is not supported by the public count/location facts. |
| Asset integrity and portability | 5% | 9.5/10 | Exact file reopens cleanly with identity root, valid material assignments and no external dependencies. |

**Weighted score: 6.75/10 (6.8/10 rounded). R4 does not pass.**

## Prioritized R5 work

1. Compare the official exterior and steeple photographs directly with the elevation/oblique views. Rework the broad upper roof and crown transition so the mansard and lantern silhouette better matches the image, while keeping all dimensions labeled as visual estimates.
2. Rebuild window head moulds as deeper, properly registered stone arches/hoods with keystones and reveals. Vary window proportions only where the reference supports it. Integrate the entrance surround and shaped eave brackets into the wall/eave rather than leaving them as applied blocks.
3. Add readable slate courses/material breakup and stronger, daylight-appropriate contrast; the current neutral views do not show enough surface depth.
4. Recompose the cutaway to show the two-story void, both gallery edges, stair flights/landings, and any supports without broad plates or thin repeated posts obscuring the connections. Show the five recovered display columns separately from explicitly schematic structural supports.
5. Freshly reopen the final exact hash, then request another independent review; do not mark finished until a new exact-SHA grade reaches at least 8/10.

## Sources reviewed

- [Purdue Stories: restoration and renewed student hub](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — central gallery, five recovered columns, and new support-beam context.
- [Purdue's 2025 exterior photograph](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg) — roof, spire, dormers, eaves, and façade proportions.
- [Purdue CLA steeple photograph](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) — tower/crown comparison.
- [BuildingShapesZip4 FID 213 service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — campus-map footprint only; not a certified survey.
