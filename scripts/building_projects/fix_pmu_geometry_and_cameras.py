import bpy
import math
from mathutils import Vector, Euler

print("--- Fixing PMU Roof Gaps & Interior Camera Alignments ---")

col_exterior = bpy.data.collections.get("45_Purdue_Memorial_Union_Exterior")
col_interiors = bpy.data.collections.get("46_Purdue_Memorial_Union_Interiors")

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

mat_brick = bpy.data.materials.get("PMU_Red_Brick_Gothic")
mat_limestone = bpy.data.materials.get("PMU_Bedford_Limestone")
mat_slate = bpy.data.materials.get("PMU_Slate_Roof")

# 1. Fill the roof and ceiling gap on South Wing:
# Build continuous transverse gable roof over South Wing spanning X: 184.0 to 247.0, Y: -316.5 to -260.0
create_box("PMU_SouthWing_Ceiling_Fill", 184.5, 246.5, -316.5, -260.0, 18.0, 18.3, mat_limestone, col_exterior)
create_gable_roof("PMU_Roof_South_Wing", 184.0, 247.0, -316.5, -260.0, 18.2, 24.2, mat_slate, col_exterior, axis='X')

# Fill wall between Tower East and East Wing (X: 224 to 236, Y: -316.5 to -300.0)
create_box("PMU_Wall_Fill_SE", 223.5, 236.5, -302.0, -300.5, 1.5, 18.2, mat_brick, col_exterior)
# Fill wall between Tower West and West Wing (X: 195 to 208, Y: -316.5 to -300.0)
create_box("PMU_Wall_Fill_SW", 194.5, 208.5, -302.0, -300.5, 1.5, 18.2, mat_brick, col_exterior)

# 2. Camera 68 (Great Hall Interior):
# Sited right in the open center aisle at X = 216.0, Y = -301.0, Z = 5.5, looking North down the hall
cam68 = bpy.data.objects.get("Cam_68_PMU_GreatHall_MemorialCross_Interior")
if cam68:
    cam68.location = Vector((216.0, -301.0, 5.5))
    target68 = Vector((216.0, -284.0, 5.2))
    cam68.rotation_euler = (target68 - cam68.location).to_track_quat('-Z', 'Y').to_euler()
    cam68.data.lens = 22.0
    print("Repositioned Cam 68 along Great Hall central axis")

# 3. Camera 69 (Dining Court Interior):
# Move to open promenade avoiding pillars (X = 207.0, Y = -258.0, Z = 1.8), looking North-Northeast
cam69 = bpy.data.objects.get("Cam_69_PMU_DiningCourt_Commons_Interior")
if cam69:
    cam69.location = Vector((208.0, -258.0, 1.8))
    target69 = Vector((224.0, -236.0, 1.8))
    cam69.rotation_euler = (target69 - cam69.location).to_track_quat('-Z', 'Y').to_euler()
    cam69.data.lens = 20.0
    print("Repositioned Cam 69 to clear dining court pillars")

# Save master blend file
master_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_path)
print(f"Master file saved to {master_path}")
