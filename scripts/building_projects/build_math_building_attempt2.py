"""
Purdue University Digital Twin - Mathematical Sciences Building (MATH - 1967) Attempt 2
Full Architectural Reconstruction:
- Authentic 10-Story Precast Concrete Window Waffle Grid on Long East & West Facades (Y in [-30, +30])
- Four Brick & Limestone Corner Stair/Service Towers (NE, NW, SE, SW)
- Recessed Ground-Floor Pilotis Colonnade with Open Pedestrian Breezeway
- Hollowed Interior Envelopes with Pristine Sightlines
- Fully Illuminated MATH 175 Amphitheater with Chalkboard Proofs & 8-Tier Risers
- Mathematical Sciences Library with Open Study Promenade, Laptops & Banker's Lamps
- 10th-Floor Faculty Sky Lounge with Panoramic Ribbon Windows & 16-Seat Conference Table
- Re-Calibrated Inspection Cameras Cam_92 through Cam_96
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

def run_attempt2():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened master blend successfully for Attempt 2.")

    # 1. Clean existing MATH collections
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

    # Clear old objects in MATH collections
    for c in [col_ext, col_int, col_site]:
        for o in list(c.objects):
            c.objects.unlink(o)
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Root Anchor Object
    root_obj = bpy.data.objects.new("MATH_Root", None)
    root_obj.location = (-180.62, -127.29, 0.0)
    col_ext.objects.link(root_obj)

    # 3. Materials
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
    mat_concrete = get_or_create_mat("MATH_Precast_Concrete", (0.78, 0.77, 0.74, 1.0), roughness=0.60)
    mat_dark_concrete = get_or_create_mat("MATH_BoardFormed_Concrete", (0.42, 0.41, 0.39, 1.0), roughness=0.70)
    mat_limestone = get_or_create_mat("MATH_Bedford_Limestone", (0.84, 0.82, 0.77, 1.0), roughness=0.55)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_or_create_mat("MATH_Ribbon_Glass", (0.04, 0.07, 0.12, 1.0), roughness=0.05, transmission=0.88)
    mat_bronze = bpy.data.materials.get("Elliott_ArtDeco_Bronze") or get_or_create_mat("MATH_Dark_Bronze", (0.20, 0.16, 0.12, 1.0), roughness=0.35, metallic=0.85)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_or_create_mat("MATH_Purdue_Gold", (0.85, 0.68, 0.22, 1.0), roughness=0.25, metallic=0.90)
    mat_terrazzo = get_or_create_mat("MATH_Terrazzo_Cream", (0.86, 0.84, 0.80, 1.0), roughness=0.18)
    mat_terrazzo_dark = get_or_create_mat("MATH_Terrazzo_Charcoal", (0.22, 0.22, 0.24, 1.0), roughness=0.22)
    mat_carpet_navy = get_or_create_mat("MATH_Navy_Carpet", (0.04, 0.08, 0.18, 1.0), roughness=0.90)
    mat_walnut = get_or_create_mat("MATH_Dark_Walnut", (0.16, 0.09, 0.05, 1.0), roughness=0.35)
    mat_honey_oak = get_or_create_mat("MATH_Honey_Oak", (0.55, 0.38, 0.20, 1.0), roughness=0.40)
    mat_blackboard = get_or_create_mat("MATH_Blackboard_Porcelain", (0.05, 0.10, 0.07, 1.0), roughness=0.45)
    mat_chalk = get_or_create_mat("MATH_Chalk_Emissive", (0.95, 0.98, 0.95, 1.0), roughness=0.8, emission=(0.95, 0.98, 0.95, 1.0), emission_strength=2.2)
    mat_leather_burgundy = get_or_create_mat("MATH_Leather_Burgundy", (0.24, 0.04, 0.06, 1.0), roughness=0.38)
    mat_persian_rug = get_or_create_mat("MATH_Persian_Rug", (0.35, 0.08, 0.10, 1.0), roughness=0.85)
    mat_green_glass = get_or_create_mat("MATH_Bankers_Green_Glass", (0.02, 0.35, 0.12, 1.0), roughness=0.15, transmission=0.75, emission=(0.05, 0.60, 0.20, 1.0), emission_strength=2.2)
    mat_brass = get_or_create_mat("MATH_Polished_Brass", (0.90, 0.75, 0.30, 1.0), roughness=0.20, metallic=0.95)
    mat_screen_white = get_or_create_mat("MATH_Screen_White", (0.92, 0.92, 0.92, 1.0), roughness=0.85, emission=(0.95, 0.95, 0.95, 1.0), emission_strength=1.5)
    mat_roof_gravel = get_or_create_mat("MATH_Roof_Gravel", (0.42, 0.42, 0.42, 1.0), roughness=0.90)

    # Mesh creation helpers
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

    print("Building 60_Math_Sciences_Exterior with Authentic Fenestration Matrix...")

    # Bounding Box reference:
    # Width X = 37.3m -> local X in [-18.65, +18.65]
    # Length Y = 68.17m -> local Y in [-34.08, +34.08]
    # Height Z = 36.3m -> local Z in [0.00, 36.30]

    # 1. Ground Slab
    create_box("MATH_Ground_Slab", col_ext, (0, 0, 0.20), (37.3, 68.17, 0.40), mat_dark_concrete)

    # 2. Four Monumental Brick & Limestone Corner Stair/Service Towers
    # Northeast, Northwest, Southeast, Southwest corners (housing elevators, stairs, risers)
    tower_dx = 5.2
    tower_dy = 6.8
    corner_locs = [
        ("NE", 18.65 - tower_dx/2, 34.08 - tower_dy/2),
        ("NW", -18.65 + tower_dx/2, 34.08 - tower_dy/2),
        ("SE", 18.65 - tower_dx/2, -34.08 + tower_dy/2),
        ("SW", -18.65 + tower_dx/2, -34.08 + tower_dy/2),
    ]
    for cname, cx, cy in corner_locs:
        # Brick core rising full height (Z = 0.4 to 33.2m)
        create_box(f"MATH_Corner_Tower_{cname}_Brick", col_ext, (cx, cy, 16.8), (tower_dx, tower_dy, 32.8), mat_brick)
        # Limestone water table base
        create_box(f"MATH_Corner_Tower_{cname}_Base", col_ext, (cx, cy, 0.9), (tower_dx + 0.3, tower_dy + 0.3, 1.4), mat_limestone)
        # Limestone parapet copings
        create_box(f"MATH_Corner_Tower_{cname}_Coping", col_ext, (cx, cy, 33.3), (tower_dx + 0.3, tower_dy + 0.3, 0.4), mat_limestone)

    # North and South End Enclosure Walls (between corner towers: X in [-13.4, +13.4])
    # Textured Purdue red brick with horizontal limestone beltcourses
    for end_name, end_y in [("North", 34.08 - 0.25), ("South", -34.08 + 0.25)]:
        create_box(f"MATH_End_Wall_{end_name}_Brick", col_ext, (0, end_y, 16.8), (26.8, 0.5, 32.8), mat_brick)
        create_box(f"MATH_End_Wall_{end_name}_Base", col_ext, (0, end_y, 0.9), (27.0, 0.7, 1.4), mat_limestone)
        create_box(f"MATH_End_Wall_{end_name}_Coping", col_ext, (0, end_y, 33.3), (27.0, 0.7, 0.4), mat_limestone)
        # Recessed vertical glass bay in center of North and South end walls
        create_box(f"MATH_End_Glass_{end_name}", col_ext, (0, end_y, 18.6), (4.5, 0.6, 26.0), mat_glass)
        # Bronze vertical mullions
        for mx in [-2.2, 0.0, 2.2]:
            create_box(f"MATH_End_Mullion_{end_name}_{mx}", col_ext, (mx, end_y, 18.6), (0.12, 0.65, 26.0), mat_bronze)

    # 3. Ground Floor Recessed Pilotis Colonnade (Z = 0.4m to 4.4m)
    # Allows pedestrians to walk beneath the 9-story tower
    # Massive rectangular concrete pilotis along East and West edges
    col_ys = [-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0]
    for py in col_ys:
        # West Colonnade (along University St)
        create_box(f"MATH_Pilotis_West_{py:.1f}", col_ext, (-16.5, py, 2.4), (1.4, 1.2, 4.0), mat_dark_concrete)
        # East Colonnade (along Oval Drive / Memorial Mall)
        create_box(f"MATH_Pilotis_East_{py:.1f}", col_ext, (16.5, py, 2.4), (1.4, 1.2, 4.0), mat_dark_concrete)

    # Ground floor recessed curtain wall (set back 3.2m from columns: X at -13.5m and +13.5m)
    create_box("MATH_Ground_Curtain_West", col_ext, (-13.5, 0, 2.4), (0.2, 54.0, 4.0), mat_glass)
    create_box("MATH_Ground_Curtain_East", col_ext, (13.5, 0, 2.4), (0.2, 54.0, 4.0), mat_glass)

    # West & East Monumental Entrance Canopies
    # West entrance canopy (University Street)
    create_box("MATH_Entrance_Canopy_West", col_ext, (-17.5, 0, 4.4), (5.5, 9.0, 0.35), mat_limestone)
    create_box("MATH_Entrance_Canopy_East", col_ext, (17.5, 0, 4.4), (5.5, 9.0, 0.35), mat_limestone)

    # 3D Gold Extruded Signage on Canopies
    for side, pos_x, rot_z in [("West", -17.5, math.pi), ("East", 17.5, 0)]:
        bpy.ops.object.text_add(location=(pos_x, -3.8, 4.65), rotation=(math.pi/2, 0, rot_z + math.pi/2))
        txt = bpy.context.active_object
        txt.name = f"MATH_Signage_{side}"
        txt.data.body = "MATHEMATICAL SCIENCES BUILDING"
        txt.data.size = 0.36
        txt.data.extrude = 0.04
        txt.data.materials.append(mat_gold)
        txt.parent = root_obj
        col_ext.objects.link(txt)
        bpy.context.scene.collection.objects.unlink(txt)

    # 4. Long Facades (East & West) Precast Concrete Window Waffle Grid (Floors 2 to 10: Z = 4.4m to 33.0m)
    # Height = 28.6m. 9 levels, floor_height = 3.18m
    # Length Y in [-27.0, +27.0] = 54.0m clear span
    floor_height = 3.18
    num_floors = 9

    # Horizontal Precast Concrete Spandrel Beams across East & West facades
    for fl in range(num_floors + 1):
        fz = 4.4 + fl * floor_height
        # West spandrel
        create_box(f"MATH_Spandrel_West_{fl}", col_ext, (-18.65, 0, fz), (0.6, 54.4, 0.5), mat_concrete)
        # East spandrel
        create_box(f"MATH_Spandrel_East_{fl}", col_ext, (18.65, 0, fz), (0.6, 54.4, 0.5), mat_concrete)

    # Vertical Concrete Solar Fins / Shadow Box Ribs (23 vertical fins spaced every 2.45m along Y)
    fin_ys = [-26.4 + i * 2.40 for i in range(23)]
    for i, fy in enumerate(fin_ys):
        # West facade fins
        create_box(f"MATH_Fin_West_{i}", col_ext, (-18.65, fy, 18.7), (0.8, 0.25, 28.6), mat_concrete)
        # East facade fins
        create_box(f"MATH_Fin_East_{i}", col_ext, (18.65, fy, 18.7), (0.8, 0.25, 28.6), mat_concrete)

    # Recessed Solar Ribbon Glazing behind fins (West & East facades)
    for fl in range(num_floors):
        mid_z = 4.4 + fl * floor_height + floor_height / 2.0
        # West ribbon glass
        create_box(f"MATH_Ribbon_Glass_West_{fl+2}", col_ext, (-18.25, 0, mid_z), (0.15, 54.0, 2.68), mat_glass)
        # East ribbon glass
        create_box(f"MATH_Ribbon_Glass_East_{fl+2}", col_ext, (18.25, 0, mid_z), (0.15, 54.0, 2.68), mat_glass)

    # 5. Roof System, Gravel Ballast & Mechanical Penthouse
    create_box("MATH_Roof_Deck_Gravel", col_ext, (0, 0, 32.95), (37.1, 67.9, 0.3), mat_roof_gravel)
    create_box("MATH_Parapet_East", col_ext, (18.65, 0, 33.3), (0.5, 54.4, 0.4), mat_limestone)
    create_box("MATH_Parapet_West", col_ext, (-18.65, 0, 33.3), (0.5, 54.4, 0.4), mat_limestone)

    # Rooftop Mechanical Penthouse (Z = 33.0m to 36.3m, height 3.3m)
    create_box("MATH_Rooftop_Penthouse_Base", col_ext, (0, 0, 34.65), (20.0, 44.0, 3.3), mat_brick)
    create_box("MATH_Rooftop_Penthouse_Copings", col_ext, (0, 0, 36.35), (20.4, 44.4, 0.3), mat_limestone)
    create_box("MATH_Penthouse_Louver_North", col_ext, (0, 22.05, 34.8), (16.0, 0.2, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_South", col_ext, (0, -22.05, 34.8), (16.0, 0.2, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_East", col_ext, (10.05, 0, 34.8), (0.2, 36.0, 2.2), mat_bronze)
    create_box("MATH_Penthouse_Louver_West", col_ext, (-10.05, 0, 34.8), (0.2, 36.0, 2.2), mat_bronze)

    # Steel Communications Antenna Mast (Z = 36.3m to 42.0m)
    create_cylinder("MATH_Communications_Mast", col_ext, (4.0, 8.0, 39.15), radius=0.18, depth=5.7, mat=mat_bronze)
    create_cylinder("MATH_Antenna_Spire", col_ext, (4.0, 8.0, 42.2), radius=0.06, depth=1.4, mat=mat_gold)

    print("Building 61_Math_Sciences_Interiors with Unobstructed Sightlines...")

    # =========================================================================
    # INTERIOR 1: MATH 175 Major Tiered Lecture Hall (Ground Floor)
    # Sited in South Ground Floor volume: X in [-12, +2], Y in [-26, -4]
    # Local Center: X = -5.0, Y = -15.0, Z = 0.40m
    # =========================================================================
    create_box("MATH_175_Floor_Navy_Carpet", col_int, (-5.0, -15.0, 0.42), (14.0, 22.0, 0.05), mat_carpet_navy)
    create_box("MATH_175_Wall_West", col_int, (-12.1, -15.0, 2.4), (0.2, 22.0, 4.0), mat_honey_oak)
    create_box("MATH_175_Wall_East", col_int, (2.1, -15.0, 2.4), (0.2, 22.0, 4.0), mat_honey_oak)
    create_box("MATH_175_Wall_South", col_int, (-5.0, -26.1, 2.4), (14.0, 0.2, 4.0), mat_walnut)
    create_box("MATH_175_Wall_North", col_int, (-5.0, -3.9, 2.4), (14.0, 0.2, 4.0), mat_honey_oak)
    create_box("MATH_175_Ceiling", col_int, (-5.0, -15.0, 4.35), (14.0, 22.0, 0.1), mat_concrete)

    # 8 Stepped Seating Risers (rising from South front Y=-22 to North rear Y=-8)
    for tier_idx in range(8):
        tz = 0.45 + (tier_idx + 1) * 0.26
        ty = -21.0 + tier_idx * 1.8
        create_box(f"MATH_175_Riser_Tier_{tier_idx+1}", col_int, (-5.0, ty, (0.42 + tz)/2.0), (13.0, 1.7, tz - 0.42), mat_carpet_navy)
        create_box(f"MATH_175_Desk_Tier_{tier_idx+1}", col_int, (-5.0, ty - 0.4, tz + 0.38), (12.2, 0.45, 0.04), mat_honey_oak)
        for sx in [-5.0, -2.5, 0.0, 2.5, 5.0]:
            create_cylinder(f"MATH_175_Desk_Leg_{tier_idx}_{sx}", col_int, (-5.0 + sx, ty - 0.4, tz + 0.19), radius=0.03, depth=0.38, mat=mat_bronze)
        for cx in [-4.8, -2.9, -1.0, 1.0, 2.9, 4.8]:
            chair_x = -5.0 + cx
            chair_y = ty + 0.25
            create_cylinder(f"MATH_175_Chair_Pedestal_{tier_idx}_{cx}", col_int, (chair_x, chair_y, tz + 0.18), radius=0.04, depth=0.36, mat=mat_bronze)
            create_box(f"MATH_175_Chair_Seat_{tier_idx}_{cx}", col_int, (chair_x, chair_y, tz + 0.38), (0.46, 0.44, 0.06), mat_carpet_navy)
            create_box(f"MATH_175_Chair_Back_{tier_idx}_{cx}", col_int, (chair_x, chair_y + 0.20, tz + 0.62), (0.44, 0.06, 0.42), mat_carpet_navy)

    # Front Stage Dais (South side: Y = -24.5)
    create_box("MATH_175_Stage_Dais", col_int, (-5.0, -24.5, 0.60), (13.0, 3.0, 0.36), mat_honey_oak)
    create_box("MATH_175_Smart_Podium", col_int, (-2.5, -24.2, 1.25), (0.9, 0.7, 1.1), mat_walnut)
    create_cylinder("MATH_175_Podium_Mic", col_int, (-2.5, -24.0, 1.85), radius=0.015, depth=0.3, mat=mat_brass)
    create_box("MATH_175_Podium_Seal", col_int, (-2.5, -24.56, 1.25), (0.35, 0.02, 0.35), mat_gold)

    # Quadruple Sliding Porcelain Blackboards (mounted on South front wall)
    create_box("MATH_175_Blackboard_Frame", col_int, (-5.0, -25.95, 2.4), (11.0, 0.06, 2.2), mat_honey_oak)
    for b_idx in range(4):
        bx = -9.0 + 1.2 + b_idx * 2.5
        create_box(f"MATH_175_Blackboard_Panel_{b_idx+1}", col_int, (bx, -25.92, 2.4), (2.35, 0.03, 2.0), mat_blackboard)

    # Mathematical Proofs & Formulas in Emissive Chalk
    formulas = [
        "e^{i\\pi} + 1 = 0",
        "\\zeta(s) = \\sum n^{-s}",
        "\\rho(\\partial_t v + v\\cdot\\nabla v) = -\\nabla p + \\mu\\nabla^2 v",
        "\\int_a^b f'(x)dx = f(b) - f(a)"
    ]
    for b_idx, eq in enumerate(formulas):
        bx = -9.0 + 1.2 + b_idx * 2.5
        bpy.ops.object.text_add(location=(bx - 0.95, -25.90, 2.3), rotation=(math.pi/2, 0, 0))
        txt = bpy.context.active_object
        txt.name = f"MATH_175_Equation_{b_idx+1}"
        txt.data.body = eq
        txt.data.size = 0.24
        txt.data.extrude = 0.02
        txt.data.materials.append(mat_chalk)
        txt.parent = root_obj
        col_int.objects.link(txt)
        bpy.context.scene.collection.objects.unlink(txt)

    # Dual 120" Motorized Projection Screens
    for sx in [-7.5, -2.5]:
        create_box(f"MATH_175_Screen_Housing_{sx}", col_int, (sx, -25.95, 3.65), (2.8, 0.15, 0.15), mat_bronze)
        create_box(f"MATH_175_Screen_Display_{sx}", col_int, (sx, -25.93, 2.90), (2.6, 0.02, 1.4), mat_screen_white)

    # Ceiling Lights & Theatrical Stage Wash in MATH 175
    stage_light_data = bpy.data.lights.new(name="MATH_175_Stage_Spotlight", type="SPOT")
    stage_light_data.energy = 2200.0
    stage_light_data.spot_size = math.radians(65)
    stage_light_data.color = (1.0, 0.96, 0.88)
    stage_light_obj = bpy.data.objects.new(name="MATH_175_Stage_Spotlight", object_data=stage_light_data)
    stage_light_obj.location = (-180.62 - 5.0, -127.29 - 20.0, 4.1)
    stage_light_obj.rotation_euler = (math.radians(-35), 0, 0)
    col_int.objects.link(stage_light_obj)

    for lx in [-8.0, -5.0, -2.0]:
        for ly in [-18.0, -12.0, -6.0]:
            light_data = bpy.data.lights.new(name=f"MATH_175_Light_{lx}_{ly}", type="POINT")
            light_data.energy = 750.0
            light_data.color = (1.0, 0.95, 0.88)
            light_obj = bpy.data.objects.new(name=f"MATH_175_Light_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 4.0)
            col_int.objects.link(light_obj)

    # =========================================================================
    # INTERIOR 2: Mathematical Sciences Library (Floor 3, Z = 10.6m to 13.8m)
    # Sited in North Floor 3 volume: X in [-10, +10], Y in [5, 27]
    # Local Center: X = 0.0, Y = 16.0, Z = 10.60m
    # =========================================================================
    create_box("MATH_Lib_Floor_Terrazzo", col_int, (0, 16.0, 10.62), (20.0, 22.0, 0.05), mat_terrazzo)
    create_box("MATH_Lib_Border_Terrazzo", col_int, (0, 16.0, 10.625), (20.0, 22.0, 0.04), mat_terrazzo_dark)
    create_box("MATH_Lib_Wall_West", col_int, (-10.1, 16.0, 12.2), (0.2, 22.0, 3.1), mat_glass) # Window overlooking University St!
    create_box("MATH_Lib_Wall_East", col_int, (10.1, 16.0, 12.2), (0.2, 22.0, 3.1), mat_glass) # Window overlooking Memorial Mall!
    create_box("MATH_Lib_Wall_South", col_int, (0, 4.9, 12.2), (20.0, 0.2, 3.1), mat_honey_oak)
    create_box("MATH_Lib_Wall_North", col_int, (0, 27.1, 12.2), (20.0, 0.2, 3.1), mat_honey_oak)
    create_box("MATH_Lib_Ceiling", col_int, (0, 16.0, 13.75), (20.0, 22.0, 0.1), mat_concrete)

    # 4 Double-sided Book Stacks aligned along East wall (X = 5.5m)
    book_colors = [
        get_or_create_mat("Book_Navy", (0.05, 0.10, 0.30, 1.0), roughness=0.6),
        get_or_create_mat("Book_Crimson", (0.35, 0.05, 0.08, 1.0), roughness=0.6),
        get_or_create_mat("Book_Forest", (0.05, 0.25, 0.08, 1.0), roughness=0.6),
        get_or_create_mat("Book_Gold", (0.65, 0.50, 0.15, 1.0), roughness=0.6)
    ]
    for stack_idx in range(4):
        sy = 8.5 + stack_idx * 4.2
        create_box(f"MATH_Lib_Stack_{stack_idx+1}", col_int, (5.8, sy, 11.9), (6.0, 0.9, 2.5), mat_walnut)
        for shelf in range(4):
            sz = 10.9 + shelf * 0.6
            for b in range(10):
                bx = 3.2 + b * 0.55
                mat_b = book_colors[(stack_idx + shelf + b) % len(book_colors)]
                create_box(f"MATH_Lib_Book_{stack_idx}_{shelf}_{b}", col_int, (bx, sy, sz), (0.45, 0.75, 0.45), mat_b)
        create_box(f"MATH_Lib_Aisle_Tag_{stack_idx+1}", col_int, (2.6, sy, 12.8), (0.04, 0.35, 0.2), mat_brass)

    # 2 Collaborative Honey Oak Study Tables aligned along West side (X = -4.5m)
    for t_idx, ty in enumerate([11.0, 19.0]):
        create_box(f"MATH_Lib_Table_{t_idx+1}", col_int, (-4.5, ty, 11.35), (6.5, 1.6, 0.06), mat_honey_oak)
        for tx in [-7.2, -1.8]:
            for ty_leg in [ty - 0.6, ty + 0.6]:
                create_cylinder(f"MATH_Lib_Table_Leg_{t_idx}_{tx}_{ty_leg}", col_int, (tx, ty_leg, 10.98), radius=0.04, depth=0.70, mat=mat_bronze)
        for cx in [-6.5, -4.5, -2.5]:
            for c_side in [-1, 1]:
                chair_y = ty + c_side * 1.1
                create_cylinder(f"MATH_Lib_Chair_Leg_{t_idx}_{cx}_{c_side}", col_int, (cx, chair_y, 10.95), radius=0.03, depth=0.65, mat=mat_bronze)
                create_box(f"MATH_Lib_Chair_Seat_{t_idx}_{cx}_{c_side}", col_int, (cx, chair_y, 11.30), (0.48, 0.48, 0.05), mat_walnut)
                create_box(f"MATH_Lib_Chair_Back_{t_idx}_{cx}_{c_side}", col_int, (cx, chair_y + (0.22 if c_side>0 else -0.22), 11.55), (0.45, 0.05, 0.40), mat_walnut)
        # Glowing green-glass banker's lamps
        for lx in [-5.8, -3.2]:
            create_box(f"MATH_Lib_Bankers_Shade_{t_idx}_{lx}", col_int, (lx, ty, 11.65), (0.30, 0.18, 0.12), mat_green_glass)
            create_cylinder(f"MATH_Lib_Bankers_Stand_{t_idx}_{lx}", col_int, (lx, ty, 11.48), radius=0.02, depth=0.22, mat=mat_brass)
            lamp_data = bpy.data.lights.new(name=f"MATH_Lib_Bankers_Light_{t_idx}_{lx}", type="POINT")
            lamp_data.energy = 280.0
            lamp_data.color = (0.75, 1.0, 0.75)
            lamp_obj = bpy.data.objects.new(name=f"MATH_Lib_Bankers_Light_{t_idx}_{lx}", object_data=lamp_data)
            lamp_obj.location = (-180.62 + lx, -127.29 + ty, 11.72)
            col_int.objects.link(lamp_obj)
        # Open student laptops with emissive screens
        create_box(f"MATH_Lib_Laptop_Base_{t_idx}", col_int, (-4.5, ty + 0.3, 11.40), (0.38, 0.28, 0.02), mat_bronze)
        create_box(f"MATH_Lib_Laptop_Screen_{t_idx}", col_int, (-4.5, ty + 0.44, 11.55), (0.38, 0.02, 0.26), mat_screen_white)

    # Ceiling Lights in Library
    for lx in [-5.0, 0.0, 5.0]:
        for ly in [8.0, 16.0, 24.0]:
            light_data = bpy.data.lights.new(name=f"MATH_Lib_Ceiling_{lx}_{ly}", type="POINT")
            light_data.energy = 700.0
            light_data.color = (1.0, 0.98, 0.92)
            light_obj = bpy.data.objects.new(name=f"MATH_Lib_Ceiling_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 13.5)
            col_int.objects.link(light_obj)

    # =========================================================================
    # INTERIOR 3: 10th-Floor Faculty Colloquium Sky Lounge (Floor 10)
    # Sited across Floor 10 with panoramic ribbon glass overlooking campus!
    # Local Center: X = 0.0, Y = 0.0, Z = 29.80m
    # =========================================================================
    create_box("MATH_10th_Floor_Walnut_Parquet", col_int, (0, 0, 29.82), (24.0, 50.0, 0.05), mat_walnut)
    create_box("MATH_10th_Persian_Rug", col_int, (0, 0, 29.85), (8.5, 14.0, 0.04), mat_persian_rug)
    create_box("MATH_10th_Ceiling", col_int, (0, 0, 32.95), (24.0, 50.0, 0.1), mat_concrete)
    # Panoramic Ribbon Glazing framing East and West views
    create_box("MATH_10th_Ribbon_Glass_East", col_int, (12.0, 0, 31.4), (0.15, 50.0, 3.1), mat_glass)
    create_box("MATH_10th_Ribbon_Glass_West", col_int, (-12.0, 0, 31.4), (0.15, 50.0, 3.1), mat_glass)
    # North and South Interior Feature Enclosure Walls
    create_box("MATH_10th_Feature_Wall_North", col_int, (0, 18.0, 31.4), (20.0, 0.25, 3.1), mat_walnut)
    create_box("MATH_10th_Feature_Wall_South", col_int, (0, -18.0, 31.4), (20.0, 0.25, 3.1), mat_walnut)

    # Monumental 16-Seat Solid Mahogany Conference Table
    create_box("MATH_10th_Conf_Table", col_int, (0, 0, 30.55), (3.4, 9.8, 0.08), mat_walnut)
    for py in [-3.2, 0.0, 3.2]:
        create_cylinder(f"MATH_10th_Table_Pedestal_{py}", col_int, (0, py, 30.18), radius=0.45, depth=0.68, mat=mat_walnut)

    # 16 Executive Articulated Burgundy Leather Swivel Armchairs
    chair_offsets_y = [-3.8, -2.5, -1.2, 0.0, 1.2, 2.5, 3.8]
    for cy in chair_offsets_y:
        # East side
        create_cylinder(f"MATH_10th_Chair_Stem_E_{cy}", col_int, (2.2, cy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Seat_E_{cy}", col_int, (2.2, cy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Back_E_{cy}", col_int, (2.5, cy, 30.90), (0.08, 0.52, 0.65), mat_leather_burgundy)
        # West side
        create_cylinder(f"MATH_10th_Chair_Stem_W_{cy}", col_int, (-2.2, cy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Seat_W_{cy}", col_int, (-2.2, cy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Back_W_{cy}", col_int, (-2.5, cy, 30.90), (0.08, 0.52, 0.65), mat_leather_burgundy)
    for hy, hrot in [(-5.4, 0), (5.4, math.pi)]:
        create_cylinder(f"MATH_10th_Chair_Head_Stem_{hy}", col_int, (0, hy, 30.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"MATH_10th_Chair_Head_Seat_{hy}", col_int, (0, hy, 30.55), (0.55, 0.55, 0.08), mat_leather_burgundy)
        create_box(f"MATH_10th_Chair_Head_Back_{hy}", col_int, (0, hy + (0.3 if hy>0 else -0.3), 30.90), (0.52, 0.08, 0.65), mat_leather_burgundy)

    # Large Colloquium Proof Blackboard on North Feature Wall
    create_box("MATH_10th_Colloquium_Board_Frame", col_int, (0, 17.85, 31.4), (9.0, 0.05, 1.8), mat_honey_oak)
    create_box("MATH_10th_Colloquium_Board_Panel", col_int, (0, 17.82, 31.4), (8.8, 0.02, 1.6), mat_blackboard)
    bpy.ops.object.text_add(location=(-3.8, 17.80, 31.4), rotation=(math.pi/2, 0, 0))
    txt = bpy.context.active_object
    txt.name = "MATH_10th_Colloquium_Text"
    txt.data.body = "FACULTY COLLOQUIUM: RIEMANN HYPOTHESIS & SPECTRAL THEORY"
    txt.data.size = 0.25
    txt.data.extrude = 0.02
    txt.data.materials.append(mat_chalk)
    txt.parent = root_obj
    col_int.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # Lounge Area with Chesterfield Sofas and Coffee Bar
    create_box("MATH_10th_Sofa_Base", col_int, (-6.5, 0, 30.05), (1.4, 3.6, 0.35), mat_leather_burgundy)
    create_box("MATH_10th_Sofa_Back", col_int, (-7.1, 0, 30.50), (0.35, 3.6, 0.55), mat_leather_burgundy)
    create_box("MATH_10th_Coffee_Table", col_int, (-4.8, 0, 30.0), (0.8, 2.2, 0.25), mat_walnut)
    create_box("MATH_10th_Credenza", col_int, (0, -17.6, 30.35), (4.5, 0.7, 0.85), mat_walnut)
    create_box("MATH_10th_Espresso_Machine", col_int, (-1.2, -17.6, 30.95), (0.6, 0.5, 0.4), mat_bronze)

    # Warm Overhead Downlights in Sky Lounge
    for lx in [-5.0, 0.0, 5.0]:
        for ly in [-8.0, 0.0, 8.0]:
            light_data = bpy.data.lights.new(name=f"MATH_10th_Light_{lx}_{ly}", type="POINT")
            light_data.energy = 650.0
            light_data.color = (1.0, 0.94, 0.86)
            light_obj = bpy.data.objects.new(name=f"MATH_10th_Light_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-180.62 + lx, -127.29 + ly, 32.7)
            col_int.objects.link(light_obj)

    print("Building 62_Math_Sciences_Plaza_and_Site...")

    # 1. Sunken Outdoor Courtyard / Plaza on East side (towards Memorial Mall & CL50)
    create_box("MATH_Sunken_Plaza_Floor", col_site, (23.5, -6.0, -2.15), (10.0, 24.0, 0.3), mat_concrete)
    create_box("MATH_Sunken_Wall_East", col_site, (28.6, -6.0, -1.0), (0.4, 24.0, 2.4), mat_dark_concrete)
    create_box("MATH_Sunken_Wall_North", col_site, (23.5, 6.2, -1.0), (10.0, 0.4, 2.4), mat_dark_concrete)
    create_box("MATH_Sunken_Wall_South", col_site, (23.5, -18.2, -1.0), (10.0, 0.4, 2.4), mat_dark_concrete)
    for st in range(5):
        step_z = -2.1 + (st + 1) * 0.35
        step_x = 27.5 - st * 0.6
        create_box(f"MATH_Sunken_Step_{st+1}", col_site, (step_x, -6.0, step_z), (0.6, 20.0, 0.35), mat_concrete)

    # 2. Main Ground-Level Arrival Plazas
    create_box("MATH_West_Plaza_Brick", col_site, (-24.5, 0, 0.05), (11.0, 64.0, 0.1), mat_brick)
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

    print("Re-Calibrating Inspection Cameras Cam_92 through Cam_96 for Flawless Composition...")

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
    # Stepped back along University St to frame full 10-story tower with precast concrete waffle grid, pilotis, and canopy
    setup_camera("Cam_92_MATH_UniversitySt_Hero", (-248.0, -175.0, 12.0), (74.0, 0.0, -52.0), lens=18.0)

    # Cam 93: MATH 175 Major Tiered Lecture Hall Interior
    # Located inside the room on top tier, looking down across desks toward blackboard proofs and instructor dais
    setup_camera("Cam_93_MATH_175_LectureHall_Interior", (-185.62, -135.0, 3.2), (76.0, 0.0, 0.0), lens=20.0)

    # Cam 94: Mathematical Sciences Library Interior (Floor 3)
    # Looking from southwest across study tables, banker's lamps, laptops, and book stacks towards the east windows
    setup_camera("Cam_94_MATH_Library_Study_Interior", (-188.0, -119.0, 12.5), (78.0, 0.0, -50.0), lens=18.0)

    # Cam 95: 10th-Floor Faculty Colloquium Sky Lounge Interior
    # Looking from southwest across conference table, burgundy leather chairs, proof blackboard, and panoramic windows
    setup_camera("Cam_95_MATH_10thFloor_SkyLounge_Interior", (-186.0, -137.0, 31.4), (74.0, 0.0, -32.0), lens=20.0)

    # Cam 96: Precinct Aerial Context
    # Elevated overview framing the full 10-story tower with precast waffle grid, rooftop penthouse, sunken plaza, and Oval Drive
    setup_camera("Cam_96_MATH_Precinct_Aerial", (-130.0, -195.0, 65.0), (58.0, 0.0, 40.0), lens=24.0)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend File saved successfully with Mathematical Sciences Building (MATH) Attempt 2!")

if __name__ == "__main__":
    run_attempt2()
