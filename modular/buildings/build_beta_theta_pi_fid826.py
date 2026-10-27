"""Build the campus-coordinate Beta Theta Pi massing asset from Purdue GIS FID 826.

Run with Blender 5.x background Python. No external asset dependencies are used.
The GIS ring is the precise base footprint; facade placement and height are
photographic interpretations recorded in audit/beta_theta_pi/evidence.json.
"""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIS = ROOT / "audit" / "beta_theta_pi" / "sources" / "purdue_buildings_fid826_4326.json"
OUT = ROOT / "modular" / "buildings" / "massing_beta_theta_pi_fid826.blend"
ORIGIN_LAT = 40.4274
ORIGIN_LON = -86.9137

with GIS.open("r", encoding="utf-8") as f:
    feature = json.load(f)["features"][0]
assert feature["attributes"]["FID"] == 826
assert feature["attributes"]["BUILDING_N"] == "Beta Theta Pi"
ring_ll = feature["geometry"]["rings"][0]
ring = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
         (lat - 40.4274) * 111040.0) for lon, lat in ring_ll]

# Clean background state and make the requested stable names.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.meshes):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
scene = bpy.context.scene
scene.name = "Building_massing_beta_theta_pi_fid826"
collection = bpy.data.collections.new("Asset_massing_beta_theta_pi_fid826")
scene.collection.children.link(collection)

def link_object(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def mat_brick(name, low, high, scale=25.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*low, 1.0)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.78
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.24
    ramp.color_ramp.elements[0].color = (*low, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (*high, 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.17
    bump.inputs["Distance"].default_value = 0.025
    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m

brick = mat_brick("Beta Theta Pi | warm red-brown brick", (0.19, 0.055, 0.035), (0.39, 0.13, 0.075), 38.0)
roof = mat_brick("Beta Theta Pi | charcoal slate roof", (0.035, 0.045, 0.05), (0.12, 0.14, 0.15), 52.0)
stone = mat_brick("Beta Theta Pi | pale limestone trim", (0.42, 0.36, 0.28), (0.70, 0.63, 0.52), 34.0)
wood = mat_brick("Beta Theta Pi | painted cream window frames", (0.58, 0.52, 0.41), (0.86, 0.80, 0.68), 35.0)
glass = bpy.data.materials.new("Beta Theta Pi | dark reflective window glass")
glass.diffuse_color = (0.08, 0.13, 0.16, 1)
glass.use_nodes = True
glass_bsdf = glass.node_tree.nodes.get("Principled BSDF")
glass_bsdf.inputs["Base Color"].default_value = (0.055, 0.12, 0.15, 1)
glass_bsdf.inputs["Roughness"].default_value = 0.2
glass_bsdf.inputs["Metallic"].default_value = 0.18
glass_bsdf.inputs["IOR"].default_value = 1.45

def mesh_obj(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj

# Vertical wall surface follows the source polygon exactly. Its height is a
# separate estimate from the GIS extrusion value and chapter-house imagery.
wall_h = 6.7
verts = [(x, y, z) for z in (0.0, wall_h) for x, y in ring]
n = len(ring)
faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
faces.append(tuple(range(2 * n - 1, n - 1, -1)))
mesh_obj("BetaThetaPi_GIS_826_exact_perimeter_walls", verts, faces, brick)

# Separate gable roof solids are photographic massing interpretations; the
# footprint base below remains the GIS authority. Ridge axes follow the house's
# dominant north-south orientation seen in the aerial tile and chapter photos.
def gable_roof(name, cx, cy, width, length, eave_z, ridge_z, axis="y"):
    if axis == "y":
        pts = [(-width/2, -length/2, eave_z), (width/2, -length/2, eave_z),
               (width/2, length/2, eave_z), (-width/2, length/2, eave_z),
               (0, -length/2, ridge_z), (0, length/2, ridge_z)]
        xy = lambda p: (cx + p[0], cy + p[1], p[2])
        faces = [(0, 4, 5, 3), (4, 1, 2, 5), (0, 1, 4), (3, 5, 2), (0, 3, 2, 1)]
    else:
        pts = [(-length/2, -width/2, eave_z), (length/2, -width/2, eave_z),
               (length/2, width/2, eave_z), (-length/2, width/2, eave_z),
               (-length/2, 0, ridge_z), (length/2, 0, ridge_z)]
        xy = lambda p: (cx + p[0], cy + p[1], p[2])
        faces = [(0, 1, 5, 4), (4, 5, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 2, 1)]
    return mesh_obj(name, [xy(p) for p in pts], faces, roof)

gable_roof("Main_long_slate_gable", 816.4, -396.8, 10.6, 25.8, wall_h, 10.5, "y")
gable_roof("North_cross_gable", 817.0, -407.3, 9.5, 12.0, wall_h, 10.1, "x")
gable_roof("South_cross_gable", 816.1, -380.9, 10.0, 9.0, wall_h, 10.2, "x")
# Front-facing projecting gable, modeled as a smaller, taller roof intersecting
# the main wing, matching the prominent central gable in the official gallery.
gable_roof("Front_entry_projecting_gable", 820.7, -395.6, 8.0, 8.5, wall_h, 11.4, "y")

def cube(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Small masonry arris", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return link_object(o)

def window_x(label, x, y, z, outward):
    # Window plane on an X-facing wall. Ivory trim, dark glass, sash muntins.
    depth = 0.20
    cube(label + "_stone_surround", (x, y, z), (depth, 1.30, 1.95), stone, 0.035)
    cube(label + "_cream_frame", (x + outward*0.13, y, z), (0.10, 1.10, 1.72), wood, 0.025)
    cube(label + "_glass", (x + outward*0.19, y, z), (0.045, 0.91, 1.50), glass, 0.01)
    cube(label + "_center_mullion", (x + outward*0.22, y, z), (0.055, 0.065, 1.52), wood)
    cube(label + "_sash_crossbar", (x + outward*0.22, y, z + 0.02), (0.055, 0.92, 0.065), wood)
    cube(label + "_stone_sill", (x + outward*0.16, y, z - 0.98), (0.30, 1.42, 0.12), stone, 0.02)

def window_y(label, x, y, z, outward):
    cube(label + "_stone_surround", (x, y, z), (1.30, 0.20, 1.95), stone, 0.035)
    cube(label + "_cream_frame", (x, y + outward*0.13, z), (1.10, 0.10, 1.72), wood, 0.025)
    cube(label + "_glass", (x, y + outward*0.19, z), (0.91, 0.045, 1.50), glass, 0.01)
    cube(label + "_center_mullion", (x, y + outward*0.22, z), (0.065, 0.055, 1.52), wood)
    cube(label + "_sash_crossbar", (x, y + outward*0.22, z + 0.02), (0.92, 0.055, 0.065), wood)
    cube(label + "_stone_sill", (x, y + outward*0.16, z - 0.98), (1.42, 0.30, 0.12), stone, 0.02)

# Facade layout from official exterior photo: tall pale-trimmed sash windows in
# two storeys, with the source's prominent entrance gable kept unobstructed.
# Placements are approximate: current imagery resolves appearance, not every
# facade's survey coordinates.
for floor, z in enumerate((2.15, 5.05), start=1):
    for idx, y in enumerate((-399.7, -396.4, -393.1, -389.8, -386.5), start=1):
        window_x(f"West_front_F{floor}_W{idx}", 809.2, y, z, -1)
    for idx, y in enumerate((-411.2, -408.0, -404.8, -401.6), start=1):
        window_x(f"East_rear_F{floor}_W{idx}", 822.0, y, z, 1)
    for idx, x in enumerate((810.4, 813.0, 815.6, 818.2, 820.8), start=1):
        window_y(f"North_end_F{floor}_W{idx}", x, -415.2, z, -1)

# Prominent stone entrance surround, modest and portable, based on the official
# facade photo; no access to or reconstruction of unverified interiors.
cube("Entry_portal_stone_jamb_left", (820.5, -396.9, 2.15), (0.36, 0.34, 4.25), stone, 0.06)
cube("Entry_portal_stone_jamb_right", (823.7, -396.9, 2.15), (0.36, 0.34, 4.25), stone, 0.06)
cube("Entry_portal_lintel", (822.1, -396.9, 4.23), (3.55, 0.42, 0.34), stone, 0.06)
cube("Entry_door_dark_wood", (822.1, -397.15, 1.48), (2.65, 0.12, 2.95), wood, 0.04)
cube("Entry_door_glazed_upper", (822.1, -397.24, 2.17), (1.65, 0.06, 1.25), glass, 0.02)
cube("Entry_step_lower", (822.1, -397.28, 0.17), (4.0, 1.1, 0.30), stone, 0.04)

# GIS-derived ground slab is low and unobtrusive, retaining the precise polygon.
slab_v = [(x, y, -0.12) for x, y in ring] + [(x, y, 0.0) for x, y in ring]
slab_f = [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)] + [tuple(range(n))]
foundation = mesh_obj("GIS_FID826_foundation_cap", slab_v, slab_f, stone)

for obj in collection.objects:
    obj["source_building"] = "Beta Theta Pi, Purdue Beta Mu Chapter"
    obj["source_gis_fid"] = 826
    obj["coordinate_system"] = "Campus local XY: X east, Y north, Z up; approximate geographic transform"
    obj["campus_origin_lat_lon"] = [ORIGIN_LAT, ORIGIN_LON]
    obj["footprint_source"] = "Purdue University BuildingShapesZip4 FeatureServer layer 0, FID 826"

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.world.color = (0.055, 0.065, 0.08)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "audit" / "beta_theta_pi" / "beta_theta_pi_preview.png")

# An isolated presentation camera/light rig is omitted to keep this as a clean
# importable building asset; consumer scenes supply their own lighting/camera.
scene.collection.objects.link(bpy.data.objects.new("Asset_Origin_GIS_FID826", None))
origin = scene.collection.objects["Asset_Origin_GIS_FID826"]
origin.location = (0, 0, 0)
origin.empty_display_type = "PLAIN_AXES"
origin.empty_display_size = 2.0
origin.hide_render = True
origin["role"] = "campus transform origin; geometry remains in the project's campus coordinates"

# Set a useful default view in the saved file without adding a camera.
for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_distance = 70
        area.spaces.active.region_3d.view_location = (817, -396, 4)
        area.spaces.active.region_3d.view_rotation = (0.89, 0.36, 0.16, 0.22)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print("SAVED", OUT)
print("SCENE", scene.name, "COLLECTION", collection.name, "OBJECTS", len(collection.objects))
