# Sigma Kappa FID 780 — independent R2 exact-SHA regrade

**Result: 8.1/10 — PASS** (threshold: 8.0/10)

Reviewed asset SHA-256: `20238EA3E7E6D84398502DD7C53A2B003E07EA5199BD4632C8C548F39282CF33`.

I verified that the on-disk asset matched the handoff SHA, read the source and revision reports, inspected the saved exterior/front/interior/footprint previews, and read the fresh-open validation. This review did not modify the asset.

| Category | Score | Weight | Weighted points |
| --- | ---: | ---: | ---: |
| Identity and provenance | 9.0 | 20% | 1.80 |
| Plan geometry and placement | 8.0 | 25% | 2.00 |
| Exterior silhouette and openings | 7.7 | 25% | 1.925 |
| Materials and facade | 8.0 | 10% | 0.80 |
| Interior and cutaway clarity | 7.4 | 10% | 0.74 |
| Presentation and technical | 8.8 | 10% | 0.88 |
| **Weighted total** |  | **100%** | **8.145 → 8.1/10** |

## Findings

- **Identity and provenance (9.0):** Purdue GIS FID 780 names Sigma Kappa at 427 Russell St. The saved commissioned house illustration also names Sigma Kappa and 427 N Russell Street. Purdue FSCL corroborates chapter identity. The source record is careful to exclude an unrelated Panhellenic image and to identify the historic archive item as a catalog entry rather than a recovered photo.
- **Plan geometry and placement (8.0):** The 21-vertex GIS ring is retained at the base and validated after fresh-open with about 0.000015 m nearest-source XY error. This is by construction under the approximate project transform, not an independent survey/placement test. The unexplained service Shape__Area/Length discrepancy is preserved and not used to rescale the model; orientation remains provisional.
- **Exterior silhouette and openings (7.7):** R2 is a substantial improvement over the R1 bar-like view. The primary render now presents the central portico/sign, three front gables, paired wings and four distributed roof dormers in the broad composition shown by the reference. The front elevation is readable. Remaining simplifications include a broad, comparatively planar roof field, gables and dormers with sparse glazing detail, and fewer facade openings than the drawing. The only architectural reference is stylized secondary artwork, so bearing and dimensions remain unknown.
- **Materials and facade (8.0):** The dark red-brown masonry, charcoal roof, pale portico/trim, and blue-gray glazing separate clearly and align qualitatively with the illustration. They should not be taken as measured material specifications or an as-built palette.
- **Interior and cutaway clarity (7.4):** The revised cutaway shows a coherent floor plate, increased low partitions, several generic furniture silhouettes, and a stair placeholder. It is legible as a schematic but remains sparse relative to a 21-vertex, approximately 624 m² local footprint and does not provide room functions or circulation evidence. The not-as-built warning is clear.
- **Presentation and technical (8.8):** Blender 5.2.3 LTS fresh-open validation passes: expected scene/collection and one mesh root, 4,489 vertices, 3,317 faces, ten materials, no saved cameras/lights and no external image dependency. Saved views make the new front composition and interior inserts assessable; some flatness is still visible in the roof/elevation.

## Remaining limitations

Roof, facade bearing, height, window count/spacing, dormer dimensions and unseen elevations are estimated from a single stylized illustration. GIS `NUM_LEVELS=1` conflicts with that drawing's two-level reading; `Extrution=12` has no documented meaning or units. The interior is a generic one-level schematic, not an as-built layout. The outline comparison is by construction and the local transform is approximate. These limits are disclosed; no further source-backed revision is required for this massing-grade pass.

Exact SHA was checked before and after review; no asset edits were made.
