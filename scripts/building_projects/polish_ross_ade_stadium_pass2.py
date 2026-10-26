"""
Pass 2 Polish: High-Impact Realism & Architectural Refinement for Ross-Ade Stadium
Purdue University Digital Twin Project
Master Blend: purdue_campus_master.blend
"""

import bpy
import bmesh
import mathutils
import math

CENTER_X = -403.2
CENTER_Y = 805.2
FIELD_Z = 0.0

def get_col(name):
    return bpy.data.collections.get(name)

def get_or_create_mat(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, emission=None, emission_str=1.0, ior=1.45):
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_str
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_str
    return mat

def create_box(name, loc, size, mat=None, col=None):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat:
        mesh.materials.append(mat)
    if col:
        col.objects.link(obj)
    return obj

def create_cylinder(name, loc, radius, depth, mat=None, col=None, verts=24):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=verts,
        radius1=radius,
        radius2=radius,
        depth=depth
    )
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat:
        mesh.materials.append(mat)
    if col:
        col.objects.link(obj)
    return obj

def polish_ross_ade():
    col_field = get_col('23_Ross_Ade_Field_and_Bowl')
    col_pav = get_col('24_Ross_Ade_West_Pavilion_and_Suites')
    col_south = get_col('25_Ross_Ade_South_Endzone_Renovation')
    col_ext = get_col('26_Ross_Ade_Gates_Lighting_and_Site')
    col_cams = get_col('05_Cameras_and_Views')

    # Materials
    mat_dark_metal = get_or_create_mat("RossAde_Steel_Lattice_Black", (0.04, 0.04, 0.04, 1.0), roughness=0.4, metallic=0.9)
    mat_gold_glow = get_or_create_mat("RossAde_Wordmark_Gold_Emissive", (0.92, 0.76, 0.28, 1.0), roughness=0.2, emission=(0.95, 0.80, 0.30, 1.0), emission_str=4.0)
    mat_screen_bg = get_or_create_mat("RossAde_Screen_Background_Navy", (0.01, 0.02, 0.04, 1.0), roughness=0.15)
    mat_screen_gold = get_or_create_mat("RossAde_Screen_Graphic_Gold", (0.95, 0.82, 0.32, 1.0), roughness=0.2, emission=(0.98, 0.85, 0.35, 1.0), emission_str=5.0)
    mat_screen_white = get_or_create_mat("RossAde_Screen_Graphic_White", (0.95, 0.95, 0.95, 1.0), roughness=0.2, emission=(1.0, 1.0, 1.0, 1.0), emission_str=6.0)
    mat_screen_red = get_or_create_mat("RossAde_Screen_Graphic_Red", (0.85, 0.08, 0.08, 1.0), roughness=0.2, emission=(0.95, 0.1, 0.1, 1.0), emission_str=4.0)
    mat_aisle_yellow = get_or_create_mat("RossAde_Aisle_Safety_Yellow", (0.92, 0.78, 0.12, 1.0), roughness=0.5)
    mat_suite_interior_glow = get_or_create_mat("RossAde_Suite_Interior_WarmGlow", (0.95, 0.88, 0.72, 1.0), roughness=0.4, emission=(0.95, 0.88, 0.72, 1.0), emission_str=2.5)
    mat_concrete = get_or_create_mat("RossAde_Concrete_Structure", (0.45, 0.45, 0.44, 1.0), roughness=0.8)
    mat_brick = get_or_create_mat("RossAde_Purdue_Red_Brick", (0.48, 0.16, 0.11, 1.0), roughness=0.85)
    mat_limestone = get_or_create_mat("RossAde_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mat_endzone_gold = get_or_create_mat("RossAde_Endzone_Gold", (0.82, 0.66, 0.32, 1.0), roughness=0.6)

    # ---------------------------------------------------------
    # 1. FIX GOALPOST NETTING (Remove solid slabs, replace with realistic slim poles & cables)
    # ---------------------------------------------------------
    for end_name in ["South", "North"]:
        old_obj = bpy.data.objects.get(f"RossAde_Netting_Support_{end_name}")
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
    for end_name, y_endline, y_dir in [("South", CENTER_Y - 54.86, -1.0), ("North", CENTER_Y + 54.86, 1.0)]:
        pole_y = y_endline + y_dir * 8.5
        # Left and Right slim black poles (height 15m, radius 0.10m)
        create_cylinder(f"RossAde_NetPole_{end_name}_L", (CENTER_X - 10.0, pole_y, 7.5), 0.10, 15.0, mat_dark_metal, col_field)
        create_cylinder(f"RossAde_NetPole_{end_name}_R", (CENTER_X + 10.0, pole_y, 7.5), 0.10, 15.0, mat_dark_metal, col_field)
        # Top cross cable
        create_box(f"RossAde_NetCable_{end_name}_Top", (CENTER_X, pole_y, 14.8), (20.0, 0.05, 0.05), mat_dark_metal, col_field)

    # ---------------------------------------------------------
    # 2. ROHRMAN VIDEO BOARD POLISH (Photorealistic Graphics & Details)
    # ---------------------------------------------------------
    board_y = CENTER_Y - 95.0
    board_z = 24.5
    screen_w = 45.82
    screen_h = 17.3

    # Main screen backdrop (Dark stadium LED matrix)
    create_box(
        "RossAde_Rohrman_Screen_Backdrop",
        (CENTER_X, board_y + 0.35, board_z),
        (screen_w - 0.2, 0.1, screen_h - 0.2),
        mat_screen_bg,
        col_south
    )
    # Top Gold Banner: "PURDUE BOILERMAKERS"
    create_box(
        "RossAde_Screen_Top_Header_Gold",
        (CENTER_X, board_y + 0.42, board_z + 6.8),
        (screen_w - 4.0, 0.1, 1.6),
        mat_screen_gold,
        col_south
    )
    # Center Giant Glowing Motion 'P'
    create_box(
        "RossAde_Screen_Motion_P_Backing",
        (CENTER_X, board_y + 0.42, board_z),
        (11.0, 0.1, 8.5),
        mat_screen_white,
        col_south
    )
    create_box(
        "RossAde_Screen_Motion_P_Gold_Core",
        (CENTER_X, board_y + 0.48, board_z),
        (9.8, 0.1, 7.4),
        mat_screen_gold,
        col_south
    )
    create_box(
        "RossAde_Screen_Motion_P_Cutout",
        (CENTER_X + 1.4, board_y + 0.52, board_z + 1.1),
        (3.4, 0.1, 2.5),
        mat_screen_bg,
        col_south
    )
    # Scoreboard Left & Right Panels
    # Left Score: "PURDUE 35"
    create_box(
        "RossAde_Screen_Score_Purdue_Box",
        (CENTER_X - 15.0, board_y + 0.42, board_z),
        (9.0, 0.1, 5.5),
        mat_screen_bg,
        col_south
    )
    create_box(
        "RossAde_Screen_Score_Purdue_GoldTag",
        (CENTER_X - 15.0, board_y + 0.48, board_z + 1.5),
        (8.0, 0.1, 1.4),
        mat_screen_gold,
        col_south
    )
    create_box(
        "RossAde_Screen_Score_Purdue_Digits",
        (CENTER_X - 15.0, board_y + 0.48, board_z - 1.2),
        (6.0, 0.1, 2.8),
        mat_screen_white,
        col_south
    )
    # Right Score: "OPPONENT 14"
    create_box(
        "RossAde_Screen_Score_Opponent_Box",
        (CENTER_X + 15.0, board_y + 0.42, board_z),
        (9.0, 0.1, 5.5),
        mat_screen_bg,
        col_south
    )
    create_box(
        "RossAde_Screen_Score_Opponent_WhiteTag",
        (CENTER_X + 15.0, board_y + 0.48, board_z + 1.5),
        (8.0, 0.1, 1.4),
        mat_screen_white,
        col_south
    )
    create_box(
        "RossAde_Screen_Score_Opponent_Digits",
        (CENTER_X + 15.0, board_y + 0.48, board_z - 1.2),
        (6.0, 0.1, 2.8),
        mat_screen_red,
        col_south
    )
    # Bottom Game State Ribbon: "4th & 2 | 2:15 4th QTR | ROHRMAN FIELD"
    create_box(
        "RossAde_Screen_Bottom_Ribbon",
        (CENTER_X, board_y + 0.42, board_z - 6.8),
        (screen_w - 4.0, 0.1, 1.4),
        mat_screen_gold,
        col_south
    )

    # ---------------------------------------------------------
    # 3. TYLER TRENT SECTION DETAIL (Benches, Tables, Memorial Plaque)
    # ---------------------------------------------------------
    # Tyler Trent commemorative bronze plaque at center patio
    create_box(
        "RossAde_TylerTrent_Dedication_Plaque",
        (CENTER_X, CENTER_Y - 72.0, 5.2),
        (4.5, 0.2, 1.2),
        mat_gold_glow,
        col_south
    )
    # Open-air patio bar high-top tables & stools across the terrace decks
    for idx in range(-6, 7):
        tx = CENTER_X + idx * 5.0
        # High top table
        create_cylinder(f"RossAde_Patio_Table_{idx}", (tx, CENTER_Y - 76.0, 5.8), 0.7, 1.1, mat_dark_metal, col_south)
        create_cylinder(f"RossAde_Patio_Top_{idx}", (tx, CENTER_Y - 76.0, 6.35), 0.85, 0.08, mat_limestone, col_south)
        # Barstools
        create_cylinder(f"RossAde_Patio_Stool1_{idx}", (tx - 0.75, CENTER_Y - 76.0, 5.4), 0.22, 0.8, mat_dark_metal, col_south)
        create_cylinder(f"RossAde_Patio_Stool2_{idx}", (tx + 0.75, CENTER_Y - 76.0, 5.4), 0.22, 0.8, mat_dark_metal, col_south)

    # ---------------------------------------------------------
    # 4. VERTICAL AISLE STAIRWAYS IN THE BOWL GRANDSTANDS
    # ---------------------------------------------------------
    # 6 yellow-striped stair aisles running vertically up each sideline
    for idx, ay in enumerate([-40.0, -24.0, -8.0, 8.0, 24.0, 40.0]):
        # Lower bowl aisles (West)
        create_box(
            f"RossAde_Aisle_West_Lower_{idx}",
            (CENTER_X - 44.0, CENTER_Y + ay, 5.0),
            (26.0, 1.4, 0.1),
            mat_aisle_yellow,
            col_field
        )
        # Lower bowl aisles (East)
        create_box(
            f"RossAde_Aisle_East_Lower_{idx}",
            (CENTER_X + 44.0, CENTER_Y + ay, 5.0),
            (26.0, 1.4, 0.1),
            mat_aisle_yellow,
            col_field
        )
        # Upper bowl aisles (East)
        create_box(
            f"RossAde_Aisle_East_Upper_{idx}",
            (CENTER_X + 75.5, CENTER_Y + ay, 16.5),
            (24.0, 1.4, 0.1),
            mat_aisle_yellow,
            col_field
        )

    # ---------------------------------------------------------
    # 5. WEST PAVILION INTERIOR SUITE LIGHTING & DETAIL
    # ---------------------------------------------------------
    # Behind the glass ribbons, add warm interior ceiling illumination slabs
    # Level 1 Shively Club Interior
    create_box(
        "RossAde_ShivelyClub_Interior_Ceiling",
        (CENTER_X - 70.0, CENTER_Y, 17.0),
        (12.0, 104.0, 0.2),
        mat_suite_interior_glow,
        col_pav
    )
    # Level 2 Buchanan Suites Interior
    create_box(
        "RossAde_Buchanan_Interior_Ceiling",
        (CENTER_X - 70.0, CENTER_Y, 22.8),
        (12.0, 104.0, 0.2),
        mat_suite_interior_glow,
        col_pav
    )
    # Level 3 Upper Suites Interior
    create_box(
        "RossAde_UpperSuites_Interior_Ceiling",
        (CENTER_X - 70.0, CENTER_Y, 28.8),
        (12.0, 104.0, 0.2),
        mat_suite_interior_glow,
        col_pav
    )
    # Level 4 Press Box Interior
    create_box(
        "RossAde_PressBox_Interior_Ceiling",
        (CENTER_X - 70.0, CENTER_Y, 34.5),
        (12.0, 104.0, 0.2),
        mat_suite_interior_glow,
        col_pav
    )

    # ---------------------------------------------------------
    # 6. RECALIBRATE INSPECTION CAMERAS FOR OPTIMAL HERO PERSPECTIVES
    # ---------------------------------------------------------
    # Cam_32 Hero: Elevated 50-yard line 3/4 view capturing field, video board, and bowl
    cam32 = bpy.data.objects.get('Cam_32_Ross_Ade_Field_50YardLine_Hero')
    if cam32:
        cam32.location = (CENTER_X - 26.0, CENTER_Y - 15.0, 3.8)
        t_loc = mathutils.Vector((CENTER_X + 15.0, CENTER_Y + 10.0, 6.0))
        c_loc = mathutils.Vector(cam32.location)
        cam32.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam32.data.lens = 22.0

    # Cam_33 South Endzone Video Board: Crisp view from north 40-yard line
    cam33 = bpy.data.objects.get('Cam_33_Ross_Ade_SouthEndzone_VideoBoard')
    if cam33:
        cam33.location = (CENTER_X, CENTER_Y - 10.0, 5.0)
        t_loc = mathutils.Vector((CENTER_X, board_y, 22.0))
        c_loc = mathutils.Vector(cam33.location)
        cam33.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam33.data.lens = 26.0

    # Cam_34 West Pavilion: Elevated grandstand view
    cam34 = bpy.data.objects.get('Cam_34_Ross_Ade_WestPavilion_Suites')
    if cam34:
        cam34.location = (CENTER_X + 35.0, CENTER_Y, 7.5)
        t_loc = mathutils.Vector((CENTER_X - 78.0, CENTER_Y, 24.0))
        c_loc = mathutils.Vector(cam34.location)
        cam34.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam34.data.lens = 28.0

    # Cam_35 North Bowl: Elevated view from south 40-yard line
    cam35 = bpy.data.objects.get('Cam_35_Ross_Ade_NorthBowl_StudentSection')
    if cam35:
        cam35.location = (CENTER_X, CENTER_Y - 20.0, 6.0)
        t_loc = mathutils.Vector((CENTER_X, CENTER_Y + 95.0, 16.0))
        c_loc = mathutils.Vector(cam35.location)
        cam35.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam35.data.lens = 24.0

    # Cam_36 Street View Exterior Gate: Street perspective looking directly at Southwest Gate A & Floodlight Tower
    cam36 = bpy.data.objects.get('Cam_36_Ross_Ade_StadiumAve_ExteriorGate')
    if cam36:
        cam36.location = (CENTER_X - 115.0, CENTER_Y - 105.0, 3.5)
        t_loc = mathutils.Vector((CENTER_X - 85.0, CENTER_Y - 90.0, 10.0))
        c_loc = mathutils.Vector(cam36.location)
        cam36.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam36.data.lens = 24.0

    print("Pass 2 Polish completed successfully!")

if __name__ == '__main__':
    polish_ross_ade()
