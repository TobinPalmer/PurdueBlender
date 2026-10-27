# Alpha Sigma Phi — independent grade

**Score: 7.25/10 — below the 8/10 completion threshold.**

The model reproduces the official Purdue GIS plan extremely closely and is packaged as a clean, reopenable building asset. The score is limited by unsupported vertical/exterior interpretation: the GIS floor-count fields conflict with the modeled three-level house, the `Extrution=34` unit is undocumented, and the available street-level view does not clearly show this house's facade. The interior is a schematic arrangement, not a verified floor plan.

## Five-criterion rubric

| Criterion | Score | Evidence and finding |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.00/2 | Purdue GIS FID 763 names Alpha Sigma Phi at 951 David Ross Road. Independently reopened geometry matches all eight GIS ring vertices within 0.000062 m; the aerial overlay follows the L-shaped roof. |
| Position, orientation, and scale/dimensions | 2.00/2 | Stable scene, collection, root, campus-coordinate bounds, and plan orientation match the GIS asset. The vertical dimension is assessed under the next criterion. |
| Evidence-backed height, floors, and roof form | 0.50/2 | 10.363 m was produced by interpreting GIS `Extrution=34` as feet, but no unit is documented. GIS also reports `NUM_LEVELS=1` and `CountOfFLO=1`, conflicting with three modeled window levels. The aerial supports plan shape but not roof profile. |
| Facade, entrances, and distinctive architecture | 0.75/2 | The model includes brick, repeated windows, and a basic canopy/entry. Available Street View is partly obstructed and does not establish the target facade's exact materials, window pattern, or entrance placement. The render reads as a generic brick residence, with little verified distinctive architecture. |
| Modular export, portability, and complete evidence | 2.00/2 | Expected asset path, scene, collection, and root reopen successfully; 851 mesh objects are contained in the asset. Nine node-based materials are present; brick is procedural and no external image dependency was observed. Provenance, source snapshots, fresh-open validation, and preview renders are saved. |

## Findings to address before regrading

1. Resolve floor count and height using a clear target-facing photograph, reliable elevation, or measured source. Do not treat the GIS extrusion field as feet without evidence.
2. Improve the facade and entrance from target-specific evidence. Keep the GIS footprint as-is; it is a strong match.
3. Improve the cutaway render with a near-vertical camera, readable spaces/furnishings, and less shadow obstruction. Any room arrangement must remain labeled illustrative unless a real floor plan is found.
4. Do not present the current roof silhouette, facade color, or room layout as verified facts.

## Evidence inspected

- `result.json` and `evaluate.py`: independent Blender 5.2.3 inspection and runnable rubric evaluator.
- `../sources/arcgis_fid763_feature.json` and `../sources/esri_world_imagery_fid763_footprint_overlay.png`: official GIS feature and aerial comparison.
- `../fresh_open_validation.json`: builder's fresh-open checks, consistent with the independent geometry calculation.
- `../previews/alpha_sigma_phi_exterior.png` and `../previews/alpha_sigma_phi_interior_cutaway.png`: inspected renders.
- [Alpha Pi chapter history](https://img1.wsimg.com/blobby/go/f462eca5-24f6-4531-81f7-6819824ee6a1/CHAPTER%20HISTORY%20-%20ALPHAs.pdf): confirms chapter house address/history, not current facade detail.
- [Purdue Alumnus photo index, January 1968](https://collections.lib.purdue.edu/pupindex/search.php?fq=PublicationYear%3A%221968%22+AND+subjectStr%3A%22Fraternities%22&q=Fraternities&qtype=SubjectHeading&submit=submit): confirms a historical David Ross fraternity-row photo feature existed; the photo itself was not available in the indexed record.
- [Google Street View panorama](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.43505,-86.92572): useful current row context but partly obscures the target house.
