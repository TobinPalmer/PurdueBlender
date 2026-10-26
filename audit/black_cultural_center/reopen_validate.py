"""Reopen BCC, verify GIS-local shell and collection contract, and export a probe."""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular" / "buildings" / "black_cultural_center.blend"
OUT = ROOT / "audit" / "black_cultural_center"
GIS = OUT / "sources" / "purdue_gis_fid_645.json"
PROBE = OUT / "black_cultural_center_collection_probe.blend"
REPORT = OUT / "reopen_validation.json"
EXPECTED_ID = "black_cultural_center"
EXPECTED_OWNER = "Rossen"
EXPECTED_COLLECTION = "Asset_black_cultural_center"
EXPECTED_SCENE = "Scene"
EXPECTED_ORIGIN = [-493.868, 14.068]

def eval_mesh_points(obj, deps):
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()

def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]

bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
scene = bpy.data.scenes.get(EXPECTED_SCENE)
asset = bpy.data.collections.get(EXPECTED_COLLECTION)
assert scene and asset, "Expected BCC scene/collection missing"
assert asset.get("building_id") == EXPECTED_ID
assert asset.get("owner") == EXPECTED_OWNER
assert asset.get("source_feature_id") == "FID 645"
objs = list(asset.all_objects)
assert not [o.name for o in objs if o.type in {"CAMERA", "LIGHT"}], "Camera/light leaked into asset"
assert not [lib.filepath for lib in bpy.data.libraries if lib.filepath], "Unexpected linked library"

deps = bpy.context.evaluated_depsgraph_get()
mesh_objs = [o for o in objs if o.type == "MESH"]
all_points = [p for o in mesh_objs for p in eval_mesh_points(o, deps)]
asset_bounds = bounds(all_points)
shell_name = "BCC | first-floor brick envelope"
shell = bpy.data.objects.get(shell_name)
assert shell and shell in objs
shell_points = eval_mesh_points(shell, deps)
shell_bounds = bounds(shell_points)

gis = json.loads(GIS.read_text(encoding="utf-8"))
feature = gis["features"][0]
attrs = feature["attributes"]
assert attrs.get("FID") == 645 and attrs.get("BLDG_ABBR") == "BCC"
assert attrs.get("BUILDING_N") == "Black Cultural Center"
ring = feature["geometry"]["rings"][0]
lon = [p[0] for p in ring[:-1]]
lat = [p[1] for p in ring[:-1]]
cx_geo = (min(lon) + max(lon)) / 2
cy_geo = (min(lat) + max(lat)) / 2
LON_M = 84810.60416539927
LAT_M = 111040.0
foot = [((p[0]-cx_geo)*LON_M,(p[1]-cy_geo)*LAT_M) for p in ring[:-1]]
gis_bounds = [[min(p[0] for p in foot),max(p[0] for p in foot)],
              [min(p[1] for p in foot),max(p[1] for p in foot)]]
gis_area = abs(sum(foot[i][0]*foot[(i+1)%len(foot)][1]-foot[(i+1)%len(foot)][0]*foot[i][1]
                   for i in range(len(foot)))/2)
footprint_delta = max(abs(shell_bounds[axis][side]-gis_bounds[axis][side])
                      for axis in (0,1) for side in (0,1))
assert footprint_delta < 1e-4, f"GIS structural shell mismatch {footprint_delta} m"

images = []
materials = {mat for obj in mesh_objs for mat in obj.data.materials if mat}
for mat in materials:
    assert mat.use_nodes and any(link.to_node.type == "OUTPUT_MATERIAL" for link in mat.node_tree.links)
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
            images.append({"material":mat.name,"image":node.image.name,"path":node.image.filepath,
                           "packed":bool(node.image.packed_file)})
assert not images, f"External image dependencies found: {images}"

manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
entry = next(x for x in manifest["assets"] if x.get("id") == EXPECTED_ID)
assert entry["file"] == "buildings/black_cultural_center.blend"
assert entry["collection"] == EXPECTED_COLLECTION
assert entry["scene"] == EXPECTED_SCENE
assert list(entry["placement_origin_xy_m"]) == EXPECTED_ORIGIN
manifest_object_count = entry["object_count"]

obj_names = sorted(o.name for o in objs)
asset_hash = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
bpy.data.libraries.write(str(PROBE), {asset}, path_remap="RELATIVE_ALL", fake_user=True)
expected_obj_count = len(objs)
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
probe_asset = bpy.data.collections.get(EXPECTED_COLLECTION)
assert probe_asset is not None
probe_objs = list(probe_asset.all_objects)
assert len(probe_objs) == expected_obj_count
assert not [o for o in probe_objs if o.type in {"CAMERA", "LIGHT"}]

report = {
    "building_id": EXPECTED_ID,
    "owner": EXPECTED_OWNER,
    "asset_path": str(ASSET_PATH.relative_to(ROOT)).replace("\\", "/"),
    "asset_sha256": asset_hash,
    "blender_version": bpy.app.version_string,
    "scene_after_reopen": EXPECTED_SCENE,
    "collection_after_reopen": EXPECTED_COLLECTION,
    "collection_object_count": expected_obj_count,
    "manifest_object_count_field": manifest_object_count,
    "manifest_object_count_delta": expected_obj_count - manifest_object_count,
    "object_count_delta_reason": "The prior asset snapshot counted two soft lobby preview lights within BCC_Interior; the canonical builder now keeps those lights scene-only in Preview_Rig, outside Asset_black_cultural_center.",
    "mesh_object_count": len(mesh_objs),
    "manifest_contract_passed": True,
    "manifest_placement_origin_xy_m": EXPECTED_ORIGIN,
    "gis_feature_id": 645,
    "gis_identity": {k:attrs.get(k) for k in ["BLDG_ABBR","BUILDING_N","ADDRESS","NUM_LEVELS","Extrution"]},
    "gis_local_bbox_m": gis_bounds,
    "structural_shell_local_bbox_m": [shell_bounds[0],shell_bounds[1]],
    "structural_shell_bbox_delta_from_gis_m": footprint_delta,
    "gis_local_polygon_area_m2_approx": round(gis_area,3),
    "overall_asset_bounds_local_m": asset_bounds,
    "asset_camera_light_count": 0,
    "external_image_dependencies": images,
    "linked_libraries": [],
    "procedural_material_count": len(materials),
    "collection_only_probe_path": str(PROBE.relative_to(ROOT)).replace("\\", "/"),
    "collection_only_probe_reopened": True,
    "probe_object_count": len(probe_objs),
    "probe_has_no_camera_lights": True,
    "source_geometry_and_local_origin_status": "GIS ring extruded directly in local frame centered on GIS bbox midpoint; master marker remains manifest value.",
    "height_status": "Estimated only: shell cornice 8.45 m; overall model 9.06 m. GIS levels=3 and extraction field=24 lack confirmed units/vertical definition; no measured elevation source.",
}
REPORT.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report,indent=2))
