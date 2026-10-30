# Knoy Hall — second-pass exterior research

**Queue rank:** 20 · **stable ID:** `knoy_hall` · **owner:** Rossen (preserved)
**Asset:** `modular/buildings/knoy_hall.blend`
**Status:** Prepared with gaps; provisional source package, not a build-readiness claim.
**Reference condition:** Latest available imagery (2025 Street View/recent orthophoto); no complete 2026 as-built survey. Research only; no model files changed.

## Identity and footprint

Purdue Campus GIS identifies **Maurice G. Knoy Hall of Technology**, 401 N. Grant Street, built in 1985. Queue/cache match **FID 243** is distinct from the later live MapServer record **OBJECTID 189 / buildingidlong 75 / ABBR KNOY**; do not conflate identifiers. Raw feature and provenance: `audit/batch4_knoy/purdue_campus_knoy_feature189_r23.json` and `official_gis_provenance_r23.json`.

The irregular, long cached boundary has 29 unique local vertices, approximate bounds **44.925 × 93.162 m**, and ring area around **2,632.7 m²** (`audit/batch4_knoy/gis_vertices_local.json`; derivation in `audit/complete_knoy/source_research_r23.md`). It is an approximate envelope, not a surveyed wall line. Current-service and cached polygons are close but not identical (maximum corresponding-vertex difference about 0.178 m; most are near 0.001 m); asset-to-cache match is about 0.000012 m. Those are GIS/cache/model comparisons, not physical wall validation. The plan/aerials indicate stepped, interlocking wings and re-entrant zones. Available sources do not resolve every inner edge as open court, lower roof or covered connector. No shared-asset boundary issue was resolved.

## Inspected source/view register

| ID | Provenance / view | Observations | Limitations |
| --- | --- | --- | --- |
| K-GIS | Purdue Campus MapServer live feature, retrieved 2026-10-25; raw JSON above | Identity and approximate boundary | Not an as-built survey; IDs differ from cached queue match |
| K-SV25 | Google Street View pano `37BzxutMJc4KJ68n5M55xw`, capture 2025-08; camera 40.4281078, -86.9106299; heading 244.316° true; approximate project XY (260.377, 78.594) | Oblique brick-heavy wall; thin horizontal glazing interrupted by broad opaque brick panels. Sight ray reaches candidate cached boundary segment 18 after ~28.745 m at approximate XY (234.472, 66.136). | Candidate edge registration only, not calibrated elevation; trees, perspective, distance and intervening walls prevent counts. Image not retained; source URL/metadata in `audit/complete_knoy/evidence_round20.json` and `evidence_round21.json`. |
| K-SV17 / K-SV09 | Same corridor historic panos `D6_nILpQqNtb2fZJUbaPJQ` (2017-09), `HBWd-zKUSYl9fdHHvzm21w` (2009-06), metadata in R20/R21 JSON | Broadly comparable brick/glazing vocabulary | Similar oblique/occluded view; no full count or condition reconciliation |
| K-ARCH1125 | Purdue Archives/eArchives item 1125, PPBUC01785; `audit/complete_knoy/purdue_archives_knoy_exterior_1125_r22.jpg`; catalog decade 1990s/2000s, capture date unknown | Stepped brick masses, pale coping/bands, long slit-window strip interrupted by broad brick panels | No camera pose or face registration; historic and partly occluded |
| K-ARCH1126 | Purdue Archives item 1126, PPBUC01786; `...exterior_winter_1126_r22.jpg`; catalog decade 1990s/2000s, capture date unknown | Winter entrance/wing junction, parapet steps, interrupted ribbon glazing, lower strip windows, ramp/landscape | Direction/date unknown; snow and trees obscure base |
| K-HIST18 | HIST 152 Purdue post, published 2018-08-09; `audit/complete_knoy/ref_knoy_main_entrance_hist152_2018.jpg`; capture date/pose unknown | Recessed dark glazed/door group under projecting canopy; ramp/rails, stairs, retaining/planter walls and planted approach | No compass registration or dimensions; planting obscures facade |
| K-POLY | Undated Purdue Polytechnic profile; `ref_purdue_profile_knoy_facade_r8.jpg` | Name wall, reddish-brown brick, narrow dark horizontal windows, light coping | Date/pose unknown; partial face only |
| K-PV17 | Purdue Polytechnic story published 2017-05-22, installation reported 2017-04-18; `knoy_pv_installation_2017_feature.jpg` | Roof close-up of tilted modules on silver rack rows. Purdue reports 28 panels replacing 24, peak 8 kW. [Source](https://old.polytechnic.purdue.edu/newsroom/new-knoy-rooftop-solar-array-generates-more-power-learning-opportunities-and-research) | Historical count; no measured plan, tilt, exact placement or confirmation of current array |
| K-ORTHO | Purdue/IndianaMap overheads `indiana_ortho_knoy_roof_detail_2023.jpg`, `indiana_ortho_knoy_current.jpg`; source metadata in roof assessment files | Multiple stepped roof areas/re-entrant spaces, broad mechanical or penthouse-like masses and a PV-like array | Roof view only; resolution/acquisition limits; not wall elevations or survey |
| K-GATEWAY | Purdue Gateway Formation Study dated 2018-05-31, retained `audit/complete_knoy/2018-05-31_knoy_massing_studies.pdf` | Typical Levels 2–4; existing L1–L4 at 14 ft 8 in (4.4704 m) floor-to-floor | Planning study, not record drawing; hand registration about ±1 m; no calibrated full elevations |

R19 glazing diagram mislabeled a 2009 ray as 2025; it is superseded. Use only corrected `facade_glazing_assignment_r20.svg/png`, an interpretive aid rather than evidence. The apparent “Berglund Project Overview and Plans” from Scribd is rejected in `audit/complete_knoy/source_research_r23.md`: metadata names a 2019 student project for a Chesterton office and its dimensions/elevations conflict with Purdue evidence. Do not use it as Knoy as-built documentation.

## Massing, levels, roof and dimensions

Photographs show long low wings and taller/stepped brick masses with changing parapet/coping heights. Orthophotos show distinct flat or low-slope roof fields and internal setbacks, but not exact roof edges, slopes, parapet sections or whether every apparent inner void is open to sky. Keep those roof areas separate until a registered roof plan or calibrated aerial/point survey resolves them.

The Gateway study supports four labeled levels, L1–L4, at 14 ft 8 in floor-to-floor. It does **not** label a fifth occupied story. The model/audit object `KNOY_FloorSlab_L5` remains **unverified/source conflict**; do not infer a fifth story from its name or assume it is a roof slab.

The cached GIS extrusion is 48 ft. A separate coarse LiDAR assessment (`audit/complete_knoy/roof_height_assessment_r8.json`) uses Indiana 2016–2020 QL2 3DEP, tile `in2018_30001885_12`, acquired 2018-04-20; 5 ft DSM cells, US survey feet, NAD83(HARN) / Indiana West (ftUS). Reported roof-footprint DSM quantiles p10 30.42 ft, p25 45.23, p50 59.88, p75 60.12, p90 63.90 above sampled terrain; DSM median is 680.94 ft and sampled bare-earth median 621.06 ft. Spread includes lower roofs, edges, voids and equipment. It is not a parapet or single-plane height. The 48 ft extrusion and LiDAR distribution conflict; neither provides a defensible as-built height.

PV evidence is limited to the 2017 reported 28 modules on tilted silver racks. Later overhead imagery suggests an array but does not verify current count, orientation, dimensions, zone or relation to the old installation.

## Face-specific partial opening and detail schedule

No source gives a registered continuous elevation of all sides. Record only what is visible; never mirror counts to unseen walls.

| Face/view key | Observed sequence | Confidence / gaps |
| --- | --- | --- |
| K-SV25 candidate edge 18 | Brick wall with thin horizontal glazing and broad opaque brick intervals | Medium for vocabulary, low for edge assignment; count, spacing, floor, sash/mullions and endpoints unknown |
| K-ARCH1125 visible long wall | At least one extended slit-window run broken by multiple broad brick panels/piers; pale horizontal coping | Medium for visible historic pattern; exact count, length, floor and current condition unknown |
| K-ARCH1126 entrance/junction | Dark/recessed entrance zone, lower strip glazing and interrupted upper ribbon near wing junction; ramp/rail approach | Medium for feature presence; door leaves, bay count, compass direction and current condition unknown |
| K-HIST18 entrance | Recessed glazed/door group under projecting canopy; ramp with rails, stairs and low retaining/planter walls | Medium for composition, low for dimensions; door count, canopy support/profile, ramp/stair dimensions and exact face unknown |
| K-POLY name zone | Brick, narrow dark horizontal windows, light coping, wall-mounted building-name treatment | Medium for presence; letter size/support/alignment and adjacent opening run unknown |
| Other outer/end/inner elevations | No continuous registered schedule in retained sources | Unknown; do not extrapolate from the partial runs above |

## Materials and signature details

- **Wall:** reddish/dark red-brown brick across profile, archive, entrance and street views. Color is uncalibrated and varies with lighting/age; bond, mortar, unit module and face-specific changes are not resolved.
- **Glazing:** dark, narrow horizontal slit/ribbon openings, interrupted by opaque brick panels; a lower strip appears in the archive entrance view. Frame finish, reflectance, mullions, reveals, sill/head details and counts are unknown.
- **Coping/trim:** pale cap/band at wall tops and stepped roof edges. Concrete, stone or metal cannot be distinguished; profile and projection unmeasured.
- **Entrance:** dark recessed glazing/doors beneath projecting canopy, stairs, accessible ramp/rails and low retaining/planter walls. Current close-ups and an oriented entry plan are needed for geometry. Trees and planting are seasonal context, not architecture.
- **Roof:** low-slope/flat fields with parapets, mechanical/penthouse-like masses and historically documented PV racks. Membrane, equipment schedule and parapet section unknown.

## Later-builder constraints

Use the irregular GIS envelope only as an orientation/registration constraint and verify actual wall offsets, setbacks and recesses independently. Preserve stepped low-wing and taller brick masses and varying parapet levels. The documented visual vocabulary is red-brown brick, horizontal dark glazing runs broken by broad brick panels, pale coping, and a recessed canopied entrance with ramp/stair approach. Tie every observed run to its named source and do not project its rhythm around corners. Keep court/roof topology, L5, height, equipment and current PV arrangement unresolved. The 14 ft 8 in interval applies only to documented L1–L4 in the planning study.

## Discrepancy and gap register

| Issue / affected area | Existing evidence and limitation | Evidence needed / effect |
| --- | --- | --- |
| Orientation and complete walkaround | Only K-SV25 has a pose; its ray is an approximate edge-18 candidate. Archive/profile views are unregistered. | Current geolocated corner-to-corner photos with heading and labeled faces; needed to assign all facade schedules. |
| Openings by face and floor | Photos are partial, distant, oblique or occluded; no continuous registered elevation. | Purdue/architect record elevations or straight-on current photos of every long, end and inner face; needed for counts, spacing and floor association. |
| Entrance/canopy/access | Presence is visible, but profiles, dimensions, face ownership and current condition are not. | Current close-ups plus oriented entry plan or survey; affects prominent silhouette and access geometry. |
| Roof/court topology and plant | Orthos show several fields and large masses but cannot classify all court/terrace/lower roof boundaries or equipment. | Georeferenced as-built roof plan, oblique roof photos, or classified point cloud; affects major massing. |
| L5 and building height | Study labels L1–L4 only; 48 ft cache extrusion conflicts with broad DSM distribution. | Original Purdue UA141 plans/sections or verified height survey; story count and roof datum remain unknown. |
| Current PV | 2017 article documents 28 panels; later ortho is suggestive only. | Current overhead photo or facilities PV record; affects roof detail, not primary volume. |
| Materials and condition | Brick and pale coping are visible but uncalibrated; exact brick/mortar, coping material, frame finish and repairs unknown. | Facilities specifications/material schedule or close daylight photos on multiple faces. |
| Renovation chronology | Archive images cataloged to 1990s/2000s but undated; entrance publication date is not capture date; Street View is 2025. | Dated owner photos and renovation/as-built records, especially for doors, glazing and roof. |
| Primary records | Purdue Archives UA141 floor-plan and UA62 construction-image leads are physical/catalog records, not digitized drawings inspected here. | Inspect or request scans of original files with sheet dates and provenance. |
| Scribd drawing lead | Repeated Knoy title blocks conflict with 2019 Chesterton student-project metadata and Purdue dimensions. | Do not reuse without authenticated Purdue/architect provenance; presently unsuitable. |

**Disposition:** the pass establishes broad massing and facade vocabulary, a partial entrance/roof record, and four planning levels. It does not establish complete elevations, opening counts, as-built dimensions, court topology or one defensible roof height. Significant gaps remain; no model or readiness decision is changed.
