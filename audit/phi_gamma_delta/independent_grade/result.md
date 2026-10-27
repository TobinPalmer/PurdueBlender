# Independent grade — Phi Gamma Delta (FID 787)

**Score: 7.8/10 — revise; below the 8.0 integration threshold**  
**Exact asset SHA-256:** `F018ED70CB67BFEF0D3195C2D65B9960AF50FE3AD5600FD07F7396032C115AFA`  
**Blender:** 5.2.3 LTS; independently reopened from the saved asset.

## Score breakdown

| Category | Score | Findings |
| --- | ---: | --- |
| Site identity and source confidence | 9.0 | Purdue GIS FID 787 names Phi Gamma Delta at 640 Russell St; official chapter material confirms the house and Lyles Addition. This strongly supports identity. The GIS feature date and a surveyed wall outline are unavailable. |
| Footprint, orientation, and placement | 9.3 | The asset retains the ten-vertex GIS-derived XY outline and the fresh-open bounds are consistent with the submitted validation. This confirms the source outline was retained; it does not independently establish surveyed wall alignment. |
| Massing and architectural details | 6.8 | Three-story main house, low addition, several hipped roofs, repeated windows, stone trim, arched doors and gutters are present. The generated facade reads much more regular than the asymmetric June 2025 construction photo. The official addition view shows a more articulated lower wing with prominent arched glazing. Addition partition and roof layout remain estimates. |
| Materials and texturing | 7.2 | Buff brick, light stone, dark glazing and slate are source-supported. Ten portable node materials load without external images. Brick courses and mortar are primarily repeated geometry; the rendered surfaces lack finer color/roughness variation and remain schematic. |
| Interior and evidence handling | 7.0 | Basement and first-floor plans document spaces, but the model has no interior because their registration to the GIS/site plan was unresolved. Avoiding a guessed interior was appropriate, though the requested interior work is incomplete. No upper-floor plans were found. |
| Blender integrity and portability | 7.0 | Fresh-open passed with stable scene/collection/root names and no external image dependencies. The probe found 187 mesh objects, 14,480 edges and 12,232 boundary/non-manifold edges; many roofs and detailing pieces are open single surfaces. Good for rendered appearance, but not a clean watertight architectural model. |

**Weighted total: 7.8/10.**

## Fresh-open results

The independently computed SHA matches the builder's reported SHA. The file reopened in Blender 5.2.3 LTS. The expected scene, export collection and root mesh exist, with 187 mesh objects. Ten named, node-based materials are present and no external image paths were found. Detailed object and topology counts are recorded in `fresh_open_probe.json`.

## Evidence and remaining limits

The asset uses the named Purdue GIS FID 787 outline. The construction photo directly supports the buff brick, low dark roof, repeated but asymmetric window openings and arched entries. The 2024 official concept views support the Lyles Addition relationship and palette. These images are useful visual references but are not calibrated elevations; precise opening positions, dimensions and hidden sides remain uncertain. The building plans document the basement and first-floor program but are not yet registered to the model.

## Recommendation

Do not integrate this revision yet. Register the available plans to the site/GIS frame, add only supported basement/first-floor interior features, and revise the asymmetric facade and lower addition from the exact building photos/renderings. Improve material-scale variation and recheck roof boundaries. Then run a fresh-open and topology review against the new saved SHA.
