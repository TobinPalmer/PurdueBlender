"""Read-only independent probe of the saved Alpha Chi Rho Blender library."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("asset_probe.json")
EXPECTED = "Asset_massing_alpha_chi_rho_0cb591a"
asset = bpy.data.collections.get(EXPECTED)
assert asset is not None, f"missing {EXPECTED}"
objects = list(asset.objects)
assert len(objects) == 1 and objects[0].type == "MESH"
obj = objects[0]
mesh = obj.data
coords = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
image_paths = [image.filepath for image in bpy.data.images
               if image.source == "FILE" and image.filepath]
result = {
    "opened_asset": bpy.data.filepath,
    "scene_names": sorted(scene.name for scene in bpy.data.scenes),
    "asset_collection": EXPECTED,
    "asset_object_count": len(objects),
    "object_name": obj.name,
    "object_type": obj.type,
    "mesh_vertices": len(mesh.vertices),
    "mesh_polygons": len(mesh.polygons),
    "material_names": [m.name if m else None for m in mesh.materials],
    "world_bounds_m": bounds,
    "external_image_dependencies": image_paths,
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
