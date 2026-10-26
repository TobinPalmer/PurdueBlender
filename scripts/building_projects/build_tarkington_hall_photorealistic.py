import bpy
import bmesh
import mathutils
import math
import os

def create_box(name, loc, size, mat=None, col=None):
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

def create_cylinder(name, loc, radius, depth, mat=None, col=None, verts=32):
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

def clean_or_create_col(col_name):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return col
    c = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(c)
    return c

def get_or_make_mat(name, base_color, roughness=0.7, metallic=0.0, transmission=0.0, emission=None, emission_strength=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
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
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def look_at(cam_obj, target_pt):
    loc = cam_obj.location
    direction = mathutils.Vector(target_pt) - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def build_tarkington_hall():
    print("===================================================================")
    print("BUILDING NEWTON BOOTH TARKINGTON RESIDENCE HALL (TARK) DIGITAL TWIN")
    print("===================================================================")

    # 1. Collections Setup
    col_ext = clean_or_create_col("17_Tarkington_Hall_Exterior")
    col_int = clean_or_create_col("18_Tarkington_Hall_Interiors")
    col_site = clean_or_create_col("19_Tarkington_Hall_Courtyards_and_Site")

    # 2. Materials Setup
    mat_brick = bpy.data.materials.get("Beering_Purdue_Red_Brick") or get_or_make_mat("Tark_Purdue_Red_Brick", (0.54, 0.18, 0.12, 1.0), roughness=0.82)
    mat_limestone = bpy.data.materials.get("Indiana_Bedford_Limestone") or bpy.data.materials.get("Beering_Bedford_Limestone") or get_or_make_mat("Tark_Bedford_Limestone", (0.82, 0.79, 0.73, 1.0), roughness=0.68)
    mat_glass = bpy.data.materials.get("Beering_Solar_Ribbon_Glass") or bpy.data.materials.get("Glass") or get_or_make_mat("Tark_Window_Glass", (0.1, 0.15, 0.22, 1.0), roughness=0.08, transmission=0.92)
    mat_terrazzo = bpy.data.materials.get("Beering_Lobby_Terrazzo") or bpy.data.materials.get("Interior | cream speckled terrazzo") or get_or_make_mat("Tark_Lobby_Terrazzo", (0.86, 0.84, 0.80, 1.0), roughness=0.18)
    mat_oak = bpy.data.materials.get("Beering_Honey_Oak_Woodwork") or get_or_make_mat("Tark_Oak_Wood", (0.48, 0.31, 0.16, 1.0), roughness=0.45)
    mat_dark_oak = bpy.data.materials.get("Beering_Executive_Dark_Oak") or get_or_make_mat("Tark_Dark_Oak", (0.28, 0.17, 0.09, 1.0), roughness=0.40)
    mat_steel = get_or_make_mat("Tark_Stainless_Steel", (0.85, 0.85, 0.88, 1.0), roughness=0.20, metallic=0.95)
    mat_bronze = get_or_make_mat("Tark_Architectural_Bronze", (0.35, 0.26, 0.15, 1.0), roughness=0.35, metallic=0.80)
    mat_black_granite = bpy.data.materials.get("Purdue_Polished_Black_Granite") or get_or_make_mat("Tark_Black_Countertop", (0.05, 0.05, 0.06, 1.0), roughness=0.15)
    mat_teak = bpy.data.materials.get("Campus_Teak_Wood_Bench") or get_or_make_mat("Tark_Teak_Bench", (0.42, 0.28, 0.16, 1.0), roughness=0.55)
    mat_felt_green = get_or_make_mat("Tark_Billiard_Green_Felt", (0.04, 0.38, 0.16, 1.0), roughness=0.85)
    mat_carpet_blue = get_or_make_mat("Tarkington_Navy_Carpet", (0.08, 0.14, 0.28, 1.0), roughness=0.90)
    mat_roof_gravel = bpy.data.materials.get("Beering_Roof_Membrane") or get_or_make_mat("Tark_Roof_Gravel", (0.28, 0.27, 0.26, 1.0), roughness=0.95)
    mat_white_plastic = get_or_make_mat("Tark_Appliance_White", (0.92, 0.92, 0.92, 1.0), roughness=0.30)
    mat_display_glow = get_or_make_mat("Tark_Display_Emission", (0.1, 0.5, 0.95, 1.0), roughness=0.2, emission=(0.1, 0.6, 1.0, 1.0), emission_strength=4.5)
    mat_pizza_red = get_or_make_mat("Tark_PetesZa_Red_Sign", (0.78, 0.08, 0.08, 1.0), roughness=0.35, emission=(0.85, 0.1, 0.1, 1.0), emission_strength=3.0)

    tc_x, tc_y = -595.0, 353.0
    print(f"Siting Tarkington Hall at georeferenced center ({tc_x}, {tc_y})...")

    h_floor = 3.8
    total_h = 15.2

    # -------------------------------------------------------------
    # 3. EXTERIOR WINGS WITH ACCURATE HOLLOW GROUND FLOORS
    # -------------------------------------------------------------
    # Standard Solid Upper Wings (Floors 2, 3, 4: z = 3.8m to 15.2m)
    wing_configs = [
        {"name": "NW_Wing", "cx": tc_x - 31.5, "cy": tc_y + 35.75, "sx": 27.0, "sy": 47.5, "hollow_gf": False},
        {"name": "SW_Wing", "cx": tc_x - 31.5, "cy": tc_y - 35.75, "sx": 27.0, "sy": 47.5, "hollow_gf": True},
        {"name": "NE_Wing", "cx": tc_x + 31.5, "cy": tc_y + 35.75, "sx": 27.0, "sy": 47.5, "hollow_gf": False},
        {"name": "SE_Wing", "cx": tc_x + 31.5, "cy": tc_y - 35.75, "sx": 27.0, "sy": 47.5, "hollow_gf": False},
        {"name": "Commons_Hub", "cx": tc_x, "cy": tc_y, "sx": 36.0, "sy": 28.0, "hollow_gf": True},
        {"name": "North_Entrance_Pavilion", "cx": tc_x, "cy": tc_y + 21.0, "sx": 24.0, "sy": 14.0, "hollow_gf": False},
        {"name": "South_Entrance_Pavilion", "cx": tc_x, "cy": tc_y - 21.0, "sx": 24.0, "sy": 14.0, "hollow_gf": True},
    ]

    for w in wing_configs:
        w_name = w["name"]
        cx, cy = w["cx"], w["cy"]
        sx, sy = w["sx"], w["sy"]
        hollow_gf = w["hollow_gf"]

        # A. Foundation / Limestone Water Table Base (0.0m to 1.5m)
        if not hollow_gf:
            create_box(
                f"Tark_{w_name}_Limestone_Base",
                loc=(cx, cy, 0.75),
                size=(sx + 0.3, sy + 0.3, 1.5),
                mat=mat_limestone,
                col=col_ext
            )
            # Main Red Brick Shaft (1.5m to 15.2m)
            create_box(
                f"Tark_{w_name}_Brick_Shaft",
                loc=(cx, cy, 1.5 + (total_h - 1.5) * 0.5),
                size=(sx, sy, total_h - 1.5),
                mat=mat_brick,
                col=col_ext
            )
        else:
            # Hollow Ground Floor: Exterior Perimeter Walls Only (z = 0.0 to 3.8m)
            # North Wall
            create_box(f"Tark_{w_name}_GF_Wall_N", loc=(cx, cy + sy*0.5 - 0.2, 1.9), size=(sx, 0.4, 3.8), mat=mat_brick, col=col_ext)
            # South Wall
            create_box(f"Tark_{w_name}_GF_Wall_S", loc=(cx, cy - sy*0.5 + 0.2, 1.9), size=(sx, 0.4, 3.8), mat=mat_brick, col=col_ext)
            # East Wall
            create_box(f"Tark_{w_name}_GF_Wall_E", loc=(cx + sx*0.5 - 0.2, cy, 1.9), size=(0.4, sy, 3.8), mat=mat_brick, col=col_ext)
            # West Wall
            create_box(f"Tark_{w_name}_GF_Wall_W", loc=(cx - sx*0.5 + 0.2, cy, 1.9), size=(0.4, sy, 3.8), mat=mat_brick, col=col_ext)
            
            # Upper Shaft (Floors 2-4: z = 3.8m to 15.2m)
            create_box(
                f"Tark_{w_name}_Upper_Brick_Shaft",
                loc=(cx, cy, 3.8 + (total_h - 3.8) * 0.5),
                size=(sx, sy, total_h - 3.8),
                mat=mat_brick,
                col=col_ext
            )
            # Floor 2 Structural Ceiling Slab over GF
            create_box(
                f"Tark_{w_name}_Ceiling_Slab",
                loc=(cx, cy, 3.8),
                size=(sx + 0.1, sy + 0.1, 0.25),
                mat=mat_limestone,
                col=col_ext
            )

        # C. Limestone Horizontal Beltcourses at each floor level (z = 3.8m, 7.6m, 11.4m, 15.2m)
        for fl_idx, fl_z in enumerate([3.8, 7.6, 11.4, 15.2]):
            create_box(
                f"Tark_{w_name}_Limestone_Belt_{fl_idx+1}",
                loc=(cx, cy, fl_z),
                size=(sx + 0.18, sy + 0.18, 0.22),
                mat=mat_limestone,
                col=col_ext
            )

        # D. Roof Parapet & Perimeter Coping Stone (z = 15.2m to 16.0m)
        create_box(
            f"Tark_{w_name}_Roof_Parapet_Coping",
            loc=(cx, cy, 15.7),
            size=(sx + 0.24, sy + 0.24, 0.40),
            mat=mat_limestone,
            col=col_ext
        )

        # E. Inset Roof Gravel / Waterproof Membrane Slab
        create_box(
            f"Tark_{w_name}_Roof_Membrane",
            loc=(cx, cy, 15.3),
            size=(sx - 0.8, sy - 0.8, 0.15),
            mat=mat_roof_gravel,
            col=col_ext
        )

    # 4. Roof Mechanical Housings & Chimney Stacks
    for p_idx, (px, py) in enumerate([
        (tc_x - 31.5, tc_y + 35.75),
        (tc_x + 31.5, tc_y + 35.75),
        (tc_x - 31.5, tc_y - 35.75),
        (tc_x + 31.5, tc_y - 35.75),
        (tc_x, tc_y)
    ]):
        create_box(f"Tark_Roof_Penthouse_{p_idx}", loc=(px, py, 17.5), size=(7.0, 6.0, 3.2), mat=mat_limestone, col=col_ext)
        create_box(f"Tark_Roof_HVAC_Louver_{p_idx}", loc=(px, py + 3.05, 17.5), size=(5.5, 0.2, 2.2), mat=mat_steel, col=col_ext)

    # 5. Monumental South Main Entrance (Front of Tarkington Facing Wiley/Owen Mall)
    se_cx, se_cy = tc_x, tc_y - 28.2
    create_box("Tark_South_Entrance_Plinth_Stairs", loc=(se_cx, se_cy - 1.5, 0.25), size=(16.0, 4.5, 0.5), mat=mat_limestone, col=col_ext)
    for p_col in [-6.0, -2.0, 2.0, 6.0]:
        create_box(f"Tark_South_Portico_Pier_{p_col}", loc=(se_cx + p_col, se_cy - 2.5, 3.2), size=(0.9, 0.9, 5.4), mat=mat_limestone, col=col_ext)
    create_box("Tark_South_Portico_Entablature", loc=(se_cx, se_cy - 2.5, 6.2), size=(16.4, 1.8, 0.8), mat=mat_limestone, col=col_ext)
    create_box("Tark_Bronze_Signage_Plaque", loc=(se_cx, se_cy - 3.42, 5.2), size=(8.5, 0.12, 0.85), mat=mat_bronze, col=col_ext)
    for d_i, d_x in enumerate([-3.5, 0.0, 3.5]):
        create_box(f"Tark_South_Glass_Door_{d_i}", loc=(se_cx + d_x, se_cy - 0.2, 1.8), size=(2.4, 0.15, 2.8), mat=mat_glass, col=col_ext)
        create_box(f"Tark_South_Door_Bronze_Frame_{d_i}", loc=(se_cx + d_x, se_cy - 0.2, 1.8), size=(2.55, 0.22, 2.95), mat=mat_bronze, col=col_ext)

    # 6. North Entrance Portico (Facing West Stadium Ave)
    ne_cx, ne_cy = tc_x, tc_y + 28.2
    create_box("Tark_North_Portico_Entablature", loc=(ne_cx, ne_cy + 1.2, 5.5), size=(14.0, 1.4, 0.7), mat=mat_limestone, col=col_ext)
    for p_col in [-4.5, 4.5]:
        create_box(f"Tark_North_Portico_Pier_{p_col}", loc=(ne_cx + p_col, ne_cy + 1.2, 2.8), size=(0.85, 0.85, 4.8), mat=mat_limestone, col=col_ext)
    create_box("Tark_North_Entrance_Glass_Doors", loc=(ne_cx, ne_cy + 0.2, 1.7), size=(4.8, 0.15, 2.6), mat=mat_glass, col=col_ext)

    # 7. Mid-Century Rhythmic Fenestration (288 Windows across 4 Floors)
    win_count = 0
    for w_cfg in [
        {"cx": tc_x + 45.0, "y_start": tc_y - 56.0, "y_end": tc_y - 15.0, "step": 3.6, "side": "East_SE"},
        {"cx": tc_x + 45.0, "y_start": tc_y + 15.0, "y_end": tc_y + 56.0, "step": 3.6, "side": "East_NE"},
        {"cx": tc_x - 45.0, "y_start": tc_y - 56.0, "y_end": tc_y - 15.0, "step": 3.6, "side": "West_SW"},
        {"cx": tc_x - 45.0, "y_start": tc_y + 15.0, "y_end": tc_y + 56.0, "step": 3.6, "side": "West_NW"},
    ]:
        curr_y = w_cfg["y_start"]
        while curr_y <= w_cfg["y_end"]:
            for fl in range(4):
                w_z = 2.4 + fl * h_floor
                create_box(f"Tark_Win_{w_cfg['side']}_{win_count}", loc=(w_cfg["cx"], curr_y, w_z), size=(0.18, 1.9, 1.6), mat=mat_glass, col=col_ext)
                create_box(f"Tark_Sill_{w_cfg['side']}_{win_count}", loc=(w_cfg["cx"], curr_y, w_z - 0.88), size=(0.32, 2.1, 0.16), mat=mat_limestone, col=col_ext)
                win_count += 1
            curr_y += w_cfg["step"]

    for w_cfg in [
        {"cy": tc_y + 59.5, "x_start": tc_x - 41.0, "x_end": tc_x - 22.0, "step": 3.6, "side": "North_NW"},
        {"cy": tc_y + 59.5, "x_start": tc_x + 22.0, "x_end": tc_x + 41.0, "step": 3.6, "side": "North_NE"},
        {"cy": tc_y - 59.5, "x_start": tc_x - 41.0, "x_end": tc_x - 22.0, "step": 3.6, "side": "South_SW"},
        {"cy": tc_y - 59.5, "x_start": tc_x + 22.0, "x_end": tc_x + 41.0, "step": 3.6, "side": "South_SE"},
    ]:
        curr_x = w_cfg["x_start"]
        while curr_x <= w_cfg["x_end"]:
            for fl in range(4):
                w_z = 2.4 + fl * h_floor
                create_box(f"Tark_Win_{w_cfg['side']}_{win_count}", loc=(curr_x, w_cfg["cy"], w_z), size=(1.9, 0.18, 1.6), mat=mat_glass, col=col_ext)
                create_box(f"Tark_Sill_{w_cfg['side']}_{win_count}", loc=(curr_x, w_cfg["cy"], w_z - 0.88), size=(2.1, 0.32, 0.16), mat=mat_limestone, col=col_ext)
                win_count += 1
            curr_x += w_cfg["step"]

    print(f"Exterior fenestration complete: {win_count} window units modeled.")

    # =============================================================
    # 8. PHOTOREALISTIC INTERIORS: LOBBY, PETE'S ZA, SHARK TANK, DORM
    # =============================================================
    print("Constructing Tarkington Hall detailed interior spaces...")

    # A. MAIN LOBBY & RECEPTION CHECK-IN (South Commons Floor 1)
    lb_cx, lb_cy = tc_x, tc_y - 18.0
    create_box("Tark_Lobby_Terrazzo_Floor", loc=(lb_cx, lb_cy, 0.10), size=(26.0, 15.0, 0.15), mat=mat_terrazzo, col=col_int)
    create_box("Tark_Lobby_Reception_Desk_Base", loc=(lb_cx - 4.5, lb_cy + 3.5, 0.65), size=(7.0, 1.2, 1.1), mat=mat_oak, col=col_int)
    create_box("Tark_Lobby_Reception_Counter_BlackGranite", loc=(lb_cx - 4.5, lb_cy + 3.5, 1.25), size=(7.4, 1.4, 0.08), mat=mat_black_granite, col=col_int)
    create_box("Tark_Lobby_Mailbox_Wall", loc=(lb_cx + 7.5, lb_cy + 4.0, 1.8), size=(6.5, 0.6, 2.4), mat=mat_bronze, col=col_int)
    create_box("Tark_Halberdier_Trophy_Case", loc=(lb_cx + 7.5, lb_cy - 3.5, 1.6), size=(5.5, 0.6, 2.2), mat=mat_glass, col=col_int)
    create_box("Tark_Halberdier_Trophy_Frame", loc=(lb_cx + 7.5, lb_cy - 3.5, 1.6), size=(5.7, 0.7, 2.3), mat=mat_dark_oak, col=col_int)
    create_box("Tark_Lobby_Digital_Directory", loc=(lb_cx - 8.5, lb_cy - 2.0, 1.9), size=(0.12, 1.6, 2.4), mat=mat_display_glow, col=col_int)
    for c_i, c_y in enumerate([lb_cy - 5.0, lb_cy - 1.0]):
        create_box(f"Tark_Lobby_Lounge_Sofa_{c_i}", loc=(lb_cx - 4.0, c_y, 0.55), size=(2.6, 1.1, 0.75), mat=mat_carpet_blue, col=col_int)

    # B. PETE'S ZA CAMPUS DINING & GRAB-AND-GO (West Commons Floor 1)
    pz_cx, pz_cy = tc_x - 8.5, tc_y + 3.0
    create_box("Tark_PetesZa_Tile_Floor", loc=(pz_cx, pz_cy, 0.10), size=(14.0, 16.0, 0.15), mat=mat_terrazzo, col=col_int)
    create_box("Tark_PetesZa_Overhead_Sign", loc=(pz_cx, pz_cy - 5.0, 3.2), size=(8.0, 0.3, 0.7), mat=mat_pizza_red, col=col_int)
    create_box("Tark_PetesZa_Order_Counter_Base", loc=(pz_cx, pz_cy - 4.0, 0.6), size=(7.5, 0.9, 1.0), mat=mat_brick, col=col_int)
    create_box("Tark_PetesZa_Order_Counter_Top_Steel", loc=(pz_cx, pz_cy - 4.0, 1.12), size=(7.8, 1.05, 0.06), mat=mat_steel, col=col_int)
    for pos_i in [-2.0, 2.0]:
        create_box(f"Tark_PetesZa_POS_Terminal_{pos_i}", loc=(pz_cx + pos_i, pz_cy - 4.0, 1.35), size=(0.4, 0.4, 0.4), mat=mat_display_glow, col=col_int)
    create_box("Tark_PetesZa_Double_Pizza_Oven", loc=(pz_cx, pz_cy + 4.5, 1.6), size=(3.8, 1.6, 2.2), mat=mat_steel, col=col_int)
    create_box("Tark_PetesZa_Prep_Table", loc=(pz_cx, pz_cy + 1.5, 0.55), size=(5.0, 1.1, 0.9), mat=mat_steel, col=col_int)
    for b_i, b_x in enumerate([-4.5, -2.5]):
        create_box(f"Tark_PetesZa_Beverage_Cooler_{b_i}", loc=(pz_cx + b_x, pz_cy + 6.0, 1.4), size=(1.6, 0.9, 2.2), mat=mat_steel, col=col_int)
        create_box(f"Tark_PetesZa_Cooler_Glass_{b_i}", loc=(pz_cx + b_x, pz_cy + 5.5, 1.4), size=(1.4, 0.08, 2.0), mat=mat_glass, col=col_int)
    for t_i, (tx, ty) in enumerate([(pz_cx + 4.0, pz_cy - 1.0), (pz_cx + 4.0, pz_cy + 3.0)]):
        create_cylinder(f"Tark_PetesZa_Table_{t_i}", loc=(tx, ty, 0.95), radius=0.75, depth=0.08, mat=mat_black_granite, col=col_int)
        create_cylinder(f"Tark_PetesZa_Table_Stem_{t_i}", loc=(tx, ty, 0.48), radius=0.08, depth=0.90, mat=mat_steel, col=col_int)

    # C. "SHARK TANK" RECREATIONAL STUDENT LOUNGE (East Commons Floor 1)
    st_cx, st_cy = tc_x + 8.5, tc_y + 3.0
    create_box("Tark_SharkTank_Carpet_Floor", loc=(st_cx, st_cy, 0.10), size=(14.0, 16.0, 0.15), mat=mat_carpet_blue, col=col_int)
    for pool_i, pool_y in enumerate([st_cy - 2.5, st_cy + 4.5]):
        create_box(f"Tark_SharkTank_PoolTable_Body_{pool_i}", loc=(st_cx - 2.2, pool_y, 0.55), size=(3.2, 1.9, 0.65), mat=mat_dark_oak, col=col_int)
        create_box(f"Tark_SharkTank_PoolTable_Felt_{pool_i}", loc=(st_cx - 2.2, pool_y, 0.88), size=(2.85, 1.55, 0.06), mat=mat_felt_green, col=col_int)
        create_box(f"Tark_SharkTank_PoolLight_{pool_i}", loc=(st_cx - 2.2, pool_y, 2.6), size=(2.4, 0.6, 0.35), mat=mat_bronze, col=col_int)
    create_box("Tark_SharkTank_PingPong_Table", loc=(st_cx + 4.2, st_cy - 2.0, 0.76), size=(1.8, 3.0, 0.08), mat=mat_carpet_blue, col=col_int)
    create_box("Tark_SharkTank_PingPong_Net", loc=(st_cx + 4.2, st_cy - 2.0, 0.88), size=(2.0, 0.04, 0.16), mat=mat_white_plastic, col=col_int)
    create_box("Tark_SharkTank_Gaming_TV", loc=(st_cx + 6.85, st_cy + 5.0, 2.1), size=(0.12, 2.2, 1.3), mat=mat_display_glow, col=col_int)
    create_box("Tark_SharkTank_Leather_Sofa_Base", loc=(st_cx + 3.8, st_cy + 5.0, 0.5), size=(2.8, 1.2, 0.65), mat=mat_black_granite, col=col_int)
    create_box("Tark_GrandPrix_Racing_Banner", loc=(st_cx, st_cy + 7.85, 2.6), size=(4.5, 0.1, 1.4), mat=mat_felt_green, col=col_int)

    # Interior Divider Wall between Pete's Za and Shark Tank
    create_box("Tark_Commons_Central_Divider_Wall", loc=(tc_x, tc_y + 3.0, 1.9), size=(0.3, 16.0, 3.8), mat=mat_limestone, col=col_int)

    # D. AUTHENTIC STUDENT DOUBLE DORM ROOM (Room 118, SW Wing Floor 1)
    rm_cx = tc_x - 34.0
    rm_cy = tc_y - 36.0
    create_box("Tark_Dorm_Room118_Floor", loc=(rm_cx, rm_cy, 0.08), size=(5.6, 4.4, 0.12), mat=mat_terrazzo, col=col_int)
    create_box("Tark_Dorm_Room118_Wall_N", loc=(rm_cx, rm_cy + 2.2, 1.9), size=(5.6, 0.2, 3.8), mat=mat_limestone, col=col_int)
    create_box("Tark_Dorm_Room118_Wall_S", loc=(rm_cx, rm_cy - 2.2, 1.9), size=(5.6, 0.2, 3.8), mat=mat_limestone, col=col_int)
    create_box("Tark_Dorm_Room118_Wall_E", loc=(rm_cx + 2.8, rm_cy, 1.9), size=(0.2, 4.4, 3.8), mat=mat_limestone, col=col_int)
    create_box("Tark_Dorm_Room118_Door", loc=(rm_cx + 2.8, rm_cy - 1.2, 1.4), size=(0.1, 1.0, 2.4), mat=mat_oak, col=col_int)
    
    # 2 Twin-XL Beds
    for bed_i, bed_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        create_box(f"Tark_Dorm_Bed_Frame_{bed_i}", loc=(rm_cx - 1.4, bed_y, 0.45), size=(2.2, 1.15, 0.6), mat=mat_oak, col=col_int)
        create_box(f"Tark_Dorm_Bed_Mattress_{bed_i}", loc=(rm_cx - 1.4, bed_y, 0.72), size=(2.1, 1.05, 0.25), mat=mat_carpet_blue, col=col_int)
        create_box(f"Tark_Dorm_Bed_Pillow_{bed_i}", loc=(rm_cx - 2.15, bed_y, 0.88), size=(0.55, 0.75, 0.15), mat=mat_white_plastic, col=col_int)

    # 2 Oak Desks & Chairs
    for dsk_i, dsk_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        create_box(f"Tark_Dorm_Desk_{dsk_i}", loc=(rm_cx + 1.6, dsk_y, 0.65), size=(1.35, 0.85, 0.76), mat=mat_oak, col=col_int)
        create_box(f"Tark_Dorm_Desk_Hutch_{dsk_i}", loc=(rm_cx + 2.1, dsk_y, 1.4), size=(0.35, 0.85, 0.85), mat=mat_oak, col=col_int)
        create_box(f"Tark_Dorm_Desk_Chair_{dsk_i}", loc=(rm_cx + 1.0, dsk_y, 0.55), size=(0.6, 0.6, 0.85), mat=mat_dark_oak, col=col_int)

    # Wardrobes
    create_box("Tark_Dorm_Wardrobes", loc=(rm_cx - 2.2, rm_cy, 1.4), size=(0.65, 1.8, 2.2), mat=mat_oak, col=col_int)

    # Signature Tarkington Window Box Fans
    create_box("Tark_Dorm_Window_Box_Fan_1", loc=(rm_cx - 2.7, rm_cy - 0.45, 1.8), size=(0.22, 0.55, 0.55), mat=mat_white_plastic, col=col_int)
    create_box("Tark_Dorm_Window_Box_Fan_2", loc=(rm_cx - 2.7, rm_cy + 0.45, 1.8), size=(0.22, 0.55, 0.55), mat=mat_white_plastic, col=col_int)

    print("Tarkington Hall interior spaces completed.")

    # =============================================================
    # 9. COURTYARDS & SITE INTEGRATION (WEST & EAST COURTYARDS)
    # =============================================================
    print("Constructing Tarkington Hall courtyards and pedestrian approaches...")

    # A. WEST INNER COURTYARD
    wcy_cx, wcy_cy = tc_x - 24.0, tc_y
    create_box("Tark_West_Courtyard_Brick_Plaza", loc=(wcy_cx, wcy_cy, 0.10), size=(13.0, 24.0, 0.14), mat=mat_brick, col=col_site)
    create_box("Tark_West_Courtyard_Lawn_Panel", loc=(wcy_cx, wcy_cy, 0.12), size=(8.5, 16.0, 0.12), mat=mat_felt_green, col=col_site)
    for sw_i, sw_y in enumerate([wcy_cy - 6.5, wcy_cy + 6.5]):
        create_box(f"Tark_West_Courtyard_Seatwall_{sw_i}", loc=(wcy_cx, sw_y, 0.35), size=(7.5, 0.65, 0.45), mat=mat_limestone, col=col_site)
        create_box(f"Tark_West_Courtyard_Teak_Top_{sw_i}", loc=(wcy_cx, sw_y, 0.60), size=(7.7, 0.75, 0.08), mat=mat_teak, col=col_site)
    create_box("Tark_West_Picnic_Table_Top", loc=(wcy_cx, wcy_cy, 0.78), size=(2.4, 1.2, 0.08), mat=mat_teak, col=col_site)
    create_box("Tark_West_Picnic_Bench_1", loc=(wcy_cx, wcy_cy - 0.9, 0.46), size=(2.4, 0.4, 0.06), mat=mat_teak, col=col_site)
    create_box("Tark_West_Picnic_Bench_2", loc=(wcy_cx, wcy_cy + 0.9, 0.46), size=(2.4, 0.4, 0.06), mat=mat_teak, col=col_site)

    # B. EAST INNER COURTYARD
    ecy_cx, ecy_cy = tc_x + 24.0, tc_y
    create_box("Tark_East_Courtyard_Brick_Plaza", loc=(ecy_cx, ecy_cy, 0.10), size=(13.0, 24.0, 0.14), mat=mat_brick, col=col_site)
    create_cylinder("Tark_East_Courtyard_Circular_Terrace", loc=(ecy_cx, ecy_cy, 0.14), radius=4.5, depth=0.12, mat=mat_limestone, col=col_site, verts=36)
    create_cylinder("Tark_East_Courtyard_Inlay_Core", loc=(ecy_cx, ecy_cy, 0.16), radius=2.6, depth=0.10, mat=mat_black_granite, col=col_site, verts=36)
    for ang_i, ang_deg in enumerate([45, 225]):
        rad = math.radians(ang_deg)
        create_box(f"Tark_East_Curved_Bench_{ang_i}", loc=(ecy_cx + 5.2 * math.cos(rad), ecy_cy + 5.2 * math.sin(rad), 0.42), size=(3.2, 0.65, 0.48), mat=mat_limestone, col=col_site)

    # C. SURROUNDING PEDESTRIAN CONCOURSE & MARTIN JISCHKE DR APPROACH
    create_box("Tark_Jischke_Pedestrian_Concourse", loc=(tc_x + 50.0, tc_y, 0.08), size=(10.0, 130.0, 0.12), mat=mat_limestone, col=col_site)
    create_box("Tark_South_Wiley_Connector_Walkway", loc=(tc_x, tc_y - 68.0, 0.08), size=(85.0, 14.0, 0.12), mat=mat_limestone, col=col_site)

    for lp_i, (lpx, lpy) in enumerate([
        (tc_x + 48.0, tc_y + 62.0),
        (tc_x + 48.0, tc_y - 62.0),
        (tc_x - 48.0, tc_y + 62.0),
        (tc_x - 48.0, tc_y - 62.0)
    ]):
        create_cylinder(f"Tark_Lantern_Pole_{lp_i}", loc=(lpx, lpy, 2.2), radius=0.08, depth=4.2, mat=mat_bronze, col=col_site)
        create_box(f"Tark_Lantern_Head_{lp_i}", loc=(lpx, lpy, 4.4), size=(0.45, 0.45, 0.65), mat=mat_glass, col=col_site)

    # =============================================================
    # 10. DEDICATED INSPECTION CAMERAS SETUP
    # =============================================================
    # 1. East Facade from North Martin Jischke Drive
    c22 = bpy.data.objects.get("Cam_22_Tarkington_Hall_Jischke_StreetView")
    if not c22:
        cdata = bpy.data.cameras.new("Cam_22_Tarkington_Hall_Jischke_StreetView")
        cdata.lens = 24.0
        cdata.clip_end = 6000.0
        c22 = bpy.data.objects.new("Cam_22_Tarkington_Hall_Jischke_StreetView", cdata)
        col_ext.objects.link(c22)
    c22.location = (tc_x + 74.0, tc_y, 8.5)
    look_at(c22, (tc_x + 31.5, tc_y, 6.0))

    # 2. South Main Entrance Facing Wiley / Owen Mall
    c23 = bpy.data.objects.get("Cam_23_Tarkington_Hall_South_Main_Entrance")
    if not c23:
        cdata = bpy.data.cameras.new("Cam_23_Tarkington_Hall_South_Main_Entrance")
        cdata.lens = 24.0
        cdata.clip_end = 6000.0
        c23 = bpy.data.objects.new("Cam_23_Tarkington_Hall_South_Main_Entrance", cdata)
        col_ext.objects.link(c23)
    c23.location = (tc_x, tc_y - 52.0, 5.5)
    look_at(c23, (tc_x, tc_y - 28.0, 4.0))

    # 3. Pete's Za Campus Dining Interior
    c24 = bpy.data.objects.get("Cam_24_Tarkington_PetesZa_Dining_Interior")
    if not c24:
        cdata = bpy.data.cameras.new("Cam_24_Tarkington_PetesZa_Dining_Interior")
        cdata.lens = 20.0
        cdata.clip_end = 6000.0
        c24 = bpy.data.objects.new("Cam_24_Tarkington_PetesZa_Dining_Interior", cdata)
        col_int.objects.link(c24)
    c24.location = (pz_cx + 4.5, pz_cy - 4.5, 1.8)
    look_at(c24, (pz_cx - 0.5, pz_cy + 2.5, 1.4))

    # 4. "Shark Tank" Recreational Lounge Interior
    c25 = bpy.data.objects.get("Cam_25_Tarkington_SharkTank_Lounge_Interior")
    if not c25:
        cdata = bpy.data.cameras.new("Cam_25_Tarkington_SharkTank_Lounge_Interior")
        cdata.lens = 20.0
        cdata.clip_end = 6000.0
        c25 = bpy.data.objects.new("Cam_25_Tarkington_SharkTank_Lounge_Interior", cdata)
        col_int.objects.link(c25)
    c25.location = (st_cx - 4.5, st_cy - 4.5, 1.8)
    look_at(c25, (st_cx + 1.5, st_cy + 2.5, 1.4))

    # 5. Authentic Double Student Dorm Room 118 Interior
    c26 = bpy.data.objects.get("Cam_26_Tarkington_Student_Dorm_Interior")
    if not c26:
        cdata = bpy.data.cameras.new("Cam_26_Tarkington_Student_Dorm_Interior")
        cdata.lens = 18.0
        cdata.clip_end = 6000.0
        c26 = bpy.data.objects.new("Cam_26_Tarkington_Student_Dorm_Interior", cdata)
        col_int.objects.link(c26)
    c26.location = (rm_cx + 2.0, rm_cy, 1.8)
    look_at(c26, (rm_cx - 1.8, rm_cy, 1.2))

    bpy.context.scene.camera = c22
    print("Dedicated Tarkington Hall inspection cameras calibrated.")

    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master scene successfully saved: {save_path}")
    print("Tarkington Hall construction complete!")

if __name__ == "__main__":
    build_tarkington_hall()
