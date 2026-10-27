import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET_ID = "massing_house_301841333_affe21e"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
EXPECTED_SHA = "0890efdbbb2eff92dfbfd6a60d69a6d4006108a029e8d209ef7791b34182b376"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get(f"Building_{ASSET_ID}")
collection = bpy.data.collections.get(f"Asset_{ASSET_ID}")
if scene is None or collection is None:
    raise RuntimeError("Expected scene or asset collection is missing")
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
mesh_count = 0
vertex_count = 0
polygon_count = 0
materials = set()
for obj in collection.all_objects:
    if obj.type != "MESH":
        continue
    mesh_count += 1
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertex_count += len(mesh.vertices)
    polygon_count += len(mesh.polygons)
    materials.update(m.name for m in obj.data.materials if m)
    points.extend(obj.matrix_world @ vertex.co for vertex in mesh.vertices)
    evaluated.to_mesh_clear()
if not points:
    raise RuntimeError("Asset collection has no evaluated mesh vertices")
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
foundation = bpy.data.objects.get("DDD_Foundation_Base")
foundation_ring = []
if foundation is not None and foundation.type == "MESH":
    foundation_ring = [list((foundation.matrix_world @ vertex.co)[:2])
                       for vertex in foundation.data.vertices if abs(vertex.co.z) < 1e-6]
images = [img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file]
linked_libraries = [lib.filepath for lib in bpy.data.libraries]
result = {
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "expected_sha256": EXPECTED_SHA,
    "sha_match": hashlib.sha256(ASSET.read_bytes()).hexdigest() == EXPECTED_SHA,
    "blender_version": bpy.app.version_string,
    "scene": scene.name,
    "collection": collection.name,
    "collection_object_count": len(collection.all_objects),
    "mesh_object_count": mesh_count,
    "evaluated_mesh_vertex_count": vertex_count,
    "evaluated_polygon_count": polygon_count,
    "evaluated_local_bounds_m": bounds,
    "foundation_outline_local_xy_m": foundation_ring,
    "material_names": sorted(materials),
    "unpacked_external_images": images,
    "linked_libraries": linked_libraries,
    "feature_object_names": {
        "interior": sorted(obj.name for obj in collection.all_objects
                            if any(token in obj.name.lower() for token in ("interior", "room", "floor", "stair", "table", "partition", "hall")))[:100],
        "entry": sorted(obj.name for obj in collection.all_objects
                         if any(token in obj.name.lower() for token in ("portico", "column", "door", "entry", "step", "rail", "badge", "emblem")))[:100],
        "facade": sorted(obj.name for obj in collection.all_objects
                          if any(token in obj.name.lower() for token in ("window", "brick", "roof", "shingle", "cornice", "limestone")))[:100],
    },
}
OUT = Path(__file__).resolve().parent / "fresh_probe.json"
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
