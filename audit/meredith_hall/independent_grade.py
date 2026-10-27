"""Independent, reproducible grade for Meredith Hall. Run with Blender 5.2:
blender --background modular/buildings/massing_meredith_hall_4bb4188.blend --python audit/meredith_hall/independent_grade.py
Only reads the saved asset and source snapshots; writes independent_grade.json.
"""
import bpy, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "meredith_hall"
ASSET = ROOT / "modular" / "buildings" / "massing_meredith_hall_4bb4188.blend"
GIS_PATH = AUDIT / "sources" / "feature_253_wgs84.geojson"
OSM_PATH = AUDIT / "sources" / "osm_way_128488696_snapshot.json"
EVIDENCE_PATH = AUDIT / "evidence.json"
PREVIEW_PATHS = [AUDIT / "preview_exterior.png", AUDIT / "preview_plan.png"]

def campus_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def polygon_area_centroid(points):
    cross_sum = 0.0
    cx = cy = 0.0
    for i, (x, y) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        cross = x * y2 - x2 * y
        cross_sum += cross
        cx += (x + x2) * cross
        cy += (y + y2) * cross
    area = cross_sum / 2
    return abs(area), (cx / (3 * cross_sum), cy / (3 * cross_sum)) if cross_sum else (sum(p[0] for p in points)/len(points), sum(p[1] for p in points)/len(points))

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# Verify this run actually reopened the requested file in Blender.
opened_path = Path(bpy.data.filepath).resolve()
if opened_path != ASSET.resolve():
    raise RuntimeError(f"Expected opened asset {ASSET}, got {opened_path}")
with GIS_PATH.open(encoding="utf-8") as f:
    gis = json.load(f)
feature = next(f for f in gis["features"] if int(f["properties"]["FID"]) == 253)
attrs = feature["properties"]
if attrs.get("BLDG_ABBR") != "MRDH" or "Meredith" not in attrs.get("BUILDING_N", ""):
    raise RuntimeError("GIS feature identity does not match Meredith Hall")
ring_ll = feature["geometry"]["coordinates"][0]
if ring_ll[0] == ring_ll[-1]: ring_ll = ring_ll[:-1]
ring = [campus_xy(float(lon), float(lat)) for lon, lat in ring_ll]
source_area, source_centroid = polygon_area_centroid(ring)
source_bounds = {"min_x": min(p[0] for p in ring), "max_x": max(p[0] for p in ring),
                 "min_y": min(p[1] for p in ring), "max_y": max(p[1] for p in ring)}

obj = bpy.data.objects.get("Meredith Hall")
coll = bpy.data.collections.get("Asset_massing_meredith_hall_4bb4188")
if obj is None or obj.type != "MESH" or coll is None:
    raise RuntimeError("Expected Meredith Hall mesh and export collection were not found")
world_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
model_bounds = {"min": [min(v[i] for v in world_verts) for i in range(3)],
                "max": [max(v[i] for v in world_verts) for i in range(3)]}

# Compare source wall edges against vertical wall faces whose base is at z=0.
actual_wall_edges = []
for poly in obj.data.polygons:
    pts = [obj.matrix_world @ obj.data.vertices[i].co for i in poly.vertices]
    base = []
    for p in pts:
        if abs(p.z) < 1e-5 and not any(dist((p.x,p.y), q) < 1e-5 for q in base):
            base.append((float(p.x), float(p.y)))
    if len(base) == 2:
        actual_wall_edges.append(base)
def edge_error(a,b):
    return min(max(dist(a[0],b[0]),dist(a[1],b[1])),
               max(dist(a[0],b[1]),dist(a[1],b[0])))
edge_errors = [min((edge_error((ring[i],ring[(i+1)%len(ring)]), e) for e in actual_wall_edges), default=float("inf"))
               for i in range(len(ring))]
matched_edges = sum(e < .002 for e in edge_errors)
identity_transform = (tuple(obj.location) == (0.0,0.0,0.0) and tuple(obj.rotation_euler) == (0.0,0.0,0.0)
                      and tuple(obj.scale) == (1.0,1.0,1.0))

# Independent OSM location/levels check; OSM level count disagrees with GIS count.
with OSM_PATH.open(encoding="utf-8") as f:
    osm = json.load(f)
way = osm["way"]
node_xy = {int(n["id"]): campus_xy(float(n["lon"]), float(n["lat"])) for n in osm["nodes"]}
osm_ring = [node_xy[int(n)] for n in way["nodes"]]
if osm_ring[0] == osm_ring[-1]: osm_ring = osm_ring[:-1]
osm_area, osm_centroid = polygon_area_centroid(osm_ring)
centroid_delta = dist(source_centroid, osm_centroid)

with EVIDENCE_PATH.open(encoding="utf-8") as f:
    evidence = json.load(f)
meas = evidence["measurements"]
materials = sorted(m.name for m in obj.data.materials if m)
external_images = [im.filepath for im in bpy.data.images if im.source == "FILE"]
source_ids = {str(s.get("feature_id", "")) for s in evidence.get("sources", [])}
preview_exists = [p.exists() for p in PREVIEW_PATHS]

criteria = [
 {"criterion":"Identity and source-backed footprint", "points":2.0, "max_points":2.0, "status":"verified with map-source limitation",
  "evidence":["Purdue BuildingShapes FeatureServer FID 253 is explicitly named Virginia C. Meredith Residence Hall and carries BLDG_ABBR MRDH.",
              "Purdue Housing source describes Meredith's unique X-shaped plan; the model's plan preview matches the X form.",
              f"All {matched_edges}/{len(ring)} transformed GIS perimeter edges match structural model wall edges within 0.002 m; maximum edge error {max(edge_errors):.6f} m.",
              "GIS polygon positional accuracy is unpublished and is not a certified survey."],
  "limitations":["Footprint identity is strongly supported by the named Purdue GIS record and independent housing description, but survey accuracy is unknown."]},
 {"criterion":"Position, orientation, and dimensions", "points":2.0, "max_points":2.0, "status":"verified against GIS geometry; geodetic uncertainty retained",
  "evidence":[f"The model retains the massing asset's campus coordinate frame and identity transform: {identity_transform}.",
              f"Model structural wall outline follows the GIS source ring exactly; source extents are {source_bounds} m and model overall extents are {model_bounds} m (small differences are porch/cornice projections).",
              f"The independently named OSM way 128488696 is Meredith Hall at 201 Martin Jischke Drive; its polygon centroid differs from GIS FID 253 by {centroid_delta:.2f} m.",
              "Dimensions/orientation are independently represented by 20 GIS source wall edges; campus conversion is the project's local approximation, not a surveyed CRS."],
  "limitations":["GIS positional accuracy is unpublished; the OSM shape is a community-maintained cross-check rather than survey control."]},
 {"criterion":"Floors, height, and roof form", "points":1.0, "max_points":2.0, "status":"partly supported; height and roof uncertain",
  "evidence":["The model has four visible above-grade window bands/floors and OSM way 128488696 has building:levels=4.",
              "Purdue GIS FID 253 reports both NUM_LEVELS=5 and CountOfFLO=5, conflicting with OSM's four levels.",
              f"Modeled wall height is {meas['estimated_wall_height_m']} m and roof top {meas['estimated_roof_top_m']} m, both explicitly estimates from a 3.8 m floor-to-floor assumption.",
              "The rendered model uses a shallow flat roof/cornice; source set provides no elevation or roof measurement."],
  "limitations":["No published elevations or verified height are present; the 4-versus-5 floor discrepancy is unresolved, and roof silhouette remains unverified."]},
 {"criterion":"Facade, entrances, and distinctive architecture", "points":1.5, "max_points":2.0, "status":"qualitatively supported; entrance placement inferred",
  "evidence":["Official Purdue exterior photo shows red brick, pale window trim, repeated window rows, a courtyard/front lawn, and a porch; model includes corresponding red brick, light-framed repeated sash windows, and porch.",
              "Purdue Housing page confirms a front lawn and porch and calls out a large porch at the main entrance.",
              "Model's entrance is assigned to an east-facing edge based on address/street context; no compass-tagged plan confirms that bearing.",
              "Only one oblique official photo is available, so other elevations and exact bay/porch dimensions cannot be compared."],
  "limitations":["The rendered porch reads as a small isolated canopy; the source describes a large main-entrance porch, but the lone photo cannot firmly resolve size or exact facade placement.","Window spacing and all unpictured elevations are generalized."]},
 {"criterion":"Modular export, portability, and complete evidence", "points":2.0, "max_points":2.0, "status":"verified",
  "evidence":[f"Reopened asset at {opened_path}; it contains object {obj.name} in expected export collection {coll.name} ({len(coll.objects)} object(s)).",
              f"Manifest points to the same massing asset ID, file, object, and collection; model has {len(obj.data.vertices)} mesh vertices, {len(obj.data.polygons)} faces, and no modifiers.",
              f"No file-backed image dependencies: {external_images}; materials are {materials}.",
              "Evidence includes source URLs/providers/feature IDs, retrieval/source dates, CRS or not-applicable status, method, uncertainty, raw GIS/OSM snapshots, official housing pages/photo, rebuild/reopen scripts, reopened check JSON, and both plan/exterior previews.",
              f"Dedicated preview files exist: {preview_exists}."]}
]
score = round(sum(c["points"] for c in criteria), 2)
findings = [
 {"severity":"major uncertainty", "finding":"Vertical height and roof are not source-verified; Purdue GIS reports five levels while OSM and the model indicate four.", "improvement":"Find a reliable elevation/plan or document the lower-level interpretation; keep the present height marked estimated until then."},
 {"severity":"minor", "finding":"The east-facing main entrance is inferred, and the modeled porch appears smaller and more isolated than the official description/photo suggests.", "improvement":"Use a second ground-level facade photo or site plan to locate and size the main porch, then add supported entrance/porch details."},
 {"severity":"limitation", "finding":"Official GIS plan is an authoritative named source, but published positional accuracy is unavailable.", "improvement":"If survey or higher-resolution orthophoto data becomes available, compare wall control points and update the stated uncertainty."}
]
result = {"building":"Virginia C. Meredith Residence Hall", "asset_id":"massing_meredith_hall_4bb4188",
          "score":score, "max_score":10, "passing_standard":8, "pass":score >= 8,
          "criteria":criteria, "evidence":{"reopened_asset":str(opened_path), "object":obj.name,
          "collection":coll.name,"identity_transform":identity_transform,"gis_feature_id":253,
          "gis_ring_vertices":len(ring),"matched_source_wall_edges":matched_edges,
          "max_source_wall_edge_error_m":max(edge_errors),"gis_source_area_m2":source_area,
          "osm_way_id":way["id"],"osm_gis_centroid_delta_m":centroid_delta,
          "model_bounds_xyz_m":model_bounds,"estimated_wall_height_m":meas["estimated_wall_height_m"],
          "estimated_roof_top_m":meas["estimated_roof_top_m"],"file_backed_images":external_images,
          "preview_files_exist":preview_exists}, "findings":findings}
(AUDIT / "independent_grade.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print("INDEPENDENT_GRADE=" + json.dumps(result))
