# Hovde Hall — independent review, round 5

**Score: 7.1/10. Does not meet the 9/10 target.** Reopened the saved `modular/buildings/hovde_hall.blend` and inspected the round 5 exterior, portico close-up, presidential office, and trustees boardroom renders. The long red-brick administration block is recognizable and the narrowed pediment is a modest improvement, but the entrance still reads as a shallow decorative overlay that hides the central facade. The room renders communicate furnishing layouts, but they do not yet demonstrate convincing enclosed interiors. Roof form and master placement remain unverified.

## Evidence inspected

- `exterior_round5c.png`
- `portico_detail_round5c.png`
- `presidential_office_round5c.png`
- `trustees_boardroom_round5c.png`
- `final_asset_check.json` and `final_check_round5.log`
- Prior independent review `independent_review_round4.md`

The final check records the `Asset_hovde_hall` collection with 727 objects (715 meshes), no mesh lacking a material slot, and `HOVD_Root` at `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, unit scale. This establishes a successful reopen and the library object's transform; it does not establish correctness of the master placement or shader appearance.

## Reference comparison

Purdue Archives describes the historic Hovde building as a four-story, 70-by-230-foot administration building that included offices and a Board of Trustees room. This makes the long four-story mass and the presence of administrative/board spaces reasonable targets, though it does not verify current room layouts. [Purdue Archives building record](https://archives.lib.purdue.edu/agents/corporate_entities/573)

The dated [2016 exterior photographs](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg) and [Purdue visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf) support the red-brick wings, prominent central classical entrance, and broad stair approach. These are perspective references and do not supply measured portico or roof dimensions. Purdue Archives also catalogs a circa-1937 campus photograph that includes Hovde, but the record alone does not expose a measured elevation. [Purdue Archives circa-1937 photo record](https://archives.lib.purdue.edu/repositories/2/archival_objects/47390)

## Findings and ranked corrections

1. **Resolve the portico-to-facade connection.** The close-up shows a recognizable pediment and six supports, and the reduced footprint improves hierarchy versus round 4. The broad limestone panel and vertical stone strips still obscure multiple central window bays and the actual entry. The shafts read as narrow flat strips rather than clearly round, recessed supports; the entry door/opening is not legible. Rebuild the portico as a structure with visible depth, bases/capitals, a readable entrance behind it, and a clean transition into the stair landing. Keep dimensions labeled estimated unless an elevation is found.
2. **Make facade openings read as openings.** The windows remain dark, flat blue-gray rectangles on a continuous brick plane; visible jamb depth and frames are weak. The center bays are especially interrupted by the portico. Add clear recesses, lintels/sills, and frames while preserving the regular rhythm visible in the reference photos. Brick and pale horizontal courses are present, but the close view still reads as a repetitive texture with limited relief.
3. **Improve the room cutaways and show enclosure.** The office image is a top-down layout with a large floor field, central desk, sparse seating, and a sofa at the perimeter; the boardroom shows a plausible long table and chairs but similarly floats as a furnishing diagram. Since Purdue Archives supports historic office and Board-room uses but no verified plan was supplied, retain the schematic label. Add legible wall thickness, door openings, windows, circulation, and human-scale context; render a cutaway or oblique interior view that demonstrates enclosed usable rooms. The current top-down views are useful plan evidence but not proof of interior architectural detail.
4. **Verify or simplify the roof.** The full view shows a broad, nearly flat dark red-brown roof plane and a small centered raised box. The cited exterior views do not verify this roof profile, cap, or finish. Keep the silhouette restrained until overhead imagery or archival drawings support additional form; document the roof material as estimated. The material-slot check confirms assignment only.
5. **Complete the placement check during master integration.** The asset root is unchanged, and the round 5 packet has no current master/GIS overlay. Compare the structural wall footprint and facade orientation with official Purdue GIS FID 618 and inspect neighboring buildings in the linked master before accepting placement. Exclude decorative steps and portico projections from the structural-wall comparison.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and massing | Recognizable long, four-story red-brick administration block; no current measured survey comparison. |
| Portico and entry | Pediment and six-support intent are clear; the shallow overlay still blocks facade and entry, and support depth is weak. |
| Facade and materials | Brick, stone bands, and window rhythm exist; glazing is flat, window recesses are not clear, and material slots do not validate shader fidelity. |
| Roof | Broad low plane with a small cap; profile and finish are unsupported by the available references. |
| Interior | Office and boardroom furniture are present; current plan renders read as diagrams rather than enclosed, usable interior spaces. |
| Export and placement | Reopens cleanly, expected export collection exists, all mesh objects have material slots, root transform is reported; master/GIS alignment is still unverified. |

**Decision:** revise before calling complete. Round 5 improves the portico silhouette slightly, but the highest-impact issue remains the entry assembly obscuring the facade and hiding the door. Interior presentation and master/GIS placement also need evidence before this can approach 9/10.
