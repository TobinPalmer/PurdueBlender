"""
Quick Polish for Stewart Center Cam 74 (HSSE Library) and Cam 75 (Ringel Gallery)
Removes blocking partition walls in Ringel Gallery, sets open perspective,
and enriches HSSE Library study tables and ambient lighting.
"""

import bpy
import mathutils
import os

master_blend = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

print("Opening master blend...")
bpy.ops.wm.open_mainfile(filepath=master_blend)

col_int = bpy.data.collections.get("49_Stewart_Center_Interiors")

# 1. Remove blocking partition walls in Ringel Gallery
for wname in ["Ringel_Exhibition_Wall_1", "Ringel_Exhibition_Wall_2"]:
    wobj = bpy.data.objects.get(wname)
    if wobj:
        print(f"Removing {wname} for open gallery circulation...")
        bpy.data.objects.remove(wobj, do_unlink=True)

# 2. Add extra gallery paintings along the walls with picture lights
mat_gold = bpy.data.materials.get("Stewart_Signage_Gold")
mat_brass = bpy.data.materials.get("Stewart_Polished_Brass")
mat_stone = bpy.data.materials.get("Stewart_Bedford_Limestone")
mat_bronze = bpy.data.materials.get("Stewart_Bronze_Metal")
mat_white = bpy.data.materials.get("Stewart_Gallery_White")

def make_box(name, col, loc, size, mat=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if col:
        col.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

# Staggered sculpture pedestals in the open gallery
for i, px, py, sculp_mat in [
    (1, 104.0, -265.5, mat_bronze),
    (2, 112.0, -260.5, mat_stone),
    (3, 120.0, -265.5, mat_bronze),
    (4, 128.0, -260.5, mat_stone)
]:
    pname = f"Ringel_Pedestal_{i}"
    pobj = bpy.data.objects.get(pname)
    if pobj:
        pobj.location = (px, py, 1.0)
    sname = f"Ringel_Sculpture_{i}"
    sobj = bpy.data.objects.get(sname)
    if sobj:
        sobj.location = (px, py, 1.9)

# 3. Enhance Honey Oak Material for HSSE Study Tables
mat_oak = bpy.data.materials.get("Stewart_Honey_Oak")
if mat_oak and mat_oak.node_tree:
    bsdf = mat_oak.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.38, 0.18, 0.06, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.20
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.85

# Warm wall sconces in HSSE Library along South Wall
mat_warm = bpy.data.materials.get("Stewart_Warm_Lamp_Glow")
for sx in [94.0, 104.0, 114.0, 124.0, 134.0]:
    make_box(f"HSSE_Wall_Sconce_{sx}", col_int, (sx, -245.7, 3.2), (0.8, 0.3, 0.4), mat_warm)

# 4. Calibrate Camera 74 (HSSE Library) and Camera 75 (Ringel Gallery)
def set_camera(name, loc, target, lens=24.0):
    cam_obj = bpy.data.objects.get(name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(name=name + "_Data")
        cam_obj = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = mathutils.Vector(loc)
    target_v = mathutils.Vector(target)
    direction = target_v - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1500.0
    print(f"Calibrated {name} at {loc} -> target {target}")
    return cam_obj

# Cam 74: HSSE Library
set_camera("Cam_74_Stewart_HSSE_Library_Interior", (95.0, -242.0, 2.5), (116.0, -229.0, 2.0), lens=24.0)

# Cam 75: Ringel Gallery - completely open view down the gallery promenade
set_camera("Cam_75_Stewart_RingelGallery_Interior", (94.0, -263.0, 2.0), (120.0, -263.0, 1.9), lens=24.0)

# Save Master Blend
print("Saving master blend file...")
bpy.ops.wm.save_mainfile(filepath=master_blend)
print("Master blend file saved!")

# Re-render all 5 cameras
cams = [
    ("Cam_72_Stewart_South_Hero", "stewart_cam72_south_hero.png"),
    ("Cam_73_Stewart_LoebPlayhouse_Interior", "stewart_cam73_loeb_playhouse.png"),
    ("Cam_74_Stewart_HSSE_Library_Interior", "stewart_cam74_hsse_library.png"),
    ("Cam_75_Stewart_RingelGallery_Interior", "stewart_cam75_ringel_gallery.png"),
    ("Cam_76_Stewart_North_Aerial", "stewart_cam76_precinct_aerial.png")
]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

for cam_name, fname in cams:
    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj:
        scene.camera = cam_obj
        out_path = os.path.join(artifact_dir, fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"Rendered {cam_name} -> {fname} ({size_kb:.1f} KB)")

print("=== Polish and Re-Render Complete! ===")
