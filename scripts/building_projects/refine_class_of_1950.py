"""
Refinement & Gold Standard Polish for Class of 1950 Lecture Hall (CL50 - 1990)
- Enhanced Oval Drive Colonnade & Hero Perspective (Cam 82)
- Flawless CL50 224 470-Seat Tiered Auditorium with 50-ft Chalkboard & Widescreen Displays (Cam 83)
- Polished Cream Terrazzo Atrium & Einstein Bros Bagels Service Counter (Cam 84)
- 2nd Floor Gallery & "The Way It Was" Bronze Sculpture by John Seward Johnson Jr. (Cam 85)
- Expansive Oval Drive & Memorial Mall Precinct Aerial Panorama (Cam 86)
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Refining Class of 1950 Lecture Hall (CL50) to Gold Standard Exemplar ===")

    # Ensure collections exist
    col_ext = bpy.data.collections.get("54_Class_of_1950_Exterior")
    col_int = bpy.data.collections.get("55_Class_of_1950_Interiors")
    col_site = bpy.data.collections.get("56_Class_of_1950_Plaza_and_Site")

    if not col_ext:
        col_ext = bpy.data.collections.new("54_Class_of_1950_Exterior")
        bpy.context.scene.collection.children.link(col_ext)
    if not col_int:
        col_int = bpy.data.collections.new("55_Class_of_1950_Interiors")
        bpy.context.scene.collection.children.link(col_int)
    if not col_site:
        col_site = bpy.data.collections.new("56_Class_of_1950_Plaza_and_Site")
        bpy.context.scene.collection.children.link(col_site)

    # Purge existing CL50 objects inside these collections to do a clean high-detail rebuild
    for col in [col_ext, col_int, col_site]:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Re-use or find CL50_Root
    root_obj = bpy.data.objects.get("CL50_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("CL50_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        bpy.context.scene.collection.objects.link(root_obj)

    root_loc = (-115.19, -116.95, 0.0)
    root_obj.location = root_loc
    root_obj.rotation_euler = (0, 0, 0)

    # Explicit transformation matrix M for guaranteed world space conversions:
    M_WORLD = mathutils.Matrix.Translation(root_loc)

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
    mat_bronze = get_mat("CL50_Bronze_Sculpture", (0.28, 0.20, 0.14, 1.0), roughness=0.35, metallic=0.88)
    mat_chrome = get_mat("CL50_Chrome_Metal", (0.95, 0.95, 0.95, 1.0), roughness=0.10, metallic=0.98)
    mat_oak = get_mat("CL50_Oak_Tables", (0.60, 0.40, 0.20, 1.0), roughness=0.32, specular=0.6)
    mat_dark_oak = get_mat("CL50_Stage_Dark_Oak", (0.22, 0.12, 0.06, 1.0), roughness=0.30, specular=0.7)
    mat_chalkboard = get_mat("CL50_Porcelain_Chalkboard", (0.12, 0.18, 0.14, 1.0), roughness=0.45, specular=0.25)
    mat_chalk_white = get_mat("CL50_Chalk_White", (0.95, 0.95, 0.92, 1.0), roughness=0.90)
    mat_terrazzo = get_mat("CL50_Terrazzo_Cream", (0.88, 0.87, 0.84, 1.0), roughness=0.08, specular=0.98)
    mat_terrazzo_gray = get_mat("CL50_Terrazzo_Border", (0.35, 0.35, 0.38, 1.0), roughness=0.10, specular=0.95)
    mat_navy_carpet = get_mat("CL50_Auditorium_Navy_Carpet", (0.05, 0.08, 0.20, 1.0), roughness=0.92)
    mat_seat_navy = get_mat("CL50_Seat_Cushion_Navy", (0.08, 0.12, 0.32, 1.0), roughness=0.60, specular=0.35)
    mat_screen_emissive = get_mat("CL50_Projector_Screen_Emissive", (0.95, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.95, 0.95, 1.0, 4.2))
    mat_warm_glow = get_mat("CL50_Warm_Glow", (1.0, 0.88, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.60, 5.0))
    mat_einstein_yellow = get_mat("CL50_Einstein_Yellow", (0.95, 0.75, 0.10, 1.0), roughness=0.35)
    mat_einstein_counter = get_mat("CL50_Einstein_Quartz", (0.92, 0.92, 0.90, 1.0), roughness=0.15, specular=0.9)
    mat_plaster_ivory = get_mat("CL50_Plaster_Ivory", (0.94, 0.93, 0.90, 1.0), roughness=0.45)
    mat_roof_gravel = get_mat("CL50_Roof_Membrane", (0.35, 0.34, 0.33, 1.0), roughness=0.85)
    mat_granite_paving = get_mat("CL50_Granite_Paving", (0.45, 0.44, 0.42, 1.0), roughness=0.5)

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
    # PART 1: EXTERIOR ENVELOPE & OVAL DRIVE COLONNADE (54_Class_of_1950_Exterior)
    # Dimensions: Width 43.8m (X in [-21.9, +21.9]), Depth 37.8m (Y in [-18.9, +18.9]), Height 16.0m
    # =========================================================================
    print("Building Part 1: Class of 1950 Exterior Envelopes & Colonnade...")

    # True Hollow Perimeter Architectural Envelopes:
    # 1. East Facade facing Oval Drive (X_local = +21.9)
    make_box_local("CL50_Wall_East_Upper", col_ext, (21.9 - 0.35, 0.0, 13.5), (0.7, 37.8, 5.0), mat_brick)
    make_box_local("CL50_CurtainWall_East", col_ext, (21.9 - 0.1, 0.0, 8.5), (0.2, 36.0, 4.8), mat_glass)
    make_box_local("CL50_Beltcourse_East_Mid", col_ext, (21.9 + 0.05, 0.0, 6.1), (0.4, 38.0, 0.4), mat_stone)
    make_box_local("CL50_Beltcourse_East_Roof", col_ext, (21.9 + 0.05, 0.0, 16.0), (0.4, 38.0, 0.4), mat_stone)

    # Colossal Brick Colonnade Piers on Ground Floor along Oval Drive (X = 21.6)
    for pi, py in enumerate(range(-18, 19, 6)):
        make_box_local(f"CL50_Colonnade_Pier_{pi+1}", col_ext, (21.6, py, 3.0), (1.4, 1.4, 6.0), mat_brick)
        make_box_local(f"CL50_Colonnade_Plinth_{pi+1}", col_ext, (21.6, py, 0.4), (1.6, 1.6, 0.8), mat_stone)
        make_box_local(f"CL50_Colonnade_Cap_{pi+1}", col_ext, (21.6, py, 5.9), (1.6, 1.6, 0.3), mat_stone)

    # Southwest Corner Column with 1950 Time Capsule Plaque
    make_box_local("CL50_Corner_SW_Column", col_ext, (-21.0, -18.0, 8.0), (2.0, 2.0, 16.0), mat_brick)
    make_box_local("CL50_Time_Capsule_Plaque", col_ext, (-21.0, -19.05, 1.8), (0.8, 0.08, 0.6), mat_bronze)

    # 2. West Facade facing Peirce Hall (X_local = -21.9)
    make_box_local("CL50_Wall_West", col_ext, (-21.9 + 0.35, 0.0, 8.0), (0.7, 37.8, 16.0), mat_brick)
    make_box_local("CL50_Base_West", col_ext, (-21.9 + 0.3, 0.0, 0.75), (0.8, 38.0, 1.5), mat_stone)
    for z_c in [6.1, 11.2, 16.0]:
        make_box_local(f"CL50_Beltcourse_West_{z_c}", col_ext, (-21.9 + 0.3, 0.0, z_c), (0.8, 38.0, 0.35), mat_stone)

    # 3. North Facade facing Psychological Sciences (Y_local = +18.9)
    make_box_local("CL50_Wall_North", col_ext, (0.0, 18.9 - 0.35, 8.0), (43.8, 0.7, 16.0), mat_brick)
    make_box_local("CL50_Base_North", col_ext, (0.0, 18.9 - 0.3, 0.75), (44.0, 0.8, 1.5), mat_stone)
    for z_c in [6.1, 11.2, 16.0]:
        make_box_local(f"CL50_Beltcourse_North_{z_c}", col_ext, (0.0, 18.9 - 0.3, z_c), (44.0, 0.8, 0.35), mat_stone)

    # 4. South Facade facing Stanley Coulter Hall (Y_local = -18.9)
    make_box_local("CL50_Wall_South", col_ext, (0.0, -18.9 + 0.35, 8.0), (43.8, 0.7, 16.0), mat_brick)
    make_box_local("CL50_Base_South", col_ext, (0.0, -18.9 + 0.3, 0.75), (44.0, 0.8, 1.5), mat_stone)
    for z_c in [6.1, 11.2, 16.0]:
        make_box_local(f"CL50_Beltcourse_South_{z_c}", col_ext, (0.0, -18.9 + 0.3, z_c), (44.0, 0.8, 0.35), mat_stone)

    # Roof Slab & Parapet Coping
    make_box_local("CL50_Roof_Slab", col_ext, (0.0, 0.0, 16.1), (43.4, 37.4, 0.3), mat_roof_gravel)
    make_box_local("CL50_Penthouse", col_ext, (-5.0, 0.0, 17.5), (18.0, 16.0, 2.8), mat_stone)
    make_box_local("CL50_Penthouse_Louvers", col_ext, (-5.0, 8.05, 17.5), (12.0, 0.2, 2.0), mat_bronze)

    # 3D Gold Building Lettering on East Entrance Canopy Lintel: "CLASS OF 1950 LECTURE HALL"
    make_box_local("CL50_Entrance_Canopy", col_ext, (22.5, 0.0, 6.2), (3.5, 16.0, 0.4), mat_stone)
    make_box_local("CL50_Sign_Plaque", col_ext, (24.2, 0.0, 6.2), (0.1, 14.5, 0.6), mat_stone)
    try:
        fnt_curve = bpy.data.curves.new(type="FONT", name="CL50_Gold_Text_Curve")
        fnt_curve.body = "CLASS OF 1950 LECTURE HALL"
        fnt_curve.size = 0.55
        fnt_curve.extrude = 0.06
        fnt_curve.align_x = 'CENTER'
        fnt_curve.align_y = 'CENTER'
        txt_obj = bpy.data.objects.new("CL50_Gold_Letters", fnt_curve)
        txt_obj.parent = root_obj
        txt_obj.location = (24.28, 0.0, 6.2)
        txt_obj.rotation_euler = (math.radians(90), 0, math.radians(90))
        col_ext.objects.link(txt_obj)
        txt_obj.data.materials.append(mat_gold)
    except Exception as e:
        print(f"Font fallback: {e}")
        make_box_local("CL50_Sign_Fallback", col_ext, (24.28, 0.0, 6.2), (0.06, 13.0, 0.5), mat_gold)

    # Ground-Floor Glass Entrance Vestibule
    make_box_local("CL50_Entrance_Glass_Wall", col_ext, (20.0, 0.0, 3.0), (0.2, 18.0, 5.8), mat_glass)
    for door_y in [-3.5, 0.0, 3.5]:
        make_box_local(f"CL50_Door_Frame_{door_y}", col_ext, (20.0, door_y, 2.2), (0.3, 2.4, 4.0), mat_stone)
        make_box_local(f"CL50_Door_Glass_{door_y}", col_ext, (20.0, door_y, 1.8), (0.1, 2.0, 3.2), mat_glass)
        make_box_local(f"CL50_Door_Handle_{door_y}", col_ext, (20.12, door_y, 1.8), (0.05, 0.1, 0.4), mat_gold)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIORS (55_Class_of_1950_Interiors)
    # Finished Floor Elevated to Z = 0.40m!
    # =========================================================================
    print("Building Part 2: Photorealistic Interiors...")

    # -------------------------------------------------------------------------
    # 1. CL50 224: THE LEGENDARY 470-SEAT TIERED AUDITORIUM
    # Spans X in [-20.0, +4.0], Y in [-17.0, +17.0], Z = 0.40 to 8.2m
    # -------------------------------------------------------------------------
    print("Building CL50 224 Tiered Lecture Auditorium...")
    
    make_box_local("CL50_Aud_Floor", col_int, (-8.0, 0.0, 0.40), (24.0, 34.0, 0.2), mat_navy_carpet)
    make_box_local("CL50_Aud_Ceiling", col_int, (-8.0, 0.0, 8.15), (24.0, 34.0, 0.1), mat_plaster_ivory)
    make_box_local("CL50_Aud_Wall_East_Partition", col_int, (4.0, 0.0, 4.25), (0.4, 34.0, 7.7), mat_stone)

    # Front Presentation Stage / Dais on West End (X in [-20.0, -15.5])
    make_box_local("CL50_Stage_Deck", col_int, (-17.5, 0.0, 0.65), (4.5, 24.0, 0.50), mat_dark_oak)
    make_box_local("CL50_Stage_Steps_N", col_int, (-15.0, 11.0, 0.55), (1.5, 2.0, 0.30), mat_dark_oak)
    make_box_local("CL50_Stage_Steps_S", col_int, (-15.0, -11.0, 0.55), (1.5, 2.0, 0.30), mat_dark_oak)

    # Monumental 50-Foot Porcelain Chalkboard System on West Stage Wall
    make_box_local("CL50_50ft_Chalkboard_Frame", col_int, (-19.65, 0.0, 2.6), (0.15, 15.6, 3.0), mat_oak)
    make_box_local("CL50_50ft_Chalkboard_Board", col_int, (-19.58, 0.0, 2.6), (0.05, 15.24, 2.7), mat_chalkboard)
    make_box_local("CL50_Chalk_Rail", col_int, (-19.50, 0.0, 1.22), (0.12, 15.24, 0.06), mat_oak)
    # Realistic chalk formula & welcome notes
    make_box_local("CL50_Chalk_Notes", col_int, (-19.54, 0.0, 2.5), (0.02, 10.0, 1.2), mat_chalk_white)

    # Dual 150" Motorized Projection Screens above Chalkboards
    for sy, s_name in [(-4.5, "South"), (4.5, "North")]:
        make_box_local(f"CL50_Screen_{s_name}", col_int, (-19.50, sy, 5.2), (0.06, 4.2, 2.4), mat_screen_emissive)
        make_box_local(f"CL50_Screen_Housing_{s_name}", col_int, (-19.50, sy, 6.45), (0.2, 4.4, 0.2), mat_stone)

    # Smart Instructor Presentation Lectern / Podium (shifted to Y = 2.5 so center stage is open!)
    make_box_local("CL50_Lectern_Body", col_int, (-16.0, 2.5, 1.45), (0.9, 1.2, 1.1), mat_oak)
    make_box_local("CL50_Lectern_Top", col_int, (-16.0, 2.5, 2.02), (1.0, 1.3, 0.06), mat_dark_oak)
    make_box_local("CL50_Lectern_Screen", col_int, (-16.1, 2.5, 2.10), (0.35, 0.5, 0.04), mat_screen_emissive)
    make_cylinder_local("CL50_Lectern_Mic", col_int, (-15.8, 2.2, 2.15), 0.015, 0.25, mat_bronze)
    make_box_local("CL50_Lectern_Purdue_Seal", col_int, (-15.52, 2.5, 1.55), (0.04, 0.45, 0.45), mat_gold)

    # 10 Stepped Seating Tiers Rising from Stage eastward (X = -13.5 to +2.0)
    for tier_i in range(10):
        tx = -13.5 + (tier_i * 1.55)
        tz = 0.40 + (tier_i * 0.48)
        
        make_box_local(f"CL50_Riser_{tier_i+1}", col_int, (tx, 0.0, tz / 2.0), (1.55, 28.0, tz), mat_navy_carpet)
        make_box_local(f"CL50_Desk_{tier_i+1}", col_int, (tx - 0.25, 0.0, tz + 0.72), (0.45, 26.0, 0.06), mat_oak)
        make_box_local(f"CL50_Desk_Leg_L_{tier_i+1}", col_int, (tx - 0.25, -12.0, tz + 0.36), (0.08, 0.08, 0.70), mat_chrome)
        make_box_local(f"CL50_Desk_Leg_R_{tier_i+1}", col_int, (tx - 0.25, 12.0, tz + 0.36), (0.08, 0.08, 0.70), mat_chrome)
        
        for chair_i, cy in enumerate(range(-12, 13, 2)):
            if abs(cy) < 1.5:
                continue
            make_box_local(f"CL50_Seat_{tier_i+1}_{chair_i}", col_int, (tx + 0.35, cy, tz + 0.45), (0.50, 0.50, 0.08), mat_seat_navy)
            make_box_local(f"CL50_Back_{tier_i+1}_{chair_i}", col_int, (tx + 0.55, cy, tz + 0.75), (0.08, 0.45, 0.55), mat_seat_navy)
            make_cylinder_local(f"CL50_Post_{tier_i+1}_{chair_i}", col_int, (tx + 0.35, cy, tz + 0.22), 0.04, 0.42, mat_chrome)

    # Stepped Center Aisle with Safety Handrails
    for ai in range(10):
        ax = -13.5 + (ai * 1.55)
        az = 0.40 + (ai * 0.48)
        make_box_local(f"CL50_Aisle_Step_{ai+1}", col_int, (ax, 0.0, az - 0.12), (1.55, 2.4, 0.24), mat_navy_carpet)
        make_box_local(f"CL50_Aisle_Rail_L_{ai+1}", col_int, (ax, -1.2, az + 0.5), (1.55, 0.06, 0.9), mat_chrome)
        make_box_local(f"CL50_Aisle_Rail_R_{ai+1}", col_int, (ax, 1.2, az + 0.5), (1.55, 0.06, 0.9), mat_chrome)

    # Overhead Auditorium Lighting
    for sx in [-16.0, -10.0, -4.0, 1.0]:
        for sy in [-8.0, 0.0, 8.0]:
            l_data = bpy.data.lights.new(name=f"CL50_Light_Data_{sx}_{sy}", type='POINT')
            l_data.energy = 4200.0 if sx == -16.0 else 2600.0
            l_data.color = (1.0, 0.95, 0.88)
            l_obj = bpy.data.objects.new(f"CL50_Light_{sx}_{sy}", l_data)
            l_obj.parent = root_obj
            l_obj.location = (sx, sy, 7.4)
            col_int.objects.link(l_obj)

    # -------------------------------------------------------------------------
    # 2. GROUND FLOOR STUDENT ATRIUM & EINSTEIN BROS BAGELS
    # Spans X in [+4.5, +21.0], Y in [-17.0, +17.0], Z = 0.40 to 4.2m
    # -------------------------------------------------------------------------
    print("Building Ground Floor Atrium & Einstein Bros Bagels...")
    
    make_box_local("CL50_Lobby_Floor", col_int, (12.5, 0.0, 0.40), (16.5, 34.0, 0.2), mat_terrazzo)
    make_box_local("CL50_Lobby_Ceiling", col_int, (12.5, 0.0, 4.15), (16.5, 34.0, 0.1), mat_plaster_ivory)
    make_box_local("CL50_Lobby_Border_E", col_int, (20.0, 0.0, 0.51), (0.6, 33.6, 0.02), mat_terrazzo_gray)
    make_box_local("CL50_Lobby_Border_W", col_int, (4.8, 0.0, 0.51), (0.6, 33.6, 0.02), mat_terrazzo_gray)

    # Einstein Bros Bagels Service Counter (centered at X = 10.0, Y = -9.0)
    make_box_local("CL50_Einstein_Base", col_int, (10.0, -9.0, 1.0), (1.4, 7.5, 1.0), mat_oak)
    make_box_local("CL50_Einstein_Countertop", col_int, (10.0, -9.0, 1.52), (1.5, 7.6, 0.06), mat_einstein_counter)
    make_box_local("CL50_Einstein_Display_1", col_int, (10.0, -10.5, 1.85), (0.9, 2.2, 0.60), mat_glass)
    make_box_local("CL50_Einstein_Display_2", col_int, (10.0, -8.0, 1.85), (0.9, 2.2, 0.60), mat_glass)
    make_box_local("CL50_Einstein_POS_1", col_int, (10.2, -6.5, 1.7), (0.35, 0.4, 0.3), mat_chrome)
    make_box_local("CL50_Einstein_POS_2", col_int, (10.2, -12.0, 1.7), (0.35, 0.4, 0.3), mat_chrome)
    
    for uy in [-5.0, -4.2, -3.4]:
        make_cylinder_local(f"CL50_Coffee_Urn_{uy}", col_int, (10.0, uy, 1.85), 0.22, 0.65, mat_chrome)
        
    make_box_local("CL50_Einstein_Header", col_int, (10.0, -9.0, 3.4), (0.2, 7.6, 0.8), mat_einstein_yellow)
    make_box_local("CL50_Einstein_Menu_1", col_int, (10.12, -10.5, 3.4), (0.05, 2.0, 0.65), mat_screen_emissive)
    make_box_local("CL50_Einstein_Menu_2", col_int, (10.12, -7.5, 3.4), (0.05, 2.0, 0.65), mat_screen_emissive)

    # Student Collaborative Cafe Seating: High-Top Tables & Barstools
    for tx in [14.0, 17.5]:
        for ty in [-8.0, -3.0, 2.0, 7.0]:
            make_cylinder_local(f"CL50_HighTable_{tx}_{ty}", col_int, (tx, ty, 1.35), 0.65, 0.05, mat_oak)
            make_cylinder_local(f"CL50_HighLeg_{tx}_{ty}", col_int, (tx, ty, 0.88), 0.06, 0.90, mat_chrome)
            for sx, sy in [(-0.55, 0), (0.55, 0), (0, -0.55), (0, 0.55)]:
                make_cylinder_local(f"CL50_Stool_{tx+sx}_{ty+sy}", col_int, (tx + sx, ty + sy, 0.82), 0.20, 0.06, mat_seat_navy)
                make_cylinder_local(f"CL50_StoolLeg_{tx+sx}_{ty+sy}", col_int, (tx + sx, ty + sy, 0.60), 0.03, 0.40, mat_chrome)

    make_box_local("CL50_Trash_Station", col_int, (18.5, 12.0, 1.0), (0.8, 2.6, 1.1), mat_chrome)
    make_box_local("CL50_Trash_Sign", col_int, (18.5, 12.0, 1.6), (0.7, 2.4, 0.1), mat_einstein_yellow)

    # Ambient Atrium Lighting
    for ay in [-8.0, 0.0, 8.0]:
        a_data = bpy.data.lights.new(name=f"CL50_Atr_Light_Data_{ay}", type='POINT')
        a_data.energy = 3600.0
        a_data.color = (1.0, 0.94, 0.88)
        a_obj = bpy.data.objects.new(f"CL50_Atr_Light_{ay}", a_data)
        a_obj.parent = root_obj
        a_obj.location = (14.0, ay, 3.8)
        col_int.objects.link(a_obj)

    # -------------------------------------------------------------------------
    # 3. SECOND FLOOR GALLERY & "THE WAY IT WAS" BRONZE SCULPTURE
    # Spans X in [+4.5, +21.0], Y in [-17.0, +17.0], Z = 4.40 to 8.2m
    # -------------------------------------------------------------------------
    print("Building Second Floor Gallery & Bronze Sculpture...")
    
    make_box_local("CL50_Gallery_Floor", col_int, (12.5, 0.0, 4.40), (16.5, 34.0, 0.2), mat_terrazzo)
    make_box_local("CL50_Gallery_Ceiling", col_int, (12.5, 0.0, 8.15), (16.5, 34.0, 0.1), mat_plaster_ivory)
    make_box_local("CL50_Mezzanine_Balustrade", col_int, (4.6, 0.0, 5.0), (0.1, 33.6, 1.0), mat_chrome)

    # Life-Size 700-Pound Bronze Sculpture: "The Way It Was" by John Seward Johnson Jr.
    # Sited at X = 13.5, Y = 5.0, Z = 4.60m
    make_box_local("CL50_Seward_Bench_Seat", col_int, (13.5, 5.0, 4.95), (0.8, 2.4, 0.08), mat_oak)
    make_box_local("CL50_Seward_Bench_Back", col_int, (13.1, 5.0, 5.45), (0.08, 2.4, 0.85), mat_oak)
    make_box_local("CL50_Seward_Bench_Legs", col_int, (13.5, 5.0, 4.72), (0.7, 2.2, 0.40), mat_bronze)
    
    # Classmate 1 (Seated Veteran Student with Books)
    make_box_local("CL50_Sculpt_Figure1_Torso", col_int, (13.5, 4.4, 5.60), (0.45, 0.45, 0.65), mat_bronze)
    make_cylinder_local("CL50_Sculpt_Figure1_Head", col_int, (13.5, 4.4, 6.10), 0.14, 0.28, mat_bronze)
    make_box_local("CL50_Sculpt_Figure1_Legs", col_int, (13.7, 4.4, 5.05), (0.40, 0.40, 0.50), mat_bronze)
    make_box_local("CL50_Sculpt_Books", col_int, (13.5, 5.0, 5.05), (0.35, 0.45, 0.14), mat_bronze)

    # Classmate 2 (Seated Veteran Student Conversing)
    make_box_local("CL50_Sculpt_Figure2_Torso", col_int, (13.5, 5.6, 5.60), (0.45, 0.45, 0.65), mat_bronze)
    make_cylinder_local("CL50_Sculpt_Figure2_Head", col_int, (13.5, 5.6, 6.10), 0.14, 0.28, mat_bronze)
    make_box_local("CL50_Sculpt_Figure2_Legs", col_int, (13.7, 5.6, 5.05), (0.40, 0.40, 0.50), mat_bronze)

    # Bronze Dedication Plaque on Marble Pedestal
    make_box_local("CL50_Seward_Plaque_Pedestal", col_int, (13.5, 6.8, 4.8), (0.5, 0.5, 0.8), mat_stone)
    make_box_local("CL50_Seward_Plaque_Plate", col_int, (13.5, 6.8, 5.25), (0.4, 0.4, 0.04), mat_bronze)

    # Dedicated Museum Accent Spotlight on "The Way It Was"
    m_spot = bpy.data.lights.new(name="CL50_Sculpt_Spot_Data", type='SPOT')
    m_spot.energy = 3400.0
    m_spot.spot_size = math.radians(45)
    m_spot.color = (1.0, 0.96, 0.88)
    m_obj = bpy.data.objects.new("CL50_Sculpt_Spot", m_spot)
    m_obj.parent = root_obj
    m_obj.location = (13.5, 5.0, 7.5)
    col_int.objects.link(m_obj)

    # Ambient Gallery Lights
    for gy in [-10.0, 0.0, 10.0]:
        g_data = bpy.data.lights.new(name=f"CL50_Gal_Light_Data_{gy}", type='POINT')
        g_data.energy = 3600.0
        g_data.color = (1.0, 0.94, 0.88)
        g_obj = bpy.data.objects.new(f"CL50_Gal_Light_{gy}", g_data)
        g_obj.parent = root_obj
        g_obj.location = (14.0, gy, 7.2)
        col_int.objects.link(g_obj)

    # =========================================================================
    # PART 3: CIVIC PLAZA & OVAL DRIVE / MEMORIAL MALL SITE INTEGRATION (56_Class_of_1950_Plaza_and_Site)
    # =========================================================================
    print("Building Part 3: Class of 1950 Plaza & Site Integration...")

    # Oval Drive Arrival Concourse
    make_box_local("CL50_Plaza_Paving", col_site, (29.0, 0.0, 0.05), (16.0, 36.0, 0.1), mat_granite_paving)

    # Symmetrical Bedford Limestone Planters with Boxwoods
    make_box_local("CL50_Planter_N", col_site, (27.0, 14.0, 0.5), (5.0, 4.0, 0.8), mat_stone)
    make_box_local("CL50_Planter_S", col_site, (27.0, -14.0, 0.5), (5.0, 4.0, 0.8), mat_stone)

    # Campus Teak Wood Benches
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_oak
    for by in [-8.0, 8.0]:
        make_box_local(f"CL50_Bench_{by}", col_site, (28.0, by, 0.45), (0.7, 2.4, 0.55), bench_mat)

    # Bank of 12 Sheffield Bicycle Racks
    for ry in range(-6, 7, 2):
        make_box_local(f"CL50_Bike_Rack_{ry}", col_site, (33.0, ry, 0.45), (1.2, 0.1, 0.9), mat_bronze)

    # Victorian Cast-Iron Campus Lantern Posts with Warm Luminaires
    for lx, ly in [(25.0, -16.0), (25.0, 16.0), (34.0, -12.0), (34.0, 12.0)]:
        make_box_local(f"CL50_Lantern_Post_{lx}_{ly}", col_site, (lx, ly, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box_local(f"CL50_Lantern_Head_{lx}_{ly}", col_site, (lx, ly, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        
        l_data = bpy.data.lights.new(name=f"CL50_Lantern_Light_Data_{lx}_{ly}", type='POINT')
        l_data.energy = 1600.0
        l_data.color = (1.0, 0.90, 0.75)
        l_obj = bpy.data.objects.new(f"CL50_Lantern_Light_{lx}_{ly}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (lx, ly, 4.2)
        col_site.objects.link(l_obj)

    # =========================================================================
    # PART 4: PRECISION-CALIBRATED INSPECTION CAMERAS
    # 5 Dedicated Inspection Cameras with Explicit M_WORLD Matrix
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

    # 1. Cam_82: Oval Drive Hero Arrival View
    # Stepped back to frame the colossal brick piers, entrance canopy, 3D gold letters, 2nd-floor ribbon glass, and arrival plaza
    cam82_loc = local_to_world_explicit((44.0, -12.0, 4.2))
    cam82_target = local_to_world_explicit((20.0, 0.0, 7.0))
    set_camera("Cam_82_CL50_OvalDrive_Hero", cam82_loc, cam82_target, lens=28.0)

    # 2. Cam_83: CL50 224 Tiered Auditorium (Rear Upper Tier Overlook)
    # Elevated slightly to look cleanly down across all 10 tiers of desks and seats at the 50-ft chalkboard and dual screens
    cam83_loc = local_to_world_explicit((3.2, 9.2, 6.4))
    cam83_target = local_to_world_explicit((-16.5, -0.5, 2.2))
    set_camera("Cam_83_CL50_224_Auditorium_Interior", cam83_loc, cam83_target, lens=24.0)

    # 3. Cam_84: Ground Floor Student Atrium & Einstein Bros Bagels
    # 3/4 perspective across polished cream terrazzo floor showing high-top tables, blue stools, and bagel service counter
    cam84_loc = local_to_world_explicit((18.0, 9.5, 2.2))
    cam84_target = local_to_world_explicit((10.0, -8.5, 1.8))
    set_camera("Cam_84_CL50_EinsteinBagels_Atrium_Interior", cam84_loc, cam84_target, lens=24.0)

    # 4. Cam_85: Second Floor Gallery & "The Way It Was" Bronze Sculpture
    # Dramatic museum perspective featuring the two 1950 veteran classmates on the bench, books, plaque, spotlight, and balustrade
    cam85_loc = local_to_world_explicit((16.4, 1.8, 5.7))
    cam85_target = local_to_world_explicit((13.5, 5.0, 5.3))
    set_camera("Cam_85_CL50_Stage_Instructor_Interior", cam85_loc, cam85_target, lens=28.0)

    # 5. Cam_86: Memorial Mall & Oval Drive Precinct Aerial
    # Panoramic aerial view framing CL50 connecting Oval Drive, Memorial Mall, Stanley Coulter, and Peirce Hall
    cam86_loc = local_to_world_explicit((64.0, -48.0, 56.0))
    cam86_target = local_to_world_explicit((-5.0, 0.0, 7.0))
    set_camera("Cam_86_CL50_MemorialMall_Precinct_Aerial", cam86_loc, cam86_target, lens=28.0)

    print("=== Class of 1950 Refinement Build Completed Successfully! ===")

if __name__ == "__main__":
    run()
