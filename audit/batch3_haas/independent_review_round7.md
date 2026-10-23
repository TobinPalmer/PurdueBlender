# Felix Haas Hall — independent review round 7

**Reviewed:** `modular/buildings/felix_haas_hall.blend`, reopened in Blender 5.2.3 on 2026-10-23. I checked the reopened asset's collection and saved counts/bounds, round-seven changes and continuity evidence, exterior and entrance renders, all four elevation renders, and first-floor plan view. Export collection `Asset_felix_haas_hall` reopens with 1,056 direct objects. The recorded envelope remains `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m; roof transform is unchanged. The report confirms 26 inlay faces, 17 entrance treads, and removal of the 47 inferred room doors.

## Score: 7.2/10 — below 9/10

Round seven improves the entry wall's construction logic: the limestone surface now replaces seven front-facing GIS polygons instead of floating in front of them, and the unsupported room doors were removed. The overall building still does not match its defining reference facade. The bright limestone treatment covers only the central entrance bay, while the long flanking wings remain dark brick fields with conspicuous pale grid trim. In Purdue's exterior photo, the principal face reads as a more continuous Bedford-limestone composition with red-brick panels and surrounds integrated across the facade. The present render still reads as a brick gym with a pale entry insert.

| Area | Score | Findings |
|---|---:|---|
| Massing and roof | 7/10 | The large hipped roof, lower entry projection, and campus envelope are recognizable. Roof pitch/profile and tile scale are still estimates. Faceted lighting/color variation makes roof planes look uneven. |
| East/front facade and entrance | 6.5/10 | The front limestone geometry is now integrated at the shell plane, a real improvement. It stops at the entrance projection, leaving both large adjacent front wings in red brick with white rectangular grids. The central bay itself is pale, but the inlay rings and window surrounds remain shallow graphic borders rather than convincing inset masonry. |
| Other elevations | 6/10 | Four views make the sides reviewable. Long sides have a repeated window/arch-and-pier rhythm, but the pale trim is oversized and repetitive. North/south views show roof masses and a small side projection whose silhouette/details are not substantiated by the available reference. There is a stray thin blue mark on one side render. |
| Materials and texturing | 6.5/10 | The roof reads as red tile and the stone/brick are distinguishable. Brick fields are too uniformly dark; the near-white stone/trim appears cool under this lighting; no visible coursing differentiates the new 26-face inlay from flat red strips. Improve texture/color at neutral daylight and camera scale. |
| Interior representation | 6.5/10 | The plan diagram contains identifiable room labels, partitions, stairs, furniture, and an explicit note that sizes and door positions are schematic/unavailable. Removing guessed door leaves was the correct evidence-driven correction. It remains a conceptual, nondimensional first-floor visualization rather than a verified interior model; upper levels and circulation are not verified. |
| GIS fit and file integrity | 8.5/10 | Reopen and continuity evidence show the export collection, envelope bounds, unchanged roof transform, and entry treads. These are continuity checks, not independent survey validation of height or architectural dimensions. |
| Evidence and uncertainty | 8/10 | Evidence appropriately distinguishes photo-derived qualitative facade from measured geometry, identifies the plan as nondimensional, and records that the GIS cannot validate roof/facade/interior details. |

## Priority fixes

1. **Carry the limestone and brick-inlay composition across the complete principal facade.** Continue the photo-derived wall treatment to the adjoining front wings and align its boundaries with the actual wall mesh. Use brick panels/bands within the stone composition, rather than leaving large red fields framed by bright grids. Keep any inferred extent labeled as an estimate if the photo perspective cannot settle exact dimensions.
2. **Make the entry masonry read as built into the wall.** Give brick inlays credible depth, jambs, lintels, and visible coursing; tune the stone response warmer and less stark. Verify the facade in neutral daylight and in both close and full-building views.
3. **Refine material consistency and roof presentation.** Reduce the near-white high-contrast trim and uniform dark brick. Reduce roof plane shading variation if it is lighting/material artifact, and document roof profile as estimated until a reliable elevation or oblique reference is found.
4. **Clean and validate side elevations.** Investigate the stray blue mark and the thin white projection visible at the ends of north/south renders; either establish their source or remove them. Avoid treating estimated window schedules as verified.
5. **Keep the interior evidence honest.** Retain the schematic warning. Add no door locations/swings without dimensioned evidence; the saved first-floor plan does not establish them.

## Evidence reviewed and limits

- Purdue Events' [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall) exterior photograph supports the qualitative pale stone/red-brick composition, arched lower openings, central entry, stairs, and roof form. Its perspective does not establish measured facade widths or exact inlay extents.
- Purdue CS's [HAAS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports room names and broad adjacency; it is nondimensional and does not establish room metrics, door positions, widths, or swings.
- Reopen and continuity evidence report the current collection count, unchanged GIS envelope/origin and roof transform, 26 inlay faces, 17 entry treads, and no exported cupola. These do not prove survey accuracy.

**9/10 decision: No.** The wall-skin integration and removal of unsupported doors are sound corrections, but the primary facade is still compositionally incomplete and the inlay/material treatment remains schematic.
