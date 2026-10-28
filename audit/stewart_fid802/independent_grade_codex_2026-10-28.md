# Stewart Cooperative House — independent exact-SHA grade

**Reviewed:** 2026-10-28  
**Asset:** `modular/buildings/massing_house_1089875810_8c9b95d.blend`  
**Verified SHA-256:** `7339f13546ef06a0530a92bee747157f22e09d2b449496b40de51cff5cd2db5e`  
**Result:** **8.07/10 — PASS** (threshold: 8.0)

This is a read-only review. I reopened the saved-asset evidence and inspected the model previews, source photo, GIS comparison and interior cutaways. The asset SHA was unchanged.

## Weighted score

| Category | Weight | Score | Weighted points | Finding |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.2/10 | 1.840 | Purdue GIS FID 802 names Stewart and gives 800 Northwestern Ave; Stewart Cooperative official home page and Purdue FSCL cooperative list corroborate the facility and address. Named-house official photograph visually ties the modeled visual style to Stewart. No independent parcel overlay was provided. |
| Plan geometry and placement | 25% | 8.5/10 | 2.125 | The asset retains the 16-vertex FID 802 ring at wall base. Fresh-open validation reports maximum nearest source-ring vertex residual 0.00002755 m and approximate bounds 13.209 by 23.323 m. This is a by-construction match under the repository approximate local transform, not independent geodetic placement or survey verification; no independent orientation check is supplied. |
| Exterior silhouette and openings | 25% | 7.3/10 | 1.825 | The undated, tree-obstructed official image supports pale masonry, dark gabled roofs, a tower-like end mass, tall windows, and an arched glazed entry. The model represents these cues, but its full roof plan/pitch, tower proportions, window rhythm, facade bearing and unseen elevations are estimates; the image does not validate the elevations quantitatively. |
| Materials and facade | 10% | 8.0/10 | 0.800 | Named procedural materials provide pale masonry, dark gray roofing, glazing, frames/trim and schematic interior surfaces with no external image dependencies. Palette aligns with the official photo, but surfaces are broad color assignments without sourced material texture or calibrated finish values. |
| Interior and cutaway | 10% | 6.8/10 | 0.680 | Four story/floor groups, stairs, partitions and illustrative furniture/use blocks plus a schematic basement give a legible cutaway and story plan. Official house-tour text supports second- and third-floor hallways and basement context, but no dimensioned/current as-built plan supports room count, circulation, placement or furniture; interiors remain schematic. |
| Presentation and technical | 10% | 8.0/10 | 0.800 | Blender 5.2.3 LTS fresh-open validation confirms the expected scene, collection and root with 11 meshes and no external image dependency; audit includes exterior, roof, overlay and interior previews. The main root shell has 76 non-manifold edges at architectural openings and is explicitly not watertight; this is documented, not a portability/open failure. |

## Overall

The independently weighted total is **8.07/10 — PASS**. The strongest evidence is identity and preservation of the named GIS wall-base footprint; the greatest limits are the unmeasured exterior, schematic-only interior, and documented open shell boundaries. The model is not fully verified for survey placement, roof form, exact facade dimensions or as-built interior.

The exact machine-readable score and reviewed evidence list are in `independent_grade_codex_2026-10-28.json`.
