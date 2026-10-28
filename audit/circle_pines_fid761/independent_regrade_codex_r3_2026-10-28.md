# Circle Pines FID 761 — independent R3 grade

**Reviewed asset SHA-256:** `D21277A85B16C4E6A271785280EE311104D19D7E489D9034E3D0F896267AD21E`  
**Result:** **7.8/10 — FAIL** (pass threshold: 8.0)  
**Review date:** 2026-10-28  
**Mode:** Read-only review of exact saved R3 asset and evidence. No asset edits.

## Weighted score

| Category | Weight | Score / 10 | Weighted points |
|---|---:|---:|---:|
| Identity and provenance | 20% | 9.0 | 1.800 |
| Plan geometry and placement | 25% | 9.4 | 2.350 |
| Exterior silhouette and openings | 25% | 5.8 | 1.450 |
| Materials and facade | 10% | 6.3 | 0.630 |
| Interior and cutaway | 10% | 6.9 | 0.690 |
| Presentation and technical | 10% | 8.7 | 0.870 |
| **Total** | **100%** |  | **7.790 → 7.8 — FAIL** |

## Findings

The exact R3 hash matches the coordinator's requested SHA. The primary identity chain remains strong: official Purdue GIS FID 761 names Circle Pines at 1000 David Ross Road, corroborated by Purdue FSCL and BoilerLink. The 44-vertex outline is retained, with a reported 0.0000305 m maximum error against the same transformed source ring. That match is by construction under the project's approximate transform, not independent placement or survey validation. The OSM polygon is appropriately secondary because it is less congruent and unnamed.

R3 improves the saved render. The neutral material no longer reads as unsupported siding, and the soft fill makes the low shell easier to read. Technical evidence remains strong: fresh-open passes in Blender 5.2.3 LTS, one mesh object, no external image dependencies, and a documented source outline. The 3D cutaway has floor zones, low partitions, a circulation strip, a short step run and generic furniture, while the plan labels the layout not as built. These are useful presentation improvements over R2.

The overall score remains below 8 because the exterior is still a plain low mass with a thin planar cap and no sourced openings, entry, roof style or cladding. R3 found no attributable current exterior photograph or elevation. The neutral placeholder is a sound evidence-based choice, but it leaves architectural identity and silhouette largely unrepresented. The 1954–55 yearbook page is correctly retained only as historic context: it does not establish continuity with the current FID 761 structure, so its porch imagery cannot support current facade geometry.

## Work needed to reach 8/10

- Find an attributable current exterior photo or elevation. Record provider, URL, source/capture date if known, and retrieval date; then model only visible details supported by it.
- If no current facade source becomes available, preserve the conservative placeholder and document that the missing exterior evidence is the limiting grade factor. Do not transfer the historical porch to the current building without continuity evidence.
- Interior remains schematic; use a verified floor plan or interior image before asserting rooms or circulation.

The asset SHA was verified unchanged during review. No Circle Pines asset, evidence packet or shared file was modified.
