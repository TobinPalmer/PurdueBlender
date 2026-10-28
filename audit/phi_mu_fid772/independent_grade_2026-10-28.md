# Independent review — Phi Mu, FID 772

**Reviewed:** 2026-10-28  
**Artifact:** `modular/buildings/massing_house_301836574_fff1661.blend`  
**Verified SHA-256:** `77d7d6075baa1f4948e48a0a0366891e33e28e0e9daf9f6290e9828ec8584f43`  
**Result:** **7.54 / 10 — FAIL** (8.0 required)

This read-only review used the source/evidence packet and previews in this folder, then reopened the exact saved asset in Blender 5.2.3 LTS. The asset loads with the expected scene and collection, one mesh object, 9,267 vertices, 8,612 faces, seven procedural materials, and 27.970 × 44.359 × 9.400 m bounds. The footprint overlay reports 18 GIS ring vertices and about 0.000015 m maximum source-to-mesh outline error. The captured top view confirms the roof is opaque, so it does not reveal or document an interior.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Basis |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.2 | 1.84 | Purdue GIS FID 772 and the official Phi Mu Delta Epsilon chapter page agree on 201 Waldron Street. The retained 2010 chapter-specific property photo supports the visible brick, light pediment/cornice, columns, tall window bays, and Phi Mu letters. It is dated and cropped, and only covers one facade. |
| Plan geometry and placement | 20% | 9.4 | 1.88 | The source polygon has 18 vertices and the saved overlay/evidence reports roughly 0.000015 m maximum outline error. This confirms construction from the transformed GIS ring, not surveyed wall lines or independent absolute campus placement. |
| Exterior silhouette and openings | 20% | 7.3 | 1.46 | The modeled front composition follows the photograph's brick base, classical pediment/cornice, columns, tall windows, and centered letters. The reference does not verify compass orientation or the other elevations; the broad roof mass, upper story, roof breaks, and unseen openings remain estimated. The rendered architecture is clean but strongly simplified. |
| Materials and facade | 10% | 7.8 | 0.78 | The seven native/procedural materials are portable and the brick/white-trim palette follows the visible photo. The current render reads as smooth, uniform surfaces, and the photo is not sufficient to verify roof or side/rear materials. |
| Interior detail and evidence | 15% | 2.0 | 0.30 | The builder explicitly states that no as-built interior is claimed or modeled. No floor plate, rooms, partitions, circulation, stairs, or furnishing detail are visible in the saved asset. Lack of a source plan justifies labeling a schematic interior, but it does not satisfy this project's required interior-detail deliverable. |
| Presentation and technical | 15% | 8.5 | 1.275 | Fresh-open in Blender 5.2.3 succeeds with the expected stable single-object asset and no external image dependencies. The exterior and outline previews are readable. No roof-open cutaway or interior view is supplied. |
| **Total** | **100%** |  | **7.535 / 10** | **7.54 — FAIL** |

Calculation: (9.2 × .20) + (9.4 × .20) + (7.3 × .20) + (7.8 × .10) + (2.0 × .15) + (8.5 × .15) = **7.535**.

## Revisions required to pass

1. Add a clearly labeled **schematic, not as-built** interior: floor plates, plausible room partitions, stairs/circulation, and a modest amount of interior furniture/detail. Keep all room locations and functions explicitly marked as estimates because no verified plan was found.
2. Provide a roof-open cutaway preview that shows the full footprint and the interior inserts without implying an authoritative floor plan.
3. Make the roof and second-level interpretation visibly provisional in the evidence: GIS `NUM_LEVELS=1` conflicts with the two-level reading, and the available 2010 photo does not document the roof. Do not claim the current roof as verified.
4. Preserve the GIS overlay, material/source notes, portable dependencies, stable asset identifiers, and the current validated footprint while revising.

## Source and technical notes

- See `evidence.json`, `source_and_model_notes.md`, `geometry_reconciliation.json`, `footprint_overlay.png`, `fresh_open_validation.json`, and `fresh_open_exterior.png`.
- Sources retained by the builder include Purdue GIS FID 772 (layer metadata and 4326/3857 feature responses), the official [Phi Mu Delta Epsilon chapter page](https://purdue.phimu.org/about), and a 2010 chapter-specific photo post at `https://cmkelham.wordpress.com/2010/08/09/phi-mu-pink-letters-201/`.
- This review did not modify the asset or any shared project file.
