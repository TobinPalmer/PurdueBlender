# Independent grade: University Hall

**Result: 4.3/10 — does not pass the 8.0/10 threshold.**

## Saved asset and reopen check

I freshly reopened `modular/buildings/university_hall.blend` in Blender 5.2.3 LTS. The inspected file SHA-256 is `7b1054212e66d8fb56155e735a90b26dab915e0bfaf8e3655a0e1d8a8536bb22`. It contains scene `Building_university_hall`, collection `Asset_university_hall`, 507 objects (495 meshes), and the expected `AssetRoot_university_hall` identity transform. The exported collection contains all 507 objects. There are 18 used materials; meshes have material assignments; no missing external images or linked libraries were found. There are no camera objects or active scene camera in this source library. The exact reopen inventory is in [independent_reopen.json](independent_reopen.json).

The model is portable as a standalone collection, but a valid Blender file and numerous objects do not establish architectural accuracy. I generated temporary neutral inspection views without saving changes to the asset. See [oblique](oblique_southwest.png), [east elevation](east_elevation.png), [south elevation](south_elevation.png), [roof plan](roof_plan.png) and [interior cutaway](interior_cutaway.png).

## Visual comparison

Purdue's current University Hall material describes a restored historic hall and shows its recognizable red-brick Victorian form: multiple occupied levels, a steep slate mansard roof with dormers, prominent central tower and steeple/cupola, and detailed pale stone/painted trim around openings and roofline. Purdue's renovation account also describes a two-story central gallery/atrium and the reintroduction of historic columns. The current saved model does not reproduce those defining elements: its main mass is a simple rectangular box with repetitive dark rectangular windows, broad flat roof, and a small square open frame on top. The large flat roof plane dominates every exterior view, while the roof pitch, mansard profile, dormers, and central tower/steeple are absent or substantially wrong. Exterior articulation and entrance treatment are minimal.

There is some useful work in the asset: brick-like procedural material, pale horizontal trim, many openings, and separately named interior and roof elements. But the procedural brick is not enough to bridge the silhouette and detailing gap. The rendered walls and roof remain visually flat, and there are no image-texture nodes. In the cutaway, the interior mostly reads as blank slabs/open spans with a few small pieces; it does not communicate the central gallery, stairs, columns, or useful room/circulation arrangement expected from Purdue's current renovation descriptions and floor-plan material.

The project GIS screening record for Purdue BuildingShapesZip4 FID 213 reports AABB overlap IoU 0.9617 and center difference 0.391 m. It also explicitly flags the result as bounds screening only and leaves orientation, plan dimensions, height, and shell verification unresolved. The existing master placement check reports the University Hall placement marker exactly matching its manifest transform (0.0 m marker error, identity rotation/scale, 507 exported objects). This supports the marker wiring, but it is not an independent survey-grade confirmation of the building walls against GIS. I therefore give placement/footprint screening partial credit, not a full accuracy pass.

## Scores

| Category | Score | Basis |
|---|---:|---|
| Campus placement and GIS footprint screening | 7.0/10 | Marker matches manifest; prior GIS AABB screening is close, but exact outline/orientation and true wall fit remain unverified. |
| Architectural form and silhouette | 2.5/10 | Box-like mass, wrong roof profile, and missing defining historic form. |
| Facade detail and fenestration | 3.0/10 | Brick, trim and openings exist, but window rhythm and ornament are generic and repetitive. |
| Roof and tower fidelity | 1.5/10 | Large flat roof; reference mansard/dormers and prominent tower/steeple are not represented. |
| Materials and textures | 4.0/10 | Assigned procedural materials, including brick, but no image textures and limited visual depth/variation. |
| Interior completeness and accuracy | 1.5/10 | A few slabs and sparse props; no legible central gallery or circulation system in the cutaway. |
| Asset integrity and portability | 8.5/10 | Fresh reopen succeeds; collection, root, materials and dependencies are sound; no camera is provided. |

The category-weighted overall score is **4.3/10**. Full scoring/evidence is serialized in [independent_grade.json](independent_grade.json).

## Highest-priority rework

1. Rebuild the roof massing as a steep mansard/slate roof with correctly scaled dormers, cornice/eaves, and the central tower/steeple/cupola.
2. Reshape the main mass and elevations to match current exterior photos and verify orientation and true perimeter against the official GIS outline, not only its AABB.
3. Add the missing facade hierarchy: pale stone/painted surrounds and lintels, sills, brackets, cornices, and a recognizable entrance.
4. Build a readable renovated interior with the central two-story gallery/atrium, stairs, columns, floors, and representative rooms/collaboration spaces.
5. Improve brick, stone, and slate material variation/relief and review the result in daylight.

## Reference sources

- [Purdue Stories: Restoring Purdue's University Hall as a campus crown jewel](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/) — 2025 current renovation story, photographs and discussion of the restored gallery and historic features.
- [Purdue College of Liberal Arts: University Hall rededication](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html) — current renovated use and central gallery/overlook context.
- [Purdue Board of Trustees: University Hall and Related Renovations (PDF)](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf) — proposed floor-plan sheets and renovation scope; use the current 2025 sources for present-day status.

This is a read-only grade. No asset, master scene, manifest, README, or shared project file was changed, and nothing was committed.
