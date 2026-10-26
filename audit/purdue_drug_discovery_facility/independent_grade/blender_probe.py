import bpy
import json
import sys
from pathlib import Path

asset_id = "massing_purdue_drug_discovery_facility_fc72a4a"
collection_name = "Asset_" + asset_id
collection = bpy.data.collections.get(collection_name)
scene = bpy.context.scene
shell = bpy.data.objects.get("DRUG | GIS footprint walls, three-storey brick and glazing")

def world_bounds(obj):
    pts = [obj.matrix_world @ __import__('mathutils').Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None

edge_pairs = []
if shell is not None and shell.type == 'MESH':
    me = shell.data
    for poly in me.polygons:
        ids = list(poly.vertices)
        bottom = [idx for idx in ids if abs(me.vertices[idx].co.z - 0.25) < 1e-5]
        if len(bottom) == 2:
            a, b = (me.vertices[idx].co for idx in bottom)
            edge_pairs.append([[float(a.x), float(a.y)], [float(b.x), float(b.y)]])

objects = list(collection.all_objects) if collection else []
meshes = [o for o in objects if o.type == 'MESH']
all_points = [o.matrix_world @ __import__('mathutils').Vector(corner)
              for o in meshes for corner in o.bound_box]
full_bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)]
               for i in range(3)] if all_points else None
materials = sorted({m.name for o in meshes for m in o.data.materials if m})
no_material_meshes = [o.name for o in meshes if not any(m for m in o.data.materials)]
images = []
for image in bpy.data.images:
    images.append({"name": image.name, "filepath": image.filepath, "packed": bool(image.packed_file)})

out = {
    "blender_version": bpy.app.version_string,
    "opened_file": bpy.data.filepath,
    "scene": scene.name if scene else None,
    "scene_objects": len(scene.objects) if scene else 0,
    "collection_found": collection is not None,
    "collection_object_count": len(objects),
    "mesh_object_count": len(meshes),
    "polygon_count": sum(len(o.data.polygons) for o in meshes),
    "unique_material_count": len(materials),
    "materials": materials,
    "meshes_without_materials": no_material_meshes,
    "external_libraries": [lib.filepath for lib in bpy.data.libraries if lib.filepath],
    "images": images,
    "shell_found": shell is not None,
    "shell_bounds_world_m": world_bounds(shell) if shell else None,
    "full_asset_bounds_world_m": full_bounds,
    "shell_z_planes": sorted({round(float(v.co.z), 4) for v in shell.data.vertices}) if shell else [],
    "base_outline_edges_xy_m": edge_pairs,
    "object_names": [o.name for o in objects],
}
target = Path(sys.argv[sys.argv.index('--') + 1])
target.write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in out.items() if k not in ('base_outline_edges_xy_m', 'object_names')}))
