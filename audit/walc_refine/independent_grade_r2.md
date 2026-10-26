# WALC independent grade — R2

**Result: 7.6/10 — below the 8.0/10 completion threshold.**

**Asset SHA-256:** `66e77776b04dd142c8a1292ff2f297c5a4b3a9b3f676ff62243bf81376714850`  
**Independent reopen:** Blender 5.2.3 LTS. `Asset_walc` reopened with 951 objects and 879 meshes; `AssetRoot_walc` is identity. The foliage library resolves from the relative path `//../site/foliage_library/engineering_foliage_library.blend`. No materialless meshes, invalid material-slot indices, or missing images were found. The one image texture is packed.

R2 addresses two technical and visual issues from the 6.8/10 R1 review: the absolute foliage link is now relative and verified on reopen, and 147 bronze fins introduce more vertical articulation. Procedural material variation and brighter inspection lighting are also present. The reviewed exterior renders still show broad dark ribbon glazing and wide reddish bands with little visible masonry or glass surface detail; the fins read most clearly around the entry. The roof remains a broad, largely featureless plane with a pale inset and an estimated raised element. The interior set is substantial and easier to inspect, but some spaces remain generic or blank, and room layouts are not verified against architectural plans. These changes improve R1, but do not reach 8/10.

## Scorecard

| Category | Score | Findings |
|---|---:|---|
| Identity and plan footprint | 2.0/2.0 | The structural roof ring traces cached Purdue GIS FID 906 to about 0.000002 m. This demonstrates agreement with the same cached outline used to build the model, not independent survey accuracy. |
| Local frame and structure | 0.9/1.0 | Identity root and local frame are preserved. The linked foliage library resolves through a project-relative path. The master `Placement_walc` marker and neighboring campus alignment were not reviewed. |
| Exterior architecture | 1.25/2.0 | The overall three-above-ground-floor mass and prominent entry canopy read as WALC. Added fins make the entry more vertical, but the normal facade views remain broad, repetitive ribbons. Window bay/pier rhythm, masonry transitions, entry depth and roof edge remain simplified; roof form/elevations are unverified. |
| Materials and surface finish | 0.85/1.5 | The new procedural brick/limestone variation and revised glass/bronze response are present, and all used meshes have materials. In the saved exterior views, large surfaces still read as flat dark glass and uniform red-brown bands; material variation is difficult to distinguish under the gray, low-contrast lighting. Paving and entrance surroundings remain generic. |
| Interior and program | 1.45/2.0 | The reading room, atrium, bridges/stairs, stacks, theatre, active-learning classroom and basement are represented. Brighter inspection lighting helps. The classroom/theatre layouts, room boundaries and finishes remain generic or schematic; the basement view is mostly empty and no detailed floor plan/as-built layout was checked. |
| Reopenability and evidence | 1.15/1.5 | Exact R2 asset reopened in Blender 5.2.3; library path resolves, 24 materials are used, image texture is packed, and no materialless/invalid-slot meshes were found. R2 records sources and limits, but current elevations, roof heights, interior plans and master placement remain unverified. |
| **Total** | **7.6/10** | **Below the 8.0/10 threshold.** |

Scores sum to **7.60/10** using the same additive component rubric as R1; the R1 components summed to 6.8/10.

## R2 change assessment

- **Relative foliage library: pass.** Fresh standalone reopen resolves `//../site/foliage_library/engineering_foliage_library.blend` to an existing file in the project. This fixes the machine-specific absolute path identified in R1.
- **Facade fins: partial improvement.** The added vertical bronze fins improve the entry composition. The southwest, southeast and north renders still read mainly as long horizontal glass bands with wide red-brown stripes; most bay rhythm and brick/stone articulation is not visually established in those standard views.
- **Materials: partial improvement.** Procedural color and bump variation are assigned, but the exterior renders remain dark and low contrast. They do not show convincing, readable brick/stone texture at the shown scale. The brighter interior render setup improved inspection visibility without changing the modeled interior.
- **Interior: substantial but schematic.** The views now reveal the modeled program more clearly. They do not establish the real floor-by-floor location, construction or finishes of each space. The simplified and mostly unoccupied basement is especially weak as an interior view.
- **Footprint: trace match only.** The measured GIS residual is nearly zero because the evaluated roof trace and cached FID 906 outline use the same project reference. It does not validate the footprint against surveyed walls or confirm façade offsets.
- **Placement: unreviewed.** This review opened the standalone asset. The coordinator must inspect `Placement_walc` and the adjacent campus context before master integration.

## Prioritized R3 work

1. Use official Purdue exterior photos/renderings to break the long horizontal facade ribbons into visible, source-supported window bays, masonry piers and entry recesses. Keep unsupported dimensions labeled as estimates.
2. Improve a normal exterior view so bronze fins, brick/limestone variation and glass depth are legible without dark underexposure; add paving/entrance detail where supported by references.
3. Compare roof/edge form against an authoritative elevation or architectural image; do not present the roof height or assembly as measured without a dimensioned source.
4. Compare atrium/stairs, reading room, classroom and library zones against available official floor/program references. Retain `schematic` labels for details with no plan source; improve the empty basement view only where supported.
5. Have the coordinator verify `Placement_walc` against the manifest and neighboring roads/plaza in the full master.

## Sources and limits

- [Purdue Office of Emergency Preparedness — WALC Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/walc/) (revision 2026-04-03) supports four total floors, three above ground and one basement, plus library stacks, 27 classrooms, café and IT computers. It is program evidence, not a dimensioned architectural plan.
- [Purdue Chemistry — Wilmeth Active Learning Center](https://www.chem.purdue.edu/media/news/2017/wilmeth.html) (2017-04-12) supports the opening-era classroom program and shows a rendering/classroom context. It does not verify as-built facade dimensions or room-by-room layout.
- [Purdue Libraries — WALC open-house photographs](https://blogs.lib.purdue.edu/news/2017/05/17/libraries-host-big-ten-academic-alliance-library-conference/) provides interior photo context from 2017, not current construction documentation.
- [Purdue News — Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html) provides official exterior/context imagery; it is not a measured elevation.
- GIS comparison uses the project snapshot `audit/official_building_references.json` (Purdue BuildingShapesZip4, FID 906, retrieved 2026-10-22). The near-zero residual is against the cached source trace and is not independent survey evidence.

Reviewed renders: `southwest.png`, `southeast.png`, `north.png`, `roof.png`, and `03_reading_room_reference.png` through `09_basement.png`. Reopen details are in `independent_reopen_r2.json` and the reproducible inspection script `independent_reopen_r2.py`.

Asset modified: **no**. Master/shared files modified: **no**. Commit created: **no**.
