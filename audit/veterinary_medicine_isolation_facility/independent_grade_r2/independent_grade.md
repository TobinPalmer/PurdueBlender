# Veterinary Medicine Isolation Facility — Independent Grade R2

**Result: 8.5/10 — Pass** (minimum: 8/10)

I independently inspected the saved R2 asset, compared its fresh-open exterior shell against the raw Purdue GIS polygon, reviewed the source records and aerial/interior references, and reopened the file in Blender 5.2.3 LTS. The asset SHA-256 was `14fae094e5a857d6ca9f4cb8b73f619df8df003728fd6a9acc9570bce45162b5`.

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 2/2 | Correct Purdue GIS feature (FID 78); all 12 source perimeter vertices match the exterior shell within 0.000093 m. The GIS `Shape__Area` field conflicts with area derived from its own ring (849.074 m² vs 491.251 m²); the model follows the ring. |
| Position, orientation, and scale/dimensions | 2/2 | Independently projected ring centroid is within 0.000008 m of the saved asset anchor. Local bounds are 37.32 × 20.56 m. Campus-master placement was outside this standalone asset review. |
| Evidence-backed height, floors, and roof form | 1.5/2 | One-story description and aerial roof plan support a low-slope white roof and two rooftop plant masses. Total height is 4.52 m, but eave/roof elevations are estimates; GIS extrusion units and exterior elevations are unavailable. |
| Facade, entrances, and distinctive architecture | 1/2 | R2 includes a service-door opening and leaf plus interior stall/access details. The exterior door location is inferred. No exterior windows or facade elevations are supported by the available views. The rendered exterior remains visually plain, with little facade articulation and flat color materials. |
| Modular export, portability, and complete evidence | 2/2 | Fresh open succeeds; the expected named scene and collection contain 145 meshes and 8 materials. No external image or linked-library dependencies and no materialless meshes were found. Building-specific evidence, previews, and validation are present. |

## Findings and uncertainty

- The GIS footprint and anchor are reproduced with very small geometric error.
- The official GIS area attribute is inconsistent with the area computed from the feature's own coordinates. Published facility areas are closer to the coordinate-derived result, but do not resolve the discrepancy.
- The roof plan and single-story form are supported. Height is not measured; the model documents it as an estimate.
- The service door fills the prior exterior-access gap, but its precise position remains an inference from the paved approach and facility use.
- The exterior is still generic in appearance. More target-specific exterior photos or elevations would be needed to add facade details responsibly.
- This grade does not assess master-file linking, campus-context placement, or surrounding buildings.

## Reproduction artifacts

- `evaluator.py` implements the five-point-category rubric and writes `result.json`.
- `result.json` contains the score, threshold, per-criterion evidence, asset hash, and findings.
- `fresh_open_probe.json` records the successful standalone Blender open and portability scan.
- `gis_comparison.json` records source-ring, anchor, and shell measurements.
- `exterior_material_render.png` is the independent exterior material render used in visual review.
