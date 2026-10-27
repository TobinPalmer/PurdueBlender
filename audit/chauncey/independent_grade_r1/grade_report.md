# Chauncey Cooperative independent grade

**Result: 8.0/10 — PASS**  
**Asset SHA-256:** `ce6fa6770e4fc76546f50f7a3889a84bdc0ed676e6ea10e1cb9c06d6757242ef`

| Category | Score | Review |
| --- | ---: | --- |
| Identity and site evidence | 2.0/2 | Purdue GIS FID 805 names Chauncey Cooperative at 215 S Chauncey, and the official house site gives the same address. Purdue's cooperative-house directory corroborates that this is an active cooperative. The saved official exterior photo matches the modeled two-story house identity. |
| Footprint, form, and orientation | 1.5/2 | The 16-vertex foundation ring matches GIS FID 805 with a reported maximum vertex error of 4.6e-7 m, and the centroid origin is documented for master placement. The two-story front-gabled massing is plausible. Roof pitch, eaves, and the roof envelope are estimates; the single large roof plane simplifies the more complex roof edges visible in the photo. |
| Facade, materials, and source fidelity | 1.5/2 | The model includes pale clapboard siding, dark shingle roof, gable louver, shuttered sash windows, stone porch base, porch railings, steps, and the house sign. The procedural textures are portable and visibly separate the siding, roof, stone, glass, and painted trim. The porch canopy and window rhythm remain simplified, and exact current paint/roof condition is not measurable from the archived photo. The builder reports the March 2026 Street View supports the same exterior type; that panorama is cited in the evidence but was not independently retrievable in this review. |
| Interior | 1.0/2 | Floor plates, partitions, a kitchen counter, dining table/chairs, common-room seating, and bedrooms are present. This reads as a deliberately schematic interior rather than an empty shell, but it is not a verified floor plan and its furniture/room arrangement is coarse compared with the saved interior room photo. |
| Portability and fresh-open validation | 2.0/2 | I confirmed the asset SHA matches the builder's fresh-open report. Blender 5.2.3 reopened the expected asset collection with 260 meshes, 13 materials, a scene camera, and no external image dependencies; the GIS foundation-ring check passes. |

The total is **8.0/10**, meeting the acceptance threshold. The asset is suitable for master integration with its stated height, roof, facade-spacing, and interior uncertainties retained. The next visual improvements would be a closer photo-matched roof/porch profile and more legible interior room detail.

## Evidence reviewed

- `audit/chauncey/evidence.md`
- `audit/chauncey/fresh_open_validation.json`
- `audit/chauncey/chauncey_preview.png`
- `audit/chauncey/sources/House.jpg` (official archived exterior photo)
- `audit/chauncey/sources/FRUP.jpg` (interior room reference)
- `audit/chauncey/sources/purdue_fid805.geojson`
- Official references listed in the evidence: Purdue cooperative-house directory, the linked Chauncey house site, and the Google Maps Street View listing.

## Limitations

- The official photo is archival and non-geotagged; hidden elevations and exact facade dimensions remain estimates.
- The Street View URL and March 2026 capture date are documented by the builder, but the panorama itself was not independently accessible in this review environment.
- The interior is schematic; no registered floor plan was found.
- The omission of a chimney is reasonable given the newer Street View reportedly does not clearly show one, but its current presence remains unresolved.
