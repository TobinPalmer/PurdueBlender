"""Reveal the existing SE curtain wall glazing in the Rawls Hall shell."""
from __future__ import annotations

import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular/buildings/rawls_hall.blend"
OUT = Path(__file__).with_name("round9_change_set.json")
CANDIDATE = Path(__file__).with_name("rawls_hall_r9_candidate.blend")
EXPECTED_R8 = "613174849a753f73aef4299d72223adeb0ceed01cf0fbc7aba4068d05bdf8088"

assert hashlib.sha256(ASSET.read_bytes()).hexdigest() == EXPECTED_R8, "Rawls asset changed since R8; refusing to overwrite."
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
wall = bpy.data.objects["RAWL_Masonry_Exterior_Walls"]
glass = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_Glass"]
frame = bpy.data.objects["RAWL_SE_Diagonal_CurtainWall_BronzeMullions"]
mesh = wall.data

# The two large sloping skins are the exact shell surfaces that occlude the 44
# existing glass quads. The geometry was measured on saved mesh faces 74/75.
outer_face, inner_face = 74, 75
assert len(mesh.polygons) > inner_face
outer_poly, inner_poly = mesh.polygons[outer_face], mesh.polygons[inner_face]
outer_pts = [wall.matrix_world @ mesh.vertices[i].co for i in outer_poly.vertices]
inner_pts = [wall.matrix_world @ mesh.vertices[i].co for i in inner_poly.vertices]
assert len(outer_pts) == len(inner_pts) == 4
outer_bottom = sorted([p for p in outer_pts if abs(p.z - 1.5) < 1e-4], key=lambda p: p.x, reverse=True)
inner_bottom = sorted([p for p in inner_pts if abs(p.z - 1.5) < 1e-4], key=lambda p: p.x, reverse=True)
assert len(outer_bottom) == len(inner_bottom) == 2
start_outer, end_outer = outer_bottom
start_inner, end_inner = inner_bottom
axis = (end_outer - start_outer).normalized()
length = (end_outer - start_outer).length
inner_u_start = (start_inner - start_outer).dot(axis)
inner_u_end = (end_inner - start_outer).dot(axis)
assert inner_u_start < inner_u_end
normal = axis.cross(Vector((0, 0, 1))).normalized()
assert normal.dot((wall.matrix_world.to_3x3() @ outer_poly.normal).normalized()) > 0.99

# Use each existing pane quad as evidence for aperture position and size.
# The 0.09 m reveals allow room for the existing bronze frame bars.
holes = []
for poly in glass.data.polygons:
    pts = [glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
    u = [(p - start_outer).dot(axis) for p in pts]
    z = [p.z for p in pts]
    holes.append((max(0.0, min(u) - 0.09), min(length, max(u) + 0.09),
                  max(1.5, min(z) - 0.08), min(24.08, max(z) + 0.08)))
assert len(holes) == 44
for i, a in enumerate(holes):
    for b in holes[i + 1:]:
        overlap_u = min(a[1], b[1]) - max(a[0], b[0])
        overlap_z = min(a[3], b[3]) - max(a[2], b[2])
        assert overlap_u <= 1e-5 or overlap_z <= 1e-5, (a, b, overlap_u, overlap_z)

verts = [v.co.copy() for v in mesh.vertices]
faces, face_materials = [], []
for poly in mesh.polygons:
    if poly.index in {outer_face, inner_face}:
        continue
    faces.append(tuple(poly.vertices))
    face_materials.append(poly.material_index)
world_to_wall = wall.matrix_world.inverted()
brick_material_index = outer_poly.material_index

def skin_point(start: Vector, end: Vector, u: float, z: float, u_start: float, u_end: float) -> Vector:
    t = (u - u_start) / (u_end - u_start)
    return Vector((start.x + (end.x - start.x) * t,
                   start.y + (end.y - start.y) * t,
                   z))

def add_world_face(points, material_index=brick_material_index):
    ids = []
    for point in points:
        ids.append(len(verts))
        verts.append(world_to_wall @ Vector(point))
    faces.append(tuple(ids))
    face_materials.append(material_index)

def rebuild_skin(start: Vector, end: Vector, u_start: float, u_end: float, reverse: bool, material_index: int):
    us = sorted(set([u_start, u_end] + [round(v, 6) for h in holes for v in h[:2]]))
    zs = sorted(set([1.5, 24.08] + [round(v, 6) for h in holes for v in h[2:]]))
    for u0, u1 in zip(us, us[1:]):
        for z0, z1 in zip(zs, zs[1:]):
            cu, cz = (u0 + u1) / 2, (z0 + z1) / 2
            if any(h[0] < cu < h[1] and h[2] < cz < h[3] for h in holes):
                continue
            p00 = skin_point(start, end, u0, z0, u_start, u_end)
            p10 = skin_point(start, end, u1, z0, u_start, u_end)
            p11 = skin_point(start, end, u1, z1, u_start, u_end)
            p01 = skin_point(start, end, u0, z1, u_start, u_end)
            points = [p00, p10, p11, p01]
            if reverse:
                points.reverse()
            add_world_face(points, material_index)

rebuild_skin(start_outer, end_outer, 0.0, length, False, outer_poly.material_index)
rebuild_skin(start_inner, end_inner, inner_u_start, inner_u_end, True, inner_poly.material_index)

# Close the reveal depth on each aperture with return faces in the existing
# brick material. Keep the two wall skins at their measured separation.
for u0, u1, z0, z1 in holes:
    o00 = skin_point(start_outer, end_outer, u0, z0, 0.0, length)
    o10 = skin_point(start_outer, end_outer, u1, z0, 0.0, length)
    o11 = skin_point(start_outer, end_outer, u1, z1, 0.0, length)
    o01 = skin_point(start_outer, end_outer, u0, z1, 0.0, length)
    i00 = skin_point(start_inner, end_inner, u0, z0, inner_u_start, inner_u_end)
    i10 = skin_point(start_inner, end_inner, u1, z0, inner_u_start, inner_u_end)
    i11 = skin_point(start_inner, end_inner, u1, z1, inner_u_start, inner_u_end)
    i01 = skin_point(start_inner, end_inner, u0, z1, inner_u_start, inner_u_end)
    add_world_face([o00, i00, i01, o01])
    add_world_face([o10, o11, i11, i10])
    add_world_face([o00, o10, i10, i00])
    add_world_face([o01, i01, i11, o11])

new_wall = bpy.data.meshes.new("RAWL_Masonry_Exterior_Walls_SE_Apertures_R9")
new_wall.from_pydata(verts, [], faces)
new_wall.update()
for material in mesh.materials:
    new_wall.materials.append(material)
for polygon, index in zip(new_wall.polygons, face_materials):
    polygon.material_index = index
new_wall.validate(verbose=True, clean_customdata=False)
wall.data = new_wall

# The existing 44 so-called mullions were full bronze boxes with the same 2.8 x
# 3.4 m footprint as each pane. Replace each slab with a slim four-sided frame.
frame_material = frame.data.materials[0]
frame_verts, frame_faces = [], []
box_faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
frame_to_local = frame.matrix_world.inverted()

def add_bar(center, u_axis, z_axis, depth_axis, du, dz, dd):
    base = len(frame_verts)
    c = Vector(center)
    for su, sz, sd in [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                       (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]:
        p = c + u_axis * (su * du / 2) + z_axis * (sz * dz / 2) + depth_axis * (sd * dd / 2)
        frame_verts.append(tuple(frame_to_local @ p))
    frame_faces.extend([tuple(base + i for i in f) for f in box_faces])

up = Vector((0, 0, 1))
for poly in glass.data.polygons:
    points = [glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
    u = [(p - start_outer).dot(axis) for p in points]
    z = [p.z for p in points]
    u0, u1, z0, z1 = min(u), max(u), min(z), max(z)
    width, height = u1 - u0, z1 - z0
    center = skin_point(start_outer, end_outer, (u0 + u1) / 2, (z0 + z1) / 2, 0.0, length) + normal * 0.035
    depth_axis = normal
    bar_width, bar_height, bar_depth = 0.075, 0.075, 0.10
    add_bar(center + up * (height / 2 - bar_height / 2), axis, up, depth_axis,
            width, bar_height, bar_depth)
    add_bar(center - up * (height / 2 - bar_height / 2), axis, up, depth_axis,
            width, bar_height, bar_depth)
    add_bar(center - axis * (width / 2 - bar_width / 2), axis, up, depth_axis,
            bar_width, height, bar_depth)
    add_bar(center + axis * (width / 2 - bar_width / 2), axis, up, depth_axis,
            bar_width, height, bar_depth)

new_frame = bpy.data.meshes.new("RAWL_SE_Diagonal_CurtainWall_Slim_Frames_R9")
new_frame.from_pydata(frame_verts, [], frame_faces)
new_frame.materials.append(frame_material)
new_frame.update()
frame.data = new_frame

# At the first floor, the plan-derived 1086 south-east boundary wall lies just
# behind the curtain wall and was blocking five-plus first-row panes. Rebuild
# only its two long skins with corresponding pane openings, retaining its
# measured 0.16 m section, top/bottom, end caps, and plan-based wall alignment.
plan_wall = bpy.data.objects["RAWL_2026_Plan1086_02_00"]
plan_mesh = plan_wall.data
plan_world_to_local = plan_wall.matrix_world.inverted()
plan_skin_records = []
for poly in plan_mesh.polygons:
    points = [plan_wall.matrix_world @ plan_mesh.vertices[i].co for i in poly.vertices]
    if len(points) != 4 or max(p.z for p in points) - min(p.z for p in points) < 3.0:
        continue
    face_normal = (plan_wall.matrix_world.to_3x3() @ poly.normal).normalized()
    if abs(face_normal.dot(normal)) > 0.98:
        along = [(p - start_outer).dot(axis) for p in points]
        u0, u1 = min(along), max(along)
        low = [p for p, u in zip(points, along) if abs(u - u0) < 1e-4 and p.z < 1e-4]
        high = [p for p, u in zip(points, along) if abs(u - u1) < 1e-4 and p.z < 1e-4]
        if low and high:
            plan_skin_records.append({"index": poly.index, "start": low[0], "end": high[0],
                                      "u0": u0, "u1": u1, "reverse": face_normal.dot(normal) < 0,
                                      "material_index": poly.material_index})
assert len(plan_skin_records) == 2, [r["index"] for r in plan_skin_records]
plan_holes = []
for poly in glass.data.polygons:
    points = [glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
    z = [p.z for p in points]
    if sum(z) / len(z) > 4.5:
        continue
    along = [(p - start_outer).dot(axis) for p in points]
    h = (min(along) - 0.09, max(along) + 0.09,
         max(0.72, min(z) - 0.08), 3.55)
    if all(h[2] < z1 for z1 in (3.55,)) and any(min(h[1], r["u1"]) - max(h[0], r["u0"]) > 0.05 for r in plan_skin_records):
        plan_holes.append(h)
assert len(plan_holes) == 6, len(plan_holes)

plan_verts = [v.co.copy() for v in plan_mesh.vertices]
plan_faces, plan_materials = [], []
for poly in plan_mesh.polygons:
    if poly.index in {r["index"] for r in plan_skin_records}:
        continue
    plan_faces.append(tuple(poly.vertices))
    plan_materials.append(poly.material_index)

def plan_point(record, u, z):
    t = (u - record["u0"]) / (record["u1"] - record["u0"])
    a, b = record["start"], record["end"]
    return Vector((a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, z))

def add_plan_face(points, material_index):
    ids = []
    for point in points:
        ids.append(len(plan_verts))
        plan_verts.append(plan_world_to_local @ Vector(point))
    plan_faces.append(tuple(ids))
    plan_materials.append(material_index)

for record in plan_skin_records:
    clipped_holes = []
    for h in plan_holes:
        u0, u1 = max(h[0], record["u0"]), min(h[1], record["u1"])
        if u1 - u0 > 0.05:
            clipped_holes.append((u0, u1, h[2], h[3]))
    us = sorted(set([record["u0"], record["u1"]] + [round(v, 6) for h in clipped_holes for v in h[:2]]))
    zs = sorted(set([0.0, 3.55] + [round(v, 6) for h in clipped_holes for v in h[2:]]))
    for u0, u1 in zip(us, us[1:]):
        for z0, z1 in zip(zs, zs[1:]):
            cu, cz = (u0 + u1) / 2, (z0 + z1) / 2
            if any(h[0] < cu < h[1] and h[2] < cz < h[3] for h in clipped_holes):
                continue
            pts = [plan_point(record, u0, z0), plan_point(record, u1, z0),
                   plan_point(record, u1, z1), plan_point(record, u0, z1)]
            if record["reverse"]:
                pts.reverse()
            add_plan_face(pts, record["material_index"])

# Close each cut through the measured thickness, using the existing interior
# finish material; opening depth follows both original wall skins.
for h in plan_holes:
    for u0, u1, z0, z1 in [(max(h[0], max(r["u0"] for r in plan_skin_records)),
                            min(h[1], min(r["u1"] for r in plan_skin_records)), h[2], h[3])]:
        if u1 <= u0:
            continue
        a, b = plan_skin_records
        a00, a10 = plan_point(a, u0, z0), plan_point(a, u1, z0)
        a11, a01 = plan_point(a, u1, z1), plan_point(a, u0, z1)
        b00, b10 = plan_point(b, u0, z0), plan_point(b, u1, z0)
        b11, b01 = plan_point(b, u1, z1), plan_point(b, u0, z1)
        imat = b["material_index"]
        add_plan_face([a00, b00, b01, a01], imat)
        add_plan_face([a10, a11, b11, b10], imat)
        add_plan_face([a00, a10, b10, b00], imat)
        add_plan_face([a01, b01, b11, a11], imat)

new_plan_mesh = bpy.data.meshes.new("RAWL_2026_Plan1086_02_SE_WindowOpenings_R9")
new_plan_mesh.from_pydata(plan_verts, [], plan_faces)
new_plan_mesh.update()
for material in plan_mesh.materials:
    new_plan_mesh.materials.append(material)
for poly, index in zip(new_plan_mesh.polygons, plan_materials):
    poly.material_index = index
new_plan_mesh.validate(verbose=True, clean_customdata=False)
plan_wall.data = new_plan_mesh

# Save as a review candidate first; do not replace the project asset until the
# dedicated render and ray validation are inspected.
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE))
report = {
    "source_asset_sha256": EXPECTED_R8,
    "candidate_asset": str(CANDIDATE),
    "candidate_asset_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
    "changed_objects": [wall.name, frame.name, plan_wall.name],
    "source_wall_face_indices_rebuilt": [outer_face, inner_face],
    "plan1086_wall_faces_rebuilt": [r["index"] for r in plan_skin_records],
    "plan1086_first_floor_window_openings": len(plan_holes),
    "glazing_pane_quads": len(holes),
    "pane_apertures": [{"u_m": list(map(float, h[:2])), "z_m": list(map(float, h[2:]))} for h in holes],
    "opening_margin_u_m": 0.09,
    "opening_margin_z_m": 0.08,
    "wall_face_count_before": len(mesh.polygons),
    "wall_face_count_after": len(new_wall.polygons),
    "mullion_geometry_before": {"vertices": 352, "faces": 264, "boxes": 44, "boxes_are_full_pane_slabs": True},
    "mullion_geometry_after": {"vertices": len(new_frame.vertices), "faces": len(new_frame.polygons), "frame_bars": len(frame_faces) // 6},
    "source_basis": [
        {"provider": "Fink Roberts & Petrie, Inc.", "url": "https://frpinc.com/projects/rawls-hall-krannert-school-of-management/", "retrieved": "2026-10-25", "supports": "four-storey Rawls Hall, public entry foyer, and central glass-roofed atrium; project photographs are attributed to Scholer Corp."},
        {"provider": "Purdue University Office of Emergency Preparedness", "url": "https://www.purdue.edu/operations/emergency-preparedness/rawl/", "retrieved": "2026-10-25", "supports": "current building description identifies four floors, large glass windows, and open ceiling design."},
        {"provider": "Purdue University Road School", "url": "https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf", "retrieved": "2026-10-25", "supports": "2024 first-floor plan used by previous rounds; supports first-floor geometry and listed rooms only."}
        ,{"provider": "Purdue University Registrar", "url": "https://www.purdue.edu/registrar/faculty-staff/scheduling/classroom-database/", "retrieved": "2026-10-25", "supports": "official classroom planning index states its room entries include seating charts and planning details; this page is not a detailed floor plan."}
        ,{"provider": "Daniels School of Business IT", "url": "https://kcc.krannert.purdue.edu/Faq/Item/811", "retrieved": "2026-10-25", "supports": "official Rawls 1086 classroom technology guidance; supports modeled classroom use and teaching display context, not exact interior finishes."}
    ],
    "geometry_interpretation": "The 44 existing panes in the modeled SE diagonal curtain wall define window locations and extents. Existing wall skins 74/75 occluded every pane, and the 44 bronze objects were full-pane slabs; those surfaces are cut back to reveal the supplied pane geometry. The first-floor plan-derived Room 1086 south-east wall overlapped six first-row panes, so matching apertures were opened in its two skins. Existing pane positions/sizes were reused; no new exterior window location or size is guessed. The plan-to-shell offset is retained as an approximately 1 m uncertainty rather than asserting surveyed registration.",
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
