import bpy
import bmesh
import json
import math
import os
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon


EVIDENCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "audit", "alpha_gamma_delta"))
with open(os.path.join(EVIDENCE, "build_config.json"), encoding="utf-8-sig") as handle:
    cfg = json.load(handle)
with open(os.path.join(EVIDENCE, cfg["source_feature_file"]), encoding="utf-8-sig") as handle:
    feature = json.load(handle)

blend_path = bpy.data.filepath
obj = bpy.data.objects.get(cfg["object_name"])
collection = bpy.data.collections.get(cfg["collection_name"])
if not blend_path or obj is None or collection is None or obj not in collection.objects[:]:
    raise RuntimeError("Assigned Alpha Gamma Delta asset structure is missing")
if len(collection.objects) != 1:
    raise RuntimeError("Expected exactly one assigned building object")
if feature["attributes"]["FID"] != 757:
    raise RuntimeError("Source feature does not match Alpha Gamma Delta FID 757")

ring = feature["geometry"]["rings"][0]
if ring[0] == ring[-1]:
    ring = ring[:-1]
lat0, lon0 = 40.4274, -86.9137
points = [
    Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0, 0.0))
    for lon, lat in ring
]
if len(points) < 3:
    raise RuntimeError("Official GIS footprint ring is invalid")

area2 = sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
ring_sign = 1.0 if area2 > 0 else -1.0
centroid = Vector((0.0, 0.0))
for i, point in enumerate(points):
    following = points[(i+1)%len(points)]
    cross = point.x*following.y-following.x*point.y
    centroid.x += (point.x+following.x)*cross
    centroid.y += (point.y+following.y)*cross
centroid /= (3.0*area2)

# Select the minimum-area rotated rectangle from footprint edge directions.
best = None
for i, point in enumerate(points):
    delta = points[(i+1)%len(points)] - point
    if delta.length < 0.05:
        continue
    axis_u = Vector((delta.x, delta.y, 0)).normalized()
    axis_v = Vector((-axis_u.y, axis_u.x, 0))
    u_values = [(p.x-centroid.x)*axis_u.x+(p.y-centroid.y)*axis_u.y for p in points]
    v_values = [(p.x-centroid.x)*axis_v.x+(p.y-centroid.y)*axis_v.y for p in points]
    bounds = (min(u_values), max(u_values), min(v_values), max(v_values))
    area = (bounds[1]-bounds[0])*(bounds[3]-bounds[2])
    if best is None or area < best[0]:
        best = (area, axis_u, axis_v, bounds)
_, axis_u, axis_v, rect_bounds = best
u_min, u_max, v_min, v_max = rect_bounds

materials = []
def make_material(name, color, roughness=0.78, metallic=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
    materials.append(material)
    return len(materials)-1

tag = "AlphaGammaDelta_"
wall = make_material(tag+"Cream_Exterior", cfg["wall_color"])
stone = make_material(tag+"Light_Trim", cfg["stone_color"])
glass = make_material(tag+"Dark_Glazing", cfg["glass_color"], 0.24, 0.04)
roof_mat = make_material(tag+"Charcoal_Roof", cfg["roof_color"], 0.9)
door_mat = make_material(tag+"Red_Entry_Doors", cfg["door_color"])
letter_mat = make_material(tag+"Entry_Letters", (0.70, 0.49, 0.10), 0.58, 0.12)

vertices = []
faces = []
material_ids = []
def polygon_face(coords, material_id):
    start = len(vertices)
    vertices.extend(tuple(Vector(co)) for co in coords)
    faces.append(tuple(range(start, len(vertices))))
    material_ids.append(material_id)

def oriented_box(center, tangent, normal, width, depth, height, material_id):
    center = Vector(center)
    tangent = Vector((tangent.x, tangent.y, 0.0)).normalized()
    normal = Vector((normal.x, normal.y, 0.0)).normalized()
    vertical = Vector((0.0, 0.0, 1.0))
    half_w, half_d, half_h = width/2, depth/2, height/2
    offsets = [(-half_w,-half_d,-half_h),(half_w,-half_d,-half_h),(half_w,half_d,-half_h),(-half_w,half_d,-half_h),
               (-half_w,-half_d,half_h),(half_w,-half_d,half_h),(half_w,half_d,half_h),(-half_w,half_d,half_h)]
    start = len(vertices)
    vertices.extend(tuple(center+tangent*u+normal*v+vertical*z for u,v,z in offsets))
    for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        faces.append(tuple(start+index for index in face))
        material_ids.append(material_id)

eaves = float(cfg["eaves_height_m"])
ridge = float(cfg["ridge_height_m"])
floors = int(cfg["modeled_floors"])
plinth_h = 0.58
story_h = eaves/floors
edges = []
for i, a in enumerate(points):
    b = points[(i+1)%len(points)]
    delta = b-a
    length = delta.length
    if length < 0.05:
        continue
    tangent = Vector((delta.x/length, delta.y/length, 0.0))
    outward = Vector((tangent.y, -tangent.x, 0.0))*ring_sign
    edges.append((a, b, length, tangent, outward))
    a0, b0 = Vector((a.x,a.y,0.0)), Vector((b.x,b.y,0.0))
    a1, b1 = Vector((a.x,a.y,plinth_h)), Vector((b.x,b.y,plinth_h))
    atop, btop = Vector((a.x,a.y,eaves)), Vector((b.x,b.y,eaves))
    polygon_face((a0,b0,b1,a1), stone)
    polygon_face((a1,b1,btop,atop), wall)

# Low roof membrane follows the complete mapped footprint; a compact pitched roof
# above the center carries the illustrated gable silhouette. Roof dimensions are estimates.
for triangle in tessellate_polygon([points]):
    coords = [Vector((points[int(index)].x, points[int(index)].y, eaves)) for index in triangle]
    polygon_face(coords, roof_mat)

# Fit a central gable rectangle inside the irregular footprint where possible.
def local_xy(u, v, z):
    q = Vector((centroid.x, centroid.y, 0.0)) + axis_u*u + axis_v*v
    return Vector((q.x, q.y, z))

def inside_polygon(point):
    inside = False
    x, y = point.x, point.y
    previous = points[-1]
    for current in points:
        if ((current.y > y) != (previous.y > y)) and x < (previous.x-current.x)*(y-current.y)/(previous.y-current.y)+current.x:
            inside = not inside
        previous = current
    return inside

half_u = (u_max-u_min)*0.37
half_v = (v_max-v_min)*0.37
while half_u > 4.0 and half_v > 4.0:
    corners = [local_xy(-half_u,-half_v,0),local_xy(-half_u,half_v,0),local_xy(half_u,-half_v,0),local_xy(half_u,half_v,0)]
    if all(inside_polygon(corner) for corner in corners):
        break
    half_u *= 0.9
    half_v *= 0.9
if half_u <= 4.0 or half_v <= 4.0:
    raise RuntimeError("Unable to place the estimated main gable within the GIS footprint")
s0, s1 = local_xy(-half_u,-half_v,eaves), local_xy(half_u,-half_v,eaves)
n0, n1 = local_xy(-half_u,half_v,eaves), local_xy(half_u,half_v,eaves)
r0, r1 = local_xy(-half_u,0.0,ridge), local_xy(half_u,0.0,ridge)
polygon_face((s0,r0,r1,s1), roof_mat)
polygon_face((r0,n0,n1,r1), roof_mat)
polygon_face((s0,n0,r0), wall)
polygon_face((s1,r1,n1), wall)

# The print source suggests a columned principal entrance with red doors. Its exact
# campus-facing side is not georeferenced, so the longest west-facing GIS edge is used.
entry_edge_index = max((i for i, edge in enumerate(edges) if edge[4].x < -0.55), key=lambda i: edges[i][2], default=None)
if entry_edge_index is None:
    entry_edge_index = max(range(len(edges)), key=lambda i: edges[i][2])
entry_a, entry_b, entry_length, entry_tangent, entry_normal = edges[entry_edge_index]
entry_center = (entry_a+entry_b)*0.5
porch_width = min(9.0, entry_length*0.72)
porch_depth = 2.8
porch_center = entry_center + entry_normal*(porch_depth*0.55)
oriented_box(porch_center+Vector((0,0,0.20)), entry_tangent, entry_normal, porch_width+0.8, porch_depth+0.5, 0.40, stone)
for fraction in (-0.46,-0.16,0.16,0.46):
    post_center = porch_center + entry_tangent*(porch_width*fraction) + Vector((0,0,3.05))
    oriented_box(post_center, entry_tangent, entry_normal, 0.42, 0.42, 5.8, stone)
oriented_box(porch_center+Vector((0,0,6.0)), entry_tangent, entry_normal, porch_width+1.0, porch_depth+0.8, 0.42, stone)
for side in (-1,1):
    oriented_box(entry_center+entry_tangent*(0.52*side)+entry_normal*0.06+Vector((0,0,1.35)), entry_tangent, entry_normal, 1.0, 0.10, 2.55, door_mat)
# Source illustration shows the Alpha Gamma Delta letters over the red double doors.
letter_curve = bpy.data.curves.new("AGD_Entry_Letters", "FONT")
letter_curve.body = "ΑΓΔ"
letter_curve.size = 0.92
letter_curve.extrude = 0.035
letter_curve.align_x = "CENTER"
letter_curve.materials.append(materials[letter_mat])
letter_object = bpy.data.objects.new("AGD_Entry_Letters_Temp", letter_curve)
bpy.context.scene.collection.objects.link(letter_object)
letter_basis = Matrix((entry_tangent, Vector((0.0,0.0,1.0)), entry_normal)).transposed()
letter_object.rotation_euler = letter_basis.to_euler()
letter_object.location = entry_center+entry_normal*0.15+Vector((0.0,0.0,4.05))
evaluated_letters = letter_object.evaluated_get(bpy.context.evaluated_depsgraph_get())
letters_mesh = evaluated_letters.to_mesh()
letter_start = len(vertices)
vertices.extend(tuple(letter_object.matrix_world@vertex.co) for vertex in letters_mesh.vertices)
for face in letters_mesh.polygons:
    faces.append(tuple(letter_start+index for index in face.vertices))
    material_ids.append(letter_mat)
evaluated_letters.to_mesh_clear()
bpy.data.objects.remove(letter_object, do_unlink=True)
for step in range(3):
    width = porch_width*(0.68+0.12*step)
    step_center = entry_center+entry_normal*(0.55+step*0.48)+Vector((0,0,0.12+step*0.10))
    oriented_box(step_center, entry_tangent, entry_normal, width, 0.95, 0.24, stone)

# Regular window bays and restrained limestone-colored trim. This rhythm is
# schematic because no scaled facade drawing was found.
window_width = float(cfg["window_width_m"])
for edge_index, (a,b,length,tangent,outward) in enumerate(edges):
    if length < 4.5 or edge_index == entry_edge_index:
        continue
    count = max(1, int((length-1.8)//4.3))
    spacing = length/(count+1)
    width = min(window_width, spacing*0.68)
    for floor in range(floors):
        z = plinth_h+story_h*(floor+0.5)
        pane_height = 1.45
        if z+pane_height/2 > eaves-0.25:
            continue
        for bay in range(count):
            point = a.lerp(b, spacing*(bay+1)/length)
            center = Vector((point.x,point.y,z))+outward*0.07
            oriented_box(center, tangent, outward, width*0.75, 0.08, pane_height, glass)
            trim_center = center+outward*0.06
            trim_depth = 0.13
            trim_h = 0.10
            oriented_box(trim_center+Vector((0,0,pane_height/2)), tangent,outward,width+0.18,trim_depth,trim_h,stone)
            oriented_box(trim_center-Vector((0,0,pane_height/2)), tangent,outward,width+0.18,trim_depth,trim_h,stone)
            oriented_box(trim_center-tangent*(width/2),tangent,outward,0.10,trim_depth,pane_height+0.1,stone)
            oriented_box(trim_center+tangent*(width/2),tangent,outward,0.10,trim_depth,pane_height+0.1,stone)
    oriented_box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,story_h)), tangent,outward,length+0.03,0.08,0.10,stone)
    oriented_box(Vector(((a.x+b.x)/2,(a.y+b.y)/2,eaves-0.18)),tangent,outward,length+0.15,0.22,0.28,stone)

mesh = bpy.data.meshes.new(obj.name+"_detailed_house")
mesh.from_pydata(vertices, [], faces)
for material in materials:
    mesh.materials.append(material)
mesh.update()
for polygon, material_id in zip(mesh.polygons, material_ids):
    polygon.material_index = material_id
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
old_mesh = obj.data
obj.data = mesh
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
# The original placeholder mesh carried absolute-relative texture references.
# Its unused materials are no longer part of this self-contained library.
for old_material in list(bpy.data.materials):
    if old_material.users == 0:
        bpy.data.materials.remove(old_material)
for image in list(bpy.data.images):
    if image.source == "FILE" and image.users == 0 and not image.packed_file:
        bpy.data.images.remove(image)
mesh.name = obj.name
obj.location = (0.0,0.0,0.0)
obj.rotation_euler = (0.0,0.0,0.0)
obj.scale = (1.0,1.0,1.0)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("BUILD_RESULT_JSON="+json.dumps({
    "asset_id":cfg["asset_id"],
    "source_fid":feature["attributes"]["FID"],
    "ring_vertices":len(points),
    "vertices":len(mesh.vertices),
    "faces":len(mesh.polygons),
    "modeled_floors":floors,
    "eaves_height_estimate_m":eaves,
    "ridge_height_estimate_m":ridge,
    "gable_estimated_size_m":[round(2*half_u,2),round(2*half_v,2)],
    "collection_objects":len(collection.objects)
}))
