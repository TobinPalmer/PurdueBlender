# Elliott Hall of Music — independent review, round 9

**Reviewer:** independent pass on the saved round 9 asset  
**Score:** **6.9/10**  
**Rating threshold:** Below 9/10; do not mark complete or integrate as a finished building yet.

## What I checked

- Reopened `modular/buildings/elliott_hall_of_music.blend` in Blender 5.2.3 LTS. `Asset_elliott_hall_of_music` loaded with 135 mesh objects; both `ELLT_R9_Estimated_Landing_Corbel_*` objects are present, the old review text is absent, and no temporary round 9 objects remain.
- Inspected the round 9 portal, audience and plan renders, and the north-up neighborhood overlay.
- Read the raw Purdue BuildingShapes layer metadata and FID 617 feature snapshot, the comparison script and JSON, and the current manifest placement record.

## Findings

### Footprint and placement

The horizontal footprint check is sound for a compact-area estimate. It identifies the source as Purdue BuildingShapes FID 617 / ELLT, records the layer’s 102100/3857 Web Mercator CRS and retrieval time, and compares the ordered vertices after a documented ground-scale conversion without fitting away a translation or rotation error. The reported 0.167 m RMS / 0.259 m maximum residual, -0.168% area difference, and -0.076% perimeter difference are consistent with a very close match. The green asset outline visually tracks the GIS outline in the overlay. These numbers support horizontal footprint correspondence only; the constant latitude scale approximation and the non-surveyed GIS source remain limitations.

FID 617 and adjacent Hovde feature 618 touch in the GIS rings (computed closest distance: 0 m). That is useful for locating the interface but does not establish an upper-level doorway, bridge, or accessible route. The current Elliott asset correctly leaves its landing isolated pending a verified Hovde portal. SAH Archipedia describes the historic second-story connection between the buildings, so the pair still needs a coordinated interface review once Hovde’s portal is assessed.

### Portal and exterior

The red brick, pale limestone banding, curved canopy, portal surround and supports read as a coherent stylized interpretation of Elliott’s Art Deco vocabulary. The two new corbels make the short landing’s support more legible. In the close portal render, however, a pale rectangular trim/block obscures part of the left door leaf and makes the entry look like overlapping geometry. Clean up that intersection and show a slightly wider view that establishes where the landing sits on the facade. Corbel, canopy, portal, and landing dimensions are still estimates.

The facade remains a major fidelity gap. There is no verified window schedule, so omitting invented openings is defensible, but the large unfenestrated wall areas do not resemble a finished representation of the real building. The flat, highly repetitive brick and limestone treatment also needs more verified elevation detail and material variation. The current evidence should not present those elevations as complete. Purdue’s architecture account identifies a red clay tile roof, limestone pilasters and ornament, secondary entries, side-exit stair walls, a fly tower and an apsidal stage projection; the model’s interior shell/audience view does not yet demonstrate all of those exterior features at a convincing level.

### Interior

The audience cutaway communicates the main floor and two balcony levels, and the plan render is now framed clearly enough to inspect. It remains an attractive schematic: seat blocks are repetitive, aisle and circulation logic is not established, the stage/backstage area is only lightly represented, and the image does not prove seating counts, dimensions, accessibility, or egress. Purdue’s seating chart supports the main floor and two balconies with curved seating blocks, but it is not dimensioned. Keep the interior labeled as schematic until dimensioned plans or measured references are available.

### Hovde and accessibility

The round 9 revision appropriately removes the misleading “LINK DEFERRED” label and does not claim a continuous connector. The landing endpoint and two corbels remain a provisional Elliott-only interface. Clear widths, thresholds, slopes, level changes, handrails, accessible seating routes, and continuity to Hovde are not evidenced. No accessibility-compliance claim is supported.

## Prioritized work

1. **Coordinate the Elliott/Hovde interface after Hovde review.** Confirm which elevation and floor connect, the actual door location and threshold, and the connector geometry against both assets; then assess a continuous route from verified source measurements. The touching GIS footprint edges alone are insufficient.
2. **Fix the portal intersection.** Remove the pale obstruction across the left door leaf and review the door, frame, canopy, piers and corbels together in a wider exterior view.
3. **Complete the exterior facade from verifiable elevations.** Add evidence-backed windows, pilaster/banding rhythm, entrances, side-exit treatment, fly tower and rear apsidal massing; record where dimensions remain estimated.
4. **Improve the interior beyond the seat-block schematic.** Use dimensioned plans if available; otherwise retain explicit schematic status and add more legible stage, orchestra/pit, aisle, balcony circulation, and backstage relationships.
5. **Refine material presentation.** Give brick and limestone more natural variation and make the tile roof read as clay tile at normal viewing distance, while checking colors against current exterior photos.

## Source checks

- [SAH Archipedia — Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079): architectural form, materials, historic connection to Hovde, fly tower, secondary entries and auditorium.
- [Purdue Convocations — Elliott seating chart](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf): main floor and balcony seating arrangement; not dimensioned.
- [Purdue Convocations — accessibility information](https://convocations.purdue.edu/accessibility/): general venue access reference; it does not validate the modeled route or clearances.
- [Purdue Convocations — Elliott Hall venue/map page](https://convocations.purdue.edu/venue/elliott-hall-of-music/?eventDisplay=past): venue location and map link.
- Purdue GIS raw FID 617 snapshot, layer metadata, neighboring features, method and footprint results are stored under `audit/batch3_elliott/`.
