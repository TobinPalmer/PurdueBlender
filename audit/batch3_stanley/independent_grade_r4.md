# Independent grade — Stanley Coulter Hall R4

**Result: 7.6/10 — below the 8.0/10 pass threshold.**  
**Asset SHA-256:** `40c1b209881cc7eaba71b1cb0057dc6d735751dd81bf2142ba5b3e4838f03a13`  
**Independent fresh reopen:** Blender 5.2.3; 825 objects, 815 meshes, identity asset root, no materialless meshes, and no missing external images. Evidence: `independent_reopen_r4.json`.

The all-object bound reaches 21.35 m because the saved collection also contains 47 high roof/dormer/chimney/HVAC option meshes. An independent check found all 47 disabled for rendering and hidden in the viewport (`hide_get`); visible geometry tops at 15.84 m. I report both bounds in the reopen evidence so the hidden options are not mistaken for the rendered building height. This does not resolve the unsupported actual roof-height estimate.

## Scorecard

| Criterion | Score | Findings |
|---|---:|---|
| Identity and full GIS footprint | 1.9/2.0 | The asset is recognizably Stanley Coulter Hall. Official Purdue ArcGIS FID 56 is identified by name. I independently recomputed the full-ring polygon intersection from the preserved source ring and the asset foundation vertices: all 12 vertices agree, IoU 0.999999899, symmetric difference 0.000286 m², and Hausdorff distance 0.0000045 m in the project’s approximate local frame. This is a strong map-outline match, but it is not a surveyed wall line or 3D validation. |
| Placement, orientation, and asset scale | 1.6/2.0 | Independent reopen confirms the expected exported collection and an identity local root. The evidence preserves the established manifest origin. The current master placement marker was not independently reopened, so actual assembled-campus placement is still unverified in this review. |
| Floors, height, and roof form | 1.2/2.0 | R4 corrected the cornice/eave junction and reduced the cornice depth, and the undated Archives image supports a broad low hipped roof historically. The saved hero still shows a large, nearly featureless dark roof and a broad continuous pale eave. No current measured elevation, roof plan, or height evidence supports the current profile or 15.78 m top. The historic image does not establish the current roof. |
| Facade, entrance, and materials | 1.25/2.0 | The brick, pale stone, and blue-green glazing resemble the current Purdue photo at a broad level; R4 removed floating frame faces, widened east-side openings, and improved trim/materials. The main entrance remains the biggest mismatch: the model presents a wide, full-width triangular portico with a row of columns, while the cited current photo shows a much narrower, tall rectangular limestone surround, an arched glazed transom, and two slender columns at the doorway. The model’s window rhythm is still highly repetitive and evenly spaced compared with the grouped openings and distinct upper glazing band in the photo. Roof, stone, and glazing read as relatively flat in the hero render; the entry render does not make the reported stair rails clearly legible. |
| Saved asset, interior, evidence, and portability | 1.65/2.0 | The exact R4 file independently reopens with 825 collection objects, complete mesh material assignment, and no missing external images. Provenance and uncertainties are unusually explicit, and the schematic cutaway is reviewable. Forty-seven high roof-option meshes are in the collection but hidden from render and viewport; the render-visible bound is 15.84 m. The cutaway is a sparse single-room arrangement without a legible circulation/core or multi-level interior; historical plans and broad current-use descriptions do not verify the modeled room layout. The interior must remain labeled schematic. |
| **Total** | **7.6/10** | **Does not meet the 8.0/10 acceptance threshold.** |

## Corrections needed for another review

1. Rework the main entrance against the current Purdue CLA photo. Reduce the full-width triangular portico to the supported narrow stone-framed entrance; show the arched transom, recessed double doors, and two slender supports. Keep dimensions qualitative unless a measured elevation is found.
2. Improve the front elevation’s window-group rhythm and upper glazed band so it follows the current photo rather than a uniform grid. Keep the GIS foundation and asset root unchanged.
3. Make the roof and eave read as a plausible low hipped roof without a blank dark slab. The undated historical image is supporting context only; continue to label current roof construction and height as estimates.
4. Add supported material depth to the pale stone, glazing, and roof. The brick shader is recognizable, but the hero render remains clean and repetitive; remove or explain the two bright white fixtures flanking the entry, which compete with the doorway in the current render.
5. Refine the interior cutaway so its partitions, door openings, floor relationship, and circulation are readable. Keep all room locations and furnishings explicitly schematic until current plans or photos support them.
6. After the next asset revision, repeat the fresh reopen check and retain the full FID 56 ring comparison. The coordinator still needs to reopen the master and verify the `Placement_stanley_coulter_hall` marker separately before integration.

## Sources and limits

- Purdue College of Liberal Arts, current exterior snapshot, retrieved 2026-10-25: `https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg`. The page does not expose the image date. It supports facade appearance and entrance composition, not dimensions.
- Purdue Archives and Special Collections, PPBUC01117, undated historic image (record digitized 2006-12-01): `https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/`. It supports historic massing/roof context only; the photo is not evidence of current roof form.
- Official Purdue ArcGIS BuildingShapesZip4, FID 56, `Stanley Coulter Hall`; local source snapshot dated 2026-10-22, retrieved 2026-10-25. The documented local conversion is approximate, not a certified survey.
- Purdue’s 2025 renovation story supports broad current uses (graduate student hub, English department main office, offices and research labs), not room-by-room layout: `https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/`.
- 2022 Board of Trustees renovation plans provide historical project layouts, not confirmation of the current as-built interior.
- Google Maps satellite imagery is documented in the builder’s evidence, but its capture date was not exposed; the opened Street View panorama was an indoor panorama and was not used as exterior dimensional evidence.

The footprint score was independently recomputed from `source_gis_fid56_r3.json` and the 12 bottom vertices in `asset_foundation_vertices_r3.json` using Shapely 2.2.0. The exact calculation is recorded in `independent_grade_r4.json`; the result matches the builder’s reported comparison to floating-point precision.

The 7.6 score reflects the model’s real improvements from R1 and R2 but does not let an almost exact foundation outline compensate for the clear entrance and facade differences. Roof and height remain estimated; interior geometry is schematic; current master placement was not reviewed here.
