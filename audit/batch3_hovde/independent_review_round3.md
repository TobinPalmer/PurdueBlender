# Hovde Hall — independent review, round 3

**Score: 6.7/10. Does not reach 9/10.** Round 3 improves the brick value, removes the oversized rooftop block, and makes the repeated window grid easier to read. The saved asset is intact and recognizable, but the portico still reads as a thin, pale facade overlay, roof geometry/materials are not supported by a Hovde-specific roof source, and the two interiors are sparse schematic cutaways. Placement is not independently certified because this packet has no current master/GIS overlay.

## What I checked

- Reopened and inspected the saved `modular/buildings/hovde_hall.blend` evidence through the Blender round-3 render and asset-check logs. The recorded reopen check reports scene `Building_hovde_hall`, export collection `Asset_hovde_hall`, 672 exported objects / 660 meshes, no unmaterialed meshes, and root scale `[1,1,1]`.
- Viewed `exterior_round3.png`, `presidential_office_round3.png`, and `trustees_boardroom_round3.png`, and compared them with both prior independent reviews and the round-3 change notes.
- Checked the dated, geotagged [2016 Julian Herzog Hovde exterior photo](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg). The page identifies the image as Hovde Hall, dates it 18 September 2016, and gives camera coordinates 40.428660, -86.913958. This is useful for facade silhouette and visible roof appearance, but is not a measured elevation or roof plan.
- Reviewed the recorded asset check: root transform remains location `[-62.85, 93.0, 0]`, Z rotation `0.689754 rad` (39.52°), and unit scale. This is an internal library transform, not the campus placement marker. No current master neighborhood view or footprint overlay is in the evidence, so I cannot certify campus location, orientation, or footprint fit.

## Improvements since round 2

- **Roof mass:** The former 12 × 24 × 2.5 m rooftop block has been reduced to a roughly 5 × 8.4 × 1.2 m feature, which no longer dominates the roofline. The render still shows this as a small, box-like raised cap, and the new low-pitch hipped roof is explicitly inferred.
- **Facade materials and windows:** Brick now reads as dark red-brown in the neutral exterior view. Window sash detail is more legible, and the limestone bands are easy to follow. Material variation remains subtle and the glazing reads mostly as flat dark blue-gray rectangles at this distance.
- **File checks:** Expected scene and export names, material assignment on every exported mesh, and the unchanged root transform are recorded in the reopened-file check.

## Prioritized remaining work

1. **Integrate and proportion the portico.** In the overview, the broad pale pediment and entablature sit over and obscure the central window grid, while the six supports read as narrow rectangular strips. The reference photo supports a clearly projecting, columned classical entry. Give the columns visible round shafts, bases and capitals, add depth to the entablature/pediment, align the stairs and entry, and show a close three-quarter view confirming the portico meets the facade cleanly. Avoid hiding windows behind an oversized stone panel unless a facade source confirms that arrangement.
2. **Resolve the roof with building-specific evidence.** The red-brown surface is an improvement over the dark flat roof in earlier rounds, but the current wide render shows a broad near-uniform plane and an unsupported central cap. Use an overhead or roof-plan source to choose the roof profile and cap; if unavailable, keep the roof conservative and label its profile/material as estimated. Tune the neutral render so the red roof and limestone can be distinguished without dramatic lighting.
3. **Develop the interiors beyond furniture diagrams.** Both cutaways show a large open box, two window frames, and a few furnishings. The office desk and small seating cluster occupy only a fraction of the room; the trustees' table and chairs form a single strip in a similarly empty space. Add plausible wall openings, doors, circulation, and room-scale furnishing/detail, or reduce the modeled room extents to a supported footprint. The modeler labels layouts illustrative; no source plan currently verifies their size or arrangement. Keep the two rooms clearly identified as interpretive until a Hovde floor plan is found.
4. **Verify the entry orientation and campus footprint in context.** Preserve the internal root and the manifest marker. Have the master agent render the saved library in the current master and overlay its structural walls against official Purdue GIS feature FID 618. Compare the facade entry direction and wall footprint separately from the steps, canopy, and site objects. Current building-only renders cannot verify this.
5. **Add a close exterior detail view.** The wide view makes the brick shader, sash depth, limestone profile, and roof edge hard to assess. A neutral facade close-up should show wall courses, window recesses/frames, stone band depth, and the portico connection at human scale.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and broad massing | Recognizable long, four-level brick administration building with central entry. |
| Portico | Correct general classical intent and six supports, but pale, shallow, and poorly integrated at overview scale. |
| Roof | Reduced cap and hipped overlay improve silhouette; exact form and material remain unverified for Hovde. |
| Facade and materials | Red-brown brick, light bands, and repeated windows are legible; surface and window depth need close-up review. |
| Interior | Two named spaces with furniture, but both remain sparse illustrative shells with unverified footprints and circulation. |
| Placement and dimensions | Root transform and asset bounds are reported; no current master/GIS overlay or measured wall-only comparison supplied. |
| File integrity | Saved asset reopens; expected export collection exists; all mesh objects report material slots. |

**Decision:** continue revisions; do not mark Hovde complete or claim 9/10. The largest remaining visible issue is the portico/facade relationship, followed by source-based roof resolution and more complete interior space planning. Independent review did not edit the asset or master file.
