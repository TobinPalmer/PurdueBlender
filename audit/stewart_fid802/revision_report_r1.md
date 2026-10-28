# Stewart FID 802 — revision report R1

**Asset SHA-256:** `7339F13546EF06A0530A92BEE747157F22E09D2B449496B40DE51CFF5CD2DB5E`

## Work completed

- Built the exterior shell to the exact 16-vertex FID 802 footprint and welded duplicate mesh vertices; retained project-compatible campus-local coordinates.
- Added a qualitative light-masonry exterior, dark roof forms, tower-like roof mass, tall windows and arched glazed entry from the current official Stewart house image. The photo is not a calibrated facade source; unseen walls and all dimensions remain inferred.
- Added four separate schematic floor objects with 3D partitions, stairs and illustrative furniture/use blocks. The official house-tour page supports a basement and second-/third-floor spaces but has no measured plan.
- Recorded the GIS `NUM_LEVELS=1` conflict explicitly. Modeled height, three above-grade stories, roof dimensions/pitch, basement elevation and room layouts are estimates, not measured or current as-built facts.
- Saved current exterior, roof-plan, footprint-overlay and story-plan previews. Reopened the saved `.blend` in Blender 5.2.3 LTS and passed the fresh-open validation.

## Validation values

See `fresh_open_validation.json` for the complete result. The saved asset contains 11 mesh objects, the expected scene/collection/root names, 16 source-ring vertices at the root wall base, maximum nearest-ring error 0.0000276 m in the approximate campus-local transform, and no external image dependencies. The open architectural root shell has 76 non-manifold edges; it is not claimed to be watertight.

The source packet and peer-review handoff are `source_record.json`, `evidence.json`, and `review_handoff.md`. Current grade status is pending independent review.
