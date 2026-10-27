"""Build the campus-coordinate Beta Theta Pi massing asset from Purdue GIS FID 826.

Run with Blender 5.x background Python. No external asset dependencies are used.
The GIS ring is the precise base footprint; facade placement and height are
photographic interpretations recorded in audit/beta_theta_pi/evidence.json.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
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
# ArcGIS rings are explicitly closed. Keep the unique perimeter vertices so
# shell caps never contain a zero-area face at the repeated closing point.
if len(ring) > 1 and math.dist(ring[0], ring[-1]) < 1e-5:
    ring.pop()
assert len(ring) == len(set((round(x, 6), round(y, 6)) for x, y in ring))

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
roof = mat_brick("Beta Theta Pi | charcoal slate roof", (0.012, 0.016, 0.021), (0.055, 0.065, 0.072), 52.0)
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
gold = bpy.data.materials.new("Beta Theta Pi | aged brass crest details")
gold.diffuse_color = (0.62, 0.36, 0.08, 1)
gold.use_nodes = True
gold.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.62, 0.36, 0.08, 1)
gold.node_tree.nodes.get("Principled BSDF").inputs["Metallic"].default_value = 0.58
gold.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.34

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
wall_h = 9.3  # three above-grade levels; official housing record lists 4 incl. basement
verts = [(x, y, z) for z in (0.0, wall_h) for x, y in ring]
n = len(ring)
faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
faces.append(tuple(range(2 * n - 1, n - 1, -1)))
mesh_obj("BetaThetaPi_GIS_826_exact_perimeter_walls", verts, faces, brick)

# Build a single watertight roof shell from the exact concave GIS footprint.
# Tessellate the polygon as one constrained top surface, then add the eaves and
# underside. This avoids the self-crossing gable caps caused by changing GIS
# cross-section topology at concave vertices. The shallow east-west ridge and
# pitch are photo-derived approximations; the perimeter remains GIS-exact.
def roof_shell():
    center_x = (min(x for x, _ in ring) + max(x for x, _ in ring)) * 0.5
    half_width = max(abs(x - center_x) for x, _ in ring)
    rise = 2.3
    top = []
    for x, y in ring:
        # A continuous shallow gable height field, clipped exactly to the GIS
        # outline. The ridge runs north-south through the footprint center.
        z = wall_h + rise * (1.0 - abs(x - center_x) / half_width)
        top.append((x, y, z))
    polygon_2d = [Vector((x, y, 0.0)) for x, y in ring]
    triangles = tessellate_polygon([polygon_2d])
    if not triangles:
        raise RuntimeError("Could not tessellate GIS footprint for roof")
    roof_faces = []
    for tri in triangles:
        ids = tuple(int(i) for i in tri)
        a, b, c = (top[i] for i in ids)
        nz = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
        roof_faces.append(ids if nz > 0 else tuple(reversed(ids)))
    n = len(ring)
    vertices = top + [(x, y, wall_h) for x, y in ring]
    faces = list(roof_faces)
    faces.extend((i, (i+1) % n, (i+1) % n + n, i+n) for i in range(n))
    faces.append(tuple(range(2*n-1, n-1, -1)))
    mesh = bpy.data.meshes.new("GIS_FID826_Continuous_Closed_RoofShell_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(roof)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    boundary_edges = sum(e.is_boundary for e in bm.edges)
    nonmanifold_edges = sum(not e.is_manifold for e in bm.edges)
    zero_area = sum(f.calc_area() < 1e-8 for f in bm.faces)
    upward_faces = sum(f.normal.z > 0.05 for f in bm.faces if f.normal.z > -0.05)
    if boundary_edges or nonmanifold_edges or zero_area:
        bm.free()
        raise RuntimeError(f"Roof shell is not closed: boundary={boundary_edges}, nonmanifold={nonmanifold_edges}, zero_area={zero_area}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new("GIS_FID826_Continuous_Closed_RoofShell", mesh)
    collection.objects.link(obj)
    print("ROOF_SHELL", json.dumps({"vertices": len(mesh.vertices), "faces": len(mesh.polygons),
          "boundary_edges": boundary_edges, "nonmanifold_edges": nonmanifold_edges,
          "zero_area_faces": zero_area, "upward_normals": sum(p.normal.z > 0 for p in mesh.polygons)}))

roof_shell()

"""Legacy parametric helper retained as a recipe for other assets, but the
Beta house now uses GIS-clipped roof bands above."""
def gable_roof(name, cx, cy, width, length, eave_z, ridge_z, axis="y"):
    if axis == "y":
        pts = [(-width/2, -length/2, eave_z), (width/2, -length/2, eave_z),
               (width/2, length/2, eave_z), (-width/2, length/2, eave_z),
               (0, -length/2, ridge_z), (0, length/2, ridge_z)]
        xy = lambda p: (cx + p[0], cy + p[1], p[2])
        faces = [(0, 4, 5, 3), (4, 1, 2, 5), (0, 1, 4), (3, 5, 2)]
    else:
        pts = [(-length/2, -width/2, eave_z), (length/2, -width/2, eave_z),
               (length/2, width/2, eave_z), (-length/2, width/2, eave_z),
               (-length/2, 0, ridge_z), (length/2, 0, ridge_z)]
        xy = lambda p: (cx + p[0], cy + p[1], p[2])
        faces = [(0, 1, 5, 4), (4, 5, 2, 3), (0, 3, 4), (1, 5, 2)]
    return mesh_obj(name, [xy(p) for p in pts], faces, roof)

# Distinct roof modules, adjoining along Y bands without overlapping slabs.
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

def x_boundaries_at_y(y):
    xs = []
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if min(y1, y2) - 1e-5 <= y <= max(y1, y2) + 1e-5 and abs(y2-y1) > 1e-6:
            t = (y-y1)/(y2-y1)
            if -1e-5 <= t <= 1+1e-5:
                xs.append(x1 + t*(x2-x1))
    return min(xs), max(xs)

def arched_window_x(label, x, y, zbottom, width=1.42, height=2.36):
    """Pale stone arched surround and divided glazing on the west/front plane."""
    spring = zbottom + height - width/2
    # Glass polygon with a true semicircular head, in a plane facing west.
    yz = [(-width/2, zbottom), (width/2, zbottom), (width/2, spring)]
    for i in range(1, 13):
        a = math.pi * i / 12
        yz.append((math.cos(a)*width/2, spring + math.sin(a)*width/2))
    verts = [(x-0.205, y+dy, z) for dy,z in yz]
    mesh_obj(label + "_arched_glass", verts, [tuple(range(len(verts)))], glass)
    # Masonry jambs and arch voussoirs outline the opening.
    cube(label+"_left_pier", (x-0.13, y-width/2-0.11, zbottom+height/2), (0.28,0.22,height), stone, 0.025)
    cube(label+"_right_pier", (x-0.13, y+width/2+0.11, zbottom+height/2), (0.28,0.22,height), stone, 0.025)
    for i in range(9):
        a = math.pi*i/8
        yy = y + math.cos(a)*(width/2+0.11)
        zz = spring + math.sin(a)*(width/2+0.11)
        cube(label+f"_arch_stone_{i+1}", (x-0.14,yy,zz), (0.30,0.25,0.23), stone, 0.025)
    cube(label+"_sill", (x-0.18,y,zbottom-0.08), (0.38,width+0.50,0.16), stone, 0.025)
    cube(label+"_central_mullion", (x-0.24,y,zbottom+height*0.48), (0.09,0.08,height*0.86), wood, 0.015)
    for k, frac in enumerate((0.34,0.69), start=1):
        cube(label+f"_transom_{k}", (x-0.24,y,zbottom+height*frac), (0.09,width-0.08,0.07), wood, 0.012)

# The official west-facing elevation has three occupied levels, a projecting
# pale vertical bay, a tall central brick gable, and an arched stone entrance.
# Relative facade placement along the GIS perimeter is approximate; no facade
# bearing or surveyed elevation is published in the available records.
floor_z = (1.75, 4.80, 7.55)
front_rows = (-414.0, -410.2, -407.0, -402.1, -399.0, -394.8, -391.0, -387.2, -383.1)
for floor, z in enumerate(floor_z, start=1):
    for idx, y in enumerate(front_rows, start=1):
        # Reserve tower, bay and portal openings for individually modeled features.
        if -407.0 <= y <= -403.0 or -400.2 <= y <= -396.2 or -393.2 <= y <= -390.0:
            continue
        xfront, _ = x_boundaries_at_y(y)
        window_x(f"West_front_F{floor}_W{idx}", xfront-0.08, y, z, -1)
    for idx, y in enumerate((-412.0,-407.6,-402.9,-398.7,-394.1,-389.3,-384.8,-380.2), start=1):
        _, xback = x_boundaries_at_y(y)
        window_x(f"East_rear_F{floor}_W{idx}", xback+0.06, y, z, 1)

# Distinct pale vertical bay, projecting from the wall. Three arched lights are
# vertically stacked, following official photos 1, 11 and 15.
bay_y = -398.1
bay_wall_x, _ = x_boundaries_at_y(bay_y)
bay_front_x = bay_wall_x - 0.68
cube("Pale_bay_main_panel", (bay_wall_x-0.34,bay_y,5.65), (0.72,3.45,8.10), stone, 0.045)
cube("Pale_bay_left_pilaster", (bay_front_x-0.12,bay_y-1.73,5.66), (0.30,0.28,8.14), stone, 0.035)
cube("Pale_bay_right_pilaster", (bay_front_x-0.12,bay_y+1.73,5.66), (0.30,0.28,8.14), stone, 0.035)
for i,z in enumerate((1.05,4.05,7.05), start=1):
    arched_window_x(f"Pale_bay_level_{i}", bay_front_x, bay_y, z, 1.45, 2.55)
cube("Pale_bay_cornice", (bay_front_x-0.12,bay_y,9.82), (0.42,3.85,0.36), stone, 0.04)

# Central brick tower gable face and its small high sash, matching the official
# front elevation. The wings retain lower, separate slate facets.
tower_y = -391.3
tower_x, _ = x_boundaries_at_y(tower_y)
tower_front = tower_x - 0.15
mesh_obj("Central_tower_front_gable_brick", [(tower_front,tower_y-3.4,wall_h),(tower_front,tower_y+3.4,wall_h),(tower_front,tower_y,15.0)], [(0,1,2)], brick)
window_x("Central_tower_high_sash", tower_front-0.18,tower_y,10.35,-1)

# Two small front-facing gabled dormers sit on the long slate wings, as seen
# in the official chapter-house elevations. They are placed on the west roof
# slope and rise from the local height-field rather than floating above it.
roof_center_x = (min(x for x, _ in ring) + max(x for x, _ in ring)) * 0.5
roof_half_width = max(abs(x-roof_center_x) for x, _ in ring)
def roof_elevation(x):
    return wall_h + 2.3 * (1.0 - abs(x-roof_center_x)/roof_half_width)

for dormer_index, dormer_y in enumerate((-411.8, -380.8), start=1):
    wall_x, _ = x_boundaries_at_y(dormer_y)
    x0 = wall_x + 3.7
    x1 = x0 + 2.0
    z0 = roof_elevation(x0)
    z1 = roof_elevation(x1)
    half_span = 1.02
    peak0, peak1 = z0 + 1.45, z1 + 1.25
    front = [(x0,dormer_y-half_span,z0),(x0,dormer_y+half_span,z0),(x0,dormer_y,peak0)]
    rear = [(x1,dormer_y-half_span,z1),(x1,dormer_y+half_span,z1),(x1,dormer_y,peak1)]
    mesh_obj(f"West_wing_dormer_{dormer_index}_brick_gable", front, [(0,1,2)], brick)
    mesh_obj(f"West_wing_dormer_{dormer_index}_rear_gable", rear, [(0,2,1)], brick)
    mesh_obj(f"West_wing_dormer_{dormer_index}_north_slate", [front[0],front[2],rear[2],rear[0]], [(0,1,2,3)], roof)
    mesh_obj(f"West_wing_dormer_{dormer_index}_south_slate", [front[2],front[1],rear[1],rear[2]], [(0,1,2,3)], roof)
    cube(f"West_wing_dormer_{dormer_index}_cream_frame", (x0-0.06,dormer_y,z0+0.56), (0.07,0.90,0.94), wood, 0.025)
    cube(f"West_wing_dormer_{dormer_index}_sash", (x0-0.13,dormer_y,z0+0.56), (0.06,0.72,0.78), glass, 0.025)

# Arched stone portal with heavy jambs, archivolt, glazed transom and shield.
door_y = -405.2
door_x, _ = x_boundaries_at_y(door_y)
cube("Entry_arch_left_jamb", (door_x-0.16,door_y-1.15,1.75), (0.42,0.32,3.45), stone, 0.04)
cube("Entry_arch_right_jamb", (door_x-0.16,door_y+1.15,1.75), (0.42,0.32,3.45), stone, 0.04)
for i in range(13):
    a = math.pi*i/12
    yy = door_y + math.cos(a)*1.15
    zz = 3.38 + math.sin(a)*1.15
    cube(f"Entry_arch voussoir_{i+1}", (door_x-0.17,yy,zz), (0.44,0.38,0.28), stone, 0.035)
cube("Entry_door_dark_wood", (door_x-0.27,door_y,1.43), (0.16,1.82,2.80), wood, 0.025)
cube("Entry_door_glazed_transom", (door_x-0.36,door_y,2.78), (0.08,1.24,0.55), glass, 0.02)
cube("Entry_door_center_rail", (door_x-0.41,door_y,1.74), (0.06,1.70,0.10), stone, 0.015)
cube("Chapter_shield_plaque", (door_x-0.42,door_y,4.48), (0.12,0.70,0.82), stone, 0.08)
# A small shield relief gives the otherwise plain entry plaque a readable
# chapter-house focal detail. The red shield and brass chevron sit proud of the
# pale plaque and remain portable as ordinary mesh geometry.
shield_x = door_x - 0.50
shield_outline = [(shield_x,door_y-0.34,4.78),(shield_x,door_y+0.34,4.78),
                  (shield_x,door_y+0.34,4.35),(shield_x,door_y,4.03),
                  (shield_x,door_y-0.34,4.35)]
mesh_obj("Beta_Mu_entry_shield", shield_outline, [(0,1,2,3,4)], brick)
crest_x = door_x - 0.54
mesh_obj("Beta_Mu_brass_crest_chevron",
         [(crest_x,door_y-0.24,4.60),(crest_x,door_y,4.37),(crest_x,door_y+0.24,4.60),
          (crest_x,door_y+0.16,4.66),(crest_x,door_y,4.49),(crest_x,door_y-0.16,4.66)],
         [(0,1,2,3,4,5)], gold)
cube("Beta_Mu_brass_crest_bar", (door_x-0.55,door_y,4.69), (0.04,0.40,0.055), gold, 0.012)
cube("Entry_step_lower", (door_x-0.35,door_y,0.17), (1.1,3.0,0.30), stone, 0.04)

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
