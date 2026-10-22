import bpy
import math
from mathutils import Vector

print("--- Starting PMU Gold Standard Remediation Pass ---")

# 1. Purge all .001 duplicates across collections 45, 46, 47
pmu_cols = [
    bpy.data.collections.get("45_Purdue_Memorial_Union_Exterior"),
    bpy.data.collections.get("46_Purdue_Memorial_Union_Interiors"),
    bpy.data.collections.get("47_Purdue_Memorial_Union_Plaza_and_Site")
]

purged_count = 0
for col in pmu_cols:
    if col:
        for obj in list(col.objects):
            if ".001" in obj.name or ".002" in obj.name:
                bpy.data.objects.remove(obj, do_unlink=True)
                purged_count += 1

print(f"Purged {purged_count} duplicate objects")

col_exterior = bpy.data.collections.get("45_Purdue_Memorial_Union_Exterior")
col_interiors = bpy.data.collections.get("46_Purdue_Memorial_Union_Interiors")
col_site = bpy.data.collections.get("47_Purdue_Memorial_Union_Plaza_and_Site")

mat_brick = bpy.data.materials.get("PMU_Red_Brick_Gothic")
mat_limestone = bpy.data.materials.get("PMU_Bedford_Limestone")
mat_slate = bpy.data.materials.get("PMU_Slate_Roof")
mat_stained = bpy.data.materials.get("PMU_Stained_Glass_Lancet")
mat_crest_black = bpy.data.materials.get("PMU_Memorial_Crest_Black")
mat_crest_gold = bpy.data.materials.get("PMU_Memorial_Crest_Gold")
mat_timber = bpy.data.materials.get("PMU_Dark_Oak_Timber")
mat_parquet = bpy.data.materials.get("PMU_GreatHall_Parquet")

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

# 2. Re-engineer South Tower Gothic Window into open hollow tracery frame
old_frame = bpy.data.objects.get("PMU_Tower_Gothic_Window_Frame")
if old_frame:
    bpy.data.objects.remove(old_frame, do_unlink=True)

# Perimeter jambs, sill, head, and stone tracery
create_box("PMU_Tower_Window_Sill", 211.5, 220.5, -318.0, -316.0, 10.0, 10.7, mat_limestone, col_exterior)
create_box("PMU_Tower_Window_Head", 211.5, 220.5, -318.0, -316.0, 17.8, 18.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Window_Jamb_L", 211.5, 212.8, -318.0, -316.0, 10.7, 17.8, mat_limestone, col_exterior)
create_box("PMU_Tower_Window_Jamb_R", 219.2, 220.5, -318.0, -316.0, 10.7, 17.8, mat_limestone, col_exterior)
create_box("PMU_Tower_Window_Mullion_C", 215.6, 216.4, -317.8, -316.2, 10.7, 17.8, mat_limestone, col_exterior)
create_box("PMU_Tower_Window_Transom", 212.8, 219.2, -317.8, -316.2, 13.8, 14.4, mat_limestone, col_exterior)

# Enhance Stained Glass with vibrant stained emissive shader
if mat_stained and mat_stained.node_tree:
    bsdf = mat_stained.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.95, 0.40, 0.15, 1.0)
        bsdf.inputs["Emission Color"].default_value = (0.98, 0.50, 0.18, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.5

# Stained glass pane positioned right behind the tracery frame
create_box("PMU_Tower_Gothic_Window_Glass", 212.6, 219.4, -316.8, -316.4, 10.6, 17.9, mat_stained, col_exterior)

# 3. Flanking South Facade Windows: Open hollow limestone surrounds
for idx, wx in enumerate([188.0, 194.0, 200.0, 226.0, 232.0, 238.0]):
    # Remove old flat solid frame
    old_f = bpy.data.objects.get(f"PMU_Gothic_Win_Frame_{idx}")
    if old_f:
        bpy.data.objects.remove(old_f, do_unlink=True)
    # Build open surround: sill, jambs, lintel
    create_box(f"PMU_Gothic_Win_Sill_{idx}", wx - 1.6, wx + 1.6, -317.4, -315.6, 6.0, 6.6, mat_limestone, col_exterior)
    create_box(f"PMU_Gothic_Win_Lintel_{idx}", wx - 1.6, wx + 1.6, -317.4, -315.6, 11.4, 12.0, mat_limestone, col_exterior)
    create_box(f"PMU_Gothic_Win_JambL_{idx}", wx - 1.6, wx - 1.1, -317.4, -315.6, 6.6, 11.4, mat_limestone, col_exterior)
    create_box(f"PMU_Gothic_Win_JambR_{idx}", wx + 1.1, wx + 1.6, -317.4, -315.6, 6.6, 11.4, mat_limestone, col_exterior)
    # Stained glass pane
    create_box(f"PMU_Gothic_Win_Glass_{idx}", wx - 1.1, wx + 1.1, -316.4, -316.1, 6.6, 11.4, mat_stained, col_exterior)

# 4. Tower Clock Hour Markers (12 Radial Tick Marks)
for hour in range(12):
    ha = hour * (math.pi / 6.0)
    hx = 216.0 + 1.15 * math.sin(ha)
    hz = 22.0 + 1.15 * math.cos(ha)
    create_box(f"PMU_Clock_Tick_{hour}", hx - 0.05, hx + 0.05, -317.9, -317.65, hz - 0.05, hz + 0.05, mat_crest_black, col_exterior)

# 5. Turret Crenellations atop the 4 corner turrets (Z = 28.5 to 29.5m)
turret_coords = [(208.2, -317.6), (223.8, -317.6), (208.2, -303.2), (223.8, -303.2)]
for t_i, (tx, ty) in enumerate(turret_coords):
    for c_i in range(4):
        ca = c_i * (math.pi / 2.0)
        cx = tx + 1.1 * math.cos(ca)
        cy = ty + 1.1 * math.sin(ca)
        create_box(f"PMU_Turret_Cren_{t_i}_{c_i}", cx - 0.35, cx + 0.35, cy - 0.35, cy + 0.35, 28.5, 29.5, mat_limestone, col_exterior)

# 6. Refine Parquet Floor Tone in Great Hall (Warm dark oak)
if mat_parquet and mat_parquet.node_tree:
    bsdf = mat_parquet.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.28, 0.16, 0.08, 1.0) # deep rich antique oak
        bsdf.inputs["Roughness"].default_value = 0.28

# Save Master Blend File
master_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_path)
print(f"Master file saved to {master_path}")
print("--- PMU Gold Standard Remediation Completed Successfully ---")
