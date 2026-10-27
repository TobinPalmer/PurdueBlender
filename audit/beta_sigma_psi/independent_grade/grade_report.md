# Beta Sigma Psi independent grade

## Final assessment

**Score: 6.25/10 — below the 8/10 passing standard.** I reviewed the raw Purdue GIS feature, the current build evidence and renders, and the saved asset after fresh-open validation. The blend was saved at 14:45:14; fresh-open verification completed at 14:45:34, with no subsequent asset changes in this review.

| Criterion | Score | Evidence and finding |
|---|---:|---|
| Identity and source-backed footprint | 1.50/2 | GIS FID 793 names Beta Sigma Psi at 525 University St; OSM and BoilerLink corroborate the chapter/address. The modeled outline uses the 14 GIS ring vertices. However, independently projecting that ring gives about 410.6 m² and 87.9 m perimeter, while the same feature attributes report 709.8 m² and 115.6 m. Identity is credible, but the authoritative footprint size is unresolved. |
| Position, orientation, scale/dimensions | 1.50/2 | Geometry derives from GIS coordinates using the documented approximate campus conversion. There is no independent surveyed placement or orientation overlay, and the conflicting GIS size metrics prevent confident validation of plan dimensions. |
| Height, floors, roof | 1.00/2 | GIS lists one level. The 3.5 m wall height, 3.75 m eave, 6.7 m peak, and low-pitch hip roof are estimates without elevation evidence. The current preview also shows visible separation at roof eaves. |
| Facade, entrances, distinctive architecture | 0.25/2 | The preview depicts masonry, windows, and a south entry, but no current building-specific photographs or elevations support those features. Appearance alone does not verify the actual facade. |
| Modular export, portability, evidence | 2.00/2 | Fresh-open verification confirms the expected collection and single named mesh, identity object transform, positive bounds, assigned materials, no external image dependencies, and no modifiers. The evidence bundle includes GIS snapshots, build record, previews, and validation output. |

### Findings

- GIS identity is corroborated, but the GIS geometry and its area/perimeter attributes disagree materially. The correct source footprint size needs resolution before treating dimensions as verified.
- The campus transform is approximate; there is no independent survey overlay.
- One floor is supported. Height and roof geometry remain estimates.
- Facade materials, openings, entrance arrangement, and distinctive architectural features remain unsupported.
- The saved modular asset passes the fresh-open export and portability checks.

Evaluator implementation: [evaluator.py](evaluator.py). Machine-readable final result: [final_grade.json](final_grade.json). The earlier assessment is retained in [provisional_grade.json](provisional_grade.json).
