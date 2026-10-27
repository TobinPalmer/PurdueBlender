# Independent grade — Von’s Shops

**Score: 8.35/10 — PASS**

Asset: `modular/buildings/massing_von_s_d207e41.blend`  
SHA-256: `4c2715c05d93ec977e878a231355fe465268d7ab32be798ff12262cfb92a0f76`  
Fresh-open: `PASS` in Blender 5.2.3 LTS

## Criterion scores

### Correct identity and source-backed footprint — 2.00/2.0
Identity and assigned-building footprint are strongly supported by the named mapped feature and address cross-check.
- OSM way 116427236 is explicitly tagged name=Von’s, building=retail.
- Von’s official Business Info page lists 315 W State St; the official history page describes the main purchased building as retail with apartments on upper floors.
- The assigned asset preserves the exact eight unique projected OSM boundary vertices; independent fresh-open measurement found 0.000000 m nearest XY error for every vertex.

### Position, orientation, and plan dimensions — 1.95/2.0
GIS plan registration is exact; the aggregate rendered bounds extend approximately 0.14 m beyond the mapped outline due to model details.
- The model remains in campus-world coordinates with an identity transform.
- All eight OSM ring vertices are present in the saved mesh base at exact projected coordinates.
- Source bounds are X 390.010–433.611 m, Y -416.933–-389.306 m; total model bounds include facade/trim details extending to X 389.870–433.754 m and Y -417.074–-389.165 m.

### Evidence-backed height, floors, and roof form — 1.20/2.0
Mixed retail and upper-floor use is source-supported, but the modeled vertical dimensions and flat parapet roof are not measured or independently verified.
- Official Von’s history supports apartments on upper floors in the main building.
- The 8.45 m parapet, two-level facade rhythm, flat roof, and exact floor heights are explicitly labeled schematic estimates; no measured elevation or roof plan was found.
- A secondary parcel summary reportedly describes a one-story assessment, so floor count/parcel coverage remains a source conflict.

### Facade, entrances, and distinctive architecture — 1.45/2.0
Distinctive brick and mural references are captured, but the facade remains schematic and the rendered entry/opening rhythm is simplified.
- The official storefront photograph supports red brick, a hand-painted Von’s Shops department mural, small openings, and a window AC unit.
- Reviewed renders show warm procedural brick, storefront glazing, upper windows, parapet, mural text/color bands, and AC detail.
- The model uses regular illustrative window spacing and a simplified retail entry; only a limited facade photo exists, so exact opening rhythm, entry position, and unseen elevations cannot be verified.

### Modular export, portability, and complete evidence — 1.75/2.0
Portable, textured, correctly named, and well documented; open-surface topology reduces geometry robustness. No verified interior plan exists, so omission is not penalized.
- Independent Blender 5.2.3 fresh-open passed with the expected scene, collection, one root mesh, and exact SHA.
- The mesh has 15,864 vertices and 11,732 faces, two UV layers, 13 named procedural materials, and no unpacked external images.
- The evidence records GIS/provider/feature ID/CRS/transform/uncertainty, official identity and facade references, four review renders, and explains why no interior was modeled.
- Topology audit found 14,872 boundary and non-manifold edges (no zero-area faces); the joined visual asset is not a closed watertight solid.

## Independent geometry and portability checks

- OSM ring vertices found: 8; maximum XY error: 0.000000 m.
- Object/mesh: 1 scene object; 15,864 vertices; 11,732 faces.
- Materials/UVs: 13 materials; Facade_Meters, UVMap.
- Unpacked external images: 0.
- Boundary/non-manifold edges: 14,872; zero-area faces: 0.

## Overall finding

The model is an appropriately portable and well-registered visual representation of the assigned Von’s building. It earns a passing score based on exact footprint registration, identity cross-checks, photo-supported brick/mural cues, a fresh-open library, and documented uncertainty. Its main limitations are the unverified roof/heights/facade rhythm and a high open-surface edge count. No interior plan was found, so not inventing one is acceptable.
