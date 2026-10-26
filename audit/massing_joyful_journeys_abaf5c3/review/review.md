# Joyful Journeys builder checkpoint r1

**Status: ready for independent grade.** This is a sourced massing approximation, not a measured as-built model.

## Identity and source match

Joyful Journey is at 600 Lindberg Road in West Lafayette, at the northwest corner of Lindberg and Salisbury. The official operator site identifies it as an adult day service and says visitors can tour the house. Tippecanoe County's 2014 Z-2571 staff report describes the existing site as a single-family home and the requested use as an adult day-care center. OSM way 869182111 provides the named 600 Lindberg outline. An Esri World Imagery export independently confirms the perimeter sits on the roof.

The XY ring is essentially exact to the OSM polygon in the project's approximate local transform (IoU 0.9999999998), but the baseline object appears to have inherited that same ring. Treat the number as a repeatability check; aerial alignment is the independent check. No official survey-quality Purdue GIS shell match was found in the existing master audit.

## Geometry revision

The original asset was a 16 m high, undecorated solid with no source metadata. It has been replaced by a low-rise one-main-level home/day-service shell with a roof silhouette based on the aerial. The roof peak estimate is 7.35 m; the small ridge cap gives a saved maximum Z of 7.41 m. The model includes schematic windows and a south-facing entry canopy. Floor count, exact eave/ridge heights, roof pitch and breaks, facade materials, window layout, and entrance location remain unverified.

The former relative image texture dependencies were removed. The saved asset is one mesh object in the expected scene and collection, with identity world transform and no linked libraries, modifiers, or external images.

## Validation

Direct reopen in Blender 5.2.0 passed all checks in `validation_r1.json`. Reopen facts: 662 vertices, 162 faces; X -104.046 to -65.915 m, Y 2056.239 to 2078.080 m, Z 0 to 7.410 m. Rendered views are `joyful_journeys_hero_r1.png` and `joyful_journeys_aerial_r1.png`; `osm_roof_aerial_overlay.jpg` shows the red source outline on the aerial.

## Coordinator note

The shared manifest still records the old 16.0 m bound. Refresh its Joyful Journeys bounds after independent review; this lane made no shared-index edits and did not commit.

# Joyful Journeys builder checkpoint r2

**Status: rebuilt and directly reopened; ready for a fresh independent grade.** The model remains a sourced approximation, not a measured as-built survey.

## New facade source and revisions

A 2019 Area IV Agency community guide page includes a Joyful Journey Adult Day Service panel for 600 Lindberg Road and a photo visibly marked `600` beside the entry. The extracted original photograph is saved as `../sources/joyful_journey_exterior_photo_page85.jpg`; the full PDF snapshot is `../sources/community_resource_guide_2019.pdf`. The photo supports a covered entrance, light trim, dark shutters, and upper-level windows in a front gable. The rebuilt facade now uses muted green-gray siding, light trim, red-brown shutters, a two-level front elevation, and the covered entrance. Photo perspective does not provide a reliable north orientation or dimensions; other elevations/openings remain schematic.

The visible upper windows support modeling two above-grade levels. The total height is now an explicitly photo-scaled estimate: 5.40 m eave and 8.70 m roof peak. Neither the guide nor the 2014 county zoning report publishes an elevation or measured height. The roof shape and ridge layout remain approximate, guided by Esri aerial imagery.

## r2 reopen measurements

Reopened the saved asset directly in Blender 4.5.15 LTS using `reopen_validate_r2.py`. All structured checks pass: expected scene and collection, one mesh, identity transform, no modifiers, no linked libraries, and no external image dependencies. The mesh contains 886 vertices and 218 faces; world bounds are X -104.04565 to -65.91480 m, Y 2056.23877 to 2078.08032 m, and Z 0 to 8.76000 m (the 8.70 m peak plus 0.06 m ridge cap). Updated renders: `joyful_journeys_hero_r2.png` and `joyful_journeys_aerial_r2.png`.

The plan still follows the OSM roof-perimeter proxy. OSM is not survey quality; roof-edge-to-wall offset and absolute accuracy remain unverified. Height, story configuration and roof pitch/ridge placement remain estimates. Facade appearance now has a photographic reference, but dimensional details remain unverified.

## Coordinator handoff

Shared `modular/manifest.json` remains unchanged as instructed. After independent grading, update both Joyful Journeys `bounds_world_m` and `exterior_bounds_world_m` (and corresponding source bounds, if kept aligned to asset bounds) from the r2 reopened geometry. Current verified Z interval is `[0.0, 8.7600002289]` m; XY interval is unchanged. No commit or Git sync was performed in this lane.
