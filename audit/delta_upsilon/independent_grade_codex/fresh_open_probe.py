import bpy
import hashlib
import json
import math
from pathlib import Path

asset_id = "massing_house_301841256_1cc7641"
collection_name = f"Asset_{asset_id}"
scene_name = f"Building_{asset_id}"
asset_path = Path(bpy.data.filepath).resolve()
collection = bpy.data.collections.get(collection_name)
errors = []
if bpy.context.scene.name != scene_name:
    errors.append(f"scene mismatch: {bpy.context.scene.name}")
if collection is None:
    errors.append(f"missing export collection: {collection_name}")

objects = list(collection.all_objects) if collection else []
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
curve_objects = [obj for obj in objects if obj.type in {"CURVE", "FONT"}]
other_objects = [obj for obj in objects if obj.type not in {"MESH", "CURVE", "FONT"}]
outside = [obj.name for obj in bpy.context.scene.objects if obj.name not in {o.name for o in objects}]
mesh_issues = []
materials_used = set()
for obj in mesh_objects:
    if len(obj.data.vertices) == 0 or len(obj.data.polygons) == 0:
        mesh_issues.append(f"empty mesh: {obj.name}")
    if not obj.data.materials:
        mesh_issues.append(f"no material slots: {obj.name}")
    for polygon in obj.data.polygons:
        if polygon.material_index >= len(obj.data.materials):
            mesh_issues.append(f"invalid material index: {obj.name}:{polygon.index}")
for obj in objects:
    for material in getattr(obj.data, "materials", []):
        if material:
            materials_used.add(material.name)

images = [
    {"name": img.name, "filepath": img.filepath, "packed": img.packed_file is not None}
    for img in bpy.data.images if img.source == "FILE"
]
libraries = [lib.filepath for lib in bpy.data.libraries]
sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
expected_sha = "94ce070ec9329d2ed1ba4f8dc264a55f9e3eb5d682190948d570f29d8fef7328"
audit_dir = Path(__file__).resolve().parents[1]
feature = json.loads((audit_dir / "official_fid_751.geojson").read_text(encoding="utf-8"))["features"][0]
origin = json.loads((audit_dir / "build_validation.json").read_text(encoding="utf-8"))["local_origin_project_xy_m"]
official_ring = [((lon + 86.9137) * 84810.60416539927 - origin[0],
                  (lat - 40.4274) * 111040.0 - origin[1])
                 for lon, lat in feature["geometry"]["coordinates"][0][:-1]]
wall = bpy.data.objects.get("House_301841256")
wall_base = [(float(v.co.x), float(v.co.y)) for v in wall.data.vertices
             if abs(v.co.z) < 1e-5] if wall else []
gis_to_model = [min(math.dist(point, candidate) for candidate in wall_base)
                for point in official_ring] if wall_base else []
def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length_sq))
    projection = (start[0] + t * dx, start[1] + t * dy)
    return math.dist(point, projection)

model_to_gis_segments = [
    min(point_segment_distance(point, official_ring[i], official_ring[(i + 1) % len(official_ring)])
        for i in range(len(official_ring))) for point in wall_base
] if official_ring else []
footprint_max_symmetric_boundary_error_m = (
    max(gis_to_model + model_to_gis_segments) if gis_to_model and model_to_gis_segments else None
)
if sha.lower() != expected_sha:
    errors.append(f"asset SHA mismatch: {sha}")
if not objects:
    errors.append("export collection is empty")
if outside:
    errors.append(f"scene contains unexpected objects outside export collection: {outside}")
if mesh_issues:
    errors.extend(mesh_issues)
if images:
    errors.append(f"external image textures present: {images}")
if libraries:
    errors.append(f"linked library dependencies present: {libraries}")

result = {
    "fresh_open": "PASS" if not errors else "FAIL",
    "blender_version": bpy.app.version_string,
    "asset_file": str(asset_path),
    "asset_sha256": sha,
    "scene": bpy.context.scene.name,
    "collection": collection.name if collection else None,
    "collection_object_count": len(objects),
    "mesh_object_count": len(mesh_objects),
    "curve_or_text_object_count": len(curve_objects),
    "other_object_count": len(other_objects),
    "mesh_vertices": sum(len(obj.data.vertices) for obj in mesh_objects),
    "mesh_polygons": sum(len(obj.data.polygons) for obj in mesh_objects),
    "materials_used": sorted(materials_used),
    "external_images": images,
    "linked_libraries": libraries,
    "unexpected_scene_objects": outside,
    "mesh_issues": mesh_issues,
    "independent_footprint_vertex_check": {
        "feature_id": feature["properties"].get("FID"),
        "source_name": feature["properties"].get("BUILDING_N"),
        "official_ring_vertex_count": len(official_ring),
        "wall_base_vertex_count": len(wall_base),
        "max_gis_vertex_to_wall_vertex_error_m": max(gis_to_model) if gis_to_model else None,
        "max_wall_base_vertex_to_gis_boundary_error_m": max(model_to_gis_segments) if model_to_gis_segments else None,
        "max_symmetric_boundary_error_m": footprint_max_symmetric_boundary_error_m,
        "placement_origin_xy_m": origin,
    },
    "errors": errors,
}
out = Path(__file__).resolve().parent / "fresh_open_probe.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
if errors:
    raise RuntimeError("Independent Delta Upsilon fresh-open probe failed")
