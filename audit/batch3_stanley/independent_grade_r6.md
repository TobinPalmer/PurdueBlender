# Independent grade — Stanley Coulter Hall R6

**Result: 8.1/10 — meets the 8.0/10 pass threshold.**  
**Asset SHA-256:** `ecc5c02b4eac97d2afee19602e790b86d84f41b3fe78222b17f75f43e70cc61e`  
**Independent reopen:** Blender 5.2.3; 760 objects / 750 meshes in the exported collection; identity root; 24 used materials; no materialless meshes, invalid material slots, external file-backed image textures, or missing images. The independently reopened SHA matches the supplied R6 asset.

R6 improves the three issues that kept R5 at 7.8: it groups the upper east openings toward Purdue’s reference photo, closes the two unsupported view-through wall gaps, and adds a connected, explicitly schematic entry-to-stair route. The entrance and facade now read closer to the current Purdue CLA photo. This is a modest pass, not a claim of fully verified architecture: the upper blue bands still sit in front of a solid brick wall instead of true openings, the entrance remains simplified, the roof is broad and visually plain, the interior remains a diagram, and the master placement marker was not checked in this asset-only review.

## Scorecard

| Criterion | Score | Findings |
|---|---:|---|
| Identity and GIS footprint | 1.9/2.0 | The unchanged foundation perimeter matches Purdue ArcGIS BuildingShapesZip4 FID 56 with IoU 0.999999899, symmetric difference 0.000286 m², and Hausdorff distance 0.0000045 m in the project’s approximate local-meter frame. This validates the campus-map outline, not surveyed wall lines or survey-grade registration. |
| Placement, orientation, and scale | 1.6/2.0 | Independent reopen confirms the expected library and identity root. The asset report retains its established placement origin. I did not open the campus master or verify `Placement_stanley_coulter_hall`; campus placement and adjacent-courtyard alignment remain unverified. |
| Floors, height, and roof form | 1.35/2.0 | The three-story mass and low hipped roof remain plausible. The R6 roof shader adds slight course variation, but the hero view still shows a large, nearly uninterrupted roof surface. No current measured roof profile or height evidence was provided; the 15.87 m all-geometry top is not a surveyed height. |
| Facade, entrance, and materials | 1.6/2.0 | The upper east glazing grouping, brick infill beside the stone portal, and slimmer entrance entablature improve the photo match. The render still has a long, nearly continuous blue band; the source photo shows grouped openings with stronger brick breaks. The blue glass is overlaid on the solid brick wall, so it does not provide actual window recesses or interior depth. The entry portal, paired supports, door/transom, stairs, and rails are legible but remain simplified relative to the photo. Procedural brick, limestone, bronze, and glass are consistently assigned and portable. |
| Interior, saved asset, evidence, and portability | 1.65/2.0 | The new corridor floor/walls overlap the door threshold, landing, and stair by documented small amounts, creating a connected schematic path. The render labels it unverified. It remains a single top-down diagram without verified room partitions, full circulation/core, or floor-to-floor context. Exact saved asset integrity and material coverage pass independent reopen. |
| **Total** | **8.1/10** | **Passes the 8.0/10 threshold.** |

## R6 change assessment

- **Grouped upper glazing:** the new ribbons better reflect the broad grouping visible in Purdue’s CLA photo, and the render no longer reads as the R5 uniform narrow-window grid. The band is visually more continuous than the photo and is not cut into the brick shell; this remains an interpreted facade surface, not verified fenestration geometry.
- **Entry infill and portal:** the two gray gaps are now brick, the portal cap is slimmer, and the image reads more like an entrance with a transom, paired supports, steps, and rails. Exact recess depth and stone dimensions remain fitted from an undimensioned photograph.
- **Interior route:** the entry, lobby/Grad Hub, and staircase are connected in the schematic. The plan explicitly says its room layout is unverified, which is appropriate given the historical plans and lack of a current as-built floor plan.
- **Roof:** the material variation is subtle and not enough to resolve the prior concern that the roof reads as an almost plain slab. Its profile, construction, and elevation remain unverified.
- **Technical integrity:** independent reopen confirmed the exact hash, object counts, identity root, used-material coverage, and no external image dependencies. The 52 unverified roof-option objects, 33 superseded window objects, and 4 unsupported entry fixture objects are preserved in hidden recovery collections outside the exported asset collection.

## Evidence and limits

- Current facade reference: Purdue College of Liberal Arts, [Stanley Coulter Hall photo](https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg), retrieved 2026-10-25. The photo is undated, undimensioned, and covers only part of the building.
- Interior context: Purdue Board of Trustees, [University Hall related renovations](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf), dated 2022-09-28, pages 11–13. These are historical plans; they do not establish current as-built room circulation or finishes.
- Footprint: Purdue ArcGIS BuildingShapesZip4, feature 56, snapshot dated 2026-10-22. The project conversion uses an approximate local-meter frame and is not a certified survey.
- Historic roof context: Purdue Archives record PPBUC01117 is undated and does not establish current roof construction.
- I inspected `SC_hero_r6.png`, `SC_entry_r6.png`, `SC_interior_circulation_r6.png`, `SC_footprint_overlay_r3.png`, and the local CLA source photo. This review did not open the campus master, so the placement marker and assembled neighborhood still need coordinator verification before integration.

## Remaining refinements (non-blocking for this grade)

1. Coordinator should verify the master placement marker and adjacent streets/courtyard before or during integration.
2. If additional facade work is done, cut real grouped openings into the brick mesh instead of placing blue glazing over opaque brick, and match the photo’s stronger masonry breaks.
3. Add supported eave/roof detail only when current photo or plan evidence is available; do not infer a surveyed roof profile from the historic photograph.
4. Treat the interior corridor as schematic until current room/core plans are available.

**Asset modified by grader:** no.  
**Master/shared files modified:** no.  
**Commit created:** no.
