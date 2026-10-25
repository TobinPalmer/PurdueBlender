# Owen Hall independent regrade — R2 asset and manifest

**Score: 8.0/10 — meets the 8/10 building-grade threshold.** This grade applies only to the current modular asset at SHA-256 `20ccd340d7cc2ab06ac6e94a84394c3d8ae0ec84573a1222e9ed541dbb19e981`. The master-library refresh is still a separate coordinator task and was not inspected or claimed here.

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Reopened wall-base outline matches Purdue GIS OBJECTID 38 in the project coordinate approximation (IoU 1.000; coverage 1.000). |
| Placement, orientation, and scale | 1.8/2 | Asset root is identity; manifest origin and dimensions align. The project transform is approximate and the new master marker has not been refreshed/reopened. |
| Height, floors, and roof form | 1.4/2 | Purdue's report supports four stories and H-shape; the flat roof silhouette is visible in the official photo. Absolute height and floor elevations remain estimates. |
| Facade and material fidelity | 1.2/2 | Brick/stone bands and a repeated window rhythm are represented with additional frames/louvers. Large glazed bays, lower facade panels, and exact opening details remain simplified. |
| Interior, portability, and asset/manifest integrity | 1.6/2 | A representative room vignette follows Purdue's approximate standard-room dimensions. The file reopens with 958 objects; its object list and bounds match the refreshed manifest. Complete as-built interiors and master integration remain outstanding. |
| **Total** | **8.0/10** | **Passes the independent asset-grade threshold; master integration is pending.** |

## Independent checks

- Blender 5.2.3 LTS reopened the current asset. `Asset_owen_hall` contains 958 objects (934 meshes, 18 lights, 5 cameras, 1 empty).
- SHA-256 is `20ccd340d7cc2ab06ac6e94a84394c3d8ae0ec84573a1222e9ed541dbb19e981`, matching the requested current asset.
- Manifest inventory matches all reopened object names exactly; count is 958 and the complete mesh bounds match to within 1 mm.
- No unassigned mesh material slots, external image paths, or external library paths were found; 21 unique node materials are assigned.
- Independent GIS polygon comparison produced IoU 1.000000, coverage 1.000000, center error 0.000001 m, and envelope dimensions 87.623 × 107.558 m (GIS) versus 87.623 × 107.558 m (model).
- The root master blend has not been refreshed and reopened for this asset hash; no campus integration score is claimed.

## Source-supported limits

The Purdue report supports the H-shaped, four-story residence hall, while the current official housing page supplies an approximate standard double-room layout and dimensions. Neither source provides measured building elevations or a complete as-built interior plan. The 16 m overall height, floor elevations, and placement of repeated room modules remain estimates/illustrative. The official facade photo supports broad brick/stone character and window patterns, but it does not establish surveyed facade dimensions.

## References

- Purdue campus map GIS OBJECTID 38: https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0/query?where=OBJECTID%3D38&outFields=*&returnGeometry=true&outSR=4326&f=pjson
- Purdue Office of Special Events and News, [Report of Findings (2007)](https://www.purdue.edu/uns/x/2007b/070702RimkusFinal.pdf), describing a four-story H-shaped hall and including a ground-level plan.
- Purdue University Residences, [Owen Hall](https://www.housing.purdue.edu/my-housing/options/residence-halls/owen.html), with official exterior image, standard-room dimensions, approximate-layout caveat, and room furnishing description.
- Local evidence snapshots and renders are listed in `source_provenance.json`, `gis_footprint_validation.json`, `independent_reopen_r3.json`, `owen_hall_facade.png`, `owen_hall_standard_room_vignette.png`, and `owen_hall_gis_footprint_topdown.png`.
