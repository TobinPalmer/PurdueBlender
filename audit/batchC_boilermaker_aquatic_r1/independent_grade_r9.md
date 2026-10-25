# Independent R9 grade — Morgan J. Burke Boilermaker Aquatic Center

**Score: 8.5/10 — passes the 8/10 threshold.**

## Asset and evidence reviewed

- Opened the saved asset read-only: `modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend`.
- SHA-256 reviewed: `136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497`. This matches `validation_r9.json` and `asset_sha256_r9.txt`.
- Read the R9 validation and source record, the raw Purdue GIS footprint snapshot (FID 896), the manifest entry, the coordinator's R9 master-placement evidence, and both R9 renders.
- Blender 5.2.3 reopened the asset. Direct inspection found the expected asset collection, 1,129 objects, 21 truss meshes, full roof visibility, 24 riser objects, 24 aisle posts, assigned mesh materials, and no external image-file dependencies.
- Reviewed R9 cutaway and bleacher aisle renders. R8 north-entry and facade renders remain relevant to exterior details carried into the R9 asset.

## Rubric

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9/2 | The Purdue GIS snapshot identifies feature FID 896, and bidirectional sampling reports only 0.000002 m between the GIS ring and the model shell. This demonstrates outline correspondence, not survey accuracy. Arsee Engineers identifies the named facility and provides qualitative interior evidence. |
| Position, orientation, and scale/dimensions | 2.0/2 | Coordinator-provided read-only master evidence gives marker translation (-808.6829834, 80.336998, 0), unit scale, and zero rotation. The manifest origin is (-808.683, 80.337); recalculated XY error is 0.00001672 m, within the requested 0.00003 m. The saved shell dimensions are 60.195 × 102.504 × 11.928 m, while the footprint match supports the plan outline. The master transform is coordinator evidence rather than a master file independently opened by this grader. |
| Evidence-backed height, floors, and roof form | 0.9/2 | The model contains a pitched-roof object and 21 schematic trusses, and the Arsee project photo qualitatively supports exposed trusses and a high-bay pool hall. No measured section or elevation validates roof profile, truss dimensions, eave/ridge heights, story count, or total height. Model dimensions are not real-building evidence. |
| Facade, entrances, and distinctive architecture | 1.8/2 | Street View supports the north brick facade, ribbon glazing, canopy, and lettering. The Arsee photo supports the pool hall, wall lettering, bleacher banks, aisle, and exposed trusses. R9 renders show connected stepped aluminum tiers, risers, aisle rails/posts, wall-mounted Purdue panels, pool/deck, and linear lighting. Exact facade dimensions and interior layouts remain schematic; the cutaway still shows a broad overhead plane with limited readable roof structure. |
| Modular export, portability, and complete evidence | 1.9/2 | The reopened file matches the manifest's stable asset path and collection, the hash records agree, materials are assigned, and there are no external image-file dependencies. The R9 evidence includes source providers, URLs, dates, CRS/method where applicable, renders, and uncertainties. Some modeled interior geometry and the coordinator-provided placement cross-check remain schematic or externally reported. |
| **Total** | **8.5/10** | **Passes.** |

## Findings and limits

- The saved R9 asset reviewed is exactly SHA-256 `136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497`.
- The marker-to-manifest placement comparison closes the placement gap noted in the R8 grade.
- Roof profile and total-height accuracy remain uncertain. The available photo supports qualitative truss presence, but there is no measured roof or elevation evidence for the modeled profile, truss layout, or eave/ridge elevations.
- The 24 risers and 24 rail posts make the bleacher and aisle presentation more coherent, but seat/tread dimensions, seating capacity layout, and accessibility compliance are not verified by an as-built plan.

The evaluator function and its complete machine-readable result are saved in `evaluate_aquatic_r9.py` and `evaluator_result_r9.json`.
