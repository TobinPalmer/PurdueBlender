"""
Build Purdue Frederick L. Hovde Hall of Administration (HOVD - 1936) Digital Twin
Complete Exterior, Office of the University President, Board of Trustees Boardroom,
Art Deco Grand Rotunda & Marble Entrance Foyer, and Memorial Mall Plaza Integration.
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Starting Hovde Hall of Administration (HOVD) Digital Twin Build ===")
    
    # 1. Clean up old massing placeholder
    col_massing = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if col_massing:
        old_hovd = bpy.data.objects.get("Hovde Hall of Administration (HOVD)")
        if old_hovd:
            print(f"Removing old massing placeholder: {old_hovd.name}")
            col_massing.objects.unlink(old_hovd)
            bpy.data.objects.remove(old_hovd, do_unlink=True)
            
    # Purge existing Hovde collections if any
    for col_name in ["51_Hovde_Hall_Exterior", "52_Hovde_Hall_Interiors", "53_Hovde_Hall_Plaza_and_Site"]:
        c = bpy.data.collections.get(col_name)
        if c:
            print(f"Purging existing collection: {col_name} ({len(c.objects)} objects)")
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(c)

    # Create dedicated collections
    col_ext = bpy.data.collections.new("51_Hovde_Hall_Exterior")
    col_int = bpy.data.collections.new("52_Hovde_Hall_Interiors")
    col_site = bpy.data.collections.new("53_Hovde_Hall_Plaza_and_Site")
    
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

    # Materials setup
    mat_stone = get_mat("Hovde_Bedford_Limestone", (0.84, 0.82, 0.77, 1.0), roughness=0.52)
    mat_brick = get_mat("Hovde_Purdue_Red_Brick", (0.48, 0.16, 0.10, 1.0), roughness=0.72)
    mat_granite_steps = get_mat("Hovde_Barre_Granite", (0.45, 0.44, 0.43, 1.0), roughness=0.45)
    mat_glass = get_mat("Hovde_Solar_Curtain_Glass", (0.10, 0.18, 0.24, 0.85), roughness=0.05, specular=0.95)
    mat_gold = get_mat("Hovde_Signage_Gold", (0.96, 0.78, 0.22, 1.0), roughness=0.22, metallic=0.95)
    mat_bronze = get_mat("Hovde_Bronze_Metal", (0.28, 0.20, 0.14, 1.0), roughness=0.35, metallic=0.85)
    mat_walnut = get_mat("Hovde_Executive_Walnut", (0.22, 0.12, 0.06, 1.0), roughness=0.28, specular=0.7)
    mat_mahogany = get_mat("Hovde_Boardroom_Mahogany", (0.28, 0.10, 0.05, 1.0), roughness=0.24, specular=0.75)
    mat_marble_cream = get_mat("Hovde_Rotunda_Marble", (0.90, 0.89, 0.86, 1.0), roughness=0.08, specular=0.98)
    mat_marble_gray = get_mat("Hovde_Rotunda_Marble_Trim", (0.40, 0.40, 0.42, 1.0), roughness=0.10, specular=0.95)
    mat_leather_black = get_mat("Hovde_Executive_Leather_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.4, specular=0.5)
    mat_leather_burgundy = get_mat("Hovde_Chesterfield_Burgundy", (0.35, 0.05, 0.07, 1.0), roughness=0.5, specular=0.4)
    mat_navy_carpet = get_mat("Hovde_Boardroom_Navy_Carpet", (0.05, 0.08, 0.20, 1.0), roughness=0.92)
    mat_terrazzo = get_mat("Hovde_Terrazzo_Floor", (0.86, 0.85, 0.83, 1.0), roughness=0.12, specular=0.95)
    mat_brass = get_mat("Hovde_Polished_Brass", (0.92, 0.76, 0.30, 1.0), roughness=0.18, metallic=0.92)
    mat_green_glass = get_mat("Hovde_Bankers_Green_Glass", (0.04, 0.42, 0.14, 0.9), roughness=0.08, specular=0.95, emission=(0.05, 0.55, 0.18, 3.5))
    mat_screen_emissive = get_mat("Hovde_Screen_Emissive", (0.95, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.95, 0.95, 1.0, 4.0))
    mat_warm_glow = get_mat("Hovde_Warm_Lamp_Glow", (1.0, 0.88, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.60, 5.0))
    mat_flag_us = get_mat("Hovde_US_Flag", (0.75, 0.12, 0.12, 1.0), roughness=0.6)
    mat_flag_in = get_mat("Hovde_Indiana_Flag", (0.08, 0.15, 0.55, 1.0), roughness=0.6)
    mat_plaster_ivory = get_mat("Hovde_Plaster_Ivory", (0.94, 0.93, 0.90, 1.0), roughness=0.45)
    mat_roof_gravel = get_mat("Hovde_Roof_Membrane", (0.35, 0.34, 0.33, 1.0), roughness=0.85)

    # Root Empty Object for Rotated Georeferencing
    root_loc = (-62.85, 93.00, 0.0)
    root_rot_z = math.radians(39.52)
    
    root_obj = bpy.data.objects.get("HOVD_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("HOVD_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        col_ext.objects.link(root_obj)
    root_obj.location = root_loc
    root_obj.rotation_euler = (0, 0, root_rot_z)

    # Box maker helper in local parented coordinates
    def make_box_local(name, col, loc_local, size, mat=None, rot_local=(0,0,0)):
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
        obj = bpy.context.active_object
        obj.name = name
        obj.dimensions = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if col:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        # Parent to root
        obj.parent = root_obj
        obj.location = loc_local
        obj.rotation_euler = rot_local
        return obj

    # Cylinder maker in local coordinates
    def make_cylinder_local(name, col, loc_local, radius, height, mat=None, rot_local=(0,0,0), vertices=32):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=vertices, location=(0,0,0))
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if col:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        obj.parent = root_obj
        obj.location = loc_local
        obj.rotation_euler = rot_local
        return obj

    # =========================================================================
    # PART 1: EXTERIOR NEOCLASSICAL ARCHITECTURE (51_Hovde_Hall_Exterior)
    # Local Envelope: X in [-10.8, +10.8] (width 21.6m), Y in [-35.5, +35.5] (length 71.0m)
    # Height Z = 0 to 16.5m (Parapet at 16.5m, attic/penthouse to 18.5m)
    # -Y local faces Memorial Mall (South-East in world coordinates)
    # +Y local faces Engineering Mall (North-West in world coordinates)
    # -X local faces Elliott Hall (South-West in world coordinates)
    # +X local faces Centennial Mall & WALC (North-East in world coordinates)
    # =========================================================================
    print("Building Part 1: Hovde Hall Exterior Envelopes & Neoclassical Porticos...")

    # True Hollow Perimeter Architectural Envelopes:
    # 1. South Facade facing Memorial Mall (Y_local = -35.5)
    make_box_local("HOVD_Wall_South_West", col_ext, (-7.2, -35.5 + 0.35, 8.25), (7.2, 0.7, 16.5), mat_stone)
    make_box_local("HOVD_Wall_South_East", col_ext, (7.2, -35.5 + 0.35, 8.25), (7.2, 0.7, 16.5), mat_stone)
    make_box_local("HOVD_Wall_South_Center_Upper", col_ext, (0.0, -35.5 + 0.35, 13.5), (7.2, 0.7, 6.0), mat_stone)

    # South Limestone Water Table Base (Z = 0.0 to 1.5m)
    make_box_local("HOVD_Base_South", col_ext, (0.0, -35.5 + 0.3, 0.75), (21.8, 0.8, 1.5), mat_stone)

    # South Horizontal Beltcourses
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_South_{z_c}", col_ext, (0.0, -35.5 + 0.3, z_c), (21.8, 0.8, h_c), mat_stone)

    # Monumental South Portico facing Memorial Mall (Y_local extends from -35.5 to -40.5)
    # Entablature beam supported by 6 fluted limestone columns at Z = 10.5 to 12.5m
    make_box_local("HOVD_Portico_Entablature", col_ext, (0.0, -38.5, 11.5), (18.4, 6.8, 2.0), mat_stone)
    make_box_local("HOVD_Portico_Cornice", col_ext, (0.0, -38.5, 12.7), (18.8, 7.2, 0.4), mat_stone)
    # Stepped Classical Pediment (Z = 12.9 to 16.5m)
    make_box_local("HOVD_Portico_Pediment_Base", col_ext, (0.0, -38.5, 14.5), (17.5, 6.5, 3.2), mat_stone)

    # 6 Monumental Fluted Bedford Limestone Columns (radius 0.55m = 1.1m dia, height 10.5m)
    col_xs = [-7.5, -4.5, -1.5, 1.5, 4.5, 7.5]
    for i, cx in enumerate(col_xs):
        # Column shaft
        make_cylinder_local(f"HOVD_Column_Shaft_{i+1}", col_ext, (cx, -40.5, 5.25), 0.55, 9.5, mat_stone)
        # Plinth base
        make_box_local(f"HOVD_Column_Base_{i+1}", col_ext, (cx, -40.5, 0.3), (1.4, 1.4, 0.6), mat_granite_steps)
        # Ionic / Neoclassical capital
        make_box_local(f"HOVD_Column_Capital_{i+1}", col_ext, (cx, -40.5, 10.25), (1.4, 1.4, 0.5), mat_stone)

    # Grand Granite Entrance Stairs (Y_local = -40.5 to -45.5, Z = 0.8 down to 0.0)
    for step_i in range(8):
        sy = -40.8 - step_i * 0.6
        sz = 0.7 - step_i * 0.1
        sw = 18.0 + step_i * 0.4
        make_box_local(f"HOVD_Grand_Step_{step_i+1}", col_site, (0.0, sy, sz/2), (sw, 0.6, sz), mat_granite_steps)

    # 3D Gold Building Lettering on Portico Frieze: "FREDERICK L. HOVDE HALL OF ADMINISTRATION"
    make_box_local("HOVD_Sign_Plaque", col_ext, (0.0, -42.0, 11.5), (16.0, 0.1, 0.8), mat_stone)
    try:
        font_curve = bpy.data.curves.new(type="FONT", name="HOVD_Gold_Sign_Curve")
        font_curve.body = "HOVDE HALL OF ADMINISTRATION"
        font_curve.size = 0.85
        font_curve.extrude = 0.05
        font_curve.bevel_depth = 0.015
        sign_obj = bpy.data.objects.new("HOVD_Sign_Text", font_curve)
        sign_obj.parent = root_obj
        sign_obj.location = (-7.2, -42.1, 11.1)
        sign_obj.rotation_euler = (math.radians(90), 0, 0)
        sign_obj.data.materials.append(mat_gold)
        col_ext.objects.link(sign_obj)
    except Exception as e:
        print(f"Sign text fallback: {e}")
        make_box_local("HOVD_Sign_Text_Box", col_ext, (0.0, -42.1, 11.5), (14.0, 0.05, 0.6), mat_gold)

    # Main South Entrance Portal: 3 Sets of Double Bronze Doors with Glass Transoms
    for dx in [-3.5, 0.0, 3.5]:
        make_box_local(f"HOVD_Door_Frame_{dx}", col_ext, (dx, -35.5 - 0.05, 1.8), (2.8, 0.3, 3.4), mat_bronze)
        make_box_local(f"HOVD_Door_Glass_{dx}", col_ext, (dx, -35.5 - 0.05, 1.8), (2.4, 0.1, 3.0), mat_glass)
        make_box_local(f"HOVD_Door_Transom_{dx}", col_ext, (dx, -35.5 - 0.05, 3.6), (2.4, 0.1, 0.8), mat_glass)

    # 2. North Facade facing Engineering Mall (Y_local = +35.5)
    make_box_local("HOVD_Wall_North", col_ext, (0.0, 35.5 - 0.35, 8.25), (21.6, 0.7, 16.5), mat_brick)
    make_box_local("HOVD_Base_North", col_ext, (0.0, 35.5 - 0.3, 0.75), (21.8, 0.8, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_North_{z_c}", col_ext, (0.0, 35.5 - 0.3, z_c), (21.8, 0.8, h_c), mat_stone)
    # North entrance portal
    make_box_local("HOVD_North_Portal_Stone", col_ext, (0.0, 35.5 + 0.1, 2.2), (5.0, 0.8, 4.4), mat_stone)
    make_box_local("HOVD_North_Door_Bronze", col_ext, (0.0, 35.5 + 0.05, 1.6), (3.4, 0.2, 3.2), mat_bronze)

    # 3. East Facade facing Centennial Mall & WALC (X_local = +10.8)
    make_box_local("HOVD_Wall_East", col_ext, (10.8 - 0.35, 0.0, 8.25), (0.7, 71.0, 16.5), mat_brick)
    make_box_local("HOVD_Base_East", col_ext, (10.8 - 0.3, 0.0, 0.75), (0.8, 71.2, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_East_{z_c}", col_ext, (10.8 - 0.3, 0.0, z_c), (0.8, 71.2, h_c), mat_stone)
    # East pilasters & window bays
    for y_bay in range(-30, 32, 6):
        make_box_local(f"HOVD_Pilaster_East_{y_bay}", col_ext, (10.8 - 0.25, y_bay, 8.25), (0.5, 0.8, 16.5), mat_stone)
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box_local(f"HOVD_Win_East_{y_bay}_{fl}", col_ext, (10.8 - 0.35, y_bay + 3.0, fz), (0.2, 3.8, 2.2), mat_glass)
            make_box_local(f"HOVD_Sill_East_{y_bay}_{fl}", col_ext, (10.8 - 0.35, y_bay + 3.0, fz - 1.15), (0.4, 4.0, 0.2), mat_stone)

    # 4. West Facade facing Elliott Hall of Music (X_local = -10.8)
    make_box_local("HOVD_Wall_West", col_ext, (-10.8 + 0.35, 0.0, 8.25), (0.7, 71.0, 16.5), mat_brick)
    make_box_local("HOVD_Base_West", col_ext, (-10.8 + 0.3, 0.0, 0.75), (0.8, 71.2, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_West_{z_c}", col_ext, (-10.8 + 0.3, 0.0, z_c), (0.8, 71.2, h_c), mat_stone)
    for y_bay in range(-30, 32, 6):
        make_box_local(f"HOVD_Pilaster_West_{y_bay}", col_ext, (-10.8 + 0.25, y_bay, 8.25), (0.5, 0.8, 16.5), mat_stone)
        for fl, fz in [(1, 2.85), (2, 6.3), (3, 10.5), (4, 14.5)]:
            make_box_local(f"HOVD_Win_West_{y_bay}_{fl}", col_ext, (-10.8 + 0.35, y_bay + 3.0, fz), (0.2, 3.8, 2.2), mat_glass)
            make_box_local(f"HOVD_Sill_West_{y_bay}_{fl}", col_ext, (-10.8 + 0.35, y_bay + 3.0, fz - 1.15), (0.4, 4.0, 0.2), mat_stone)

    # 5. Roof System & Central Attic/Penthouse
    make_box_local("HOVD_Roof_Membrane", col_ext, (0.0, 0.0, 16.3), (20.6, 69.8, 0.3), mat_roof_gravel)
    # Raised Central Mechanical Penthouse / Attic
    make_box_local("HOVD_Penthouse_Body", col_ext, (0.0, 0.0, 17.5), (14.0, 24.0, 2.2), mat_stone)
    make_box_local("HOVD_Penthouse_Coping", col_ext, (0.0, 0.0, 18.7), (14.6, 24.6, 0.3), mat_stone)
    make_box_local("HOVD_Penthouse_Louver_E", col_ext, (7.05, 0.0, 17.5), (0.2, 18.0, 1.4), mat_bronze)
    make_box_local("HOVD_Penthouse_Louver_W", col_ext, (-7.05, 0.0, 17.5), (0.2, 18.0, 1.4), mat_bronze)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIORS (52_Hovde_Hall_Interiors)
    # Finished Floor Elevated to Z = 0.40m!
    # 1. Art Deco Grand Rotunda & Marble Foyer (Ground Floor: Z = 0.40 to 4.2m)
    # 2. Office of the University President (Floor 2: Z = 4.40 to 8.2m)
    # 3. Board of Trustees Boardroom (Floor 2: Z = 4.40 to 8.2m)
    # =========================================================================
    print("Building Part 2: Hovde Hall Photorealistic Interiors...")

    # -------------------------------------------------------------------------
    # 1. ART DECO GRAND ROTUNDA & MARBLE FOYER (Ground Floor Center)
    # Local: X in [-9.5, +9.5], Y in [-14.0, +14.0], Z = 0.40 to 7.8m (2-story volume!)
    # -------------------------------------------------------------------------
    print("Building Art Deco Grand Rotunda...")
    # Floor slab in polished cream marble tile
    make_box_local("HOVD_Rotunda_Floor_Base", col_int, (0.0, 0.0, 0.40), (19.0, 28.0, 0.20), mat_marble_cream)
    make_box_local("HOVD_Rotunda_Ceiling", col_int, (0.0, 0.0, 7.75), (19.0, 28.0, 0.10), mat_plaster_ivory)

    # Central Circular Terrazzo Purdue Seal Medallion (radius 1.6m = 3.2m dia)
    make_cylinder_local("HOVD_Rotunda_Seal_Medallion", col_int, (0.0, 0.0, 0.51), 1.6, 0.02, mat_terrazzo)
    make_cylinder_local("HOVD_Rotunda_Seal_Gold_Ring", col_int, (0.0, 0.0, 0.52), 1.62, 0.02, mat_gold)
    make_box_local("HOVD_Rotunda_Seal_Center_P", col_int, (0.0, 0.0, 0.53), (1.2, 0.8, 0.02), mat_gold)

    # Marble perimeter wall border
    make_box_local("HOVD_Rotunda_Border_N", col_int, (0.0, 13.5, 0.51), (18.6, 0.8, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_S", col_int, (0.0, -13.5, 0.51), (18.6, 0.8, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_E", col_int, (9.0, 0.0, 0.51), (0.8, 27.6, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_W", col_int, (-9.0, 0.0, 0.51), (0.8, 27.6, 0.02), mat_marble_gray)

    # Twin Sweeping Marble Staircases to Floor 2 (East and West sides)
    for side_sign, s_name in [(-1, "W"), (1, "E")]:
        stair_x = side_sign * 7.5
        # 16 Marble steps rising from Z = 0.5 to 4.2m
        for step_i in range(16):
            step_y = -8.0 + step_i * 0.9
            step_z = 0.5 + step_i * 0.23
            make_box_local(f"HOVD_Stair_{s_name}_{step_i+1}", col_int, (stair_x, step_y, step_z), (2.4, 0.85, 0.23), mat_marble_cream)
        # Ornate Cast-Bronze Balustrades and Walnut Handrail
        make_box_local(f"HOVD_Handrail_{s_name}", col_int, (stair_x - side_sign * 1.1, -1.0, 2.8), (0.1, 15.0, 0.9), mat_bronze)
        make_box_local(f"HOVD_Handrail_Cap_{s_name}", col_int, (stair_x - side_sign * 1.1, -1.0, 3.3), (0.15, 15.2, 0.1), mat_walnut)

    # 2 Monumental Art Deco Multi-Tier Brass Ring Chandeliers
    for cy in [-4.0, 4.0]:
        make_cylinder_local(f"HOVD_Chandelier_Tier1_{cy}", col_int, (0.0, cy, 6.2), 1.8, 0.15, mat_brass)
        make_cylinder_local(f"HOVD_Chandelier_Tier2_{cy}", col_int, (0.0, cy, 5.7), 1.2, 0.15, mat_brass)
        make_cylinder_local(f"HOVD_Chandelier_Tier3_{cy}", col_int, (0.0, cy, 5.2), 0.7, 0.15, mat_brass)
        # Chandelier lights
        for ang_deg in range(0, 360, 45):
            rad = math.radians(ang_deg)
            lx = 1.6 * math.cos(rad)
            ly = cy + 1.6 * math.sin(rad)
            make_box_local(f"HOVD_Chandelier_Bulb_{cy}_{ang_deg}", col_int, (lx, ly, 6.0), (0.15, 0.15, 0.2), mat_warm_glow)
        
        # Dedicated point light for ambient foyer glow
        l_data = bpy.data.lights.new(name=f"HOVD_Rotunda_Light_Data_{cy}", type='POINT')
        l_data.energy = 4200.0
        l_data.color = (1.0, 0.92, 0.82)
        l_obj = bpy.data.objects.new(f"HOVD_Rotunda_Light_{cy}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (0.0, cy, 5.5)
        col_int.objects.link(l_obj)

    # Historic 1936 Foundation Bronze Plaques on Foyer Walls
    make_box_local("HOVD_Bronze_Plaque_PWA", col_int, (0.0, 13.85, 2.2), (3.2, 0.1, 1.8), mat_bronze)
    make_box_local("HOVD_Bronze_Plaque_Hovde", col_int, (0.0, -13.85, 2.2), (3.2, 0.1, 1.8), mat_bronze)

    # -------------------------------------------------------------------------
    # 2. OFFICE OF THE UNIVERSITY PRESIDENT (Presidential Executive Suite, Floor 2)
    # Local: X in [-9.5, +9.5], Y in [-34.0, -16.0], Z = 4.40 to 8.2m
    # South corner overlooking Memorial Mall!
    # -------------------------------------------------------------------------
    print("Building Office of the University President...")
    # Floor slab in polished dark walnut parquet
    make_box_local("HOVD_Pres_Floor", col_int, (0.0, -25.0, 4.40), (19.0, 18.0, 0.20), mat_walnut)
    make_box_local("HOVD_Pres_Ceiling", col_int, (0.0, -25.0, 8.15), (19.0, 18.0, 0.10), mat_plaster_ivory)
    # Dark Walnut Wainscoting (height 1.4m) around room
    make_box_local("HOVD_Pres_Wainscot_N", col_int, (0.0, -16.2, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_S", col_int, (0.0, -33.8, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_E", col_int, (9.2, -25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_W", col_int, (-9.2, -25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)

    # Burgundy Persian Area Rug under Presidential Desk & Seating
    make_box_local("HOVD_Pres_Rug", col_int, (0.0, -26.0, 4.51), (14.0, 12.0, 0.02), mat_leather_burgundy)

    # Monumental Executive Mahogany Partner Desk (centered at Y = -27.5)
    make_box_local("HOVD_Pres_Desk_Top", col_int, (0.0, -27.5, 5.25), (4.2, 2.2, 0.10), mat_mahogany)
    # Desk pedestals
    make_box_local("HOVD_Pres_Desk_Ped_L", col_int, (-1.5, -27.5, 4.85), (0.9, 1.9, 0.70), mat_walnut)
    make_box_local("HOVD_Pres_Desk_Ped_R", col_int, (1.5, -27.5, 4.85), (0.9, 1.9, 0.70), mat_walnut)
    # Green leather desk writing blotter
    make_box_local("HOVD_Pres_Desk_Blotter", col_int, (0.0, -27.5, 5.31), (2.2, 1.4, 0.02), mat_green_glass)
    # Brass Banker's Lamp with Green Glass Shade
    make_box_local("HOVD_Pres_Lamp_Base", col_int, (1.2, -27.5, 5.34), (0.3, 0.3, 0.06), mat_brass)
    make_box_local("HOVD_Pres_Lamp_Stem", col_int, (1.2, -27.5, 5.55), (0.05, 0.05, 0.40), mat_brass)
    make_box_local("HOVD_Pres_Lamp_Shade", col_int, (1.2, -27.5, 5.75), (0.45, 0.25, 0.14), mat_green_glass)
    make_box_local("HOVD_Pres_Lamp_Bulb", col_int, (1.2, -27.5, 5.70), (0.35, 0.15, 0.05), mat_warm_glow)
    # Brass Pen Stand & Gold Purdue Desk Seal
    make_box_local("HOVD_Pres_Desk_Seal", col_int, (-1.2, -27.5, 5.34), (0.35, 0.35, 0.04), mat_gold)

    # President's Executive High-Back Leather Swivel Chair
    make_box_local("HOVD_Pres_Chair_Seat", col_int, (0.0, -29.0, 4.95), (0.9, 0.9, 0.15), mat_leather_black)
    make_box_local("HOVD_Pres_Chair_Back", col_int, (0.0, -29.4, 5.55), (0.85, 0.18, 1.05), mat_leather_black)
    make_box_local("HOVD_Pres_Chair_Base", col_int, (0.0, -29.0, 4.65), (0.7, 0.7, 0.45), mat_brass)

    # Meeting Area: Pair of Burgundy Chesterfield Leather Armchairs & Mahogany Coffee Table
    make_box_local("HOVD_Chesterfield_L_Seat", col_int, (-2.5, -23.5, 4.85), (1.1, 1.1, 0.45), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_L_Back", col_int, (-2.5, -22.8, 5.25), (1.1, 0.3, 0.65), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_R_Seat", col_int, (2.5, -23.5, 4.85), (1.1, 1.1, 0.45), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_R_Back", col_int, (2.5, -22.8, 5.25), (1.1, 0.3, 0.65), mat_leather_burgundy)
    # Round Mahogany Coffee Table
    make_cylinder_local("HOVD_Coffee_Table", col_int, (0.0, -23.5, 4.75), 1.1, 0.50, mat_mahogany)

    # Carved Bedford Limestone Fireplace on North Wall (Y = -16.2)
    make_box_local("HOVD_Pres_Fireplace_Mantel", col_int, (0.0, -16.5, 5.6), (4.2, 0.8, 1.8), mat_stone)
    make_box_local("HOVD_Pres_Firebox", col_int, (0.0, -16.3, 5.1), (2.2, 0.4, 1.1), mat_leather_black)
    make_box_local("HOVD_Pres_Embers", col_int, (0.0, -16.3, 4.7), (1.8, 0.3, 0.2), mat_warm_glow)
    # Fireplace Gold Purdue Clock
    make_box_local("HOVD_Pres_Mantel_Clock", col_int, (0.0, -16.5, 6.7), (0.8, 0.2, 0.5), mat_gold)

    # Flags Display: United States Flag and Indiana State Flag on Mahogany Standards
    # US Flag
    make_cylinder_local("HOVD_Flag_US_Pole", col_int, (-5.5, -31.5, 6.2), 0.05, 3.4, mat_brass)
    make_box_local("HOVD_Flag_US_Banner", col_int, (-5.5, -31.5, 6.8), (0.05, 1.2, 1.8), mat_flag_us)
    # Indiana Flag
    make_cylinder_local("HOVD_Flag_IN_Pole", col_int, (5.5, -31.5, 6.2), 0.05, 3.4, mat_brass)
    make_box_local("HOVD_Flag_IN_Banner", col_int, (5.5, -31.5, 6.8), (0.05, 1.2, 1.8), mat_flag_in)

    # Presidential Portrait Gallery: Gold-framed portraits on East Wall with picture lights
    for i, py in enumerate(range(-30, -18, 3)):
        make_box_local(f"HOVD_Portrait_{i+1}", col_int, (9.05, py, 6.4), (0.08, 1.6, 2.0), mat_gold)
        make_box_local(f"HOVD_Portrait_Light_{i+1}", col_int, (8.9, py, 7.5), (0.15, 0.8, 0.1), mat_brass)

    # President's Office Ceiling Chandelier & Warm Glow
    p_light_data = bpy.data.lights.new(name="HOVD_Pres_Light_Data", type='POINT')
    p_light_data.energy = 3800.0
    p_light_data.color = (1.0, 0.94, 0.85)
    p_light_obj = bpy.data.objects.new("HOVD_Pres_Light", p_light_data)
    p_light_obj.parent = root_obj
    p_light_obj.location = (0.0, -25.0, 7.2)
    col_int.objects.link(p_light_obj)

    # -------------------------------------------------------------------------
    # 3. BOARD OF TRUSTEES BOARDROOM (Floor 2 North Wing)
    # Local: X in [-9.5, +9.5], Y in [+16.0, +34.0], Z = 4.40 to 8.2m
    # -------------------------------------------------------------------------
    print("Building Board of Trustees Boardroom...")
    make_box_local("HOVD_Board_Floor", col_int, (0.0, 25.0, 4.40), (19.0, 18.0, 0.20), mat_navy_carpet)
    make_box_local("HOVD_Board_Ceiling", col_int, (0.0, 25.0, 8.15), (19.0, 18.0, 0.10), mat_plaster_ivory)

    # Walnut wall wainscoting
    make_box_local("HOVD_Board_Wainscot_N", col_int, (0.0, 33.8, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_S", col_int, (0.0, 16.2, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_E", col_int, (9.2, 25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_W", col_int, (-9.2, 25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)

    # Monumental 24-Seat Boat-Shaped Mahogany Boardroom Table
    # Table top: 13.5m length, 3.6m width, 0.08m thickness, at Z = 5.25m
    make_box_local("HOVD_Board_Table_Center", col_int, (0.0, 25.0, 5.25), (3.6, 13.5, 0.08), mat_mahogany)
    # 4 Solid Walnut Table Pedestal Bases
    for py in [19.5, 23.0, 27.0, 30.5]:
        make_box_local(f"HOVD_Board_Table_Ped_{py}", col_int, (0.0, py, 4.85), (2.0, 0.8, 0.70), mat_walnut)
    
    # Delegate Microphone Podiums & Connection Wells
    for my in range(19, 32, 2):
        for side_sign in [-1, 1]:
            make_box_local(f"HOVD_Mic_Base_{my}_{side_sign}", col_int, (side_sign * 1.5, my, 5.31), (0.15, 0.15, 0.02), mat_bronze)
            make_cylinder_local(f"HOVD_Mic_Gooseneck_{my}_{side_sign}", col_int, (side_sign * 1.5, my, 5.42), 0.015, 0.22, mat_bronze)

    # 24 Executive High-Back Black Leather Swivel Chairs
    # 10 along East side, 10 along West side, 2 at North head, 2 at South foot
    for chair_i, cy in enumerate(range(19, 32, 2)):
        # West chairs
        make_box_local(f"HOVD_Board_Chair_W_{chair_i}", col_int, (-2.4, cy, 4.95), (0.85, 0.85, 0.15), mat_leather_black)
        make_box_local(f"HOVD_Board_Back_W_{chair_i}", col_int, (-2.75, cy, 5.55), (0.15, 0.80, 1.05), mat_leather_black)
        make_box_local(f"HOVD_Board_Base_W_{chair_i}", col_int, (-2.4, cy, 4.65), (0.6, 0.6, 0.45), mat_brass)
        # East chairs
        make_box_local(f"HOVD_Board_Chair_E_{chair_i}", col_int, (2.4, cy, 4.95), (0.85, 0.85, 0.15), mat_leather_black)
        make_box_local(f"HOVD_Board_Back_E_{chair_i}", col_int, (2.75, cy, 5.55), (0.15, 0.80, 1.05), mat_leather_black)
        make_box_local(f"HOVD_Board_Base_E_{chair_i}", col_int, (2.4, cy, 4.65), (0.6, 0.6, 0.45), mat_brass)
    # Head & Foot chairs
    for head_y, h_name in [(17.6, "South"), (32.4, "North")]:
        make_box_local(f"HOVD_Board_Chair_Head_{h_name}", col_int, (0.0, head_y, 4.95), (0.85, 0.85, 0.15), mat_leather_black)
        make_box_local(f"HOVD_Board_Back_Head_{h_name}", col_int, (0.0, head_y + (0.35 if h_name == 'North' else -0.35), 5.55), (0.80, 0.15, 1.05), mat_leather_black)

    # Monumental 3D Gold Purdue University Seal on North Feature Wall (Y = 33.8)
    make_cylinder_local("HOVD_Board_Gold_Seal_Ring", col_int, (0.0, 33.65, 6.6), 1.2, 0.05, mat_gold, rot_local=(math.radians(90), 0, 0))
    make_box_local("HOVD_Board_Gold_Seal_Emblem", col_int, (0.0, 33.60, 6.6), (1.6, 0.04, 1.6), mat_gold)

    # Trustee Witness / Presentation Lectern with Gold Seal
    make_box_local("HOVD_Lectern_Body", col_int, (-4.5, 25.0, 5.0), (0.8, 0.8, 1.2), mat_mahogany)
    make_box_local("HOVD_Lectern_Top", col_int, (-4.5, 25.0, 5.62), (0.9, 0.9, 0.05), mat_walnut)
    make_box_local("HOVD_Lectern_Seal", col_int, (-4.05, 25.0, 5.2), (0.04, 0.35, 0.35), mat_gold)

    # Dual 120" Wall-Mounted Presentation Screens
    make_box_local("HOVD_Screen_E", col_int, (9.1, 25.0, 6.5), (0.05, 3.2, 1.8), mat_screen_emissive)
    make_box_local("HOVD_Screen_W", col_int, (-9.1, 25.0, 6.5), (0.05, 3.2, 1.8), mat_screen_emissive)

    # Boardroom Overhead Illumination
    b_light_data = bpy.data.lights.new(name="HOVD_Board_Light_Data", type='POINT')
    b_light_data.energy = 4500.0
    b_light_data.color = (1.0, 0.95, 0.88)
    b_light_obj = bpy.data.objects.new("HOVD_Board_Light", b_light_data)
    b_light_obj.parent = root_obj
    b_light_obj.location = (0.0, 25.0, 7.4)
    col_int.objects.link(b_light_obj)

    # =========================================================================
    # PART 3: CIVIC PLAZA & MEMORIAL MALL SITE INTEGRATION (53_Hovde_Hall_Plaza_and_Site)
    # =========================================================================
    print("Building Part 3: Hovde Hall Plaza & Site Integration...")

    # South Memorial Mall Arrival Concourse (extends forward along -Y_local)
    # Y_local in [-45.0, -60.0], X_local in [-16.0, +16.0]
    make_box_local("HOVD_Plaza_Paving", col_site, (0.0, -52.0, 0.05), (32.0, 16.0, 0.1), mat_granite_steps)

    # Symmetrical Bedford Limestone Planters with Evergreen Shrubs
    make_box_local("HOVD_Planter_L", col_site, (-11.5, -45.0, 0.5), (4.5, 3.0, 0.8), mat_stone)
    make_box_local("HOVD_Planter_R", col_site, (11.5, -45.0, 0.5), (4.5, 3.0, 0.8), mat_stone)

    # Campus Teak Wood Benches along Plaza
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_walnut
    for bx in [-8.0, 8.0]:
        make_box_local(f"HOVD_Bench_{bx}", col_site, (bx, -48.0, 0.45), (2.4, 0.7, 0.55), bench_mat)

    # Bank of 12 Sheffield Bicycle Racks
    for rx in range(-6, 7, 2):
        make_box_local(f"HOVD_Bike_Rack_{rx}", col_site, (rx, -55.0, 0.45), (0.1, 1.2, 0.9), mat_bronze)

    # Victorian Cast-Iron Campus Lantern Posts with Warm Luminaires
    for lx, ly in [(-12.0, -42.0), (12.0, -42.0), (-12.0, -56.0), (12.0, -56.0)]:
        make_box_local(f"HOVD_Lantern_Post_{lx}_{ly}", col_site, (lx, ly, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box_local(f"HOVD_Lantern_Head_{lx}_{ly}", col_site, (lx, ly, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        # Point light
        l_data = bpy.data.lights.new(name=f"HOVD_Lantern_Light_Data_{lx}_{ly}", type='POINT')
        l_data.energy = 1400.0
        l_data.color = (1.0, 0.90, 0.75)
        l_obj = bpy.data.objects.new(f"HOVD_Lantern_Light_{lx}_{ly}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (lx, ly, 4.2)
        col_site.objects.link(l_obj)

    # =========================================================================
    # PART 4: PRECISION-CALIBRATED INSPECTION CAMERAS
    # 5 Dedicated Inspection Cameras with Vector Track-To Calibration
    # =========================================================================
    print("Setting up 5 Precision-Calibrated Inspection Cameras...")

    def set_camera(name, loc_world, target_world, lens=28.0):
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
        print(f"Calibrated {name} at {loc_world} -> target {target_world}")
        return cam_obj

    # Matrix transformation helper to convert local coordinates to world coordinates:
    def local_to_world(local_coord):
        return root_obj.matrix_world @ mathutils.Vector(local_coord)

    # 1. Cam_77: South Hero View from Memorial Mall
    # Looking North at the 6-column portico, entablature, gold lettering, grand stairs
    cam77_loc = local_to_world((0.0, -58.0, 4.5))
    cam77_target = local_to_world((0.0, -36.0, 8.5))
    set_camera("Cam_77_Hovde_South_Hero", cam77_loc, cam77_target, lens=24.0)

    # 2. Cam_78: Office of the University President Interior
    # Inside the Presidential Suite looking at the mahogany desk, green banker's lamp, flags, fireplace
    cam78_loc = local_to_world((-3.5, -21.0, 5.8))
    cam78_target = local_to_world((0.0, -27.5, 5.4))
    set_camera("Cam_78_Hovde_President_Office_Interior", cam78_loc, cam78_target, lens=22.0)

    # 3. Cam_79: Board of Trustees Boardroom Interior
    # Inside Boardroom looking down the 24-seat mahogany table at the 3D gold Purdue seal & screens
    cam79_loc = local_to_world((0.0, 18.0, 5.8))
    cam79_target = local_to_world((0.0, 31.0, 6.2))
    set_camera("Cam_79_Hovde_BoardOfTrustees_Interior", cam79_loc, cam79_target, lens=24.0)

    # 4. Cam_80: Art Deco Grand Rotunda & Marble Foyer
    # Looking across the marble floor, central terrazzo seal, twin sweeping staircases & chandeliers
    cam80_loc = local_to_world((0.0, -9.5, 2.4))
    cam80_target = local_to_world((0.0, 3.5, 4.0))
    set_camera("Cam_80_Hovde_ArtDeco_Rotunda_Interior", cam80_loc, cam80_target, lens=22.0)

    # 5. Cam_81: Precinct Aerial View
    # High aerial view framing Hovde Hall, Memorial Mall, Elliott Hall, WALC, and Bell Tower
    cam81_loc = local_to_world((30.0, -80.0, 58.0))
    cam81_target = local_to_world((-10.0, 10.0, 10.0))
    set_camera("Cam_81_Hovde_Mall_Centennial_Aerial", cam81_loc, cam81_target, lens=28.0)

    print("=== Hovde Hall (HOVD) Digital Twin Build Completed Successfully! ===")

if __name__ == "__main__":
    run()
