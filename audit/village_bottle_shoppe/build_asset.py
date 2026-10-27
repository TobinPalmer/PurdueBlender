"""Rebuild the assigned Village Bottle Shoppe library from documented sources.

This script intentionally edits only the assigned asset. It preserves the stable
scene, collection, object names and the campus-coordinate frame used by this
massing library. Its procedural materials are generated inside the .blend.
"""
import bpy
import bmesh
import json
import math
import os
from mathutils import Vector, Quaternion

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_village_bottle_shoppe_6a17e23.blend")
SOURCE_JSON = os.path.join(os.path.dirname(__file__), "sources", "indiana_building_footprints_nearby.json")
ID = "massing_village_bottle_shoppe_6a17e23"
SCENE = "Building_" + ID
COLLECTION = "Asset_" + ID
OBJECT = "Village Bottle Shoppe"

with open(SOURCE_JSON, "r", encoding="utf-8-sig") as f:
    source = json.load(f)
feature = next(f for f in source["features"] if f["attributes"]["objectid"] == 409442)
ring = feature["geometry"]["rings"][0][:-1]

# Project the Indiana statewide 2018 building polygon with the project transform.
lat0, lon0 = 40.4274, -86.9137
scale_x = 111412.84 * math.cos(math.radians(lat0))
def project(lon, lat):
    return Vector(((lon - lon0) * scale_x, (lat - lat0) * 111040.0, 0.0))

# Re-index the near-rectangular polygon as front-left, front-right, rear-left,
# rear-right. The GIS polygon is a rotated rectangle; front is the northwest edge.
xy = [project(lon, lat) for lon, lat in ring]
footprint_area_calc = abs(sum(xy[i].x*xy[(i+1)%len(xy)].y - xy[(i+1)%len(xy)].x*xy[i].y for i in range(len(xy)))) / 2.0
footprint_perimeter_calc = sum((xy[(i+1)%len(xy)]-xy[i]).length for i in range(len(xy)))
long_edges = [(i, (i + 1) % 4, (xy[(i + 1) % 4] - xy[i]).length) for i in range(4)]
short_i = min(range(4), key=lambda i: long_edges[i][2])
# The first short edge is the front-left to rear-left edge; its next vertex is
# front-right along the long, street-facing side.
p_fl = xy[short_i]
p_fr = xy[(short_i - 1) % 4]
p_rl = xy[(short_i + 1) % 4]
u_vec = p_fr - p_fl
v_vec = p_rl - p_fl
L, D = u_vec.length, v_vec.length
u = u_vec.normalized()
v = v_vec.normalized()

def world(s, t, z):
    return (p_fl + u * s + v * t + Vector((0, 0, z)))

scene = bpy.data.scenes.get(SCENE)
asset_collection = bpy.data.collections.get(COLLECTION)
obj = bpy.data.objects.get(OBJECT)
assert scene and asset_collection and obj and obj.type == "MESH"
assert obj.name == OBJECT and asset_collection.name == COLLECTION
for c in list(obj.users_collection):
    c.objects.unlink(obj)
asset_collection.objects.link(obj)
obj.data.clear_geometry()
obj.data.materials.clear()

# Procedural, portable facade/roof materials.
def material(name, color, roughness=0.6, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    return m, bs

def add_noise_bump(mat, scale, strength, distance):
    nt = mat.node_tree
    bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 3.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])

brick, _ = material("VBS_Red_Brick", (0.34, 0.105, 0.075), 0.84)
add_noise_bump(brick, 75.0, 0.12, 0.012)
brick_shader = next(n for n in brick.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
brick_pattern = brick.node_tree.nodes.new("ShaderNodeTexBrick")
brick_pattern.inputs["Color1"].default_value = (0.39, 0.12, 0.085, 1.0)
brick_pattern.inputs["Color2"].default_value = (0.27, 0.075, 0.052, 1.0)
brick_pattern.inputs["Mortar"].default_value = (0.20, 0.16, 0.13, 1.0)
brick_pattern.inputs["Scale"].default_value = 1.0
brick_pattern.inputs["Mortar Size"].default_value = 0.035
brick_coord = brick.node_tree.nodes.new("ShaderNodeTexCoord")
brick.node_tree.links.new(brick_coord.outputs["UV"], brick_pattern.inputs["Vector"])
brick.node_tree.links.new(brick_pattern.outputs["Color"], brick_shader.inputs["Base Color"])
block, _ = material("VBS_Tan_Masonry_Block", (0.60, 0.52, 0.40), 0.82)
block_shader = next(n for n in block.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
block_pattern = block.node_tree.nodes.new("ShaderNodeTexBrick")
block_pattern.inputs["Color1"].default_value = (0.68, 0.59, 0.46, 1.0)
block_pattern.inputs["Color2"].default_value = (0.56, 0.49, 0.39, 1.0)
block_pattern.inputs["Mortar"].default_value = (0.39, 0.36, 0.31, 1.0)
block_pattern.inputs["Scale"].default_value = 1.0
block_pattern.inputs["Mortar Size"].default_value = 0.045
block_coord = block.node_tree.nodes.new("ShaderNodeTexCoord")
block.node_tree.links.new(block_coord.outputs["UV"], block_pattern.inputs["Vector"])
block.node_tree.links.new(block_pattern.outputs["Color"], block_shader.inputs["Base Color"])
roof, _ = material("VBS_Flat_Roof_Membrane", (0.09, 0.105, 0.11), 0.82)
add_noise_bump(roof, 80.0, 0.16, 0.012)
trim, _ = material("VBS_White_Metal_Fascia", (0.86, 0.85, 0.79), 0.54, 0.2)
sign_red, _ = material("VBS_Sign_Channel_Letter_Red", (0.90, 0.008, 0.004), 0.38, 0.15)
glass, bs = material("VBS_Storefront_Glass", (0.085, 0.19, 0.24), 0.14, 0.22)
bs.inputs["Coat Weight"].default_value = 0.45
frame, _ = material("VBS_Black_Aluminum", (0.025, 0.03, 0.032), 0.33, 0.55)
concrete, _ = material("VBS_Concrete", (0.43, 0.42, 0.39), 0.9)
mat_list = [brick, block, roof, trim, sign_red, glass, frame, concrete]

parts = []
def polygon(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        n2d = Vector((poly.normal.x, poly.normal.y, 0.0))
        horizontal = "s" if abs(n2d.dot(v)) >= abs(n2d.dot(u)) else "t"
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            rel = Vector((co.x-p_fl.x, co.y-p_fl.y, 0.0))
            hcoord = rel.dot(u if horizontal == "s" else v)
            uv_layer.data[li].uv = (hcoord, co.z)
    mesh.materials.append(mat)
    mesh.update()
    piece = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(piece)
    piece.data.materials.clear()
    piece.data.materials.append(mat)
    parts.append(piece)
    return piece

def box_local(name, s0, t0, z0, w, d, h, mat):
    vtx = [world(s0-w/2, t0-d/2, z0-h/2), world(s0+w/2, t0-d/2, z0-h/2),
           world(s0+w/2, t0+d/2, z0-h/2), world(s0-w/2, t0+d/2, z0-h/2),
           world(s0-w/2, t0-d/2, z0+h/2), world(s0+w/2, t0-d/2, z0+h/2),
           world(s0+w/2, t0+d/2, z0+h/2), world(s0-w/2, t0+d/2, z0+h/2)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return polygon(name, vtx, faces, mat)

def prism(name, points, z0, z1, mat):
    # Extruded polygon in the skewed campus-coordinate footprint.
    n = len(points)
    verts = [world(s,t,z0) for s,t in points] + [world(s,t,z1) for s,t in points]
    faces = [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return polygon(name, verts, faces, mat)

# Simple commercial street store. The low pitch is hidden behind the eaves in
# the direct #4 location photos; the roof height is estimated, not surveyed.
footprint = [(0,0),(L,0),(L,D),(0,D)]
prism("Footing_Concrete", footprint, 0.04, 0.34, concrete)
prism("Masonry_Main_Volume", footprint, 0.30, 4.20, brick)
roof_level = 4.46
box_local("Flat_Roof_Deck", L/2, D/2, roof_level, L+0.46, D+0.46, 0.24, roof)
# The subject photos show a clean white overhang/cornice concealing a shallow roof.
box_local("Front_White_Fascia", L/2, -0.07, 4.48, L+0.55, 0.34, 0.36, trim)
box_local("Rear_White_Fascia", L/2, D+0.07, 4.48, L+0.55, 0.34, 0.36, trim)
box_local("West_White_Fascia", -0.07, D/2, 4.48, 0.34, D+0.55, 0.36, trim)
box_local("East_White_Fascia", L+0.07, D/2, 4.48, 0.34, D+0.55, 0.36, trim)

# Storefront glazing and black aluminum frames on the northwest long elevation.
front_t = -0.24
def storefront_window(tag, s, width, sill=1.22, height=2.22):
    zc = sill + height/2
    box_local(tag+"_Outer_Frame", s, front_t, zc, width+0.12, 0.12, height+0.12, frame)
    box_local(tag+"_Glass", s, front_t-0.075, zc, width-0.12, 0.035, height-0.12, glass)
    box_local(tag+"_Lower_Rail", s, front_t-0.11, sill+0.70, width-0.12, 0.055, 0.06, frame)

for i, (s, w) in enumerate([(2.45,2.5),(5.15,2.5),(7.85,2.5),(10.55,2.5)]):
    storefront_window("Display_Glazing_%02d" % i, s, w, sill=1.22, height=2.05)
# The exact-branch photograph shows continuous brick below the sign and no
# entry in this visible elevation, so no unsupported front door is invented.
# The direct photo shows a tan masonry bay below the storefront glazing, with
# exposed red brick continuing to grade beneath the sign and at the side wall.
box_local("Front_Tan_Masonry_Storefront_Bay", 6.25, -0.115, 0.78, 12.50, 0.23, 0.90, block)
# Tan masonry continues into a low sill/base immediately below the display glass.
box_local("Front_Upper_Brick_Lintel", L/2, -0.10, 3.38, L+0.15, 0.20, 0.28, brick)

# Exact-branch photo shows red channel letters on the brick bay. Model a compact
# 5x7 raised font from closed cells; this keeps the exported mesh manifold.
font5x7 = {
    "A":["01110","10001","10001","11111","10001","10001","10001"],
    "B":["11110","10001","10001","11110","10001","10001","11110"],
    "E":["11111","10000","10000","11110","10000","10000","11111"],
    "G":["01111","10000","10000","10111","10001","10001","01111"],
    "H":["10001","10001","10001","11111","10001","10001","10001"],
    "I":["11111","00100","00100","00100","00100","00100","11111"],
    "L":["10000","10000","10000","10000","10000","10000","11111"],
    "O":["01110","10001","10001","10001","10001","10001","01110"],
    "P":["11110","10001","10001","11110","10000","10000","10000"],
    "S":["01111","10000","10000","01110","00001","00001","11110"],
    "T":["11111","00100","00100","00100","00100","00100","00100"],
    "V":["10001","10001","10001","10001","01010","01010","00100"]
}
sign_text = "VILLAGE BOTTLE SHOPPE"
cell_w, cell_h, col_gap, row_gap = 0.10, 0.12, 0.0, 0.0
char_width = 5*cell_w + 4*col_gap
char_gap, word_gap = 0.09, 0.40
sign_width = sum(char_width if ch != " " else 0 for ch in sign_text) + \
             sum(word_gap if sign_text[i] == " " else char_gap for i in range(len(sign_text)-1))
cursor_s = L*0.72 - sign_width/2
sign_verts, sign_faces = [], []
for i, ch in enumerate(sign_text):
    if ch == " ":
        cursor_s += word_gap
        continue
    glyph = font5x7[ch]
    for row, bits in enumerate(glyph):
        for col, bit in enumerate(bits):
            if bit != "1": continue
            sc = cursor_s + col*(cell_w+col_gap) + cell_w/2
            zc = 3.79 + (3-row)*(cell_h+row_gap)
            tc = -0.31
            cell = [world(sc-cell_w/2,tc-0.08,zc-cell_h/2), world(sc+cell_w/2,tc-0.08,zc-cell_h/2),
                    world(sc+cell_w/2,tc+0.08,zc-cell_h/2), world(sc-cell_w/2,tc+0.08,zc-cell_h/2),
                    world(sc-cell_w/2,tc-0.08,zc+cell_h/2), world(sc+cell_w/2,tc-0.08,zc+cell_h/2),
                    world(sc+cell_w/2,tc+0.08,zc+cell_h/2), world(sc-cell_w/2,tc+0.08,zc+cell_h/2)]
            start = len(sign_verts)
            sign_verts.extend(cell)
            sign_faces.extend([tuple(start+j for j in face) for face in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
    if i < len(sign_text)-1 and sign_text[i+1] != " ": cursor_s += char_width + char_gap
    elif i < len(sign_text)-1: cursor_s += char_width
polygon("Village_Bottle_Shoppe_Channel_Letters", sign_verts, sign_faces, sign_red)

# Subtle black wall lights frame the front retail window/sign band.
for i, s in enumerate([0.45, 14.85, L-0.65]):
    box_local("Wall_Sconce_%02d" % i, s, -0.22, 3.18, 0.18, 0.14, 0.48, frame)

# Merge all closed architectural components into the one stable source object.
base = obj
for p in parts:
    p.select_set(True)
base.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.object.join()
base.name = OBJECT
base.data.name = OBJECT + "Mesh"
bm = bmesh.new()
bm.from_mesh(base.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(base.data)
bm.free()
base.data.validate(verbose=True)
for c in list(base.users_collection):
    if c != asset_collection:
        c.objects.unlink(base)
if asset_collection not in base.users_collection:
    asset_collection.objects.link(base)
base.location = (0,0,0)
base.rotation_euler = (0,0,0)
base.scale = (1,1,1)
base.data.update()
for i in range(len(base.data.materials)-1, -1, -1):
    if base.data.materials[i] is None and not any(p.material_index == i for p in base.data.polygons):
        base.data.materials.pop(index=i)

# Asset library scenes remain clean: one scene, one collection, one exported mesh.
for c in list(scene.collection.children):
    if c != asset_collection:
        scene.collection.children.unlink(c)
for o in list(scene.objects):
    if o != base:
        bpy.data.objects.remove(o, do_unlink=True)

# Render a review image with temporary ground, camera and lights, then remove all
# preview-only objects before saving the portable library.
preview_col = bpy.data.collections.new("__PreviewOnly")
scene.collection.children.link(preview_col)
def link_preview(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    preview_col.objects.link(o)
    return o
ground_mesh = bpy.data.meshes.new("__PreviewGroundMesh")
ground_mesh.from_pydata([(-1000,-1000,0),(1000,-1000,0),(1000,1000,0),(-1000,1000,0)], [], [(0,1,2,3)])
ground_obj = bpy.data.objects.new("__PreviewGround", ground_mesh)
preview_col.objects.link(ground_obj)
ground_mat, _ = material("__PreviewGroundMaterial", (0.21,0.23,0.22), 0.9)
ground_mesh.materials.append(ground_mat)
cam_data = bpy.data.cameras.new("__PreviewCameraData")
cam = bpy.data.objects.new("__PreviewCamera", cam_data)
preview_col.objects.link(cam)
center = Vector((p_fl.x + u.x*L/2 + v.x*D/2, p_fl.y + u.y*L/2 + v.y*D/2, 4.3))
cam.location = center + Vector((-44,58,38))
cam.rotation_euler = (center-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type = "ORTHO"
cam.data.ortho_scale = 49.0
scene.camera = cam
for i,(loc,power,size) in enumerate([((center.x-15,center.y-25,32),520,22),((center.x+20,center.y+8,24),310,18),((center.x-3,center.y+18,20),230,14)]):
    ld = bpy.data.lights.new("__PreviewArea%d"%i, "AREA")
    lo = bpy.data.objects.new("__PreviewArea%d"%i, ld)
    preview_col.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (center-lo.location).to_track_quat("-Z","Y").to_euler()
    ld.energy=power; ld.shape="DISK"; ld.size=size
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1100
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.world.color = (0.18,0.18,0.18)
scene.render.filepath = os.path.join(os.path.dirname(__file__), "preview_village_bottle_shoppe.png")
bpy.ops.render.render(write_still=True)
scene.camera = None
for o in list(preview_col.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(preview_col)
if ground_mat.name in bpy.data.materials: bpy.data.materials.remove(ground_mat)

# Store source summary as custom properties on the exported mesh for traceability.
base["source_name"] = "Village Bottle Shoppe, 1832 Northwestern Ave, West Lafayette, IN"
base["footprint_source"] = "Indiana Statewide LiDAR Derived Building Footprints 2016-2020, objectid 409442, lidar year 2018"
base["footprint_area_m2"] = float(footprint_area_calc)
base["source_shape_area_raw"] = float(feature["attributes"]["SHAPE__Area"])
base["source_shape_length_raw"] = float(feature["attributes"]["SHAPE__Length"])
base["footprint_method"] = "Vertices projected with project local approximation; polygon preserved; no bbox rescaling"
base["height_status"] = "estimated from exact-branch storefront photos; low one-story parapet, not surveyed"
base["interior_status"] = "omitted: no credible public floor plan found"
base["asset_id"] = ID

bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("SAVED_ASSET", ASSET)
print("MEASURED_FOOTPRINT", json.dumps({"area_geometry_m2":footprint_area_calc,"perimeter_geometry_m":footprint_perimeter_calc,"source_shape_area_raw":feature["attributes"]["SHAPE__Area"],"source_shape_length_raw":feature["attributes"]["SHAPE__Length"],"long_m":L,"depth_m":D,"campus_corners":[list(world(s,t,0)) for s,t in footprint],"wall_eave_est_m":4.20,"fascia_top_est_m":4.66,"source_shape_area_units":"undocumented; discrepant from polygon geometry"}))
