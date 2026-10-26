"""Source-backed detailed model for Purdue's Clayton W. Dement Fire Station.

Run with Blender's Python, e.g. blender --background --python this_file.py.
All building geometry is in the campus-world coordinate frame used by the source
massing asset. The master placement remains untouched.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET_ID = "massing_purdue_fire_department_520430b"
ASSET_PATH = os.path.join(ROOT, "modular", "buildings", ASSET_ID + ".blend")
EVIDENCE_DIR = os.path.join(ROOT, "audit", "purdue_fire_department")
PREVIEW_PATH = os.path.join(EVIDENCE_DIR, "purdue_fire_department_preview.png")
COLLECTION_NAME = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID

# Official Purdue GIS building polygon (FeatureServer FID 211, WGS84),
# transformed to the project's documented approximate campus-meter frame.
RING_WGS84 = [
    (-86.9241147517122, 40.4276216855161),
    (-86.9241854031011, 40.4276228258978),
    (-86.9241821799624, 40.4277406362001),
    (-86.9241257519900, 40.4277397348814),
    (-86.9241238657109, 40.4278085215198),
    (-86.9239391369292, 40.4278055769607),
    (-86.9239372109390, 40.4278758732467),
    (-86.9238192544263, 40.4278739812107),
    (-86.9238249563934, 40.4276650685575),
    (-86.9238076437437, 40.4276647702397),
    (-86.9238099658322, 40.4275789652854),
    (-86.9239657078101, 40.4275814584514),
    (-86.9239648847416, 40.4276105540571),
    (-86.9241149878051, 40.4276129568191),
    (-86.9241147517122, 40.4276216855161),
]
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137
RING = [
    ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
     (lat - ORIGIN_LAT) * 111040.0)
    for lon, lat in RING_WGS84
]
RING = RING[:-1]  # last point repeats first

os.makedirs(EVIDENCE_DIR, exist_ok=True)

def material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat, bsdf

def box(name, location, dimensions, mat, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    uv = obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        normal = poly.normal
        axis = max(range(3), key=lambda a: abs(normal[a]))
        axes = [a for a in range(3) if a != axis]
        for li in poly.loop_indices:
            co = obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv.data[li].uv = (co[axes[0]] + dimensions[axes[0]]/2,
                              co[axes[1]] + dimensions[axes[1]]/2)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Small softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def mesh_obj(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if mat:
        mesh.materials.append(mat)
    return obj

def extruded_footprint(name, ring, z0, z1, mat, collection):
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    obj = mesh_obj(name, verts, faces, mat, collection)
    uv = obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        if poly.index < 2:
            for li in poly.loop_indices:
                co = obj.data.vertices[obj.data.loops[li].vertex_index].co
                uv.data[li].uv = (co.x, co.y)
            continue
        edge = poly.index - 2
        i, j = edge, (edge + 1) % n
        edge_len = math.dist(ring[i], ring[j])
        for li in poly.loop_indices:
            vi = obj.data.loops[li].vertex_index
            if vi == i:
                uv.data[li].uv = (0.0, 0.0)
            elif vi == j:
                uv.data[li].uv = (edge_len, 0.0)
            elif vi == n+j:
                uv.data[li].uv = (edge_len, z1-z0)
            else:
                uv.data[li].uv = (0.0, z1-z0)
    return obj

def clip_ring_above(ring, y_cut):
    """Clip a simple footprint polygon to its part north of y_cut."""
    out = []
    prev = ring[-1]
    prev_in = prev[1] >= y_cut
    for cur in ring:
        cur_in = cur[1] >= y_cut
        if cur_in != prev_in:
            t = (y_cut - prev[1]) / (cur[1] - prev[1])
            out.append((prev[0] + t * (cur[0] - prev[0]), y_cut))
        if cur_in:
            out.append(cur)
        prev, prev_in = cur, cur_in
    return out

def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()

# Rebuild this single-asset file from scratch, retaining its fixed export names.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections,):
    for block in list(datablocks):
        if block.name != "Collection":
            datablocks.remove(block)
root = bpy.context.scene.collection
asset = bpy.data.collections.new(COLLECTION_NAME)
root.children.link(asset)
bpy.context.scene.name = SCENE_NAME

brick, brick_bsdf = material("Dement | weathered red-brown brick", (0.34, 0.105, 0.075), 0.9)
# Subtle masonry color/block variation with broad mortar joints; scales follow
# the model's normalized Generated coordinates, so the asset remains portable.
brick_nodes = brick.node_tree.nodes
brick_links = brick.node_tree.links
uvmap = brick_nodes.new("ShaderNodeUVMap")
uvmap.uv_map = "UVMap"
brick_tex = brick_nodes.new("ShaderNodeTexBrick")
brick_tex.inputs["Scale"].default_value = 1.0
brick_tex.inputs["Color1"].default_value = (0.42, 0.145, 0.105, 1)
brick_tex.inputs["Color2"].default_value = (0.29, 0.075, 0.058, 1)
brick_tex.inputs["Mortar"].default_value = (0.12, 0.085, 0.070, 1)
brick_tex.inputs["Mortar Size"].default_value = 0.025
brick_tex.inputs["Mortar Smooth"].default_value = 0.015
brick_tex.inputs["Brick Width"].default_value = 0.5
brick_tex.inputs["Row Height"].default_value = 0.25
brick_links.new(uvmap.outputs["UV"], brick_tex.inputs["Vector"])
brick_links.new(brick_tex.outputs["Color"], brick_bsdf.inputs["Base Color"])
noise = brick_nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 180.0
bump = brick_nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.10
bump.inputs["Distance"].default_value = 0.012
texcoord = brick_nodes.new("ShaderNodeTexCoord")
brick_links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
brick_links.new(noise.outputs["Fac"], bump.inputs["Height"])
brick_links.new(bump.outputs["Normal"], brick_bsdf.inputs["Normal"])

trim, _ = material("Dement | dark red steel trim", (0.36, 0.055, 0.035), 0.55, 0.25)
roofmat, _ = material("Dement | charcoal standing-seam metal", (0.085, 0.095, 0.10), 0.38, 0.55)
cladding, _ = material("Dement | charcoal ribbed metal cladding", (0.16, 0.18, 0.18), 0.4, 0.44)
metal, _ = material("Dement | pale gray sectional bay doors", (0.68, 0.70, 0.69), 0.5, 0.20)
glass, glass_bsdf = material("Dement | blue-gray glazing", (0.08, 0.16, 0.20), 0.2, 0.15)
glass_bsdf.inputs["Metallic"].default_value = 0.18
white, _ = material("Dement | warm white paint", (0.79, 0.77, 0.70), 0.6)
dark, _ = material("Dement | dark doors and openings", (0.035, 0.042, 0.045), 0.65)
concrete, _ = material("Dement | concrete apron", (0.31, 0.32, 0.31), 0.9)

# The primary outer shell follows the official footprint. Source fields list
# two levels and a nominal 15 m extrusion, while current street imagery shows a
# low front office block and a taller apparatus volume; vertical zoning remains
# estimated from images rather than a measured elevation.
base_z = 0.0
office_h = 5.0
shell = extruded_footprint("DMNT | GIS-footprint brick station shell", RING, base_z, office_h, brick, asset)

# Taller attached apparatus hall on the north/rear portion of the footprint.
# The ribbed metal upper cladding is directly visible in the current Street View.
upper_h = 9.2
hall_cut = 37.45
hall_ring = clip_ring_above(RING, hall_cut)
upper = extruded_footprint("DMNT | high apparatus hall | corrugated upper cladding",
                           hall_ring, office_h, office_h+upper_h, cladding, asset)
roof = extruded_footprint("DMNT | high hall flat roof", hall_ring,
                          office_h+upper_h, office_h+upper_h+0.40, roofmat, asset)

# Low office wing roof and a narrow roof edge/fascia.
office_roof = extruded_footprint("DMNT | low roof slab", RING, office_h, office_h+0.30, roofmat, asset)
fascia = box("DMNT | red roof edge above bays", (-870.25, 19.98, 5.18), (25.2, 0.32, 0.20), trim, asset, bevel=0.035)
canopy = box("DMNT | red bay canopy", (-870.3, 19.55, 4.88), (22.0, 0.95, 0.20), trim, asset, bevel=0.04)
for x in (-881.1, -872.8, -864.4, -859.1):
    box("DMNT | canopy support", (x, 19.19, 2.42), (0.14, 0.14, 4.65), trim, asset, bevel=0.015)

# Three vehicle bay doors: two are visible in the current frontal view; the
# third bay remains a source-supported interpretation of Purdue's official
# three-bay description and is set into the recessed southwest front segment.
def sectional_door(name, cx, cy, width, zbase=0.15, height=3.85, facing_south=True):
    # Flush panel and frame, viewed from outside.
    panel_y = cy - 0.16 if facing_south else cy + 0.16
    box(name + " | panel", (cx, panel_y, zbase+height/2), (width, 0.16, height), metal, asset, bevel=0.035)
    # dark frame around the pale overhead panel
    for x in (cx-width/2-0.11, cx+width/2+0.11):
        box(name + " | jamb", (x, panel_y-0.07, zbase+height/2), (0.14, 0.16, height+0.20), dark, asset)
    box(name + " | header", (cx, panel_y-0.07, zbase+height+0.10), (width+0.36, 0.16, 0.16), dark, asset)
    # Six horizontal joints and a glazed top row echo the sectional doors.
    for k in range(1, 6):
        z = zbase + height*k/6
        box(name + " | panel joint", (cx, panel_y-0.09, z), (width-0.12, 0.025, 0.035), white, asset)
    glass_h = 0.52
    for sx in (-1, 0, 1):
        box(name + " | upper light", (cx+sx*(width/3.0), panel_y-0.095, zbase+height-0.60),
            (width/3.0-0.12, 0.035, glass_h), glass, asset)

sectional_door("DMNT | bay 1", -862.05, 19.98, 4.8)
sectional_door("DMNT | bay 2", -867.45, 19.98, 4.8)
sectional_door("DMNT | bay 3", -877.5, 23.55, 4.5)

# Main pedestrian entry and modest station signage, beside the apparatus bays.
box("DMNT | front personnel door", (-858.7, 19.64, 1.18), (1.12, 0.12, 2.35), dark, asset, bevel=0.025)
box("DMNT | front door glass", (-858.7, 19.55, 1.63), (0.73, 0.035, 1.02), glass, asset)
box("DMNT | entrance sidelight", (-859.55, 19.62, 1.55), (0.25, 0.10, 1.85), glass, asset)
box("DMNT | station sign panel", (-858.9, 19.42, 4.04), (2.6, 0.16, 0.55), white, asset, bevel=0.025)

# Front office windows and upper strip windows. Slight offsets keep the glazing
# legible without changing the GIS-controlled footprint.
for x in (-881.0, -874.4, -871.0, -864.2, -860.6):
    box("DMNT | front office window", (x, 19.78, 3.95), (1.05, 0.06, 0.72), glass, asset)
for x in (-880.7, -876.3, -872.0, -867.7, -863.4, -859.0):
    box("DMNT | clerestory band", (x, 31.55, 4.18), (0.92, 0.06, 0.48), glass, asset)

# Narrow vertical metal ribs on the tall apparatus hall's visible east/west
# long walls, echoing the close Street View evidence.
for x in [-888.5 + i*0.82 for i in range(38)]:
    if x >= -858.6:
        break
    box("DMNT | front hall corrugation rib", (x, hall_cut-0.025, office_h+upper_h/2),
        (0.055, 0.07, upper_h-0.12), trim, asset)

# A restrained concrete apron below the engine bays. It is a part of the
# building presentation; it stays within the cadastral building footprint.
box("DMNT | bay threshold", (-870.2, 19.92, 0.035), (24.5, 0.10, 0.07), concrete, asset)

# Temporary photo setup: render the asset, then remove camera/lights so the
# exported library contains only building geometry and materials.
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    # Blender 5.2 names this engine BLENDER_EEVEE; the exception lists the
    # available identifiers in this installation.
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = PREVIEW_PATH
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
world = bpy.data.worlds.new("DMNT preview world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.28, 0.34, 0.42, 1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.7
cam_data = bpy.data.cameras.new("Temporary preview camera")
cam = bpy.data.objects.new("Temporary preview camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (-867.0, -37.0, 18.5)
look_at(cam, (-872.5, 35.5, 7.0))
cam_data.lens = 45
scene.camera = cam
light_data = bpy.data.lights.new("Temporary sun", "SUN")
light = bpy.data.objects.new("Temporary sun", light_data)
scene.collection.objects.link(light)
light.rotation_euler = (math.radians(25), math.radians(-18), math.radians(-25))
light_data.energy = 2.1
fill_data = bpy.data.lights.new("Temporary large softbox", "AREA")
fill = bpy.data.objects.new("Temporary large softbox", fill_data)
scene.collection.objects.link(fill)
fill.location = (-908, -8, 35)
fill_data.energy = 1800
fill_data.size = 32
look_at(fill, (-873, 35, 5))
bpy.ops.render.render(write_still=True)

# Remove temporary render rig before saving the modular asset.
for obj in (cam, light, fill):
    bpy.data.objects.remove(obj, do_unlink=True)
scene.camera = None
scene.world = None
bpy.data.worlds.remove(world)
bpy.ops.wm.save_as_mainfile(filepath=ASSET_PATH)

# Reopen validation in-place: report collection, object counts, bbox and file.
deps = bpy.context.evaluated_depsgraph_get()
mesh_objs = [o for o in asset.objects if o.type == "MESH"]
pts = []
for obj in mesh_objs:
    ev = obj.evaluated_get(deps)
    for corner in ev.bound_box:
        pts.append(ev.matrix_world @ Vector(corner))
bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
report = {
    "asset_id": ASSET_ID,
    "asset_path": os.path.relpath(ASSET_PATH, ROOT).replace("\\", "/"),
    "collection": COLLECTION_NAME,
    "scene": SCENE_NAME,
    "object_count": len(mesh_objs),
    "material_count": len([m for m in bpy.data.materials if m.users > 0]),
    "bounds_world_m": bounds,
    "preview": os.path.relpath(PREVIEW_PATH, ROOT).replace("\\", "/"),
    "notes": [
        "Exterior footprint uses Purdue GIS FeatureServer FID 211 (DMNT), transformed from WGS84 to project campus meters.",
        "Official Purdue source identifies this as the Clayton W. Dement Fire Station at 1250 3rd Street; it is not the DMNT fire station with the same identity mismatch in any other context.",
        "Height zoning and the tall attached apparatus hall are interpreted from official GIS levels and current Street View; the elevated zone is clipped to the source footprint, and its height is not measured.",
        "Three-bay interpretation follows the Purdue historic record; current Street View directly shows two front doors, with the third modelled on the recessed front segment."
    ]
}
with open(os.path.join(EVIDENCE_DIR, "asset_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
