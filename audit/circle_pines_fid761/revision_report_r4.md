# Circle Pines FID 761 — R4 source-backed revision

Date: 2026-10-28

## Candidate

- Asset: `modular/buildings/massing_house_301841609_c6c9ac4.blend`
- SHA-256: `1E2048AF786DD3724A92DACCA5E59BC9C4FD33025DA9239930B72028F067EAD2`
- Stable scene, collection and object IDs retained.
- R3 exact-SHA independent result remains 7.8/10 FAIL; see `independent_regrade_codex_r3_2026-10-28.md`.

## Source-supported changes

The newly located Google Maps Street View frame (April 2026 listing; pano ID `ytu8Bz_eEp2xCv9QeF0xRw`) faces the FID 761 building across its parking area. Camera location, heading, transformed FID centroid and nearest-edge alignment are summarized in `streetview_target_reconciliation.json`; the approximate alignment supports the target match but is not survey verification. See `visual_source_search_r4.md` for the source and its limits.

The exact 44-vertex Purdue GIS outline is unchanged. On the camera-facing long wall only, R4 adds the observed red-brown brick finish, two rows of four rectangular window assemblies, a taller central glazed entry bay and a shallow light canopy. Other elevations remain a neutral unverified study surface. Tree cover obscures most of the roof, so the saved asset keeps only a conservative planar cap; no roof style is claimed. The visible two window bands motivate an estimated 5.4 m wall plus 0.35 m cap (5.75 m total), not a measured height. GIS `NUM_LEVELS=1` conflicts with the two visible bands; the conflict remains explicit. The unsupported `Extrution=32` field is not used as a measurement.

The asset still has one-level 3D schematic floor zones, partitions, circulation, short step run and furniture inserts. They are unverified and not as-built; no upper-floor interior is asserted. A schematic plan and roof-open cutaway accompany the exterior previews.

## Fresh-open validation

Blender 5.2.3 LTS reopened the saved asset and passed the building-specific validator. It reports one object, 1,000 vertices, 713 faces, 14 procedural materials, no external image dependency, exact collection/object identity and a 44-vertex source ring. The wall-base maximum component error from the GIS ring is 0.0000305 m (Blender vertex precision). Bounds top is 5.75 m. The mesh has 44 boundary/nonmanifold edges, consistent with the intentionally open massing shell. Full report: `fresh_open_validation.json`.

## Review state and limits

R4 received an independent read-only exact-SHA grade of 8.3/10 PASS; the scorecard is `independent_regrade_codex_r4_2026-10-28.md`. The current image supports only one facade and approximate visual features. The roof is mostly hidden, unseen elevations and interior remain uncertain, height is estimated, and GIS story count conflicts with the visible two bands. The old 1954–55 archive image is context only and contributes no current geometry claims.
