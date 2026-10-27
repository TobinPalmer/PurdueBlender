"""Build a source-backed Chauncey Cooperative House library.

The exact foundation wall ring comes from Purdue GIS FID 805. The official
house website supplies the architectural reference photo. Heights, roof
proportions, facade repetitions, and the interior layout are estimates because
no survey or registered plan was found. Run with Blender 5.2+:
    blender -b --python build_chauncey_cooperative_fid805.py
"""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "chauncey"
GIS_PATH = AUDIT / "sources" / "purdue_fid805.geojson"
OUT = ROOT / "modular" / "buildings" / "massing_chauncey_cooperative_fid805.blend"
ASSET_ID = "massing_chauncey_cooperative_fid805"
ASSET_COLLECTION = "Asset_" + ASSET_ID
SCENE_NAME = "Building_" + ASSET_ID
LAT0, LON0 = 40.4274, -86.9137

feature = json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
assert feature["id"] == 805
props = feature["properties"]
assert props["BUILDING_N"] == "Chauncey" and props["ADDRESS"] == "215 S Chauncey"
ring_ll = feature["geometry"]["coordinates"][0][:-1]
ring_world = [((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
               (lat - LAT0) * 111040.0) for lon, lat in ring_ll]

# Signed polygon centroid in the same approximate metric conversion used by
# this project. Local geometry is centered on this origin for marker placement.
cross = [ring_world[i][0] * ring_world[(i + 1) % len(ring_world)][1] -
         ring_world[(i + 1) % len(ring_world)][0] * ring_world[i][1]
         for i in range(len(ring_world))]
area2 = sum(cross)
cx = sum((ring_world[i][0] + ring_world[(i + 1) % len(ring_world)][0]) * cross[i]
         for i in range(len(ring_world))) / (3.0 * area2)
cy = sum((ring_world[i][1] + ring_world[(i + 1) % len(ring_world)][1]) * cross[i]
         for i in range(len(ring_world))) / (3.0 * area2)
footprint = [(x - cx, y - cy) for x, y in ring_world]
xmin = min(x for x, _ in footprint)
xmax = max(x for x, _ in footprint)
ymin = min(y for _, y in footprint)
ymax = max(y for _, y in footprint)
ycenter = (ymin + ymax) * 0.5

# Clear only the standalone output scene, then create the one export collection.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
    if coll != bpy.context.scene.collection:
        bpy.data.collections.remove(coll)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset = bpy.data.collections.new(ASSET_COLLECTION)
scene.collection.children.link(asset)


def material(name, base, roughness=0.8, metallic=0.0, noise_scale=None, noise_strength=0.15):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if noise_scale:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise_scale
        tex.inputs["Detail"].default_value = 3.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.24
        ramp.color_ramp.elements[1].position = 0.78
        c0 = tuple(max(0.0, c * (1.0 - noise_strength)) for c in base) + (1.0,)
        c1 = tuple(min(1.0, c * (1.0 + noise_strength)) for c in base) + (1.0,)
        ramp.color_ramp.elements[0].color = c0
        ramp.color_ramp.elements[1].color = c1
        links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    if name == "Painted ivory clapboard":
        wave = mat.node_tree.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "Z"
        wave.inputs["Scale"].default_value = 38.0
        wave.inputs["Distortion"].default_value = 0.15
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.10
        bump.inputs["Distance"].default_value = 0.018
        mat.node_tree.links.new(wave.outputs["Color"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


MAT = {
    "siding": material("Painted ivory clapboard", (0.83, 0.81, 0.74), noise_scale=3.5, noise_strength=0.07),
    "foundation": material("Weathered gray fieldstone", (0.34, 0.35, 0.33), noise_scale=18.0, noise_strength=0.33),
    "roof": material("Dark charcoal asphalt shingles", (0.105, 0.12, 0.14), roughness=0.94, noise_scale=34.0, noise_strength=0.35),
    "trim": material("Warm white painted wood trim", (0.93, 0.91, 0.85), noise_scale=4.0, noise_strength=0.025),
    "shutter": material("Black painted shutters", (0.045, 0.055, 0.065), roughness=0.76),
    "glass": material("Deep blue gray window glass", (0.085, 0.13, 0.16), roughness=0.22, metallic=0.18),
    "door": material("Stained dark mahogany entry door", (0.17, 0.078, 0.036), roughness=0.48, noise_scale=6.0, noise_strength=0.15),
    "wood": material("Painted porch wood", (0.78, 0.77, 0.71), noise_scale=6.0, noise_strength=0.08),
    "concrete": material("Entry concrete", (0.48, 0.48, 0.44), noise_scale=12.0, noise_strength=0.12),
    "interior_wall": material("Schematic interior partitions", (0.67, 0.62, 0.52), noise_scale=4.0, noise_strength=0.04),
    "floor": material("Interior wood floors", (0.32, 0.20, 0.12), noise_scale=8.0, noise_strength=0.12),
    "furniture": material("Interior furniture", (0.26, 0.15, 0.09), roughness=0.75),
    "lawn": material("Yard and planting", (0.16, 0.29, 0.12), noise_scale=7.0, noise_strength=0.26),
    "sign": material("Chauncey sign enamel", (0.35, 0.055, 0.035), roughness=0.66),
}


def link_obj(obj, mat=None):
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    asset.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj


def box(name, center, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_obj(obj, mat)
    if bevel:
        mod = obj.modifiers.new("Soft carpentry edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def mesh_object(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    asset.objects.link(obj)
    return obj


def prism(name, points, z0, z1, mat):
    n = len(points)
    verts = [(x, y, z0) for x, y in points] + [(x, y, z1) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n + n, i+n) for i in range(n)]
    return mesh_object(name, verts, faces, mat)


def oriented_box(name, center, length, thickness, height, angle, mat, bevel=0.0):
    obj = box(name, center, (length, thickness, height), mat, bevel)
    obj.rotation_euler[2] = angle
    return obj


def add_front_window(y, z, w=1.35, h=1.55, shutters=False, name="Front window"):
    # West/front wall is x=xmin. Window plane is in Y/Z.
    x = xmin - 0.09
    box(name + " glass", (x, y, z), (0.07, w, h), MAT["glass"], 0.025)
    t = 0.105
    for dy in (-w/2-t/2, w/2+t/2):
        box(name + " jamb", (x-0.015, y+dy, z), (0.12, t, h+0.19), MAT["trim"], 0.018)
    for dz in (-h/2-t/2, h/2+t/2):
        box(name + " rail", (x-0.018, y, z+dz), (0.13, w+0.19, t), MAT["trim"], 0.018)
    box(name + " center mullion", (x-0.065, y, z), (0.04, 0.055, h), MAT["trim"])
    box(name + " sash", (x-0.065, y, z), (0.04, w, 0.055), MAT["trim"])
    if shutters:
        for sy in (-1, 1):
            box(name + " shutter", (x-0.035, y+sy*(w/2+0.22), z), (0.10, 0.30, h*0.88), MAT["shutter"], 0.025)


def add_side_window(x, y, z, width=1.25, height=1.45, south=True, name="Side window"):
    # North/south wall plane; width extends along X.
    yy = ymin - 0.08 if south else ymax + 0.08
    box(name + " glass", (x, yy, z), (width, 0.065, height), MAT["glass"], 0.025)
    t = 0.10
    for dx in (-width/2-t/2, width/2+t/2):
        box(name + " jamb", (x+dx, yy, z), (t, 0.12, height+0.18), MAT["trim"], 0.015)
    for dz in (-height/2-t/2, height/2+t/2):
        box(name + " rail", (x, yy, z+dz), (width+0.18, 0.12, t), MAT["trim"], 0.015)
    box(name + " center mullion", (x, yy-0.05 if south else yy+0.05, z), (0.045, 0.04, height), MAT["trim"])
    box(name + " sash", (x, yy-0.05 if south else yy+0.05, z), (width, 0.04, 0.045), MAT["trim"])


# Exact GIS structural wall ring; distinct stone base and painted upper walls.
prism("Stone foundation on official FID 805 wall ring", footprint, 0.0, 1.0, MAT["foundation"])
prism("Clapboard exterior on official FID 805 wall ring", footprint, 1.0, 7.1, MAT["siding"])

# Gable ends: main ridge runs approximately east-west; front faces west toward
# South Chauncey Avenue. The estimated roof envelope covers the irregular GIS shell.
roof_overhang = 0.65
xl, xr = xmin-roof_overhang, xmax+roof_overhang
yn, ys = ymin-roof_overhang, ymax+roof_overhang
ridge_z = 13.3
eave_z = 7.0
ym = (yn + ys) / 2
mesh_object("West front gable", [(xmin-0.03, yn+0.45, 7.08), (xmin-0.03, ys-0.45, 7.08), (xmin-0.03, ym, ridge_z-0.05)], [(2,1,0)], MAT["siding"])
mesh_object("East rear gable", [(xmax+0.03, ys-0.45, 7.08), (xmax+0.03, yn+0.45, 7.08), (xmax+0.03, ym, ridge_z-0.05)], [(2,1,0)], MAT["siding"])

def roof_slab(name, yedge, ysign):
    # Sloped roof surface is a 3D quad extruded normal to the slope.
    a = (xl, yedge, eave_z)
    b = (xr, yedge, eave_z)
    c = (xr, ym, ridge_z)
    d = (xl, ym, ridge_z)
    # Slight thickness offset follows the roof slope, not world Z.
    normal = Vector((0.0, -ysign*0.63, 0.78)).normalized() * 0.20
    verts = [a, b, c, d] + [tuple(Vector(v)-normal) for v in (a,b,c,d)]
    faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    mesh_object(name, verts, faces, MAT["roof"])

roof_slab("North roof plane", ys, 1)
roof_slab("South roof plane", yn, -1)
box("Continuous roof ridge cap", ((xl+xr)/2, ym, ridge_z+0.04), (xr-xl+0.18, 0.22, 0.20), MAT["roof"], 0.06)
# Painted bargeboards frame the two visible gable roof edges.
def rake_board(name, x, y0, z0, y1, z1):
    length = math.hypot(y1-y0, z1-z0)
    obj = box(name, (x,(y0+y1)/2,(z0+z1)/2), (0.18,length,0.20), MAT["trim"],0.025)
    obj.rotation_euler[0] = math.atan2(z1-z0,y1-y0)
for x,side in ((xmin-0.72,"West/front"),(xmax+0.72,"East/rear")):
    rake_board(side+" gable rake south",x,yn, eave_z,ym,ridge_z)
    rake_board(side+" gable rake north",x,ym,ridge_z,ys,eave_z)
# Light painted fascia boards finish both eaves and gable rake edges.
for side, y in (("south",yn),("north",ys)):
    box(f"{side.title()} eave fascia", ((xl+xr)/2,y,eave_z-0.04),(xr-xl,0.18,0.24),MAT["trim"],0.025)

# Small gable vent at the attic center, with wood louver lines.
front_x = xmin - 0.12
vent_y = ym
box("Attic louver dark inset", (front_x, vent_y, 10.65), (0.06, 0.76, 0.56), MAT["shutter"], 0.05)
for z in (10.48, 10.60, 10.72, 10.84):
    box("Attic louver", (front_x-0.05, vent_y, z), (0.05, 0.68, 0.035), MAT["trim"])

# Main front fenestration and second-story shutters, based on the official photo.
add_front_window(ym-2.2, 5.35, 1.45, 1.62, True, "Upper front left window")
add_front_window(ym+2.2, 5.35, 1.45, 1.62, True, "Upper front right window")
# First-floor entrance is set behind a deep wrap porch; two window groups flank it.
door_y = ym - 0.35
box("Front entry door", (front_x-0.05, door_y, 2.35), (0.16, 1.1, 2.45), MAT["door"], 0.04)
box("Door glazed upper panel", (front_x-0.14, door_y, 2.75), (0.03, 0.46, 0.72), MAT["glass"], 0.025)
box("Door stoop threshold", (front_x-0.35, door_y, 1.13), (0.70, 1.55, 0.16), MAT["concrete"], 0.05)
box("Door knob", (front_x-0.17, door_y-0.37, 2.25), (0.07, 0.07, 0.07), MAT["trim"], 0.03)
add_front_window(ym-4.7, 2.8, 1.25, 1.5, False, "Front lower window west")
add_front_window(ym+4.0, 2.8, 1.25, 1.5, False, "Front lower window east")

# Repeated, plausible side and rear windows; storey and rhythm reflect the
# archival image while exact openings remain unverified.
interior_xs = [xmin+3.1, xmin+6.4, xmin+9.7, xmin+13.0, xmax-3.0]
for i, x in enumerate(interior_xs):
    add_side_window(x, 0.0, 2.75, 1.32, 1.52, True, f"South ground window {i+1}")
    add_side_window(x, 0.0, 5.35, 1.32, 1.52, True, f"South upper window {i+1}")
    add_side_window(x, 0.0, 2.75, 1.32, 1.52, False, f"North ground window {i+1}")
    add_side_window(x, 0.0, 5.35, 1.32, 1.52, False, f"North upper window {i+1}")

# Porch, columns, balustrades, rails, steps. The source image shows the porch on
# the western/front elevation; its exact limits and height are approximated.
porch_y0, porch_y1 = ymin+1.7, ymax-1.4
porch_x0, porch_x1 = xmin-3.65, xmin+0.6
box("Full front porch deck", ((porch_x0+porch_x1)/2, (porch_y0+porch_y1)/2, 1.17),
    (porch_x1-porch_x0, porch_y1-porch_y0, 0.30), MAT["wood"], 0.06)
column_x = porch_x0 + 0.35
for i in range(6):
    y = porch_y0 + 0.35 + i*(porch_y1-porch_y0-0.7)/5
    box(f"Porch post {i+1}", (column_x, y, 2.55), (0.22, 0.22, 2.8), MAT["trim"], 0.035)
    box(f"Porch post foot {i+1}", (column_x, y, 1.28), (0.33, 0.33, 0.20), MAT["wood"], 0.035)
# Canopy is a lean-to, just below the upper-storey windows.
roof_verts = [(porch_x0-0.32, porch_y0-0.25, 3.95), (porch_x0-0.32, porch_y1+0.25, 3.95),
              (porch_x1+0.12, porch_y1+0.25, 4.35), (porch_x1+0.12, porch_y0-0.25, 4.35),
              (porch_x0-0.32, porch_y0-0.25, 3.78), (porch_x0-0.32, porch_y1+0.25, 3.78),
              (porch_x1+0.12, porch_y1+0.25, 4.18), (porch_x1+0.12, porch_y0-0.25, 4.18)]
mesh_object("Front porch shed canopy", roof_verts, [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], MAT["roof"])
box("Porch front handrail top", (column_x+0.4, (porch_y0+porch_y1)/2, 2.05), (0.14, porch_y1-porch_y0-0.45, 0.14), MAT["trim"], 0.04)
box("Porch front handrail bottom", (column_x+0.4, (porch_y0+porch_y1)/2, 1.47), (0.10, porch_y1-porch_y0-0.45, 0.10), MAT["trim"], 0.03)
for i in range(14):
    y=porch_y0+0.45+i*(porch_y1-porch_y0-0.9)/13
    box(f"Porch baluster {i+1}", (column_x+0.4,y,1.76), (0.07,0.07,0.55), MAT["trim"],0.02)
stairs_y=door_y
for i in range(4):
    step_x=porch_x0-0.35-i*0.34
    step_z=1.10-i*0.23
    box(f"Front entry stair {i+1}", (step_x, stairs_y, step_z), (0.58,1.55,0.22), MAT["concrete"],0.045)

# Front-yard co-op identification sign visible in the official photo.
sign_x = xmin - 5.3
box("Chauncey sign post", (sign_x, ym+4.9, 1.0), (0.16,0.16,1.75), MAT["wood"],0.025)
box("Chauncey co-op sign board", (sign_x-0.05, ym+4.9, 1.85), (0.13,1.65,0.92), MAT["sign"],0.07)
box("Sign inset face", (sign_x-0.13, ym+4.9, 1.86), (0.025,1.42,0.69), MAT["trim"],0.025)
# Small raised lettering blocks communicate the identity without embedding a font dependency.
for i, length in enumerate((0.68,0.94,0.52)):
    box(f"Sign lettering bar {i+1}", (sign_x-0.15, ym+4.9, 2.06-i*0.19), (0.035,length,0.045), MAT["sign"],0.008)

# Schematic interior: continuous floor plates and simple room partitions/furnishings.
# These are explicitly illustrative and are not represented as plan-verified.
# Inset the plates inside the exterior shell so their finish does not leak through
# the wall outline at the story bands.
interior_footprint = [(x*0.94,y*0.94) for x,y in footprint]
prism("Schematic first-floor plate", interior_footprint, 1.04, 1.20, MAT["floor"])
prism("Schematic second-floor plate", interior_footprint, 4.12, 4.28, MAT["floor"])
for zbase in (1.20,4.28):
    wall_z=zbase+1.35
    # Partial partitions make the room divisions legible through window glazing.
    # Keep this partition inside the actual concave footprint rather than the
    # larger roof envelope; the south-west corner is recessed in FID 805.
    box("Schematic partition east-west A", (2.0, ymin+4.8, wall_z), (14.0,0.12,2.7), MAT["interior_wall"])
    box("Schematic partition north-south B", (xmin+7.4, 0.9, wall_z), (0.12,ymax-ymin-4.0,2.7), MAT["interior_wall"])
    box("Schematic partition north-south C", (xmax-6.2,-0.7,wall_z), (0.12,ymax-ymin-3.5,2.7), MAT["interior_wall"])
# Shared-meal kitchen and dining cues, plus common room seating.
box("Schematic kitchen counter", (xmin+13.0, ymin+2.4, 2.05), (4.2,0.72,1.7), MAT["furniture"],0.08)
box("Schematic dining table", (xmin+12.0, ycenter-0.2, 1.72), (3.8,1.35,0.12), MAT["furniture"],0.08)
for i in range(6):
    x=xmin+10.6+(i%3)*1.35
    y=ycenter-1.3+(i//3)*2.2
    box(f"Schematic dining chair {i+1}",(x,y,1.23),(0.48,0.48,0.86),MAT["furniture"],0.04)
box("Schematic common-room sofa", (xmin+5.0,ymax-3.4,1.75),(2.7,0.9,0.85),MAT["furniture"],0.10)
box("Schematic common-room table", (xmin+8.0,ymax-3.0,1.48),(1.3,0.8,0.18),MAT["furniture"],0.04)
for i in range(8):
    x=xmin+3.0+(i%4)*4.3
    y=ymin+2.5+(i//4)*8.0
    box(f"Schematic upper-floor bed {i+1}",(x,y,4.65),(2.0,0.95,0.52),MAT["furniture"],0.06)

# Asset metadata allows an integrator to audit coordinates without editing shared files.
for key, value in {
    "asset_id": ASSET_ID,
    "source_feature_id": 805,
    "source_name": "Chauncey Cooperative House",
    "source_address": "215 S Chauncey Ave, West Lafayette, IN 47906",
    "origin_latitude": LAT0,
    "origin_longitude": LON0,
    "origin_campus_x_m": cx,
    "origin_campus_y_m": cy,
    "geometry_frame": "local meters centered on official Purdue GIS FID 805 footprint centroid",
    "height_status": "estimated from archived official house photo; not surveyed",
    "interior_status": "schematic only; no registered floor plans located",
}.items():
    asset[key] = value

# Studio camera, lights and ground are kept out of the exported building collection.
ground_mat = material("Preview neutral ground", (0.24,0.27,0.23), roughness=0.92)
bpy.ops.mesh.primitive_plane_add(size=90, location=(0,0,-0.18))
ground=bpy.context.object
ground.name="Preview Ground (not in exported asset)"
ground.data.materials.append(ground_mat)
for c in list(ground.users_collection): c.objects.unlink(ground)
scene.collection.objects.link(ground)

def aim(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

bpy.ops.object.camera_add(location=(-40,-25,24))
camera=bpy.context.object
camera.name="Preview Camera"
camera.data.lens=42
aim(camera,(-1.8,0,5.6))
scene.camera=camera
for name, loc, energy, size in (
    ("Large softbox",(-16,-20,28),8500,14),
    ("Porch fill",(-8,10,16),4200,10),
    ("Roof rim",(16,5,23),5200,12),
):
    bpy.ops.object.light_add(type="AREA", location=loc)
    light=bpy.context.object
    light.name=name
    light.data.energy=energy
    light.data.shape="DISK"
    light.data.size=size
    aim(light,(0,0,4))
sun_data=bpy.data.lights.new("Daylight Sun","SUN")
sun_data.energy=2.2
sun_data.angle=math.radians(9)
sun=bpy.data.objects.new("Daylight Sun",sun_data)
scene.collection.objects.link(sun)
sun.location=(-20,-30,34)
aim(sun,(0,0,0))
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1200
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(AUDIT/"chauncey_preview.png")
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(0.34,0.39,0.46,1.0)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=0.45
scene.view_settings.view_transform="AgX"
scene.render.image_settings.color_mode="RGBA"
scene.camera.data.dof.use_dof=False

# Set scene to a useful camera view and save a portable source library.
OUT.parent.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print(json.dumps({
    "asset": str(OUT), "collection": ASSET_COLLECTION,
    "feature": 805, "origin_xy": [round(cx, 6), round(cy, 6)],
    "wall_footprint_bounds_local": [[round(xmin,3),round(xmax,3)],[round(ymin,3),round(ymax,3)]],
    "exported_collection_bounds_local": [
        [round(min((obj.matrix_world @ Vector(corner))[axis] for obj in asset.objects for corner in obj.bound_box),3),
         round(max((obj.matrix_world @ Vector(corner))[axis] for obj in asset.objects for corner in obj.bound_box),3)]
        for axis in range(3)
    ],
    "object_count": len(asset.objects), "materials": len(MAT),
}, indent=2))
