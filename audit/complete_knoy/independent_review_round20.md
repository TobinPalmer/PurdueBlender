# Knoy Hall — Independent R20 Full-Building Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/knoy_hall.blend`  
**Grade:** **7.8/10 — below the 8.0 threshold.**  
**Scope:** Reopened asset validation, R20 source record and corrected sightline SVG/preview, R17 exterior/entrance renders, prior R18 scorecard, and cited source summaries. No Knoy, master, or shared project files were changed.

## Scorecard

I use the established six-category full-building rubric. The first five categories are out of 2 points; technical/evidence quality is out of 1 point. Normalized score: **8.6/11 × 10 = 7.8/10**.

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.7/2 | Official Purdue GIS and campus context support Knoy's identity and stepped footprint. The local conversion remains approximate, not survey control. R20's corrected ray identifies a candidate GIS segment only. |
| Placement, orientation, and scale | 1.6/2 | Prior manifest and placement evidence remains applicable; R20 changes no transform and supplies no new survey control. |
| Height, floors, and roof | 1.2/2 | 2018 DSM measurements provide broad roof-like surface context but do not establish exact slab/parapet height, occupied L5, penthouse geometry, or resolve the 48-ft GIS attribute conflict. No R20 geometry changed. |
| Exterior and entrances | 1.4/2 | The official archive image shows brick-heavy masses and interrupted horizontal glazing on the pictured faces, while the current exterior render still shows repeated continuous ribbon glazing. R20 corrects which panorama/ray was plotted but does not add a face-registered elevation or measured opening schedule. |
| Interior and circulation | 1.7/2 | The model includes plan traces, illustrative doors, fixtures, and stairs. No new digitized as-built circulation/stair plan was found; route continuity and exact dimensions remain unverified. |
| Technical and evidence quality | 1.0/1 | Blender reopen and four mesh-fingerprint checks pass; no unpacked images are reported. R20 now correctly distinguishes the Aug 2025 and June 2009 camera positions and regenerates the 2025 diagram from the primary JSON. |
| **Total** | **8.6/11 = 7.8/10** | **Below target** |

## Corrected R19/R20 sightline

The R19 issue is resolved in R20. The former diagram had plotted the June 2009 panorama's camera/ray while labeling it as Aug 2025. R20 records those two panorama positions separately and regenerates the diagram from the 2025 camera values.

The corrected 2025 pair is internally consistent: camera `[260.3770, 78.5941] m`, heading `244.31604°`, intersection `[234.4722, 66.1359] m` on GIS edge 18, edge parameter `u=0.6919`, and range `28.7448 m`. The R20 SVG labels the same point and parameter. This repairs the metadata mismatch and restores full technical/evidence credit; it does not change the building or raise its visual/architectural fidelity score.

The sightline still only narrows the photographed facade to a candidate GIS edge. The cited image remains perspective and partly occluded, without camera calibration or surveyed registration. It cannot justify exact slit count, dimensions, interruption positions, or applying one facade pattern to every elevation.

## Full-building findings and remaining work

R20 is a sound evidence correction, but the asset's geometry and materials are unchanged from R18/R19. The exterior render retains the most visible mismatch against the Purdue Archives photo: regular continuous glazing bands versus the photo's more interrupted narrow glazing and broad brick fields. No face-specific segmentation change is warranted solely from this uncalibrated ray/photo. The roof and L5 interpretation, floor heights, penthouse, and complete interior circulation still need better source drawings or measurements.

The grade remains **7.8/10**, below the 8.0 target. R20 improves the accuracy of the evidence package, not the model. A calibrated elevation/photo or digitized as-built drawing is still needed before changing the window pattern, roof, or circulation.

## Evidence reviewed

- `audit/complete_knoy/evidence_round20.json`
- `audit/complete_knoy/validation_round20.json`
- `audit/complete_knoy/facade_glazing_assignment_r20.svg` and `facade_glazing_assignment_r20.png`
- `audit/complete_knoy/knoy_exterior_full_r17.png`, `knoy_entrance_facade_r17.png`, `reviewer_cutaway.png`
- Prior R18 independent review and scorecard; roof spatial analysis and saved-source fingerprint validation.
- [Purdue Archives Knoy Hall photo](https://collections.lib.purdue.edu/campus/buildings/75)
- [Purdue Archives UA 141 finding aid](https://archives.lib.purdue.edu/repositories/2/resources/1490)
- [Purdue Engineering 2018 Existing Knoy Elevations study](https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf)

No grade of 8.0 or higher is supported by this review.
