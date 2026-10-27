# Independent grade — West Lafayette Intermediate School r2

**Result: 7.60/10 — does not pass the 8.0 threshold.** The asset reopened successfully in Blender 5.2.3 LTS, and its SHA-256 exactly matches the requested frozen revision: `17e0af212022641e2e14d69df022dcf3b407366aa9ddf6e34a12926bfc98304a`.

## Scores

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed GIS footprint | 1.50/1.50 | Correct school/address and excellent match to the 45-node OSM outline. |
| Campus placement and scale | 1.40/1.50 | Plan placement is convincing; project transform and heights are not survey controlled. |
| Roof form and vertical massing | 0.95/1.50 | Major school volumes exist, but the roof reads more orthogonal/simple than the diagonal crossing wings and southeastern complex in the aerial. |
| Facade and recognizable architecture | 1.05/1.50 | Brick, glazing, light panels, and red steel are present; entry canopy, clerestory, and facade proportions remain simplified. |
| Source-supported classroom and gym interior | 0.55/1.50 | Furniture and gym features are present, but 18 of 36 classroom centers calculate outside the source footprint and are visible in exterior/courtyard openings. |
| Materials, texture, and portability | 1.25/1.50 | Portable procedural material graphs with no external image dependencies; several surfaces remain very flat. |
| Evidence and handoff quality | 0.90/1.00 | Strong identity/architecture evidence and honest limitations; no measured elevations or floor plan. |

## Independent file and geometry checks

- Fresh process: Blender 5.2.3 LTS opened the exact `.blend`; expected scene and asset collection were present.
- Asset SHA-256: `17e0af212022641e2e14d69df022dcf3b407366aa9ddf6e34a12926bfc98304a` (626,768 bytes).
- Scene collection: 1,667 objects, 1,655 meshes, 13,359 vertices, 9,966 polygons.
- OSM way 772742586 is named West Lafayette Intermediate School at 1838 North Salisbury Street. The modeled shell has 45 unique base vertices and matches all source points with maximum nearest-vertex error 0.000061 m. Shell topology has no boundary, nonmanifold, or zero-area faces.
- Overall bounds are X 26.05–196.21 m, Y 1855.66–2020.78 m, Z 0–12.20 m. Heights are estimates; no measured elevation was found.
- All 14 materials reopen as native material node graphs. Brick, metal panel, and terrazzo have procedural texture nodes. There are no external image dependencies.
- The 36 inferred classroom centers were recomputed from the builder's ray layout against the OSM polygon: 18 inside, 18 outside. Outside IDs: 13–24, 29–32, 34, 36.

## Visual/source review

Reviewed every r2 render: aerial, main entry, northwest, gym exterior, interior cutaway, classroom interior, and gym interior. Also reviewed the archived Esri aerial and architect project photographs for the entry, classroom, and gym. The references support school identity, the broad wings/program, brick/glazing/red-steel visual language, classrooms, and gym. The model includes these motifs but simplifies the characteristic roof plan and entrance. Interior room placement is speculative; the detected out-of-footprint centers make part of the interior visibly spill into open site/courtyard space.

## Required fixes to reach a pass

1. Reposition or rebuild the 18 classroom bays outside the footprint, then validate every classroom envelope and its furniture against the GIS shell.
2. Refine the roof plan to show two long diagonal classroom wings crossing and the irregular southeastern gym/multipurpose cluster. Keep unmeasured heights labeled as estimates.
3. Refine the entry canopy and clerestory/facade proportions from the architect photo; reconsider dark gym fins that are not supported by the available references.
4. Provide a legible classroom interior render with real room boundaries, and a richer gym interior view with the supported trusses, bleachers, and court-side walls.

Structured rubric and source findings are in `result.json` and `fresh_open_findings.json`. The evaluator is `evaluate.py`; the independent fresh-open script/log are `inspect_asset.py` and `blender_fresh_open.log`.
