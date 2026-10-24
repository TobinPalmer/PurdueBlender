# Knoy Hall — R22 source and geometry decision

**Date:** 2026-10-24  
**Scope:** Search for new, accessible, direction-registered facade, roof, or floor-plan evidence that would justify measurable edits to the Knoy source model. Knoy-only; no model, builder, master, or shared files changed.

## Outcome

No newly accessible source located in this pass is sufficiently calibrated and face-registered to support changing Knoy's facade openings, roof/L5/penthouse, or interior circulation. The existing 2018 Purdue Gateway planning sheet remains the only accessible source found with explicit L1–L4 vertical intervals and a typical upper-floor plan. The model already follows its 14 ft 8 in nominal interval to within 0.011 m per floor; those geometry values are effectively source-consistent, and changing them would be a negligible correction to planning-study precision, not a meaningful fidelity gain.

## New primary image records checked

Purdue Archives' *Purdue Buildings and Campus Scenes* collection exposes two downloadable official Knoy exterior photographs:

| Item | Record | Source date | Use and limitation |
|---|---|---|---|
| PPBUC01785 / ContentDM 1125 | https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1125/ | Original date undated; catalog decade `1990s;2000s` | Shows stepped brick volumes, pale coping/bands, and a long lower glazing strip. No camera position, heading, scale, or identified facade; foliage/perspective prevent assigning wall segments to a GIS edge. |
| PPBUC01786 / ContentDM 1126 | https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1126/ | Original date undated; catalog decade `1990s;2000s` | Winter entrance view shows brick fields and interrupted slit glazing on a tall wing, plus a lower strip and stepped coping. No camera position, heading, scale, or identified facade; it cannot resolve the 2025 sightline's candidate-face assignment. |

Provider/retrieval: Purdue University Libraries, Karnes Archives and Special Collections, *Purdue Buildings and Campus Scenes*; records and IIIF JPEGs retrieved 2026-10-24. Raw API snapshots and downloaded JPEGs are saved alongside this note as `purdue_archives_item_1125_r22.json`, `purdue_archives_item_1126_r22.json`, `purdue_archives_knoy_exterior_1125_r22.jpg`, and `purdue_archives_knoy_exterior_winter_1126_r22.jpg`. These are unreferenced perspective photographs; no source CRS or geotag is supplied.

## Direction-registered plan lead assessed

A 2012 Purdue CERIAS technical report states that the College of Technology had downloadable Knoy floor-plan JPEGs and that the author placed a plan over Google Earth imagery by fitting opposing image corners. Figure 3.3 reproduces a Knoy floor-plan overlay on an aerial image. This confirms an approximate plan-to-aerial overlay was used, but not a recoverable direction/coordinate registration: the report only embeds a small raster figure (~480 × 480 source pixels); it gives no coordinate tie points, map heading, scale, level identifier for the depicted plan, control residual, or independent survey. Its walls/room labels are too low-resolution for reliable wall tracing, door/stair identification, or dimensional edits. The original higher-resolution floor-plan JPEG was not located. Source: https://www.cerias.purdue.edu/assets/pdf/bibtex_archive/2012-07.pdf, PDF pp. 74–76 (printed pp. 57–59), especially Figure 3.3 on PDF p. 76 and the accompanying georeferencing description. A local PDF snapshot and rendered pages/crop are retained as `source_knoy_r22_cerias_report.pdf`, `source_knoy_r22_cerias_p-075.png`, `source_knoy_r22_cerias_p-076.png`, and `source_knoy_r22_cerias_knoy_plan_crop.png`.

The overlay is a potentially useful lead for a higher-resolution source request, but its rendered figure does not meet the project evidence standard for measurable edits. It was not used to infer dimensions or circulate a speculative plan trace.

## Actionable geometry already supported

- The 2018 Purdue Gateway Formation Study marks existing Levels 1–4 at 14 ft 8 in (4.4704 m) floor-to-floor. The saved asset uses L1–L4 datums 0.000, 4.481, 8.961, and 13.442 m. Its interval differences from the nominal source value are +0.0106, +0.0096, and +0.0106 m, respectively; the accumulated L4 offset is +0.0308 m. The dimensions are a planning-study note, not an as-built survey. The existing geometry is already consistent within ~3.1 cm through L4 and offers no consequential correction at this model's level of certainty.
- The two archive photos independently support the building's brick-heavy treatment, stepped parapet/coping silhouette, and interrupted rather than uniformly continuous glazing on pictured but unidentified faces. They reinforce the existing uncertainty report, but cannot locate exact glazing interruptions on a specific model wall. No wall/window edit is justified.
- No accessible direction-registered elevation, roof plan, measured height survey, or basement/stair plan was found. L5, roof and penthouse geometry and continuous circulation therefore remain unresolved. No unsupported geometry was added or moved.

## Request for future evidence

To resolve the current blockers, obtain either the original high-resolution plan JPEGs cited by the 2012 report or inspect/copy the relevant Purdue Archives UA 141 construction/floor-plan folder and UA 62 1985/1989 exterior/interior photo material. For facade edits, an elevation with compass orientation or a geotagged/calibratable view is required. For L5/roof edits, obtain a roof plan or measured elevation tied to known datums. For circulation, obtain floor plans with level labels and stair/elevator connections. Archive finding aids identify physical holdings but do not themselves provide the drawings/images.
