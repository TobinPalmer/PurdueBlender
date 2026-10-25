import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/physics_building_phys_3bf42f3.blend"
WORK = Path(__file__).resolve().parent
OUT = WORK / "independent_reopen_r2.json"
GIS_PATH = WORK / "physics_building_fid273_gis_snapshot.json"

asset = bpy.data.collections.get("Asset_physics_building")
if asset is None:
    raise RuntimeError("Asset_physics_building collection missing after reopen")
objects = list(asset.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
unmaterialed = [o.name for o in meshes if not o.data.materials]
missing_images = []
for image in bpy.data.images:
    if image.source != "FILE" or not image.filepath:
        continue
    resolved = Path(bpy.path.abspath(image.filepath))
    if image.filepath.startswith("//"):
        resolved = (ASSET_PATH.parent / image.filepath[2:]).resolve()
    if not resolved.is_file():
        missing_images.append(image.filepath)

body = bpy.data.objects.get("PHYS | GIS footprint brick envelope")
if body is None or body.type != "MESH":
    raise RuntimeError("GIS footprint brick envelope missing")
snapshot = json.loads(GIS_PATH.read_text(encoding="utf-8"))
ring = snapshot["feature"]["geometry"]["rings"][0]
lat0, lon0 = 40.4274, -86.9137
lon_scale = 111412.84 * math.cos(math.radians(lat0))
world = [Vector(((lon + 86.9137) * lon_scale, (lat - 40.4274) * 111040.0)) for lon, lat in ring]
if (world[0] - world[-1]).length < 1e-5:
    world.pop()
origin = Vector(((min(p.x for p in world) + max(p.x for p in world)) / 2,
                 (min(p.y for p in world) + max(p.y for p in world)) / 2))
expected = [p - origin for p in world]
model_xy = sorted({(round((body.matrix_world @ v.co).x, 6),
                    round((body.matrix_world @ v.co).y, 6)) for v in body.data.vertices})
model = [Vector(p) for p in model_xy]
gis_to_model = max(min((p - q).length for q in model) for p in expected)
model_to_gis = max(min((p - q).length for q in expected) for p in model)
bounds = [[min((o.matrix_world @ Vector(c))[axis] for o in meshes for c in o.bound_box),
            max((o.matrix_world @ Vector(c))[axis] for o in meshes for c in o.bound_box)]
           for axis in range(3)]

manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
record = next(a for a in manifest["assets"] if a["id"] == "physics_building")
manifest_names = record.get("objects", [])
object_names = [o.name for o in objects]
name_diff = {"missing_from_manifest": sorted(set(object_names) - set(manifest_names)),
             "extra_in_manifest": sorted(set(manifest_names) - set(object_names))}
bound_errors = [[float(bounds[i][j]) - float(record["local_bounds_m"][i][j]) for j in range(2)]
                for i in range(3)]
textured_materials = []
for material in bpy.data.materials:
    if any(word in material.name.lower() for word in ("masonry", "roof", "clay", "tile", "brick")):
        nodes = [n.type for n in material.node_tree.nodes] if material.use_nodes and material.node_tree else []
        textured_materials.append({"name": material.name, "node_types": nodes})

result = {
    "asset_sha256": hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "collection": asset.name,
    "collection_object_count": len(objects),
    "collection_mesh_count": len(meshes),
    "object_type_counts": {t: sum(o.type == t for o in objects) for t in sorted({o.type for o in objects})},
    "object_inventory_matches_manifest": len(objects) == int(record.get("object_count", -1)) and not any(name_diff.values()),
    "object_name_differences": name_diff,
    "unmaterialed_meshes": unmaterialed,
    "missing_external_images": missing_images,
    "mesh_bounds_local_m": bounds,
    "manifest_local_bounds_m": record.get("local_bounds_m"),
    "manifest_bound_errors_m": bound_errors,
    "base_mesh": body.name,
    "gis_expected_ring_vertices": len(expected),
    "model_unique_xy_vertices": len(model_xy),
    "gis_to_model_max_nearest_m": gis_to_model,
    "model_to_gis_max_nearest_m": model_to_gis,
    "textured_materials": textured_materials,
    "manifest_placement_origin_xy_m": record.get("placement_origin_xy_m"),
    "expected_gis_campus_origin_xy_m": [20.732372, 300.324127],
    "manifest_xy_to_source_origin_error_m": math.dist(record.get("placement_origin_xy_m", []), [20.732372, 300.324127]),
    "interior_and_bridge_object_names": [o.name for o in objects if any(k in o.name.lower() for k in ("interior", "vestibule", "bridge", "partition", "corridor", "stair"))],
}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
