# Independent Whistler Hall review

**Independent score: 7.9 / 10 — below the 8/10 threshold because the asset and manifest placement conventions conflict.**

## Evidence checked

- Read `modular/AGENTS.md` for geometry and library placement conventions.
- Reviewed `audit/whistler_hall/source_register.md`, `placement.json`, the raw Purdue FeatureServer response for FID 84, and the preserved 2015 Purdue Agricultural Communication photograph.
- Inspected the saved exterior and top-down renders and the builder's fresh-open validation report.
- Independently computed the asset SHA-256. It matches the requested value: `CE3C33048AC70467C25317192839AD4B6290542F23024F909351EC05F84115DD`.

## Score breakdown

| Category | Score | Finding |
| --- | ---: | --- |
| GIS identity and source traceability | 1.0 / 1.0 | FID 84 identifies WSLR / Roy L. Whistler Hall of Agricultural Research; the audit correctly flags FID 263 as Forest Products instead. Raw feature response and provenance are retained. |
| Footprint | 2.0 / 2.0 | The 31-vertex FID 84 perimeter is retained in the shell and roof outline, without simplification. Recorded local extents and area checks are consistent with that geometry. |
| Plan orientation | 1.0 / 1.0 | The footprint follows the GIS ring in the project east/north coordinates. Facade detail orientation remains inferred from a single oblique photo, not independently established by the source. |
| Campus placement and library convention | 0.2 / 1.5 | A proposed origin is documented, but this asset is `kind: massing` and local-centered. `modular/AGENTS.md` requires simple massing assets to retain campus coordinates and link directly. The current manifest still describes the old campus-space bounds and identity transform. If imported at identity, this local model will sit at the project origin, not Whistler's location. |
| Height and levels | 0.5 / 1.0 | Four levels are supported by GIS attributes. The 16.2 m parapet and 19.35 m apex are explicitly presented as estimates; no independent elevation source verifies them. |
| Exterior architecture | 1.0 / 1.5 | Russet masonry, pale belt courses, grouped glazing, broad upper glazing, and a raised gable are visible in the Purdue photo and represented. The render is convincing as a campus massing model, but window groupings, pilaster rhythm, and facade-side assignment are simplified or inferred. |
| Materials | 0.75 / 1.0 | Eight procedural materials and no external image dependencies are reported. The rendered brick reads rather uniformly at this distance, and no facade-specific material calibration is possible from the lone winter image. |
| Interior and use evidence | 0.6 / 1.0 | Generic lab benches/partitions suit the documented research-lab use. They are properly marked schematic; no actual room plan is claimed. |
| Portability and saved-file check | 0.85 / 1.0 | Stable names/collection and procedural assets are reported. The supplied fresh-process open check passes, and the file hash is verified. |
| **Total** | **7.9 / 10** | |

## Required placement resolution

Before integrating into the master, align the asset and manifest with one convention. Under the current instructions for a simple massing asset, the direct-link option is to translate its geometry into the project campus coordinates using the documented origin `(-156.31015498, -497.01139780) m`, then update the manifest bounds and retain the identity transform. Alternatively, change the asset's classification and integrate it using the detailed-building placement-marker workflow. Do not link the current local-centered file at identity.

The photo evidence supports general facade character but cannot prove which GIS side contains the pictured facade, exact entrance location, window schedule, or roof elevation. Keep those details labeled as estimates until a georeferenced elevation or additional source is found.

