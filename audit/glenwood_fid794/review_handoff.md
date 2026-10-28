# Independent review handoff — Glenwood, FID 794

**Frozen asset:** `modular/buildings/massing_house_301841249_f827941.blend`  
**SHA-256:** `d0b2fa56be3b5db1352eddc202b83204012cf18c21b3ce3db9866e793e0e6319`  
**Fresh-open:** Blender 5.2.3 LTS PASS; see `fresh_open_validation.json`.

Separate read-only independent review is complete at **8.6/10 PASS** on the exact SHA above. See `independent_grade_codex_2026-10-28.md` for the six-category scorecard. Primary references are `sources/purdue_fscl_glenwood_hero.jpg`, `sources/purdue_ag_success_glenwood_house.jpg`, the GIS snapshots in `sources/`, and `schematic_interior_plan.png`. `source_and_model_notes.md` summarizes identity reconciliation and limits.

Review focus:

- GIS: FID 794 resolves to `Glenwood`, SOGL, 503 University St. The saved feature ring is the lower wall outline and its transformed vertices agree with the modeled bottom outline to 0.0000163 m; this is not a separate survey or placement check.
- Exterior: the official image supports light horizontal siding, shutters, repeated windows, entry portico/sign and dormer-like upper roof forms. The modeled roof mass, count/spacing, story arrangement, dimensions and unseen elevations remain illustrative. The attribute `NUM_LEVELS=1` conflicts with the multi-level source image and is explicitly unresolved.
- Interior: rooms, floor plates, partitions, stairs, circulation and furnishings are schematic placeholders. No as-built plan or interior image was found. The 2D plan is explicitly labeled not as built.
- Geometry and technical: the one-mesh stable asset opens in Blender 5.2.3, has 12 procedural materials and no external image dependencies. GIS `Extrution=12` is not interpreted as height; the modeled ridge is an estimate, not measured.

The independent-grade threshold is met; master integration remains coordinator-owned. Keep the asset frozen at this SHA during integration.
