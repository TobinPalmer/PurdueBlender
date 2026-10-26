"""Fresh-open probe of the localized Drug Discovery building library."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

asset_id = "massing_purdue_drug_discovery_facility_fc72a4a"
collection_name = "Asset_" + asset_id
collection = bpy.data.collections.get(collection_name)
scene = bpy.context.scene
shell = bpy.data.objects.get("DRUG | GIS footprint walls, three-storey brick and glazing")

def bounds(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None

edges = []
if shell is not None and shell.type == "MESH":
    mesh = shell.data
    for poly in mesh.polygons:
        bottom = [mesh.vertices[i] for i in poly.vertices if abs(mesh.vertices[i].co.z - 0.25) < 1e-5]
        if len(bottom) == 2:
            a, b = (shell.matrix_world @ v.co for v in bottom)
            edges.append([[float(a.x), float(a.y)], [float(b.x), float(b.y)]])

objects = list(collection.all_objects) if collection else []
meshes = [o for o in objects if o.type == "MESH"]
all_points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
materials = sorted({m.name for o in meshes for m in o.data.materials if m})
images = [{"name": im.name, "filepath": im.filepath, "packed": bool(im.packed_file)} for im in bpy.data.images]
result = {
    "blender_version": bpy.app.version_string,
    "opened_file": bpy.data.filepath,
    "scene": scene.name if scene else None,
    "scene_object_count": len(scene.objects) if scene else 0,
    "collection_found": collection is not None,
    "collection_object_count": len(objects),
    "mesh_object_count": len(meshes),
    "polygon_count": sum(len(o.data.polygons) for o in meshes),
    "unique_material_count": len(materials),
    "materials": materials,
    "meshes_without_materials": [o.name for o in meshes if not any(m for m in o.data.materials)],
    "external_libraries": [bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries if lib.filepath],
    "images": images,
    "shell_found": shell is not None,
    "shell_local_bounds_m": bounds(shell) if shell else None,
    "full_asset_local_bounds_m": [[min(p[i] for p in all_points), max(p[i] for p in all_points)] for i in range(3)] if all_points else None,
    "base_outline_edges_local_xy_m": edges,
    "root_found": bpy.data.objects.get("AssetRoot_" + asset_id) is not None,
    "root_location": list(bpy.data.objects["AssetRoot_" + asset_id].location) if bpy.data.objects.get("AssetRoot_" + asset_id) else None,
    "collection_coordinate_frame": collection.get("coordinate_frame") if collection else None,
    "collection_placement_origin_xy_m": list(collection.get("placement_origin_xy_m", [])) if collection and collection.get("placement_origin_xy_m") else None,
}
target = Path(sys.argv[sys.argv.index("--") + 1])
target.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "base_outline_edges_local_xy_m"}))
