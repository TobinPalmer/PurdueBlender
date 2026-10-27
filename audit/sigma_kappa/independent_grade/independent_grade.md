# Sigma Kappa independent grade

**Result: 8.25 / 10 — pass (minimum 8 / 10).** I reopened the final `.blend` in Blender 5.2.3 LTS and inspected the current render, raw Purdue GIS feature 780, the Beta Sigma newsletters, Purdue Panhellenic chapter profile, and the saved Two Tulips artist drawing labeled “Sigma Kappa 427 N Russell Street.” The saved asset contains only the expected one-mesh collection; the temporary camera and light are absent.

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00 / 2 | Official Purdue GIS labels FID 780 as Sigma Kappa at 427 Russell St. Chapter newsletter confirms the house address, and Purdue Panhellenic identifies Beta Sigma. All 21 GIS vertices match the reopened mesh base within 0.000015 m. |
| Position, orientation, and scale/dimensions | 1.50 / 2 | Wall placement and footprint are GIS-registered with identity transform. The illustrative portico and steps extend about 3.34 m west of the wall envelope; roof eaves project about 0.22 m. The drawing is not georeferenced, so facade bearing remains unverified. |
| Evidence-backed height, floors, and roof | 1.25 / 2 | The drawing supports the broad two-story silhouette, twin gables, dormers, and chimney. Modeled eaves, ridge, and chimney are explicitly estimates. GIS `NUM_LEVELS=1` conflicts with the visible two-story drawing; `Extrution=12` has no published unit or meaning. |
| Facade, entrances, and distinctive architecture | 1.50 / 2 | Brick wings, centered columned portico and pediment, paired windows, twin gables, dormers, and chimney follow the labeled illustration. Window rhythm and proportions are simplified; the drawing is not a measured elevation. |
| Modular export, portability, and complete evidence | 2.00 / 2 | Expected collection contains only `House_301840869`; the asset reopens, has identity transform, and contains no external image dependencies. Raw GIS and visual sources, evidence, validation output, preview, and evaluator artifacts are included. |

The result passes the project’s minimum grade. The strongest evidence is the identity/address match and exact GIS wall footprint. Floor count, all heights, and facade direction remain uncertain because the available visual reference is a stylized, unscaled drawing and GIS vertical fields are undocumented.

Machine-readable evaluation: `result.json`; direct Blender probe: `blender_probe.json`; evaluator: `evaluate.py`.
