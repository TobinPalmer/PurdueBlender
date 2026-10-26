"""Fresh-reopen validation for the Rawls Hall R9 project asset."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
ASSET = Path(__file__).resolve().parents[2] / "modular" / "buildings" / "rawls_hall.blend"
OUT = Path(__file__).with_name("round10_reopen_validation.json")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
depsgraph = bpy.context.evaluated_depsgraph_get()
glass = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
wall = bpy.data.objects["RAWL_Masonry_Exterior_Walls"]
frame = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_BronzeMullions"]
plan_wall = bpy.data.objects["RAWL_2026_Plan1086_02_00"]
pane0 = glass.data.polygons[0]
pane_pts = [glass.matrix_world @ glass.data.vertices[i].co for i in pane0.vertices]
inward = (glass.matrix_world.to_3x3() @ pane0.normal).normalized()

def make_bvh(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        return BVHTree.FromPolygons(verts, faces, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()

def ray_coverage(obj, max_distance=1.2):
    tree = make_bvh(obj)
    rows = []
    for poly in glass.data.polygons:
        points = [glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
        center = sum(points, Vector()) / len(points)
        start = center - inward * 0.5
        hit, normal, face, dist = tree.ray_cast(start, inward, max_distance)
        rows.append({"pane": poly.index, "wall_hit_within_test_length": hit is not None,
                     "distance_m": round(float(dist), 4) if dist is not None else None,
                     "face_index": face})
    return rows

def mesh_bounds(obj):
    ev = obj.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        pts = [ev.matrix_world @ v.co for v in me.vertices]
        return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None
    finally:
        ev.to_mesh_clear()

scene_objs = list(scene.objects)
materialless = [o.name for o in scene_objs if o.type == "MESH" and not o.data.materials]
images = [i for i in bpy.data.images if i.source == "FILE"]
external_images = [{"name": i.name, "filepath": i.filepath, "packed": bool(i.packed_file)} for i in images]
outliers = []
for obj in scene_objs:
    if obj.type != "MESH":
        continue
    b = mesh_bounds(obj)
    if b and max(abs(v) for axis in b[:2] for v in axis) > 120:
        outliers.append({"name": obj.name, "bounds": b})

wall_rays = ray_coverage(wall)
plan_rays = ray_coverage(plan_wall, 2.0)
first_center = sum(pane_pts, Vector()) / len(pane_pts)
first_origin = first_center - inward * 0.5
scene_hit, scene_loc, scene_normal, scene_face, scene_obj, scene_mat = scene.ray_cast(
    depsgraph, first_origin, inward, distance=0.8)
report = {
    "validation": "Blender 5.2.3 fresh reopen",
    "asset": str(ASSET.resolve()),
    "sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    "scene": scene.name,
    "scene_object_count": len(scene_objs),
    "scene_mesh_count": sum(o.type == "MESH" for o in scene_objs),
    "root_world_matrix": [list(row) for row in bpy.data.objects["AssetRoot_rawls_hall"].matrix_world],
    "se_glass_pane_count": len(glass.data.polygons),
    "se_frame_bars": len(frame.data.polygons) // 6,
    "exterior_shell_face_count": len(wall.data.polygons),
    "plan1086_wall_face_count": len(plan_wall.data.polygons),
    "exterior_wall_center_rays_clear": sum(not r["wall_hit_within_test_length"] for r in wall_rays),
    "exterior_wall_center_rays_total": len(wall_rays),
    "plan1086_wall_center_rays_clear": sum(not r["wall_hit_within_test_length"] for r in plan_rays),
    "plan1086_wall_center_rays_total": len(plan_rays),
    "first_exterior_ray_hit": {"hit": scene_hit, "object": scene_obj.name if scene_obj else None,
                                "location": list(scene_loc) if scene_hit else None,
                                "distance_m": (scene_loc - first_origin).length if scene_hit else None},
    "shell_evaluated_bounds_local_m": mesh_bounds(wall),
    "plan1086_wall_evaluated_bounds_local_m": mesh_bounds(plan_wall),
    "materialless_meshes": materialless,
    "external_images": external_images,
    "linked_libraries": [lib.filepath for lib in bpy.data.libraries],
    "mesh_bound_outliers_over_120m": outliers,
    "ray_details": {"exterior_shell": wall_rays, "plan1086_wall": plan_rays},
    "limitations": [
        "The current available first-floor plan supports the room 1086 layout; upper-floor partitions and circulation are not newly modeled.",
        "The approximate plan-to-shell registration remains uncertain by about 1 m; the plan-derived wall was given matching pane openings but not shifted.",
        "Interior surfaces, including furnishings, remain schematic/estimated beyond the documented room geometry."
    ]
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({k: report[k] for k in report if k != "ray_details"}, indent=2))

