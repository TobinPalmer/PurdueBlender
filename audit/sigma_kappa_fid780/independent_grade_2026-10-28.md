# Sigma Kappa FID 780 — independent exact-SHA grade

**Result: 7.3/10 — FAIL** (pass threshold: 8.0/10)

Reviewed asset SHA-256: `74DE8B51A91D6BAD5F8B40EB9282D77E221EC4EDB0AAABE82F08BCFE335C1430`

The SHA matches both the handoff and the on-disk `.blend` at review time. Review was read-only with respect to the asset. I compared `exterior_preview.png`, `front_elevation_preview.png`, `interior_cutaway_preview.png`, and `source_footprint_diagnostic.png` with the saved Sigma Kappa house illustration and the documented GIS/provenance packet. Fresh-open validation reports Blender 5.2.3 LTS, one root mesh in the expected scene/collection, 2,724 vertices, 10 materials and no external image dependencies.

| Category | Score | Weight | Weighted points |
| --- | ---: | ---: | ---: |
| Identity and provenance | 8.7 | 20% | 1.74 |
| Plan geometry and placement | 8.0 | 25% | 2.00 |
| Exterior silhouette and openings | 6.0 | 25% | 1.50 |
| Materials and facade | 7.5 | 10% | 0.75 |
| Interior and cutaway | 5.5 | 10% | 0.55 |
| Presentation and technical | 8.0 | 10% | 0.80 |
| **Weighted total** |  | **100%** | **7.34 → 7.3/10** |

## Findings

- **Identity and provenance (8.7):** GIS FID 780 names Sigma Kappa at 427 Russell St; the cited commissioned house illustration labels Sigma Kappa / 427 N Russell Street. The source packet is candid that the image is stylized and the 1952 Purdue Archives item is a catalog listing only, not an obtained photo. The potentially misleading unrelated Panhellenic image is explicitly excluded.
- **Plan geometry and placement (8.0):** The 21-vertex source ring is preserved at the base with a reported maximum nearest-vertex deviation of about 0.000015 m. This is a by-construction match under the approximate campus transform, not independent placement/survey verification. The report appropriately flags that GIS Shape__Area/Length materially differ from locally transformed ring metrics; more explanation or an independent parcel/map comparison would strengthen confidence.
- **Exterior silhouette and openings (6.0):** The illustration shows a clear two-wing composition with front-facing gables, a centered full-height portico, and four dormers grouped above the central entry. The saved model views instead read as a long, mostly rectilinear two-story bar with a broad, nearly flat-looking roof slab, a side-offset portico and four box dormers clustered at one end. The illustration's defining gabled roof transitions and centered entry composition are not legible in the current exterior or front elevation. The west-facing camera label does not resolve the mismatch because the orientation is expressly provisional.
- **Materials and facade (7.5):** Red-brown masonry, pale trim/portico and blue-gray glazing are present and are directionally consistent with the illustration. In the saved previews, the brick is muted/salmon and the roof/trim read as large flat gray/white planes; masonry and roof articulation need stronger visual definition to communicate the reference palette and form.
- **Interior and cutaway (5.5):** The preview is a labeled schematic, but it reads mainly as an unpartitioned footprint/floor plate with a few furniture-like marks. Circulation, room divisions, stairs and distinct modest furniture are not legible enough to evidence an interior. No as-built plan is claimed, appropriately.
- **Presentation and technical (8.0):** The library is clean and fresh-open validation passes. The outside preview framing is legible, but the flat gray world/background and pale low-contrast presentation obscure roof and facade details. The interior image does not demonstrate a clear roof-open/cutaway relationship.

## Revisions needed to reach the bar

1. Rework the primary exterior view to make the illustrated two front-facing gable wings, central portico and roof transitions read clearly; keep the four dormers but place and size them in a way that supports the source composition. Do not infer unpictured sides as verified.
2. Improve roof and facade material contrast and articulation so the brown/slate roof, red-brown brick, pale portico and window rhythm are distinguishable in the saved view.
3. Make the schematic interior evidence more legible with visible room partitions, circulation/stair placeholder and several recognizable furniture blocks, while retaining the “not as built” qualification.
4. If possible, add an independent GIS/parcel placement check or explicitly retain placement as unverified; the current shell-ring residual is by construction.

The asset is below threshold and should not be treated as finished until revised and independently regraded on a new exact SHA.
