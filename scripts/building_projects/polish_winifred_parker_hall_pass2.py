"""
Pass 2 Polish: High-Impact Photorealism & Hollowed Architectural Envelopes
for Winifred Parker Hall (Purdue University Digital Twin)
Master Blend: purdue_campus_master.blend
"""

import bpy
import bmesh
import mathutils
import math

CENTER_X = -562.65
CENTER_Y = 49.53
GROUND_Z = 0.0

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

def polish_winifred_parker_hall():
    col_ext = get_col('27_Winifred_Parker_Hall_Exterior')
    col_int = get_col('28_Winifred_Parker_Hall_Interiors')
    col_site = get_col('29_Winifred_Parker_Hall_Courtyard_and_Site')

    # Materials
    mat_wall_ivory = get_or_create_mat("Parker_Wall_Ivory", (0.92, 0.90, 0.85, 1.0), roughness=0.8)
    mat_starbucks_green = get_or_create_mat("Parker_Starbucks_Green", (0.005, 0.12, 0.05, 1.0), roughness=0.4)
    mat_wall_starbucks = mat_starbucks_green
    mat_wood_walnut = get_or_create_mat("Parker_Wood_Floor_Walnut", (0.28, 0.15, 0.08, 1.0), roughness=0.45)
    mat_terrazzo = get_or_create_mat("Parker_Terrazzo_Cream", (0.86, 0.84, 0.78, 1.0), roughness=0.22)
    mat_quartz = get_or_create_mat("Parker_White_Quartz", (0.92, 0.92, 0.91, 1.0), roughness=0.25)
    mat_oak = get_or_create_mat("Parker_Oak_Furniture", (0.62, 0.44, 0.24, 1.0), roughness=0.5)
    mat_fabric_navy = get_or_create_mat("Parker_Fabric_Navy", (0.04, 0.08, 0.22, 1.0), roughness=0.8)
    mat_warm_glow = get_or_create_mat("Parker_Warm_Ceiling_Glow", (1.0, 0.92, 0.78, 1.0), roughness=0.2, emission=(1.0, 0.92, 0.78, 1.0), emission_str=3.5)
    mat_bronze = get_or_create_mat("Parker_Bronze_Mullion", (0.12, 0.10, 0.08, 1.0), roughness=0.4, metallic=0.85)
    mat_starbucks_logo = get_or_create_mat("Parker_Starbucks_Logo", (0.92, 0.98, 0.92, 1.0), roughness=0.2, emission=(0.85, 1.0, 0.85, 1.0), emission_str=4.5)
    mat_glass = get_or_create_mat("Parker_Solar_Curtain_Glass", (0.02, 0.05, 0.07, 1.0), roughness=0.05, metallic=0.1, transmission=0.88, ior=1.52)
    mat_brick = get_or_create_mat("Parker_Purdue_Red_Brick", (0.50, 0.16, 0.11, 1.0), roughness=0.85)
    mat_limestone = get_or_create_mat("Parker_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mat_sign_gold = get_or_create_mat("Parker_Signage_Gold", (0.88, 0.72, 0.28, 1.0), roughness=0.3, metallic=0.85)
    mat_concrete = get_or_create_mat("Parker_Plaza_Concrete", (0.55, 0.55, 0.54, 1.0), roughness=0.8)

    # ---------------------------------------------------------
    # 1. HOLLOW OUT GROUND FLOOR & UPPER SUITES MASSING
    # ---------------------------------------------------------
    # The South Wing solid box Parker_SouthWing_MainMass is elevated so ground floor is hollow!
    # Height of ground floor: Z = 0.0 to 4.2m. Upper floors: Z = 4.2 to 20.2m (height 16.0m)
    s_cx = -562.65
    s_cy = 20.1
    s_w = 54.5
    s_d = 16.4
    create_box("Parker_SouthWing_MainMass", (s_cx, s_cy, 12.2), (s_w, s_d, 16.0), mat_brick, col_ext)

    # Intermediate floor slab separating ground floor from upper floors
    create_box("Parker_Ground_Ceiling_Slab", (s_cx, s_cy, 4.1), (s_w, s_d, 0.2), mat_concrete, col_int)

    # Ground floor perimeter walls (North wall, West wall, East wall)
    # North wall of ground floor (Y = 28.3, Z = 0 to 4.2)
    create_box("Parker_Ground_NorthWall", (s_cx, 28.15, 2.1), (s_w, 0.3, 4.2), mat_brick, col_ext)
    create_box("Parker_Ground_NorthWall_Interior", (s_cx, 27.95, 2.1), (s_w - 0.6, 0.1, 4.0), mat_wall_ivory, col_int)

    # West wall of ground floor along Russell St (X = -589.9, Y in [11.9, 28.3])
    create_box("Parker_Ground_WestWall", (-589.75, s_cy, 2.1), (0.3, s_d, 4.2), mat_brick, col_ext)
    create_box("Parker_Ground_WestWall_Interior", (-589.55, s_cy, 2.1), (0.1, s_d - 0.6, 4.0), mat_wall_ivory, col_int)

    # East wall of ground floor (X = -535.4)
    create_box("Parker_Ground_EastWall", (-535.55, s_cy, 2.1), (0.3, s_d, 4.2), mat_brick, col_ext)

    # Interior partition wall between Starbucks and Main Lobby (X = -568.0, Y in [11.9, 28.3])
    create_box("Parker_Starbucks_Lobby_Partition", (-568.0, s_cy, 2.1), (0.3, s_d - 0.6, 4.0), mat_wall_starbucks, col_int)
    # Connecting archway / double door between Starbucks and Lobby
    create_box("Parker_Starbucks_Lobby_DoorFrame", (-568.0, 20.0, 1.5), (0.35, 2.4, 3.0), mat_bronze, col_int)

    # Interior partition wall between Main Lobby and Third Street Market (X = -550.0, Y in [11.9, 28.3])
    create_box("Parker_Lobby_Market_Partition", (-550.0, s_cy, 2.1), (0.3, s_d - 0.6, 4.0), mat_wall_ivory, col_int)

    # ---------------------------------------------------------
    # 2. POLISH CAMPUS STARBUCKS INTERIOR (High-End Retail Details)
    # ---------------------------------------------------------
    sb_cx = -578.0
    sb_cy = 20.0

    # Walnut flooring perfectly aligned at Z = 0.05m
    create_box("Parker_Starbucks_Floor", (sb_cx, sb_cy, 0.05), (21.0, 15.0, 0.1), mat_wood_walnut, col_int)

    # Dark oak baseboards along walls
    create_box("Parker_Starbucks_Baseboard_N", (sb_cx, 27.8, 0.15), (21.0, 0.1, 0.2), mat_oak, col_int)
    create_box("Parker_Starbucks_Baseboard_W", (-589.4, sb_cy, 0.15), (0.1, 15.0, 0.2), mat_oak, col_int)

    # Starbucks Coffee Menu Board with full graphic elements
    for b in range(4):
        bx = -576.5 + b * 1.8
        create_box(f"Parker_Starbucks_MenuBoard_{b}", (bx, 22.0, 3.1), (1.6, 0.08, 0.95), mat_warm_glow, col_int)
        # Menu frame
        create_box(f"Parker_Starbucks_MenuFrame_{b}", (bx, 22.0, 3.1), (1.7, 0.06, 1.05), mat_bronze, col_int)

    # Condiment bar for students (sugars, napkins, stirrers)
    create_box("Parker_Starbucks_CondimentBar", (-587.0, 15.0, 0.55), (1.2, 3.2, 1.1), mat_oak, col_int)
    create_box("Parker_Starbucks_CondimentTop", (-587.0, 15.0, 1.15), (1.3, 3.3, 0.1), mat_quartz, col_int)

    # Community high-top wood table in center cafe
    create_box("Parker_Starbucks_CommunityTable", (-579.0, 15.5, 0.55), (4.5, 1.2, 1.1), mat_oak, col_int)
    create_box("Parker_Starbucks_CommunityTop", (-579.0, 15.5, 1.12), (4.7, 1.4, 0.08), mat_oak, col_int)
    for s in range(6):
        sx = -580.8 + s * 0.72
        create_cylinder(f"Parker_SB_CommStool_A_{s}", (sx, 14.5, 0.4), 0.2, 0.8, mat_bronze, col_int)
        create_cylinder(f"Parker_SB_CommStool_B_{s}", (sx, 16.5, 0.4), 0.2, 0.8, mat_bronze, col_int)

    # Warm ceiling pendant lamps hanging over tables
    for idx, px in enumerate([-581.0, -579.0, -577.0]):
        create_cylinder(f"Parker_SB_PendantCord_{idx}", (px, 15.5, 2.8), 0.02, 2.0, mat_bronze, col_int)
        create_cylinder(f"Parker_SB_PendantShade_{idx}", (px, 15.5, 1.9), 0.25, 0.25, mat_starbucks_green, col_int)
        create_cylinder(f"Parker_SB_PendantBulb_{idx}", (px, 15.5, 1.8), 0.10, 0.12, mat_warm_glow, col_int)

    # ---------------------------------------------------------
    # 3. POLISH MAIN RECEPTION LOBBY INTERIOR
    # ---------------------------------------------------------
    lob_cx = -559.0
    lob_cy = 20.0

    # Terrazzo flooring
    create_box("Parker_Lobby_Terrazzo_Floor", (lob_cx, lob_cy, 0.05), (17.0, 15.0, 0.1), mat_terrazzo, col_int)
    # Oak baseboards
    create_box("Parker_Lobby_Baseboard_N", (lob_cx, 27.8, 0.15), (17.0, 0.1, 0.2), mat_oak, col_int)

    # Purdue Boilermakers Athletic Gold Emblem on Lobby Feature Wall
    create_cylinder("Parker_Lobby_Purdue_Seal", (lob_cx + 2.0, 27.75, 2.6), 1.0, 0.08, mat_sign_gold, col_int)

    # Winifred Parker White Historical Memorial Plaque
    create_box("Parker_Lobby_Memorial_Plaque", (lob_cx - 4.0, 27.75, 2.2), (2.2, 0.08, 1.4), mat_sign_gold, col_int)

    # Reception Desk with keycard access console and digital monitor
    create_box("Parker_Reception_Desk_Base", (lob_cx + 2.0, lob_cy + 3.0, 0.55), (4.8, 1.4, 1.1), mat_oak, col_int)
    create_box("Parker_Reception_Desk_Top", (lob_cx + 2.0, lob_cy + 3.0, 1.15), (5.0, 1.6, 0.1), mat_quartz, col_int)
    create_box("Parker_Reception_Monitor", (lob_cx + 2.0, lob_cy + 3.0, 1.45), (0.7, 0.15, 0.45), mat_bronze, col_int)

    # Modern modular sectional lounge seating with coffee table
    create_box("Parker_Lobby_Modular_Sofa", (lob_cx + 2.0, lob_cy - 2.5, 0.45), (5.2, 1.8, 0.75), mat_fabric_navy, col_int)
    create_box("Parker_Lobby_Coffee_Table", (lob_cx + 2.0, lob_cy - 0.8, 0.25), (3.8, 0.9, 0.4), mat_oak, col_int)

    # ---------------------------------------------------------
    # 4. POLISH UPPER-FLOOR STUDENT SUITE (Model Unit Floor 2)
    # ---------------------------------------------------------
    # Hollow out East Wing model suite zone (Y in [30, 46], Z in [4.2, 7.4])
    # The solid East Wing main mass is split so the suite is completely open!
    create_box("Parker_EastWing_MainMass_North", (-541.8, 64.0, 12.2), (12.8, 37.0, 16.0), mat_brick, col_ext)
    create_box("Parker_EastWing_MainMass_South", (-541.8, 28.0, 12.2), (12.8, 5.0, 16.0), mat_brick, col_ext)
    create_box("Parker_EastWing_MainMass_Upper", (-541.8, 46.0, 15.4), (12.8, 31.0, 9.6), mat_brick, col_ext)

    # Model Suite interior walls (Ivory drywall)
    suite_cx = -542.0
    suite_cy = 38.0
    suite_z = 5.8
    # Suite perimeter walls
    create_box("Parker_Suite_Wall_West", (-547.8, suite_cy, suite_z), (0.2, 16.0, 3.0), mat_wall_ivory, col_int)
    create_box("Parker_Suite_Wall_North", (suite_cx, 46.0, suite_z), (12.0, 0.2, 3.0), mat_wall_ivory, col_int)
    create_box("Parker_Suite_Wall_South", (suite_cx, 30.0, suite_z), (12.0, 0.2, 3.0), mat_wall_ivory, col_int)
    # Interior dividing wall between living room and bedrooms
    create_box("Parker_Suite_Wall_Divide", (suite_cx, 37.5, suite_z), (11.8, 0.2, 3.0), mat_wall_ivory, col_int)
    create_box("Parker_Suite_Door_Divide", (-544.0, 37.5, suite_z - 0.5), (1.2, 0.25, 2.1), mat_oak, col_int)

    # ---------------------------------------------------------
    # 5. RECALIBRATE INSPECTION CAMERAS FOR OPTIMAL PERSPECTIVES
    # ---------------------------------------------------------
    # Cam_37 Third St Street View: Elevated street perspective
    cam37 = bpy.data.objects.get('Cam_37_Winifred_Parker_ThirdSt_StreetView')
    if cam37:
        cam37.location = (-562.6, -14.0, 4.0)
        t_loc = mathutils.Vector((-562.6, 20.0, 7.5))
        c_loc = mathutils.Vector(cam37.location)
        cam37.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam37.data.lens = 22.0

    # Cam_38 Starbucks Interior: Intimate cafe perspective
    cam38 = bpy.data.objects.get('Cam_38_Winifred_Parker_Starbucks_Interior')
    if cam38:
        cam38.location = (-582.0, 15.0, 1.6)
        t_loc = mathutils.Vector((-574.0, 22.0, 1.5))
        c_loc = mathutils.Vector(cam38.location)
        cam38.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam38.data.lens = 22.0

    # Cam_39 Main Lobby Interior: Looking at reception desk, seal, and lockers
    cam39 = bpy.data.objects.get('Cam_39_Winifred_Parker_Main_Lobby_Interior')
    if cam39:
        cam39.location = (-563.0, 15.5, 1.6)
        t_loc = mathutils.Vector((-557.0, 23.0, 1.6))
        c_loc = mathutils.Vector(cam39.location)
        cam39.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam39.data.lens = 22.0

    # Cam_40 Student Suite Interior: Looking at living room, TV, and bedroom
    cam40 = bpy.data.objects.get('Cam_40_Winifred_Parker_Student_Suite_Interior')
    if cam40:
        cam40.location = (-546.0, 31.5, 6.2)
        t_loc = mathutils.Vector((-540.0, 38.5, 5.6))
        c_loc = mathutils.Vector(cam40.location)
        cam40.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam40.data.lens = 20.0

    # Cam_41 Inner Courtyard: View from Parker Quad looking at East Wing
    cam41 = bpy.data.objects.get('Cam_41_Winifred_Parker_Inner_Courtyard')
    if cam41:
        cam41.location = (-498.0, 56.0, 6.8)
        t_loc = mathutils.Vector((-542.0, 55.0, 9.5))
        c_loc = mathutils.Vector(cam41.location)
        cam41.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam41.data.lens = 24.0

    print("Pass 2 Polish completed successfully!")

if __name__ == '__main__':
    polish_winifred_parker_hall()
