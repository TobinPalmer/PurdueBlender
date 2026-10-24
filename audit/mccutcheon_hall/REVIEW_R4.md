# John T. McCutcheon Residence Hall — R4 Evidence and Review Notes

**Updated:** 2026-10-24  
**Asset:** `modular/buildings/mccutcheon_hall.blend`  
**Scope:** McCutcheon asset and its dedicated audit folder only. No master, shared indexes/scripts, other buildings, commit, or push.

## R4 model change

Removed 16 unsupported tall rooftop penthouse objects: brick enclosures, their coping and roof slabs, louver panels, and doors from both towers. Retained the tower roof decks, parapets, coping, and existing roof HVAC objects. This reduces modeled tower roof edge to 27.72 m in the local model; the model's remaining mesh maximum is 28.50 m at the existing HVAC fan objects. The 28.50 m maximum is not treated as a measured building elevation.

This change follows the available 2017–2018 USGS 3DEP returns: the roof candidate distribution within Purdue GIS FID 57 has p95 height 25.93 m and maximum 26.16 m above nearby ground. There are no candidate returns at or above 27 m. These data make the previous 30.35 m penthouse top difficult to support and place the retained model roof deck (about 26.6 m local Z) in approximate agreement with the candidate returns. However, the point cloud contains no class-6 building returns, its candidates are class-1 unclassified points, the product metadata says vertical accuracy N/A, and vegetation or missed roof details are possible. The LiDAR does not establish an exact as-built height or prove the roof has no enclosure. The remaining modeled HVAC fans reach 28.5 m and likewise are not verified by a roof plan or elevation.

## Floor evidence

Official Indiana Commission for Higher Education agenda documents for 2014 and 2015 describe McCutcheon north- and south-tower renovation work on floors 1 through 8. This supports eight documented occupied floors per tower, matching the eight repeated window bands in the current model. It does not prove floor-to-floor spacing, total building height, or roof construction. The Purdue GIS layer's `NUM_LEVELS=10` and related floor/elevation fields have no documented units or definitions in the service schema, so they remain ambiguous.

## Other source and confidence limits

The official Purdue Residences exterior photo supports the qualitative entry/facade feature set recorded in R3: brick, blue-gray glazing, a perforated concrete-block screen, low glazed entrance, light base, wall sign, lawn/planting, and rooftop equipment. The image is cropped and oblique, with no stated capture date, scale, or camera orientation; it cannot register facade locations or dimensions. Existing windows, screen and entrance geometry were not changed in R4.

No as-built floor plans or direction-registered elevations were found in this pass. No interior or circulation geometry was changed. The footprint uses the approximate project transform of Purdue GIS FeatureServer FID 57; the envelope match is not survey control and no master placement validation was performed.

## Saved asset validation

`mccutcheon_r4_validation.json` records successful reopening and rendering in Blender 5.2.3. The asset has one direct root and 219 objects including children; the root remains at origin with unit scale. Roof decks/parapets/coping remain, the render-hidden GIS diagnostic overlay is present, ten foliage images remain packed, and there are no unresolved unpacked image dependencies. Hero and entrance renders were created from the reopened saved file. The validation reports both the 27.72 m tower roof edge and 28.50 m overall mesh maximum including HVAC separately.

R4 is ready for independent full-building grading. No self-score is claimed.
