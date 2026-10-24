# Math Sciences Source Review — R11

**Date:** 2026-10-24  
**Asset reviewed/reopened:** `modular/buildings/math_sciences.blend`  
**Scope:** Source investigation for unresolved facade, rooftop, and interior questions. No geometry, materials, asset metadata, master, or shared files were changed.

## Result

R11 improves the evidence available for broad historical facade characteristics, but did not locate a direction-identified elevation or measured roof drawing. It also found an archival floor-plan lead that is not available as a public scan. No unsupported edits were made. The asset remains at its R10 geometry and is ready for a fresh independent grade on the added evidence.

## Newly inspected exterior sources

Purdue eArchives item 823 is an undated black-and-white exterior photograph, cataloged as a 12 × 10 cm portrait photograph. Its public IIIF image shows an oblique corner: one masonry end wall is largely unfenestrated, while the adjacent long face has recurring vertical window groupings. This establishes that a substantially blank end wall and vertical facade rhythm are historically plausible. The image is not direction-tagged or dimensioned, and its date/current status are unknown, so it does not identify which model cardinal face is shown or verify present openings.

Purdue eArchives item 824 is an undated black-and-white exterior-view drawing, cataloged as a 10 × 12 cm landscape drawing. The public image shows a tall rectilinear tower, repeated vertical window bands, simple corner/end bays, a glazed lower level, a flat parapet, and a raised rear roof silhouette. This supports original-design motifs only. The drawing's date, compass orientation, dimensions, as-built status, and meaning/height of the roof element are unknown. It cannot justify moving the shell or penthouse, adding openings to a particular elevation, or assigning the R10 DSM high-return cluster to a roof component.

The original eArchives pages state **Copyright Purdue University Libraries**. I inspected the linked images but did not add the copyrighted image files to this project. Image-record metadata and the source URLs, observations, and limitations are preserved in `math_source_inventory_r11.json`.

## Roof-height follow-up

The R10 2018 DSM/DTM comparison still shows a broad height conflict: the normalized surface median is 36.92 m above the estimated local terrain, compared with the modeled shell roof slab at 33.4 m and penthouse coping at 36.5 m. The footprint statistic includes multiple surface types, and the 5-ft cells do not delineate architectural components. The historic drawing's raised roof silhouette is qualitative and lacks scale. Neither source supports assigning a correction to the shell, penthouse, parapet, or equipment, so R11 leaves all heights unchanged.

The Indiana Statewide Elevation Catalog confirms that Indiana's 2016–2020 lidar point-cloud LAS files are publicly available as a tile-organized dataset. The IU portal describes QL2 point-cloud deliverables at about two last-pulse returns per square metre. The matching LAS object for the R10 raster tile was not identified and analyzed in R11. Even a successfully aligned point cloud would need local vertical-datum and roof-component checks before it could justify a specific geometry change. [Indiana Statewide Elevation Catalog](https://registry.opendata.aws/in-elevation/) · [IU Indiana Spatial Data Portal — 2016–2020 elevation](https://gis.iu.edu/s/isdp/page/20162020elevation)

## Interior-plan lead

Purdue Archives' [accession record 2024-012](https://archives.lib.purdue.edu/repositories/2/accessions/2685) lists annual reports, floor plans, and information concerning the Mathematics Library move into MATH. It describes a small physical folder; no scanned plans are linked, and the record says its source and acquisition date are unknown. It could be a useful research lead through the Archives, but it does not establish current as-built conditions and was not used to add rooms or circulation. The accessible 2022 Board third-floor plan and 2025 Libraries reopening article/photo remain the evidence for the schematic library/core area; full room layout, route widths, and vertical circulation remain unverified.

## Saved-file validation

Blender 5.2.3 reopened the unchanged saved asset. `round11_validation.json` passes: 550 direct objects, 593 collection objects including children, unchanged shell/roof/penthouse bounds (shell top 33.2 m, roof slab top 33.4 m, coping top 36.5 m), the R10 geometry-change flag remains false, and no unpacked image dependencies are present. R11 made zero geometry changes. The validation script and complete source/evidence record are in this dedicated audit folder.

**Status:** Ready for fresh independent grading. No R11 self-score is claimed. No master or shared files were edited; no commit or push was made.
