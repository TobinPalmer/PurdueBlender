import bpy
import math
from mathutils import Vector, Euler

print("--- Executing PMU Full Refinement & Photorealistic Pass (Attempt 3) ---")

# Collections
col_exterior = bpy.data.collections.get("45_Purdue_Memorial_Union_Exterior")
col_interiors = bpy.data.collections.get("46_Purdue_Memorial_Union_Interiors")
col_site = bpy.data.collections.get("47_Purdue_Memorial_Union_Plaza_and_Site")
col_cams = bpy.data.collections.get("00_Inspection_Cameras")

# Helper mesh builder
def create_box(name, x_min, x_max, y_min, y_max, z_min, z_max, mat, collection):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    verts = [
        (x_min, y_min, z_min), (x_max, y_min, z_min), (x_max, y_max, z_min), (x_min, y_max, z_min),
        (x_min, y_min, z_max), (x_max, y_min, z_max), (x_max, y_max, z_max), (x_min, y_max, z_max)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2),
        (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_gable_roof(name, x_min, x_max, y_min, y_max, z_base, z_ridge, mat, collection, axis='Y'):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    mesh = bpy.data.meshes.new(name + "_mesh")
    if axis == 'Y':
        x_mid = (x_min + x_max) / 2.0
        verts = [
            (x_min, y_min, z_base), (x_max, y_min, z_base), (x_max, y_max, z_base), (x_min, y_max, z_base),
            (x_mid, y_min, z_ridge), (x_mid, y_max, z_ridge)
        ]
        faces = [
            (0, 1, 2, 3), (0, 4, 1), (3, 2, 5), (0, 3, 5, 4), (1, 4, 5, 2)
        ]
    else:
        y_mid = (y_min + y_max) / 2.0
        verts = [
            (x_min, y_min, z_base), (x_max, y_min, z_base), (x_max, y_max, z_base), (x_min, y_max, z_base),
            (x_min, y_mid, z_ridge), (x_max, y_mid, z_ridge)
        ]
        faces = [
            (0, 1, 2, 3), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1), (3, 2, 5, 4)
        ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_cylinder(name, x, y, z_min, z_max, radius, segments, mat, collection):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    verts = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        verts.append((x + radius * math.cos(a), y + radius * math.sin(a), z_min))
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        verts.append((x + radius * math.cos(a), y + radius * math.sin(a), z_max))
    faces = [[i for i in range(segments)], [segments + i for i in reversed(range(segments))]]
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, next_i, segments + next_i, segments + i))
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_3d_text(name, text, loc, rot, size, mat, collection, extrude=0.03):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    curve_data = bpy.data.curves.new(name=name, type='FONT')
    curve_data.body = text
    curve_data.size = size
    curve_data.extrude = extrude
    curve_data.align_x = 'CENTER'
    curve_data.align_y = 'CENTER'
    obj = bpy.data.objects.new(name=name, object_data=curve_data)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

# Materials
mat_brick = bpy.data.materials.get("PMU_Red_Brick_Gothic")
mat_limestone = bpy.data.materials.get("PMU_Bedford_Limestone")
mat_slate = bpy.data.materials.get("PMU_Slate_Roof")
mat_glass = bpy.data.materials.get("PMU_Lead_Gothic_Glass")
mat_stained = bpy.data.materials.get("PMU_Stained_Glass_Lancet")
mat_timber = bpy.data.materials.get("PMU_Dark_Oak_Timber")
mat_parquet = bpy.data.materials.get("PMU_GreatHall_Parquet")
mat_crest_gold = bpy.data.materials.get("PMU_Memorial_Crest_Gold")
mat_crest_black = bpy.data.materials.get("PMU_Memorial_Crest_Black")
mat_terrazzo = bpy.data.materials.get("PMU_Dining_Terrazzo")
mat_booth = bpy.data.materials.get("PMU_Dining_Booth_Leather")
mat_steel = bpy.data.materials.get("PMU_Stainless_Steel")
mat_gold_text = bpy.data.materials.get("PMU_Signage_Gold")
mat_ember = bpy.data.materials.get("PMU_Fireplace_Ember")
mat_granite = bpy.data.materials.get("PMU_Granite_Paver")

# Refine Parquet Floor Material to deep warm rich oak
if mat_parquet and mat_parquet.node_tree:
    bsdf = mat_parquet.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.35, 0.20, 0.10, 1.0) # warm dark oak
        bsdf.inputs["Roughness"].default_value = 0.25

# 1. FIX EXTERIOR ROOFS & WALL CLOSURES
# Remove the old buggy flat panels
for o in list(col_exterior.objects):
    if "PMU_Window_Frame_S_" in o.name or "PMU_Window_Glass_S_" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# Build complete 4-sided East Wing perimeter walls and solid floor/ceiling
create_box("PMU_EastWing_Wall_InnerWest", 236.0, 237.4, -300.0, -215.0, 1.5, 18.2, mat_brick, col_exterior)
create_box("PMU_EastWing_Wall_South", 236.0, 265.9, -300.0, -298.6, 1.5, 18.2, mat_brick, col_exterior)
create_box("PMU_EastWing_Floor", 236.0, 265.9, -300.0, -215.0, 0.0, 0.2, mat_limestone, col_exterior)
create_box("PMU_EastWing_Roof_Slab", 236.0, 265.9, -300.0, -215.0, 18.0, 18.3, mat_limestone, col_exterior)

# Build complete West Wing inner east wall
create_box("PMU_WestWing_Wall_InnerEast", 193.6, 195.0, -300.0, -215.0, 1.5, 18.2, mat_brick, col_exterior)
create_box("PMU_WestWing_Wall_South", 165.7, 195.0, -300.0, -298.6, 1.5, 18.2, mat_brick, col_exterior)

# Close Courtyard Ground with brick pavers
create_box("PMU_Inner_Courtyard_Ground", 195.0, 236.0, -260.0, -245.0, 0.0, 0.1, mat_brick, col_exterior)

# Completely re-create East Wing Gable Roof spanning full dimensions
create_gable_roof("PMU_Roof_East_Wing", 235.0, 266.5, -300.5, -214.5, 18.2, 23.5, mat_slate, col_exterior, axis='Y')
create_gable_roof("PMU_Roof_West_Wing", 165.0, 195.5, -300.5, -214.5, 18.2, 23.5, mat_slate, col_exterior, axis='Y')
create_gable_roof("PMU_Roof_South_Wing", 194.0, 237.0, -316.5, -260.0, 18.2, 24.0, mat_slate, col_exterior, axis='Y')

# 2. GOTHIC TOWER ARTICULATION & FENESTRATION
# Massive 2-story Gothic Stained Glass Window on South Tower (Z = 10.0 to 18.5m)
create_box("PMU_Tower_Gothic_Window_Frame", 212.0, 220.0, -318.0, -316.2, 10.0, 18.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Gothic_Window_Glass", 212.8, 219.2, -317.2, -316.8, 10.5, 18.0, mat_stained, col_exterior)
# Gothic Mullions (vertical tracery bars)
create_box("PMU_Tower_Mullion_1", 214.8, 215.2, -317.5, -316.5, 10.5, 17.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Mullion_2", 216.8, 217.2, -317.5, -316.5, 10.5, 17.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Transom_1", 212.8, 219.2, -317.5, -316.5, 14.0, 14.4, mat_limestone, col_exterior)

# Circular Gothic Clock Face on Tower (Z = 20.5m to 23.5m)
create_cylinder("PMU_Tower_Clock_Bezel", 216.0, -317.4, 20.5, 23.5, 1.6, 24, mat_limestone, col_exterior)
create_cylinder("PMU_Tower_Clock_Face", 216.0, -317.6, 20.7, 23.3, 1.4, 24, mat_gold_text, col_exterior)
# Clock Hands
create_box("PMU_Clock_Hour_Hand", 215.9, 216.1, -317.8, -317.6, 22.0, 22.8, mat_crest_black, col_exterior)
create_box("PMU_Clock_Min_Hand", 215.9, 216.8, -317.8, -317.6, 21.9, 22.1, mat_crest_black, col_exterior)

# South Facade Collegiate Gothic Lancet Windows on flanking wings
for idx, wx in enumerate([188.0, 194.0, 200.0, 226.0, 232.0, 238.0]):
    # Outer limestone arch frame
    create_box(f"PMU_Gothic_Win_Frame_{idx}", wx - 1.5, wx + 1.5, -317.4, -315.6, 6.0, 12.0, mat_limestone, col_exterior)
    # Stained glass pane
    create_box(f"PMU_Gothic_Win_Glass_{idx}", wx - 1.1, wx + 1.1, -316.6, -316.4, 6.4, 11.6, mat_stained, col_exterior)
    # Vertical stone mullion dividing the two lancets
    create_box(f"PMU_Gothic_Win_Mullion_{idx}", wx - 0.15, wx + 0.15, -317.0, -316.0, 6.4, 11.6, mat_limestone, col_exterior)
    # Upper gothic arch hood molding
    create_box(f"PMU_Gothic_Win_Hood_{idx}", wx - 1.8, wx + 1.8, -317.6, -315.5, 12.0, 12.6, mat_limestone, col_exterior)

# 3. REVISE INSPECTION CAMERAS FOR FLAWLESS UNRESTRICTED VIEWS
# Cam 67: South Hero View (State Street) - Elevated slightly to frame grand steps, arch, gothic window, clock, and rooflines
cam67 = bpy.data.objects.get("Cam_67_PMU_StateStreet_South_Hero")
if cam67:
    cam67.location = Vector((216.0, -365.0, 7.5))
    target67 = Vector((216.0, -305.0, 16.0))
    cam67.rotation_euler = (target67 - cam67.location).to_track_quat('-Z', 'Y').to_euler()
    cam67.data.lens = 32.0

# Cam 68: Great Hall Interior - Frame the Sacred Floor Crest, Fireplace, Chandelier, and Timber Ceilings
cam68 = bpy.data.objects.get("Cam_68_PMU_GreatHall_MemorialCross_Interior")
if cam68:
    cam68.location = Vector((208.0, -306.0, 5.6))
    target68 = Vector((216.0, -288.0, 5.0))
    cam68.rotation_euler = (target68 - cam68.location).to_track_quat('-Z', 'Y').to_euler()
    cam68.data.lens = 24.0

# Add 3D Inscription around Sacred Floor Crest
create_3d_text("PMU_Crest_Text_North", "PURDUE  MEMORIAL  UNION", (216.0, -290.0, 4.38), (0, 0, 0), 0.32, mat_crest_gold, col_interiors, extrude=0.01)
create_3d_text("PMU_Crest_Text_South", "HONORING  PURDUE  VETERANS", (216.0, -296.0, 4.38), (0, 0, math.radians(180)), 0.28, mat_crest_gold, col_interiors, extrude=0.01)

# Cam 69: PMU Dining Court - Position in open central promenade avoiding pillars
cam69 = bpy.data.objects.get("Cam_69_PMU_DiningCourt_Commons_Interior")
if cam69:
    # Placed at X=210.0, Y=-256.0, Z=1.8 (midway between pillars), looking North-Northeast toward Walk-On's, BBQ, and Zen
    cam69.location = Vector((210.0, -256.0, 1.8))
    target69 = Vector((220.0, -236.0, 1.8))
    cam69.rotation_euler = (target69 - cam69.location).to_track_quat('-Z', 'Y').to_euler()
    cam69.data.lens = 22.0

# Add Illuminated Restaurant Signage in Dining Court
create_3d_text("PMU_Sign_WalkOns", "WALK-ON'S  SPORTS  BISTREAUX", (194.5, -256.0, 3.2), (math.radians(90), 0, math.radians(-90)), 0.45, mat_gold_text, col_interiors)
create_3d_text("PMU_Sign_BBQ", "BBQ  DISTRICT", (206.0, -226.5, 3.2), (math.radians(90), 0, 0), 0.50, mat_gold_text, col_interiors)
create_3d_text("PMU_Sign_Zen", "ZEN  ASIAN  BOWLS", (228.0, -226.5, 3.2), (math.radians(90), 0, 0), 0.50, mat_gold_text, col_interiors)
create_3d_text("PMU_Sign_Starbucks", "STARBUCKS  COFFEE", (240.2, -257.0, 3.2), (math.radians(90), 0, math.radians(90)), 0.45, mat_gold_text, col_interiors)

# Cam 70: West Courtyard - Move OUT of Stewart Center!
# Stewart Center East wall is at X = 151.3m. PMU West wall is at X = 165.7m.
# Place camera at X = 154.0m, Y = -308.0m, Z = 3.2m, looking North-East down the courtyard promenade toward the Gothic Loggia
cam70 = bpy.data.objects.get("Cam_70_PMU_WestCourtyard_Stewart_Interface")
if cam70:
    cam70.location = Vector((154.0, -308.0, 3.2))
    target70 = Vector((166.0, -270.0, 6.5))
    cam70.rotation_euler = (target70 - cam70.location).to_track_quat('-Z', 'Y').to_euler()
    cam70.data.lens = 28.0
    print("Updated Cam 70 position to open West Courtyard promenade")

# Cam 71: Aerial Precinct Overview
cam71 = bpy.data.objects.get("Cam_71_PMU_StateStreet_GrantStreet_Aerial")
if cam71:
    cam71.location = Vector((320.0, -380.0, 72.0))
    target71 = Vector((216.0, -263.0, 10.0))
    cam71.rotation_euler = (target71 - cam71.location).to_track_quat('-Z', 'Y').to_euler()
    cam71.data.lens = 32.0

# Save master file
master_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_path)
print(f"Master file saved to {master_path}")
print("--- Refinement Pass Completed Successfully ---")
