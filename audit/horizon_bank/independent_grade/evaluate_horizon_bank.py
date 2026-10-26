import bpy
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_horizon_bank_debc8f2"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS = ROOT / "audit" / "horizon_bank" / "sources" / "indiana_footprint_objectid_430274_2026-10-26.json"
OUT = Path(__file__).resolve().parent / "grade_result.json"
EXPECTED_SHA = "680582b359045eb790948391bf46831ead37059c100f4874333ebad67c4491fc"

sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha.lower() != EXPECTED_SHA:
    raise RuntimeError(f"Asset SHA changed before grading: {sha}")
source_doc = json.loads(GIS.read_text(encoding="utf-8"))
feature = source_doc["features"][0]
assert feature["id"] == 430274 and feature["properties"]["objectid"] == 430274
ring_closed = feature["geometry"]["coordinates"][0]
ring = ring_closed[:-1]
# Independently apply the project’s documented local conversion to the raw WGS84 ring.
source_xy = [((lon + 86.9137) * 84810.60416539927,
              (lat - 40.4274) * 111040.0) for lon, lat in ring]

def polygon_area(points):
    return abs(sum(points[i][0] * points[(i+1)%len(points)][1] -
                   points[(i+1)%len(points)][0] * points[i][1]
                   for i in range(len(points))) * 0.5)

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset = bpy.data.collections.get("Asset_" + ASSET_ID)
assert asset is not None
assert scene.name == "Building_" + ASSET_ID
all_objects = list(asset.all_objects)
mesh_objects = [o for o in all_objects if o.type == "MESH"]
shell = bpy.data.objects.get("Horizon_Bank_LiDAR_Footprint_Walls")
assert shell is not None and shell in all_objects
shell_world = [shell.matrix_world @ v.co for v in shell.data.vertices]
# The extrusion uses matching upper/lower rings; collapse to unique plan vertices.
model_xy = sorted(set((round(p.x, 5), round(p.y, 5)) for p in shell_world))

def nearest(a, b):
    return [min(math.dist(p, q) for q in b) for p in a]

source_to_model = nearest(source_xy, model_xy)
model_to_source = nearest(model_xy, source_xy)
max_xy_residual = max(source_to_model + model_to_source)
rms_xy_residual = math.sqrt(sum(d*d for d in source_to_model + model_to_source) /
                             len(source_to_model + model_to_source))
source_area = polygon_area(source_xy)
model_xy_in_source_order = [min(model_xy, key=lambda q: math.dist(p, q)) for p in source_xy]
assert len(set(model_xy_in_source_order)) == len(source_xy)
model_area = polygon_area(model_xy_in_source_order)
R = 6378137.0
mercator_xy = [(R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))
               for lon, lat in ring]
source_area_native_mercator = polygon_area(mercator_xy)
source_bounds = [[min(p[i] for p in source_xy), max(p[i] for p in source_xy)] for i in range(2)]
model_bounds = [[min(p[i] for p in model_xy), max(p[i] for p in model_xy)] for i in range(2)]

# Freshly inspect evaluated meshes, not the builder's saved validation report.
depsgraph = bpy.context.evaluated_depsgraph_get()
world_points = []
for obj in mesh_objects:
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    world_points.extend(ev.matrix_world @ v.co for v in mesh.vertices)
    ev.to_mesh_clear()
asset_bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
materials = sorted({m.name for obj in mesh_objects for m in obj.data.materials if m})
materialless_meshes = [o.name for o in mesh_objects if not any(m for m in o.data.materials)]
external_images = [{"name":i.name,"path":i.filepath,"packed":bool(i.packed_file)}
                   for i in bpy.data.images if i.source == "FILE"]
external_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
interior_scene = bpy.data.scenes.get("Horizon_Bank_Interior_Schematic_NOT_AS_BUILT")
interior_count = len(interior_scene.objects) if interior_scene else 0

assert len(ring) == 8 and len(model_xy) == 8
assert max_xy_residual < 0.001
assert asset in scene.collection.children_recursive
assert len(all_objects) == 80 and len(mesh_objects) == 79
assert not external_images and not external_libraries and not materialless_meshes
assert interior_scene is not None and interior_count == 10

criteria = [
  {
    "criterion":"Identity and source-backed footprint",
    "points_awarded":2.0,"points_possible":2.0,
    "evidence":"Horizon Bank’s official branch page identifies 1980 Northwestern Ave, West Lafayette. Raw Indiana LiDAR footprint objectid 430274 is an 8-vertex polygon at that site, from 2018-derived data. I independently transformed the raw WGS84 vertices into the project’s campus coordinates and compared them to the saved wall mesh: symmetric maximum nearest-vertex residual %.6f m; ground-projected polygon area %.2f m²; independently reprojecting the same ring to EPSG:3857 gives %.2f m², matching the layer area attribute %.2f m²."%(max_xy_residual,source_area,source_area_native_mercator,feature["properties"]["SHAPE__Area"]),
    "limitations":"The statewide LiDAR outline is not a surveyed legal wall boundary and may omit post-2018 changes."
  },
  {
    "criterion":"Position, orientation, scale, and dimensions",
    "points_awarded":2.0,"points_possible":2.0,
    "evidence":"The model’s eight distinct plan vertices register directly to the Indiana polygon with the project’s disclosed local transform; no additional translation, rotation, or scaling is needed. Source/model local XY bounds are %.3f/%.3f by %.3f/%.3f m and %.3f/%.3f by %.3f/%.3f m, respectively."%(source_bounds[0][0],source_bounds[0][1],source_bounds[1][0],source_bounds[1][1],model_bounds[0][0],model_bounds[0][1],model_bounds[1][0],model_bounds[1][1]),
    "limitations":"Accuracy inherits the approximate local degrees-to-meters projection and the source polygon’s cartographic tolerance."
  },
  {
    "criterion":"Evidence-backed height, floors, and roof form",
    "points_awarded":1.3,"points_possible":2.0,
    "evidence":"The April 2026 Google Street View pano shows a single visible occupied story, a raised central entry/sign tower, and a broad shallow dark roof. The asset reproduces those broad elements; evaluated Z bounds are %.2f to %.2f m."%(asset_bounds[2][0],asset_bounds[2][1]),
    "limitations":"No elevation or surveyed height source was found. Wall height 4.55 m and entry tower height 6.05 m are explicitly model estimates; the render’s roof surface is simplified and its precise pitch/edge profile cannot be verified from the oblique pano."
  },
  {
    "criterion":"Facade, entrances, and distinctive architecture",
    "points_awarded":1.6,"points_possible":2.0,
    "evidence":"The Street View reference shows red-brown masonry, pale vertical/jamb trim, repeated dark glazed bays, and a tall arched entry beneath a green Horizon sign. The model has corresponding brick/trim/glazing materials, four front window assemblies, side windows, the arched glazed doorway and sign tower. I visually compared the rendered exterior against the April 2026 panorama.",
    "limitations":"Street-level vegetation and perspective obscure parts of the facade. The exact masonry/stone specification, full window spacing on concealed elevations, and sign/door dimensions are not established by a measured elevation."
  },
  {
    "criterion":"Modular export, portability, and complete evidence",
    "points_awarded":2.0,"points_possible":2.0,
    "evidence":"Fresh-opened the exact SHA asset in Blender %s. Expected scene and exported collection are present, with %d export objects (%d meshes), %d named materials, all meshes assigned materials, no external image files, and no linked libraries. The interior is in a separate scene explicitly named as schematic/not-as-built. Source record includes official branch identity, raw LiDAR source and identifier, CRS/transform, retrieval/source dates, Street View pano and capture date, method, and uncertainty."%(bpy.app.version_string,len(all_objects),len(mesh_objects),len(materials)),
    "limitations":"Interior is only schematic because no as-built plan was available; this is disclosed in its scene name and source record."
  }
]
score = round(sum(c["points_awarded"] for c in criteria), 1)
assert score == 8.9
result = {
  "building":"Horizon Bank",
  "asset_id":ASSET_ID,
  "asset_path":"modular/buildings/"+ASSET.name,
  "asset_sha256":sha,
  "grade_type":"independent fresh-open evaluation",
  "blender_version":bpy.app.version_string,
  "score":score,"max_score":10,
  "criteria":criteria,
  "evidence":{
    "identity_source":"https://www.horizonbank.com/locations/west-lafayette",
    "identity_claim":"Official branch page lists 1980 Northwestern Ave, West Lafayette, Indiana.",
    "footprint_source":"https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0/query?objectIds=430274&outFields=*&returnGeometry=true&outSR=4326&f=geojson",
    "raw_footprint_snapshot":"audit/horizon_bank/sources/indiana_footprint_objectid_430274_2026-10-26.json",
    "footprint_object_id":430274,
    "source_ring_vertices":len(ring),"model_plan_vertices":len(model_xy),
    "source_area_m2_from_transformed_vertices":source_area,
    "reported_source_area_m2":feature["properties"]["SHAPE__Area"],
    "model_outline_area_m2":model_area,
    "source_area_from_wgs84_in_local_ground_frame_m2":source_area,
    "source_area_recomputed_in_native_epsg3857_m2":source_area_native_mercator,
    "area_method_note":"The feature attribute SHAPE__Area is calculated in the service native Web Mercator frame, while the footprint vertices are returned in WGS84. For a like-for-like comparison, both the source and model polygons are measured in the project local frame; no mismatch is inferred from their different projection areas.",
    "symmetric_max_vertex_residual_m":max_xy_residual,
    "symmetric_rms_vertex_residual_m":rms_xy_residual,
    "source_bounds_xy_m":source_bounds,"model_bounds_xy_m":model_bounds,
    "google_street_view":"https://www.google.com/maps/place/Horizon+Bank/@40.4480882,-86.92279,219a,37.5y,138.84h,90t/data=!3m7!1e1!3m5!1sBEIDnVCsMXxMoQp6FvbLUA!2e0!6shttps:%2F%2Fstreetviewpixels-pa.clients6.google.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D0%26panoid%3DBEIDnVCsMXxMoQp6FvbLUA%26yaw%3D138.84352!7i16384!8i8192!4m9!3m8!1s0x8812fd3f60727997:0xb8169804a15fbb8a!8m2!3d40.4477521!4d-86.9224333!10e5!14m1!1BCgIgARICCAI!16s%2Fg%2F11f3_lhfct?entry=ttu",
    "street_view_observed":"Google Street View pano BEIDnVCsMXxMoQp6FvbLUA, capture displayed as Apr 2026; one-story masonry bank, pale trim, repeated glazed bays, raised center tower, arched entry and green Horizon sign, shallow dark roof.",
    "evaluated_asset_bounds_xyz_m":asset_bounds,
    "scene":scene.name,"collection":asset.name,"export_object_count":len(all_objects),"mesh_count":len(mesh_objects),
    "material_names":materials,"materialless_meshes":materialless_meshes,
    "external_images":external_images,"external_libraries":external_libraries,
    "separate_schematic_interior_scene":interior_scene.name if interior_scene else None,
    "schematic_interior_object_count":interior_count
  },
  "findings":[
    "PASS: exact eight-corner LiDAR plan outline and campus registration independently confirmed from raw feature geometry.",
    "PASS: principal exterior identity cues from the April 2026 Street View are represented and texturing is portable/procedural.",
    "LIMITATION: all vertical dimensions and the roof profile remain estimates without a public elevation or survey.",
    "LIMITATION: interior is schematic and must not be presented as an as-built floor plan."
  ]
}
if hashlib.sha256(ASSET.read_bytes()).hexdigest().lower() != EXPECTED_SHA:
    raise RuntimeError("Asset SHA changed during grading; refusing to write a grade for a moving target")
OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print("HORIZON_INDEPENDENT_GRADE="+json.dumps(result,sort_keys=True))
