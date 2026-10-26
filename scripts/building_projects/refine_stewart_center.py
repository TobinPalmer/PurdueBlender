"""
Refine Purdue Stewart Center (STEW - 1958) Digital Twin - Pass 2 & 3
Full Mid-Century Collegiate Envelopes, Loeb Playhouse 1,011-Seat Proscenium Theatre,
HSSE Library Reading Hall with Book Stacks & Banker's Lamps, Robert L. Ringel Art Gallery,
Main Concourse / Boilermaker Station, North Memorial Mall Terrace & South State St Plaza.
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Refining Stewart Center (STEW) Digital Twin ===")

    # 1. Purge previous objects in Stewart Center collections for clean build
    for col_name in ["48_Stewart_Center_Exterior", "49_Stewart_Center_Interiors", "50_Stewart_Center_Plaza_and_Site"]:
        c = bpy.data.collections.get(col_name)
        if c:
            print(f"Purging existing collection: {col_name} ({len(c.objects)} objects)")
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(c)

    # Recreate dedicated collections
    col_ext = bpy.data.collections.new("48_Stewart_Center_Exterior")
    col_int = bpy.data.collections.new("49_Stewart_Center_Interiors")
    col_site = bpy.data.collections.new("50_Stewart_Center_Plaza_and_Site")
    
    bpy.context.scene.collection.children.link(col_ext)
    bpy.context.scene.collection.children.link(col_int)
    bpy.context.scene.collection.children.link(col_site)

    # Material Helper
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
                    bsdf.inputs["Emission Color"].default_value = emission[:3] + (1.0,)
                    bsdf.inputs["Emission Strength"].default_value = emission[3] if len(emission) > 3 else 1.0
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission[:3] + (1.0,)
        return mat

    # Materials setup
    mat_brick = get_mat("Stewart_Purdue_Red_Brick", (0.48, 0.16, 0.10, 1.0), roughness=0.72)
    mat_stone = get_mat("Stewart_Bedford_Limestone", (0.82, 0.80, 0.75, 1.0), roughness=0.55)
    mat_glass = get_mat("Stewart_Solar_Curtain_Glass", (0.10, 0.18, 0.24, 0.85), roughness=0.05, specular=0.95)
    mat_gold = get_mat("Stewart_Signage_Gold", (0.96, 0.78, 0.22, 1.0), roughness=0.22, metallic=0.95)
    mat_bronze = get_mat("Stewart_Bronze_Metal", (0.28, 0.20, 0.14, 1.0), roughness=0.35, metallic=0.85)
    mat_dark_oak = get_mat("Stewart_Dark_Oak", (0.24, 0.14, 0.08, 1.0), roughness=0.32)
    mat_honey_oak = get_mat("Stewart_Honey_Oak", (0.58, 0.38, 0.20, 1.0), roughness=0.28, specular=0.6)
    mat_terrazzo = get_mat("Stewart_Polished_Terrazzo", (0.86, 0.85, 0.83, 1.0), roughness=0.12, specular=0.95)
    mat_crimson_velvet = get_mat("Stewart_Crimson_Velvet", (0.48, 0.04, 0.06, 1.0), roughness=0.85, specular=0.4)
    mat_navy_carpet = get_mat("Stewart_Navy_Carpet", (0.06, 0.10, 0.22, 1.0), roughness=0.92)
    mat_concrete = get_mat("Stewart_Walkway_Concrete", (0.75, 0.74, 0.72, 1.0), roughness=0.6)
    mat_plaza_brick = get_mat("Stewart_Plaza_Brick", (0.42, 0.15, 0.10, 1.0), roughness=0.7)
    mat_brass = get_mat("Stewart_Polished_Brass", (0.92, 0.76, 0.30, 1.0), roughness=0.18, metallic=0.92)
    mat_green_glass = get_mat("Stewart_Bankers_Green_Glass", (0.04, 0.38, 0.12, 0.9), roughness=0.08, specular=0.95, emission=(0.08, 0.45, 0.15, 2.0))
    mat_white_gallery = get_mat("Stewart_Gallery_White", (0.95, 0.95, 0.95, 1.0), roughness=0.35)
    mat_roof_gravel = get_mat("Stewart_Roof_Membrane", (0.35, 0.34, 0.33, 1.0), roughness=0.85)
    mat_screen_emissive = get_mat("Stewart_Screen_Emissive", (0.95, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.95, 0.95, 1.0, 4.0))
    mat_warm_glow = get_mat("Stewart_Warm_Lamp_Glow", (1.0, 0.88, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.60, 5.0))
    
    # Book materials
    mat_b_red = get_mat("Stewart_Book_Red", (0.55, 0.08, 0.08, 1.0), roughness=0.6)
    mat_b_blue = get_mat("Stewart_Book_Blue", (0.08, 0.18, 0.50, 1.0), roughness=0.6)
    mat_b_gold = get_mat("Stewart_Book_Gold", (0.70, 0.55, 0.15, 1.0), roughness=0.5)
    mat_b_green = get_mat("Stewart_Book_Green", (0.08, 0.35, 0.12, 1.0), roughness=0.6)
    mat_b_leather = get_mat("Stewart_Book_Leather", (0.25, 0.15, 0.10, 1.0), roughness=0.6)
    book_mats = [mat_b_red, mat_b_blue, mat_b_gold, mat_b_green, mat_b_leather]

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

    # =========================================================================
    # PART 1: EXTERIOR ENVELOPES & MID-CENTURY FACADES (48_Stewart_Center_Exterior)
    # Bounds: X in [16.5, 151.3] (width 134.8m), Y in [-303.3, -211.0] (length 92.3m)
    # Height Z = 0 to 16.5m (Parapet coping at 16.5m), Fly Loft to 22.0m
    # =========================================================================
    print("Building Exterior Facades...")
    
    # 1. South Facade along State Street (Y = -303.3)
    make_box("STEW_Ext_Wall_South_West", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.35, 8.25), (66.0 - 16.5, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_South_East", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.35, 8.25), (151.3 - 102.0, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_South_Center_Upper", col_ext, (84.0, -303.3 + 0.35, 12.75), (36.0, 0.7, 7.5), mat_brick)

    # South Limestone Water Table Base (Z = 0.0 to 1.5m)
    make_box("STEW_Base_Limestone_South_W", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.3, 0.75), (66.0 - 16.5 + 0.2, 0.8, 1.5), mat_stone)
    make_box("STEW_Base_Limestone_South_E", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.3, 0.75), (151.3 - 102.0 + 0.2, 0.8, 1.5), mat_stone)

    # South Horizontal Limestone Beltcourses (Z = 4.2m, 8.4m, 12.6m, 16.5m coping)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_South_W_{z_c}", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.3, z_c), (66.0 - 16.5 + 0.2, 0.8, h_c), mat_stone)
        make_box(f"STEW_Beltcourse_South_E_{z_c}", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.3, z_c), (151.3 - 102.0 + 0.2, 0.8, h_c), mat_stone)
    make_box("STEW_Beltcourse_South_Center_Parapet", col_ext, (84.0, -303.3 + 0.3, 16.5), (36.2, 0.8, 0.4), mat_stone)

    # South Monumental Portico (Recessed entrance: X in [66.0, 102.0], Y from -303.3 to -297.0)
    make_box("STEW_Portico_Back_Wall", col_ext, (84.0, -297.0, 4.5), (36.0, 0.6, 9.0), mat_brick)
    make_box("STEW_Portico_Side_Wall_W", col_ext, (66.0 + 0.3, -300.15, 4.5), (0.6, 6.3, 9.0), mat_stone)
    make_box("STEW_Portico_Side_Wall_E", col_ext, (102.0 - 0.3, -300.15, 4.5), (0.6, 6.3, 9.0), mat_stone)
    make_box("STEW_Portico_Ceiling", col_ext, (84.0, -300.15, 9.0), (36.0, 6.3, 0.4), mat_stone)

    # 4 Monumental Limestone Colonnade Piers
    pier_xs = [68.0, 78.5, 89.5, 100.0]
    for i, px in enumerate(pier_xs):
        make_box(f"STEW_Portico_Pier_{i+1}", col_ext, (px, -303.3 + 0.5, 4.5), (1.4, 1.2, 9.0), mat_stone)
        make_box(f"STEW_Portico_Pier_Base_{i+1}", col_ext, (px, -303.3 + 0.5, 0.5), (1.6, 1.4, 1.0), mat_stone)
        make_box(f"STEW_Portico_Pier_Cap_{i+1}", col_ext, (px, -303.3 + 0.5, 8.7), (1.6, 1.4, 0.6), mat_stone)

    # South Entrance Glazing & Doors
    make_box("STEW_South_Entrance_Glazing", col_ext, (84.0, -297.0 + 0.1, 2.3), (28.0, 0.2, 4.2), mat_glass)
    for dx in [75.0, 84.0, 93.0]:
        make_box(f"STEW_South_Door_Frame_{dx}", col_ext, (dx, -297.0 - 0.05, 1.5), (3.4, 0.3, 3.0), mat_bronze)
        make_box(f"STEW_South_Door_Glass_{dx}", col_ext, (dx, -297.0 - 0.05, 1.5), (3.0, 0.1, 2.6), mat_glass)

    # Cantilevered Entrance Canopy at Z = 5.2m with Recessed Warm Downlights
    make_box("STEW_South_Canopy", col_ext, (84.0, -301.5, 5.2), (32.0, 8.0, 0.4), mat_stone)
    for cdx in [72.0, 78.0, 84.0, 90.0, 96.0]:
        for cdy in [-299.0, -302.0]:
            make_box(f"STEW_South_Canopy_Light_{cdx}_{int(abs(cdy))}", col_ext, (cdx, cdy, 5.0), (0.6, 0.6, 0.05), mat_warm_glow)

    # 3D Gold Building Lettering: "STEWART CENTER" on South Canopy Fascia
    make_box("STEW_South_Building_Lettering_Plaque", col_ext, (84.0, -305.55, 5.2), (18.0, 0.1, 0.7), mat_stone)
    try:
        font_curve = bpy.data.curves.new(type="FONT", name="STEW_Gold_Sign_Curve")
        font_curve.body = "STEWART CENTER"
        font_curve.size = 1.3
        font_curve.extrude = 0.06
        font_curve.bevel_depth = 0.015
        sign_obj = bpy.data.objects.new("STEW_South_Building_Lettering", font_curve)
        sign_obj.location = (75.5, -305.65, 4.85)
        sign_obj.rotation_euler = (math.radians(90), 0, 0)
        sign_obj.data.materials.append(mat_gold)
        col_ext.objects.link(sign_obj)
    except Exception as e:
        print(f"Sign text fallback: {e}")
        make_box("STEW_South_Building_Lettering_Text", col_ext, (84.0, -305.65, 5.2), (16.0, 0.05, 0.5), mat_gold)

    # South Facade Fenestration: Vertical Limestone Colonnade Fins and Ribbon Windows
    for seg_start, seg_end in [(20.0, 62.0), (106.0, 148.0)]:
        x_step = 6.0
        num_bays = int((seg_end - seg_start) / x_step)
        for b in range(num_bays):
            bx = seg_start + b * x_step + 3.0
            make_box(f"STEW_South_Fin_{int(bx)}", col_ext, (bx, -303.3 + 0.4, 8.5), (0.4, 0.9, 14.0), mat_stone)
            for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
                make_box(f"STEW_South_Win_{int(bx)}_{fl}", col_ext, (bx - 2.8, -303.3 + 0.35, fz), (4.8, 0.2, 2.2), mat_glass)
                make_box(f"STEW_South_Sill_{int(bx)}_{fl}", col_ext, (bx - 2.8, -303.3 + 0.35, fz - 1.15), (5.0, 0.4, 0.2), mat_stone)

    # 2. East Facade facing PMU West Courtyard (X = 151.3, Y in [-303.3, -211.0])
    make_box("STEW_Ext_Wall_East", col_ext, (151.3 - 0.35, -257.15, 8.25), (0.7, 92.3, 16.5), mat_brick)
    make_box("STEW_Base_Limestone_East", col_ext, (151.3 - 0.3, -257.15, 0.75), (0.8, 92.5, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_East_{z_c}", col_ext, (151.3 - 0.3, -257.15, z_c), (0.8, 92.5, h_c), mat_stone)

    # East Concourse Portal to PMU Courtyard
    make_box("STEW_East_Portal_Frame_S", col_ext, (151.3 + 0.1, -264.0, 2.1), (0.8, 0.8, 4.2), mat_stone)
    make_box("STEW_East_Portal_Frame_N", col_ext, (151.3 + 0.1, -244.0, 2.1), (0.8, 0.8, 4.2), mat_stone)
    make_box("STEW_East_Portal_Header", col_ext, (151.3 + 0.1, -254.0, 4.4), (0.8, 20.8, 0.6), mat_stone)
    make_box("STEW_East_Portal_Glazing", col_ext, (151.3 - 0.1, -254.0, 2.1), (0.2, 18.0, 3.8), mat_glass)
    make_box("STEW_East_Door_Bronze", col_ext, (151.3 + 0.05, -254.0, 1.4), (0.3, 4.0, 2.8), mat_bronze)

    for y_win in range(-295, -215, 7):
        if -266 <= y_win <= -242:
            continue
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box(f"STEW_East_Win_{y_win}_{fl}", col_ext, (151.3 - 0.35, y_win, fz), (0.2, 4.2, 2.2), mat_glass)
            make_box(f"STEW_East_Sill_{y_win}_{fl}", col_ext, (151.3 - 0.35, y_win, fz - 1.15), (0.4, 4.4, 0.2), mat_stone)

    # 3. West Facade facing University Hall Walkway (X = 16.5, Y in [-303.3, -211.0])
    make_box("STEW_Ext_Wall_West", col_ext, (16.5 + 0.35, -257.15, 8.25), (0.7, 92.3, 16.5), mat_brick)
    make_box("STEW_Base_Limestone_West", col_ext, (16.5 + 0.3, -257.15, 0.75), (0.8, 92.5, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_West_{z_c}", col_ext, (16.5 + 0.3, -257.15, z_c), (0.8, 92.5, h_c), mat_stone)
    for y_win in range(-295, -215, 7):
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box(f"STEW_West_Win_{y_win}_{fl}", col_ext, (16.5 + 0.35, y_win, fz), (0.2, 4.2, 2.2), mat_glass)
            make_box(f"STEW_West_Sill_{y_win}_{fl}", col_ext, (16.5 + 0.35, y_win, fz - 1.15), (0.4, 4.4, 0.2), mat_stone)

    # 4. North Facade facing Memorial Mall & Founders Park (Y = -211.0, X in [16.5, 151.3])
    make_box("STEW_Ext_Wall_North_West", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.35, 8.25), (55.0 - 16.5, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_North_East", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.35, 8.25), (151.3 - 115.0, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_North_Center_Upper", col_ext, (85.0, -211.0 - 0.35, 12.45), (60.0, 0.7, 8.1), mat_brick)
    
    make_box("STEW_Base_Limestone_North_W", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.3, 0.75), (55.0 - 16.5 + 0.2, 0.8, 1.5), mat_stone)
    make_box("STEW_Base_Limestone_North_E", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.3, 0.75), (151.3 - 115.0 + 0.2, 0.8, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_North_W_{z_c}", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.3, z_c), (55.0 - 16.5 + 0.2, 0.8, h_c), mat_stone)
        make_box(f"STEW_Beltcourse_North_E_{z_c}", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.3, z_c), (151.3 - 115.0 + 0.2, 0.8, h_c), mat_stone)
    make_box("STEW_Beltcourse_North_Center_Parapet", col_ext, (85.0, -211.0 - 0.3, 16.5), (60.2, 0.8, 0.4), mat_stone)

    # North 2-Story Glass Curtain Wall Entrance
    make_box("STEW_North_Grand_Curtain_Glass", col_ext, (85.0, -211.0 + 0.1, 4.2), (59.6, 0.2, 8.2), mat_glass)
    for gx in [55.0, 67.0, 79.0, 91.0, 103.0, 115.0]:
        make_box(f"STEW_North_Glass_Column_{gx}", col_ext, (gx, -211.0 - 0.2, 4.2), (0.8, 0.8, 8.4), mat_stone)
    
    # North Grand Entrance Canopy at Z = 4.5m
    make_box("STEW_North_Canopy", col_ext, (85.0, -208.5, 4.5), (28.0, 5.0, 0.35), mat_stone)
    # North 3D Gold Lettering facing Memorial Mall (Looking South, so body faces North)
    try:
        font_curve_n = bpy.data.curves.new(type="FONT", name="STEW_North_Sign_Curve")
        font_curve_n.body = "BOILERMAKER STATION"
        font_curve_n.size = 1.1
        font_curve_n.extrude = 0.06
        sign_n_obj = bpy.data.objects.new("STEW_North_Building_Lettering", font_curve_n)
        # Position on north fascia of canopy, facing north towards Memorial Mall
        sign_n_obj.location = (76.5, -211.1, 4.8)
        sign_n_obj.rotation_euler = (math.radians(90), 0, 0)
        sign_n_obj.data.materials.append(mat_gold)
        col_ext.objects.link(sign_n_obj)
    except Exception as e:
        print(f"North sign text fallback: {e}")

    for dx in [80.0, 85.0, 90.0]:
        make_box(f"STEW_North_Door_Bronze_{dx}", col_ext, (dx, -211.0 - 0.1, 1.4), (3.6, 0.3, 2.8), mat_bronze)
        make_box(f"STEW_North_Door_Glass_{dx}", col_ext, (dx, -211.0 - 0.1, 1.4), (3.2, 0.1, 2.4), mat_glass)

    # 5. Roof System, Fly Loft & Mechanical Penthouses
    make_box("STEW_Roof_Membrane_Main", col_ext, (83.89, -257.14, 16.3), (133.4, 90.8, 0.3), mat_roof_gravel)
    make_box("STEW_FlyLoft_Body", col_ext, (61.0, -254.0, 19.3), (26.0, 28.0, 5.8), mat_brick)
    make_box("STEW_FlyLoft_Coping", col_ext, (61.0, -254.0, 22.3), (26.6, 28.6, 0.4), mat_stone)
    for px in [48.0, 56.5, 65.5, 74.0]:
        make_box(f"STEW_FlyLoft_Pilaster_{px}", col_ext, (px, -254.0, 19.3), (0.6, 28.4, 5.8), mat_stone)

    make_box("STEW_Penthouse_East", col_ext, (118.0, -260.0, 18.3), (18.0, 22.0, 3.8), mat_stone)
    make_box("STEW_Penthouse_East_Louver", col_ext, (118.0, -248.9, 18.3), (16.0, 0.2, 2.8), mat_bronze)
    make_box("STEW_Penthouse_West", col_ext, (30.0, -260.0, 18.3), (14.0, 18.0, 3.8), mat_stone)
    make_box("STEW_Penthouse_West_Louver", col_ext, (30.0, -250.9, 18.3), (12.0, 0.2, 2.8), mat_bronze)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIORS (49_Stewart_Center_Interiors)
    # =========================================================================
    print("Building Photorealistic Interiors...")

    # -------------------------------------------------------------------------
    # 1. LOEB PLAYHOUSE (1,011-Seat Proscenium Theatre)
    # -------------------------------------------------------------------------
    print("Building Loeb Playhouse Proscenium Theatre...")
    make_box("Loeb_Interior_Wall_North", col_int, (52.0, -238.5, 6.0), (40.0, 0.5, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_South", col_int, (52.0, -277.5, 6.0), (40.0, 0.5, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_West", col_int, (32.5, -258.0, 6.0), (0.5, 39.0, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_East", col_int, (71.5, -258.0, 6.0), (0.5, 39.0, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Floor_Base", col_int, (52.0, -258.0, 0.05), (39.0, 38.0, 0.1), mat_navy_carpet)
    make_box("Loeb_Interior_Ceiling", col_int, (52.0, -258.0, 11.95), (39.0, 38.0, 0.1), mat_dark_oak)

    # Proscenium Stage Deck (tongue-and-groove dark oak)
    make_box("Loeb_Stage_Deck", col_int, (52.0, -244.5, 0.6), (24.0, 11.0, 1.2), mat_dark_oak)
    make_box("Loeb_Stage_Apron_Edge", col_int, (52.0, -250.1, 0.6), (24.4, 0.2, 1.25), mat_stone)
    # Proscenium Footlights
    for fx in range(42, 63, 2):
        make_box(f"Loeb_Footlight_{fx}", col_int, (fx, -250.0, 1.25), (0.4, 0.1, 0.05), mat_warm_glow)

    # Proscenium Arch
    make_box("Loeb_Proscenium_Jamb_L", col_int, (42.5, -249.8, 4.4), (3.0, 0.8, 6.4), mat_honey_oak)
    make_box("Loeb_Proscenium_Jamb_R", col_int, (61.5, -249.8, 4.4), (3.0, 0.8, 6.4), mat_honey_oak)
    make_box("Loeb_Proscenium_Header", col_int, (52.0, -249.8, 7.8), (22.0, 0.8, 1.2), mat_honey_oak)
    make_box("Loeb_Proscenium_Gold_Trim", col_int, (52.0, -249.9, 8.4), (22.4, 0.2, 0.3), mat_gold)
    # Central Gold Purdue Seal on Proscenium Arch
    make_box("Loeb_Proscenium_Seal", col_int, (52.0, -250.25, 7.8), (1.4, 0.1, 1.4), mat_gold)

    # Grand Stage Curtain in Rich Crimson Velvet
    make_box("Loeb_Curtain_Main", col_int, (52.0, -249.2, 4.3), (16.2, 0.2, 6.2), mat_crimson_velvet)
    make_box("Loeb_Curtain_Valance", col_int, (52.0, -249.4, 7.0), (16.6, 0.3, 1.0), mat_crimson_velvet)
    make_box("Loeb_Curtain_Swag_L", col_int, (44.5, -249.3, 4.3), (2.0, 0.4, 6.2), mat_crimson_velvet)
    make_box("Loeb_Curtain_Swag_R", col_int, (59.5, -249.3, 4.3), (2.0, 0.4, 6.2), mat_crimson_velvet)
    # Gold Tassel Tiebacks
    make_box("Loeb_Curtain_Tassel_L", col_int, (45.2, -249.5, 3.2), (0.2, 0.2, 0.8), mat_gold)
    make_box("Loeb_Curtain_Tassel_R", col_int, (58.8, -249.5, 3.2), (0.2, 0.2, 0.8), mat_gold)

    # Orchestra Seating: Stepped Riser Terraces (Risers only 0.18m high, treads 1.6m deep!)
    # Central Aisle (width 2.4m) at X = 52.0
    for t in range(12):
        ty = -252.0 - t * 1.7
        step_z = 0.1 + t * 0.16
        # Terrace base risers
        make_box(f"Loeb_Terrace_L_{t+1}", col_int, (42.5, ty, step_z - 0.08), (16.0, 1.65, 0.16), mat_navy_carpet)
        make_box(f"Loeb_Terrace_R_{t+1}", col_int, (61.5, ty, step_z - 0.08), (16.0, 1.65, 0.16), mat_navy_carpet)
        # Individual velvet cushioned theatre seats with armrests
        for seat_col in range(7):
            sx_l = 35.5 + seat_col * 2.1
            sx_r = 54.5 + seat_col * 2.1
            # Left seat
            make_box(f"Loeb_Seat_Base_L_{t+1}_{seat_col}", col_int, (sx_l, ty, step_z + 0.22), (0.85, 0.65, 0.44), mat_dark_oak)
            make_box(f"Loeb_Seat_Cushion_L_{t+1}_{seat_col}", col_int, (sx_l, ty - 0.05, step_z + 0.48), (0.8, 0.6, 0.12), mat_crimson_velvet)
            make_box(f"Loeb_Seat_Back_L_{t+1}_{seat_col}", col_int, (sx_l, ty - 0.32, step_z + 0.72), (0.8, 0.15, 0.5), mat_crimson_velvet)
            # Right seat
            make_box(f"Loeb_Seat_Base_R_{t+1}_{seat_col}", col_int, (sx_r, ty, step_z + 0.22), (0.85, 0.65, 0.44), mat_dark_oak)
            make_box(f"Loeb_Seat_Cushion_R_{t+1}_{seat_col}", col_int, (sx_r, ty - 0.05, step_z + 0.48), (0.8, 0.6, 0.12), mat_crimson_velvet)
            make_box(f"Loeb_Seat_Back_R_{t+1}_{seat_col}", col_int, (sx_r, ty - 0.32, step_z + 0.72), (0.8, 0.15, 0.5), mat_crimson_velvet)

    # Center Aisle Carpet Runner with Floor Track Lights
    make_box("Loeb_Aisle_Carpet", col_int, (52.0, -262.0, 0.06), (2.2, 22.0, 0.02), mat_navy_carpet)
    for ay in range(-253, -272, 3):
        make_box(f"Loeb_Aisle_Light_L_{ay}", col_int, (50.8, ay, 0.08), (0.1, 0.3, 0.02), mat_warm_glow)
        make_box(f"Loeb_Aisle_Light_R_{ay}", col_int, (53.2, ay, 0.08), (0.1, 0.3, 0.02), mat_warm_glow)

    # Cantilevered Balcony Level at South end
    make_box("Loeb_Balcony_Floor", col_int, (52.0, -272.5, 4.4), (36.0, 7.0, 0.4), mat_navy_carpet)
    make_box("Loeb_Balcony_Rail", col_int, (52.0, -269.0, 5.0), (36.0, 0.2, 0.8), mat_brass)
    for bt in range(3):
        bty = -270.5 - bt * 1.8
        btz = 4.6 + bt * 0.3
        make_box(f"Loeb_Balcony_Seats_{bt+1}", col_int, (52.0, bty, btz + 0.35), (34.0, 0.7, 0.7), mat_crimson_velvet)

    # Acoustic Ceiling Clouds & Theatrical Lighting
    for c_i, cy in enumerate([-247.0, -256.0, -265.0]):
        make_box(f"Loeb_Ceiling_Cloud_{c_i+1}", col_int, (52.0, cy, 10.2), (30.0, 5.0, 0.25), mat_honey_oak)
        for sx in [42.0, 48.0, 52.0, 56.0, 62.0]:
            make_box(f"Loeb_Spot_{c_i+1}_{sx}", col_int, (sx, cy, 10.05), (0.6, 0.6, 0.1), mat_warm_glow)

    # Theatrical Stage Lighting
    light_data_stage = bpy.data.lights.new(name="Loeb_Stage_Key_Data", type='POINT')
    light_data_stage.energy = 5500.0
    light_data_stage.color = (1.0, 0.90, 0.75)
    light_data_stage.shadow_soft_size = 0.8
    light_stage_obj = bpy.data.objects.new("Loeb_Stage_Key", light_data_stage)
    light_stage_obj.location = (52.0, -247.0, 8.5)
    col_int.objects.link(light_stage_obj)

    light_data_house = bpy.data.lights.new(name="Loeb_House_Wash_Data", type='POINT')
    light_data_house.energy = 3800.0
    light_data_house.color = (1.0, 0.94, 0.84)
    light_house_obj = bpy.data.objects.new("Loeb_House_Wash", light_data_house)
    light_house_obj.location = (52.0, -262.0, 7.5)
    col_int.objects.link(light_house_obj)

    # -------------------------------------------------------------------------
    # 2. HSSE LIBRARY (Humanities, Social Science and Education Library)
    # -------------------------------------------------------------------------
    print("Building HSSE Library Reading Hall & Book Stacks...")
    make_box("HSSE_Interior_Wall_South", col_int, (117.0, -246.0, 4.0), (58.0, 0.5, 8.0), mat_white_gallery)
    make_box("HSSE_Interior_Wall_West", col_int, (88.0, -230.5, 4.0), (0.5, 31.0, 8.0), mat_dark_oak)
    make_box("HSSE_Floor_Parquet", col_int, (117.0, -230.5, 0.05), (57.5, 30.5, 0.1), mat_honey_oak)
    make_box("HSSE_Ceiling", col_int, (117.0, -230.5, 7.95), (57.5, 30.5, 0.1), mat_white_gallery)

    # Navy Carpet Area Rugs under study clusters
    make_box("HSSE_Rug_West", col_int, (102.0, -230.0, 0.06), (24.0, 26.0, 0.02), mat_navy_carpet)

    # 6 Rows of Double-Sided Mahogany Book Stacks with Multi-Colored Books
    for s_i, sy in enumerate(range(-242, -218, 4)):
        make_box(f"HSSE_BookStack_{s_i+1}", col_int, (135.0, sy, 1.8), (18.0, 1.1, 3.4), mat_dark_oak)
        # 4 Shelving levels of realistic colored book spines
        for lvl_idx, lvl in enumerate([0.55, 1.25, 1.95, 2.65]):
            b_mat = book_mats[(s_i + lvl_idx) % len(book_mats)]
            make_box(f"HSSE_Books_{s_i+1}_{lvl_idx}_S", col_int, (135.0, sy - 0.48, lvl), (17.4, 0.22, 0.52), b_mat)
            b_mat2 = book_mats[(s_i + lvl_idx + 2) % len(book_mats)]
            make_box(f"HSSE_Books_{s_i+1}_{lvl_idx}_N", col_int, (135.0, sy + 0.48, lvl), (17.4, 0.22, 0.52), b_mat2)
        # Endcap brass aisle signage
        make_box(f"HSSE_Stack_Endcap_{s_i+1}", col_int, (125.8, sy, 2.4), (0.1, 0.8, 0.4), mat_brass)

    # Solid Honey Oak Collaborative Study Tables with Banker's Lamps & Laptops
    tbl_coords = [
        (96.0, -238.0), (108.0, -238.0),
        (96.0, -230.0), (108.0, -230.0),
        (96.0, -222.0), (108.0, -222.0)
    ]
    for i, (tx, ty) in enumerate(tbl_coords):
        # Oak tabletop
        make_box(f"HSSE_Table_{i+1}", col_int, (tx, ty, 0.74), (8.0, 3.2, 0.08), mat_honey_oak)
        # 4 Square Oak Legs
        for lx, ly in [(-3.8, -1.4), (3.8, -1.4), (-3.8, 1.4), (3.8, 1.4)]:
            make_box(f"HSSE_Leg_{i+1}_{lx}_{ly}", col_int, (tx + lx, ty + ly, 0.36), (0.16, 0.16, 0.72), mat_dark_oak)
        
        # 2 Classic Brass Banker's Lamps with glowing green glass shades
        for bx in [-2.0, 2.0]:
            make_box(f"HSSE_Lamp_Base_{i+1}_{bx}", col_int, (tx + bx, ty, 0.82), (0.28, 0.28, 0.06), mat_brass)
            make_box(f"HSSE_Lamp_Stem_{i+1}_{bx}", col_int, (tx + bx, ty, 1.05), (0.05, 0.05, 0.42), mat_brass)
            make_box(f"HSSE_Lamp_Shade_{i+1}_{bx}", col_int, (tx + bx, ty, 1.25), (0.48, 0.24, 0.14), mat_green_glass)
            make_box(f"HSSE_Lamp_Bulb_{i+1}_{bx}", col_int, (tx + bx, ty, 1.20), (0.36, 0.14, 0.06), mat_warm_glow)
        
        # Student Laptops & Open Books on Table
        for lx in [-2.5, 0.0, 2.5]:
            make_box(f"HSSE_Laptop_Base_{i+1}_{lx}", col_int, (tx + lx, ty - 0.8, 0.79), (0.42, 0.30, 0.02), mat_bronze)
            make_box(f"HSSE_Laptop_Screen_{i+1}_{lx}", col_int, (tx + lx, ty - 0.95, 0.95), (0.42, 0.02, 0.28), mat_screen_emissive)
            # Open textbook
            make_box(f"HSSE_OpenBook_{i+1}_{lx}", col_int, (tx + lx, ty + 0.8, 0.79), (0.40, 0.28, 0.03), mat_stone)

        # Ergonomic Oak Task Chairs (8 chairs per table)
        for cx in [-2.7, -0.9, 0.9, 2.7]:
            # South chair
            make_box(f"HSSE_Chair_S_{i+1}_{cx}", col_int, (tx + cx, ty - 1.2, 0.45), (0.55, 0.55, 0.85), mat_dark_oak)
            make_box(f"HSSE_Chair_Cushion_S_{i+1}_{cx}", col_int, (tx + cx, ty - 1.2, 0.48), (0.5, 0.5, 0.08), mat_navy_carpet)
            # North chair
            make_box(f"HSSE_Chair_N_{i+1}_{cx}", col_int, (tx + cx, ty + 1.2, 0.45), (0.55, 0.55, 0.85), mat_dark_oak)
            make_box(f"HSSE_Chair_Cushion_N_{i+1}_{cx}", col_int, (tx + cx, ty + 1.2, 0.48), (0.5, 0.5, 0.08), mat_navy_carpet)

    # Warm Library Ceiling Lighting
    light_data_lib = bpy.data.lights.new(name="HSSE_Main_Light_Data", type='POINT')
    light_data_lib.energy = 4500.0
    light_data_lib.color = (1.0, 0.94, 0.85)
    light_lib_obj = bpy.data.objects.new("HSSE_Main_Light", light_data_lib)
    light_lib_obj.location = (104.0, -230.0, 6.0)
    col_int.objects.link(light_lib_obj)

    # -------------------------------------------------------------------------
    # 3. ROBERT L. RINGEL GALLERY (Fine Arts Exhibition Hall)
    # -------------------------------------------------------------------------
    print("Building Robert L. Ringel Gallery...")
    make_box("Ringel_Floor_Terrazzo", col_int, (110.0, -263.0, 0.05), (55.0, 25.0, 0.1), mat_terrazzo)
    make_box("Ringel_Ceiling", col_int, (110.0, -263.0, 4.15), (55.0, 25.0, 0.1), mat_white_gallery)
    make_box("Ringel_Wall_South", col_int, (110.0, -275.5, 2.1), (55.0, 0.4, 4.0), mat_white_gallery)
    make_box("Ringel_Wall_North", col_int, (110.0, -250.5, 2.1), (55.0, 0.4, 4.0), mat_white_gallery)
    make_box("Ringel_Wall_East", col_int, (137.5, -263.0, 2.1), (0.4, 25.0, 4.0), mat_white_gallery)

    # Freestanding Museum Partition Exhibition Walls (Placed to allow open central circulation!)
    make_box("Ringel_Exhibition_Wall_1", col_int, (102.0, -269.0, 1.8), (0.4, 11.0, 3.4), mat_white_gallery)
    make_box("Ringel_Exhibition_Wall_2", col_int, (120.0, -257.0, 1.8), (0.4, 11.0, 3.4), mat_white_gallery)

    # Curated Large Canvas Oil Paintings on Gallery Walls
    paintings = [
        ("Ringel_Painting_S1", (94.0, -275.25, 2.2), (3.6, 0.1, 2.0)),
        ("Ringel_Painting_S2", (106.0, -275.25, 2.2), (4.2, 0.1, 2.2)),
        ("Ringel_Painting_S3", (122.0, -275.25, 2.2), (3.6, 0.1, 2.0)),
        ("Ringel_Painting_N1", (94.0, -250.75, 2.2), (4.0, 0.1, 2.0)),
        ("Ringel_Painting_N2", (110.0, -250.75, 2.2), (4.8, 0.1, 2.2)),
        ("Ringel_Painting_N3", (126.0, -250.75, 2.2), (3.6, 0.1, 2.0)),
        ("Ringel_Painting_Part1_W", (101.75, -269.0, 2.2), (0.1, 3.8, 2.0)),
        ("Ringel_Painting_Part2_E", (120.25, -257.0, 2.2), (0.1, 3.8, 2.0))
    ]
    for pname, ploc, psize in paintings:
        make_box(pname, col_int, ploc, psize, mat_gold)
        # Dedicated Picture Light Fixture
        make_box(f"{pname}_Light", col_int, (ploc[0], ploc[1], ploc[2] + psize[2]/2 + 0.22), (1.4, 0.2, 0.08), mat_brass)

    # 4 Minimalist White Display Pedestals with Modern Art Sculptures
    pedestal_coords = [
        (108.0, -264.0, mat_bronze),
        (114.0, -264.0, mat_stone),
        (126.0, -268.0, mat_bronze),
        (126.0, -260.0, mat_stone)
    ]
    for i, (px, py, sculp_mat) in enumerate(pedestal_coords):
        make_box(f"Ringel_Pedestal_{i+1}", col_int, (px, py, 0.6), (1.1, 1.1, 1.2), mat_white_gallery)
        make_box(f"Ringel_Sculpture_{i+1}", col_int, (px, py, 1.5), (0.55, 0.55, 0.65), sculp_mat)

    # Gallery Exhibition Title Header: "ROBERT L. RINGEL GALLERY"
    make_box("Ringel_Title_Board", col_int, (88.0, -263.0, 2.6), (0.2, 8.0, 1.2), mat_dark_oak)
    make_box("Ringel_Title_Gold", col_int, (88.15, -263.0, 2.6), (0.05, 7.6, 0.8), mat_gold)

    # Focused Gallery Track Lights
    for i, (gx, gy) in enumerate([(100.0, -263.0), (112.0, -264.0), (124.0, -263.0)]):
        g_data = bpy.data.lights.new(name=f"Ringel_Light_Data_{i+1}", type='POINT')
        g_data.energy = 2600.0
        g_data.color = (1.0, 0.96, 0.90)
        g_data.shadow_soft_size = 0.5
        g_obj = bpy.data.objects.new(f"Ringel_Light_{i+1}", g_data)
        g_obj.location = (gx, gy, 3.8)
        col_int.objects.link(g_obj)

    # -------------------------------------------------------------------------
    # 4. MAIN CIVIC CONCOURSE & BOILERMAKER STATION
    # -------------------------------------------------------------------------
    print("Building Main Concourse & Boilermaker Station...")
    make_box("STEW_Concourse_Floor", col_int, (79.0, -260.0, 0.05), (13.5, 70.0, 0.1), mat_terrazzo)
    make_box("STEW_Concourse_Ceiling", col_int, (79.0, -260.0, 4.15), (13.5, 70.0, 0.1), mat_white_gallery)

    # Boilermaker Station Reception Desk
    make_box("STEW_Welcome_Desk", col_int, (79.0, -230.0, 0.55), (6.0, 1.8, 1.1), mat_honey_oak)
    make_box("STEW_Welcome_Desk_Top", col_int, (79.0, -230.0, 1.12), (6.4, 2.0, 0.06), mat_terrazzo)
    make_box("STEW_Desk_Chair_1", col_int, (77.8, -228.8, 0.5), (0.6, 0.6, 0.9), mat_dark_oak)
    make_box("STEW_Desk_Chair_2", col_int, (80.2, -228.8, 0.5), (0.6, 0.6, 0.9), mat_dark_oak)
    # Digital information monitor
    make_box("STEW_Welcome_Screen", col_int, (79.0, -229.5, 1.4), (1.2, 0.1, 0.7), mat_screen_emissive)

    # Overhead Directional Signage Header
    make_box("STEW_Directional_Sign_Bar", col_int, (79.0, -245.0, 3.4), (10.0, 0.2, 0.7), mat_dark_oak)
    make_box("STEW_Directional_Sign_Face", col_int, (79.0, -245.15, 3.4), (9.8, 0.05, 0.6), mat_gold)

    # =========================================================================
    # PART 3: CIVIC PLAZA & SITE INTEGRATION (50_Stewart_Center_Plaza_and_Site)
    # =========================================================================
    print("Building Site & Plaza Integration...")

    # 1. North Memorial Mall Grand Terrace (Y in [-211.0, -195.0], X in [55.0, 115.0])
    make_box("STEW_North_Terrace_Paving", col_site, (85.0, -203.0, 0.18), (60.0, 16.0, 0.35), mat_stone)
    for step_i, sy in enumerate([-195.0, -194.2, -193.4]):
        make_box(f"STEW_North_Step_{step_i+1}", col_site, (85.0, sy, 0.25 - step_i * 0.1), (62.0, 0.8, 0.12), mat_stone)

    # Manicured Lawn Panels with Boxwood Hedges
    make_box("STEW_North_Lawn_West", col_site, (42.0, -203.0, 0.05), (24.0, 15.0, 0.1), mat_stone)
    make_box("STEW_North_Lawn_East", col_site, (128.0, -203.0, 0.05), (24.0, 15.0, 0.1), mat_stone)

    # Curved Limestone Seatwalls on North Terrace
    make_box("STEW_North_Seatwall_W", col_site, (62.0, -197.0, 0.55), (12.0, 0.6, 0.7), mat_stone)
    make_box("STEW_North_Seatwall_E", col_site, (108.0, -197.0, 0.55), (12.0, 0.6, 0.7), mat_stone)

    # Teak Wood Benches
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_dark_oak
    for bx in [70.0, 78.0, 92.0, 100.0]:
        make_box(f"STEW_North_Bench_{bx}", col_site, (bx, -197.5, 0.45), (2.4, 0.7, 0.55), bench_mat)

    # Victorian Cast-Iron Lantern Posts on North Terrace
    for lx in [60.0, 85.0, 110.0]:
        make_box(f"STEW_North_Lantern_Post_{lx}", col_site, (lx, -196.0, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box(f"STEW_North_Lantern_Head_{lx}", col_site, (lx, -196.0, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        l_data = bpy.data.lights.new(name=f"STEW_Lantern_Light_Data_{lx}", type='POINT')
        l_data.energy = 1600.0
        l_data.color = (1.0, 0.90, 0.75)
        l_obj = bpy.data.objects.new(f"STEW_Lantern_Light_{lx}", l_data)
        l_obj.location = (lx, -196.0, 4.2)
        col_site.objects.link(l_obj)

    # 2. South State Street Plaza & Sidewalk (Y in [-316.0, -303.3])
    make_box("STEW_South_Plaza_Paving", col_site, (85.0, -309.5, 0.05), (70.0, 12.5, 0.1), mat_plaza_brick)
    # Bank of 12 Sheffield Bicycle Racks
    for rx in range(58, 82, 2):
        make_box(f"STEW_Bike_Rack_{rx}", col_site, (rx, -310.0, 0.45), (0.1, 1.2, 0.9), mat_bronze)

    # Limestone Planter Beds along State Street
    make_box("STEW_South_Planter_W", col_site, (64.0, -313.5, 0.45), (18.0, 2.4, 0.7), mat_stone)
    make_box("STEW_South_Planter_E", col_site, (106.0, -313.5, 0.45), (18.0, 2.4, 0.7), mat_stone)

    # 3. East Concourse Walkway linking seamlessly to PMU West Courtyard
    make_box("STEW_PMU_Concourse_Connector", col_site, (158.5, -254.0, 0.05), (14.4, 28.0, 0.1), mat_concrete)

    # =========================================================================
    # PART 4: CALIBRATED INSPECTION CAMERAS (Using Vector Track-To Calculation)
    # =========================================================================
    print("Setting up 5 Precision-Calibrated Inspection Cameras...")

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

    # 1. Cam_72: South Hero State Street View
    # Sited on State Street sidewalk north of Hicks Library: (62.0, -315.0, 3.2) looking at portico & colonnade (84.0, -301.0, 6.5)
    set_camera("Cam_72_Stewart_South_Hero", (62.0, -315.0, 3.2), (84.0, -301.0, 6.5), lens=26.0)

    # 2. Cam_73: Loeb Playhouse Proscenium Theatre Interior
    # Orchestra aisle (52.0, -266.0, 2.2) looking at proscenium stage deck & crimson curtain (52.0, -244.0, 3.6)
    set_camera("Cam_73_Stewart_LoebPlayhouse_Interior", (52.0, -266.0, 2.2), (52.0, -244.0, 3.6), lens=24.0)

    # 3. Cam_74: HSSE Library Interior
    # Positioned at (98.0, -242.0, 2.0) looking across study tables and book stacks to (118.0, -230.0, 2.2)
    set_camera("Cam_74_Stewart_HSSE_Library_Interior", (98.0, -242.0, 2.0), (118.0, -230.0, 2.2), lens=22.0)

    # 4. Cam_75: Robert L. Ringel Gallery Interior
    # Positioned at (92.0, -270.0, 1.8) looking along gallery concourse at sculptures & art (112.0, -262.0, 2.0)
    set_camera("Cam_75_Stewart_RingelGallery_Interior", (92.0, -270.0, 1.8), (112.0, -262.0, 2.0), lens=24.0)

    # 5. Cam_76: Precinct Aerial View
    # Positioned high above Memorial Mall (35.0, -145.0, 48.0) looking SE at Stewart Center & PMU (100.0, -250.0, 10.0)
    set_camera("Cam_76_Stewart_North_Aerial", (35.0, -145.0, 48.0), (100.0, -250.0, 10.0), lens=28.0)

    print("=== Stewart Center Refinement Pass Complete! ===")

if __name__ == "__main__":
    run()
