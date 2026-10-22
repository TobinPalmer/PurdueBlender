# East building finishing pass — 2026-10-22

Changed source libraries WALC, Potter, Mechanical Engineering, and Brown Family Hall of Electrical Engineering. Master and manifest were not edited.

## Concrete corrections

Potter, ME and BHEE previously used whole-volume limestone band solids directly overlaid on structural solid envelopes. Their exterior surfaces were coplanar and could flicker or render inconsistently. Rebuilt five structural envelopes as continuous closed meshes segmented at the existing band elevations, assigned limestone material to the appropriate side faces, and removed twenty overlapping band solids. Structural XY vertices and inherited roof elevations remain unchanged. Each reconstructed envelope reopened with zero nonmanifold edges and positive signed volume; measurements are in verification.json.

Recalculated generated shell and roof mesh normals for all four libraries. Enabled standard material nodes on generated materials which previously specified viewport color alone, preserving existing base colors so conventional render engines receive the intended colors. WALC glass remains an opaque visual representation; no physical glazing or real building elevations are certified.

Rendered before and after oblique views, then reopened all four saved files and inspected the after images. These images document topology/render cleanup, not architectural fidelity. The simplified facades and flat source-shaped roof forms remain incomplete.

## Research and uncertainty

Purdue-hosted November 2017 Potter Engineering Center Renovation Study, American Structurepoint, Part 2: https://engineering.purdue.edu/~frosch/Renderings/Masterplans/2015.02663%20--%20Potter%20Engineering%20Center%20Study%20--%20SUPPLEMENTAL%20--%20spreads.pdf . Retrieved 2026-10-22. Its existing-building description identifies brick expanses, repeated precast panels and small deeply shaded perimeter windows. Proposed renovation illustrations are not evidence that a renovation was built. No proposed facade was copied into the model. Source publication November 2017; no geospatial CRS applies to this architectural report.

Purdue emergency preparedness WALC page https://www.purdue.edu/operations/emergency-preparedness/walc/ confirms three above-ground floors and a basement. Retrieved 2026-10-22; source publication date unavailable. This supports story count but does not measure height or window arrangement.

Horizontal provenance remains the cached official GIS features in audit/official_building_references.json and prior audit/walc_east/REVIEW.md: POTR864, ME857/108, BHEE292/109, WALC906. No geographic placement change. Local coordinates and manifest origins are retained. Heights, roof shape and exact facade/window arrangements remain unverified estimates. Future facade work should obtain measured elevations or accurately registered current photographs.

Backups: each *_before.blend in this folder. Reproducible editing and checks: finish.py; verification.json. Before/after images are named by asset ID.
