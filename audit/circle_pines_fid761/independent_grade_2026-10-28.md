# Independent review — Circle Pines, FID 761

**Reviewed:** 2026-10-28  
**Asset:** `modular/buildings/massing_house_301841609_c6c9ac4.blend`  
**Verified SHA-256:** `BB8F6BDE52311FEC32979C9525EC6A6EAE29206672ECE2F07B59CD16112C4EE4`  
**Result:** **6.78/10 — FAIL** (threshold 8.0)

This is a read-only review of the frozen candidate. I independently fresh-opened the exact file in Blender 5.2.3 LTS and confirmed the expected scene, named asset collection and one mesh object (`House_301841609`), with 188 vertices, 131 faces, and bounds 49.855 × 64.392 × 4.05 m. The exact hash remained unchanged.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Basis |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.0 | 1.80 | Purdue GIS FID 761 directly identifies Circle Pines at 1000 David Ross Rd; Purdue FSCL and BoilerLink corroborate current identity/address. No attributable current facade photo, measured elevation or floor plan was supplied. |
| Plan geometry and placement | 25% | 9.4 | 2.35 | The model uses the full 44-vertex GIS ring; fresh-open reports max wall-base XY error 0.0000305 m. This is a same-source construction check using an approximate local transform, not an independent survey/placement confirmation. The OSM way is materially less congruent and is appropriately treated as secondary only. |
| Exterior silhouette and openings | 25% | 4.5 | 1.13 | The asset reads as a single low mass with a generic planar cap and only three small glazing cues. No current building photo or elevation supports the silhouette, roof, entry, window schedule, or facade composition; appearance remains almost entirely generic. |
| Materials and facade | 10% | 5.0 | 0.50 | Neutral placeholder colors are honestly described and portable. They provide no evidence of the actual building's material palette or facade construction. |
| Interior detail and cutaway clarity | 10% | 2.0 | 0.20 | The open-roof plan is a cleanly qualified diagram, but it contains only a few illustrative partition lines. The saved asset has no meaningful floor plates, room volumes, circulation/stairs, or furniture. It does not meet the project's interior-detail bar even as a schematic. No as-built plan is claimed or expected without a source. |
| Presentation and technical | 10% | 8.0 | 0.80 | Fresh-open succeeds with the expected stable single object, correct source bounds and no external dependencies. The source validation reports 44 boundary/nonmanifold edges, consistent with an open surface massing shell rather than a closed solid. The previews and limitations are clear. |
| **Total** | **100%** |  | **6.775 / 10 = 6.78/10** | **FAIL** |

## Revisions required before a passing grade

1. Add actual schematic interior geometry to the saved asset: floor areas or plates, readable room divisions, stairs/circulation, and a small amount of furniture or fixtures. Keep every room, opening and use clearly labeled as illustrative because no plan was found. Supply an open-roof cutaway render from the saved asset that shows those inserts across the full GIS footprint.
2. Obtain an attributable exterior photograph, elevation, or another reliable visual source before claiming facade fidelity. If no such source can be found, preserve the massing as a clearly unverified placeholder and avoid invented facade-specific claims; the present exterior score remains low because the deliverable itself is minimal.
3. Improve the exterior evidence/presentation with a clearly readable roof mass, entry and window rhythm only where a source supports those choices. Do not infer height from `Extrution=32`; its units and meaning remain undocumented.

## Evidence reviewed

- `review_handoff.md`, `evidence.json`, `source_record.json`, raw FID 761 GIS snapshot and `fresh_open_validation.json`.
- `exterior_preview.png`, `schematic_interior_plan.png`, and `footprint_overlay.png`.
- Exact saved asset reopened directly in Blender 5.2.3 LTS; SHA checked before and after.

No asset or shared project file was modified during this review.
