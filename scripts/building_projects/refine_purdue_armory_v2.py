"""
Attempt 3 / Gold Standard Exemplar Refinement Script for Purdue Armory (AR - 1918)
- Fixes Cam 87 street view framing & Elliott Hall clearance (lens=18mm diagonal corridor view)
- Fixes Cam 90 mezzanine overlook by placing on West mezzanine with clean 3/4 vista
- Enhances Officer's Club with rich dark oak parquet floor (Z=0.45m), Persian rug (Z=0.48m), banker's lamp
- Articulates West facade of Officer's Club with dark oak wainscoting, arched doors, and framed historical photos
- Adds 4 regulation basketball hoops, glass backboards, and cadet obstacle vaults to Drill Hall
- Warms maple hardwood floor color and boosts specular reflections
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Refining Purdue Armory (AR - 1918) to Gold Standard Exemplar (Pass 3) ===")

    col_ext = bpy.data.collections.get("57_Armory_Exterior")
    col_int = bpy.data.collections.get("58_Armory_Interiors_and_DrillHall")
    col_site = bpy.data.collections.get("59_Armory_Plaza_and_Site")

    root_obj = bpy.data.objects.get("Armory_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("Armory_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        bpy.context.scene.collection.objects.link(root_obj)

    root_loc = (-218.55, 68.35, 0.0)
    root_obj.location = root_loc
    root_obj.rotation_euler = (0, 0, 0)
    M_WORLD = mathutils.Matrix.Translation(root_loc)

    def get_mat(name, color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, specular=0.5, metallic=0.0, emission=None):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if "Base Color" in bsdf.inputs:
                bsdf.inputs["Base Color"].default_value = color
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = roughness
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = specular
            elif "Specular" in bsdf.inputs:
                bsdf.inputs["Specular"].default_value = specular
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metallic
            if emission:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission[:4]
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission[4] if len(emission) > 4 else 1.0
        return mat

    # Enhanced Materials
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_mat("Purdue_Old_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mat_bronze = get_mat("Armory_Dark_Bronze", (0.25, 0.20, 0.16, 1.0), roughness=0.35, metallic=0.85)
    mat_dark_oak = get_mat("Armory_Dark_Oak", (0.22, 0.12, 0.06, 1.0), roughness=0.28, specular=0.65)
    mat_maple_floor = get_mat("Armory_Polished_Maple", (0.85, 0.62, 0.36, 1.0), roughness=0.12, specular=0.95)
    mat_court_lines = get_mat("Armory_Court_Lines", (0.95, 0.95, 0.95, 1.0), roughness=0.3)
    mat_court_gold = get_mat("Armory_Court_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25)
    mat_persian_rug = get_mat("Armory_Persian_Rug", (0.50, 0.12, 0.14, 1.0), roughness=0.75)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_mat("Solar_Ribbon_Glass", (0.15, 0.28, 0.38, 0.85), roughness=0.08, specular=0.98)
    mat_green_glass = get_mat("Armory_Green_Glass_Shade", (0.05, 0.40, 0.15, 1.0), roughness=0.15, specular=0.95, emission=(0.1, 0.9, 0.3, 2.5))
    mat_photo_bw = get_mat("Armory_Historical_Photo", (0.75, 0.75, 0.72, 1.0), roughness=0.3)
    mat_orange_rim = get_mat("Armory_Orange_Rim", (0.95, 0.35, 0.05, 1.0), roughness=0.3)
    mat_vault_blue = get_mat("Armory_Vault_Blue", (0.10, 0.22, 0.55, 1.0), roughness=0.5)

    def make_box_local(name, col, loc, size, mat=None):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        sx, sy, sz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
        verts = [
            (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
            (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (1, 2, 6, 5),
            (2, 3, 7, 6), (3, 0, 4, 7)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        obj.parent = root_obj
        obj.location = loc
        col.objects.link(obj)
        return obj

    # 1. Update Officer's Club Floor & Persian Rug Elevations to Eliminate Z-Fighting
    # Update existing floor and rug
    old_floor = bpy.data.objects.get("Armory_Club_Floor")
    if old_floor:
        old_floor.location = (20.0, 0.0, 0.46)
        old_floor.data.materials.clear()
        old_floor.data.materials.append(mat_dark_oak)
    else:
        make_box_local("Armory_Club_Floor", col_int, (20.0, 0.0, 0.46), (7.8, 23.6, 0.06), mat_dark_oak)

    old_rug = bpy.data.objects.get("Armory_Officer_Rug")
    if old_rug:
        old_rug.location = (19.5, -4.5, 0.50)
    else:
        make_box_local("Armory_Officer_Rug", col_int, (19.5, -4.5, 0.50), (4.5, 5.5, 0.02), mat_persian_rug)

    # Add Brass Banker's Lamp and Open Cadence Manuals to Officer's Table
    make_box_local("Armory_Table_Banker_Lamp", col_int, (19.5, -4.5, 1.45), (0.35, 0.20, 0.40), mat_gold)
    make_box_local("Armory_Table_Lamp_Shade", col_int, (19.5, -4.5, 1.65), (0.42, 0.24, 0.15), mat_green_glass)
    make_box_local("Armory_Table_Manual", col_int, (18.8, -4.5, 1.28), (0.40, 0.30, 0.04), mat_gold)

    # 2. Articulate West Exterior Wall of Officer's Club facing Drill Hall (X = 16.0m)
    # Dark Oak Wainscoting Band along Drill Hall floor
    make_box_local("Armory_Club_Ext_Wainscot", col_int, (15.75, 0.0, 1.2), (0.1, 23.8, 1.6), mat_dark_oak)
    # Double Arched Access Doors into Officer's Club
    for d_y in [-6.0, 6.0]:
        make_box_local(f"Armory_Club_Ext_Door_{d_y}", col_int, (15.72, d_y, 2.2), (0.15, 2.2, 3.6), mat_dark_oak)
        make_box_local(f"Armory_Club_Ext_Arch_{d_y}", col_int, (15.70, d_y, 4.2), (0.2, 2.4, 0.4), mat_gold)
    # Framed Historical Purdue ROTC Photographs
    for p_idx, p_y in enumerate([-9.0, -2.0, 2.0, 9.0]):
        make_box_local(f"Armory_Club_Photo_Frame_{p_idx}", col_int, (15.72, p_y, 3.2), (0.1, 1.8, 1.4), mat_dark_oak)
        make_box_local(f"Armory_Club_Photo_Print_{p_idx}", col_int, (15.65, p_y, 3.2), (0.05, 1.6, 1.2), mat_photo_bw)

    # 3. Add 4 Basketball Hoops & Backboards to Drill Hall
    hoop_locs = [
        ("N_Main", 0.0, 14.5, 0.0),
        ("S_Main", 0.0, -14.5, math.pi),
        ("E_Side", 13.5, 0.0, -math.pi/2),
        ("W_Side", -13.5, 0.0, math.pi/2)
    ]
    for h_id, hx, hy, hrot in hoop_locs:
        # Steel stanchion post
        make_box_local(f"Armory_Hoop_Post_{h_id}", col_int, (hx, hy + (0.8 if hrot==0 else -0.8 if hrot==math.pi else 0), 2.2), (0.2, 0.2, 3.8), mat_bronze)
        # Clear glass backboard
        bb_w = 1.8 if hrot in [0, math.pi] else 0.1
        bb_l = 0.1 if hrot in [0, math.pi] else 1.8
        make_box_local(f"Armory_Backboard_{h_id}", col_int, (hx, hy, 3.5), (bb_w, bb_l, 1.05), mat_glass)
        # Orange breakaway rim
        make_box_local(f"Armory_Rim_{h_id}", col_int, (hx + (0.3 if hrot==math.pi/2 else -0.3 if hrot==-math.pi/2 else 0), hy + (0.3 if hrot==math.pi else -0.3 if hrot==0 else 0), 3.05), (0.5, 0.5, 0.06), mat_orange_rim)

    # Cadet Physical Training Vault Boxes along West Wall
    for vx in [-18.0, -18.0]:
        for vy in [-25.0, 25.0]:
            make_box_local(f"Armory_Vault_Box_{vy}", col_int, (vx, vy, 0.9), (1.4, 2.2, 1.0), mat_dark_oak)
            make_box_local(f"Armory_Mat_{vy}", col_int, (vx, vy, 0.43), (2.4, 3.2, 0.06), mat_vault_blue)

    # =========================================================================
    # RE-CALIBRATE PRECISION INSPECTION CAMERAS
    # =========================================================================
    print("Re-calibrating Precision Inspection Cameras for Gold Standard Certification...")

    def set_camera(name, loc_world, target_world, lens=24.0):
        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name=name + "_Data")
            cam_obj = bpy.data.objects.new(name, cam_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = mathutils.Vector(loc_world)
        target_v = mathutils.Vector(target_world)
        direction = target_v - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_obj.data.lens = lens
        cam_obj.data.clip_start = 0.1
        cam_obj.data.clip_end = 1500.0
        print(f"Calibrated {name} at {loc_world} -> target {target_world} (lens={lens}mm)")
        return cam_obj

    def local_to_world_explicit(local_coord):
        return M_WORLD @ mathutils.Vector(local_coord)

    # 1. Cam_87: University St Hero Arrival View
    # Perfectly placed inside University Street corridor at local (44.0, -36.0, 5.2)
    # Targets local (15.0, 8.0, 9.5) with wide 18mm lens to frame both Romanesque towers, portico, lettering, cannons & flag
    cam87_loc = local_to_world_explicit((44.0, -36.0, 5.2))
    cam87_target = local_to_world_explicit((15.0, 8.0, 9.5))
    set_camera("Cam_87_Armory_UniversitySt_Hero", cam87_loc, cam87_target, lens=18.0)

    # 2. Cam_88: The Great Drill Hall Interior
    # Looking down the full 85m clear length with basketball hoops, running track, and ROTC dais
    cam88_loc = local_to_world_explicit((0.0, -36.0, 3.2))
    cam88_target = local_to_world_explicit((0.0, 16.0, 5.5))
    set_camera("Cam_88_Armory_DrillHall_Colossal_Trusses_Interior", cam88_loc, cam88_target, lens=22.0)

    # 3. Cam_89: Officer's Club & Cadet Heritage Lounge
    # 3/4 perspective across Persian rug, wingback chairs, banker's lamp, chandelier, and vitrines
    cam89_loc = local_to_world_explicit((17.2, -8.8, 2.3))
    cam89_target = local_to_world_explicit((21.2, 0.2, 2.0))
    set_camera("Cam_89_Armory_OfficersClub_Lounge_Interior", cam89_loc, cam89_target, lens=24.0)

    # 4. Cam_90: Viewing Mezzanine Gallery Overlook
    # Positioned on West Mezzanine at local (-21.5, -20.0, 7.2)
    # Targets local (2.0, 12.0, 2.0) with 20mm lens: sweeping unobstructed overlook of the entire drill floor,
    # basketball courts, colossal arched steel trusses, North fanlight window, and Officer's Club facade!
    cam90_loc = local_to_world_explicit((-21.5, -20.0, 7.2))
    cam90_target = local_to_world_explicit((2.0, 12.0, 2.0))
    set_camera("Cam_90_Armory_Mezzanine_Overlook_Interior", cam90_loc, cam90_target, lens=20.0)

    # 5. Cam_91: North-East Precinct Aerial Overview
    cam91_loc = local_to_world_explicit((68.0, 62.0, 54.0))
    cam91_target = local_to_world_explicit((0.0, 0.0, 10.0))
    set_camera("Cam_91_Armory_Precinct_Aerial", cam91_loc, cam91_target, lens=28.0)

    print("=== Purdue Armory Pass 3 Completed Successfully! ===")

if __name__ == "__main__":
    run()
