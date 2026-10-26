# South Hall build record — R2

**Asset:** `modular/buildings/south_hall.blend`  
**Building ID / collection / local root:** `south_hall` / `Asset_south_hall` / `AssetRoot_south_hall`  
**Revision date:** 2026-10-25  
**R2 asset SHA-256:** `f0358b1cc5c9a9b1fbe0f0aefd99c618b9f7a2dfa46fb50d2fafd51e19e7c03c`

## Independent review response

R1 received **7.8/10**, below the 8.0 acceptance threshold. The reviewer identified four concrete gaps: a missing prominent full-height glazed bay/atrium visible in Purdue's 2026 construction photo; overly repetitive window sizing; weak roof/eave articulation; and a ground-floor cutaway that read as isolated sample modules rather than connected public areas.

R2 addresses those items while preserving the full GIS-ground-outline comparison and the explicit labels on estimated heights and the connector split:

1. Added a two-face, full-height glazed bay at an approximate outer corner, spanning the seven upper residential levels. Its 6 m facade runs, dark perimeter/vertical mullions, and level transoms are based on the prominent multi-storey glazed corner visible in Purdue's 2026 construction image. Nearby punched windows are suppressed to avoid collisions. The source image is not georegistered to the GIS facade; the chosen corner, extent, interior depth, and bay dimensions remain approximate.
2. Kept the 3.25 m residential window bay rhythm but alternated the window module between broader lounge/room glazing (1.48 × 1.92 m) and narrower bedroom openings (1.18 × 1.78 m). These dimensions/patterns are visual interpretations of the photo, not a published window schedule.
3. Retained the low-confidence flat membrane, with darker restrained 6 m seam detailing and subtle surface variation. No usable roof image or construction detail is available, so no unsupported rooftop equipment or roof assembly is claimed.
4. Added a continuous schematic public-area route from the MacArthur-side entry through the lobby and dining to the game/lounge zone, with differentiated public-area floor patches. The ground-floor cutaway now shows the Level 01 floor and connected route; the nine schematic lab modules and representative bedroom are hidden in this particular review view so they do not read as disconnected ground-floor rooms. They remain in the asset and remain labeled schematic.

## Source basis

| Evidence | Provider / identifier | Date and use |
|---|---|---|
| [Purdue BuildingShapesZip4 ArcGIS feature query](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D528&outFields=*&returnGeometry=true&outSR=4326&f=geojson) | Purdue-linked campus GIS; `FID=528`, `BLDG_ABBR=SH`, GlobalID `{FBB17D8A-34ED-4E5F-BA58-43089D065963}`; `201 N Macarthur Dr` | Retrieved 2026-10-25. Query returns EPSG:4326; source layer reports EPSG:3857 (WKID 102100). Raw response: `raw_south_hall_fid528.geojson`. Feature dates are blank. |
| [Purdue Board of Trustees, Hillenbrand Residence Hall South, Exhibit A](https://www.purdue.edu/bot/meetings/past-meetings/2023/07.%20aug/pfc/Hillenbrand%20Residence%20Hall%20South.pdf) | Purdue Administrative Operations; plan dated 2023-07-24; PDF metadata created 2023-07-31 | Distinguishes blue residential area and tan dining/link arm. Captured PDF: `purdue_board_hillenbrand_south_siteplan_2023.pdf`; page image: `board_siteplan-6.png`. The plan is not georeferenced. |
| [Purdue Residences — South Hall](https://housing.purdue.edu/my-housing/options/residence-halls/south-hall.html) | Purdue University Residences | Retrieved 2026-10-25. Confirms eight-story program, address, amenities, and connection with Hillenbrand. Used for program, not measured geometry. |
| [Purdue construction update, January 2025](https://housing.purdue.edu/news/2025_0115-construction-ambassadors-south-hill.html) | Purdue University Residences | Eight floors, 252,525 sq ft, and progress imagery. Narrative area is not used as a footprint measurement. |
| [Purdue 2026 South Hall feature](https://www.housing.purdue.edu/get-reconnected/2026/03/special-feature3.html) | Purdue University Residences | Retrieved 2026-10-25; exterior/interior reference photos. Captured photos: `purdue_southhall_exterior_construction_2026.jpg` and `purdue_southhall_mainfloor_2026.jpg`. The exterior image provides the full-height glazed-bay cue; it may show construction-stage details. |

## Footprint, placement, and height checks

The full base/podium remains the complete FID 528 polygon. It has 83 raw vertices, simplified to 53 vertices with topology-preserving 0.50 m tolerance after the project's local conversion at `(40.4274° N, 86.9137° W)`. The project-local placement offset remains `[-1091.6500244, -131.2249985]` m. Simplified area is 3,434.516 m² (raw projected area 3,436.52 m²; 0.0583% change; maximum source-to-simplified displacement 0.383 m). The derived coordinate conversion is approximate, not surveyed.

The registered outline comparison is `official_footprint_vs_asset_r2.png`; reopened base-mesh area is 3,434.516 m² and its maximum vertex-to-source-vertex distance is 0.00000224 m. The mesh was generated directly from that same GIS outline, so this verifies coordinate construction, not independent survey accuracy or a structural-wall boundary.

As in R1, the non-georeferenced site plan is compared with the GIS morphology using a Y=5 m split. The estimated eight-storey residential shell covers 3,180.967 m²; the estimated one-storey north dining/link portion covers 253.549 m². The full 3,434.516 m² base remains intact. The split and its endpoint are approximate (about 3 m); no off-site tunnel is drawn beyond the GIS polygon because the plan endpoint cannot be registered reliably.

GIS reports `NUM_LEVELS=8` and floor fields `F01=621.85` through `F08=695.85`, plus `R=705.85`. Interpreting relative intervals as feet gives 84 ft (25.603 m) from F01 to roof: 14 ft for the first interval, then seven 10 ft intervals. Units and vertical datum are not documented, so roof elevation is an estimate, not a surveyed absolute height. The north link stays at the one-storey glazed podium height, 4.267 m.

## Interior treatment and review files

Purdue confirms the amenity program, including nine Data Mine learning labs and dining/lounge/game functions, but no room-by-room plan was located. The public route, area carpets, lab partitions/furniture, lounge/game props, and representative double room remain schematic and must not be read as surveyed placement or exact room adjacencies. The ground-floor R2 cutaway is intentionally a public-space/circulation review, not a complete architectural floor plan.

R2 review images:

- `south_hall_human_scale_east_entry_r2.png` — entry, repeated windows, and atrium bay.
- `south_hall_oblique_full_r2.png` — high residential shell, low north link, and overall footprint.
- `south_hall_schematic_ground_floor_cutaway_r2.png` — connected public circulation and amenity zones.
- `official_footprint_vs_asset_r2.png` — registered GIS polygon/base-mesh overlay.

Fresh Blender 5.2.3 reopen validation is in `validation_r2.json`; it confirms the asset collection/root, no materialless mesh or unpacked image dependencies, and the R2 asset hash above. R2 was not committed, and the master/shared indexes were not touched.

## Remaining uncertainties

- The ArcGIS outline is not a certified wall survey; full GIS envelope and high-shell structural boundary remain separate concepts.
- The blue/tan site-plan split and exact Hillenbrand-link endpoint are approximate; a georeferenced architectural/site plan could materially refine both.
- The 2026 facade image supports a multi-storey glazed bay, but its exact location on the GIS footprint cannot be matched conclusively. Bay placement/dimensions and alternating window sizes remain estimates.
- Absolute heights/vertical units, roof build-up/seam spacing, final cladding details, entry dimensions, and floor-by-floor interiors remain unverified.
