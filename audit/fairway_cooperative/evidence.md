# Fairway Cooperative / BYX Fairway House

## Identity and footprint

- Stable project ID: `massing_fairway_cooperative_2101b77`.
- Address: 1320 David Ross Road, West Lafayette, Indiana.
- OSM source feature: building way 220568267, named Fairway Cooperative. Raw API snapshot: [`osm_way_220568267_full.json`](osm_way_220568267_full.json).
- The project local transform (X east, Y north) converts the 14 unique OSM outline vertices into bounds X `[-1148.641, -1117.549]` m and Y `[488.498, 532.559]` m. These agree with the existing massing bounds to better than 0.0001 m. This verifies the project coordinates against its source geometry; OSM is volunteered mapping and is not a measured wall survey.
- The geometry follows the complete irregular footprint ring; plan rotation is preserved. Street-level photos show a long multi-wing residence, brick exterior, regular window rows, and dark sloped roof. Exact wall elevations and roof pitch are not available in the found sources.

## Vertical and interior evidence

- OSM tags the building with `building:levels=3`.
- West Lafayette's 2025 building permit list identifies a “New 3-story addition - BYX/Fairway House” at 1320 David Ross Road, permit 27954, valuation $5,000,000. This supports a three-level residence/addition but does not state a surveyed height or roof profile.
- A September 28, 2026 WLFI report describes the expanded house at 130 beds and documents sleeping rooms, study rooms, lounges, a multipurpose chapter room, and a prayer room. The raw article HTML is preserved as [`wlfi_article.html`](wlfi_article.html).
- The modeled 3.15 m floor-to-floor spacing and 1.45 m roof rise are estimates. The room layout is schematic and follows the published room program rather than architectural plans. The interior preview is a ground-floor cutaway plan.

## Imagery

- Google Maps Street View viewpoint used for the exterior appearance: <https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.432,-86.92706> (retrieved 2026-10-26; imagery date was not exposed in the viewer). The view shows the residence on the David Ross Road frontage, a brick facade, repeated windows, and a dark sloped roof.
- WLFI article: <https://www.wlfi.com/2026/09/28/purdue-byx-expansion-puts-focus-faith/> (published 2026-09-28; retrieved 2026-10-26).
- City permit list: <https://d3n9y02raazwpg.cloudfront.net/westlafayette/a2b4913f-b24c-11ef-ab4b-005056a89546-cff30912-cddf-4b95-ab44-f6b7a2c8f869-1764618160.pdf> (permit 27954, 2025-11-20; retrieved 2026-10-26).
- MapCARTa's place record cross-checks the address, OSM way ID, and three-level tag: <https://mapcarta.com/W220568267> (retrieved 2026-10-26; secondary index of OSM data).

## Model and uncertainty

- The source asset remains in campus coordinates and keeps the expected scene and collection names. Exterior elements include masonry shell walls, repeated glazed window bays and frames, sill/string courses, entry and sign, hipped/gable roof surfaces, eaves, and gutters.
- The library contains three floor plates, a central corridor, representative sleeping/study furniture, kitchen counter, lounge, chapter-room table, prayer-room rug, and stair treads.
- No external image, linked library, or absolute-path dependency is required by the building asset.
- Roof silhouette, facade dimensions, floor heights, window spacing, and the exact entrance treatment remain estimated where sources do not provide plans or measured elevations.

## Builder outputs

- Build module: [`../../modular/buildings/build_massing_fairway_cooperative_2101b77.py`](../../modular/buildings/build_massing_fairway_cooperative_2101b77.py).
- Blender library: [`../../modular/buildings/massing_fairway_cooperative_2101b77.blend`](../../modular/buildings/massing_fairway_cooperative_2101b77.blend).
- Exterior render: [`exterior_preview.png`](exterior_preview.png).
- Ground-floor cutaway: [`interior_schematic_preview.png`](interior_schematic_preview.png).
- Candidate build data and hash: [`build_report.json`](build_report.json).
