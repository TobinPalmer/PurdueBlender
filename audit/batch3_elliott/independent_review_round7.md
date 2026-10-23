# Elliott Hall of Music — independent review round 7

**Score: 6.4/10. This revision is below 9/10.** The round 7 additions respond to identifiable source descriptions, and the saved asset reopens, but key visual and functional details remain estimated or unresolved.

## Review performed

Reopened `modular/buildings/elliott_hall_of_music.blend` in Blender 5.2.3 LTS with the round 7 reopen check. `Asset_elliott_hall_of_music` contains 126 mesh objects (128 total collection objects); 48 object names carry the round 7 prefix. No `TEMP_R7_` objects remain. The same file inventory contains no Hovde instance. The temporary review context therefore did not persist into Elliott's saved asset.

Inspected the round 7 exterior elevation, canopy close-up, linked Elliott/Hovde context, auditorium cutaway and seating plan renders, along with the round 7 handoff, change notes, and result record.

## What improved

- The two groups of three figures reflect SAH Archipedia's written description of two groups of allegorical sculptures. Six small figures are visible at the modeled perimeter. Their scale, poses and exact positions remain illustrative.
- The curved canopy is visible at the upper connector interface and adds the source-described canopy feature. Its broad, pale curved surface reads as an architectural canopy, but the close-up shows its support and wall tie-in are unresolved: it sits across a broad slab/connector and intersects the facade composition without a clear entrance or portal.
- Horizontal limestone bands, vertical pilaster-like trim, and roof tiling give the building a recognizable brick-and-stone vocabulary. The interior cutaway now reads as a large auditorium with multiple seating levels, aisles, stage drape, balcony fronts, and lighting elements.
- The Hovde context render makes the intended relationship visible without saving Hovde data into the Elliott library.

## Prioritized issues

1. **Resolve exterior openings and facade hierarchy.** The principal elevation remains a large, nearly uninterrupted red-brown wall. Window bays, glazing, and entry composition are not legible in the overall render. Although a glass material exists in the file, the rendered exterior does not establish a convincing window schedule or clear windows through the masonry. Purdue's anniversary material was not inspected at pixel level, so the schedule needs reliable visual references before it is modeled as verified.
2. **Finish the connector portal and route as one joint review.** The context view shows the gray/teal connector reaching into Hovde's side wall, while no clearly open portal or continuous circulation route is visible. The Elliott-side approach still does not establish the documented second-floor connection. The entrance canopy, bridge, landing, and Hovde opening need one source-checked geometry decision; accessibility cannot be credited from the current renders.
3. **Clarify the entrance and canopy attachment.** In the close-up the curved canopy appears to land on the connector slab, while the facade has no clearly framed doorway beneath it. The handoff correctly calls profile, location, span, and dimensions unverified. Better placement and a readable door/threshold/landing are needed before accepting it as a faithful entrance detail.
4. **Make the auditorium cutaway structurally readable.** The cutaway communicates seating and tiers, but its large opaque roof and side slabs obscure the auditorium, and the seating plan is an unscaled schematic. Seat counts, aisle widths, balcony elevations, stage dimensions, and accessible seating/egress are not verified. Label it as a concept view or improve the cutaway framing and corroborate geometry with a dimensioned source.
5. **Improve material evidence and detail.** The current close views show mostly smooth, flat brick and stone colors; tile relief is clearer on the roof than brick bond or masonry texture on the walls. The mesh material inventory contains brick, limestone, glass, roof, and seating materials, but material names alone do not demonstrate convincing mapped surface texture. Refine scale and surface variation while keeping the red-brick and Indiana-limestone palette tied to the source.
6. **Verify sculpture and flytower treatment.** Source descriptions support the feature types, but the small figures, their placement and the simplified flytower trim remain estimates. The figures are difficult to read at the overall building scale; use source photographs or archive drawings to validate their silhouette and relation to entrances.

## Source and confidence notes

- [SAH Archipedia: Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) supports red brick, Indiana limestone banding/pilasters, a curving canopy, a flytower, and two groups of three allegorical figures. It does not support the modeled dimensions or exact placements.
- [Purdue Convocations accessibility guidance](https://convocations.purdue.edu/accessibility/) identifies north and south accessible entrances and step-free access guidance. The current model does not verify clear widths, thresholds, landing dimensions, approach slopes, or route continuity.
- [Purdue Convocations directions](https://convocations.purdue.edu/clubconvos/) describes an approach via Hovde's second floor. The exact shared portal geometry remains unresolved in the current joint view.
- The stated footprint basis is Purdue BuildingShapes Feature 617. This review did not independently remeasure the shell or establish its height.

**Disposition:** useful progress, but do not mark Elliott complete or 9/10. Prioritize a source-backed fenestration/entrance pass and a joint Elliott–Hovde portal/route review, then reassess the interior against a dimensioned plan.
