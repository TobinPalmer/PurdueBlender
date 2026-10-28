# Circle Pines FID 761 — independent R2 grade

**Reviewed asset SHA-256:** `ECD7341DDA0162B1935821B2739081B241378E4586C864CB0507A7CC049E134B`  
**Result:** **7.6/10 — FAIL** (pass threshold: 8.0)  
**Review date:** 2026-10-28  
**Mode:** Read-only review of exact saved asset and current R2 evidence. The asset was not modified.

## Weighted score

| Category | Weight | Score | Weighted points |
|---|---:|---:|---:|
| Identity and provenance | 20% | 9.0 | 1.800 |
| Plan geometry and placement | 25% | 9.4 | 2.350 |
| Exterior silhouette and openings | 25% | 5.5 | 1.375 |
| Materials and facade | 10% | 5.5 | 0.550 |
| Interior and cutaway | 10% | 6.8 | 0.680 |
| Presentation and technical | 10% | 8.5 | 0.850 |
| **Total** | **100%** |  | **7.605 → 7.6 — FAIL** |

## Findings

The exact file hash matches the requested R2 SHA. The evidence packet provides a strong identity chain: Purdue GIS FID 761 names Circle Pines at 1000 David Ross Road, with Purdue FSCL and BoilerLink corroboration. The plan comparison uses all 44 GIS ring vertices; the reported 0.0000305 m XY error is a same-source construction check under the repository's approximate conversion, not an independent survey check. The weaker unnamed OSM polygon is appropriately treated as secondary.

R2 meaningfully addresses the prior interior deficiency. The saved mesh now contains 3D schematic room floor zones, six low partition strips, a circulation band, one short stair run and generic furniture. Both cutaway and plan evidence state that the arrangement is not an as-built plan. The spatial layout and room use remain unverified, but this is a material improvement over the previous 2D-only/near-empty interior score.

The exterior remains the limiting category. The saved exterior is a low, largely blank neutral mass capped by a thin planar roof. The evidence record and source-search report state that no attributable current photograph, elevation, or other reliable architectural visual source was found. The decision not to invent windows, entry, roofing style or materials is sound, and the GIS footprint is represented accurately; however, the artifact still has little exterior detail and no source-backed facade identity. Roof/eave and total height are estimated. This keeps the overall grade below 8 despite strong identity, plan and technical scores.

Fresh-open evidence records the expected scene/collection/root, a single mesh object, no external images, and the expected geometry bounds. The 44 boundary/nonmanifold edges are consistent with the open shell representation and are disclosed in the validation report.

## Work needed for 8/10

- An attributable current exterior photograph or elevation is the key blocker. If one is found, model only details it supports and update the evidence packet with provider, URL, capture date if known, and retrieval date.
- Until such a source exists, keep the exterior neutral and unverified; do not add an unsupported roof, entry, material, or opening rhythm.
- Keep the interior explicitly schematic unless a floor plan or interior image becomes available.

The asset SHA was verified unchanged during this review. No asset or shared file was modified.
