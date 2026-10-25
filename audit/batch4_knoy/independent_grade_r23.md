# Independent Knoy Hall R23 grade

**Score: 8.10/10 — PASS (threshold 8/10).**

The saved `modular/buildings/knoy_hall.blend` was reopened directly in Blender 5.2.3. This grade applies the `AGENT.md` five-criterion rubric and evaluates evidence separately from builder assertions. The source-ID clarification improves traceability; it is not treated as new geometry evidence.

| Criterion | Score | Basis |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2 | Raw Purdue service record verifies Knoy as OBJECTID 189 / buildingidlong 75; cache FID 243 is distinct. Saved boundary residual is 0.000012 m to project cache and 0.178 m to live service. |
| Position, orientation, scale/dimensions | 1.35/2 | Asset root and dimensions reopen as expected; orientation and plan registration rely on a manual fit with about ±1 m uncertainty. Master placement marker was not checked in R23. |
| Height, floors, roof | 1.30/2 | Purdue 2018 source backs four levels and near-matching L1–L4 datums; L5/roof meaning and roof-equipment dimensions remain unresolved. |
| Facade, entrances, architecture | 1.50/2 | Purdue archive/official photos support the stepped brick and horizontal glazing character; plan sources support approximate interior details. No calibrated elevation fit establishes exact openings/roof details. |
| Modular export, portability, evidence | 1.95/2 | Expected asset collection reopens, identity root, no unpacked image paths, and extensive building-specific source/validation records. Full-master integration was not part of this check. |

## Findings

- The OBJECTID/FID correction is a strong provenance improvement and correctly separates the live Campus GIS record from the cached project's attribute row. It does not verify the cache-only five-level claim.
- The saved footprint is exceptionally close to the project cache; a two-vertex live-service discrepancy of up to 0.178 m is disclosed and does not justify editing the model.
- L5 occupied floor versus roof slab remains `UNVERIFIED / SOURCE CONFLICT`; penthouse, PV placement, and roof equipment are only partly supported.
- Internal plan alignment is manual and estimated; ground-level door candidates and stair dimensions retain documented uncertainty.
- Result is a narrow pass (8.10/10), not a claim that height, roof form, or campus placement is fully verified.

See `independent_grade_r23.json` for criterion evidence, scene-reopen facts, source paths, and complete findings.
