# Glenwood FID 794 — independent exact-SHA grade

**Reviewed asset:** `modular/buildings/massing_house_301841249_f827941.blend`  
**Verified SHA-256:** `d0b2fa56be3b5db1352eddc202b83204012cf18c21b3ce3db9866e793e0e6319`  
**Result:** **8.6/10 — PASS** (threshold 8.0)  
**Review date:** 2026-10-28  
**Mode:** Read-only review of the frozen saved asset and evidence. No asset edits.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Rationale |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.5 | 1.90 | GIS FID 794 directly names Glenwood/SOGL at 503 University St, with official FSCL and Glenwood history/contact corroboration. The image sources and retrieval limits are recorded. |
| Plan geometry and placement | 25% | 9.5 | 2.375 | All 8 unique source-ring vertices agree with the saved base outline to 0.0000163 m using the project-local approximation. This is a by-construction source-ring check, not independent placement or survey validation. |
| Exterior silhouette and openings | 25% | 7.2 | 1.80 | The model visibly represents the official photo's white horizontal siding, dark shutters, repeated windows, entry portico/sign and dormer-like roof forms. The stepped roof/upper masses, opening spacing, facade orientation and dimensions are interpretive; only one oblique facade photo is available. |
| Materials and facade | 10% | 8.5 | 0.85 | White siding, dark shutters, white trim, dark roof, foundation band and purple Glenwood sign use the saved official visual as qualitative evidence. Exact materials and hidden elevations remain unverified. |
| Interior and cutaway | 10% | 7.0 | 0.70 | The asset has a clear schematic plan/cutaway with floor plates, partitions, stair/circulation and generic furnishings, but no actual plan, room use or dimensions are sourced. The plan states it is not as built. |
| Presentation and technical | 10% | 9.5 | 0.95 | Fresh-open Blender 5.2.3 LTS PASS; expected one-mesh collection, no external image dependencies, and separate exterior, roof, top and cutaway views. Geometry bounds and limitations are documented. |
| **Total** | **100%** |  | **8.575 → 8.6/10** | **PASS** |

## Remaining limits

The GIS source supports only the base plan; exact wall placement is not independently surveyed. The only architectural source is an official oblique photo, so the roof form, dormer count/spacing, level interpretation, dimensions, compass orientation and unseen facades remain estimated. The GIS `NUM_LEVELS=1` conflicts with the multi-level photograph, while `Extrution=12` is undocumented and was not treated as measured height. Interior geometry remains schematic and is not an as-built floor plan.

## Evidence reviewed

- `review_handoff.md`, `evidence.json`, `source_and_model_notes.md`, `source` snapshots, and `fresh_open_validation.json`.
- `fresh_open_exterior.png`, `fresh_open_roof_oblique.png`, `fresh_open_top.png`, and `fresh_open_schematic_interior_cutaway.png`.
- `sources/purdue_fscl_glenwood_hero.jpg` and `sources/purdue_ag_success_glenwood_house.jpg`.
- Exact asset hash verified before review. No asset or shared file was modified.
