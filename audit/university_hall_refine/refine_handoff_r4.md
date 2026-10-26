# University Hall refinement handoff — revision 4

**Asset:** `modular/buildings/university_hall.blend`  
**SHA-256:** `227d6163491da17cb4ec9a34155951b62c921089d5d0e383e01c5e50614fbeef`  
**Fresh reopen:** Blender 5.2.3 LTS, passed. The asset opens as `Building_university_hall` and exports all 1,003 objects in `Asset_university_hall`. It has 990 meshes, one curve, 11 lights, no materialless meshes, no invalid material slots, no missing external images, and no linked libraries. Report: [independent_reopen_r4.json](independent_reopen_r4.json).

## Work completed

- Replaced the large rectangular roof block with four constructed, pitched mansard planes, limestone eaves, a defined upper deck, and ten small brick dormers with glazing, stone surrounds, and pitched caps.
- Added procedural slate color variation and relief, plus additional subtle surface relief on existing brick. Kept the texture self-contained in Blender materials.
- Reworked the tower crown: added the hipped slate bell-stage cap, an octagonal copper lantern and steeper spire, gold finial, louvers, and clock faces at each cardinal face. Total crown height remains at the source model's previous 27.7 m ceiling.
- Added limestone arched window moulds to the long elevations and nine illustrative sash openings on each short elevation, with mullions, jambs, sills, headers, and keystones.
- Replaced the broad first- and second-floor plates with gallery rings. The openings are 7.6 × 12.0 m and 6.6 × 10.8 m respectively. Added gallery book bays and feature wall, an upper overlook guard, cast-iron column representations, and two stair flights with landings and handrails.
- Preserved `AssetRoot_university_hall` location `(0,0,0)`, rotation `(0,0,0)`, and scale `(1,1,1)`. The modeled main wall footprint was left at its current coordinates and dimensions; roof eaves intentionally project beyond the wall line.

## Renders

- [Oblique exterior](oblique_southwest_r2.png)
- [East elevation](east_elevation_r2.png)
- [Interior shell cutaway](interior_cutaway_r2.png)

These are temporary neutral daylight review renders. Cameras, fill lights and the ground plane were removed from the session and were not saved into the asset.

## Evidence and uncertainty

Research retrieved 2026-10-25. Purdue's 2025 restoration story identifies the renovated building as a student-centered hub and documents the revived two-story central gallery, recovered columns, roof trusses, and the restoration approach: [Purdue Stories, 2025-06-30](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/). The official rededication account describes the completed two-story gallery, second-floor academy overlook, collaboration spaces, and classrooms: [Purdue CLA, 2025-10-25](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html). Current campus imagery used for the steeple, trim, and roof silhouette includes [Purdue CLA's University Hall steeple photo](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) and the [Purdue Stories 2025 exterior photo](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg). The Board of Trustees packet has proposed renovation floor plans dated 2022-09-28, before completion; it was used only as planning/program context, not represented as an as-built survey: [University Hall and Related Renovations PDF](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf).

The GIS record previously cited in `independent_grade.md` is BuildingShapesZip4 FID 213. It supplied bounds screening only (AABB overlap IoU 0.9617, center difference 0.391 m); it did not verify the true perimeter, orientation, elevation, or roof. The original main shell outline, local frame, and manifest placement have been preserved. No new GIS fit was claimed.

The roof's upper plan dimensions and roof pitch were proportioned to the existing shell and Purdue's exterior imagery; they are not archival or field measurements. Dormer count and exact spacing are visually estimated. The 7.6 × 12.0 m / 6.6 × 10.8 m gallery openings are a schematic interpretation of the documented two-story gallery and overlook, not dimensions measured from the 2022 plan sheet or current as-built drawings. Window counts and short-elevation fenestration are reconstructed from visual comparison and remain unverified against an elevation drawing. Cast-iron column positions are representative; Purdue reports five recovered columns, but the public description only assigns broad floor/stair locations. No changes were made to the master blend, shared manifest, README, or Git history.

## Grading status

The prior 4.3/10 grade belongs to asset SHA `7b105421…bb22` and is not a grade of this revision. Independent review of this SHA is still required. The new visual/evidence package is ready for that review; no score is claimed here.
