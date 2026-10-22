"""
Pass 3 Polish: True Hollow Architectural Envelopes & Flawless Interior Visibility
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

def polish_pass3():
    col_ext = get_col('27_Winifred_Parker_Hall_Exterior')
    col_int = get_col('28_Winifred_Parker_Hall_Interiors')
    col_site = get_col('29_Winifred_Parker_Hall_Courtyard_and_Site')

    # Materials
    mat_wall_ivory = get_or_create_mat("Parker_Wall_Ivory", (0.92, 0.90, 0.85, 1.0), roughness=0.8)
    mat_starbucks_green = get_or_create_mat("Parker_Starbucks_Green", (0.005, 0.12, 0.05, 1.0), roughness=0.4)
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

    # ---------------------------------------------------------
    # 1. PURGE SOLID INTRUSIVE SLABS (Replace with Perimeter Wall Strips)
    # ---------------------------------------------------------
    # Remove the solid water table blocks that were filling the interiors
    for obj_name in ["Parker_Base_WaterTable_South", "Parker_Base_WaterTable_East", "Parker_Base_WaterTable_North", "Parker_Base_WaterTable_Center"]:
        old = bpy.data.objects.get(obj_name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)

    # Remove any solid beltcourses at Z=4.2 that filled the interior
    old_b0 = bpy.data.objects.get("Parker_Beltcourse_South_0")
    if old_b0:
        bpy.data.objects.remove(old_b0, do_unlink=True)

    # Build authentic hollow PERIMETER water table base strips (0.4m thick, 1.2m high)
    # South facade base strip along Third Street (Y = 11.7m)
    create_box("Parker_WaterTable_Strip_South", (-562.65, 11.65, 0.6), (54.5, 0.4, 1.2), mat_limestone, col_ext)
    # West facade base strip along Russell Street (X = -589.9m)
    create_box("Parker_WaterTable_Strip_West", (-589.7, 20.1, 0.6), (0.4, 16.4, 1.2), mat_limestone, col_ext)
    # North ground wall base strip (Y = 28.3m)
    create_box("Parker_WaterTable_Strip_North", (-562.65, 28.15, 0.6), (54.5, 0.4, 1.2), mat_limestone, col_ext)
    # East ground wall base strip (X = -535.4m)
    create_box("Parker_WaterTable_Strip_East", (-535.6, 20.1, 0.6), (0.4, 16.4, 1.2), mat_limestone, col_ext)

    # Perimeter beltcourse stringer at Z = 4.2m along South facade
    create_box("Parker_Beltcourse_Stringer_South_0", (-562.65, 11.60, 4.2), (54.5, 0.35, 0.35), mat_limestone, col_ext)

    # ---------------------------------------------------------
    # 2. CAMPUS STARBUCKS INTERIOR (Prismatic Layout & Clear Sightlines)
    # ---------------------------------------------------------
    sb_cx = -578.0
    sb_cy = 20.0
    # Pristine walnut floor slab (Z = 0.02 to 0.12)
    create_box("Parker_Starbucks_Floor", (sb_cx, sb_cy, 0.08), (21.5, 14.5, 0.12), mat_wood_walnut, col_int)

    # L-Shaped Barista Counter
    # Front service counter (X: -578 to -570, Y = 22.0, Z = 0.12 to 1.22)
    create_box("Parker_Starbucks_FrontCounter_Base", (-574.0, 22.0, 0.65), (8.0, 1.1, 1.05), mat_oak, col_int)
    create_box("Parker_Starbucks_FrontCounter_Top", (-574.0, 22.0, 1.20), (8.2, 1.3, 0.08), mat_quartz, col_int)
    # Return counter (X = -578.0, Y: 22 to 26)
    create_box("Parker_Starbucks_ReturnCounter_Base", (-578.0, 24.2, 0.65), (1.1, 4.2, 1.05), mat_oak, col_int)
    create_box("Parker_Starbucks_ReturnCounter_Top", (-578.0, 24.2, 1.20), (1.3, 4.4, 0.08), mat_quartz, col_int)

    # Espresso Machines & POS Terminals
    create_box("Parker_Starbucks_Espresso_1", (-575.5, 22.0, 1.55), (0.85, 0.75, 0.6), mat_bronze, col_int)
    create_box("Parker_Starbucks_Espresso_2", (-573.5, 22.0, 1.55), (0.85, 0.75, 0.6), mat_bronze, col_int)
    create_box("Parker_Starbucks_PastryCase", (-571.5, 22.0, 1.55), (1.6, 0.85, 0.6), mat_glass, col_int)

    # Green Starbucks Feature Wall & Illuminated Siren Logo
    create_box("Parker_Starbucks_FeatureWall", (-568.0, sb_cy, 2.1), (0.25, 14.5, 4.0), mat_starbucks_green, col_int)
    create_cylinder("Parker_Starbucks_Interior_Siren", (-567.8, sb_cy, 2.4), 1.0, 0.08, mat_starbucks_logo, col_int)

    # Menu Boards (Above Counter)
    for b in range(4):
        bx = -576.5 + b * 1.8
        create_box(f"Parker_Starbucks_MenuBoard_{b}", (bx, 22.0, 3.1), (1.5, 0.06, 0.9), mat_warm_glow, col_int)

    # Cafe High-Top Tables & Barstools
    for idx in range(3):
        tx = -583.5 + idx * 3.6
        create_cylinder(f"Parker_SB_Table_{idx}", (tx, 15.5, 0.62), 0.55, 1.05, mat_bronze, col_int)
        create_cylinder(f"Parker_SB_Top_{idx}", (tx, 15.5, 1.18), 0.72, 0.06, mat_quartz, col_int)
        create_cylinder(f"Parker_SB_StoolA_{idx}", (tx - 0.7, 15.5, 0.42), 0.22, 0.75, mat_oak, col_int)
        create_cylinder(f"Parker_SB_StoolB_{idx}", (tx + 0.7, 15.5, 0.42), 0.22, 0.75, mat_oak, col_int)

    # Community Dining Table
    create_box("Parker_Starbucks_CommunityTable", (-578.5, 18.0, 0.62), (4.5, 1.2, 1.05), mat_oak, col_int)
    create_box("Parker_Starbucks_CommunityTop", (-578.5, 18.0, 1.18), (4.7, 1.4, 0.06), mat_oak, col_int)

    # Hanging Pendant Lamps (Adjusted higher to open sightlines)
    for idx, px in enumerate([-580.5, -578.5, -576.5]):
        create_cylinder(f"Parker_SB_PendantCord_{idx}", (px, 18.0, 3.2), 0.015, 1.4, mat_bronze, col_int)
        create_cylinder(f"Parker_SB_PendantShade_{idx}", (px, 18.0, 2.45), 0.25, 0.25, mat_starbucks_green, col_int)
        create_cylinder(f"Parker_SB_PendantBulb_{idx}", (px, 18.0, 2.35), 0.08, 0.10, mat_warm_glow, col_int)

    # ---------------------------------------------------------
    # 3. MAIN RECEPTION LOBBY INTERIOR (Terrazzo & Purdue Seal)
    # ---------------------------------------------------------
    lob_cx = -559.0
    lob_cy = 20.0
    # Terrazzo floor (Z = 0.08)
    create_box("Parker_Lobby_Terrazzo_Floor", (lob_cx, lob_cy, 0.08), (17.5, 14.5, 0.12), mat_terrazzo, col_int)

    # Reception Front Desk
    create_box("Parker_Reception_Desk_Base", (lob_cx + 2.0, lob_cy + 3.0, 0.65), (4.8, 1.3, 1.05), mat_oak, col_int)
    create_box("Parker_Reception_Desk_Top", (lob_cx + 2.0, lob_cy + 3.0, 1.20), (5.0, 1.5, 0.08), mat_quartz, col_int)
    create_box("Parker_Reception_Monitor", (lob_cx + 2.0, lob_cy + 3.0, 1.48), (0.7, 0.15, 0.45), mat_bronze, col_int)

    # Parcel Lockers
    create_box("Parker_Parcel_Lockers", (lob_cx - 6.5, lob_cy + 3.5, 1.5), (0.8, 5.0, 2.7), mat_bronze, col_int)

    # Purdue Seal and Memorial Plaque on North wall
    create_cylinder("Parker_Lobby_Purdue_Seal", (lob_cx + 2.0, 27.7, 2.6), 1.0, 0.08, mat_sign_gold, col_int)
    create_box("Parker_Lobby_Memorial_Plaque", (lob_cx - 3.5, 27.7, 2.2), (2.4, 0.08, 1.4), mat_sign_gold, col_int)

    # Modular Lounge Seating
    create_box("Parker_Lobby_Modular_Sofa", (lob_cx + 2.0, lob_cy - 2.5, 0.5), (5.2, 1.8, 0.8), mat_fabric_navy, col_int)
    create_box("Parker_Lobby_Coffee_Table", (lob_cx + 2.0, lob_cy - 0.8, 0.28), (3.8, 0.9, 0.4), mat_oak, col_int)

    # ---------------------------------------------------------
    # 4. RECALIBRATE INSPECTION CAMERAS FOR MAXIMUM AESTHETIC CLARITY
    # ---------------------------------------------------------
    # Cam_38 Starbucks: Framed across cafe tables towards the barista bar
    cam38 = bpy.data.objects.get('Cam_38_Winifred_Parker_Starbucks_Interior')
    if cam38:
        cam38.location = (-583.5, 14.5, 1.6)
        t_loc = mathutils.Vector((-574.0, 21.5, 1.35))
        c_loc = mathutils.Vector(cam38.location)
        cam38.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam38.data.lens = 22.0

    # Cam_39 Main Lobby: Framed across terrazzo floor towards reception desk & seal
    cam39 = bpy.data.objects.get('Cam_39_Winifred_Parker_Main_Lobby_Interior')
    if cam39:
        cam39.location = (-564.0, 14.5, 1.6)
        t_loc = mathutils.Vector((-557.0, 22.5, 1.5))
        c_loc = mathutils.Vector(cam39.location)
        cam39.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam39.data.lens = 22.0

    print("Pass 3 Polish completed successfully!")

if __name__ == '__main__':
    polish_pass3()
