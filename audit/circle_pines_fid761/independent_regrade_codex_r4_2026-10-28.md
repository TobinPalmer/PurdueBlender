# Circle Pines FID 761 — independent R4 exact-SHA grade

**Reviewed asset SHA-256:** `1E2048AF786DD3724A92DACCA5E59BC9C4FD33025DA9239930B72028F067EAD2`  
**Result:** **8.3/10 — PASS** (threshold: 8.0/10)  
**Review date:** 2026-10-28  
**Mode:** Read-only review of the exact R4 asset and evidence packet.

The on-disk SHA matched the handoff and R4 evidence. I compared the saved exterior and front elevation with the saved April 2026 Google Street View thumbnail, reviewed the interior and plan evidence, and checked the fresh-open report and GIS reconciliation notes. The Circle Pines asset was not modified.

## Weighted score

| Category | Weight | Score / 10 | Weighted points |
|---|---:|---:|---:|
| Identity and provenance | 20% | 9.0 | 1.800 |
| Plan geometry and placement | 25% | 8.5 | 2.125 |
| Exterior silhouette and openings | 25% | 7.9 | 1.975 |
| Materials and facade | 10% | 8.2 | 0.820 |
| Interior and cutaway | 10% | 7.1 | 0.710 |
| Presentation and technical | 10% | 8.6 | 0.860 |
| **Weighted total** | **100%** |  | **8.290 → 8.3 — PASS** |

## Findings

- **Identity and provenance (9.0):** Purdue GIS FID 761 identifies Circle Pines at 1000 David Ross Road; FSCL and BoilerLink corroborate the cooperative identity/location. R4 adds an attributable current Street View frame listed as April 2026. The packet gives the Maps listing URL, thumbnail, pano ID, retrieval date, and candid caveats that the date is taken from the UI and alignment is approximate. The 1954–55 archive image is retained as historical context and not used to assert continuity.
- **Plan geometry and placement (8.5):** All 44 source ring vertices are retained, with a 0.0000305 m fresh-open wall-base error. This is by construction, not independent survey or placement validation. The Street View point is approximately 62.77 m from the transformed centroid, with a 7.93° centroid-bearing/heading difference and 42.53 m nearest-edge distance. Those values support the target association but depend on an approximate campus transform and URL-supplied camera data. The weaker OSM shape is properly treated as secondary.
- **Exterior silhouette and openings (7.9):** The saved front elevation now shows the source-visible long brick facade, two rows of windows, central vertical glazed entry bay, and shallow canopy. The exterior view gives enough context to distinguish this facade from the neutral, unverified sides. It is a restrained match to what the image supports, not a full architectural reconstruction. Roof form remains unknown because trees obscure it; the planar cap is an honest placeholder. Height is estimated and conflicts with GIS `NUM_LEVELS=1`.
- **Materials and facade (8.2):** The red-brown brick, dark glazing, light trim and pale canopy read clearly and follow the current image. The model limits those finishes to the camera-facing wall and leaves unseen elevations neutral. Window spacing and all measurements remain visual estimates.
- **Interior and cutaway (7.1):** The 3D view and plan show a floor zone, partitions, circulation band, short steps and generic furniture. This is legible as a one-level schematic and explicitly not as-built. It remains sparse for a roughly 1,111 m² local footprint; actual room use, dimensions, stair location, circulation, and upper interior are unknown.
- **Presentation and technical (8.6):** Blender 5.2.3 LTS fresh-open validation passes with the expected one mesh object, 1,000 vertices, 713 faces, 14 materials, no saved camera/light objects, and no external image dependencies. The front elevation is especially useful for comparing the observed openings. The oblique whole-building preview is quite distant and has neutral context that competes for attention; this is a minor presentation limitation.

## Remaining limits

Only one current facade is visually supported. Exact camera-to-building alignment is plausible, not survey-verified. Roof, height, facade dimensions, unseen elevations and all interior details remain uncertain or schematic. The 1954–55 porch image is not applied to the current model. No further changes are required to meet the massing-grade threshold, but a closer primary exterior render and an independent parcel-to-GIS placement check would strengthen future review.

The 8.3/10 pass applies only to SHA `1E2048AF786DD3724A92DACCA5E59BC9C4FD33025DA9239930B72028F067EAD2`.
