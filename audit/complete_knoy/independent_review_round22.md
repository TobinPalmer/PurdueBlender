# Knoy Hall — Independent R22 Full-Building Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/knoy_hall.blend`  
**Grade:** **7.8/10 — below the 8.0 acceptance target.**  
**Scope:** Independent read-only review of the saved model, R22 Purdue Archives photographs and CERIAS plan-overlay evidence, R22 source research, prior source package, validation, and available R17 exterior/interior renders. No Knoy geometry, materials, master, or shared indexes were edited.

## Scorecard

The Knoy review series uses six categories: five criteria worth two points each plus one technical/evidence point. The raw score is **8.6/11**, normalized as **8.6 ÷ 11 × 10 = 7.8/10**.

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.7/2 | Purdue GIS and the stepped plan support the building identity and horizontal form. R22 adds an aerial with a plan overlaid, but its source report provides no control points/residual and the embedded plan is too small to improve measured registration. The campus-local transform remains approximate, not survey control. |
| Placement, orientation, and scale | 1.6/2 | Prior manifest/GIS evidence remains applicable. The saved root is identity and R21/R22 geometry-world-matrix hash is unchanged, but R22 adds no surveyed placement or master-marker audit. |
| Height, floors, and roof | 1.2/2 | Existing L1–L4 spacing follows Purdue’s 14 ft 8 in planning-study note within about 0.011 m per interval. The R22 source hunt did not resolve L5, the penthouse, the measured roof profile, or the conflicting 48-ft GIS attribute. The two new photographs are perspective and not height references. |
| Exterior and entrances | 1.4/2 | The new Purdue Archives images independently confirm stepped red-brick masses, pale coping/bands, a long low glazing strip, and interrupted upper slit windows on pictured faces. The current model has the right broad vocabulary, but its repeated continuous glazing ribbons do not reproduce the visible brick interruptions consistently. The archive images have no geotag, compass face, or scale, so exact facade assignments/cadence remain unverified. |
| Interior and circulation | 1.7/2 | Existing modeled plans, stairs, and fixtures are supported in broad architectural character by the available 2018 planning study and emergency-plan context. The R22 CERIAS figure shows a plan superimposed over aerial imagery, but the source image is about 480 × 480 pixels and supplies no coordinates, map heading, scale, level label, or tie-point residual. It cannot validate individual walls, stairs, basement levels, or route continuity. |
| Technical and evidence quality | 1.0/1 | Blender 5.2.3 reopened the current file read-only: 191 scene objects, 169 meshes, identity `AssetRoot_knoy_hall`, and no file-backed texture images. I independently recalculated the all-object mesh/world-matrix SHA-256 as `ed4a5c1d41d90a65a53b2190888d1b54b49fa3d519d5698536f9173dd8cbe31a`, matching R21's saved value. R22 made no geometry change. |
| **Total** | **8.6/11 = 7.8/10** | **Below threshold** |

## Did R22 resolve the prior deductions?

**No.** R22 adds two useful, primary Purdue Archives photographs and a source trail to the CERIAS plan-overlay figure. The photos strengthen visual evidence for the brick-and-coping vocabulary and confirm that some facades have broad opaque masonry interruptions rather than continuous window ribbons. They still cannot identify which exact GIS edge is pictured or supply measured opening positions. The low-resolution overlay shows a plausible plan-to-aerial relationship but is not a reusable registration because its control, direction, level, and residual are absent. Neither source resolves roof/L5 height or current circulation.

Because R22 did not change the saved geometry and none of its new sources closes those gaps, the full-building grade remains **7.8/10**, the same as R21. The R22 sources improve the documentation but do not justify a grade increase or new geometry claims.

## Evidence reviewed

- **Purdue Archives, PPBUC01785 / item 1125:** [catalog record](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1125/), raw API metadata `purdue_archives_item_1125_r22.json`, image `purdue_archives_knoy_exterior_1125_r22.jpg`. Undated original image; catalog decade 1990s/2000s. Shows stepped brick masses, light coping, low glazing strip, and brick interruptions. No camera pose/scale or face ID.
- **Purdue Archives, PPBUC01786 / item 1126:** [catalog record](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1126/), raw API metadata `purdue_archives_item_1126_r22.json`, winter image `purdue_archives_knoy_exterior_winter_1126_r22.jpg`. Undated catalog decade 1990s/2000s; supports a tall brick volume with interrupted slit windows and stepped coping. No georeference or measured elevation.
- **CERIAS 2012 report:** [source PDF](https://www.cerias.purdue.edu/assets/pdf/bibtex_archive/2012-07.pdf), local copy `source_knoy_r22_cerias_report.pdf`, pp. 74–76; Figure 3.3 at PDF p. 76 and its crop `source_knoy_r22_cerias_knoy_plan_crop.png`. The figure is an approximate plan-on-aerial overlay, but the reproduced plan is low resolution and has no documented tie-point coordinates or accuracy. It is not adequate for tracing dimensions or circulation into this model.
- **Purdue 2018 Gateway Formation Study:** floor intervals and elevations discussed in earlier review/evidence records; [source PDF](https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf). L1–L4 intervals provide useful planning-level context; no measured roof profile or facade-opening schedule.
- **R21 saved-file validation:** `validation_round21.json`; R22 independent reopen and hash are recorded in the scorecard. The geometry and transforms match R21 exactly.
- **Model renders:** `knoy_exterior_full_r17.png`, `knoy_entrance_facade_r17.png`, and the R13 spatial interior plan renders. The exterior remains a generalized, repetitive facade; interior circulation and basement alignment retain documented uncertainty.

## Decision

R22 is a useful source-research pass, not a model-fidelity revision. Keep the remaining height/roof, face-specific glazing, and interior-circulation claims uncertain. To improve the score defensibly, obtain the original high-resolution plan or an authorized measured elevation/roof plan with levels and orientation, then register it to the GIS footprint before changing geometry.
