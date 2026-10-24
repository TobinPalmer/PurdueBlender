# Mathematical Sciences Building — Independent R11 Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Grade:** **7.9/10 — below the 8.0 target.**  
**Rubric:** Five criteria, each worth 2 points, per `AGENT.md`.  
**Scope:** Read-only independent review of the R11 evidence-only pass. The asset geometry is unchanged from R10. No building, master, or shared files were modified by this reviewer.

## Criteria

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9/2 | Purdue archive identity and GIS FID 227 support the building and horizontal footprint envelope. Shell/plinth bounds closely match the transformed GIS bounds. The documented local geographic projection and AABB comparison are approximate and do not prove every wall edge or represent survey control. |
| Position, orientation, and scale/dimensions | 1.9/2 | The retained R8 read-only master check records one `Placement_math_sciences` instance at the manifest origin within 0.02 m, with zero rotation, unit scale, and the expected relative library path. This check was not repeated against the master in R11; the model's local geographic frame remains approximate. |
| Evidence-backed height, floors, and roof form | 0.9/2 | Purdue's archive record supports a ten-story identity. The newly inspected drawing gives a qualitative flat parapet and raised rear-roof silhouette. However, the modeled shell top is 33.2 m and penthouse coping 36.5 m while the 2018 DSM-minus-DTM median is 36.92 m and p95 is 40.43 m. The 5-ft footprint-wide raster and unverified vertical datum do not identify which roof/story component causes the discrepancy. Exact height and roof form remain unverified. |
| Facade, entrances, and distinctive architecture | 1.4/2 | The archive photograph shows one largely blank end wall beside a vertically grouped window elevation; the drawing shows vertical facade bands, simple end bays, a glazed lower level, and a raised rear roof edge. These broad motifs are plausible in the saved model renders. Neither archived view has a known compass direction, date, dimensions, or confirmed as-built/current status, so the images cannot verify a specific model cardinal face, current openings, or exact entrance. The blank rendered areas therefore remain only partly verified. |
| Modular export, portability, and complete evidence | 1.8/2 | Blender 5.2.3 reopened the standalone asset with the expected collection, 550 direct/593 inclusive objects, unchanged bounds, and no unpacked external images. R11 adds structured source observations and uncertainty limits. The placement/integration check is retained from R8 rather than repeated in this review, and current elevation/interior evidence is incomplete. |
| **Total** | **7.9/10** | **Below target.** The evaluator function in `independent_review_round11_evaluate.py` sums the five criteria and saves the result to the scorecard JSON. |

## Independent review of R11 source claims

I inspected the two Purdue eArchives IIIF images directly. Item 823's visible perspective supports the statement that an end elevation was largely blank and an adjacent facade had repeated vertical window groupings. Item 824's illustration supports a qualitative vertical-band facade, simpler corner bays, glazed base, and raised rear roof silhouette. The images are undated and directionless; item 824 is an architectural drawing rather than a demonstrated as-built elevation. They are helpful historical design evidence, but cannot locate those views on the model's north/east/south/west faces, verify the current facade, or supply dimensions.

The R10 roof analysis correctly reports a meaningful discrepancy while preserving uncertainty. The raster's footprint mask includes several surface types and its 5-ft grid cannot assign the height returns to the shell, penthouse, coping, or roof equipment. The existence of public state LAS data is confirmed by the [Indiana Statewide Elevation Catalog](https://registry.opendata.aws/in-elevation/), but R11 does not identify or analyze the matching point-cloud file, so this does not resolve the roof. No roof geometry should be changed on the R11 evidence alone.

The [Purdue Archives accession record](https://archives.lib.purdue.edu/repositories/2/accessions/2685) is a concrete lead to library-move records and floor plans, but describes physical, unscanned material of uncertain provenance/date. It is not inspected interior evidence and does not establish a current as-built plan.

## Findings

- R11 strengthens historical facade evidence but does not close the direction/current-condition gap for the rendered elevations.
- The model keeps broad blank surfaces that are plausible from one historic photograph, yet the archive images do not establish which current face should be blank or windowed.
- Ten-story identity is supported; absolute roof and floor elevations remain in conflict with the 2018 DSM/DTM surface statistics.
- The library interior remains schematic relative to the public 2022 plan and 2025 article/photo; the R11 floor-plan accession is only a lead. Interior uncertainty is noted under evidence completeness, not scored as a separate AGENT.md criterion.
- `round11_validation.json` passes after Blender 5.2.3 reopened the saved asset. It confirms 550 direct/593 inclusive objects, unchanged R10 roof and shell bounds, and no unpacked image dependencies. R11 makes no geometry claim or change.

## Decision

**The asset remains below the 8.0/10 project threshold at 7.9/10.** The strongest next evidence would be a direction-identified current elevation/photo set and a measured or reliably registered roof source that resolves the shell-versus-penthouse height discrepancy. No unsupported geometry edit is recommended from the current evidence.
