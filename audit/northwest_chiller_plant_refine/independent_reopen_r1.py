import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path.cwd()
ASSET = ROOT / "modular/buildings/northwest_chiller_plant.blend"
MASTER = ROOT / "purdue_campus_master.blend"
MANIFEST = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
RECORD = next(a for a in MANIFEST["assets"] if a["id"] == "northwest_chiller_plant")
OUT = ROOT / "audit/northwest_chiller_plant_refine/independent_reopen_r1.json"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
collection = bpy.data.collections.get(RECORD["collection"])
if collection is None:
    raise RuntimeError("Asset collection missing after reopening")
objects = list(collection.all_objects)
names = [obj.name for obj in objects]
expected_names = list(RECORD.get("objects", []))
meshes = [obj for obj in objects if obj.type == "MESH"]
types = {}
for obj in objects:
    types[obj.type] = types.get(obj.type, 0) + 1
unique_materials = {mat.name for obj in objects for slot in obj.material_slots
                    if (mat := slot.material) is not None}
unassigned_meshes = [obj.name for obj in meshes if not any(slot.material for slot in obj.material_slots)]
image_refs = sorted({node.image.filepath for mat in bpy.data.materials if mat.use_nodes and mat.node_tree
                     for node in mat.node_tree.nodes if node.type == "TEX_IMAGE" and node.image})
missing_images = [path for path in image_refs if not bpy.path.abspath(path) or
                  not Path(bpy.path.abspath(path)).exists()]
mesh_points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
mesh_bounds = [[min(p[i] for p in mesh_points), max(p[i] for p in mesh_points)] for i in range(3)]
shell = bpy.data.objects.get("northwest_chiller_plant_official_GIS_shell")
if shell is None or shell.type != "MESH":
    raise RuntimeError("Official GIS shell missing")
shell_points = [shell.matrix_world @ Vector(corner) for corner in shell.bound_box]
shell_bounds = [[min(p[i] for p in shell_points), max(p[i] for p in shell_points)] for i in range(3)]
base = {
    "asset": str(ASSET),
    "asset_sha256": asset_hash,
    "blender_version": bpy.app.version_string,
    "collection": collection.name,
    "collection_object_count": len(objects),
    "object_type_counts": types,
    "manifest_count": RECORD.get("object_count"),
    "manifest_name_count": len(expected_names),
    "manifest_inventory_matches": sorted(names) == sorted(expected_names),
    "manifest_name_differences": {
        "missing": sorted(set(names) - set(expected_names)),
        "extra": sorted(set(expected_names) - set(names)),
    },
    "unique_material_count": len(unique_materials),
    "materialless_meshes": unassigned_meshes,
    "image_references": image_refs,
    "missing_images": missing_images,
    "mesh_bounds_local_m": mesh_bounds,
    "manifest_bounds_local_m": RECORD.get("local_bounds_m"),
    "mesh_shell_bounds_local_m": shell_bounds,
    "manifest_shell_bounds_local_m": RECORD.get("source_bounds_world_m"),
}
# Reopen the project master read-only, then verify its existing instance and marker.
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
marker = bpy.data.objects.get("Placement_northwest_chiller_plant")
master_collection = bpy.data.collections.get(RECORD["collection"])
if marker is None or master_collection is None:
    base["master_check"] = {"present": False}
else:
    linked = Path(bpy.path.abspath(master_collection.library.filepath)).resolve()
    expected_path = (ROOT / "modular" / RECORD["file"]).resolve()
    origin = RECORD.get("placement_origin_xy_m", [None, None])
    error = ((float(marker.location.x) - float(origin[0])) ** 2 +
             (float(marker.location.y) - float(origin[1])) ** 2) ** 0.5
    base["master_check"] = {
        "present": True,
        "marker_collection_match": marker.instance_collection == master_collection,
        "linked_asset_path": str(linked),
        "expected_asset_path": str(expected_path),
        "library_path_matches": linked == expected_path,
        "linked_object_count": len(master_collection.all_objects),
        "marker_xy_m": [float(marker.location.x), float(marker.location.y)],
        "manifest_xy_m": origin,
        "placement_error_m": error,
        "scale": [float(v) for v in marker.scale],
        "rotation_euler": [float(v) for v in marker.rotation_euler],
        "direct_root_link": any(child.name == RECORD["collection"] for child in bpy.context.scene.collection.children),
    }
OUT.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(base, indent=2, ensure_ascii=False))
