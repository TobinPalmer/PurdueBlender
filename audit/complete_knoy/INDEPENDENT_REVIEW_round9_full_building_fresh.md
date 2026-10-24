# Knoy Hall — fresh full-building review (R9 material pass; current saved asset)

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** Reviewed read-only on 2026-10-24. The saved asset currently includes the R9 material pass and subsequent R10 entrance sign and R11 typical-floor door updates; this is a fresh review of the whole current model, not a reuse of the targeted plan/corridor scores. No Knoy geometry or shared/master files were edited for this review.

| Category | Score |
| --- | ---: |
| Identity, GIS footprint and placement | 1.8/2 |
| Floors, height and roof interpretation | 1.2/2 |
| Exterior massing, facade and materials | 1.5/2 |
| Interior plan and circulation | 1.4/2 |
| Evidence, saved-asset validation and technical integrity | 1.9/2 |
| **Total** | **7.8/10** |

## Findings

### Identity, GIS footprint and placement — 1.8/2

The retained Indiana 2023 orthophoto and GIS outline support the building identity and broad footprint. The earlier coordinator marker check reports the placement marker matching the manifest to within 0.000008 m; the asset’s GIS-derived outline and orthophoto context are useful screening checks. The overlays use an approximate local-to-geographic conversion and do not prove surveyed wall alignment or facade-level registration. The R10 sign placement check confirms local alignment to the modeled entry wall, not an as-built survey.

### Floors, height and roof interpretation — 1.2/2

The 2018 Purdue Gateway study supports the L1–L4 floor interval and typical-plan pattern. The 2018 3DEP DSM/DEM check gives about 59.9 ft median surface-above-ground, consistent with a roof-like surface near the inherited L5 slab datum of 58.8 ft. Five-foot DSM cells combine stepped roof surfaces, edges and rooftop objects; the modeled/interpolated bare-earth samples and approximate footprint also limit precision. These data do not establish an occupied fifth story, exact roof/parapet or penthouse heights, or resolve the conflicting GIS 48 ft field. L5 and upper roof semantics remain unverified.

### Exterior massing, facade and materials — 1.5/2

The exterior render reads as a stepped multi-level building with continuous dark ribbon glazing, pale horizontal bands, brick strips and a flat roof. R9’s procedural brick, pale trim and glass colors are qualitatively consistent with Purdue’s undated profile image, but the source is a single uncalibrated perspective and does not support full facade cadence or exact material values. The R10 entrance lettering is clearly legible and R11 reduces its scale, though the photo still cannot verify the modeled letter dimensions or exact position. The broad facade remains repetitive and schematic; roof equipment and all-sided elevation detail are not established by the reviewed images.

### Interior plan and circulation — 1.4/2

The L2–L4 traces and partitions plausibly follow the 2018 typical-plan drawing, with about ±1 m hand-registration uncertainty; repeating that single drawing across all three levels is an informed representation, not proof of each floor’s as-built condition. R11 adds 45 illustrative closed door panels at 15 plan-visible openings across L2–L4. Their locations are visually supported by door-swing symbols, while panel dimensions and closed poses remain estimates. The L1 plan is a separate, less legible thesis raster: 12 illustrative leaves are modeled and six candidate gaps remain unresolved. The spatial door/stair render communicates partition and leaf height, but the top-down cutaway remains sparse and has no source-backed finishes or furnishings. Three stair cores connect the modeled L2–L4 levels; a continuous route through basement, L1, L5 and roof is not verified.

### Evidence and technical integrity — 1.9/2

R9 documents the qualitative material cues, estimated shader values and unchanged preexisting mesh geometry. R10 and R11 add bounded source citations, edit scopes and reopened-file checks. R11 reports 45 door panels present in the saved collection hierarchy, 118 descendant objects, and an unchanged geometry hash for the 62 preexisting meshes; the sign’s transform follows the shell parent inverse. Evidence appropriately distinguishes plan-traced locations from estimated door sizes and leaves uncertain L1 gaps unresolved. The withdrawn cyan PV-alignment overlay remains excluded from evidence. The historical 28-module count and 2023 image support presence of a panel-like installation in the south roof zone, not the current array’s exact layout or height. These technical checks support reproducibility, while they do not constitute a full independent as-built survey.

## Highest-value next work

1. Obtain a measured elevation or section before changing L5, penthouse or roof geometry; document how the GIS 48 ft field is defined if its metadata can be found.
2. Seek calibrated/current facade elevations or multiple matching views before changing window rhythm or assigning materials across all sides.
3. Keep L1 door candidates and vertical route uncertain until a clearer plan or as-built circulation source resolves them; improve cutaway contrast and floor-wide readability without implying actual finishes.
4. Keep PV count historical, placement schematic and the withdrawn cyan alignment overlay out of grading.

## Evidence reviewed

- `modular/buildings/knoy_hall.blend`
- `audit/complete_knoy/evidence_round9.json` (not present in the current audit folder; R9 details were checked in `facade_material_review_r9.json` and `facade_material_validation_r9.json`)
- `audit/complete_knoy/evidence_round10.json` and `entrance_detail_validation_r10.json`
- `audit/complete_knoy/evidence_round11.json` and `door_model_validation_r11.json`
- `audit/complete_knoy/roof_height_validation_r8.json` and `roof_height_assessment_r8.json`
- `audit/complete_knoy/door_gap_collision_audit.json`, `interior_cutaway_render_audit.json`, and `corridor_spatial_audit.json`
- `audit/complete_knoy/knoy_exterior_full_r10.png`, `knoy_entrance_detail_r11.png`, `knoy_l2_doors_stairs_spatial_r11.png`, `knoy_l1_corridor_spatial_audit.png`, and `knoy_l2_interior_cutaway.png`
- `audit/complete_knoy/INDEPENDENT_REVIEW_round9.md` and `INDEPENDENT_REVIEW_round10.md`
