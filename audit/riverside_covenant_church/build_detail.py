import bpy
import bmesh
import json
import math
import os
from mathutils import Vector

folder = os.path.dirname(__file__)
with open(os.path.join(folder, "build_config.json"), encoding="utf-8-sig") as f:
    cfg = json.load(f)
with open(os.path.join(folder, "source_mesh_snapshot.json"), encoding="utf-8-sig") as f:
    snapshot = json.load(f)

obj = bpy.data.objects.get(cfg["object_name"])
collection = bpy.data.collections.get(cfg["collection_name"])
if not bpy.data.filepath or obj is None or collection is None or obj not in collection.objects[:] or len(collection.objects) != 1:
    raise RuntimeError("Assigned church collection mismatch")

old_mesh = obj.data
world = obj.matrix_world.copy()
inverse = world.inverted_safe()
ring_local = []
for raw in snapshot["vertices_local"]:
    p = Vector(raw)
    if abs(p.z) < 1e-6:
        xy = (round(p.x, 6), round(p.y, 6))
        if xy not in {(round(q.x, 6), round(q.y, 6)) for q in ring_local}:
            ring_local.append(p.copy())
ring = [world @ p for p in ring_local]
if len(ring) != 4:
    raise RuntimeError(f"Expected the four-node original OSM ring, found {len(ring)}")

# Derive a stable long axis and width from opposite side midpoints; the exact four
# source-ring points remain the wall footprint, including the slight map rotation.
end_a = (ring[0] + ring[1]) * 0.5
end_b = (ring[2] + ring[3]) * 0.5
axis = Vector((end_b.x - end_a.x, end_b.y - end_a.y, 0.0)).normalized()
center = sum(ring, Vector((0.0, 0.0, 0.0))) / len(ring)
cross = Vector((-axis.y, axis.x, 0.0))
if cross.dot((ring[1] + ring[2]) * 0.5 - center) < 0:
    cross.negate()
length = abs((end_b - end_a).dot(axis))
width = abs(((ring[1] + ring[2]) * 0.5 - (ring[0] + ring[3]) * 0.5).dot(cross))
eaves = float(cfg["wall_eaves_m"])
ridge = float(cfg["ridge_height_m"])
overhang = float(cfg["roof_overhang_m"])
if not (0.0 < eaves < ridge and length > width > 0.0):
    raise RuntimeError("Invalid estimated church form dimensions")

tag = cfg["asset_id"]
def make_material(name, color, roughness=0.78, metallic=0.0):
    m = bpy.data.materials.get(tag + "_" + name) or bpy.data.materials.new(tag + "_" + name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m

materials = [
    make_material("Brick", (0.30, 0.12, 0.085)),
    make_material("Stone_Trim", (0.68, 0.59, 0.47)),
    make_material("Glazing", (0.035, 0.11, 0.16), 0.22, 0.04),
    make_material("Slate_Roof", (0.11, 0.12, 0.13), 0.86),
]
vertices, faces, material_ids = [], [], []
def add_face(points, material_index):
    start = len(vertices)
    vertices.extend(tuple(inverse @ p) for p in points)
    faces.append(tuple(range(start, start + len(points))))
    material_ids.append(material_index)

def add_box(center_point, tangent, normal, box_width, depth, height, material_index):
    c = Vector(center_point)
    t = Vector((tangent.x, tangent.y, 0.0)).normalized()
    n = Vector((normal.x, normal.y, 0.0)).normalized()
    z = Vector((0.0, 0.0, 1.0))
    hw, hd, hh = box_width / 2.0, depth / 2.0, height / 2.0
    offsets = [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
               (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    start = len(vertices)
    vertices.extend(tuple(inverse @ (c + t*a + n*b + z*h)) for a,b,h in offsets)
    for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(start + i for i in face))
        material_ids.append(material_index)

# Perimeter wall shell exactly follows the saved bottom-ring points.
for i, a0 in enumerate(ring):
    b0 = ring[(i + 1) % len(ring)]
    a = Vector((a0.x, a0.y, 0.0))
    b = Vector((b0.x, b0.y, 0.0))
    add_face((a, b, Vector((b.x, b.y, eaves)), Vector((a.x, a.y, eaves))), 0)

# One long-axis gable roof is an illustrative completion of the source massing.
half_length = length / 2.0 + overhang
half_width = width / 2.0 + overhang
end_a_roof = center - axis * half_length
end_b_roof = center + axis * half_length
south_a = end_a_roof - cross * half_width
south_b = end_b_roof - cross * half_width
north_a = end_a_roof + cross * half_width
north_b = end_b_roof + cross * half_width
ridge_a = Vector((center.x - axis.x * half_length, center.y - axis.y * half_length, ridge))
ridge_b = Vector((center.x + axis.x * half_length, center.y + axis.y * half_length, ridge))
south_a.z = south_b.z = north_a.z = north_b.z = eaves
add_face((south_a, ridge_a, ridge_b, south_b), 3)
add_face((ridge_a, north_a, north_b, ridge_b), 3)
add_face((south_a, north_a, ridge_a), 0)
add_face((south_b, ridge_b, north_b), 0)

# A restrained, single row of small side windows is schematic and unmeasured.
for side_sign in (-1.0, 1.0):
    outward = cross * side_sign
    wall_center = center + outward * (width / 2.0)
    for fraction in (-0.30, -0.10, 0.10, 0.30):
        p = wall_center + axis * (length * fraction)
        zc, ww, wh = 2.35, 1.25, 1.25
        pane_center = Vector((p.x, p.y, zc)) + outward * 0.07
        add_box(pane_center, axis, outward, ww * 0.78, 0.07, wh, 2)
        frame_center = pane_center + outward * 0.07
        trim = 0.075
        add_box(frame_center + Vector((0,0,wh/2)),axis,outward,ww,0.13,trim,1)
        add_box(frame_center - Vector((0,0,wh/2)),axis,outward,ww,0.13,trim,1)
        add_box(frame_center - axis*(ww/2-trim/2),axis,outward,trim,0.13,wh,1)
        add_box(frame_center + axis*(ww/2-trim/2),axis,outward,trim,0.13,wh,1)

old_name = old_mesh.name
new_mesh = bpy.data.meshes.new(old_name + "_gable_revision")
new_mesh.from_pydata(vertices, [], faces)
for material in materials:
    new_mesh.materials.append(material)
new_mesh.update()
for polygon, material_index in zip(new_mesh.polygons, material_ids):
    polygon.material_index = material_index
bm = bmesh.new()
bm.from_mesh(new_mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(new_mesh)
bm.free()
new_mesh.update()
obj.data = new_mesh
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
new_mesh.name = old_name
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
world_vertices = [world @ v.co for v in new_mesh.vertices]
result = {
    "asset_id": tag,
    "collection_objects": len(collection.objects),
    "source_ring_vertices": len(ring),
    "mesh_vertices": len(new_mesh.vertices),
    "mesh_faces": len(new_mesh.polygons),
    "bounds_world_m": [[round(min(v[i] for v in world_vertices), 6), round(max(v[i] for v in world_vertices), 6)] for i in range(3)],
    "wall_eaves_estimate_m": eaves,
    "ridge_estimate_m": ridge,
    "footprint_preserved": True,
}
print("BUILD_RESULT_JSON=" + json.dumps(result))
