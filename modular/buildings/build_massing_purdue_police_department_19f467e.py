"""Build the Purdue Police Department / Oliver Perkins Terry House asset.

Run with Blender 4.5 in background mode from the PurdueBlender project root.
The GIS perimeter is campus-world XY; vertical dimensions other than the
one-above-grade story count are explicitly estimated from the official photo.
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "massing_purdue_police_department_19f467e.blend")
GIS = os.path.join(ROOT, "audit", "massing_purdue_police_department_19f467e", "sources", "purdue_gis_fid_275.json")
VIEWS = os.path.join(ROOT, "audit", "massing_purdue_police_department_19f467e", "views")
os.makedirs(VIEWS, exist_ok=True)

BUILDING_ID = "massing_purdue_police_department_19f467e"
SCENE_NAME = "Building_" + BUILDING_ID
COLLECTION_NAME = "Asset_" + BUILDING_ID
OBJECT_NAME = "Purdue Police Department"
BASE_Z = 0.0
PLINTH_TOP = 0.24
WALL_TOP = 4.05              # estimated low one-story wall/parapet from photo
ROOF_TOP = 4.45              # estimated roof/parapet silhouette from photo

with open(GIS, encoding="utf-8") as f:
    gis = json.load(f)
feature = next(x for x in gis["features"] if x["attributes"]["FID"] == 275)
mercator_ring = feature["geometry"]["rings"][0]

def campus_xy(x, y):
    # ArcGIS source uses Web Mercator (EPSG:3857). Convert to WGS84, then use
    # the project's documented local campus approximation (EPSG:4326-derived).
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2.0)
    X = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    Y = (lat - 40.4274) * 111040.0
    return (X, Y)

outline = [campus_xy(x, y) for x, y in mercator_ring]
if outline[0] == outline[-1]:
    outline.pop()

# Reuse the manifest scene and exported collection. Keep the original massing
# asset coordinates and named object; remove only its old geometry.
scene = bpy.data.scenes.get(SCENE_NAME) or bpy.context.scene
scene.name = SCENE_NAME
collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
for obj in list(collection.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, roughness=0.72, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

brick = material("TERY warm red brick", (0.31, 0.075, 0.045))
brick_light = material("TERY brick piers", (0.43, 0.13, 0.075))
glass = material("TERY dark ribbon glazing", (0.12, 0.30, 0.32), 0.2, 0.15)
frame = material("TERY charcoal mullions", (0.025, 0.035, 0.04), 0.38, 0.35)
roofmat = material("TERY flat roof membrane", (0.22, 0.23, 0.22), 0.88)
canopy_mat = material("TERY red canopy fascia", (0.53, 0.12, 0.065), 0.55)
door_mat = material("TERY entrance glazing", (0.025, 0.08, 0.1), 0.25, 0.08)

parts = []
def mesh_obj(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    parts.append(obj)
    return obj

def prism(name, polygon, z0, z1, mat):
    n = len(polygon)
    verts = [(x, y, z0) for x, y in polygon] + [(x, y, z1) for x, y in polygon]
    faces = [tuple(range(n)), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n + n, i+n) for i in range(n)]
    return mesh_obj(name, verts, faces, mat)

def box(name, center, dims, mat):
    x, y, z = center
    dx, dy, dz = (v / 2 for v in dims)
    verts = [(x+sx*dx, y+sy*dy, z+sz*dz)
             for sx, sy, sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return mesh_obj(name, verts, faces, mat)

# Source footprint is one closed building polygon (not a curb/plaza envelope).
prism("TERY structural footprint walls", outline, BASE_Z, WALL_TOP, brick)
prism("TERY flat roof and parapet", outline, WALL_TOP, ROOF_TOP, roofmat)

# Official exterior photo shows a long horizontal glazed ribbon with brick
# piers. This is a representative long east frontage; GIS/photo do not identify
# compass side or exact bay spacing, so these are documented as visual estimates.
east_x = max(x for x, _ in outline)
east_pts = sorted([(x, y) for x, y in outline if x > east_x - 0.35], key=lambda p: p[1])
y_min = min(y for x, y in east_pts)
y_max = max(y for x, y in east_pts)
front_x = east_x + 0.12
run = y_max - y_min
window_bottom, window_top = 1.15, 3.05
box("TERY continuous dark ribbon glass", (front_x, (y_min+y_max)/2, (window_bottom+window_top)/2),
    (0.18, run-0.25, window_top-window_bottom), glass)
# Regular vertical mullions; visual rhythm is inferred from the official photo.
for i in range(1, 17):
    yy = y_min + run * i / 17.0
    box("TERY ribbon mullion %02d" % i, (front_x+0.10, yy, (window_bottom+window_top)/2),
        (0.12, 0.10, window_top-window_bottom+0.06), frame)
# Projecting brick piers at a broader cadence behind the glazing.
for i in range(0, 9):
    yy = y_min + run * (i + 0.5) / 9.0
    box("TERY facade brick pier %02d" % i, (east_x+0.12, yy, (PLINTH_TOP+WALL_TOP)/2),
        (0.38, 0.28, WALL_TOP-PLINTH_TOP), brick_light)

# Public-photo entrance canopy and doorway. Its frontage and location are
# approximate: the photo has no georeferenced view direction or labeled door.
entry_y = y_min + run * 0.29
box("TERY entrance glazed door", (east_x+0.24, entry_y, 1.42), (0.14, 1.65, 2.36), door_mat)
box("TERY entrance canopy soffit", (east_x+0.55, entry_y, 3.35), (1.50, 4.25, 0.18), canopy_mat)
box("TERY entrance canopy fascia", (east_x+1.27, entry_y, 3.23), (0.12, 4.25, 0.42), canopy_mat)
for dy in (-1.75, 1.75):
    box("TERY canopy support", (east_x+1.02, entry_y+dy, 1.80), (0.10, 0.10, 2.90), frame)

# Join all components into the manifest's single expected object.
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
asset = bpy.context.object
asset.name = OBJECT_NAME
asset.data.name = OBJECT_NAME + "Mesh"
asset.location = (0.0, 0.0, 0.0)
asset.rotation_euler = (0.0, 0.0, 0.0)
asset.scale = (1.0, 1.0, 1.0)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
for c in list(asset.users_collection):
    if c != collection:
        c.objects.unlink(asset)
if asset.name not in collection.objects:
    collection.objects.link(asset)

# Export scene contains the asset only; rendering camera/lights are temporary.
for obj in list(scene.objects):
    if obj != asset:
        bpy.data.objects.remove(obj, do_unlink=True)

# Preview render from southeast looking at the long ribbon frontage.
world = scene.world or bpy.data.worlds.new("TERY preview world")
scene.world = world
world.color = (0.18, 0.18, 0.18)
cam_data = bpy.data.cameras.new("PreviewCamera")
cam = bpy.data.objects.new("PreviewCamera", cam_data)
scene.collection.objects.link(cam)
cam.location = (east_x + 48, (y_min+y_max)/2 - 4, 6.8)
target = Vector((sum(x for x, _ in outline)/len(outline), (y_min+y_max)/2, 2.0))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_data.type = "ORTHO"
cam_data.ortho_scale = 88
scene.camera = cam
ld = bpy.data.lights.new("PreviewKey", "AREA")
light = bpy.data.objects.new("PreviewKey", ld)
scene.collection.objects.link(light)
light.location = (east_x+22, (y_min+y_max)/2-22, 32)
ld.energy = 8500
ld.shape = "DISK"
ld.size = 28
light.rotation_euler = (Vector((east_x, (y_min+y_max)/2, 1.5))-light.location).to_track_quat("-Z", "Y").to_euler()
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1500
scene.render.resolution_y = 950
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(VIEWS, "purdue_police_department_frontage.png")
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
bpy.ops.render.render(write_still=True)

# Remove temporary camera/lights from deliverable, then save clean library.
for obj in (cam, light):
    bpy.data.objects.remove(obj, do_unlink=True)
scene.camera = None
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print("SAVED", ASSET)
