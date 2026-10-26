# Schowe House model notes

## Identity and source match

The README assigns `purdue center for regional development scho` (stable ID `massing_purdue_center_for_regional_development_scho_a2375c9`) to Tobin. The official Purdue campus GIS feature is OBJECTID 295 / ABBR `SCHO`, named **Schowe House**, address 1341 Northwestern Avenue. Its source description records the original house in 1929, west-wing improvements in 1990, and use as the Global Policy Research Institute center beginning in 2009. Purdue's current campus map labels SCHO as “Global Policy Research Institute (Schowe House),” and PCRD's official page confirms the house address.

## Geometry and placement

The exterior wall path is built from all 40 non-closing vertices of GIS feature 295, converted from returned WGS84 geographic coordinates using the campus project's local approximate meter transform. GIS plan area is 471.365 m² and the polygon perimeter is 127.871 m. The transformed bounds are X -404.934 to -379.679 m and Y 1309.704 to 1330.742 m. The exterior wall faces coincide with the GIS segments within the documented 0.14 m wall thickness; each segment midpoint is computed from the segment endpoints, and adjacent runs overlap at corners to avoid disconnected seams. The roof is clipped to the same concave footprint and does not extend outside it. The building remains in campus coordinates, preserving the existing massing asset collection/scene and direct-link placement convention.

## Visual evidence and construction

A 2025 NIRPC appendix page associates a color photograph of the actual brick Schowe House with the PCRD contact panel and 1341 Northwestern Avenue address. Visible properties include red/brown brick, steep intersecting gables, gray slate-like roof on the main sections, dark brown wood cladding on an upper gable, tall chimneys, rectangular dark-framed windows, and garage doors. The photo is partially obscured by mature trees and does not identify its camera azimuth or building height. The revised model represents the west historic roof, east main cross-gable, and south cross-wing with three GIS-bounds-derived roof runs, dark wood triangular gable infill, and two brick chimneys with caps. The roof panels are single-sided slate surfaces, and fascia is restricted to eaves; the prior thick deck and tall rake boards that left bright intersection faces have been removed. Junction dimensions, exact roof pitches and chimney positions remain photo-based estimates. Brick/slate tile images are generated deterministically and packed into the Blender file; they are authored assets, not copied photo textures.

A simple ground-floor slab and internal partitions are present to provide a schematic interior volume. No room plan or interior photo was located, so the interior layout is not claimed as accurate.

## Estimates and unresolved evidence

- Wall/eave, roof ridge, and garage-door dimensions are estimates inferred from one exterior photograph and common residential proportions. There is no surveyed vertical model or published elevation.
- Roof-run boundaries are inferred from orthogonal GIS footprint bounds, not a roof survey; the imagery does not disclose exact ridge intersections or the compass direction of the photo. Chimney positions and dimensions are approximate.
- The West Lafayette Public Library search-indexed collection describes a 1930 image of the Allen family home at this address and dates construction to the early 1930s; Purdue GIS records 1929. The dates conflict and are retained as such.
- Interior partitions are schematic and unverified.

The raw GIS responses, official campus-map PDF, official PCRD page, source appendix PDF, page raster, and cropped reference photograph are preserved in `sources/`. The photo crop is only a review aid; no external image is linked into the model.
