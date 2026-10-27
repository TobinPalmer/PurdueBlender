"""Independent exact-hash reopen and structural probe for the ISGL asset."""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / "modular" / "buildings" / "massing_islamic_societyof_greater_lafayette_0130012.blend"
GIS = ROOT / "audit" / "massing_islamic_societyof_greater_lafayette_0130012" / "sources" / "purdue_gis_FID771_SOMSA.json"
OUT = Path(__file__).with_name("fresh_open_probe.json")
EXPECTED = "57d4bdacd2dde6759bbc4892e153266ea0f4856368fa792179a002f5fe9f24fe"
SCENE = "Building_massing_islamic_societyof_greater_lafayette_0130012"
COLLECTION = "Asset_massing_islamic_societyof_greater_lafayette_0130012"
STABLE = "Islamic Society of Greater Lafayette"

def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def lonlat_to_xy(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

before = file_sha(ASSET)
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get(SCENE)
collection = bpy.data.collections.get(COLLECTION)
obj = bpy.data.objects.get(STABLE)
floor = bpy.data.objects.get("ISGL_Schematic_Interior_Open_Gathering_Space_Floor")
label = bpy.data.objects.get("ISGL_Schematic_Interior_Label")
gis = json.loads(GIS.read_text(encoding="utf-8"))
feature = gis["features"][0]
ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
ring_xy = [lonlat_to_xy(lon, lat) for lon, lat in ring]
shell_xy = []
if obj:
    for v in obj.data.vertices:
        w = obj.matrix_world @ v.co
        if abs(w.z) < 1e-5:
            shell_xy.append((w.x, w.y))
ring_errors = [min((math.hypot(x-gx, y-gy) for x,y in shell_xy), default=None) for gx,gy in ring_xy]
material_info = {}
for mat in bpy.data.materials:
    if mat.name.startswith("ISGL |"):
        node_counts = {}
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                node_counts[node.type] = node_counts.get(node.type, 0) + 1
        material_info[mat.name] = {"has_nodes": bool(mat.use_nodes), "node_types": node_counts}
unpacked_external = []
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file:
        p = Path(bpy.path.abspath(img.filepath)).resolve()
        unpacked_external.append({"filepath": img.filepath, "exists": p.exists()})
probe = {
    "sha256_before_open": before,
    "sha256_after_open": file_sha(ASSET),
    "expected_sha_matches": before == EXPECTED,
    "blender_version": bpy.app.version_string,
    "scene": scene.name if scene else None,
    "asset_collection": collection.name if collection else None,
    "collection_objects": [o.name for o in collection.objects] if collection else [],
    "stable_object": obj.name if obj else None,
    "stable_object_location": list(obj.location) if obj else None,
    "stable_mesh_vertex_count": len(obj.data.vertices) if obj else None,
    "stable_mesh_face_count": len(obj.data.polygons) if obj else None,
    "gis_fid": feature["attributes"].get("FID"),
    "gis_name": feature["attributes"].get("BUILDING_N"),
    "gis_address": feature["attributes"].get("ADDRESS"),
    "gis_ring_points": len(ring_xy),
    "gis_wall_ring_max_nearest_error_m": max(ring_errors, default=None),
    "schematic_floor": {
        "exists": floor is not None,
        "dimensions": list(floor.dimensions) if floor else None,
        "status": floor.get("accuracy_status") if floor else None,
        "layout_note": floor.get("layout_note") if floor else None,
        "partitions": 0,
    },
    "schematic_label": {"exists": label is not None, "name": label.name if label else None},
    "materials": material_info,
    "unpacked_external_image_files": unpacked_external,
    "linked_libraries": [lib.filepath for lib in bpy.data.libraries],
    "temporary_preview_objects": [o.name for o in bpy.data.objects if o.name.startswith("TEMP ISGL")],
}
probe["fresh_open_pass"] = all([
    probe["expected_sha_matches"], scene and scene.name == SCENE,
    collection and collection.name == COLLECTION,
    obj and len(obj.data.vertices) == 982 and len(obj.data.polygons) == 747,
    len(ring_errors) == 11 and max(ring_errors) < 0.00002,
    floor and label, not unpacked_external, not bpy.data.libraries,
])
OUT.write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8")
print(json.dumps(probe, indent=2))
if not probe["fresh_open_pass"]:
    raise RuntimeError("Independent exact-hash fresh-open failed")
