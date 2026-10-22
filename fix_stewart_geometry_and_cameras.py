"""
Fine-tune Stewart Center (STEW) Camera Framing & Interior Materials - Pass 3
Eliminates Hicks Library corner in Cam 72, enriches HSSE Library study tables/flooring in Cam 74,
and positions Ringel Gallery Cam 75 down the central sculpture & art promenade.
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Fine-Tuning Stewart Center Geometry, Materials & Cameras ===")
    
    col_ext = bpy.data.collections.get("48_Stewart_Center_Exterior")
    col_int = bpy.data.collections.get("49_Stewart_Center_Interiors")
    col_site = bpy.data.collections.get("50_Stewart_Center_Plaza_and_Site")

    # Update Materials with richer tones
    mat_honey_oak = bpy.data.materials.get("Stewart_Honey_Oak")
    if mat_honey_oak and mat_honey_oak.node_tree:
        bsdf = mat_honey_oak.node_tree.nodes.get("Principled BSDF")
        if bsdf and "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.46, 0.24, 0.10, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.25
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.8

    mat_terrazzo = bpy.data.materials.get("Stewart_Polished_Terrazzo")
    if mat_terrazzo and mat_terrazzo.node_tree:
        bsdf = mat_terrazzo.node_tree.nodes.get("Principled BSDF")
        if bsdf and "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.88, 0.87, 0.85, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.08
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.98

    mat_green_glass = bpy.data.materials.get("Stewart_Bankers_Green_Glass")
    if mat_green_glass and mat_green_glass.node_tree:
        bsdf = mat_green_glass.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (0.05, 0.55, 0.18, 1.0)
                bsdf.inputs["Emission Strength"].default_value = 4.0

    # Adjust HSSE Library Light
    lib_light = bpy.data.objects.get("HSSE_Main_Light")
    if lib_light and lib_light.data:
        lib_light.data.energy = 3000.0
        lib_light.data.color = (1.0, 0.92, 0.80)

    # Helper function to calibrate camera with look_at vector
    def set_camera(name, loc, target, lens=28.0):
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

    # 1. Cam_72: Positioned on State Street concourse at (58.0, -308.0, 3.0) looking NE at (84.0, -300.0, 5.5)
    # This is completely North of Hicks Library (Y = -318), giving 100% unobstructed hero view of portico & gold sign
    set_camera("Cam_72_Stewart_South_Hero", (58.0, -308.0, 3.0), (84.0, -300.0, 5.5), lens=24.0)

    # 2. Cam_73: Loeb Playhouse
    set_camera("Cam_73_Stewart_LoebPlayhouse_Interior", (52.0, -266.0, 2.3), (52.0, -244.0, 3.8), lens=24.0)

    # 3. Cam_74: HSSE Library Interior
    # Positioned at (97.0, -242.0, 2.1) looking at (116.0, -230.0, 1.9) with lens 24.0
    set_camera("Cam_74_Stewart_HSSE_Library_Interior", (97.0, -242.0, 2.1), (116.0, -230.0, 1.9), lens=24.0)

    # 4. Cam_75: Robert L. Ringel Gallery Interior
    # Positioned right along central gallery aisle (103.0, -264.0, 1.8) looking East at (126.0, -264.0, 1.8)
    set_camera("Cam_75_Stewart_RingelGallery_Interior", (103.0, -264.0, 1.8), (126.0, -264.0, 1.8), lens=26.0)

    # 5. Cam_76: Precinct Aerial
    set_camera("Cam_76_Stewart_North_Aerial", (35.0, -145.0, 48.0), (100.0, -250.0, 10.0), lens=28.0)

    print("=== Fine-Tuning Completed Successfully! ===")

if __name__ == "__main__":
    run()
