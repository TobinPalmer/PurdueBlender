"""Read-only verification run in a separate Blender process.

Usage from project root:
  blender -b modular/buildings/massing_von_s_d207e41.blend --python audit/von_s/fresh_open_check.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_von_s_d207e41.blend"
SOURCE = ROOT / "audit" / "von_s" / "sources" / "osm_way_116427236_footprint.json"
OUT = ROOT / "audit" / "von_s" / "reopen_verification.json"
PREVIEWS = [
    ROOT / "audit" / "von_s" / "previews" / "von_s_three_quarter.png",
    ROOT / "audit" / "von_s" / "previews" / "von_s_state_street_facade.png",
    ROOT / "audit" / "von_s" / "previews" / "von_s_mural_detail.png",
    ROOT / "audit" / "von_s" / "previews" / "von_s_roof_footprint.png",
]
ASSET_ID = "massing_von_s_d207e41"
SCENE = f"Building_{ASSET_ID}"
COLLECTION = f"Asset_{ASSET_ID}"

issues = []
scene = bpy.data.scenes.get(SCENE)
collection = bpy.data.collections.get(COLLECTION)
obj = bpy.data.objects.get("Von's")
if scene is None:
    issues.append("expected named building scene is missing")
if collection is None:
    issues.append("expected asset collection is missing")
if obj is None or obj.type != "MESH":
    issues.append("stable root object Von's is missing or not a mesh")
if scene and len(scene.objects) != 1:
    issues.append(f"expected one scene object, found {len(scene.objects)}")
if collection and obj and obj.name not in {item.name for item in collection.objects}:
    issues.append("stable root object is not linked to its expected collection")

data = json.loads(SOURCE.read_text(encoding="utf-8"))
ring = data["projected_ring_m"][:-1]
footprint_vertices_found = []
world_bounds = None
materials = []
vertex_count = face_count = 0
uv_layers = []
external_image_nodes = []
if obj and obj.type == "MESH":
    vertex_count = len(obj.data.vertices)
    face_count = len(obj.data.polygons)
    uv_layers = [layer.name for layer in obj.data.uv_layers]
    coords = [tuple(v.co) for v in obj.data.vertices]
    world_bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
    for source_point in ring:
        x, y = source_point
        found = any(abs(v.co.x-x) < 0.0005 and abs(v.co.y-y) < 0.0005 and abs(v.co.z) < 0.0005
                    for v in obj.data.vertices)
        footprint_vertices_found.append(found)
        if not found:
            issues.append(f"source footprint vertex missing after reopen: {source_point}")
    if obj.location.length > 1e-6 or any(abs(v) > 1e-6 for v in obj.rotation_euler) or any(abs(v-1)>1e-6 for v in obj.scale):
        issues.append("object transform is not identity; campus-world coordinates may have moved")
    if "Facade_Meters" not in uv_layers:
        issues.append("brick facade UV layer is missing")
    materials = [m.name if m else None for m in obj.data.materials]
    if any(m is None for m in materials):
        issues.append("mesh has empty material slots")
    for mat in obj.data.materials:
        if not mat or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                image = node.image
                path = bpy.path.abspath(image.filepath) if image else "<missing image>"
                external_image_nodes.append({"material": mat.name, "path": path})
                if image is None or (image.filepath and not Path(path).exists()):
                    issues.append(f"missing external image dependency: {path}")

for path in PREVIEWS:
    if not path.is_file() or path.stat().st_size < 1000:
        issues.append(f"missing or implausibly small preview: {path}")

if bpy.data.filepath and Path(bpy.data.filepath).resolve() != ASSET.resolve():
    issues.append(f"opened wrong file: {bpy.data.filepath}")

report = {
    "status": "PASS" if not issues else "FAIL",
    "check": "fresh Blender process opened the saved Von's library read-only",
    "blender_version": bpy.app.version_string,
    "opened_file": bpy.data.filepath,
    "asset_path": str(ASSET),
    "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "asset_id": ASSET_ID,
    "scene": scene.name if scene else None,
    "collection": collection.name if collection else None,
    "object": obj.name if obj else None,
    "scene_object_count": len(scene.objects) if scene else None,
    "vertex_count": vertex_count,
    "face_count": face_count,
    "world_bounds_m": world_bounds,
    "source_footprint_vertices_found": sum(footprint_vertices_found),
    "source_footprint_vertex_count": len(ring),
    "uv_layers": uv_layers,
    "materials": materials,
    "external_image_nodes": external_image_nodes,
    "preview_files": [str(p) for p in PREVIEWS],
    "issues": issues,
    "height_assessment": "estimated 8.45 m parapet; no measured elevation source",
    "interior_assessment": "not modeled; no public floor-plan evidence found",
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
