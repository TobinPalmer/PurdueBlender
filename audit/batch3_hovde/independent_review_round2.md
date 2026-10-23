# Hovde Hall — independent review, round 2

**Score: 6.4/10. Does not reach 9/10.** Round 2 makes visible progress on the entry silhouette and glazing, and the model now contains named enclosed office and boardroom shells with furniture. It is still a stylized massing study rather than a source-faithful finished building. The roof/penthouse reads as an oversized blank rooftop block, the interiors remain oversized sparse rooms, and the preview is too pale to judge the actual brick and limestone materials confidently.

## What I checked

- Reopened `modular/buildings/hovde_hall.blend` in Blender 5.2.3, inspected its export collection and transforms, and checked the saved round 2 exterior, presidential office, and trustees' boardroom renders.
- Confirmed the file contains scene `Building_hovde_hall`, collection `Asset_hovde_hall`, 702 exported objects / 690 meshes, assigned materials on all meshes, and unit scale on `HOVD_Root`. The root's authored location and rotation remain the same as in round 1. No current master footprint overlay was included, so I cannot certify the final campus placement.
- Read the round 1 independent review, round 2 change notes, and asset-check JSON.
- Compared the modeled silhouette to the dated geotagged [2016 Hovde exterior photo](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg) and Purdue's [visitor-guide image description](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf), which identifies the front as a classical building with columns and pediment. The photo supports the central columned portico and brick wings. The current captured frontal image remains too flat/front-on and overexposed to compare fine facade details; the cited sources are perspective photos, not dimensioned drawings.

## Round 1 findings that improved

- **Portico:** a triangular pediment now reads clearly, and six columns are visible with bases/capitals. This directly addresses the former box-like entrance and narrow poles. The feature remains a simplified overlay: the front view shows the entry columns crowding the entrance/window zone, and the rendered stone is nearly white with little relief.
- **Windows:** blue-gray glazing makes the repeated openings legible from the front. Frames, muntins, and depth remain minimal, so the windows read as dark flat rectangles.
- **Room enclosure:** both cutaways now have wall segments, door leaves/gaps, floor/ceiling geometry, and furnishings. The earlier single slab plus furniture issue is partially addressed.
- **Roof color:** the roof is no longer charcoal, and tile-course hints were added. The rendered rooftop still does not read as a convincing sloped red-tile roof.

## Prioritized remaining work

1. **Correct the roof and penthouse silhouette.** The front render's largest rooftop feature is a blank, pale, flat-sided box that dominates the building. The saved geometry confirms a 12 × 24 × 2.5 m `HOVD_Penthouse` above a 21.4 × 70.8 m roof slab, with the whole building reaching 19.25 m. The roof is still a flat slab with thin tile hints. Compare the rooftop silhouette against a current overhead/photo reference or an authoritative roof plan; then resize/shape or omit unsupported rooftop mass and model the visible roof plane and edge. The sources currently cited establish a campus material context, not Hovde's exact roof form.
2. **Make the interior footprints credible and complete.** Each room floor is 19 × 18 m (342 m²) and the views still show large empty expanses surrounding a small office setup or narrow board table. That is far more space than the depicted use appears to need. Find a Hovde plan or use a clearly labeled, conservative room footprint; add circulation and meaningful room-scale furnishings, wall openings/windows, and full-height partition continuity. Keep the furnishings explicitly interpretive without source plans. The round 2 camera hides the ceiling/walls for clarity, which is acceptable as a cutaway, but a second intact-room view would help verify enclosure.
3. **Improve material/readability and portico integration.** The overall image is severely washed out: stone, window trim, stairs, and portico merge into a bright white mass; brick appears pink and noisy. Set a less blown-out exposure/lighting, strengthen material value separation, and review close-up facade details. Ensure the portico is integrated to the actual facade plane, with the six column bases aligned to the stair and entry, rather than reading as a thin decorative front layer. Add restrained, source-supported stone course/cornice depth and window frames.
4. **Check placement in context.** Preserve the asset's root and the manifest marker. Generate a fresh building-to-GIS footprint overlay and neighborhood render from the saved asset after building-side edits; current evidence does not verify the final footprint/orientation or façade entry position in the master.
5. **Verify texture in a neutral review render.** The material assignments are complete, but the dramatic pale render and screen-space noise make it hard to judge the brick course scale or roof tiling. Include a neutral, exposure-controlled close-up and wide three-quarter view; make sure tile courses are geometry/material relief at building scale rather than visible broad rectangular patch hints.

## Rating summary

| Area | Assessment |
|---|---|
| Identity and broad massing | Recognizable four-story brick administration hall; front composition improved. |
| Portico | Pediment and six columns now present; proportions/integration and lighting still need work. |
| Roof | Red-tinted surface added, but blank rooftop penthouse and flat slab dominate and lack source verification. |
| Windows/materials | Glazing cues exist; facades remain overexposed and details too flat to assess accurately. |
| Interior | Enclosed room shells exist, but 19 × 18 m footprints are oversized and contents too sparse. |
| Geometry/placement | Root scale and authored transforms check; no fresh GIS/master overlay to certify context. |
| File integrity | Saved file reopened; expected scene/collection and material assignments are present. |

**Decision:** do not mark complete and do not claim 9/10. Address the roof/penthouse and room scale first, then have another independent reviewer check the source comparison, facade integration, and master placement.
