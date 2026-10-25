# Independent grade — Purdue Memorial Union R3

**Score: 7.9/10 — below the 8.0 pass threshold.**

Reviewed asset SHA-256: `a53a451a998085af0ae765fdae2c364bd709e02bd03b7169a412b181ada547cd`. The saved asset was reopened independently in Blender 5.2.3; reopen evidence is `independent_reopen_r3.json`. This review compares the R3 render set with the cited Purdue Archives 1924 and Purdue University 2024 images and the source record in `audit/purdue_memorial_union_refine/build_evidence.md`.

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 1.8/2.0 | The asset remains recognizable as PMU's tower-and-wings complex. The historic Purdue Libraries GIS phase context and immutable original bounds support the main shell. R3 freshly reopened with all 18 original wall/base bounds unchanged at 0.0 m delta; three new bases are documented as additive. |
| Placement, orientation, and scale | 1.9/2.0 | Fresh reopen confirms identity transform on AssetRoot_purdue_memorial_union. Existing read-only master marker records the expected placement at (205.75, -271.65, 0), zero rotation, unit scale. The live master was not reopened as part of this asset-only grading pass. |
| Evidence-backed height, floors, and roof form | 1.2/2.0 | R3 makes the wing roofs more legible as separate gables and adds three source-supported south-west dormers, restrained slate texture, and caps. The roof render still reads as very broad continuous planes around an oversized open courtyard, with abrupt central junctions and roof planes that compete with the tower silhouette. Height (29.5 m), floor spacing, and roof elevations remain explicitly estimated; the dated images are not measured elevations. |
| Facade rhythm, entrance, and distinctive architecture | 1.5/2.0 | The south facade now has seven arched openings with stone surrounds, a more articulated entry, multi-tier tower glazing, and a documented 4+3 window rhythm. Brick and slate are visibly textured. However, the tower's window proportions and stone field remain schematic compared with the Purdue references; relief fields are blank, repeated wing openings are sparse, and oblique renders show large unarticulated side walls. |
| Modular portability and evidence/validation | 1.5/2.0 | Independent fresh reopen confirms 630 objects, 588 meshes, identity root, no mesh without a material, and no unpacked image dependencies. R3 validation records the exact asset SHA and structural comparison. The shared manifest still describes PMU as unverified with object_count 414 and no asset hash or grade record, and master reload/integration remains pending. |

## Findings

1. Score: 7.9/10, below the 8.0 pass threshold. R3 improves facade rhythm and source-specific detail over R2 but does not resolve the roof silhouette/junction problem enough to pass.
2. Break up the broad roof planes and make the individual wing gables/eaves and courtyard transitions read cleanly from south-west and west oblique views. Preserve the footprint and identify any roof dimensions as estimates.
3. Bring tower glazing and limestone surround closer to the 2024 reference proportions; add supported articulation to the currently blank side relief panels and increase facade rhythm where supported by the 1924 photo.
4. After a passing grade, synchronize the PMU manifest object count/hash and verify the master placement on a fresh reopen. Do not treat the manifest's current count 414 as the actual R3 count of 630.

## Review limits

- Historical GIS is approximate and phase-specific; it does not prove present-day dimensions or detailed roof geometry.
- The 1924 archival and 2024 university images differ in date and viewpoint, so comparisons support qualitative facade and massing review only.
- This reviewer did not modify the PMU asset, manifest, or master file.

Machine-readable result: `independent_grade_r3.json`. Scoring function: `independent_evaluator_r3.py`.
