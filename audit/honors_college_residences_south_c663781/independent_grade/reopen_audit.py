import hashlib
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_honors_college_and_residences_south_c663781"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
GIS = ROOT / "audit" / "honors_college_residences_south_c663781" / "sources" / "purdue_gis_fid905.json"
OUT = Path(__file__).resolve().parent / "reopen_audit.json"

def web_mercator_to_campus(x, y):
    r = 6378137.0
    lon = math.degrees(x / r)
    lat = math.degrees(2 * math.atan(math.exp(y / r)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection_name = "Asset_" + ASSET_ID
collection = bpy.data.collections.get(collection_name)
objects = list(collection.all_objects) if collection else []
mesh_objects = [o for o in objects if o.type == "MESH"]
source = json.loads(GIS.read_text(encoding="utf-8"))["feature"]
ring = source["geometry"]["rings"][0][:-1]
source_xy = [web_mercator_to_campus(x, y) for x, y in ring]

# Identify the model's footprint shell by its explicitly descriptive object name,
# but independently transform evaluated mesh vertices into world coordinates.
shell_candidates = [o for o in mesh_objects if "GIS footprint" in o.name and "shell" in o.name.lower()]
shell_records = []
for obj in shell_candidates:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    pts = [(evaluated.matrix_world @ v.co).xy[:] for v in mesh.vertices]
    evaluated.to_mesh_clear()
    # Keep planar footprint vertices at the object base and compare all unique XYs.
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    shell_records.append({"name": obj.name, "vertex_xy_count": len(pts), "points": pts,
                         "bounds_xy_m": [[min(p[0] for p in pts), max(p[0] for p in pts)],
                                         [min(p[1] for p in pts), max(p[1] for p in pts)]] if pts else None,
                         "z_bounds_m": [min((evaluated.matrix_world @ v.co).z for v in obj.data.vertices),
                                        max((evaluated.matrix_world @ v.co).z for v in obj.data.vertices)] if obj.data.vertices else None})

def directed_nearest(a, b):
    return [min(math.dist(p, q) for q in b) for p in a] if b else []

comparisons = []
for rec in shell_records:
    model_xy = rec["points"]
    s2m = directed_nearest(source_xy, model_xy)
    m2s = directed_nearest(model_xy, source_xy)
    comparisons.append({"shell": rec["name"], "source_vertex_count": len(source_xy),
                        "model_unique_xy_count": len(model_xy),
                        "source_to_model_max_nearest_m": max(s2m, default=None),
                        "model_to_source_max_nearest_m": max(m2s, default=None),
                        "source_to_model_mean_nearest_m": sum(s2m) / len(s2m) if s2m else None,
                        "model_to_source_mean_nearest_m": sum(m2s) / len(m2s) if m2s else None,
                        "bounds_xy_m": rec["bounds_xy_m"], "z_bounds_m": rec["z_bounds_m"]})

all_image_refs = []
for image in bpy.data.images:
    if image.source == "FILE":
        all_image_refs.append({"name": image.name, "filepath": image.filepath,
                               "packed": bool(image.packed_file)})
external_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
material_names = sorted({m.name for o in mesh_objects for m in o.data.materials if m})
schematic_count = sum(o.name.startswith("SCHEMATIC INTERIOR") for o in objects)
all_world_points = []
object_z_report = []
depsgraph = bpy.context.evaluated_depsgraph_get()
for obj in objects:
    if obj.type != "MESH":
        continue
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    z_values = [(ev.matrix_world @ v.co).z for v in mesh.vertices]
    all_world_points.extend(z_values)
    if z_values:
        object_z_report.append({"name": obj.name, "z_min_m": min(z_values), "z_max_m": max(z_values),
                                "materials": [m.name for m in obj.data.materials if m]})
    ev.to_mesh_clear()

result = {
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "blender_version": bpy.app.version_string,
    "saved_scene": scene.name,
    "expected_scene": "Building_" + ASSET_ID,
    "scene_name_matches": scene.name == "Building_" + ASSET_ID,
    "export_collection_found": collection is not None,
    "collection_name": collection.name if collection else None,
    "collection_object_count": len(objects),
    "mesh_object_count": len(mesh_objects),
    "gis_feature": {k: source["attributes"].get(k) for k in ["FID", "BLDG_ABBR", "BUILDING_N", "ADDRESS", "NUM_LEVELS", "CountOfFLO", "Extrution"]},
    "source_ring_vertex_count": len(source_xy),
    "shells": shell_records,
    "footprint_comparisons": comparisons,
    "asset_z_bounds_m": [min(all_world_points), max(all_world_points)] if all_world_points else None,
    "tallest_mesh_objects": sorted(object_z_report, key=lambda x: x["z_max_m"], reverse=True)[:12],
    "materials": material_names,
    "file_images": all_image_refs,
    "linked_libraries": external_libraries,
    "schematic_labeled_object_count": schematic_count,
    "collection_direct_scene_membership": bool(collection and collection in scene.collection.children_recursive),
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("INDEPENDENT_HCRS_AUDIT=" + json.dumps(result, sort_keys=True))
