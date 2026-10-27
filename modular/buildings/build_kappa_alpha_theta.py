"""Build the Kappa Alpha Theta (FID 786) asset in a local coordinate frame.

Source dimensions and facade interpretation are recorded in
audit/kappa_alpha_theta/evidence.md. The interior geometry is explicitly a
schematic because no floor plan was available.
"""
import bpy
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_house_301840865_cbf7de2.blend"
SCENE_NAME = "Building_massing_house_301840865_cbf7de2"
COLL_NAME = "Asset_massing_house_301840865_cbf7de2"

# Approximate center of the official GIS outline after project local conversion.
# Building geometry is modeled relative to this origin; master placement remains
# coordinator-owned and will need to be moved from the old, incorrect marker.
ORIGIN_XY = (-496.8858331764946, 343.5669554847756)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = SCENE_NAME
asset_coll = bpy.data.collections.new(COLL_NAME)
scene.collection.children.link(asset_coll)

def link_mesh(name, verts, faces, mat, collection=asset_coll):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj

def mat_principled(name, color, roughness=0.75, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    return m

brick = mat_principled("KAT | warm red-brown brick", (0.33, 0.105, 0.067), 0.88)
brick_light = mat_principled("KAT | varied brick courses", (0.40, 0.15, 0.095), 0.9)
trim = mat_principled("KAT | ivory painted trim", (0.88, 0.84, 0.73), 0.55)
stone = mat_principled("KAT | pale limestone", (0.69, 0.63, 0.52), 0.78)
shutter = mat_principled("KAT | charcoal shutters and doors", (0.035, 0.047, 0.052), 0.62)
glass = mat_principled("KAT | blue gray window glass", (0.15, 0.27, 0.32), 0.2, 0.08)
roof = mat_principled("KAT | dark gray standing seam roof", (0.105, 0.12, 0.13), 0.62, 0.15)
concrete = mat_principled("KAT | courtyard and entry concrete", (0.57, 0.55, 0.5), 0.92)
interior = mat_principled("KAT | schematic interior partition", (0.77, 0.72, 0.61), 0.92)
accent = mat_principled("KAT | interior schematic floor bands", (0.42, 0.58, 0.54), 0.85)

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Move object from default collection into the asset collection.
    for c in tuple(obj.users_collection):
        c.objects.unlink(obj)
    asset_coll.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft masonry edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj

def prism(name, x0, x1, y0, y1, z0, z1, mat):
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    return link_mesh(name,v,f,mat)

def gable_roof(name, x0, x1, y0, y1, base, ridge, mat):
    # Ridge runs north-south, so the south street facade presents a gable end
    # as seen in the chapter's official exterior photo.
    xm=(x0+x1)/2
    v=[(x0,y0,base),(x1,y0,base),(x1,y1,base),(x0,y1,base),
       (xm,y0,ridge),(xm,y1,ridge)]
    f=[(0,4,5,3),(4,1,2,5),(0,1,4),(3,5,2),(0,3,2,1)]
    return link_mesh(name,v,f,mat)

# Overall GIS envelope is ~32 x 40 m, but it is a generalized legacy polygon
# with no separate courtyard ring. The photographed house mass is modeled as a
# compact 3-storey south bar with lower two-storey return wings around a court.
# The dimension split remains an estimate, not a measured wall survey.
Z_FLOORS = (0.0, 3.2, 6.4)
H_MAIN = 9.55
H_WING = 6.65
# Main street-facing bar (west-east), aligned to W Stadium Street (south).
prism("House_301840865", -11.5, 11.5, -12.6, -3.1, 0.0, H_MAIN, brick)
# North-south return wings enclose a landscaped internal courtyard.
prism("East_return_wing", 6.8, 11.5, -3.1, 13.8, 0.0, H_WING, brick)
prism("West_return_wing", -11.5, -6.8, -3.1, 13.8, 0.0, H_WING, brick)
# Rear link closes the court partially; the central opening stays clear toward
# the north, matching the open courtyard feel in the chapter's official photo.
prism("North_courtyard_link", -6.8, 6.8, 9.1, 13.8, 0.0, H_WING, brick)

# Roof forms: low dark hipped/flat wings and a modest gabled feature over the
# older main block, visible in official exterior photography.
gable_roof("Main_gabled_roof", -11.8, 11.8, -12.95, -2.75, H_MAIN+0.2, H_MAIN+2.35, roof)
for nm,x0,x1,y0,y1,h in [
    ("East_wing_roof",6.65,11.65,-3.35,14.05,H_WING),
    ("West_wing_roof",-11.65,-6.65,-3.35,14.05,H_WING),
    ("North_link_roof",-6.95,6.95,9.0,14.05,H_WING),
]:
    box(nm,( (x0+x1)/2,(y0+y1)/2,h+0.2),(x1-x0,y1-y0,0.4),roof,0.05)

# Main street facade faces south (-Y), with three stories of white sash windows,
# dark shutters, pale arched lintel panels, and a centered classical porch.
def south_window(prefix, x, z, width=1.35, height=1.72, shutters=True):
    y=-12.69
    box(prefix+"_sash",(x,y,z),(width,0.13,height),trim,0.025)
    box(prefix+"_glass",(x,y-0.075,z),(width-0.20,0.035,height-0.22),glass)
    # six-pane muntins
    box(prefix+"_muntin_v",(x,y-0.105,z),(0.045,0.04,height-0.20),trim)
    for dz in (-0.34,0.34):
        box(prefix+"_muntin_h",(x,y-0.107,z+dz),(width-0.2,0.04,0.035),trim)
    if shutters:
        sw=0.27
        for side in (-1,1):
            sx=x+side*(width/2+sw/2+0.06)
            box(prefix+f"_shutter_{side}",(sx,y-0.01,z),(sw,0.12,height*0.94),shutter,0.025)
            for dz in (-0.32,0.0,0.32):
                box(prefix+f"_slat_{side}_{dz}",(sx,y-0.085,z+dz),(sw*0.72,0.035,0.035),stone)
    # broad pale lintel over the window, a simplified arch-panel cue from photos.
    box(prefix+"_lintel",(x,y-0.03,z+height/2+0.14),(width+0.32,0.17,0.22),stone,0.05)

for floor,z in enumerate((1.95,5.05,8.1),1):
    for x in (-9.0,-5.7,-2.65,2.65,5.7,9.0):
        south_window(f"South_f{floor}_window_{x:+.1f}",x,z,1.2 if abs(x)>7 else 1.45,1.7)

# Chapter letters are visible on the upper brick wall in official chapter
# imagery. Use the Greek initials, but keep them modest and non-emissive.
letter_curve = bpy.data.curves.new("KAT_facade_letters_curve", type='FONT')
letter_curve.body = "ΚΑΘ"
letter_curve.align_x = 'CENTER'
letter_curve.align_y = 'CENTER'
letter_curve.size = 0.82
letter_curve.extrude = 0.025
letter_curve.bevel_depth = 0.008
letter_obj = bpy.data.objects.new("KAT_facade_letters", letter_curve)
asset_coll.objects.link(letter_obj)
letter_obj.location=(0,-12.86,6.92)
letter_obj.rotation_euler=(math.radians(90),0,0)
letter_obj.data.materials.append(shutter)

# Main door and porch portico at center. Main entry is modeled as double doors,
# transom and three round column stand-ins with square bases/capitals.
box("Main_entry_door_pair",(0,-12.78,1.35),(2.3,0.22,2.55),shutter,0.04)
box("Main_entry_door_seam",(0,-12.91,1.37),(0.055,0.035,2.5),stone)
for x in (-0.68,0.68):
    box(f"Door_glazing_{x:+.1f}",(x,-12.93,1.68),(0.38,0.035,1.25),glass)
box("Entry_transom",(0,-12.84,2.83),(2.9,0.18,0.42),trim,0.04)
box("Portico_pediment",(0,-14.0,4.5),(6.0,1.0,0.35),trim,0.05)
box("Portico_entablature",(0,-14.0,4.12),(6.0,0.75,0.35),stone,0.04)
for x in (-2.35,-0.78,0.78,2.35):
    box(f"Portico_column_{x:+.2f}",(x,-14.08,2.72),(0.42,0.42,2.45),trim,0.08)
    box(f"Column_base_{x:+.2f}",(x,-14.08,1.48),(0.64,0.62,0.22),stone,0.035)
    box(f"Column_capital_{x:+.2f}",(x,-14.08,3.98),(0.62,0.62,0.22),stone,0.035)
for i in range(3):
    box(f"Entry_step_{i+1}",(0,-13.2-i*0.42,0.28-i*0.085),(6.2,0.5,0.22),stone,0.04)

# Courtyard-side and side elevations carry matching white-trim sash windows.
def side_window(prefix, x, y, z, width=1.15, height=1.58, facing='east'):
    xx=x+(0.075 if facing=='east' else -0.075)
    box(prefix+"_trim",(xx,y,z),(0.14,width,height),trim,0.025)
    box(prefix+"_glass",(xx+(0.08 if facing=='east' else -0.08),y,z),(0.035,width-0.20,height-0.2),glass)
    box(prefix+"_muntin_h",(xx+(0.11 if facing=='east' else -0.11),y,z),(0.04,width-0.2,0.035),trim)
    for sy in (-1,1):
        box(prefix+f"_shutter_{sy}",(xx,y+sy*(width/2+0.19),z),(0.1,0.26,height*0.9),shutter,0.02)

for side,x,face in (("East",11.5,"east"),("West",-11.5,"west")):
    for floor,z in enumerate((1.9,5.0),1):
        for y in (-0.5,3.0,6.5,10.5):
            side_window(f"{side}_court_f{floor}_{y:+.1f}",x,y,z,1.25,1.55,face)
for x,face in ((-11.5,"west"),(11.5,"east")):
    for floor,z in enumerate((1.9,5.0),1):
        for y in (-8.5,-4.8):
            side_window(f"Outer_side_{x:+.1f}_f{floor}_{y:+.1f}",x,y,z,1.15,1.55,face)

# Visible facade brick pilasters and horizontal limestone belt/cornice courses.
for x in (-11.35,-8.2,0,8.2,11.35):
    box(f"South_pilaster_{x:+.2f}",(x,-12.71,4.75),(0.22,0.18,9.3),brick_light,0.025)
for z in (3.2,6.4,9.5):
    box(f"South_belt_course_{z:.1f}",(0,-12.73,z),(22.8,0.20,0.18),stone,0.025)

# Courtyard: quiet concrete floor, planting islands, paths and light site fixtures.
box("Courtyard_paved_walk",(0,3.25,0.07),(11.8,11.5,0.14),concrete,0.08)
for x in (-2.8,2.8):
    box(f"Courtyard_planter_{x:+.1f}",(x,3.3,0.28),(2.35,2.35,0.42),stone,0.08)
    # low stylized shrub canopies, kept as schematic site detail
    for dx,dy,r in ((0,0,0.72),(-0.55,0.15,0.48),(0.52,-0.2,0.52)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=(x+dx,3.3+dy,1.05))
        o=bpy.context.object; o.name=f"Courtyard_shrub_{x:+.1f}_{dx:+.1f}_{dy:+.1f}"
        for c in tuple(o.users_collection): c.objects.unlink(o)
        asset_coll.objects.link(o)
        o.data.materials.append(mat_principled("KAT | courtyard evergreen foliage",(0.12,0.22,0.14),0.9))

# Small brick chimney at the gabled end and simple white ridge/soffit cues.
box("Gable_chimney",(-7.8,-9.2,12.25),(1.2,1.2,3.0),brick,0.04)
box("Chimney_cap",(-7.8,-9.2,13.8),(1.42,1.42,0.20),stone,0.025)

# Clearly labeled schematic plan geometry. No plan source was available: these
# bands and partitions communicate floors and circulation only, never exact use.
for level,z in enumerate((3.18,6.38),1):
    box(f"SCHEMATIC_ONLY_floor_plate_level_{level}",(0,-7.8,z),(20.4,8.8,0.10),interior)
    if level == 1:
        # Low interior layout cues stay inside the south bar; they do not claim
        # room sizes or functions and cannot protrude through the courtyard roof.
        box("SCHEMATIC_ONLY_corridor_level_1",(0,-7.75,z+0.11),(2.0,8.1,0.10),interior)
        for y in (-10.3,-7.8,-5.3):
            box(f"SCHEMATIC_ONLY_room_divider_level_1_{y:+.1f}",(0,y,z+0.48),(18.0,0.10,0.75),interior)
        for x in (-4.5,4.5):
            box(f"SCHEMATIC_ONLY_cross_partition_level_1_{x:+.1f}",(x,-7.75,z+0.48),(0.10,4.6,0.75),interior)

# No geospatial translation is baked into local geometry. The master collection
# instance should be positioned by the official FID centroid computed below.
# The linked wings are brought closer to the current GIS envelope while leaving
# wall heights unchanged. This is a plan-size estimate because the GIS shape is
# a generalized outline and no as-built dimension sheet was found.
PLAN_SCALE = 1.18
for obj in asset_coll.objects:
    obj.location.x *= PLAN_SCALE
    obj.location.y *= PLAN_SCALE
    if obj.type == 'MESH':
        for vertex in obj.data.vertices:
            vertex.co.x *= PLAN_SCALE
            vertex.co.y *= PLAN_SCALE

scene.unit_settings.system = 'METRIC'
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new("KAT asset world")
scene.world.color = (0.45,0.45,0.45)
scene.camera = None
scene['asset_id'] = "massing_house_301840865_cbf7de2"
scene['building'] = "Kappa Alpha Theta (Purdue Alpha Chi), FID 786"
scene['geometry_origin'] = "Local 0,0,0; GIS polygon centroid anchor (-496.8858331765, 343.5669554848) m"
scene['interior_disclaimer'] = "SCHEMATIC_ONLY geometry: no verified floor plan was available"

# Set asset collection origin naturally at 0,0,0; geometry spans approximately
# 23m x 27m plus porch and is designed to be instanced at the GIS anchor.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print(f"SAVED {ASSET}")
print(f"OBJECTS {len(asset_coll.objects)}")
print(f"ANCHOR {ORIGIN_XY}")
