# Independent Review — Mathematical Sciences Building (MATH)

**Reviewer:** independent secondary review  
**Date:** 2026-10-23  
**Asset:** `modular/buildings/math_sciences.blend`  
**Export:** `Asset_math_sciences`  
**Result:** **6.5/10 — not at the requested 9/10 threshold**

This review inspects the saved, reopened asset and the submitted exterior/interior renders, opening checks, plan sheet, current Purdue Libraries photo, Purdue Statistics exterior photo, official GIS footprint metadata, and the Google Maps place page. No asset or master edits were made.

## Scores

| Criterion | Score | Finding |
|---|---:|---|
| Identity and map placement | 8.5/10 | Correct building/address. Saved placement and asset envelope line up closely with FID 227's public GIS envelope. The Google Maps pin identifies the building and address, but is not a surveyed entrance coordinate. |
| Footprint and scale | 7.5/10 | Existing local frame, unit scale, and GIS-derived shell were preserved. The saved bounds are close to the GIS AABB. This is a bounds check, not a polygon-overlap or surveyed-dimension check. |
| Exterior architecture | 6.5/10 | The new east and south walls have visible repeated windows, reveals, mullions, piers, and a glazed entrance. Reference photo supports brick, narrow vertical windows, and pale framing. Only two elevations received this treatment; exact bay rhythm, height, entrance location, roof equipment, and the other elevations remain unverified. |
| Materials and texturing | 6.0/10 | Brick, glazing, stone, metal, carpet, oak, and book colors are assigned. In `exterior_after.png` the brick reads unusually dark and its brick courses are not clearly legible at this render exposure/scale. The references show lighter red-brown masonry with pronounced pale vertical members. Materials are plausible but not yet visually matched. |
| Interior and circulation | 4.2/10 | The model includes the library carpet, 6 carrels, 2 group tables with 8 seats, 3 bookcase runs, room 352, and schematic stairs/elevators. The 2025 photo supports the type of furniture and the testing room, but not these quantities or placements. The 2022 plan shows a much more articulated third-floor layout and circulation; the render is a sparse, largely open floor with no modeled boundaries for the additional group-study rooms. Nine upper slabs are estimates, with no office layouts, services, or verified circulation. |
| File and evidence hygiene | 8.5/10 | The asset reopens, keeps `Asset_math_sciences`, uses project materials without external image paths, records source uncertainty, and includes a saved render and geometry check. The ray test verifies clear samples at 81 assumed pane centers and solid hits at six control samples; it does not validate every window's dimensions, glazing, frame alignment, or all façade geometry. |

## Specific checks and discrepancies

- The saved manifest reports a local envelope of X `[-18.815, 18.040]` m and Y `[-33.964, 33.805]` m, translated by marker `[-181.120, -126.905]` m. The resulting world bounds closely match the official FID 227 GIS AABB: west/north/south limits agree to about 0.004 m or less; the east limit differs by about 0.17 m. This supports horizontal registration and scale at the bounding-box level. The GIS is a public campus building polygon, not a certified survey.
- The asset keeps zero model rotation in its existing local frame per the batch evidence. No independent structural polygon IoU, measured dimensions, or height survey is supplied. Treat plan shape as inherited/preserved, not independently verified by this review.
- The Purdue Statistics photo (`audit/next_math/reference.jpg`) shows red-brown brick, prominent pale vertical framing, repeated tall windows, and a glazed ground-level entrance. The exterior render reproduces the broad material pattern and window repetition, but the new modeled elevations still look like simple brick planes with inset rectangular panes and limited façade articulation. Exact bay count and proportions cannot be extracted confidently from this single oblique, tree-obscured photo.
- The exterior render itself is dark. The brick is close to deep brown/maroon while the reference reads lighter red-brown. Review shader color under neutral daylight before treating the current finish as matched. The procedural texture does not show clearly legible mortar courses in the supplied render.
- The 2022 Board plan marks 2,884 GSF affected and shows the third-floor library within a larger set of rooms and core/corridor spaces. The library render isolates a large uninterrupted floor and a small amount of furniture; it does not show a convincing plan-defined library boundary or the surrounding circulation. This reads as a furniture vignette rather than a reconstructed floor plan.
- Purdue's 2025 reopening article confirms refreshed carpet, upgraded furniture, rearranged shelving, additional group-study rooms, and a small windowless room 352 with a desktop. The modeled room 352's exact position and dimensions, furniture counts, shelf layout, and group-room arrangement are inferred. No current measured interior plan was found in the evidence package.
- The 2022 plan is a renovation proposal/plan sheet, not proof of the current post-2025 furniture arrangement. The 2025 article/photo is stronger evidence for current furniture/material types, but does not publish a dimensioned as-built layout.
- Google Maps currently labels the place “Mathematical Sciences Bldg” at 150 N University St, West Lafayette, IN 47907. This verifies the identity and map context. The Maps place pin does not validate the modeled east entrance center; the 1.1 m pin-to-portal comparison recorded by the builder should be treated as contextual only.
- The exterior image shows a narrow rear/south end window grid with 3 bays and no source dimension. This is an estimate from an oblique photo; the check only confirms holes at generated sample positions.
- The entrance has a canopy and glass portal but no visible steps, landing, handrails, signage lettering, or adjacent site connections in the render. These may exist in inherited geometry; the supplied render does not establish them as accurate.

## Evidence inspected

- Saved asset and render/check records: `modular/buildings/math_sciences.blend`; `audit/batch3_math/exterior_after.png`; `audit/batch3_math/library_after.png`; `audit/batch3_math/geometry_checks.json`; `audit/batch3_math/changes.json`.
- Purdue Statistics exterior photograph (source date unknown): https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg ; local copy: `audit/next_math/reference.jpg`.
- Purdue Board of Trustees, *Libraries Study Space Renovation*, Exhibit B, MATH third-floor plan, 2022-09-28: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf ; inspected image: `audit/batch3_math/plan_third_floor.png`.
- Purdue Libraries current reopening article, 2025-09-09: https://blogs.lib.purdue.edu/news/2025/09/09/mathematical-sciences-library-math-partially-reopened-with-refresh-and-a-new-testing-room/ ; inspected photo: `audit/batch3_math/library_2025.jpg`.
- Google Maps place, address and current map context: https://www.google.com/maps/place/Purdue+Mathematical+Sciences+Building/@40.4261348,-86.915642,17z/ . The page resolved to 150 N University St; map imagery/photos were not used to assert measured dimensions.
- Purdue GIS BuildingShapes FeatureServer, feature 227, EPSG:4326, retrieved 2026-10-22: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0 . Compared the manifest's saved world bounds with feature AABB only.
- Purdue Archives building history / story count: https://archives.lib.purdue.edu/agents/corporate_entities/672 . It identifies the ten-story MATH building; it does not verify the modeled 33.2 m wall top or 42.9 m maximum roof/mast extent.

## Work still needed to reach 9/10

1. Improve the exterior material match under a neutral, brighter lighting setup and make brick coursing, pale vertical bands, and window proportions read like the reference.
2. Review all four elevations against current Google Maps/street-level imagery or additional Purdue photographs; add only details supported by those views. Verify the entry's actual location and surrounding ground-level structure.
3. Match the 2025 library at the level supported by evidence: define the actual library footprint within the floor, model its circulation and group-study-room boundaries, and rework shelf/carrel quantities and locations where a current plan/photo supports them.
4. Confirm glazing and frame geometry directly, and replace the six-control-sample wall test with an opening/frame check across all façade objects.
5. Keep the nine upper slabs and 33.2 m/42.9 m heights labeled estimated until dimensioned elevation or survey data is found.

**Final independent verdict:** the saved work is a useful, textured exterior/interior visual upgrade with a strong opening check and good retained map envelope. Its current library layout is illustrative, the elevation/height evidence is incomplete, and the façade/material match remains moderate. It does **not** meet 9/10.
