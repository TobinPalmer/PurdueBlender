import bpy
import hashlib
import json
import math
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
asset = repo / "modular" / "buildings" / "massing_islamic_societyof_greater_lafayette_0130012.blend"
source = repo / "audit" / "massing_islamic_societyof_greater_lafayette_0130012" / "sources" / "purdue_gis_FID771_SOMSA.json"
expected_sha = "c84126f5b1f549db17faa7282e449fc6de171e632b6e627062ad46379247c39b"
actual_sha = hashlib.sha256(asset.read_bytes()).hexdigest()
errors = []
if actual_sha != expected_sha:
    errors.append(f"asset SHA differs from reviewed hash: {actual_sha}")

asset_id = "massing_islamic_societyof_greater_lafayette_0130012"
scene_name = f"Building_{asset_id}"
collection_name = f"Asset_{asset_id}"
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
if bpy.context.scene.name != scene_name:
    errors.append(f"active scene mismatch: {bpy.context.scene.name}")
if collection is None:
    errors.append(f"collection missing: {collection_name}")
objects = list(collection.all_objects) if collection else []
meshes = [o for o in objects if o.type == "MESH"]
if len(meshes) != 1:
    errors.append(f"expected one mesh, found {len(meshes)}")
mesh = meshes[0] if meshes else None
missing_material_slots = []
if mesh:
    for i, slot in enumerate(mesh.material_slots):
        if slot.material is None:
            missing_material_slots.append(i)
    if missing_material_slots:
        errors.append(f"materialless slots on mesh: {missing_material_slots}")

all_images = [image.name for image in bpy.data.images if image.source == "FILE" and image.filepath]
missing_images = []
for image in bpy.data.images:
    if image.source != "FILE" or not image.filepath:
        continue
    path = Path(bpy.path.abspath(image.filepath))
    if not path.exists():
        missing_images.append(str(path))
if missing_images:
    errors.append(f"missing image files: {missing_images}")
linked_libraries = [lib.filepath for lib in bpy.data.libraries]
if linked_libraries:
    errors.append(f"unexpected linked libraries: {linked_libraries}")

verts = [mesh.matrix_world @ v.co for v in mesh.data.vertices] if mesh else []
bounds = [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)] if verts else None
used_materials = sorted({slot.material.name for slot in mesh.material_slots if slot.material}) if mesh else []

gis = json.loads(source.read_text(encoding="utf-8"))
feature = gis["features"][0]
ring = feature["geometry"]["rings"][0][:-1]
lon0, lat0 = -86.9137, 40.4274
lat_scale = 111040.0
lon_scale = 111412.84 * math.cos(math.radians(lat0))
gis_xy = [((xy[0] - lon0) * lon_scale, (xy[1] - lat0) * lat_scale) for xy in ring]
base_vertices = []
if mesh:
    for v in verts:
        if abs(float(v.z)) < 0.0001:
            xy = (float(v.x), float(v.y))
            if not any(math.dist(xy, old) < 1e-6 for old in base_vertices):
                base_vertices.append(xy)
nearest = [min(math.dist(p, q) for q in base_vertices) for p in gis_xy] if base_vertices else []

result = {
    "fresh_open": "PASS" if not errors else "FAIL",
    "reviewed_asset_sha256": expected_sha,
    "recomputed_asset_sha256": actual_sha,
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "expected_scene": scene_name,
    "collection": collection.name if collection else None,
    "collection_object_count": len(objects),
    "mesh_count": len(meshes),
    "mesh_names": [o.name for o in meshes],
    "mesh_vertex_count": len(mesh.data.vertices) if mesh else 0,
    "mesh_polygon_count": len(mesh.data.polygons) if mesh else 0,
    "used_materials": used_materials,
    "image_files": all_images,
    "missing_images": missing_images,
    "linked_libraries": linked_libraries,
    "bounds_world_m": bounds,
    "source_gis_fid": feature["attributes"]["FID"],
    "source_gis_name": feature["attributes"]["BUILDING_N"],
    "source_gis_address": feature["attributes"]["ADDRESS"],
    "gis_ring_vertex_count": len(gis_xy),
    "base_vertex_candidate_count": len(base_vertices),
    "max_gis_vertex_nearest_distance_m": max(nearest) if nearest else None,
    "errors": errors,
}
out = Path(__file__).with_name("fresh_open_probe.json")
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
if errors:
    raise RuntimeError("Independent asset fresh-open checks failed")
