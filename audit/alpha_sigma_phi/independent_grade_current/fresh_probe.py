import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector
import math

asset = Path(bpy.data.filepath)
collection_name = "Asset_massing_house_301841603_654031c"
scene_name = "Building_massing_house_301841603_654031c"
col = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
objs = list(col.all_objects) if col else []
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
mesh_objs = [o for o in objs if o.type == "MESH"]
materials = sorted({m.name for o in objs if o.type == "MESH" for m in o.data.materials if m})
materialless = [o.name for o in mesh_objs if not any(m for m in o.data.materials)]
world_points = []
for o in mesh_objs:
    ev = o.evaluated_get(depsgraph)
    for p in ev.bound_box:
        world_points.append(ev.matrix_world @ Vector(p))
if world_points:
    bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)]
else:
    bounds = None
root = bpy.data.objects.get("House_301841603")
footprint = {}
if root and root.type == "MESH":
    modeled_xy = sorted({(round((root.matrix_world @ v.co).x, 6), round((root.matrix_world @ v.co).y, 6)) for v in root.data.vertices if abs((root.matrix_world @ v.co).z) < 1.0e-5})
    source_path = asset.parent.parent.parent / "audit" / "alpha_sigma_phi" / "sources" / "arcgis_fid763_feature.json"
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    ring = raw["features"][0]["geometry"]["rings"][0][:-1]
    src_xy = sorted({(round((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), 6), round((lat - 40.4274) * 111040, 6)) for lon, lat in ring})
    dists = []
    for x, y in src_xy:
        dists.append(min(math.hypot(x-mx, y-my) for mx, my in modeled_xy))
    for x, y in modeled_xy:
        dists.append(min(math.hypot(x-mx, y-my) for mx, my in src_xy))
    footprint = {"source_unique_xy_vertices": len(src_xy), "model_base_unique_xy_vertices": len(modeled_xy), "symmetric_vertex_nearest_max_m": max(dists) if dists else None, "symmetric_vertex_nearest_mean_m": sum(dists)/len(dists) if dists else None}
images = []
for img in bpy.data.images:
    if img.source == "FILE":
        images.append({"name": img.name, "filepath": img.filepath, "packed": bool(img.packed_file)})
result = {
    "asset": str(asset),
    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "scene_names": sorted(s.name for s in bpy.data.scenes),
    "scene_found": bool(scene),
    "collection_found": bool(col),
    "collection_object_count": len(objs),
    "scene_object_count": len(scene.objects) if scene else None,
    "type_counts": {t: sum(o.type == t for o in objs) for t in sorted({o.type for o in objs})},
    "material_count": len(materials),
    "materials": materials,
    "materialless_meshes": materialless,
    "external_images": images,
    "evaluated_world_bounds_m": bounds,
    "root_transform": {"location": list(root.location), "rotation_euler": list(root.rotation_euler), "scale": list(root.scale)} if root else None,
    "source_to_model_footprint": footprint,
    "scene_objects_outside_asset_collection": [o.name for o in scene.objects if o not in objs] if scene else [],
    "mesh_objects_outside_asset_collection": [o.name for o in bpy.data.objects if o.type == "MESH" and o not in objs],
}
out = asset.parent.parent.parent / "audit" / "alpha_sigma_phi" / "independent_grade_current" / "fresh_probe.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in {"materials", "external_images"}}, indent=2))
