import json
import math
from pathlib import Path
import bpy
import bmesh

root = Path(bpy.data.filepath).parents[2]
source_path = root / "audit/massing_lilly_hall_e7fc13e/sources/purdue_gis_fid_581.json"
source = json.loads(source_path.read_text(encoding="utf-8-sig"))["features"][0]
ring = source["geometry"]["rings"][0][:-1]

def project(x, y):
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

expected = [project(float(x), float(y)) for x, y in ring]
coll = bpy.data.collections.get("Asset_massing_lilly_hall_e7fc13e")
assert bpy.context.scene.name == "Building_massing_lilly_hall_e7fc13e"
assert coll is not None
shell = bpy.data.objects["Lilly Hall | official footprint shell"]
assert shell.type == "MESH"
assert shell.parent is None
assert all(abs(v) < 1e-7 for v in shell.location)
assert all(abs(v) < 1e-7 for v in shell.rotation_euler)
assert not shell.modifiers

mesh = bmesh.new()
mesh.from_mesh(shell.data)
boundary_edges = sum(1 for edge in mesh.edges if len(edge.link_faces) != 2)
mesh.free()
actual_xy = [(float(v.co.x), float(v.co.y)) for v in shell.data.vertices[:len(expected)]]
nearest = [min(math.dist(q, p) for q in actual_xy) for p in expected]
coords_error_max_m = max(nearest)
world_bounds = [
    min(v.co.x for v in shell.data.vertices), max(v.co.x for v in shell.data.vertices),
    min(v.co.y for v in shell.data.vertices), max(v.co.y for v in shell.data.vertices),
    min(v.co.z for v in shell.data.vertices), max(v.co.z for v in shell.data.vertices),
]
objects = []
for obj in coll.objects:
    objects.append({"name": obj.name, "type": obj.type,
                    "verts": len(obj.data.vertices) if obj.type == "MESH" else None,
                    "modifiers": len(obj.modifiers)})
record = {
    "status": "PASS" if coords_error_max_m < 0.002 and boundary_edges == 0 else "FAIL",
    "blender_version": bpy.app.version_string,
    "reopened_file": bpy.data.filepath,
    "scene": bpy.context.scene.name,
    "collection": coll.name,
    "collection_object_count": len(coll.objects),
    "objects": objects,
    "shell_boundary_edges_not_two_faces": boundary_edges,
    "gis_ring_vertices": len(expected),
    "max_nearest_vertex_difference_m": coords_error_max_m,
    "shell_bounds_xy_z_m": world_bounds,
    "shell_height_m": world_bounds[5],
    "modifiers": [],
    "external_images": [i.filepath for i in bpy.data.images if i.source == "FILE"],
    "source_fid": source["attributes"]["FID"],
    "source_code": source["attributes"]["BLDG_ABBR"],
}
out = Path(bpy.data.filepath).parents[2] / "audit/massing_lilly_hall_e7fc13e/reopen_validation.json"
out.write_text(json.dumps(record, indent=2), encoding="utf-8")
print("LILLY_REOPEN", json.dumps(record))
