# Independent R2 grade: University Hall

**Reviewed asset SHA-256:** `227d6163491da17cb4ec9a34155951b62c921089d5d0e383e01c5e50614fbeef`  
**Result: 5.6/10 — below the 8.0/10 acceptance threshold.**  
**Review date:** 2026-10-25

This is a fresh, independent review of R2. The prior 4.3/10 score applies to the earlier R1 SHA and was not reused. I reopened the exact R2 asset in Blender 5.2.3 LTS and inspected its saved geometry plus the three R2 review renders. No model or master scene was changed.

## Fresh reopen and asset integrity

The exact requested SHA was confirmed on disk and on fresh reopen. Blender opened scene `Building_university_hall` with collection `Asset_university_hall`, 1,003 objects (990 meshes, one curve, one empty, 11 lights), and an identity `AssetRoot_university_hall`. The collection has 20 used materials; all meshes have valid material slots. There are no image-texture nodes, missing external image paths, or linked libraries. Procedural node materials keep the asset self-contained, but the lack of image textures and the flat roof appearance in the renders limit visual material credibility.

Independent reopen details: [independent_reopen_r2.json](independent_reopen_r2.json). Views reviewed: [oblique exterior](oblique_southwest_r2.png), [east elevation](east_elevation_r2.png), and [interior cutaway](interior_cutaway_r2.png).

## Reference comparison

Purdue's 2025 restoration account describes a student-centered hub, the restored two-story central gallery, historic roof trusses, and a restoration approach that deliberately retains and reinterprets historic elements. The CLA rededication account describes the completed gallery and second-floor overlook. The model has added a roof form, dormers, tower/spire, facade surrounds, gallery rings, columns, and stairs; these are meaningful improvements over R1. However, the submitted exterior renders still show a broad, shallow roof plane with little visual separation between the lower mansard and upper roof. Dormers read as small boxes sitting on the roof, and the tower crown reads as a thin open square frame with a small pyramid cap. The prominent historic roof-and-tower silhouette is therefore still not convincing.

The exterior elevations show a plausible red-brick, three-level mass with pale courses, regular window openings, and a central entry. The window rhythm remains highly repetitive; trim is thin and uniform, and the entry lacks a strong, legible historic portal. Procedural brick is visible, but the slate reads as a single pale blue, largely smooth plane.

The cutaway suggests floors, galleries, stairs, columns, and an overlook, but the atrium is hard to read as a coherent two-story space. Several upper wall/column-like pieces appear suspended and disconnected above the floors in the submitted view. Stairs and gallery edges are diagrammatic, and there is little furniture or room activity to convey the completed student commons. Purdue's current renovation descriptions support a gallery, overlook, classrooms, and collaboration/study spaces; they do not support treating the 2022 Trustees plans as a verified as-built dimension survey. The interior should remain an evidence-based schematic unless current as-built plans are obtained.

For location screening, the original main wall shell was preserved. Adding the asset's manifest placement origin to the independently measured shell-object bounds gives approximately X = -137.57 to -115.65 m and Y = -258.15 to -214.91 m. The official campus-map polygon for FID 213 has bounds X = -137.82 to -115.43 m and Y = -257.92 to -214.36 m. This is close at the bounds level (roughly 0.2–0.6 m per edge), and the long axis is aligned north/south as expected. The official source marks its polygon as a campus-map reference rather than a certified survey. This comparison checks only the shell AABB; it does not establish vertex-by-vertex perimeter overlap or a survey-grade fit. The previously recorded 0.391 m center offset and 0.9617 AABB IoU also describe bounds screening, not a polygon intersection test.

The 2022 Board of Trustees renovation packet was considered as program/design context only. Its proposed floor plans predate the completed 2025 renovation and do not establish current as-built room dimensions.

## Scorecard

| Category | Weight | Score | Rationale |
|---|---:|---:|---|
| Campus placement and footprint evidence | 15% | 7.5/10 | Main-shell bounds are close to FID 213, with about 0.39 m center offset; true GIS polygon overlap and precise wall fit remain unverified. |
| Massing and architectural silhouette | 20% | 5.5/10 | Three-level brick mass is recognizable, but the roof remains broad and shallow and the tower has weak hierarchy in the renders. |
| Facade and entrance detail | 15% | 5.5/10 | Brick, pale bands, window surrounds, and a central entry exist; window rhythm and entrance articulation remain generic and repetitive. |
| Roof and tower fidelity | 15% | 4.5/10 | Pitched planes and dormers are present, but the mansard reads as a shallow hip and the crown does not yet convey the reference silhouette. |
| Materials and surface treatment | 10% | 6.0/10 | Procedural brick and slate materials are self-contained and assigned; roof and trim look too uniform in the review lighting. |
| Interior coherence and supported program | 20% | 4.0/10 | Gallery/stair components exist, but the cutaway is difficult to interpret and includes visibly disconnected-looking upper parts; interior is sparse. |
| Asset integrity and portability | 5% | 9.0/10 | Exact hash freshly reopens; collection/root, valid assignments, and no external dependencies are confirmed. |

**Weighted score: 5.6/10** (weighted arithmetic: 5.575, rounded to one decimal). This does not pass the 8.0/10 threshold.

## Required R3 work

1. Rework the roof silhouette against Purdue's current exterior photographs: make the lower mansard slope visibly steeper and distinct from the upper roof, integrate the dormers into that slope, and establish the tower/spire as a dominant, coherent roof feature. Avoid treating dormer count or dimensions as measured facts.
2. Improve the tower's proportions and transitions so the shaft, clock/bell stage, cap, and spire read as one supported architectural assembly from ground-level views. Check the silhouette in orthographic elevation and oblique views.
3. Repair the cutaway composition and geometry: eliminate floating or detached-looking facade/column pieces, ensure supports meet their floors and gallery rings, make stair flights connect to landings, and clearly expose a continuous two-story gallery with the overlook.
4. Strengthen the entrance hierarchy and facade articulation using current photos. Keep the window spacing grounded in evidence while giving the entry and major trim enough depth and contrast to read at building scale.
5. Improve the slate/stone material response and render lighting so roof relief, brick variation, pale surrounds, and trim are legible. The procedural materials are portable, so external image textures are not required to pass if the result reads convincingly.
6. Validate the transformed exterior wall footprint against the complete FID 213 ring, not only its axis-aligned bounds, and report vertex-level overlap or explicit residuals. Do not infer height from the campus-map attribute.
7. Re-render the same oblique, elevation, and cutaway views after the fixes and submit a new exact asset hash for independent review.

## Sources

- [Purdue Stories, “Restoring Purdue’s University Hall as a campus crown jewel” (June 30, 2025)](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — present renovation/restoration context, gallery, roof trusses, current use, and exterior imagery.
- [Purdue CLA, University Hall rededication (October 25, 2025)](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html) — completed gallery, overlook, and current program context.
- [Purdue CLA, University Hall renovation and preservation (September 3, 2025)](https://cla.purdue.edu/news/college/2025/university-hall-renovation-and-preservation.html) — preservation/restoration context and current use.
- [Purdue Board of Trustees, University Hall and Related Renovations (September 28, 2022 PDF)](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf) — pre-completion project scope and proposed floor plans; used as planning context, not proof of as-built details.
- [Purdue BuildingShapesZip4 GIS feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — campus-map polygon record FID 213 / UNIV, with an explicit non-survey limitation.

This review only added independent audit files in `audit/university_hall_refine/`. It did not modify the Blender asset, master blend, shared manifest, or Git history.
