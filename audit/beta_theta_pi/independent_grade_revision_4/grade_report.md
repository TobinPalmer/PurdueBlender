# Independent grade — Beta Theta Pi revision 4

**Result: 8.40/10 — passes the 8.0 threshold.** The asset SHA matches the requested frozen revision exactly: `34d0b02c5e76284e3751f1b533d6489074aced3c9eddb7f5bb006ae255957277`. I reopened it independently in Blender 5.2.3 LTS and reviewed all six `preview_r4_*.png` images, the retained GIS and chapter-house references, and the prior revision-3 findings.

## Scores

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 2.00/2.00 | FID 826, Beta Theta Pi, and 150 Littleton St are corroborated; all 19 GIS perimeter vertices match. |
| Campus placement and plan scale | 1.90/2.00 | XY placement and plan dimensions are strong; photographed facade bearing is not georegistered. |
| Roof and vertical massing | 1.45/2.00 | The shell is continuous and correctly oriented; gable intersections remain dark-looking and dimensions are photo-derived estimates. |
| Facade, entry, and photo-backed details | 1.55/2.00 | Brick, divided sash windows, projecting arched bay, front gable, dormers, arched entry, and crest give the right identity; window rhythm and doorway are simplified. |
| Portable materials, modular handoff, and evidence | 1.50/2.00 | File reopens with six self-contained node materials and no image dependencies. Evidence is traceable; procedural surfaces look mottled, and interior is omitted without a reliable public plan. |

## Independent Blender and geometry checks

- Fresh open succeeded in Blender 5.2.3 LTS. Scene `Building_massing_beta_theta_pi_fid826` and collection `Asset_massing_beta_theta_pi_fid826` are present.
- The collection contains 349 objects, all meshes. Overall world bounds: X 805.983–827.110 m, Y -417.268–-375.652 m, Z -0.12–15.00 m.
- Purdue GIS FID 826 identifies Beta Theta Pi, address 150 Littleton St. The footprint wall base contains 19 unique vertices; maximum nearest-vertex error to the transformed feature ring is 0.0000294 m (RMS 0.0000199 m).
- The continuous roof shell has 38 vertices, 73 edges, and 37 faces. It has **zero boundary edges, zero nonmanifold edges, and zero zero-area faces**. Seventeen roof-top facets point up; 19 eave sides are vertical and one underside face points down. This resolves the earlier disconnected-facet/normals failure. Across all 349 meshes, zero-area face count is zero.
- All six materials reopen as native shader-node graphs. Brick, slate, limestone, and trim have procedural texture nodes; there are no external image dependencies.
- Two west-wing dormers and their gable/roof meshes are present. The doorway close-up still reads as a pale blank block, and roof/gable intersections create dark visual seams despite the continuous watertight roof shell.

## Reference review and remaining refinements

The official Beta Mu chapter-house gallery supports the brick-and-slate palette, three visible facade levels, central front gable, pale projecting bay, divided windows, dormers, and arched entrance. Purdue’s GIS feature and campus imagery support identity and placement. The previews are recognizable and the revision fixes the principal structural roof issue from r3. Height and ridge measurements remain estimates because the available imagery is not surveyed or registered to the footprint.

For another refinement pass, clarify the dark door/transom behind the entry arch, reduce dark-looking roof intersections with cleaner lighting and fit, and adjust procedural brick/slate patterns so they read as masonry and slate courses rather than mottled noise. No interior change is required unless a reliable public plan becomes available.

Structured criteria and exact asset data: `result.json` and `fresh_open_findings.json`. Reproducible independent scripts/log: `evaluate.py`, `inspect_asset.py`, and `blender_fresh_open.log`.
