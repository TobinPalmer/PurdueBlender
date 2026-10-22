"""
Refinement & Gold Standard Polish for Frederick L. Hovde Hall of Administration (HOVD - 1936)
Uses mathematically explicit matrix transformation M for bulletproof camera alignment and interior detailing.
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Refining Hovde Hall of Administration (HOVD) to Gold Standard Exemplar ===")

    # Ensure collections exist
    col_ext = bpy.data.collections.get("51_Hovde_Hall_Exterior")
    col_int = bpy.data.collections.get("52_Hovde_Hall_Interiors")
    col_site = bpy.data.collections.get("53_Hovde_Hall_Plaza_and_Site")

    if not col_ext:
        col_ext = bpy.data.collections.new("51_Hovde_Hall_Exterior")
        bpy.context.scene.collection.children.link(col_ext)
    if not col_int:
        col_int = bpy.data.collections.new("52_Hovde_Hall_Interiors")
        bpy.context.scene.collection.children.link(col_int)
    if not col_site:
        col_site = bpy.data.collections.new("53_Hovde_Hall_Plaza_and_Site")
        bpy.context.scene.collection.children.link(col_site)

    # Purge existing Hovde objects inside these collections to do a clean high-detail rebuild
    for col in [col_ext, col_int, col_site]:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Re-use or find HOVD_Root
    root_obj = bpy.data.objects.get("HOVD_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("HOVD_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        bpy.context.scene.collection.objects.link(root_obj)
        
    root_obj.location = (-62.85, 93.00, 0.0)
    root_obj.rotation_euler = (0, 0, math.radians(39.52))

    # Explicit transformation matrix M for guaranteed world space conversions:
    M_WORLD = mathutils.Matrix.Translation((-62.85, 93.00, 0.0)) @ mathutils.Euler((0, 0, math.radians(39.52))).to_matrix().to_4x4()

    # Helper for materials
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

    # Materials
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick") or get_mat("Purdue_Red_Brick", (0.50, 0.22, 0.18, 1.0), roughness=0.72)
    mat_stone = bpy.data.materials.get("Bedford_Indiana_Limestone") or get_mat("Bedford_Indiana_Limestone", (0.84, 0.83, 0.79, 1.0), roughness=0.55)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_mat("Solar_Ribbon_Glass", (0.15, 0.28, 0.38, 0.85), roughness=0.08, specular=0.98)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_mat("Purdue_Old_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mat_bronze = get_mat("Hovde_Bronze_Metal", (0.28, 0.20, 0.14, 1.0), roughness=0.35, metallic=0.85)
    mat_chrome = get_mat("Hovde_Chrome_Metal", (0.95, 0.95, 0.95, 1.0), roughness=0.10, metallic=0.98)
    mat_walnut = get_mat("Hovde_Executive_Walnut", (0.22, 0.12, 0.06, 1.0), roughness=0.28, specular=0.7)
    mat_mahogany = get_mat("Hovde_Boardroom_Mahogany", (0.26, 0.09, 0.04, 1.0), roughness=0.22, specular=0.82)
    mat_marble_cream = get_mat("Hovde_Rotunda_Marble", (0.92, 0.91, 0.88, 1.0), roughness=0.06, specular=0.98)
    mat_marble_gray = get_mat("Hovde_Rotunda_Marble_Trim", (0.35, 0.35, 0.38, 1.0), roughness=0.08, specular=0.95)
    mat_leather_black = get_mat("Hovde_Executive_Leather_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.38, specular=0.55)
    mat_leather_burgundy = get_mat("Hovde_Chesterfield_Burgundy", (0.35, 0.05, 0.07, 1.0), roughness=0.48, specular=0.42)
    mat_navy_carpet = get_mat("Hovde_Boardroom_Navy_Carpet", (0.05, 0.08, 0.20, 1.0), roughness=0.92)
    mat_terrazzo = get_mat("Hovde_Terrazzo_Floor", (0.86, 0.85, 0.83, 1.0), roughness=0.12, specular=0.95)
    mat_brass = get_mat("Hovde_Polished_Brass", (0.92, 0.76, 0.30, 1.0), roughness=0.18, metallic=0.92)
    mat_green_glass = get_mat("Hovde_Bankers_Green_Glass", (0.04, 0.42, 0.14, 0.9), roughness=0.08, specular=0.95, emission=(0.05, 0.55, 0.18, 3.5))
    mat_screen_emissive = get_mat("Hovde_Screen_Emissive", (0.95, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.95, 0.95, 1.0, 4.0))
    mat_mic_tally = get_mat("Hovde_Mic_Tally", (1.0, 0.1, 0.1, 1.0), roughness=0.2, emission=(1.0, 0.1, 0.1, 5.0))
    mat_warm_glow = get_mat("Hovde_Warm_Lamp_Glow", (1.0, 0.88, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.60, 5.0))
    mat_flag_us = get_mat("Hovde_US_Flag", (0.75, 0.12, 0.12, 1.0), roughness=0.6)
    mat_flag_in = get_mat("Hovde_Indiana_Flag", (0.08, 0.15, 0.55, 1.0), roughness=0.6)
    mat_plaster_ivory = get_mat("Hovde_Plaster_Ivory", (0.94, 0.93, 0.90, 1.0), roughness=0.45)
    mat_roof_gravel = get_mat("Hovde_Roof_Membrane", (0.35, 0.34, 0.33, 1.0), roughness=0.85)
    mat_granite_steps = get_mat("Hovde_Granite_Steps", (0.45, 0.44, 0.42, 1.0), roughness=0.5)

    # Geometry builders in local coordinates
    def make_box_local(name, col, local_pos, dimensions, mat=None, rot_local=(0, 0, 0)):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        obj.parent = root_obj
        obj.location = local_pos
        obj.rotation_euler = rot_local
        
        dx, dy, dz = dimensions[0] / 2.0, dimensions[1] / 2.0, dimensions[2] / 2.0
        verts = [
            (-dx, -dy, -dz), (dx, -dy, -dz), (dx, dy, -dz), (-dx, dy, -dz),
            (-dx, -dy, dz), (dx, -dy, dz), (dx, dy, dz), (-dx, dy, dz)
        ]
        faces = [
            (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
            (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    def make_cylinder_local(name, col, local_pos, radius, height, mat=None, segments=24, rot_local=(0,0,0)):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        obj.parent = root_obj
        obj.location = local_pos
        obj.rotation_euler = rot_local

        verts = []
        half_h = height / 2.0
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            verts.append((x, y, -half_h))
            verts.append((x, y, half_h))
        verts.append((0, 0, -half_h))
        verts.append((0, 0, half_h))
        bot_center = len(verts) - 2
        top_center = len(verts) - 1

        faces = []
        for i in range(segments):
            next_i = (i + 1) % segments
            b1 = i * 2
            t1 = i * 2 + 1
            b2 = next_i * 2
            t2 = next_i * 2 + 1
            faces.append((b1, b2, t2, t1))
            faces.append((bot_center, next_i * 2, i * 2))
            faces.append((top_center, i * 2 + 1, next_i * 2 + 1))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    # =========================================================================
    # PART 1: EXTERIOR NEOCLASSICAL ARCHITECTURE (51_Hovde_Hall_Exterior)
    # Dimensions: Width 21.6m (X in [-10.8, +10.8]), Length 71.0m (Y in [-35.5, +35.5]), Height 16.5m
    # =========================================================================
    print("Building Part 1: Exterior Neoclassical Architecture...")

    # True Hollow Perimeter Architectural Envelopes:
    # 1. South Facade facing Memorial Mall (Y_local = -35.5)
    make_box_local("HOVD_Wall_South_West", col_ext, (-7.2, -35.5 + 0.35, 8.25), (7.2, 0.7, 16.5), mat_brick)
    make_box_local("HOVD_Wall_South_East", col_ext, (7.2, -35.5 + 0.35, 8.25), (7.2, 0.7, 16.5), mat_brick)
    make_box_local("HOVD_Wall_South_Center_Upper", col_ext, (0.0, -35.5 + 0.35, 13.5), (7.2, 0.7, 6.0), mat_stone)

    # South Limestone Water Table Base (Z = 0.0 to 1.5m)
    make_box_local("HOVD_Base_South_West", col_ext, (-7.2, -35.5 + 0.3, 0.75), (7.4, 0.8, 1.5), mat_stone)
    make_box_local("HOVD_Base_South_East", col_ext, (7.2, -35.5 + 0.3, 0.75), (7.4, 0.8, 1.5), mat_stone)

    # South Horizontal Limestone Beltcourses
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_South_W_{z_c}", col_ext, (-7.2, -35.5 + 0.3, z_c), (7.4, 0.8, h_c), mat_stone)
        make_box_local(f"HOVD_Beltcourse_South_E_{z_c}", col_ext, (7.2, -35.5 + 0.3, z_c), (7.4, 0.8, h_c), mat_stone)

    # 2. North Facade facing Centennial Mall (Y_local = +35.5)
    make_box_local("HOVD_Wall_North", col_ext, (0.0, 35.5 - 0.35, 8.25), (21.6, 0.7, 16.5), mat_brick)
    make_box_local("HOVD_Base_North", col_ext, (0.0, 35.5 - 0.3, 0.75), (21.8, 0.8, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_North_{z_c}", col_ext, (0.0, 35.5 - 0.3, z_c), (21.8, 0.8, h_c), mat_stone)

    # 3. East Facade facing Centennial Mall & WALC (X_local = +10.8)
    make_box_local("HOVD_Wall_East", col_ext, (10.8 - 0.35, 0.0, 8.25), (0.7, 71.0, 16.5), mat_brick)
    make_box_local("HOVD_Base_East", col_ext, (10.8 - 0.3, 0.0, 0.75), (0.8, 71.2, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_East_{z_c}", col_ext, (10.8 - 0.3, 0.0, z_c), (0.8, 71.2, h_c), mat_stone)

    # 4. West Facade facing Elliott Hall of Music (X_local = -10.8)
    make_box_local("HOVD_Wall_West", col_ext, (-10.8 + 0.35, 0.0, 8.25), (0.7, 71.0, 16.5), mat_brick)
    make_box_local("HOVD_Base_West", col_ext, (-10.8 + 0.3, 0.0, 0.75), (0.8, 71.2, 1.5), mat_stone)
    for z_c, h_c in [(4.2, 0.3), (8.4, 0.3), (12.6, 0.3), (16.5, 0.4)]:
        make_box_local(f"HOVD_Beltcourse_West_{z_c}", col_ext, (-10.8 + 0.3, 0.0, z_c), (0.8, 71.2, h_c), mat_stone)

    # Roof Slab & Parapet Coping
    make_box_local("HOVD_Roof_Slab", col_ext, (0.0, 0.0, 16.6), (21.4, 70.8, 0.3), mat_roof_gravel)
    make_box_local("HOVD_Penthouse", col_ext, (0.0, 0.0, 18.0), (12.0, 24.0, 2.5), mat_stone)
    make_box_local("HOVD_Penthouse_Louvers", col_ext, (0.0, 12.05, 18.0), (8.0, 0.2, 1.8), mat_bronze)

    # Rhythmic Classical Window Bays on East & West Facades
    for y_win in range(-30, 31, 5):
        for floor_i, z_win in enumerate([2.6, 6.4, 10.5, 14.6]):
            # East windows
            make_box_local(f"HOVD_Win_E_{y_win}_{floor_i}", col_ext, (10.8 - 0.1, y_win, z_win), (0.2, 2.2, 2.4), mat_glass)
            make_box_local(f"HOVD_Sill_E_{y_win}_{floor_i}", col_ext, (10.8 + 0.05, y_win, z_win - 1.25), (0.35, 2.4, 0.2), mat_stone)
            # West windows
            make_box_local(f"HOVD_Win_W_{y_win}_{floor_i}", col_ext, (-10.8 + 0.1, y_win, z_win), (0.2, 2.2, 2.4), mat_glass)
            make_box_local(f"HOVD_Sill_W_{y_win}_{floor_i}", col_ext, (-10.8 - 0.05, y_win, z_win - 1.25), (0.35, 2.4, 0.2), mat_stone)

    # Monumental South Portico facing Memorial Mall (Y_local extends from -35.5 to -41.5)
    make_box_local("HOVD_Portico_Entablature", col_ext, (0.0, -38.5, 11.5), (18.4, 6.8, 2.0), mat_stone)
    make_box_local("HOVD_Portico_Cornice", col_ext, (0.0, -38.5, 12.7), (18.8, 7.2, 0.4), mat_stone)
    make_box_local("HOVD_Portico_Pediment_Base", col_ext, (0.0, -38.5, 14.5), (17.5, 6.5, 3.2), mat_stone)
    make_box_local("HOVD_Portico_Pediment_Crown", col_ext, (0.0, -38.5, 16.3), (16.0, 6.0, 0.5), mat_stone)

    # 6 Monumental Fluted Bedford Limestone Columns (radius 0.55m = 1.1m dia, height 10.5m)
    for col_i, cx in enumerate([-7.5, -4.5, -1.5, 1.5, 4.5, 7.5]):
        make_box_local(f"HOVD_Col_Plinth_{col_i+1}", col_ext, (cx, -41.0, 0.4), (1.4, 1.4, 0.8), mat_stone)
        make_cylinder_local(f"HOVD_Col_Shaft_{col_i+1}", col_ext, (cx, -41.0, 5.65), 0.55, 9.7, mat_stone, segments=32)
        make_box_local(f"HOVD_Col_Capital_{col_i+1}", col_ext, (cx, -41.0, 10.6), (1.5, 1.5, 0.4), mat_stone)

    # 3D Gold Building Lettering on Portico Frieze: "FREDERICK L. HOVDE HALL OF ADMINISTRATION"
    make_box_local("HOVD_Sign_Plaque", col_ext, (0.0, -42.0, 11.5), (16.4, 0.1, 0.8), mat_stone)
    try:
        fnt_curve = bpy.data.curves.new(type="FONT", name="HOVD_Gold_Text_Curve")
        fnt_curve.body = "FREDERICK L. HOVDE HALL OF ADMINISTRATION"
        fnt_curve.size = 0.52
        fnt_curve.extrude = 0.06
        fnt_curve.align_x = 'CENTER'
        fnt_curve.align_y = 'CENTER'
        txt_obj = bpy.data.objects.new("HOVD_Gold_Letters", fnt_curve)
        txt_obj.parent = root_obj
        txt_obj.location = (0.0, -42.08, 11.5)
        txt_obj.rotation_euler = (math.radians(90), 0, 0)
        col_ext.objects.link(txt_obj)
        txt_obj.data.materials.append(mat_gold)
    except Exception as e:
        print(f"Font text fallback: {e}")
        make_box_local("HOVD_Sign_Fallback", col_ext, (0.0, -42.08, 11.5), (15.5, 0.08, 0.5), mat_gold)

    # Monumental Triple Bronze Entrance Portals on South Facade (Y = -35.5)
    for door_i, dx in enumerate([-3.2, 0.0, 3.2]):
        make_box_local(f"HOVD_Door_Frame_{door_i+1}", col_ext, (dx, -35.4, 2.5), (2.4, 0.3, 4.2), mat_stone)
        make_box_local(f"HOVD_Door_Bronze_{door_i+1}", col_ext, (dx, -35.35, 1.8), (2.0, 0.1, 2.8), mat_bronze)
        make_box_local(f"HOVD_Door_Transom_{door_i+1}", col_ext, (dx, -35.35, 3.6), (2.0, 0.08, 0.8), mat_glass)
        make_box_local(f"HOVD_Door_Handle_{door_i+1}", col_ext, (dx, -35.28, 1.8), (0.1, 0.05, 0.4), mat_gold)

    # Grand Granite Entrance Staircase (12 Steps leading down to plaza grade)
    for step_i in range(12):
        sz = 1.8 * (12 - step_i) / 12.0
        sy = -41.5 - (step_i * 0.6)
        sw = 20.0 - (step_i * 0.2)
        make_box_local(f"HOVD_Grand_Step_{step_i+1}", col_site, (0.0, sy, sz/2), (sw, 0.6, sz), mat_granite_steps)

    # Flanking Limestone Step Balustrades & Urns
    for s_sign, side_n in [(-1, "W"), (1, "E")]:
        bx = s_sign * 10.2
        make_box_local(f"HOVD_Balustrade_{side_n}", col_site, (bx, -45.0, 1.4), (0.8, 8.0, 1.2), mat_stone)
        make_box_local(f"HOVD_Urn_Ped_{side_n}", col_site, (bx, -48.8, 0.6), (1.2, 1.2, 1.2), mat_stone)
        make_cylinder_local(f"HOVD_Urn_{side_n}", col_site, (bx, -48.8, 1.5), 0.5, 0.6, mat_bronze)
        make_cylinder_local(f"HOVD_Urn_Shrub_{side_n}", col_site, (bx, -48.8, 1.9), 0.55, 0.4, mat_brick)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIORS (52_Hovde_Hall_Interiors)
    # All Finished Floors Elevated to Z = 0.40m!
    # =========================================================================
    print("Building Part 2: Photorealistic Interiors...")

    # -------------------------------------------------------------------------
    # 1. ART DECO GRAND ROTUNDA & MARBLE FOYER (Ground Floor Center)
    # Local: X in [-9.5, +9.5], Y in [-14.0, +14.0], Z = 0.40 to 7.8m (2-story volume)
    # -------------------------------------------------------------------------
    print("Building Art Deco Grand Rotunda...")
    # Floor slab in polished cream marble tile
    make_box_local("HOVD_Rotunda_Floor_Base", col_int, (0.0, 0.0, 0.40), (19.0, 28.0, 0.20), mat_marble_cream)
    make_box_local("HOVD_Rotunda_Ceiling", col_int, (0.0, 0.0, 7.75), (19.0, 28.0, 0.10), mat_plaster_ivory)

    # Central Circular Terrazzo Purdue Seal Medallion
    make_cylinder_local("HOVD_Rotunda_Seal_Medallion", col_int, (0.0, 0.0, 0.51), 2.2, 0.02, mat_terrazzo)
    make_cylinder_local("HOVD_Rotunda_Seal_Gold_Ring_Outer", col_int, (0.0, 0.0, 0.52), 2.24, 0.02, mat_gold)
    make_cylinder_local("HOVD_Rotunda_Seal_Gold_Ring_Inner", col_int, (0.0, 0.0, 0.525), 1.6, 0.02, mat_gold)
    make_box_local("HOVD_Rotunda_Seal_Center_P", col_int, (0.0, 0.0, 0.53), (1.4, 0.9, 0.02), mat_gold)

    # Marble perimeter wall border
    make_box_local("HOVD_Rotunda_Border_N", col_int, (0.0, 13.5, 0.51), (18.6, 0.8, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_S", col_int, (0.0, -13.5, 0.51), (18.6, 0.8, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_E", col_int, (9.0, 0.0, 0.51), (0.8, 27.6, 0.02), mat_marble_gray)
    make_box_local("HOVD_Rotunda_Border_W", col_int, (-9.0, 0.0, 0.51), (0.8, 27.6, 0.02), mat_marble_gray)

    # North Enclosing Corridor Wall & 3 Arched Double Portals at Y = +14.0
    make_box_local("HOVD_Rotunda_North_Wall", col_int, (0.0, 14.0, 2.3), (19.0, 0.4, 3.8), mat_stone)
    for portal_x in [-5.5, 0.0, 5.5]:
        make_box_local(f"HOVD_Rotunda_NDoor_{portal_x}", col_int, (portal_x, 13.9, 1.8), (2.4, 0.2, 2.8), mat_walnut)
        make_box_local(f"HOVD_Rotunda_NDoor_Kick_{portal_x}", col_int, (portal_x, 13.85, 0.7), (2.3, 0.1, 0.4), mat_bronze)
        make_box_local(f"HOVD_Rotunda_NTransom_{portal_x}", col_int, (portal_x, 13.9, 3.5), (2.4, 0.1, 0.7), mat_glass)

    # South Wall (Interior face of entrance doors)
    make_box_local("HOVD_Rotunda_South_Wall", col_int, (0.0, -14.0, 2.3), (19.0, 0.4, 3.8), mat_stone)

    # Twin Sweeping Marble Staircases to Floor 2 (East and West sides)
    for side_sign, s_name in [(-1, "W"), (1, "E")]:
        sx = side_sign * 7.5
        for st_i in range(18):
            st_z = 0.4 + (st_i * 0.21)
            st_y = -8.0 + (st_i * 0.8)
            make_box_local(f"HOVD_Stair_{s_name}_{st_i+1}", col_int, (sx, st_y, st_z), (2.4, 0.8, 0.21), mat_marble_cream)
            make_cylinder_local(f"HOVD_Baluster_{s_name}_{st_i+1}", col_int, (sx + (side_sign * -1.1), st_y, st_z + 0.5), 0.03, 0.9, mat_bronze)
        make_box_local(f"HOVD_Handrail_{s_name}", col_int, (sx + (side_sign * -1.1), -1.0, 2.5), (0.12, 14.8, 0.08), mat_walnut)

    # 2nd Floor Mezzanine Promenade (Z = 4.2 to 4.4m)
    make_box_local("HOVD_Rotunda_Mezzanine", col_int, (0.0, 7.0, 4.2), (18.6, 14.0, 0.2), mat_marble_cream)
    make_box_local("HOVD_Mezzanine_Railing", col_int, (0.0, 0.0, 4.75), (14.0, 0.1, 0.9), mat_bronze)

    # Dual Multi-Tier Art Deco Brass Ring Chandeliers
    for cy in [-5.0, 5.0]:
        make_cylinder_local(f"HOVD_Chandelier_Rod_{cy}", col_int, (0.0, cy, 7.0), 0.05, 1.5, mat_brass)
        make_cylinder_local(f"HOVD_Chandelier_Ring1_{cy}", col_int, (0.0, cy, 6.2), 1.8, 0.12, mat_brass)
        make_cylinder_local(f"HOVD_Chandelier_Ring2_{cy}", col_int, (0.0, cy, 5.8), 1.2, 0.10, mat_brass)
        make_cylinder_local(f"HOVD_Chandelier_Bowl_{cy}", col_int, (0.0, cy, 5.5), 0.6, 0.25, mat_brass)
        
        for ang_deg in range(0, 360, 45):
            rad = math.radians(ang_deg)
            lx = 1.8 * math.cos(rad)
            ly = cy + 1.8 * math.sin(rad)
            make_box_local(f"HOVD_Chandelier_Bulb_{cy}_{ang_deg}", col_int, (lx, ly, 6.2), (0.15, 0.15, 0.2), mat_warm_glow)
        
        l_data = bpy.data.lights.new(name=f"HOVD_Rotunda_Light_Data_{cy}", type='POINT')
        l_data.energy = 5500.0
        l_data.color = (1.0, 0.92, 0.82)
        l_obj = bpy.data.objects.new(f"HOVD_Rotunda_Light_{cy}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (0.0, cy, 5.5)
        col_int.objects.link(l_obj)

    # Historic Bronze PWA Dedication Plaques
    for py, pname in [(-10.0, "South"), (10.0, "North")]:
        make_box_local(f"HOVD_Plaque_{pname}", col_int, (-9.05, py, 2.2), (0.08, 1.2, 1.8), mat_bronze)

    # -------------------------------------------------------------------------
    # 2. THE OFFICE OF THE UNIVERSITY PRESIDENT (Floor 2 South Wing)
    # Local: X in [-9.5, +9.5], Y in [-34.0, -16.0], Z = 4.40 to 8.2m
    # -------------------------------------------------------------------------
    print("Building Office of the University President...")
    make_box_local("HOVD_Pres_Floor", col_int, (0.0, -25.0, 4.40), (19.0, 18.0, 0.20), mat_walnut)
    make_box_local("HOVD_Pres_Ceiling", col_int, (0.0, -25.0, 8.15), (19.0, 18.0, 0.10), mat_plaster_ivory)

    # Dark Walnut Wainscoting
    make_box_local("HOVD_Pres_Wainscot_N", col_int, (0.0, -16.2, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_S", col_int, (0.0, -33.8, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_E", col_int, (9.2, -25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)
    make_box_local("HOVD_Pres_Wainscot_W", col_int, (-9.2, -25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)

    # Persian Area Rug
    make_box_local("HOVD_Pres_Rug", col_int, (0.0, -27.5, 4.51), (12.0, 8.0, 0.02), mat_leather_burgundy)

    # Monumental Executive Mahogany Partner Desk (centered at Y = -27.5)
    make_box_local("HOVD_Pres_Desk_Top", col_int, (0.0, -27.5, 5.25), (4.2, 2.2, 0.10), mat_mahogany)
    make_box_local("HOVD_Pres_Desk_Ped_L", col_int, (-1.5, -27.5, 4.85), (0.9, 1.9, 0.70), mat_walnut)
    make_box_local("HOVD_Pres_Desk_Ped_R", col_int, (1.5, -27.5, 4.85), (0.9, 1.9, 0.70), mat_walnut)
    make_box_local("HOVD_Pres_Desk_Blotter", col_int, (0.0, -27.5, 5.31), (2.2, 1.4, 0.02), mat_green_glass)
    
    # Brass Banker's Lamp
    make_box_local("HOVD_Pres_Lamp_Base", col_int, (1.2, -27.5, 5.34), (0.3, 0.3, 0.06), mat_brass)
    make_box_local("HOVD_Pres_Lamp_Stem", col_int, (1.2, -27.5, 5.55), (0.05, 0.05, 0.40), mat_brass)
    make_box_local("HOVD_Pres_Lamp_Shade", col_int, (1.2, -27.5, 5.75), (0.45, 0.25, 0.14), mat_green_glass)
    make_box_local("HOVD_Pres_Lamp_Bulb", col_int, (1.2, -27.5, 5.70), (0.35, 0.15, 0.05), mat_warm_glow)
    
    # Banker's lamp point light
    bl_data = bpy.data.lights.new(name="HOVD_Pres_Banker_Light_Data", type='POINT')
    bl_data.energy = 450.0
    bl_data.color = (1.0, 0.92, 0.65)
    bl_obj = bpy.data.objects.new("HOVD_Pres_Banker_Light", bl_data)
    bl_obj.parent = root_obj
    bl_obj.location = (1.2, -27.5, 5.8)
    col_int.objects.link(bl_obj)

    make_box_local("HOVD_Pres_Desk_Seal", col_int, (-1.2, -27.5, 5.34), (0.35, 0.35, 0.04), mat_gold)
    make_box_local("HOVD_Pres_Desk_Phone", col_int, (-1.3, -26.9, 5.33), (0.3, 0.35, 0.08), mat_leather_black)
    make_box_local("HOVD_Pres_Desk_Binder", col_int, (0.0, -26.9, 5.32), (0.45, 0.35, 0.04), mat_walnut)

    # President's Executive High-Back Leather Swivel Chair
    make_box_local("HOVD_Pres_Chair_Seat", col_int, (0.0, -29.2, 4.95), (0.95, 0.95, 0.15), mat_leather_black)
    make_box_local("HOVD_Pres_Chair_Back", col_int, (0.0, -29.6, 5.65), (0.90, 0.18, 1.15), mat_leather_black)
    make_box_local("HOVD_Pres_Chair_Arm_L", col_int, (-0.45, -29.2, 5.30), (0.10, 0.70, 0.08), mat_walnut)
    make_box_local("HOVD_Pres_Chair_Arm_R", col_int, (0.45, -29.2, 5.30), (0.10, 0.70, 0.08), mat_walnut)
    make_cylinder_local("HOVD_Pres_Chair_Base", col_int, (0.0, -29.2, 4.65), 0.45, 0.45, mat_brass)

    # Visitor Guest Chairs in front of desk
    for vx, v_name in [(-1.2, "L"), (1.2, "R")]:
        make_box_local(f"HOVD_Pres_Guest_Seat_{v_name}", col_int, (vx, -25.6, 4.90), (0.75, 0.75, 0.12), mat_leather_burgundy)
        make_box_local(f"HOVD_Pres_Guest_Back_{v_name}", col_int, (vx, -25.2, 5.40), (0.70, 0.15, 0.85), mat_leather_burgundy)
        make_box_local(f"HOVD_Pres_Guest_Legs_{v_name}", col_int, (vx, -25.6, 4.65), (0.65, 0.65, 0.45), mat_walnut)

    # Lounge Seating Area along West Wall
    make_box_local("HOVD_Chesterfield_Sofa_Seat", col_int, (-6.5, -21.0, 4.85), (1.1, 2.6, 0.45), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_Sofa_Back", col_int, (-7.1, -21.0, 5.35), (0.3, 2.6, 0.65), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_Chair_Seat", col_int, (-4.8, -23.5, 4.85), (1.1, 1.1, 0.45), mat_leather_burgundy)
    make_box_local("HOVD_Chesterfield_Chair_Back", col_int, (-4.8, -24.1, 5.35), (1.1, 0.3, 0.65), mat_leather_burgundy)
    make_cylinder_local("HOVD_Coffee_Table", col_int, (-4.8, -21.0, 4.75), 0.9, 0.45, mat_mahogany)

    # Fireplace on North Wall
    make_box_local("HOVD_Pres_Fireplace_Mantel", col_int, (0.0, -16.5, 5.6), (4.2, 0.8, 1.8), mat_stone)
    make_box_local("HOVD_Pres_Firebox", col_int, (0.0, -16.3, 5.1), (2.2, 0.4, 1.1), mat_leather_black)
    make_box_local("HOVD_Pres_Embers", col_int, (0.0, -16.3, 4.7), (1.8, 0.3, 0.2), mat_warm_glow)
    make_box_local("HOVD_Pres_Mantel_Clock", col_int, (0.0, -16.5, 6.7), (0.8, 0.2, 0.5), mat_gold)

    # Flags Display
    make_cylinder_local("HOVD_Flag_US_Pole", col_int, (-5.5, -31.5, 6.2), 0.05, 3.4, mat_brass)
    make_box_local("HOVD_Flag_US_Banner", col_int, (-5.5, -31.5, 6.8), (0.05, 1.2, 1.8), mat_flag_us)
    make_cylinder_local("HOVD_Flag_IN_Pole", col_int, (5.5, -31.5, 6.2), 0.05, 3.4, mat_brass)
    make_box_local("HOVD_Flag_IN_Banner", col_int, (5.5, -31.5, 6.8), (0.05, 1.2, 1.8), mat_flag_in)

    # Presidential Portrait Gallery
    for i, py in enumerate(range(-30, -18, 3)):
        make_box_local(f"HOVD_Portrait_{i+1}", col_int, (9.05, py, 6.4), (0.08, 1.6, 2.0), mat_gold)
        make_box_local(f"HOVD_Portrait_Light_{i+1}", col_int, (8.9, py, 7.5), (0.15, 0.8, 0.1), mat_brass)

    # President's Office Ceiling Ambient Glow
    p_light_data = bpy.data.lights.new(name="HOVD_Pres_Light_Data", type='POINT')
    p_light_data.energy = 5200.0
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

    # Wainscoting
    make_box_local("HOVD_Board_Wainscot_N", col_int, (0.0, 33.8, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_S", col_int, (0.0, 16.2, 5.1), (18.6, 0.3, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_E", col_int, (9.2, 25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)
    make_box_local("HOVD_Board_Wainscot_W", col_int, (-9.2, 25.0, 5.1), (0.3, 17.6, 1.4), mat_walnut)

    # Monumental 24-Seat Boat-Shaped Mahogany Boardroom Table
    make_box_local("HOVD_Board_Table_Center", col_int, (0.0, 25.0, 5.25), (3.2, 13.5, 0.08), mat_mahogany)
    make_box_local("HOVD_Board_Table_Edge_E", col_int, (1.62, 25.0, 5.24), (0.06, 13.5, 0.09), mat_walnut)
    make_box_local("HOVD_Board_Table_Edge_W", col_int, (-1.62, 25.0, 5.24), (0.06, 13.5, 0.09), mat_walnut)

    for py in [19.5, 23.0, 27.0, 30.5]:
        make_box_local(f"HOVD_Board_Table_Ped_{py}", col_int, (0.0, py, 4.85), (1.8, 0.7, 0.70), mat_walnut)
    
    # 24 Articulated Executive Chairs & Delegate Microphones
    for chair_i, cy in enumerate(range(19, 31, 2)):
        # West Chairs
        make_box_local(f"HOVD_Chair_Seat_W_{chair_i}", col_int, (-2.1, cy, 4.95), (0.75, 0.75, 0.12), mat_leather_black)
        make_box_local(f"HOVD_Chair_Back_W_{chair_i}", col_int, (-2.45, cy, 5.55), (0.12, 0.70, 0.95), mat_leather_black)
        make_box_local(f"HOVD_Chair_Arm_W1_{chair_i}", col_int, (-2.1, cy - 0.35, 5.30), (0.50, 0.08, 0.06), mat_walnut)
        make_box_local(f"HOVD_Chair_Arm_W2_{chair_i}", col_int, (-2.1, cy + 0.35, 5.30), (0.50, 0.08, 0.06), mat_walnut)
        make_cylinder_local(f"HOVD_Chair_Base_W_{chair_i}", col_int, (-2.1, cy, 4.65), 0.35, 0.45, mat_chrome)
        
        make_cylinder_local(f"HOVD_Mic_Base_W_{chair_i}", col_int, (-1.25, cy, 5.31), 0.08, 0.02, mat_bronze)
        make_cylinder_local(f"HOVD_Mic_Stalk_W_{chair_i}", col_int, (-1.20, cy, 5.45), 0.012, 0.25, mat_bronze)
        make_cylinder_local(f"HOVD_Mic_Head_W_{chair_i}", col_int, (-1.15, cy, 5.58), 0.02, 0.04, mat_mic_tally)
        make_box_local(f"HOVD_Portfolio_W_{chair_i}", col_int, (-0.85, cy, 5.305), (0.45, 0.35, 0.02), mat_leather_burgundy)

        # East Chairs
        make_box_local(f"HOVD_Chair_Seat_E_{chair_i}", col_int, (2.1, cy, 4.95), (0.75, 0.75, 0.12), mat_leather_black)
        make_box_local(f"HOVD_Chair_Back_E_{chair_i}", col_int, (2.45, cy, 5.55), (0.12, 0.70, 0.95), mat_leather_black)
        make_box_local(f"HOVD_Chair_Arm_E1_{chair_i}", col_int, (2.1, cy - 0.35, 5.30), (0.50, 0.08, 0.06), mat_walnut)
        make_box_local(f"HOVD_Chair_Arm_E2_{chair_i}", col_int, (2.1, cy + 0.35, 5.30), (0.50, 0.08, 0.06), mat_walnut)
        make_cylinder_local(f"HOVD_Chair_Base_E_{chair_i}", col_int, (2.1, cy, 4.65), 0.35, 0.45, mat_chrome)

        make_cylinder_local(f"HOVD_Mic_Base_E_{chair_i}", col_int, (1.25, cy, 5.31), 0.08, 0.02, mat_bronze)
        make_cylinder_local(f"HOVD_Mic_Stalk_E_{chair_i}", col_int, (1.20, cy, 5.45), 0.012, 0.25, mat_bronze)
        make_cylinder_local(f"HOVD_Mic_Head_E_{chair_i}", col_int, (1.15, cy, 5.58), 0.02, 0.04, mat_mic_tally)
        make_box_local(f"HOVD_Portfolio_E_{chair_i}", col_int, (0.85, cy, 5.305), (0.45, 0.35, 0.02), mat_leather_burgundy)

    for head_y, h_name, sign_y in [(17.6, "South", -1), (32.4, "North", 1)]:
        make_box_local(f"HOVD_Chair_Head_{h_name}", col_int, (0.0, head_y, 4.95), (0.80, 0.80, 0.12), mat_leather_black)
        make_box_local(f"HOVD_Back_Head_{h_name}", col_int, (0.0, head_y + (0.35 * sign_y), 5.55), (0.75, 0.12, 0.95), mat_leather_black)
        make_cylinder_local(f"HOVD_Base_Head_{h_name}", col_int, (0.0, head_y, 4.65), 0.35, 0.45, mat_chrome)

    # 3D Gold Purdue Seal on North Feature Wall
    make_cylinder_local("HOVD_Board_Gold_Seal_Ring", col_int, (0.0, 33.65, 6.6), 1.3, 0.06, mat_gold, rot_local=(math.radians(90), 0, 0))
    make_box_local("HOVD_Board_Gold_Seal_Emblem", col_int, (0.0, 33.60, 6.6), (1.8, 0.04, 1.8), mat_gold)
    make_box_local("HOVD_Board_Acoustic_Panel", col_int, (0.0, 33.72, 6.6), (6.5, 0.06, 2.8), mat_walnut)

    # Trustee Witness Lectern
    make_box_local("HOVD_Lectern_Body", col_int, (-4.2, 25.0, 5.0), (0.8, 0.8, 1.2), mat_mahogany)
    make_box_local("HOVD_Lectern_Top", col_int, (-4.2, 25.0, 5.62), (0.9, 0.9, 0.05), mat_walnut)
    make_box_local("HOVD_Lectern_Seal", col_int, (-3.78, 25.0, 5.2), (0.04, 0.35, 0.35), mat_gold)

    # Dual 120" Screens
    make_box_local("HOVD_Screen_E", col_int, (9.1, 25.0, 6.5), (0.05, 3.2, 1.8), mat_screen_emissive)
    make_box_local("HOVD_Screen_W", col_int, (-9.1, 25.0, 6.5), (0.05, 3.2, 1.8), mat_screen_emissive)

    # Boardroom Overhead Lighting
    b_light_data = bpy.data.lights.new(name="HOVD_Board_Light_Data", type='POINT')
    b_light_data.energy = 5500.0
    b_light_data.color = (1.0, 0.95, 0.88)
    b_light_obj = bpy.data.objects.new("HOVD_Board_Light", b_light_data)
    b_light_obj.parent = root_obj
    b_light_obj.location = (0.0, 25.0, 7.4)
    col_int.objects.link(b_light_obj)

    # =========================================================================
    # PART 3: CIVIC PLAZA & MEMORIAL MALL SITE INTEGRATION (53_Hovde_Hall_Plaza_and_Site)
    # =========================================================================
    print("Building Part 3: Hovde Hall Plaza & Site Integration...")

    # South Memorial Mall Arrival Concourse
    make_box_local("HOVD_Plaza_Paving", col_site, (0.0, -56.0, 0.05), (36.0, 24.0, 0.1), mat_granite_steps)

    # Symmetrical Bedford Limestone Planters with Boxwoods
    make_box_local("HOVD_Planter_L", col_site, (-11.5, -46.0, 0.5), (4.5, 3.0, 0.8), mat_stone)
    make_box_local("HOVD_Planter_R", col_site, (11.5, -46.0, 0.5), (4.5, 3.0, 0.8), mat_stone)

    # Teak Benches
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_walnut
    for bx in [-8.0, 8.0]:
        make_box_local(f"HOVD_Bench_{bx}", col_site, (bx, -50.0, 0.45), (2.4, 0.7, 0.55), bench_mat)

    # Bicycle Racks
    for rx in range(-6, 7, 2):
        make_box_local(f"HOVD_Bike_Rack_{rx}", col_site, (rx, -58.0, 0.45), (0.1, 1.2, 0.9), mat_bronze)

    # Victorian Cast-Iron Lanterns
    for lx, ly in [(-13.0, -44.0), (13.0, -44.0), (-13.0, -60.0), (13.0, -60.0)]:
        make_box_local(f"HOVD_Lantern_Post_{lx}_{ly}", col_site, (lx, ly, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box_local(f"HOVD_Lantern_Head_{lx}_{ly}", col_site, (lx, ly, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        
        l_data = bpy.data.lights.new(name=f"HOVD_Lantern_Light_Data_{lx}_{ly}", type='POINT')
        l_data.energy = 1600.0
        l_data.color = (1.0, 0.90, 0.75)
        l_obj = bpy.data.objects.new(f"HOVD_Lantern_Light_{lx}_{ly}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (lx, ly, 4.2)
        col_site.objects.link(l_obj)

    # =========================================================================
    # PART 4: BULLETPROOF CAMERA CALIBRATION WITH EXPLICIT WORLD MATRIX
    # =========================================================================
    print("Calibrating 5 Precision Inspection Cameras with Explicit M_WORLD Matrix...")

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
        print(f"Calibrated {name} at {loc_world} -> target {target_world} (lens={lens}mm)")
        return cam_obj

    def local_to_world_explicit(local_coord):
        return M_WORLD @ mathutils.Vector(local_coord)

    # 1. Cam_77: South Hero View from Memorial Mall
    # Local: (-3.0, -64.0, 3.6) -> Target: (0.0, -38.5, 7.8), lens=28.0
    cam77_loc = local_to_world_explicit((-3.0, -64.0, 3.6))
    cam77_target = local_to_world_explicit((0.0, -38.5, 7.8))
    set_camera("Cam_77_Hovde_South_Hero", cam77_loc, cam77_target, lens=28.0)

    # 2. Cam_78: Office of the University President Interior
    # Local: (5.5, -20.5, 5.8) -> Target: (-0.5, -27.5, 5.3), lens=24.0
    cam78_loc = local_to_world_explicit((5.5, -20.5, 5.8))
    cam78_target = local_to_world_explicit((-0.5, -27.5, 5.3))
    set_camera("Cam_78_Hovde_President_Office_Interior", cam78_loc, cam78_target, lens=24.0)

    # 3. Cam_79: Board of Trustees Boardroom Interior
    # Local: (-6.0, 18.5, 6.2) -> Target: (0.5, 27.0, 5.3), lens=24.0
    cam79_loc = local_to_world_explicit((-6.0, 18.5, 6.2))
    cam79_target = local_to_world_explicit((0.5, 27.0, 5.3))
    set_camera("Cam_79_Hovde_BoardOfTrustees_Interior", cam79_loc, cam79_target, lens=24.0)

    # 4. Cam_80: Art Deco Grand Rotunda & Marble Foyer
    # Local: (-5.5, -9.0, 1.8) -> Target: (1.0, 3.5, 3.5), lens=22.0
    cam80_loc = local_to_world_explicit((-5.5, -9.0, 1.8))
    cam80_target = local_to_world_explicit((1.0, 3.5, 3.5))
    set_camera("Cam_80_Hovde_ArtDeco_Rotunda_Interior", cam80_loc, cam80_target, lens=22.0)

    # 5. Cam_81: Precinct Aerial View
    # Local: (45.0, -85.0, 60.0) -> Target: (-5.0, 5.0, 6.0), lens=28.0
    cam81_loc = local_to_world_explicit((45.0, -85.0, 60.0))
    cam81_target = local_to_world_explicit((-5.0, 5.0, 6.0))
    set_camera("Cam_81_Hovde_Mall_Centennial_Aerial", cam81_loc, cam81_target, lens=28.0)

    print("=== Hovde Hall Refinement Build Completed Successfully! ===")

if __name__ == "__main__":
    run()
