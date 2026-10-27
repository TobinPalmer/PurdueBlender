"""Fresh-open geometry and full-asset bounds report for Dauch R3."""
import bpy
import bmesh
import hashlib
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIT = os.path.join(ROOT, "audit", "dauch_alumni_center")
ASSET = os.path.join(ROOT, "modular", "buildings", "dauch_alumni_center.blend")
os.makedirs(AUDIT, exist_ok=True)
COL = bpy.data.collections["Asset_dauch_alumni_center"]
shell = bpy.data.objects["dauch_alumni_center_GIS_outline_primary_shell"]
roof = bpy.data.objects["DAUC_roof_membrane_surface"]

evidence = json.load(open(os.path.join(AUDIT, "dauch_alumni_center_evidence.json"), encoding="utf-8"))
gis_path = os.path.join(AUDIT, "dauch_alumni_center_gis_feature_71.json")
gis = json.load(open(gis_path, encoding="utf-8"))
ring = gis["feature"]["geometry"]["rings"][0]
if math.dist(ring[0], ring[-1]) < 1e-12:
    ring = ring[:-1]
origin = (241.19898675231826, -618.1852061961912)
lat0 = math.radians(40.4274)
source_local = [((lon + 86.9137) * 111412.84 * math.cos(lat0) - origin[0],
                 (lat - 40.4274) * 111040.0 - origin[1]) for lon, lat in ring]
area = sum(source_local[i][0] * source_local[(i+1) % len(source_local)][1]
           - source_local[(i+1) % len(source_local)][0] * source_local[i][1]
           for i in range(len(source_local))) / 2

shell_bm = bmesh.new()
shell_bm.from_mesh(shell.data)
shell_bm.normal_update()
side_faces = [f for f in shell_bm.faces if abs(f.normal.z) < 1e-5]
normal_counts = {"outward": 0, "inward": 0, "ambiguous": 0}
outward_dots = []
for face in side_faces:
    cx = sum(v.co.x for v in face.verts) / len(face.verts)
    cy = sum(v.co.y for v in face.verts) / len(face.verts)
    near_i = min(range(len(source_local)), key=lambda i: math.hypot(
        (source_local[i][0] + source_local[(i+1) % len(source_local)][0]) / 2 - cx,
        (source_local[i][1] + source_local[(i+1) % len(source_local)][1]) / 2 - cy))
    ax, ay = source_local[near_i]
    bx, by = source_local[(near_i+1) % len(source_local)]
    ex, ey = bx-ax, by-ay
    expected = Vector((ey, -ex)) if area > 0 else Vector((-ey, ex))
    dot = face.normal.x * expected.x + face.normal.y * expected.y
    outward_dots.append(dot)
    key = "outward" if dot > 1e-6 else "inward" if dot < -1e-6 else "ambiguous"
    normal_counts[key] += 1
side_count = len(side_faces)
caps = [{"normal_z": f.normal.z, "mean_z": sum(v.co.z for v in f.verts)/len(f.verts)}
        for f in shell_bm.faces if abs(f.normal.z) > 0.99]
signed_volume = shell_bm.calc_volume(signed=True)
assert side_count == 109 and normal_counts["outward"] == 109, normal_counts
assert normal_counts["inward"] == normal_counts["ambiguous"] == 0, normal_counts
assert signed_volume > 0, signed_volume
assert sorted(round(c["normal_z"]) for c in caps) == [-1, 1], caps

shell_xy = list({(round(v.co.x, 6), round(v.co.y, 6)) for v in shell.data.vertices})
footprint_errors = [min(math.hypot(x-a, y-b) for a,b in shell_xy) for x,y in source_local]

depsgraph = bpy.context.evaluated_depsgraph_get()
asset_pts = []
zero_area = []
for obj in COL.all_objects:
    if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
        continue
    evaluated = obj.evaluated_get(depsgraph)
    asset_pts.extend(obj.matrix_world @ Vector(c) for c in evaluated.bound_box)
    if obj.type == "MESH":
        zero_area.extend(f"{obj.name}:{p.index}" for p in obj.data.polygons if p.area < 1e-9)
local_bounds = [[min(p[i] for p in asset_pts) for i in range(3)],
                [max(p[i] for p in asset_pts) for i in range(3)]]
world_xy_bounds = [[local_bounds[0][0] + origin[0], local_bounds[1][0] + origin[0]],
                   [local_bounds[0][1] + origin[1], local_bounds[1][1] + origin[1]]]

external_images = []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath and not image.packed_file:
        p = bpy.path.abspath(image.filepath)
        if not os.path.exists(p):
            external_images.append(image.filepath)

info = {
    "validation_date": "2026-10-27",
    "fresh_open": True,
    "blender_version": bpy.app.version_string,
    "asset_path": "modular/buildings/dauch_alumni_center.blend",
    "asset_sha256": hashlib.sha256(open(ASSET, "rb").read()).hexdigest(),
    "scene": bpy.context.scene.name,
    "export_collection": COL.name,
    "collection_object_count": len(COL.all_objects),
    "used_material_count": len({m.name for o in COL.all_objects if getattr(o.data, "materials", None) for m in o.data.materials if m}),
    "gis_feature_id": 71,
    "source_outer_ring_vertices": len(source_local),
    "gis_shell_vertices": len(shell.data.vertices),
    "gis_shell_faces": len(shell.data.polygons),
    "gis_shell_side_faces": side_count,
    "wall_side_normal_counts": normal_counts,
    "wall_side_min_outward_dot": min(outward_dots),
    "signed_volume_m3": signed_volume,
    "cap_normals": caps,
    "footprint_max_nearest_error_m": max(footprint_errors),
    "footprint_rms_nearest_error_m": math.sqrt(sum(e*e for e in footprint_errors)/len(footprint_errors)),
    "roof_mesh_vertices": len(roof.data.vertices),
    "roof_local_bounds_m": [[min(v.co[i] for v in roof.data.vertices) for i in range(3)],
                             [max(v.co[i] for v in roof.data.vertices) for i in range(3)]],
    "local_full_asset_bounds_m": local_bounds,
    "placement_origin_xy_m": list(origin),
    "world_full_asset_xy_bounds_m": world_xy_bounds,
    "zero_area_mesh_faces": len(zero_area),
    "missing_external_image_files": external_images,
    "GIS_shell_and_local_frame_preserved": max(footprint_errors) < 0.00001
}
assert info["collection_object_count"] == 663
assert info["zero_area_mesh_faces"] == 0, zero_area[:10]
assert not external_images, external_images
assert info["GIS_shell_and_local_frame_preserved"]
with open(os.path.join(AUDIT, "asset_validation_r3.json"), "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)
with open(os.path.join(AUDIT, "asset_bounds_r3.json"), "w", encoding="utf-8") as f:
    json.dump({
        "asset": "modular/buildings/dauch_alumni_center.blend",
        "placement_origin_xy_m": list(origin),
        "local_full_asset_bounds_m": local_bounds,
        "world_full_asset_xy_bounds_m": world_xy_bounds,
        "shell_local_bounds_m": [[-30.668753, -19.686562, 0.35], [29.725935, 16.850447, 14.4]],
        "old_full_asset_world_y_min_m": -641.7151057933592,
        "new_full_asset_world_y_min_m": world_xy_bounds[1][0],
        "new_southward_extension_m": -641.7151057933592 - world_xy_bounds[1][0],
        "note": "Dauch-only bounds report. The shared campus manifest was not edited. Full asset bounds include the south approach sign/planting and roof details; shell footprint and placement remain unchanged."
    }, f, indent=2)
print(json.dumps(info, indent=2))
