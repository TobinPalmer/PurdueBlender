# Circle Pines FID 761 — R3 revision report

Date: 2026-10-28

## Candidate

- Asset: `modular/buildings/massing_house_301841609_c6c9ac4.blend`
- SHA-256: `D21277A85B16C4E6A271785280EE311104D19D7E489D9034E3D0F896267AD21E`
- Independent review: requested; pending. R2 FAIL (7.6/10) remains preserved.

## Changes

- Replaced fine bump and high-frequency material variation that looked like an unsupported horizontal siding pattern with a restrained warm-neutral study material and broad low-contrast variation. No actual facade material is claimed.
- Refreshed the preview lighting with soft directional fill and a neutral studio ground so the shell silhouette and open-roof interior render more clearly. Preview ground and lights are temporary render objects and are not saved in the building asset.
- No architectural features or envelope geometry were added. The exact GIS footprint remains the 44-vertex Purdue FID 761 polygon. The 3.6 m wall height plus 0.25 m planar cap (3.85 m total) remains estimated. Roof form, openings, entry, cladding, and current interior remain unverified.
- Searched Purdue FSCL, the official Circle Pines site, the official Instagram handle, indexed image results, and exact-address queries; no attributable current exterior image was recovered. The 1954–55 Purdue Debris archive page is saved as historical context only; it does not establish that the depicted porch belongs to the current FID 761 structure and no historic detail is transferred into the model. Details are documented in `visual_source_search_r3.md`.

## Validation

Fresh-open validation succeeded in Blender 5.2.3 LTS. Expected scene, collection, and object names are present; 696 vertices and 485 faces; saved bounds are 49.8551 × 64.3915 × 3.85 m. All 44 source-ring vertices remain aligned to the wall base within 0.0000305 m. The 44 open underside boundary edges are expected for this shell representation. Current exterior and cutaway previews were rendered from the saved asset.

## Limits

This remains a GIS-accurate, conservative massing study rather than a verified architectural reconstruction. Height, roof cap, schematic room divisions, circulation, and furniture are illustrative. No current facade imagery or measured elevation/floor plan was found.
