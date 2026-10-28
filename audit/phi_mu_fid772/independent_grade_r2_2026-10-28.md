# Independent review — Phi Mu, FID 772, revision 2

**Reviewed:** 2026-10-28  
**Artifact:** `modular/buildings/massing_house_301836574_fff1661.blend`  
**Verified SHA-256:** `8524c009a3931f1e04ca1ed313d43be3be1cb94ff07ea99c62797841db65d861`  
**Result:** **8.285 / 10 — PASS** (8.29 rounded)

I independently reopened the exact saved asset in Blender 5.2.3 LTS and inspected the revised exterior/cutaway, GIS outline comparison, source notes, and validation record. The stable scene and collection load successfully with one mesh object, 11,469 vertices, 10,734 faces, 12 materials, and no external image dependencies. The latest footprint evidence reports an 18-vertex source ring matched within about 0.000015 m by construction. The revision adds a legible roof-open view with schematic floor areas, room dividers and circulation inserts; this is explicitly not represented as an as-built plan.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Basis |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.2 | 1.84 | Purdue GIS FID 772 and the official Phi Mu Delta Epsilon page agree on 201 Waldron Street. The retained 2010 chapter-specific photo supports the visible brick, light pediment/cornice, columns, tall window bays and Phi Mu letters. It is dated, cropped, and only covers one facade. |
| Plan geometry and placement | 20% | 9.4 | 1.88 | The 18-vertex source outline and saved overlay show near-exact construction agreement. This demonstrates use of the transformed GIS ring, not surveyed wall lines or independent absolute campus positioning. |
| Exterior silhouette and openings | 20% | 7.3 | 1.46 | The modeled front composition follows the photographed brick base, pediment/cornice, columns, window bays and centered letters. Roof shape, the two-level interpretation, compass orientation and unseen elevations remain unsupported estimates; GIS `NUM_LEVELS=1` conflicts with the modeled two-level reading. |
| Materials and facade | 10% | 7.8 | 0.78 | The procedural palette is portable and the brick/white trim follows the visible photo. Roof and unseen facade materials remain interpretive; the exterior remains stylized rather than photoreal. |
| Interior detail and evidence | 15% | 7.0 | 1.05 | The revision adds a roof-open cutaway, floor surfaces, room dividers, and circulation/furnishing cues within the full footprint. These are expressly schematic and not as-built: no verified plan, room count, room functions, or dimensions were found. The cutaway is now inspectable, but remains a diagram. |
| Presentation and technical | 15% | 8.5 | 1.275 | Independent fresh-open succeeds with stable identity, one mesh, 12 materials and no external image dependencies. The outline, exterior and roof-open cutaway previews are readable. |
| **Total** | **100%** |  | **8.285 / 10** | **PASS — meets 8.0** |

Calculation: (9.2 × .20) + (9.4 × .20) + (7.3 × .20) + (7.8 × .10) + (7.0 × .15) + (8.5 × .15) = **8.285**.

## Remaining limits

- The roof, height, facade orientation, two-level interpretation and unseen elevations remain estimates. GIS reports one level; the available 2010 photo does not verify the roof or full building.
- The added interior improves the required visual-detail deliverable, but it is only a labeled schematic and must not be presented as a recovered floor plan.
- The footprint comparison is by construction from the same GIS ring after the repository's local coordinate conversion; absolute survey placement is not independently established.

## Evidence reviewed

- `evidence.json`, `source_and_model_notes.md`, `geometry_reconciliation.json`, `footprint_overlay.png`, `fresh_open_validation.json`, `fresh_open_exterior.png`, and `fresh_open_schematic_interior_cutaway.png`.
- GIS source snapshots identify FID 772 as Phi Mu at 201 Waldron Street; the official chapter page and dated chapter-specific exterior photo provide identity and visible-facade support.
- The previous **7.54/10 FAIL** applies only to SHA `77d7d6075baa1f4948e48a0a0366891e33e28e0e9daf9f6290e9828ec8584f43`, which had no interior. This pass applies only to revision 2 SHA above.
- No asset or shared project file was modified during this review.
