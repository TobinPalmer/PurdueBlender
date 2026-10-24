# Math Sciences Source Review — R12

**Date:** 2026-10-24  
**Asset reopened:** `modular/buildings/math_sciences.blend`  
**Scope:** Supplementary exterior photo research and source-only validation. No geometry/material edits, master changes, shared-file changes, or commits.

## Result

R12 adds two clearer exterior references: a dated 2009 high-resolution photo by an independent photographer and an image published by Purdue Statistics. Together with the R11 archive photo/drawing, they verify the broad design vocabulary more strongly: repeated vertical window bands, simpler corner/end bays, a lighter glazed lower level, and a parapet/raised roof edge. The photo sources do not provide a verified compass bearing; their faces cannot be mapped to model north/east/south/west. The rooftop silhouettes have no scale or component identification. No openings, facade parts, roof geometry, or interior geometry were changed.

## New image evidence

The Department of Statistics' [Getting Started page](https://www.stat.purdue.edu/external_relations/statcom/getting_started.html) labels its image “Purdue's Math Building - Home of Department of Statistics.” The associated [image file](https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg) is a small view of a brick elevation, window ribbons, simpler end bays, and the lower entrance area. The image's capture date is not stated, and its page date is not proof that the image is current.

John Feister's Flickr photo, [Math Building — Purdue University](https://www.flickr.com/photos/ataindy/4062109632/), states that it was taken on September 26, 2009 and uploaded October 31, 2009. I inspected the 2384 × 3526 original through Flickr's [sizes/download page](https://www.flickr.com/photos/ataindy/4062109632/sizes/o/). The image shows a broad brick elevation with repeated vertical window strips, discrete end/corner windows, a lighter lower level, and a parapet/roof edge with thin rail-like elements. The original EXIF has a 2009-10-29 DateTime, which conflicts with the photographer's stated taken date; R12 preserves both without treating the EXIF timestamp as the capture date. No GPS coordinates were embedded. Flickr states all rights reserved, so the original was inspected but not retained in the project.

The images strengthen the qualitative match between the saved facade vocabulary and photographed MATH elevations. They do not settle which local/cardinal face appears in either photo or prove current post-2009 conditions. R12 therefore does not fill or move the currently blank surfaces. Source details, observations, and limitations are recorded in `math_photo_inventory_r12.json`.

## Roof and interior follow-up

Neither new photo is a measured roof source. They show a roof edge/penthouse silhouette but no dimensioned elevation, identifiable component, or georeferenced camera location. R10's DSM-minus-DTM p50 of 36.92 m and p95 of 40.43 m remain above the modeled shell/roof/penthouse bounds, but the broad 5-ft raster values still cannot be assigned to a specific shell, penthouse, parapet, or rooftop-equipment object. No roof component moved.

No new as-built interior plan was found. The physical Purdue Archives floor-plan accession identified in R11 remains an uninspected, unscanned lead. The interior model remains schematic.

## Validation

Blender 5.2.3 reopened the unchanged saved asset. `round12_validation.json` passes with 550 direct and 593 inclusive objects, unchanged 33.2 m shell top, 33.4 m roof-slab top, 36.5 m penthouse coping, no unpacked image files, and zero R12 geometry changes. The master and shared files were not edited.

**Status:** Ready for a fresh independent R12 grade. No R12 self-score is claimed.
