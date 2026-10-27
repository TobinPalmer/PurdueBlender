"""Fresh-open structural, identity, and geometry validation for Delta Upsilon.

Run as:
  blender -b modular/buildings/massing_house_301841256_1cc7641.blend \
    --python audit/delta_upsilon/validate_delta_upsilon.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/massing_house_301841256_1cc7641.blend"
AUDIT = ROOT / "audit/delta_upsilon"
ASSET_ID = "massing_house_301841256_1cc7641"
COLLECTION_NAME = "Asset_massing_house_301841256_1cc7641"
SCENE_NAME = "Building_massing_house_301841256_1cc7641"

scene = bpy.context.scene
collection = bpy.data.collections.get(COLLECTION_NAME)
if scene.name != SCENE_NAME or collection is None:
    raise RuntimeError(f"Fresh-open mismatch: {scene.name}, collection={collection}")
wall = bpy.data.objects.get("House_301841256")
if wall is None or wall.type != "MESH":
    raise RuntimeError("Stable primary wall mesh is missing")

feature = json.loads((AUDIT / "official_fid_751.geojson").read_text(encoding="utf-8"))["features"][0]
props = feature["properties"]
if props.get("FID") != 751 or props.get("BUILDING_N") != "Delta Upsilon":
    raise RuntimeError("Official feature identity mismatch")
build = json.loads((AUDIT / "build_validation.json").read_text(encoding="utf-8"))
origin = build["local_origin_project_xy_m"]
lonlat = feature["geometry"]["coordinates"][0][:-1]
official_local = [((lon + 86.9137) * 84810.60416539927 - origin[0],
                   (lat - 40.4274) * 111040.0 - origin[1]) for lon, lat in lonlat]
base_verts = [(v.co.x, v.co.y) for v in wall.data.vertices if abs(v.co.z) < 1e-5]
nearest = []
for source_point in official_local:
    nearest.append(min(math.dist(source_point, p) for p in base_verts))

depsgraph = bpy.context.evaluated_depsgraph_get()
all_points = []
for obj in collection.objects:
    if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        all_points.extend(tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
collection_bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)]
                     for i in range(3)]
used_materials = sorted({mat.name for obj in collection.objects
                         for mat in getattr(obj.data, "materials", []) if mat})
object_names = sorted(obj.name for obj in collection.objects)
mesh_count = sum(obj.type == "MESH" for obj in collection.objects)
text_count = sum(obj.type == "FONT" for obj in collection.objects)
outside_collection = sorted(obj.name for obj in scene.objects
                            if obj.name not in object_names)

if outside_collection:
    raise RuntimeError(f"Unexpected non-asset objects in saved scene: {outside_collection}")
if max(nearest) > 1e-4:
    raise RuntimeError(f"Wall footprint is displaced from the official GIS polygon: {max(nearest)} m")
if collection_bounds[2][0] < -1e-5 or collection_bounds[2][1] < 11.0:
    raise RuntimeError(f"Unexpected height range {collection_bounds[2]}")

sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest().upper()
result = {
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "asset_sha256": sha,
    "asset_id": ASSET_ID,
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(collection.objects),
    "mesh_object_count": mesh_count,
    "font_object_count": text_count,
    "other_object_count": len(collection.objects) - mesh_count - text_count,
    "object_names": object_names,
    "used_material_count": len(used_materials),
    "used_material_names": used_materials,
    "outside_collection_scene_objects": outside_collection,
    "all_asset_bounds_local_m": collection_bounds,
    "wall_mesh_bounds_local_m": [
        [min(v.co[i] for v in wall.data.vertices), max(v.co[i] for v in wall.data.vertices)]
        for i in range(3)
    ],
    "official_fid": props.get("FID"),
    "official_name": props.get("BUILDING_N"),
    "official_address": props.get("ADDRESS"),
    "local_origin_project_xy_m": origin,
    "footprint_vertex_nearest_distance_to_wall_base_m": nearest,
    "max_footprint_vertex_distance_m": max(nearest),
    "wall_material_has_uv": len(wall.data.uv_layers) > 0,
    "all_meshes_have_at_least_one_material": all(
        bool(obj.data.materials) for obj in collection.objects if obj.type == "MESH"),
}
if not result["all_meshes_have_at_least_one_material"]:
    raise RuntimeError("At least one mesh has no material")

# Re-opened-file preview: render an isolated view, then keep the saved .blend
# untouched. These temporary objects exist only in this validation process.
temp = bpy.data.collections.new("_DU_Fresh_Open_Preview_Temporary")
scene.collection.children.link(temp)
camera_data = bpy.data.cameras.new("_DU_Fresh_Open_Preview_Camera")
camera = bpy.data.objects.new("_DU_Fresh_Open_Preview_Camera", camera_data)
temp.objects.link(camera)
scene.camera = camera
target = Vector((0, -0.4, 5.0))
camera.location = (0, -53, 22)
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 32
sun_data = bpy.data.lights.new("_DU_Fresh_Open_Sun", type="SUN")
sun = bpy.data.objects.new("_DU_Fresh_Open_Sun", sun_data)
temp.objects.link(sun)
sun.rotation_euler = (math.radians(24), math.radians(-20), math.radians(-30))
sun.data.energy = 0.60
sun_data.angle = math.radians(18)
ground_data = bpy.data.meshes.new("_DU_Fresh_Open_Ground_Mesh")
ground_data.from_pydata([(-60,-60,-0.08),(60,-60,-0.08),(60,60,-0.08),(-60,60,-0.08)], [], [(0,1,2,3)])
ground_mat = bpy.data.materials.new("_DU_Fresh_Open_Ground_Material")
ground_mat.diffuse_color = (0.12, 0.16, 0.08, 1.0)
ground_data.materials.append(ground_mat)
ground = bpy.data.objects.new("_DU_Fresh_Open_Ground", ground_data)
temp.objects.link(ground)
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.65
scene.render.filepath = str(AUDIT / "delta_upsilon_fresh_open_preview.png")
bpy.ops.render.render(write_still=True)
scene.camera = None
for obj in list(temp.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(temp)

(AUDIT / "fresh_open_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("DU_FRESH_OPEN_VALIDATION", json.dumps(result, sort_keys=True))
