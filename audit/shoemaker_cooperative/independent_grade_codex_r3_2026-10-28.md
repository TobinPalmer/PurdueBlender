# Shoemaker Cooperative FID 800 — independent R3 exact-SHA grade

**Reviewed asset SHA-256:** `7DC9A6D7E32C0E1E788157200D98209CEF5322F9617CFBEC144259AC1EB975EB`  
**Result:** **8.3/10 — PASS** (threshold: 8.0/10)  
**Review date:** 2026-10-28  
**Mode:** Read-only exact-SHA review.

I verified the on-disk blend SHA against `review_r3.md` and `evidence.json`, then reviewed the source-owner photo, exterior preview, interior cutaway, evidence packet, and fresh-open validation. No Shoemaker asset or shared file was modified.

## Weighted score

| Category | Weight | Score / 10 | Weighted points |
|---|---:|---:|---:|
| Identity and provenance | 20% | 9.2 | 1.840 |
| Plan geometry and placement | 25% | 8.8 | 2.200 |
| Exterior silhouette and openings | 25% | 8.1 | 2.025 |
| Materials and facade | 10% | 7.8 | 0.780 |
| Interior usefulness | 10% | 6.5 | 0.650 |
| Technical and presentation | 10% | 8.5 | 0.850 |
| **Weighted total** | **100%** |  | **8.345 → 8.3 — PASS** |

## Findings

- **Identity and provenance (9.2):** Purdue GIS FID 800 identifies Shoemaker at 351 Northwestern Avenue. The cooperative's own site gives the same address and supplies a 2016-dated exterior photo and a Floor Two tour; Purdue Archives and FSCL corroborate identity. The report clearly distinguishes what the operator image supports from what it cannot establish: scale, bearing, exact colors, dimensions, and unseen sides.
- **Plan geometry and placement (8.8):** The full ten-vertex official GIS polygon is used as the structural shell base, and the fresh-open vertex discrepancy is only about 0.000014 m after the project local transform. This verifies preservation by construction, not independent survey accuracy or campus position. The source polygon's positional uncertainty is unpublished. The estimate and measured evidence are separated clearly.
- **Exterior silhouette and openings (8.1):** The exterior render shows a two-level gabled mass with a broad gable facade, three gable vents, two rows of sash windows with dark shutters, a corner balcony/porch, and a shallow canopy. These are identifiable in the operator's monochrome photograph. The model generalizes a partial oblique photo into a whole footprint roof and massing; the ridge axis, roof wings, facade bearing, and unseen sides remain estimates. It does not claim the image to be georeferenced.
- **Materials and facade (7.8):** Light plaster-like walls, darker shutters/trim, glazing, and a dark roof provide clear separation and read consistently with a monochrome light-wall/dark-trim reference. Exact wall and roof colors are not supported by that image, and the model appropriately labels them as estimates. Procedural texture is restrained and does not undermine the massing read.
- **Interior usefulness (6.5):** The roof/floor-hidden cutaway exposes a two-level corridor and partition scheme with doorway gaps. It is legible as a spatial schematic and is not presented as as-built. The supplied view is sparse: it has little floor/context, no clear room labels, and no furnished cues, so it provides limited practical understanding of the ten rooms or common spaces mentioned by the operator. No floor plan exists, so those details should remain unasserted.
- **Technical and presentation (8.5):** Blender 5.2.3 fresh-open validation passes with the expected collection and one mesh object, 2,692 vertices, 1,911 faces, ten procedural materials, and no external image dependencies. The exterior is cleanly framed and the cutaway is assessable. The 44 boundary/nonmanifold edges are consistent with an intentionally open shell; future mesh consumers should know the model is not watertight.

## Limits and remaining improvement

The official GIS record says `NUM_LEVELS=1`, while the operator page/photo supports two above-grade window rows and a Floor Two tour. The counting convention is unresolved. Eaves/ridge heights, facade orientation, roof wings, porch dimensions, window spacing, colors, and all interior partitions remain estimated or schematic. No as-built plan or independent placement check was found.

The asset meets the 8/10 massing threshold. A future revision could make the interior view more useful with simple floor-zone fills and labels marked schematic, and add a second close exterior view; neither is required to pass this exact-SHA grade. This pass applies only to SHA `7DC9A6D7E32C0E1E788157200D98209CEF5322F9617CFBEC144259AC1EB975EB`.
