"""
Purdue University Digital Twin - Mathematical Sciences Building (MATH - 1967) Builder
Location: 150 N. University St, West Lafayette, IN (Center: X = -180.62m, Y = -127.29m, Z = 0.0m)
Bounds: X in [-199.27, -161.97] (37.30m), Y in [-161.37, -93.21] (68.17m), Z in [0.00, 36.30m]
Architect: Scholer Corporation (1965-1967). 10 stories + mechanical penthouse + communications mast.
"""

import bpy
import bmesh
import math
import mathutils

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

def run_build():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened master blend successfully.")

    # 1. Purge / remove old placeholder
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    old_placeholder = bpy.data.objects.get("Mathematical Sciences Building (MATH)")
    if old_placeholder and massing_col:
        print(f"Removing old placeholder: {old_placeholder.name}")
        massing_col.objects.unlink(old_placeholder)
        bpy.data.objects.remove(old_placeholder, do_unlink=True)

    # 2. Setup Collections
    def get_or_create_col(name, parent=None):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            if parent:
                parent.children.link(col)
            else:
                bpy.context.scene.collection.children.link(col)
        return col

    col_ext = get_or_create_col("60_Math_Sciences_Exterior")
    col_int = get_or_create_col("61_Math_Sciences_Interiors")
    col_site = get_or_create_col("62_Math_Sciences_Plaza_and_Site")
    col_cams = get_or_create_col("00_Inspection_Cameras")

    # Clear existing objects in these collections if re-running
    for c in [col_ext, col_int, col_site]:
        for o in list(c.objects):
            c.objects.unlink(o)
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Create Root Anchor
    root_obj = bpy.data.objects.new("MATH_Root", None)
    root_obj.location = (-180.62, -127.29, 0.0)
    col_ext.objects.link(root_obj)

    # 4. Materials Setup
    def get_or_create_mat(name, color, roughness=0.5, metallic=0.0, transmission=0.0, emission=None, emission_strength=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if not bsdf:
                bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = transmission
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = transmission
            if emission:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission
        return mat

    mat_brick = bpy.data.materials.get("Purdue_Red_Brick") or get_or_create_mat("MATH_Purdue_Red_Brick", (0.38, 0.14, 0.10, 1.0), roughness=0.75)
    mat_concrete = get_or_create_mat("MATH_Precast_Concrete", (0.76, 0.75, 0.72, 1.0), roughness=0.65)
    mat_dark_concrete = get_or_create_mat("MATH_BoardFormed_Concrete", (0.45, 0.44, 0.42, 1.0), roughness=0.70)
    mat_limestone = get_or_create_mat("MATH_Bedford_Limestone", (0.82, 0.80, 0.75, 1.0), roughness=0.60)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_or_create_mat("MATH_Ribbon_Glass", (0.05, 0.08, 0.12, 1.0), roughness=0.05, transmission=0.85)
    mat_bronze = bpy.data.materials.get("Elliott_ArtDeco_Bronze") or get_or_create_mat("MATH_Dark_Bronze", (0.20, 0.16, 0.12, 1.0), roughness=0.35, metallic=0.85)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_or_create_mat("MATH_Purdue_Gold", (0.85, 0.68, 0.22, 1.0), roughness=0.25, metallic=0.90)
    mat_terrazzo = get_or_create_mat("MATH_Terrazzo_Cream", (0.85, 0.83, 0.79, 1.0), roughness=0.18)
    mat_terrazzo_dark = get_or_create_mat("MATH_Terrazzo_Charcoal", (0.22, 0.22, 0.24, 1.0), roughness=0.22)
    mat_carpet_navy = get_or_create_mat("MATH_Navy_Carpet", (0.04, 0.08, 0.18, 1.0), roughness=0.90)
    mat_walnut = get_or_create_mat("MATH_Dark_Walnut", (0.16, 0.09, 0.05, 1.0), roughness=0.35)
    mat_honey_oak = get_or_create_mat("MATH_Honey_Oak", (0.55, 0.38, 0.20, 1.0), roughness=0.40)
    mat_blackboard = get_or_create_mat("MATH_Blackboard_Porcelain", (0.06, 0.12, 0.08, 1.0), roughness=0.45)
    mat_chalk = get_or_create_mat("MATH_Chalk_Emissive", (0.95, 0.98, 0.95, 1.0), roughness=0.8, emission=(0.95, 0.98, 0.95, 1.0), emission_strength=1.5)
    mat_leather_burgundy = get_or_create_mat("MATH_Leather_Burgundy", (0.22, 0.04, 0.06, 1.0), roughness=0.38)
    mat_persian_rug = get_or_create_mat("MATH_Persian_Rug", (0.35, 0.08, 0.10, 1.0), roughness=0.85)
    mat_green_glass = get_or_create_mat("MATH_Bankers_Green_Glass", (0.02, 0.35, 0.12, 1.0), roughness=0.15, transmission=0.75, emission=(0.05, 0.60, 0.20, 1.0), emission_strength=2.0)
    mat_brass = get_or_create_mat("MATH_Polished_Brass", (0.90, 0.75, 0.30, 1.0), roughness=0.20, metallic=0.95)
    mat_screen_white = get_or_create_mat("MATH_Screen_White", (0.92, 0.92, 0.92, 1.0), roughness=0.85, emission=(0.95, 0.95, 0.95, 1.0), emission_strength=1.2)
    mat_roof_gravel = get_or_create_mat("MATH_Roof_Gravel", (0.40, 0.40, 0.40, 1.0), roughness=0.90)

    # Helper mesh creator
    def create_box(name, col, loc, size, mat=None, parent=root_obj):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        if col != bpy.context.scene.collection:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        return obj

    def create_cylinder(name, col, loc, radius, depth, mat=None, parent=root_obj, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        if col != bpy.context.scene.collection:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        return obj

    # Bounding Box reference:
    # CX = -180.62, CY = -127.29
    # Width X = 37.3m, Length Y = 68.17m, Height Z = 36.3m
    # We will build relative to local origin (0, 0, 0) of MATH_Root!
    # Local X in [-18.65, +18.65] (width 37.3m)
    # Local Y in [-34.08, +34.08] (length 68.17m)
    # Local Z in [0.00, 36.30]

    print("Building 60_Math_Sciences_Exterior...")

    # 1. Ground Floor Recessed Foundation Slab
    create_box("MATH_Ground_Slab", col_ext, (0, 0, 0.20), (37.3, 68.17, 0.40), mat_dark_concrete)

    # 2. Massive Concrete Pilotis / Colonnade (Ground Floor: Z = 0.4m to 4.2m)
    # 14 colossal pilotis supporting the 9-story tower overhand
    pilotis_x = [-17.2, -11.5, -5.7, 0.0, 5.7, 11.5, 17.2]
    pilotis_y = [-32.5, 32.5]
    for px in pilotis_x:
        for py in pilotis_y:
            create_box(f"MATH_Pilotis_Y_{px:.1f}_{py:.1f}", col_ext, (px, py, 2.3), (1.4, 1.2, 3.8), mat_dark_concrete)

    pilotis_x_sides = [-17.2, 17.2]
    pilotis_y_intermediate = [-21.5, -10.8, 0.0, 10.8, 21.5]
    for px in pilotis_x_sides:
        for py in pilotis_y_intermediate:
            create_box(f"MATH_Pilotis_X_{px:.1f}_{py:.1f}", col_ext, (px, py, 2.3), (1.2, 1.4, 3.8), mat_dark_concrete)

    # 3. Ground Floor Recessed Glass Lobby Envelope
    # Set back 2.2m from the column line
    create_box("MATH_Lobby_CurtainWall_North", col_ext, (0, 30.5, 2.3), (32.0, 0.25, 3.8), mat_glass)
    create_box("MATH_Lobby_CurtainWall_South", col_ext, (0, -30.5, 2.3), (32.0, 0.25, 3.8), mat_glass)
    create_box("MATH_Lobby_CurtainWall_East", col_ext, (15.5, 0, 2.3), (0.25, 61.0, 3.8), mat_glass)
    create_box("MATH_Lobby_CurtainWall_West", col_ext, (-15.5, 0, 2.3), (0.25, 61.0, 3.8), mat_glass)

    # Ground floor entrance vestibules & canopies (East towards Memorial Mall, West towards University St)
    # West entrance canopy
    create_box("MATH_Entrance_Canopy_West", col_ext, (-18.6, 0, 4.2), (4.5, 8.0, 0.4), mat_limestone)
    # East entrance canopy
    create_box("MATH_Entrance_Canopy_East", col_ext, (18.6, 0, 4.2), (4.5, 8.0, 0.4), mat_limestone)

    # 3D Lettering on Canopies
    for side, pos_x, rot_z in [("West", -18.65, math.pi), ("East", 18.65, 0)]:
        bpy.ops.object.text_add(location=(pos_x, -3.2, 4.45), rotation=(math.pi/2, 0, rot_z + math.pi/2))
        txt = bpy.context.active_object
        txt.name = f"MATH_Signage_{side}"
        txt.data.body = "MATHEMATICAL SCIENCES BUILDING"
        txt.data.size = 0.32
        txt.data.extrude = 0.04
        txt.data.materials.append(mat_gold)
        txt.parent = root_obj
        col_ext.objects.link(txt)
        bpy.context.scene.collection.objects.unlink(txt)

    # 4. Brick Utility & Vertical Circulation Cores (East and West End Blocks)
    # East Brick Core (housing elevators, stairs, utilities)
    create_box("MATH_East_Brick_Core", col_ext, (16.8, 0, 18.6), (3.7, 68.17, 28.8), mat_brick)
    create_box("MATH_East_Limestone_Parapet", col_ext, (16.8, 0, 33.2), (3.8, 68.3, 0.4), mat_limestone)

    # West Brick Core (housing stairs, utilities)
    create_box("MATH_West_Brick_Core", col_ext, (-16.8, 0, 18.6), (3.7, 68.17, 28.8), mat_brick)
    create_box("MATH_West_Limestone_Parapet", col_ext, (-16.8, 0, 33.2), (3.8, 68.3, 0.4), mat_limestone)

    # 5. Floors 2 through 10 Tower Envelope & Concrete Sunshade Grid (Floors 2-10: Z = 4.2m to 33.0m)
    # Floor height = 3.2m per story. 9 stories = 28.8m
    floor_height = 3.2
    # Continuous concrete floor spandrels along North & South facades
    for floor_idx in range(10): # Z from 4.2 to 33.0
        fz = 4.2 + floor_idx * floor_height
        # North spandrel
        create_box(f"MATH_Spandrel_North_{floor_idx}", col_ext, (0, 34.0, fz), (30.0, 0.6, 0.5), mat_concrete)
        # South spandrel
        create_box(f"MATH_Spandrel_South_{floor_idx}", col_idx := col_ext, (0, -34.0, fz), (30.0, 0.6, 0.5), mat_concrete)

    # Concrete Vertical Solar Fins / Shadow Boxes (15 vertical fins across North and South facades)
    fin_xs = [-14.0 + i * 2.0 for i in range(15)]
    for i, fx in enumerate(fin_xs):
        # North facade fins
        create_box(f"MATH_Fin_North_{i}", col_ext, (fx, 34.2, 18.6), (0.25, 0.8, 28.8), mat_concrete)
        # South facade fins
        create_box(f"MATH_Fin_South_{i}", col_ext, (fx, -34.2, 18.6), (0.25, 0.8, 28.8), mat_concrete)

    # Recessed Ribbon Glazing behind fins (Floors 2 to 10)
    for floor_idx in range(9):
        mid_z = 4.2 + floor_idx * floor_height + floor_height / 2.0
        create_box(f"MATH_Ribbon_Glazing_North_{floor_idx+2}", col_ext, (0, 33.7, mid_z), (29.8, 0.15, 2.7), mat_glass)
        create_box(f"MATH_Ribbon_Glazing_South_{floor_idx+2}", col_ext, (0, -33.7, mid_z), (29.8, 0.15, 2.7), mat_glass)

    # 6. Roof Parapets, Gravel Deck & Mechanical Penthouse
    # Main roof deck (Z = 33.0m)
    create_box("MATH_Roof_Deck_Gravel", col_ext, (0, 0, 32.95), (37.1, 67.9, 0.3), mat_roof_gravel)
    create_box("MATH_Roof_Parapet_North", col_ext, (0, 34.0, 33.5), (30.0, 0.4, 0.8), mat_limestone)
    create_box("MATH_Roof_Parapet_South", col_ext, (0, -34.0, 33.5), (30.0, 0.4, 0.8), mat_limestone)

    # Rooftop Mechanical Penthouse (Z = 33.0m to 36.3m, height 3.3m)
    create_box("MATH_Rooftop_Penthouse_Base", col_ext, (0, 0, 34.65), (22.0, 42.0, 3.3), mat_brick)
    create_box("MATH_Rooftop_Penthouse_Copings", col_ext, (0, 0, 36.35), (22.4, 42.4, 0.3), mat_limestone)
    # Bronze HVAC louvers on Penthouse
    create_box("MATH_Penthouse_Louver_North", col_ext, (0, 21.05, 34.8), (18.0, 0.2, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_South", col_ext, (0, -21.05, 34.8), (18.0, 0.2, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_East", col_ext, (11.05, 0, 34.8), (0.2, 34.0, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_West", col_ext, (-11.05, 0, 34.8), (0.2, 34.0, 2.2), mat_bronze)

    # Steel Communications Antenna Mast (Z = 36.3m to 42.0m)
    create_cylinder("MATH_Communications_Mast", col_ext, (4.0, 8.0, 39.15), radius=0.18, depth=5.7, mat=mat_bronze)
    create_cylinder("MATH_Antenna_Spire", col_ext, (4.0, 8.0, 42.2), radius=0.06, depth=1.4, mat=mat_gold)

    print("Building 61_Math_Sciences_Interiors...")

    # INTERIOR 1: MATH 175 Major Tiered Lecture Hall (Ground Floor, Z = 0.4m to 4.2m)
    # Sited in South-West Ground Floor quadrant: X in [-14, 0], Y in [-28, -6]
    # Center: X = -7.0, Y = -17.0, Z = 0.40m
    create_box("MATH_175_Floor_Navy_Carpet", col_int, (-7.0, -17.0, 0.42), (13.5, 21.5, 0.05), mat_carpet_navy)
    create_box("MATH_175_Acoustic_Wall_West", col_int, (-13.8, -17.0, 2.3), (0.2, 21.5, 3.8), mat_honey_oak)
    create_box("MATH_175_Acoustic_Wall_East", col_int, (-0.2, -17.0, 2.3), (0.2, 21.5, 3.8), mat_honey_oak)
    create_box("MATH_175_Front_Wall_South", col_int, (-7.0, -27.8, 2.3), (13.5, 0.2, 3.8), mat_walnut)
    create_box("MATH_175_Rear_Wall_North", col_int, (-7.0, -6.2, 2.3), (13.5, 0.2, 3.8), mat_honey_oak)
    create_box("MATH_175_Ceiling", col_int, (-7.0, -17.0, 4.15), (13.5, 21.5, 0.1), mat_concrete)

    # 8 Stepped Seating Risers (rising from South front to North rear)
    # Tier height = 0.28m, Tier depth = 1.6m
    for tier_idx in range(8):
        tz = 0.45 + (tier_idx + 1) * 0.24
        ty = -22.5 + tier_idx * 1.8
        # Tier riser platform
        create_box(f"MATH_175_Riser_Tier_{tier_idx+1}", col_int, (-7.0, ty, (0.42 + tz)/2.0), (12.5, 1.7, tz - 0.42), mat_carpet_navy)
        # Continuous student oak desk
        create_box(f"MATH_175_Desk_Tier_{tier_idx+1}", col_int, (-7.0, ty - 0.4, tz + 0.38), (11.8, 0.45, 0.04), mat_honey_oak)
        # Stanchion supports for desks
        for sx in [-5.0, -2.5, 0.0, 2.5, 5.0]:
            create_cylinder(f"MATH_175_Desk_Leg_{tier_idx}_{sx}", col_int, (-7.0 + sx, ty - 0.4, tz + 0.19), radius=0.03, depth=0.38, mat=mat_bronze)
        # Articulated navy student swivel chairs (6 chairs per tier)
        for cx in [-4.8, -2.9, -1.0, 1.0, 2.9, 4.8]:
            chair_x = -7.0 + cx
            chair_y = ty + 0.25
            create_cylinder(f"MATH_175_Chair_Pedestal_{tier_idx}_{cx}", col_int, (chair_x, chair_y, tz + 0.18), radius=0.04, depth=0.36, mat=mat_bronze)
            create_box(f"MATH_175_Chair_Seat_{tier_idx}_{cx}", col_int, (chair_x, chair_y, tz + 0.38), (0.46, 0.44, 0.06), mat_carpet_navy)
            create_box(f"MATH_175_Chair_Back_{tier_idx}_{cx}", col_int, (chair_x, chair_y + 0.20, tz + 0.62), (0.44, 0.06, 0.42), mat_carpet_navy)

    # Front Lecture Stage Dais (South side)
    create_box("MATH_175_Stage_Dais", col_int, (-7.0, -26.0, 0.58), (12.5, 3.2, 0.32), mat_honey_oak)

    # Smart Instructor Podium with gold Purdue seal
    create_box("MATH_175_Smart_Podium", col_int, (-4.5, -25.5, 1.25), (0.9, 0.7, 1.1), mat_walnut)
    create_cylinder("MATH_175_Podium_Mic", col_int, (-4.5, -25.3, 1.85), radius=0.015, depth=0.3, mat=mat_brass)
    create_box("MATH_175_Podium_Seal", col_int, (-4.5, -25.86, 1.25), (0.35, 0.02, 0.35), mat_gold)

    # Quadruple Sliding Porcelain Blackboards (mounted on South front wall)
    create_box("MATH_175_Blackboard_Frame", col_int, (-7.0, -27.65, 2.2), (10.2, 0.06, 2.2), mat_honey_oak)
    for b_idx in range(4):
        bx = -10.5 + 1.4 + b_idx * 2.4
        create_box(f"MATH_175_Blackboard_Panel_{b_idx+1}", col_int, (bx, -27.62, 2.2), (2.25, 0.03, 2.0), mat_blackboard)

    # Chalk Formulas and Mathematical Proofs on Blackboards (Euler, Navier-Stokes, Riemann, Calculus)
    formulas = [
        "e^{i\\pi} + 1 = 0",
        "\\zeta(s) = \\sum n^{-s}",
        "\\rho(\\partial_t v + v\\cdot\\nabla v) = -\\nabla p + \\mu\\nabla^2 v",
        "\\int_a^b f'(x)dx = f(b) - f(a)"
    ]
    for b_idx, eq in enumerate(formulas):
        bx = -10.5 + 1.4 + b_idx * 2.4
        bpy.ops.object.text_add(location=(bx - 0.95, -27.60, 2.1), rotation=(math.pi/2, 0, 0))
        txt = bpy.context.active_object
        txt.name = f"MATH_175_Equation_{b_idx+1}"
        txt.data.body = eq
        txt.data.size = 0.22
        txt.data.extrude = 0.02
        txt.data.materials.append(mat_chalk)
        txt.parent = root_obj
        col_int.objects.link(txt)
        bpy.context.scene.collection.objects.unlink(txt)

    # Dual 120" Motorized Projection Screens
    for sx in [-9.2, -4.8]:
        create_box(f"MATH_175_Screen_Housing_{sx}", col_int, (sx, -27.65, 3.4), (2.8, 0.15, 0.15), mat_bronze)
        create_box(f"MATH_175_Screen_Display_{sx}", col_int, (sx, -27.63, 2.65), (2.6, 0.02, 1.4), mat_screen_white)

    # Ceiling Recessed Downlights in MATH 175
    for lx in [-10.0, -7.0, -4.0]:
        for ly in [-24.0, -18.0, -12.0]:
            light_data = bpy.data.lights.new(name=f"MATH_175_Light_{lx}_{ly}", type="POINT")
            light_data.energy = 800.0
            light_data.color = (1.0, 0.95, 0.88)
            light_data.shadow_soft_size = 0.4
            light_obj = bpy.data.objects.new(name=f"MATH_175_Light_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 3.9)
            col_int.objects.link(light_obj)

    # INTERIOR 2: Mathematical Sciences Library & Math Resource Room (Floor 3, Z = 10.6m to 13.8m)
    # Sited in North-East Floor 3 quadrant: X in [0, 15], Y in [6, 28]
    # Center: X = 7.5, Y = 17.0, Z = 10.60m
    create_box("MATH_Lib_Floor_Terrazzo", col_int, (7.5, 17.0, 10.62), (14.5, 21.5, 0.05), mat_terrazzo)
    create_box("MATH_Lib_Border_Terrazzo", col_int, (7.5, 17.0, 10.625), (14.5, 21.5, 0.04), mat_terrazzo_dark)
    create_box("MATH_Lib_Wall_West", col_int, (0.2, 17.0, 12.2), (0.2, 21.5, 3.1), mat_honey_oak)
    create_box("MATH_Lib_Wall_East", col_int, (14.8, 17.0, 12.2), (0.2, 21.5, 3.1), mat_glass)
    create_box("MATH_Lib_Wall_South", col_int, (7.5, 6.2, 12.2), (14.5, 0.2, 3.1), mat_honey_oak)
    create_box("MATH_Lib_Wall_North", col_int, (7.5, 27.8, 12.2), (14.5, 0.2, 3.1), mat_glass)
    create_box("MATH_Lib_Ceiling", col_int, (7.5, 17.0, 13.75), (14.5, 21.5, 0.1), mat_concrete)

    # 4 Double-sided Mahogany Book Stacks loaded with math monographs
    book_colors = [
        get_or_create_mat("Book_Navy", (0.05, 0.10, 0.30, 1.0), roughness=0.6),
        get_or_create_mat("Book_Crimson", (0.35, 0.05, 0.08, 1.0), roughness=0.6),
        get_or_create_mat("Book_Forest", (0.05, 0.25, 0.08, 1.0), roughness=0.6),
        get_or_create_mat("Book_Gold", (0.65, 0.50, 0.15, 1.0), roughness=0.6)
    ]
    for stack_idx in range(4):
        sy = 9.5 + stack_idx * 3.2
        # Stack structure
        create_box(f"MATH_Lib_Stack_{stack_idx+1}", col_int, (4.5, sy, 11.9), (6.5, 0.8, 2.5), mat_walnut)
        # Shelves & Books
        for shelf in range(4):
            sz = 10.9 + shelf * 0.6
            for b in range(12):
                bx = 1.8 + b * 0.45
                mat_b = book_colors[(stack_idx + shelf + b) % len(book_colors)]
                create_box(f"MATH_Lib_Book_{stack_idx}_{shelf}_{b}", col_int, (bx, sy, sz), (0.35, 0.65, 0.45), mat_b)
        # Brass aisle classification plaque
        create_box(f"MATH_Lib_Aisle_Tag_{stack_idx+1}", col_int, (1.2, sy, 12.8), (0.04, 0.35, 0.2), mat_brass)

    # 2 Collaborative Honey Oak Study Tables with Green Banker's Lamps & Laptops
    for t_idx, ty in enumerate([23.0, 26.0]):
        # Study Table
        create_box(f"MATH_Lib_Table_{t_idx+1}", col_int, (7.5, ty, 11.35), (7.0, 1.4, 0.06), mat_honey_oak)
        for tx in [4.2, 10.8]:
            for ty_leg in [ty - 0.5, ty + 0.5]:
                create_cylinder(f"MATH_Lib_Table_Leg_{t_idx}_{tx}_{ty_leg}", col_int, (tx, ty_leg, 10.98), radius=0.04, depth=0.70, mat=mat_bronze)
        # 4 Chairs per table
        for cx in [5.0, 6.8, 8.6, 10.0]:
            create_cylinder(f"MATH_Lib_Chair_Leg_{t_idx}_{cx}", col_int, (cx, ty - 0.9, 10.95), radius=0.03, depth=0.65, mat=mat_bronze)
            create_box(f"MATH_Lib_Chair_Seat_{t_idx}_{cx}", col_int, (cx, ty - 0.9, 11.30), (0.45, 0.45, 0.05), mat_walnut)
            create_box(f"MATH_Lib_Chair_Back_{t_idx}_{cx}", col_int, (cx, ty - 1.1, 11.55), (0.42, 0.05, 0.40), mat_walnut)
        # Glowing green-glass banker's lamps on tables
        for lx in [5.8, 9.2]:
            create_box(f"MATH_Lib_Bankers_Shade_{t_idx}_{lx}", col_int, (lx, ty, 11.65), (0.28, 0.16, 0.12), mat_green_glass)
            create_cylinder(f"MATH_Lib_Bankers_Stand_{t_idx}_{lx}", col_int, (lx, ty, 11.48), radius=0.02, depth=0.22, mat=mat_brass)
            lamp_data = bpy.data.lights.new(name=f"MATH_Lib_Bankers_Light_{t_idx}_{lx}", type="POINT")
            lamp_data.energy = 220.0
            lamp_data.color = (0.75, 1.0, 0.75)
            lamp_obj = bpy.data.objects.new(name=f"MATH_Lib_Bankers_Light_{t_idx}_{lx}", object_data=lamp_data)
            lamp_obj.location = (-180.62 + lx, -127.29 + ty, 11.70)
            col_int.objects.link(lamp_obj)
        # Open student laptops with emissive screens
        create_box(f"MATH_Lib_Laptop_Base_{t_idx}", col_int, (7.5, ty + 0.3, 11.40), (0.35, 0.25, 0.02), mat_bronze)
        create_box(f"MATH_Lib_Laptop_Screen_{t_idx}", col_int, (7.5, ty + 0.42, 11.54), (0.35, 0.02, 0.24), mat_screen_white)

    # Ceiling illumination in Library
    for lx in [4.0, 8.0, 12.0]:
        for ly in [10.0, 18.0, 24.0]:
            light_data = bpy.data.lights.new(name=f"MATH_Lib_Ceiling_Light_{lx}_{ly}", type="POINT")
            light_data.energy = 600.0
            light_data.color = (1.0, 0.98, 0.92)
            light_obj = bpy.data.objects.new(name=f"MATH_Lib_Ceiling_Light_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 13.5)
            col_int.objects.link(light_obj)

    # INTERIOR 3: 10th-Floor Faculty Colloquium Sky Lounge (Floor 10, Z = 29.8m to 33.0m)
    # Sited across Floor 10 with panoramic 360 ribbon glass
    # Center: X = 0.0, Y = 0.0, Z = 29.80m
    create_box("MATH_10th_Floor_Walnut_Parquet", col_int, (0, 0, 29.82), (28.0, 56.0, 0.05), mat_walnut)
    create_box("MATH_10th_Persian_Rug", col_int, (0, 0, 29.85), (8.5, 14.0, 0.04), mat_persian_rug)
    create_box("MATH_10th_Ceiling", col_int, (0, 0, 32.95), (28.0, 56.0, 0.1), mat_concrete)
    # Feature partition walls
    create_box("MATH_10th_Feature_Wall_North", col_int, (0, 16.0, 31.4), (16.0, 0.25, 3.1), mat_walnut)
    create_box("MATH_10th_Feature_Wall_South", col_int, (0, -16.0, 31.4), (16.0, 0.25, 3.1), mat_walnut)

    # Monumental 16-Seat Solid Mahogany Conference Table
    create_box("MATH_10th_Conf_Table", col_int, (0, 0, 30.55), (3.6, 9.8, 0.08), mat_walnut)
    # Table Pedestals
    for py in [-3.2, 0.0, 3.2]:
        create_cylinder(f"MATH_10th_Table_Pedestal_{py}", col_int, (0, py, 30.18), radius=0.45, depth=0.68, mat=mat_walnut)

    # 16 Executive Articulated Burgundy Leather Swivel Armchairs
    chair_offsets_y = [-3.8, -2.5, -1.2, 0.0, 1.2, 2.5, 3.8]
    for cy in chair_offsets_y:
        # East side
        create_cylinder(f"MATH_10th_Chair_Stem_E_{cy}", col_int, (2.3, cy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Seat_E_{cy}", col_int, (2.3, cy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Back_E_{cy}", col_int, (2.6, cy, 30.90), (0.08, 0.52, 0.65), mat_leather_burgundy)
        # West side
        create_cylinder(f"MATH_10th_Chair_Stem_W_{cy}", col_int, (-2.3, cy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Seat_W_{cy}", col_int, (-2.3, cy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Back_W_{cy}", col_int, (-2.6, cy, 30.90), (0.08, 0.52, 0.65), mat_leather_burgundy)
    # Head of table chairs
    for hy, hrot in [(-5.4, 0), (5.4, math.pi)]:
        create_cylinder(f"MATH_10th_Chair_Head_Stem_{hy}", col_int, (0, hy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Head_Seat_{hy}", col_int, (0, hy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Head_Back_{hy}", col_int, (0, hy + (0.3 if hy>0 else -0.3), 30.90), (0.52, 0.08, 0.65), mat_leather_burgundy)

    # Large Colloquium Proof Blackboard on North Feature Wall
    create_box("MATH_10th_Colloquium_Board_Frame", col_int, (0, 15.85, 31.4), (8.4, 0.05, 1.8), mat_honey_oak)
    create_box("MATH_10th_Colloquium_Board_Panel", col_int, (0, 15.82, 31.4), (8.2, 0.02, 1.6), mat_blackboard)
    bpy.ops.object.text_add(location=(-3.6, 15.80, 31.4), rotation=(math.pi/2, 0, 0))
    txt = bpy.context.active_object
    txt.name = "MATH_10th_Colloquium_Text"
    txt.data.body = "FACULTY COLLOQUIUM: RIEMANN HYPOTHESIS & SPECTRAL THEORY"
    txt.data.size = 0.24
    txt.data.extrude = 0.02
    txt.data.materials.append(mat_chalk)
    txt.parent = root_obj
    col_int.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # Lounge Area with Chesterfield Sofas and Coffee Bar
    create_box("MATH_10th_Sofa_Base", col_int, (-8.0, 0, 30.2), (1.4, 3.6, 0.35), mat_leather_burgundy)
    create_box("MATH_10th_Sofa_Back", col_int, (-8.6, 0, 30.65), (0.35, 3.6, 0.55), mat_leather_burgundy)
    create_box("MATH_10th_Coffee_Table", col_int, (-6.5, 0, 30.15), (0.8, 2.2, 0.25), mat_walnut)
    # Coffee Bar Credenza on South Wall
    create_box("MATH_10th_Credenza", col_int, (0, -15.6, 30.35), (4.5, 0.7, 0.85), mat_walnut)
    create_box("MATH_10th_Espresso_Machine", col_int, (-1.2, -15.6, 30.95), (0.6, 0.5, 0.4), mat_bronze)

    # Warm Overhead Downlights in 10th-Floor Sky Lounge
    for lx in [-6.0, 0.0, 6.0]:
        for ly in [-8.0, 0.0, 8.0]:
            light_data = bpy.data.lights.new(name=f"MATH_10th_Light_{lx}_{ly}", type="POINT")
            light_data.energy = 550.0
            light_data.color = (1.0, 0.94, 0.85)
            light_obj = bpy.data.objects.new(name=f"MATH_10th_Light_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 32.7)
            col_int.objects.link(light_obj)

    print("Building 62_Math_Sciences_Plaza_and_Site...")

    # 1. Sunken Outdoor Courtyard / Plaza on East side (towards Memorial Mall & CL50)
    # Descends from Z = 0 to Z = -2.2m
    create_box("MATH_Sunken_Plaza_Floor", col_site, (22.5, -6.0, -2.15), (10.0, 24.0, 0.3), mat_concrete)
    # Sunken concrete retaining walls
    create_box("MATH_Sunken_Wall_East", col_site, (27.6, -6.0, -1.0), (0.4, 24.0, 2.4), mat_dark_concrete)
    create_box("MATH_Sunken_Wall_North", col_site, (22.5, 6.2, -1.0), (10.0, 0.4, 2.4), mat_dark_concrete)
    create_box("MATH_Sunken_Wall_South", col_site, (22.5, -18.2, -1.0), (10.0, 0.4, 2.4), mat_dark_concrete)
    # Stepped concrete seating terraces in sunken plaza
    for st in range(5):
        step_z = -2.1 + (st + 1) * 0.35
        step_x = 26.5 - st * 0.6
        create_box(f"MATH_Sunken_Step_{st+1}", col_site, (step_x, -6.0, step_z), (0.6, 20.0, 0.35), mat_concrete)

    # 2. Main Ground-Level Arrival Plazas
    # West Plaza along University Street (X = -26.0 to -18.6m)
    create_box("MATH_West_Plaza_Brick", col_site, (-24.5, 0, 0.05), (11.0, 64.0, 0.1), mat_brick)
    # East Concourse along Oval Drive (connecting to CL50)
    create_box("MATH_East_Concourse_Paving", col_site, (24.0, 22.0, 0.05), (10.0, 26.0, 0.1), mat_concrete)

    # 3. Limestone Planter Beds with Evergreen Boxwoods
    for px, py, pw, pl in [(-22.0, 24.0, 4.0, 10.0), (-22.0, -24.0, 4.0, 10.0), (22.0, 24.0, 3.5, 12.0)]:
        create_box(f"MATH_Planter_Wall_{px}_{py}", col_site, (px, py, 0.3), (pw, pl, 0.5), mat_limestone)
        create_box(f"MATH_Planter_Hedge_{px}_{py}", col_site, (px, py, 0.65), (pw - 0.5, pl - 0.5, 0.55), book_colors[2])

    # 4. Campus Teak Wood Benches
    for bx, by, rot in [(-22.5, 12.0, 0), (-22.5, -12.0, 0), (22.5, 15.0, math.pi)]:
        create_box(f"MATH_Bench_Seat_{bx}_{by}", col_site, (bx, by, 0.45), (0.6, 2.2, 0.08), mat_honey_oak)
        create_box(f"MATH_Bench_Back_{bx}_{by}", col_site, (bx - (0.28 if rot==0 else -0.28), by, 0.75), (0.08, 2.2, 0.45), mat_honey_oak)
        create_box(f"MATH_Bench_Legs_{bx}_{by}", col_site, (bx, by, 0.22), (0.55, 2.0, 0.42), mat_bronze)

    # 5. Bank of 12 Sheffield Bicycle Racks
    rack_xs = [-24.0 + i * 1.1 for i in range(12)]
    for i, rx in enumerate(rack_xs):
        create_cylinder(f"MATH_Bike_Rack_Arch_{i+1}", col_site, (rx, 30.0, 0.45), radius=0.035, depth=0.9, mat=mat_bronze)
        create_box(f"MATH_Bike_Rack_Crossbar_{i+1}", col_site, (rx, 30.0, 0.85), (0.07, 0.85, 0.07), mat_bronze)

    # 6. Victorian Cast-Iron Lantern Posts with Warm Point Lights
    lantern_locs = [(-25.0, -18.0), (-25.0, 18.0), (26.0, 26.0), (26.0, -15.0)]
    for i, (lx, ly) in enumerate(lantern_locs):
        create_cylinder(f"MATH_Lantern_Post_{i+1}", col_site, (lx, ly, 1.8), radius=0.10, depth=3.6, mat=mat_bronze)
        create_cylinder(f"MATH_Lantern_Luminaire_{i+1}", col_site, (lx, ly, 3.7), radius=0.25, depth=0.45, mat=mat_gold)
        l_data = bpy.data.lights.new(name=f"MATH_Lantern_Light_{i+1}", type="POINT")
        l_data.energy = 900.0
        l_data.color = (1.0, 0.85, 0.65)
        l_obj = bpy.data.objects.new(name=f"MATH_Lantern_Light_{i+1}", object_data=l_data)
        l_obj.location = (-180.62 + lx, -127.29 + ly, 3.8)
        col_site.objects.link(l_obj)

    print("Calibrating Inspection Cameras Cam_92 through Cam_96...")

    def setup_camera(name, loc, rot_deg, lens=24.0):
        cam = bpy.data.objects.get(name)
        if not cam:
            cam_data = bpy.data.cameras.new(name=name)
            cam = bpy.data.objects.new(name=name, object_data=cam_data)
            col_cams.objects.link(cam)
        cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 1200.0
        cam.location = loc
        cam.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        return cam

    # Cam 92: Hero South-West University Street Arrival
    # World location: X = -225.0, Y = -165.0, Z = 6.0 looking North-East towards MATH
    setup_camera("Cam_92_MATH_UniversitySt_Hero", (-225.0, -165.0, 6.0), (78.0, 0.0, -45.0), lens=20.0)

    # Cam 93: MATH 175 Major Tiered Lecture Hall Interior
    # Looking from rear top tier toward blackboard & instructor dais
    setup_camera("Cam_93_MATH_175_LectureHall_Interior", (-187.62, -135.5, 3.2), (76.0, 0.0, 0.0), lens=18.0)

    # Cam 94: Mathematical Sciences Library Interior (Floor 3)
    # Looking across study tables, book stacks, and Memorial Mall windows
    setup_camera("Cam_94_MATH_Library_Study_Interior", (-175.5, -114.0, 12.4), (78.0, 0.0, 45.0), lens=20.0)

    # Cam 95: 10th-Floor Faculty Colloquium Sky Lounge Interior
    # Looking across conference table, leather chairs, blackboard proofs, and ribbon windows
    setup_camera("Cam_95_MATH_10thFloor_SkyLounge_Interior", (-184.0, -133.0, 31.3), (76.0, 0.0, 25.0), lens=19.0)

    # Cam 96: Precinct Aerial Context
    # Elevated aerial view showing full 10-story tower, mechanical penthouse, sunken plaza, and connections to CL50 & Beering
    setup_camera("Cam_96_MATH_Precinct_Aerial", (-130.0, -195.0, 65.0), (58.0, 0.0, 40.0), lens=24.0)

    # Save Master Blend File
    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend File saved successfully with Mathematical Sciences Building (MATH)!")

if __name__ == "__main__":
    run_build()
