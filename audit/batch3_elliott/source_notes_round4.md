# Elliott Hall of Music source notes — round 4

Research and model pass: 2026-10-23. This pass changed only `modular/buildings/elliott_hall_of_music.blend` and evidence under `audit/batch3_elliott/`.

## Primary and architectural references

- Purdue Convocations' accessibility page states that the north and south access doors carry black-and-gold awnings and provide step-free access to main-floor seating; it says Elliott has no elevators. It also identifies wheelchair seating with nearby companion seating. [Accessibility](https://convocations.purdue.edu/accessibility/)
- Purdue Convocations says Club Convos uses Hovde's southeast entrance, then elevator or stairs to the second floor, followed by the adjoining bridge into Elliott's main-floor lobby. [Club Convos](https://convocations.purdue.edu/clubconvos/)
- SAH Archipedia describes a formal campus entrance via a second-story Hovde walkway, further ground-level entrances between the halls, and exterior materials/features including red brick, Indiana limestone and red clay tile. The prior source notes also record the described curved canopy, entrance frames and sculpture groups. [SAH Archipedia](https://sah-archipedia.org/buildings/IN-01-157-0079)
- Purdue Convocations' 75th anniversary article links exterior construction photography and an archival panorama. The article identifies Elliott as a roughly 6,000-seat proscenium auditorium. The image files were located, but their pixels could not be inspected with the available browser tools in this pass; they were not used to claim an opening count or rhythm. [Anniversary article](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/), [exterior construction image](https://convocations.purdue.edu/wp-content/uploads/2015/06/ElliottHallbw1-300x247.jpg), [construction panorama](https://convocations.purdue.edu/wp-content/uploads/2015/06/Elliott-Pano.jpg)
- Purdue Archives' collection guide indexes a 1940 photograph titled “South facade of new music hall (Elliott Hall of Music).” The index entry identifies an archival source, but the image itself was not accessed in this pass. [Purdue University Office of Marketing and Media photographs collection guide](https://archives.lib.purdue.edu/fa/UA62_Series3.pdf)
- The horizontal shell continues to use the existing 188-point Purdue GIS footprint for Feature ID 617. The footprint gives plan position only; it does not supply facade windows, levels, building height, or bridge geometry. [Purdue BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0)

## Round 4 modeling changes and evidence status

- Kept the two north/south accessible openings and Purdue-specified black/gold awning assemblies. Their exact location, size and elevation remain estimates derived from the GIS boundary and prior round's modeling.
- Added two approximate ground-level openings on Elliott's Hovde-facing/east-side boundary. Their existence between the halls follows the SAH description; exact position, count, width, door leaf and surrounding stone are estimates.
- Added an upper opening and a tapered second-story bridge component. Purdue and SAH document the bridge and Elliott lobby destination. The modeled span is about 18.0 m, with bridge level about 4.2–7.3 m; these values and the connector profile are estimates. Its far endpoint is registered to the closest southwest Hovde wall segment from the current Hovde source library and manifest origin. Hovde's linked asset was used only for a temporary context render and was not modified.
- Removed two invented interior route ribbons and two invented wheelchair-clearance pads. Retained the existing wheelchair-seat markers, relabeled them as indicative positions from Purdue's unscaled seating chart. The markers do not certify route, seat coordinate or clearance dimensions.
- The shell currently has no window apertures. Round 3 removed the unverified 140-opening schedule. No schedule was restored because the official photo files and archival catalog image could not be visually inspected here. The result is still visibly too blank and should not be treated as a finished facade; window number/placement needs direct photo or elevation verification.
- Procedural brick/limestone/roof materials remain; bridge glazing and light framing are conceptual. No measured facade finish schedule or bridge detail was found.

## Registration and limits

- The source asset's local horizontal frame and manifest placement origin were preserved. The bridge-to-Hovde endpoint is inferred using the saved Hovde asset's relative placement; it is not a surveyed tie.
- The model was saved and reopened with Blender 5.2.3. Export collection contains 89 mesh objects after the new openings/bridge. The prior 496-object legacy collection remains outside the export collection.
- All vertical envelope levels, door dimensions, ground-entry spacing, bridge shape/section, flytower geometry, window placement and most seating coordinates remain estimated. No scaled architectural plan or measured elevation was located.
