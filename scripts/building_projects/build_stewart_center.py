"""
Build Purdue Stewart Center (STEW - 1958) Digital Twin
Complete Exterior, Loeb Playhouse Proscenium Theatre, HSSE Library,
Robert L. Ringel Gallery, Main Concourse, and Memorial Mall / State St Site Integration.
"""

import bpy
import math
import mathutils

def run():
    print("=== Starting Stewart Center (STEW) Digital Twin Build ===")
    
    # 1. Clean up old placeholder or existing STEW objects if any
    col_massing = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if col_massing:
        old_stew = bpy.data.objects.get("Stewart Center (STEW)")
        if old_stew:
            print(f"Removing old massing placeholder: {old_stew.name}")
            col_massing.objects.unlink(old_stew)
            bpy.data.objects.remove(old_stew, do_unlink=True)
            
    # Purge any previous Stewart Center collections to allow fresh, clean build
    for col_name in ["48_Stewart_Center_Exterior", "49_Stewart_Center_Interiors", "50_Stewart_Center_Plaza_and_Site"]:
        c = bpy.data.collections.get(col_name)
        if c:
            print(f"Purging existing collection: {col_name} ({len(c.objects)} objects)")
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(c)

    # Create dedicated collections
    col_ext = bpy.data.collections.new("48_Stewart_Center_Exterior")
    col_int = bpy.data.collections.new("49_Stewart_Center_Interiors")
    col_site = bpy.data.collections.new("50_Stewart_Center_Plaza_and_Site")
    
    bpy.context.scene.collection.children.link(col_ext)
    bpy.context.scene.collection.children.link(col_int)
    bpy.context.scene.collection.children.link(col_site)
    
    # Helper to get or create material
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

    # Materials
    mat_brick = bpy.data.materials.get("PMU_Red_Brick_Gothic") or get_mat("Stewart_Purdue_Red_Brick", (0.48, 0.16, 0.10, 1.0), roughness=0.75)
    mat_stone = bpy.data.materials.get("PMU_Bedford_Limestone") or get_mat("Stewart_Bedford_Limestone", (0.82, 0.80, 0.75, 1.0), roughness=0.55)
    mat_glass = bpy.data.materials.get("Parker_Solar_Curtain_Glass") or get_mat("Stewart_Solar_Curtain_Glass", (0.12, 0.22, 0.28, 0.85), roughness=0.08, specular=0.95)
    mat_gold = bpy.data.materials.get("PMU_Signage_Gold") or get_mat("Stewart_Signage_Gold", (0.95, 0.78, 0.22, 1.0), roughness=0.25, metallic=0.95)
    mat_bronze = bpy.data.materials.get("Beering_Architectural_Bronze_Metal") or get_mat("Stewart_Bronze_Metal", (0.28, 0.20, 0.14, 1.0), roughness=0.35, metallic=0.85)
    mat_dark_oak = bpy.data.materials.get("PMU_Dark_Oak_Timber") or get_mat("Stewart_Dark_Oak", (0.26, 0.15, 0.08, 1.0), roughness=0.35)
    mat_honey_oak = bpy.data.materials.get("Beering_Honey_Oak_Woodwork") or get_mat("Stewart_Honey_Oak", (0.55, 0.35, 0.18, 1.0), roughness=0.30)
    mat_terrazzo = bpy.data.materials.get("PMU_Dining_Terrazzo") or get_mat("Stewart_Polished_Terrazzo", (0.85, 0.84, 0.82, 1.0), roughness=0.15, specular=0.9)
    mat_crimson_velvet = bpy.data.materials.get("Elliott_Burgundy_Velvet") or get_mat("Stewart_Crimson_Velvet", (0.45, 0.04, 0.06, 1.0), roughness=0.85)
    mat_navy_carpet = bpy.data.materials.get("Beering_Vision21_Carpet_Navy") or get_mat("Stewart_Navy_Carpet", (0.05, 0.10, 0.22, 1.0), roughness=0.9)
    mat_concrete = bpy.data.materials.get("Campus_Walkway_Concrete") or get_mat("Stewart_Walkway_Concrete", (0.75, 0.74, 0.72, 1.0), roughness=0.6)
    mat_plaza_brick = bpy.data.materials.get("PMU_Plaza_Brick") or bpy.data.materials.get("Plaza_Purdue_Red_Brick_Pavers") or get_mat("Stewart_Plaza_Brick", (0.42, 0.15, 0.10, 1.0), roughness=0.7)
    mat_brass = get_mat("Stewart_Polished_Brass", (0.92, 0.75, 0.32, 1.0), roughness=0.2, metallic=0.9)
    mat_green_glass = get_mat("Stewart_Bankers_Green_Glass", (0.05, 0.35, 0.12, 0.9), roughness=0.1, specular=0.95)
    mat_white_gallery = get_mat("Stewart_Gallery_White", (0.94, 0.94, 0.94, 1.0), roughness=0.4)
    mat_roof_gravel = get_mat("Stewart_Roof_Membrane", (0.35, 0.34, 0.33, 1.0), roughness=0.85)
    mat_screen_emissive = get_mat("Stewart_Screen_Emissive", (0.95, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.9, 0.95, 1.0, 3.0))
    mat_warm_glow = get_mat("Stewart_Warm_Lamp_Glow", (1.0, 0.85, 0.55, 1.0), roughness=0.2, emission=(1.0, 0.85, 0.55, 4.0))

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
    # PART 1: EXTERIOR ARCHITECTURE (48_Stewart_Center_Exterior)
    # Bounds: X in [16.5, 151.3] (width 134.8m), Y in [-303.3, -211.0] (length 92.3m)
    # Height Z = 0 to 16.5m (Parapet coping at 16.5m), Stage Fly Loft to 22.0m
    # =========================================================================
    print("Building Part 1: Stewart Center Exterior Envelopes & Facades...")

    # True Hollow Perimeter Architectural Envelopes:
    # 1. South Wall along State Street (Y = -303.3)
    # Split into West, Center Entrance, and East sections
    make_box("STEW_Ext_Wall_South_West", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.35, 8.25), (66.0 - 16.5, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_South_East", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.35, 8.25), (151.3 - 102.0, 0.7, 16.5), mat_brick)
    # Upper South Center Wall above the portico (Z = 9.0 to 16.5)
    make_box("STEW_Ext_Wall_South_Center_Upper", col_ext, (84.0, -303.3 + 0.35, 12.75), (36.0, 0.7, 7.5), mat_brick)
    
    # South Limestone Water Table (Z = 0.0 to 1.5)
    make_box("STEW_Base_Limestone_South_W", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.3, 0.75), (66.0 - 16.5 + 0.2, 0.8, 1.5), mat_stone)
    make_box("STEW_Base_Limestone_South_E", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.3, 0.75), (151.3 - 102.0 + 0.2, 0.8, 1.5), mat_stone)

    # South Horizontal Limestone Beltcourses (Z = 4.2m, 8.4m, 12.6m, 16.5m coping)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_South_W_{z_c}", col_ext, ((16.5 + 66.0)/2, -303.3 + 0.3, z_c), (66.0 - 16.5 + 0.2, 0.8, h_c), mat_stone)
        make_box(f"STEW_Beltcourse_South_E_{z_c}", col_ext, ((102.0 + 151.3)/2, -303.3 + 0.3, z_c), (151.3 - 102.0 + 0.2, 0.8, h_c), mat_stone)
    make_box("STEW_Beltcourse_South_Center_Parapet", col_ext, (84.0, -303.3 + 0.3, 16.5), (36.2, 0.8, 0.4), mat_stone)

    # South Monumental Portico (Recessed entrance: X in [66.0, 102.0], Y from -303.3 to -297.0)
    # Recessed back wall of portico
    make_box("STEW_Portico_Back_Wall", col_ext, (84.0, -297.0, 4.5), (36.0, 0.6, 9.0), mat_brick)
    make_box("STEW_Portico_Side_Wall_W", col_ext, (66.0 + 0.3, -300.15, 4.5), (0.6, 6.3, 9.0), mat_stone)
    make_box("STEW_Portico_Side_Wall_E", col_ext, (102.0 - 0.3, -300.15, 4.5), (0.6, 6.3, 9.0), mat_stone)
    # Portico ceiling / soffit at Z = 9.0
    make_box("STEW_Portico_Ceiling", col_ext, (84.0, -300.15, 9.0), (36.0, 6.3, 0.4), mat_stone)
    # Monumental 4 Limestone Fluted Colonnade Piers along South Facade
    pier_xs = [68.0, 78.5, 89.5, 100.0]
    for i, px in enumerate(pier_xs):
        make_box(f"STEW_Portico_Pier_{i+1}", col_ext, (px, -303.3 + 0.5, 4.5), (1.4, 1.2, 9.0), mat_stone)
        # Pier base plinth & capital
        make_box(f"STEW_Portico_Pier_Base_{i+1}", col_ext, (px, -303.3 + 0.5, 0.5), (1.6, 1.4, 1.0), mat_stone)
        make_box(f"STEW_Portico_Pier_Cap_{i+1}", col_ext, (px, -303.3 + 0.5, 8.7), (1.6, 1.4, 0.6), mat_stone)

    # Entrance Glazed Portal at back wall (Y = -297.0, Z = 0 to 4.2)
    make_box("STEW_South_Entrance_Glazing", col_ext, (84.0, -297.0 + 0.1, 2.3), (28.0, 0.2, 4.2), mat_glass)
    # Triple Double Bronze Entrance Doors
    for dx in [75.0, 84.0, 93.0]:
        make_box(f"STEW_South_Door_Frame_{dx}", col_ext, (dx, -297.0 - 0.05, 1.5), (3.4, 0.3, 3.0), mat_bronze)
        make_box(f"STEW_South_Door_Glass_{dx}", col_ext, (dx, -297.0 - 0.05, 1.5), (3.0, 0.1, 2.6), mat_glass)

    # Cantilevered Entrance Canopy at Z = 5.2m
    make_box("STEW_South_Canopy", col_ext, (84.0, -301.5, 5.2), (32.0, 8.0, 0.4), mat_stone)
    # 3D Gold Building Lettering: "STEWART CENTER"
    try:
        font_curve = bpy.data.curves.new(type="FONT", name="STEW_Gold_Sign_Curve")
        font_curve.body = "STEWART CENTER"
        font_curve.size = 1.6
        font_curve.extrude = 0.08
        font_curve.bevel_depth = 0.02
        sign_obj = bpy.data.objects.new("STEW_South_Building_Lettering", font_curve)
        sign_obj.location = (74.0, -303.55, 6.2)
        sign_obj.rotation_euler = (math.radians(90), 0, 0)
        sign_obj.data.materials.append(mat_gold)
        col_ext.objects.link(sign_obj)
    except Exception as e:
        print(f"Sign text fallback: {e}")
        make_box("STEW_South_Building_Lettering_Plaque", col_ext, (84.0, -303.55, 6.5), (20.0, 0.1, 1.6), mat_gold)

    # South Facade Fenestration: Vertical Limestone Fins and Window Ribbons
    # West section: X in [20, 62], East section: X in [106, 148]
    for seg_start, seg_end in [(20.0, 62.0), (106.0, 148.0)]:
        x_step = 6.0
        num_bays = int((seg_end - seg_start) / x_step)
        for b in range(num_bays):
            bx = seg_start + b * x_step + 3.0
            # Limestone vertical fin
            make_box(f"STEW_South_Fin_{int(bx)}", col_ext, (bx, -303.3 + 0.4, 8.5), (0.4, 0.9, 14.0), mat_stone)
            # Window ribbons at Floors 1, 2, 3
            for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
                make_box(f"STEW_South_Win_{int(bx)}_{fl}", col_ext, (bx - 2.8, -303.3 + 0.35, fz), (4.8, 0.2, 2.2), mat_glass)
                make_box(f"STEW_South_Sill_{int(bx)}_{fl}", col_ext, (bx - 2.8, -303.3 + 0.35, fz - 1.15), (5.0, 0.4, 0.2), mat_stone)

    # 2. East Facade facing PMU West Courtyard (X = 151.3, Y in [-303.3, -211.0])
    print("Building East Facade facing PMU West Courtyard...")
    make_box("STEW_Ext_Wall_East", col_ext, (151.3 - 0.35, -257.15, 8.25), (0.7, 92.3, 16.5), mat_brick)
    make_box("STEW_Base_Limestone_East", col_ext, (151.3 - 0.3, -257.15, 0.75), (0.8, 92.5, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_East_{z_c}", col_ext, (151.3 - 0.3, -257.15, z_c), (0.8, 92.5, h_c), mat_stone)

    # East Ground Floor Covered Concourse Portal to PMU Courtyard (Y in [-264.0, -244.0], Z = 0 to 4.2)
    # Open arcade portal with limestone framing
    make_box("STEW_East_Portal_Frame_S", col_ext, (151.3 + 0.1, -264.0, 2.1), (0.8, 0.8, 4.2), mat_stone)
    make_box("STEW_East_Portal_Frame_N", col_ext, (151.3 + 0.1, -244.0, 2.1), (0.8, 0.8, 4.2), mat_stone)
    make_box("STEW_East_Portal_Header", col_ext, (151.3 + 0.1, -254.0, 4.4), (0.8, 20.8, 0.6), mat_stone)
    make_box("STEW_East_Portal_Glazing", col_ext, (151.3 - 0.1, -254.0, 2.1), (0.2, 18.0, 3.8), mat_glass)
    # Double bronze entrance doors
    make_box("STEW_East_Door_Bronze", col_ext, (151.3 + 0.05, -254.0, 1.4), (0.3, 4.0, 2.8), mat_bronze)

    # East Facade Fenestration bays
    for y_win in range(-295, -215, 7):
        if -266 <= y_win <= -242:
            continue
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box(f"STEW_East_Win_{y_win}_{fl}", col_ext, (151.3 - 0.35, y_win, fz), (0.2, 4.2, 2.2), mat_glass)
            make_box(f"STEW_East_Sill_{y_win}_{fl}", col_ext, (151.3 - 0.35, y_win, fz - 1.15), (0.4, 4.4, 0.2), mat_stone)

    # 3. West Facade facing University Hall Walkway (X = 16.5, Y in [-303.3, -211.0])
    print("Building West Facade...")
    make_box("STEW_Ext_Wall_West", col_ext, (16.5 + 0.35, -257.15, 8.25), (0.7, 92.3, 16.5), mat_brick)
    make_box("STEW_Base_Limestone_West", col_ext, (16.5 + 0.3, -257.15, 0.75), (0.8, 92.5, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_West_{z_c}", col_ext, (16.5 + 0.3, -257.15, z_c), (0.8, 92.5, h_c), mat_stone)
    # West fenestration bays
    for y_win in range(-295, -215, 7):
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box(f"STEW_West_Win_{y_win}_{fl}", col_ext, (16.5 + 0.35, y_win, fz), (0.2, 4.2, 2.2), mat_glass)
            make_box(f"STEW_West_Sill_{y_win}_{fl}", col_ext, (16.5 + 0.35, y_win, fz - 1.15), (0.4, 4.4, 0.2), mat_stone)

    # 4. North Facade facing Memorial Mall & Founders Park (Y = -211.0, X in [16.5, 151.3])
    print("Building North Facade facing Memorial Mall...")
    # Split into West, Central Grand Entrance, and East sections
    make_box("STEW_Ext_Wall_North_West", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.35, 8.25), (55.0 - 16.5, 0.7, 16.5), mat_brick)
    make_box("STEW_Ext_Wall_North_East", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.35, 8.25), (151.3 - 115.0, 0.7, 16.5), mat_brick)
    # Upper North Center Wall above the grand 2-story glass pavilion (Z = 8.4 to 16.5)
    make_box("STEW_Ext_Wall_North_Center_Upper", col_ext, (85.0, -211.0 - 0.35, 12.45), (60.0, 0.7, 8.1), mat_brick)
    
    make_box("STEW_Base_Limestone_North_W", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.3, 0.75), (55.0 - 16.5 + 0.2, 0.8, 1.5), mat_stone)
    make_box("STEW_Base_Limestone_North_E", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.3, 0.75), (151.3 - 115.0 + 0.2, 0.8, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box(f"STEW_Beltcourse_North_W_{z_c}", col_ext, ((16.5 + 55.0)/2, -211.0 - 0.3, z_c), (55.0 - 16.5 + 0.2, 0.8, h_c), mat_stone)
        make_box(f"STEW_Beltcourse_North_E_{z_c}", col_ext, ((115.0 + 151.3)/2, -211.0 - 0.3, z_c), (151.3 - 115.0 + 0.2, 0.8, h_c), mat_stone)
    make_box("STEW_Beltcourse_North_Center_Parapet", col_ext, (85.0, -211.0 - 0.3, 16.5), (60.2, 0.8, 0.4), mat_stone)

    # North 2-Story Glass Curtain Wall Entrance (Boilermaker Station & Memorial Mall Welcome Portal)
    # X in [55.0, 115.0], Y = -211.0, Z = 0.0 to 8.4m
    make_box("STEW_North_Grand_Curtain_Glass", col_ext, (85.0, -211.0 + 0.1, 4.2), (59.6, 0.2, 8.2), mat_glass)
    # Structural limestone columns framing the 2-story glass pavilion
    for gx in [55.0, 67.0, 79.0, 91.0, 103.0, 115.0]:
        make_box(f"STEW_North_Glass_Column_{gx}", col_ext, (gx, -211.0 - 0.2, 4.2), (0.8, 0.8, 8.4), mat_stone)
    # North Grand Entrance Canopy at Z = 4.5m
    make_box("STEW_North_Canopy", col_ext, (85.0, -208.5, 4.5), (28.0, 5.0, 0.35), mat_stone)
    # North 3D Gold Lettering: "BOILERMAKER STATION WELCOME CENTER"
    try:
        font_curve_n = bpy.data.curves.new(type="FONT", name="STEW_North_Sign_Curve")
        font_curve_n.body = "BOILERMAKER STATION"
        font_curve_n.size = 1.1
        font_curve_n.extrude = 0.06
        sign_n_obj = bpy.data.objects.new("STEW_North_Building_Lettering", font_curve_n)
        sign_n_obj.location = (74.0, -206.1, 4.8)
        sign_n_obj.rotation_euler = (math.radians(90), 0, 0)
        sign_n_obj.data.materials.append(mat_gold)
        col_ext.objects.link(sign_n_obj)
    except Exception as e:
        print(f"North sign text fallback: {e}")

    # Triple North Entrance Bronze Doors
    for dx in [80.0, 85.0, 90.0]:
        make_box(f"STEW_North_Door_Bronze_{dx}", col_ext, (dx, -211.0 - 0.1, 1.4), (3.6, 0.3, 2.8), mat_bronze)
        make_box(f"STEW_North_Door_Glass_{dx}", col_ext, (dx, -211.0 - 0.1, 1.4), (3.2, 0.1, 2.4), mat_glass)

    # 5. Roof System, Fly Loft & Mechanical Penthouses
    print("Building Roof System, Fly Loft & HVAC Penthouses...")
    # Flat main gravel roof membrane at Z = 16.3m
    make_box("STEW_Roof_Membrane_Main", col_ext, (83.89, -257.14, 16.3), (133.4, 90.8, 0.3), mat_roof_gravel)
    
    # Central Loeb Playhouse Stage Fly Loft Tower (Stage House)
    # X in [48.0, 74.0], Y in [-268.0, -240.0], Z = 16.4 to 22.2m (height 5.8m above roof)
    make_box("STEW_FlyLoft_Body", col_ext, (61.0, -254.0, 19.3), (26.0, 28.0, 5.8), mat_brick)
    make_box("STEW_FlyLoft_Coping", col_ext, (61.0, -254.0, 22.3), (26.6, 28.6, 0.4), mat_stone)
    # Fly loft vertical brick pilasters
    for px in [48.0, 56.5, 65.5, 74.0]:
        make_box(f"STEW_FlyLoft_Pilaster_{px}", col_ext, (px, -254.0, 19.3), (0.6, 28.4, 5.8), mat_stone)

    # Mechanical Penthouses with bronze HVAC louvers
    make_box("STEW_Penthouse_East", col_ext, (118.0, -260.0, 18.3), (18.0, 22.0, 3.8), mat_stone)
    make_box("STEW_Penthouse_East_Louver", col_ext, (118.0, -248.9, 18.3), (16.0, 0.2, 2.8), mat_bronze)
    make_box("STEW_Penthouse_West", col_ext, (30.0, -260.0, 18.3), (14.0, 18.0, 3.8), mat_stone)
    make_box("STEW_Penthouse_West_Louver", col_ext, (30.0, -250.9, 18.3), (12.0, 0.2, 2.8), mat_bronze)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIOR ARCHITECTURE (49_Stewart_Center_Interiors)
    # 1. Loeb Playhouse (1,011-Seat Proscenium Theatre)
    # 2. HSSE Library (Humanities, Social Science and Education Library)
    # 3. Robert L. Ringel Gallery (Fine Arts Exhibition Hall)
    # 4. Main Concourse & Boilermaker Station
    # =========================================================================
    print("Building Part 2: Stewart Center Photorealistic Interiors...")

    # -------------------------------------------------------------------------
    # Interior Destination 1: LOEB PLAYHOUSE (The 1,011-Seat Proscenium Theatre)
    # Enclosure: X in [32.0, 72.0], Y in [-278.0, -238.0], Z = 0.0 to 12.0m
    # -------------------------------------------------------------------------
    print("Building Loeb Playhouse Interior...")
    # Interior acoustic shell walls
    make_box("Loeb_Interior_Wall_North", col_int, (52.0, -238.5, 6.0), (40.0, 0.5, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_South", col_int, (52.0, -277.5, 6.0), (40.0, 0.5, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_West", col_int, (32.5, -258.0, 6.0), (0.5, 39.0, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Wall_East", col_int, (71.5, -258.0, 6.0), (0.5, 39.0, 12.0), mat_dark_oak)
    make_box("Loeb_Interior_Floor_Base", col_int, (52.0, -258.0, 0.05), (39.0, 38.0, 0.1), mat_navy_carpet)
    make_box("Loeb_Interior_Ceiling", col_int, (52.0, -258.0, 11.95), (39.0, 38.0, 0.1), mat_dark_oak)

    # Proscenium Stage Deck (North end: Y in [-250.0, -239.0], X in [40.0, 64.0], Z = 0.0 to 1.2m)
    make_box("Loeb_Stage_Deck", col_int, (52.0, -244.5, 0.6), (24.0, 11.0, 1.2), mat_dark_oak)
    make_box("Loeb_Stage_Apron_Edge", col_int, (52.0, -250.1, 0.6), (24.4, 0.2, 1.25), mat_stone)

    # Proscenium Arch (at Y = -249.8, opening width 16.0m, height 6.5m)
    # Left jamb, right jamb, header beam
    make_box("Loeb_Proscenium_Jamb_L", col_int, (42.5, -249.8, 4.4), (3.0, 0.8, 6.4), mat_honey_oak)
    make_box("Loeb_Proscenium_Jamb_R", col_int, (61.5, -249.8, 4.4), (3.0, 0.8, 6.4), mat_honey_oak)
    make_box("Loeb_Proscenium_Header", col_int, (52.0, -249.8, 7.8), (22.0, 0.8, 1.2), mat_honey_oak)
    make_box("Loeb_Proscenium_Gold_Trim", col_int, (52.0, -249.9, 8.4), (22.4, 0.2, 0.3), mat_gold)

    # Grand Stage Curtain in Rich Crimson Velvet (Y = -249.2, Z = 1.2 to 7.4m)
    # Pleated look via multiple layered boxes
    make_box("Loeb_Curtain_Main", col_int, (52.0, -249.2, 4.3), (16.2, 0.2, 6.2), mat_crimson_velvet)
    make_box("Loeb_Curtain_Valance", col_int, (52.0, -249.4, 7.0), (16.6, 0.3, 1.0), mat_crimson_velvet)
    # Left and Right gathered curtain swags
    make_box("Loeb_Curtain_Swag_L", col_int, (44.5, -249.3, 4.3), (2.0, 0.4, 6.2), mat_crimson_velvet)
    make_box("Loeb_Curtain_Swag_R", col_int, (59.5, -249.3, 4.3), (2.0, 0.4, 6.2), mat_crimson_velvet)

    # Orchestra Seating Bowl: 12 Stepped Tiers sloping up from Y = -252.0 to -274.0
    # Central Aisle (width 2.2m) at X = 52.0
    for t in range(12):
        ty = -252.0 - t * 1.8
        tz = 0.2 + t * 0.22
        # Left Seating Tier (X from 35.0 to 50.8)
        make_box(f"Loeb_Tier_L_{t+1}", col_int, (42.9, ty, tz/2), (15.8, 1.7, tz), mat_navy_carpet)
        # Right Seating Tier (X from 53.2 to 69.0)
        make_box(f"Loeb_Tier_R_{t+1}", col_int, (61.1, ty, tz/2), (15.8, 1.7, tz), mat_navy_carpet)
        # Velvet Theatre Seats (continuous curved bank)
        make_box(f"Loeb_Seats_L_{t+1}", col_int, (42.9, ty, tz + 0.45), (15.4, 0.7, 0.75), mat_crimson_velvet)
        make_box(f"Loeb_Seats_R_{t+1}", col_int, (61.1, ty, tz + 0.45), (15.4, 0.7, 0.75), mat_crimson_velvet)

    # Balcony Level at South end (Y in [-276.0, -266.0], Z = 4.8 to 7.0m)
    make_box("Loeb_Balcony_Floor", col_int, (52.0, -271.0, 4.6), (36.0, 10.0, 0.4), mat_navy_carpet)
    make_box("Loeb_Balcony_Rail", col_int, (52.0, -266.0, 5.2), (36.0, 0.2, 0.8), mat_brass)
    # Balcony 4 Seating Tiers
    for bt in range(4):
        bty = -267.5 - bt * 2.0
        btz = 4.8 + bt * 0.35
        make_box(f"Loeb_Balcony_Tier_{bt+1}", col_int, (52.0, bty, btz - 0.15), (34.0, 1.8, 0.3), mat_navy_carpet)
        make_box(f"Loeb_Balcony_Seats_{bt+1}", col_int, (52.0, bty, btz + 0.35), (33.6, 0.7, 0.7), mat_crimson_velvet)

    # Suspended Acoustic Ceiling Clouds/Baffles
    for c_i, cy in enumerate([-248.0, -256.0, -265.0]):
        make_box(f"Loeb_Ceiling_Cloud_{c_i+1}", col_int, (52.0, cy, 10.2), (30.0, 5.0, 0.25), mat_honey_oak)
        # Recessed warm theatrical stage and house spotlights
        for sx in [42.0, 48.0, 52.0, 56.0, 62.0]:
            make_box(f"Loeb_Spot_{c_i+1}_{sx}", col_int, (sx, cy, 10.05), (0.6, 0.6, 0.1), mat_warm_glow)

    # Theatrical Stage Lighting: 2 Dedicated Point Lights aimed at stage
    light_data_stage = bpy.data.lights.new(name="Loeb_Stage_Light_Data", type='POINT')
    light_data_stage.energy = 4500.0
    light_data_stage.color = (1.0, 0.88, 0.70)
    light_data_stage.shadow_soft_size = 1.0
    light_stage_obj = bpy.data.objects.new("Loeb_Stage_Light", light_data_stage)
    light_stage_obj.location = (52.0, -248.0, 8.5)
    col_int.objects.link(light_stage_obj)

    light_data_house = bpy.data.lights.new(name="Loeb_House_Light_Data", type='POINT')
    light_data_house.energy = 3000.0
    light_data_house.color = (1.0, 0.92, 0.80)
    light_house_obj = bpy.data.objects.new("Loeb_House_Light", light_data_house)
    light_house_obj.location = (52.0, -262.0, 8.0)
    col_int.objects.link(light_house_obj)

    # -------------------------------------------------------------------------
    # Interior Destination 2: HSSE LIBRARY (Humanities, Social Science and Education)
    # Enclosure: X in [88.0, 146.0], Y in [-246.0, -215.0], Z = 0.0 to 8.0m
    # -------------------------------------------------------------------------
    print("Building HSSE Library Interior...")
    # Interior library partitions
    make_box("HSSE_Interior_Wall_South", col_int, (117.0, -246.0, 4.0), (58.0, 0.5, 8.0), mat_white_gallery)
    make_box("HSSE_Interior_Wall_West", col_int, (88.0, -230.5, 4.0), (0.5, 31.0, 8.0), mat_dark_oak)
    make_box("HSSE_Floor_Parquet", col_int, (117.0, -230.5, 0.05), (57.5, 30.5, 0.1), mat_honey_oak)
    make_box("HSSE_Ceiling", col_int, (117.0, -230.5, 7.95), (57.5, 30.5, 0.1), mat_white_gallery)

    # 6 Rows of Double-Sided Walnut Book Stacks / Shelving Units (X in [124.0, 144.0])
    for s_i, sy in enumerate(range(-242, -218, 4)):
        make_box(f"HSSE_BookStack_{s_i+1}", col_int, (134.0, sy, 1.8), (18.0, 1.2, 3.4), mat_dark_oak)
        # Shelving rows / book spines
        for lvl in [0.6, 1.3, 2.0, 2.7]:
            make_box(f"HSSE_Books_{s_i+1}_{lvl}_S", col_int, (134.0, sy - 0.55, lvl), (17.4, 0.25, 0.55), mat_stone)
            make_box(f"HSSE_Books_{s_i+1}_{lvl}_N", col_int, (134.0, sy + 0.55, lvl), (17.4, 0.25, 0.55), mat_stone)

    # Collaborative Honey Oak Study Tables with Green Banker's Lamps (X in [92.0, 120.0])
    tbl_positions = [
        (96.0, -238.0), (108.0, -238.0),
        (96.0, -230.0), (108.0, -230.0),
        (96.0, -222.0), (108.0, -222.0)
    ]
    for i, (tx, ty) in enumerate(tbl_positions):
        # Oak study table
        make_box(f"HSSE_Study_Table_{i+1}", col_int, (tx, ty, 0.75), (8.0, 3.2, 0.08), mat_honey_oak)
        # 4 Table legs
        for lx, ly in [(-3.8, -1.4), (3.8, -1.4), (-3.8, 1.4), (3.8, 1.4)]:
            make_box(f"HSSE_Table_Leg_{i+1}_{lx}_{ly}", col_int, (tx + lx, ty + ly, 0.37), (0.15, 0.15, 0.74), mat_dark_oak)
        # 2 Classic Brass Banker's Lamps with Green Glass Shades per table
        for bx in [-2.0, 2.0]:
            make_box(f"HSSE_Bankers_Lamp_Base_{i+1}_{bx}", col_int, (tx + bx, ty, 0.82), (0.25, 0.25, 0.06), mat_brass)
            make_box(f"HSSE_Bankers_Lamp_Stem_{i+1}_{bx}", col_int, (tx + bx, ty, 1.05), (0.05, 0.05, 0.4), mat_brass)
            make_box(f"HSSE_Bankers_Lamp_Shade_{i+1}_{bx}", col_int, (tx + bx, ty, 1.25), (0.45, 0.25, 0.12), mat_green_glass)
            make_box(f"HSSE_Bankers_Lamp_Bulb_{i+1}_{bx}", col_int, (tx + bx, ty, 1.20), (0.35, 0.15, 0.05), mat_warm_glow)
        # Ergonomic Study Task Chairs (4 chairs per side = 8 per table)
        for cx in [-2.7, -0.9, 0.9, 2.7]:
            make_box(f"HSSE_Chair_S_{i+1}_{cx}", col_int, (tx + cx, ty - 1.2, 0.45), (0.6, 0.6, 0.8), mat_dark_oak)
            make_box(f"HSSE_Chair_N_{i+1}_{cx}", col_int, (tx + cx, ty + 1.2, 0.45), (0.6, 0.6, 0.8), mat_dark_oak)

    # Library Point Light for warm study illumination
    light_data_lib = bpy.data.lights.new(name="HSSE_Study_Light_Data", type='POINT')
    light_data_lib.energy = 3500.0
    light_data_lib.color = (1.0, 0.94, 0.85)
    light_lib_obj = bpy.data.objects.new("HSSE_Study_Light", light_data_lib)
    light_lib_obj.location = (102.0, -230.0, 5.5)
    col_int.objects.link(light_lib_obj)

    # -------------------------------------------------------------------------
    # Interior Destination 3: ROBERT L. RINGEL GALLERY (Fine Arts Exhibition Hall)
    # Enclosure: X in [82.0, 138.0], Y in [-276.0, -250.0], Z = 0.0 to 4.2m
    # -------------------------------------------------------------------------
    print("Building Robert L. Ringel Gallery Interior...")
    make_box("Ringel_Floor_Terrazzo", col_int, (110.0, -263.0, 0.05), (55.0, 25.0, 0.1), mat_terrazzo)
    make_box("Ringel_Ceiling", col_int, (110.0, -263.0, 4.15), (55.0, 25.0, 0.1), mat_white_gallery)
    make_box("Ringel_Wall_South", col_int, (110.0, -275.5, 2.1), (55.0, 0.4, 4.0), mat_white_gallery)
    make_box("Ringel_Wall_North", col_int, (110.0, -250.5, 2.1), (55.0, 0.4, 4.0), mat_white_gallery)

    # Freestanding Museum Partition Exhibition Walls
    make_box("Ringel_Exhibition_Wall_1", col_int, (98.0, -263.0, 1.8), (0.4, 14.0, 3.4), mat_white_gallery)
    make_box("Ringel_Exhibition_Wall_2", col_int, (118.0, -263.0, 1.8), (0.4, 14.0, 3.4), mat_white_gallery)

    # 3 Minimalist White Sculpture Pedestals with Modern Art Sculptures
    pedestal_coords = [(108.0, -268.0), (108.0, -263.0), (108.0, -258.0)]
    for i, (px, py) in enumerate(pedestal_coords):
        make_box(f"Ringel_Pedestal_{i+1}", col_int, (px, py, 0.6), (1.0, 1.0, 1.2), mat_white_gallery)
        # Bronze / Marble modern art sculpture piece
        sculp_mat = mat_bronze if i % 2 == 0 else mat_stone
        make_box(f"Ringel_Sculpture_{i+1}", col_int, (px, py, 1.5), (0.5, 0.5, 0.6), sculp_mat)

    # Curated Large Canvas Oil Paintings on Gallery Walls
    paintings = [
        ("Ringel_Painting_S1", (94.0, -275.25, 2.2), (3.6, 0.1, 2.0)),
        ("Ringel_Painting_S2", (106.0, -275.25, 2.2), (4.2, 0.1, 2.2)),
        ("Ringel_Painting_S3", (122.0, -275.25, 2.2), (3.6, 0.1, 2.0)),
        ("Ringel_Painting_N1", (94.0, -250.75, 2.2), (4.0, 0.1, 2.0)),
        ("Ringel_Painting_N2", (110.0, -250.75, 2.2), (4.8, 0.1, 2.2)),
        ("Ringel_Painting_N3", (126.0, -250.75, 2.2), (3.6, 0.1, 2.0))
    ]
    for pname, ploc, psize in paintings:
        make_box(pname, col_int, ploc, psize, mat_gold)
        # Brass picture light fixture directly above painting
        make_box(f"{pname}_Light", col_int, (ploc[0], ploc[1], ploc[2] + psize[2]/2 + 0.25), (1.4, 0.3, 0.1), mat_brass)

    # Gallery Track Lights: 4 Focused Spotlights aimed at art
    for i, gx in enumerate([94.0, 108.0, 122.0]):
        g_light_data = bpy.data.lights.new(name=f"Ringel_TrackLight_Data_{i+1}", type='POINT')
        g_light_data.energy = 1800.0
        g_light_data.color = (1.0, 0.96, 0.90)
        g_light_obj = bpy.data.objects.new(f"Ringel_TrackLight_{i+1}", g_light_data)
        g_light_obj.location = (gx, -263.0, 3.8)
        col_int.objects.link(g_light_obj)

    # -------------------------------------------------------------------------
    # Interior Destination 4: MAIN CIVIC CONCOURSE & BOILERMAKER STATION
    # Sited at X in [72.0, 86.0], Y in [-296.0, -225.0], Z = 0.0 to 4.2m
    # -------------------------------------------------------------------------
    print("Building Main Concourse & Boilermaker Station...")
    make_box("STEW_Concourse_Floor", col_int, (79.0, -260.0, 0.05), (13.5, 70.0, 0.1), mat_terrazzo)
    make_box("STEW_Concourse_Ceiling", col_int, (79.0, -260.0, 4.15), (13.5, 70.0, 0.1), mat_white_gallery)

    # Boilermaker Station Reception / Information Desk at Y = -230.0
    make_box("STEW_Welcome_Desk", col_int, (79.0, -230.0, 0.55), (6.0, 1.8, 1.1), mat_honey_oak)
    make_box("STEW_Welcome_Desk_Top", col_int, (79.0, -230.0, 1.12), (6.4, 2.0, 0.06), mat_terrazzo)
    # 2 Staff task chairs
    make_box("STEW_Desk_Chair_1", col_int, (77.8, -228.8, 0.5), (0.6, 0.6, 0.9), mat_dark_oak)
    make_box("STEW_Desk_Chair_2", col_int, (80.2, -228.8, 0.5), (0.6, 0.6, 0.9), mat_dark_oak)

    # Overhead Directional Signage Header
    make_box("STEW_Directional_Sign_Bar", col_int, (79.0, -245.0, 3.4), (10.0, 0.2, 0.7), mat_dark_oak)
    make_box("STEW_Directional_Sign_Face", col_int, (79.0, -245.15, 3.4), (9.8, 0.05, 0.6), mat_gold)

    # =========================================================================
    # PART 3: CIVIC PLAZA & SITE INTEGRATION (50_Stewart_Center_Plaza_and_Site)
    # 1. North Memorial Mall Arrival Terrace (facing Loeb Fountain & Founders Park)
    # 2. South State Street Concourse & Bicycle Parking
    # 3. East Concourse Interface linking to PMU West Courtyard Promenade
    # =========================================================================
    print("Building Part 3: Stewart Center Site & Plaza Integration...")

    # 1. North Memorial Mall Grand Terrace (Y in [-211.0, -195.0], X in [55.0, 115.0])
    # Elevated terrace slab at Z = 0.35m
    make_box("STEW_North_Terrace_Paving", col_site, (85.0, -203.0, 0.18), (60.0, 16.0, 0.35), mat_stone)
    # Stepped wide limestone stairs descending to Memorial Mall grade (Z = 0.35 down to 0.0)
    for step_i, sy in enumerate([-195.0, -194.2, -193.4]):
        make_box(f"STEW_North_Step_{step_i+1}", col_site, (85.0, sy, 0.25 - step_i * 0.1), (62.0, 0.8, 0.12), mat_stone)

    # Manicured Lawn Panels with Boxwood Hedges framing the North Terrace
    make_box("STEW_North_Lawn_West", col_site, (42.0, -203.0, 0.05), (24.0, 15.0, 0.1), mat_stone)
    make_box("STEW_North_Lawn_East", col_site, (128.0, -203.0, 0.05), (24.0, 15.0, 0.1), mat_stone)

    # Curved Limestone Seatwalls on North Terrace
    make_box("STEW_North_Seatwall_W", col_site, (62.0, -197.0, 0.55), (12.0, 0.6, 0.7), mat_stone)
    make_box("STEW_North_Seatwall_E", col_site, (108.0, -197.0, 0.55), (12.0, 0.6, 0.7), mat_stone)

    # Campus Teak Wood Benches on North Terrace
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_dark_oak
    for bx in [70.0, 78.0, 92.0, 100.0]:
        make_box(f"STEW_North_Bench_{bx}", col_site, (bx, -197.5, 0.45), (2.4, 0.7, 0.55), bench_mat)

    # Victorian Cast-Iron Campus Lantern Posts on North Terrace
    for lx in [60.0, 85.0, 110.0]:
        make_box(f"STEW_North_Lantern_Post_{lx}", col_site, (lx, -196.0, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box(f"STEW_North_Lantern_Head_{lx}", col_site, (lx, -196.0, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        # Point light for ambient terrace illumination
        l_data = bpy.data.lights.new(name=f"STEW_Lantern_Light_Data_{lx}", type='POINT')
        l_data.energy = 1200.0
        l_data.color = (1.0, 0.88, 0.70)
        l_obj = bpy.data.objects.new(f"STEW_Lantern_Light_{lx}", l_data)
        l_obj.location = (lx, -196.0, 4.2)
        col_site.objects.link(l_obj)

    # 2. South State Street Plaza (Y in [-318.0, -303.3], X in [50.0, 120.0])
    make_box("STEW_South_Plaza_Paving", col_site, (85.0, -310.5, 0.05), (70.0, 14.5, 0.1), mat_plaza_brick)
    # Bank of 12 Sheffield Bicycle Racks
    for rx in range(58, 82, 2):
        make_box(f"STEW_Bike_Rack_{rx}", col_site, (rx, -311.0, 0.45), (0.1, 1.2, 0.9), mat_bronze)

    # Limestone Planter Beds along State Street sidewalk
    make_box("STEW_South_Planter_W", col_site, (64.0, -315.0, 0.45), (18.0, 2.4, 0.7), mat_stone)
    make_box("STEW_South_Planter_E", col_site, (106.0, -315.0, 0.45), (18.0, 2.4, 0.7), mat_stone)

    # 3. East Concourse Walkway linking seamlessly into PMU West Courtyard
    # X in [151.3, 165.7], Y in [-268.0, -240.0]
    make_box("STEW_PMU_Concourse_Connector", col_site, (158.5, -254.0, 0.05), (14.4, 28.0, 0.1), mat_concrete)

    # =========================================================================
    # PART 4: DEDICATED INSPECTION CAMERAS
    # Cam_72: South Hero State Street View
    # Cam_73: Loeb Playhouse Proscenium Theatre Interior
    # Cam_74: HSSE Library Reading Room & Book Stacks
    # Cam_75: Robert L. Ringel Gallery Interior
    # Cam_76: North Memorial Mall Terrace & Aerial Context
    # =========================================================================
    print("Setting up 5 Calibrated Inspection Cameras...")
    cams_spec = [
        ("Cam_72_Stewart_South_Hero", (84.0, -332.0, 6.5), (math.radians(82), 0, 0)),
        ("Cam_73_Stewart_LoebPlayhouse_Interior", (52.0, -273.0, 2.2), (math.radians(84), 0, 0)),
        ("Cam_74_Stewart_HSSE_Library_Interior", (103.0, -243.0, 2.2), (math.radians(83), 0, math.radians(-35))),
        ("Cam_75_Stewart_RingelGallery_Interior", (95.0, -273.0, 1.9), (math.radians(85), 0, math.radians(-30))),
        ("Cam_76_Stewart_North_Aerial", (85.0, -170.0, 42.0), (math.radians(52), 0, math.radians(180)))
    ]

    for cname, cloc, crot in cams_spec:
        cam_obj = bpy.data.objects.get(cname)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name=cname + "_Data")
            cam_obj = bpy.data.objects.new(cname, cam_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = cloc
        cam_obj.rotation_euler = crot
        cam_obj.data.lens = 24.0 if "Aerial" in cname else (28.0 if "Hero" in cname else 22.0)
        cam_obj.data.clip_start = 0.1
        cam_obj.data.clip_end = 1500.0

    print("=== Stewart Center (STEW) Digital Twin Build Completed Successfully! ===")

if __name__ == "__main__":
    run()
