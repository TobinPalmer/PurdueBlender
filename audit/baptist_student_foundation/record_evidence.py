"""Normalize the selected source feature and record comparison provenance."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
raw_path = SOURCES / "indiana_lidar_building_footprints_near_bsf_2026-10-25.geojson"
raw = json.loads(raw_path.read_text(encoding="utf-8"))
feature = next(f for f in raw["features"] if f["properties"].get("objectid") == 441814)
probe_path = HERE / "blender_probe.json"
probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path.exists() else {}
(SOURCES / "indiana_lidar_building_footprint_feature_441814_raw.json").write_text(
    json.dumps(feature, indent=2), encoding="utf-8"
)

radius = 6378137.0
ring = []
for mx, my in feature["geometry"]["coordinates"][0]:
    lon = math.degrees(mx / radius)
    lat = math.degrees(2 * math.atan(math.exp(my / radius)) - math.pi / 2)
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    ring.append((x, y))
if ring[0] == ring[-1]:
    ring.pop()

cross = [ring[i][0] * ring[(i + 1) % len(ring)][1]
         - ring[(i + 1) % len(ring)][0] * ring[i][1]
         for i in range(len(ring))]
area2 = sum(cross)
area = abs(area2) / 2
cx = sum((ring[i][0] + ring[(i + 1) % len(ring)][0]) * cross[i]
         for i in range(len(ring))) / (3 * area2)
cy = sum((ring[i][1] + ring[(i + 1) % len(ring)][1]) * cross[i]
         for i in range(len(ring))) / (3 * area2)
perimeter = sum(math.dist(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring)))
xs = [x for x, _ in ring]
ys = [y for _, y in ring]
old_center = (-433.908, -101.204)
offset = math.dist(old_center, (cx, cy))
bbox_center = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
bbox_offset = math.dist(old_center, bbox_center)

comparison = {
    "building_id": "massing_baptist_student_foundation_c3d8114",
    "source_feature_id": 441814,
    "source_retrieved": "2026-10-25",
    "source_date": "2018 lidar collection; statewide dataset publication date 2022-08-08",
    "source_crs": "EPSG:3857 (Web Mercator; service spatial reference 102100/3857)",
    "local_frame": "EPSG:3857 vertices inverse-projected to geographic, then approximate Purdue campus local XY per modular/AGENTS.md: X=(lon+86.9137)*111412.84*cos(40.4274 radians), Y=(lat-40.4274)*111040",
    "source_geometry_metrics_local_m": {
        "vertex_count": len(ring), "area_m2": area, "perimeter_m": perimeter,
        "bounds_m": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)]},
        "centroid_m": [cx, cy],
    },
    "prior_massing_bbox_m": {
        "x": [-445.57794189453125, -422.2210998535156],
        "y": [-112.2392349243164, -90.18669128417969],
        "height_m": 16.0, "bbox_center_xy_m": list(old_center),
        "height_note": "Historical pre-revision simple-massing bound only; current reopened detailed asset height is recorded separately as 6.0 m.",
    },
    "prior_bbox_center_to_source_centroid_m": offset,
    "prior_bbox_center_to_source_bbox_center_m": bbox_offset,
    "revision": {
        "structural_footprint": "Feature 441814 vertex ring after inverse Web Mercator and local-frame transform; no fit-to-bounds scaling applied.",
        "estimated_vertical_design_m": {
            "main_wall_top_proxy": 4.5,
            "roof_crest_proxy": 6.0,
            "south_wing_wall_top_proxy": 4.5,
            "basis": "Design proxies guided by 2018 NDHM roof-surface samples (roughly 4.45 m p10 to 5.81 m p90 after canopy/outlier filtering); these are not measured eave/ridge elevations.",
        },
        "resulting_xy_envelope_m": [max(xs) - min(xs), max(ys) - min(ys)],
        "vertical_height_total_m": 6.0,
        "reopened_asset_bounds_m": probe.get("all_geometry_bounds_m"),
        "reopened_asset_collection_object_count": probe.get("collection_object_count"),
    },
    "uncertainty": "The Indiana statewide footprint is LiDAR-derived and not a survey. SHAPE__Area/Length are service properties in EPSG:3857 map units; local-plan metrics above use the repository approximate ground conversion. The 2018 NDHM is 5-ft resolution, normalized roof/vegetation surface height; 2-25 ft cells were retained for robust roof summaries, but possible canopy overlap remains. It does not provide measured eave/ridge values, exact floor count, gable pitch, facade rhythm, or entrance dimensions.",
}
(HERE / "footprint_comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")

sources = [
    {
        "role": "identity, address, photo, and facade cross-check",
        "provider": "The Found at Purdue (organization website)",
        "url": "https://www.thefoundatpurdue.org/",
        "feature_identifier": "Official organization; website states 200 N Russell St; exterior image official_web_image_5.jpg from 20181014-124554.jpg",
        "retrieved": "2026-10-25", "source_date": "2018-10-14 filename; exact capture date not independently confirmed",
        "crs": None,
        "method": "Official site states the address; its dated exterior image visually compared to the building location and footprint.",
        "uncertainty": "Low-resolution partial oblique exterior; no dimensioned plans or surveyed elevations found.",
    },
    {
        "role": "independent exterior photo and identity cross-check",
        "provider": "The Purdue Exponent, issue dated Aug. 17-18, 2017",
        "url": "https://bloximages.newyork1.vip.townnews.com/purdueexponent.org/content/tncms/assets/v3/editorial/c/c7/cc7ac664-843e-11e7-bdd5-335a6bc6456b/59972adb59de1.pdf.pdf",
        "feature_identifier": "2017-08-17 issue, printed page 19, ad for The Baptist Student Foundation at Purdue, 200 N Russell St",
        "retrieved": "2026-10-25", "source_date": "2017-08-17/18 issue", "crs": None,
        "method": "Photo printed with address and organization name; supports brick exterior, gabled principal roof, entry canopy, and apparent multiple levels.",
        "uncertainty": "Small monochrome halftone ad; exact window count, roof pitch, and height cannot be measured.",
    },
    {
        "role": "plan footprint and location",
        "provider": "Indiana Geographic Information Office / Polis Center at IUPUI; Indiana Statewide LiDAR Derived Building Footprints layer",
        "url": "https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0",
        "feature_identifier": "OBJECTID 441814, Tippecanoe County, LidarYear 2018",
        "retrieved": "2026-10-25", "source_date": "2018 lidar; metadata publication date 2022-08-08",
        "crs": "EPSG:3857 (layer reports wkid 102100/latestWkid 3857)",
        "method": f"Queried polygons within 80 m of manifest placement. Selected 441814: source polygon bbox center is within {bbox_offset:.3f} m of prior massing bbox center; its polygon area centroid is {offset:.3f} m from that center because the southern stem shifts the centroid. It has an 8-vertex T-shaped outline plus a closing coordinate. Vertices were inverse-projected then transformed to repository local XY. No scale fitting applied.",
        "uncertainty": "Automated LiDAR footprint extraction, published as-is; not a survey. Service area/perimeter use map-plane units, while local metrics apply the project local conversion.",
    },
    {
        "role": "roof form and plan confirmation",
        "provider": "Indiana Geographic Information Office, Indiana 2023 Imagery ImageServer",
        "url": "https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer",
        "feature_identifier": "Exported 1400x1400 JPG, Web Mercator bbox around feature centroid; 2023 county orthophoto",
        "retrieved": "2026-10-25", "source_date": "2023",
        "crs": "EPSG:3857 export bbox; image has no embedded CRS; export parameters and service metadata preserved beside it",
        "method": "Plan-view comparison: T-shaped footprint aligns with T-shaped roof, with north crossbar and southern projecting wing; roof edge and ridge details are visually estimated.",
        "uncertainty": "Orthophoto cannot verify wall height, floors, facade, or entrance.",
    },
    {
        "role": "roof-surface height estimate",
        "provider": "Purdue Geospatial Data Science Lab / Indiana Digital Forestry, Indiana 2017-2019 3DEP LiDAR NDHM",
        "url": "https://giselevationingov.s3.us-east-2.amazonaws.com/ndhmoptimized/statewide/2018/SPW/5ft/in2018_29951885_12_ndhm.tif",
        "feature_identifier": "Tippecanoe 2018 NDHM tile in2018_29951885_12_ndhm.tif; queried BStF tile footprint OBJECTID 35356; 5-ft pixels",
        "retrieved": "2026-10-25", "source_date": "2018 LiDAR collection", "crs": "EPSG:2968 NAD83(HARN) Indiana West (ftUS)",
        "method": "Sampled raster cell centers inside feature 441814 after projection from EPSG:3857. 191 raw cells were sampled; 177 values between 2 and 25 ft were retained for robust roof-surface quantiles. p10–p90 are approximately 4.45–5.81 m overall; crossbar and south stem medians are 5.07 m and 5.14 m. Source tile, tile query, and reproducible sampling script/results are preserved beside this record.",
        "uncertainty": "5-ft cells, automated footprint, and tree canopy/edge mixing limit the reading. NDHM values are normalized roof/vegetation surface heights and are not measured wall, eave, or ridge elevations. Values above 25 ft were excluded as likely canopy returns, but some vegetation may remain; no floor count or roof pitch is directly measured.",
    },
    {
        "role": "Purdue historical context check",
        "provider": "Purdue University Libraries, Campus Buildings Historic Database / Purdue Campus GIS",
        "url": "https://collections.lib.purdue.edu/campus/ ; https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0",
        "feature_identifier": "Purdue campus GIS search within 150 m; legacy campus layer did not return this current off-campus foundation; nearby historic features saved as context only",
        "retrieved": "2026-10-25", "source_date": "campus GIS time extent through 2015; no match for current Baptist Student Foundation",
        "crs": "EPSG:3857",
        "method": "Recorded negative search result to avoid confusing a historic Baptist Church record elsewhere with this building.",
        "uncertainty": "The Found is adjacent to but outside the historic campus layer coverage; current organization address and Exponent ad support identity.",
    },
]
record = {
    "building_id": comparison["building_id"],
    "name": "Baptist Student Foundation at Purdue / The Found",
    "manifest_asset": "modular/buildings/massing_baptist_student_foundation_c3d8114.blend",
    "manifest_collection": "Asset_massing_baptist_student_foundation_c3d8114",
    "sources": sources,
    "geometry_and_design": comparison,
    "validation": {
        "asset_rebuilt_from_source": True,
        "source_snapshot_preserved": True,
        "reopened_blender_probe": "audit/baptist_student_foundation/blender_probe.json",
        "reopened_asset_bounds_m": probe.get("all_geometry_bounds_m"),
        "reopened_asset_collection_object_count": probe.get("collection_object_count"),
        "mesh_topology": probe.get("mesh_topology"),
        "rendered_preview": "audit/baptist_student_foundation/preview.png",
        "rendered_roof_plan_view": "audit/baptist_student_foundation/roof_plan_view.png",
        "remaining_uncertainty": [
            "No published measured heights or floor plans located.",
            "Vertical design proxies are estimates guided by 2018 NDHM roof-surface quantiles; no eave/ridge elevations or floor count are measured. Facade windows, entrance dimensions/location, roof pitch, and colors remain approximate from dated imagery.",
            "The NDHM sample distribution is similar on the north crossbar and south stem; a distinct low roof level is not supported by these samples.",
            "The 2018 LiDAR footprint is automated; no cadastral or boundary survey was available.",
        ],
    },
}
(HERE / "build_evidence.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps({"metrics": comparison["source_geometry_metrics_local_m"], "centroid_offset_m": offset, "bbox_center_offset_m": bbox_offset}, indent=2))
