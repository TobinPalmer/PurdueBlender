# Felix Haas Hall — independent review

**Asset inspected:** `modular/buildings/felix_haas_hall.blend`, reopened render set and `reopen_check.json` dated 2026-10-23.  
**Overall score: 5.8/10.** This is a useful first-floor and exterior blockout with a strong entry concept, but it does **not** meet the requested 9/10 bar.

## Category scores

| Area | Score | Review |
|---|---:|---|
| Building form and architectural detail | 5.5/10 | The long GIS footprint, central limestone entry bay, brick flanks, arched lower windows, and hipped roof read as Haas Hall. The rendered side elevations remain broad, dark, nearly blank walls with several plain window-colored panels; the photographed façade has more continuous stonework and a richer brick-and-stone pattern. The roof/cupola silhouette is not supported by measured elevation evidence. |
| Materials and textures | 5/10 | The material families distinguish brick, pale stone, glass, and red roofing, but the renders show brick that is much too dark and noisy, stone that reads as flat blue-gray, and roof tiles that read as bright salmon. The result does not match the warm pale limestone, red-brown masonry, and darker red roof in the available Purdue exterior photo (`exterior_reference.jpg`). |
| Windows and roof | 4.5/10 | The front openings are legible, including upper rectangular windows and lower arches. Other elevations and much of the building perimeter lack verified window treatment. Roof planes are present and cleanly separate from the GIS wall shell, but the circular drum, dome, and tall spire are image-based/uncorroborated in the reviewed reference set; the source renders make this feature prominent. |
| Main entrance and stairs | 5/10 | The centered double door, approach, arch, and broad stair make the entry recognizable. The model has 10 treads. Purdue’s own historical timeline says the entrance has 17 steps, one for each person commemorated by the gymnasium, so this needs correction. The current tall blank side blocks obscure parts of the lower façade and do not resemble the lower stone sidewalls/railing in the photo. |
| First-floor rooms and circulation | 6.5/10 | The cutaway has a perimeter of small offices, larger interior rooms, furniture, and visible stair cores. This is a plausible schematic. Against the 2016 Purdue CS first-floor plan, it still needs a labeled room-by-room check: the plan identifies three stairs, an elevator, restrooms, two conference rooms, a student organization room, and distinct office groups. The render does not make the full three-stair arrangement or those room identities easy to verify. No upper-floor plan was verified. |
| Scale and placement | 8/10 | The GIS wall envelope stays at the cached official polygon bounds, local shell scale is 1 and rotation is 0, and the stored manifest origin is consistent with that local envelope. This supports the campus placement. Roof/elevation dimensions and first-floor furniture registration remain estimates; the cupola/spire reaches 18.7 m in the reopened mesh, while the documented roof ridge is 14 m. |
| File and integration hygiene | 7/10 | The asset reopens, keeps `Asset_felix_haas_hall`, preserves the GIS shell, and puts superseded parts in a hidden recovery archive. The asset now has 687 direct export objects, while `modular/manifest.json` still records 340 and omits the new object list/bounds. The master needs its manifest refreshed before this asset is treated as integrated. |

## Evidence and specific fixes

1. **Rebuild the entry stair to 17 risers/treads.** The current saved asset has only `HAAS_Photo_Entry_Stair_Tread_0` through `_9`. Purdue’s [campus history timeline](https://collections.lib.purdue.edu/timelines/puhistorical) identifies 17 entrance steps. Preserve the threshold height by recalculating riser height and landing geometry; do not simply add seven overlapping slabs.
2. **Tune material values against the exterior photo.** Darken and warm the roof toward red-brown, lighten and reduce contrast/noise in the brick, and use warm limestone rather than the cool blue-gray finish visible in the final renders. Add visible masonry/block coursing to the stone where it appears in the source.
3. **Remove the entrance-side obstruction.** Replace the tall blank blocks in front of the lower façade with short stone cheeks/rails that preserve the two arched lower windows and match the photo’s step-side treatment.
4. **Finish the other elevations.** Add/verify window openings and trim on all sides using photo or archival evidence. In the final overall render, large areas of the long sides are unbroken dark walls with simple pale rectangles, which lowers the building’s recognizability from campus views.
5. **Resolve the cupola/spire from an overhead or archival reference.** It is the highest silhouette feature at 18.7 m and dominates the current exterior render, but the reviewed ground-level Purdue photo and first-floor plan cannot verify its shape or height. Keep it marked estimated until aerial/archival evidence supports it.
6. **Check stairs, elevator, and room adjacency against the published plan.** The [Purdue CS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) is useful for adjacency and named rooms, though it has no scale. Record which modeled stair corresponds to each of the three plan locations and show the elevator/restrooms/conference rooms/student organization room clearly.
7. **Refresh master metadata at integration.** Update manifest count from 340 to 687 and regenerate object names and bounds from the saved asset. The existing `reopen_check.json` verifies reopen/collection and selected shell/roof transforms, not the master link or exact exterior accuracy.

## References and limits

- Local Purdue Events exterior reference: `audit/batch3_haas/exterior_reference.jpg` (qualitative shape/material reference, no surveyed dimensions).
- Owner’s cited [Google Maps listing/photo gallery](https://www.google.com/maps/search/Felix+Haas+Hall+Purdue) is a user-contributed reference; dates and camera geometry cannot establish measured elevations. The Maps gallery did not render during this independent review, so I did not use it to resolve the cupola or side elevations.
- Purdue CS [first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf), authored/created in 2016 according to the owner’s source record; supports first-floor adjacency only.
- Purdue [campus history timeline](https://collections.lib.purdue.edu/timelines/puhistorical); authoritative source for the 17 memorial entrance steps.

This score is a visual/source-evidence review, not a claim of certified survey accuracy. **The asset is not 9/10.**
