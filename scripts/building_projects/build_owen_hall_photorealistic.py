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

def build_owen_hall():
    print("===================================================================")
    print("BUILDING RICHARD OWEN RESIDENCE HALL (OWEN) DIGITAL TWIN")
    print("===================================================================")

    # 1. Collections Setup
    col_ext = clean_or_create_col("20_Owen_Hall_Exterior")
    col_int = clean_or_create_col("21_Owen_Hall_Interiors")
    col_site = clean_or_create_col("22_Owen_Hall_Courtyards_and_Site")

    # 2. Materials Setup
    mat_brick = bpy.data.materials.get("Beering_Purdue_Red_Brick") or get_or_make_mat("Owen_Purdue_Red_Brick", (0.54, 0.22, 0.16, 1.0), roughness=0.82)
    mat_limestone = bpy.data.materials.get("Indiana_Bedford_Limestone") or get_or_make_mat("Owen_Bedford_Limestone", (0.85, 0.82, 0.77, 1.0), roughness=0.68)
    mat_glass = bpy.data.materials.get("Beering_Solar_Ribbon_Glass") or get_or_make_mat("Owen_Window_Glass", (0.1, 0.15, 0.22, 1.0), roughness=0.08, transmission=0.92)
    mat_terrazzo = bpy.data.materials.get("Beering_Lobby_Terrazzo") or get_or_make_mat("Owen_Lobby_Terrazzo", (0.86, 0.84, 0.80, 1.0), roughness=0.18)
    mat_oak = bpy.data.materials.get("Beering_Honey_Oak_Woodwork") or get_or_make_mat("Owen_Oak_Wood", (0.48, 0.31, 0.16, 1.0), roughness=0.45)
    mat_dark_oak = bpy.data.materials.get("Beering_Executive_Dark_Oak") or get_or_make_mat("Owen_Dark_Oak", (0.28, 0.17, 0.09, 1.0), roughness=0.40)
    mat_steel = bpy.data.materials.get("Tark_Stainless_Steel") or get_or_make_mat("Owen_Stainless_Steel", (0.85, 0.85, 0.88, 1.0), roughness=0.20, metallic=0.95)
    mat_bronze = bpy.data.materials.get("Tark_Architectural_Bronze") or get_or_make_mat("Owen_Bronze", (0.35, 0.26, 0.15, 1.0), roughness=0.35, metallic=0.80)
    mat_black_granite = bpy.data.materials.get("Purdue_Polished_Black_Granite") or get_or_make_mat("Owen_Black_Countertop", (0.05, 0.05, 0.06, 1.0), roughness=0.15)
    mat_teak = bpy.data.materials.get("Campus_Teak_Wood_Bench") or get_or_make_mat("Owen_Teak_Bench", (0.42, 0.28, 0.16, 1.0), roughness=0.55)
    mat_felt_green = bpy.data.materials.get("Tark_Billiard_Green_Felt") or get_or_make_mat("Owen_Billiard_Green_Felt", (0.04, 0.38, 0.16, 1.0), roughness=0.85)
    mat_carpet_burgundy = get_or_make_mat("Owen_Burgundy_Carpet", (0.28, 0.08, 0.12, 1.0), roughness=0.90)
    mat_carpet_navy = bpy.data.materials.get("Tarkington_Navy_Carpet") or get_or_make_mat("Owen_Navy_Carpet", (0.08, 0.14, 0.28, 1.0), roughness=0.90)
    mat_roof_gravel = bpy.data.materials.get("Beering_Roof_Membrane") or get_or_make_mat("Owen_Roof_Gravel", (0.28, 0.27, 0.26, 1.0), roughness=0.95)
    mat_white = bpy.data.materials.get("Tark_Appliance_White") or get_or_make_mat("Owen_White", (0.92, 0.92, 0.92, 1.0), roughness=0.30)
    mat_display_glow = bpy.data.materials.get("Tark_Display_Emission") or get_or_make_mat("Owen_Display_Glow", (0.1, 0.5, 0.95, 1.0), roughness=0.2, emission=(0.1, 0.6, 1.0, 1.0), emission_strength=4.5)
    mat_piano_black = get_or_make_mat("Owen_Piano_Polished_Ebony", (0.02, 0.02, 0.02, 1.0), roughness=0.08, metallic=0.05)

    # Building Georeferenced Coordinates Center
    # OSM relation 12647862 center: X = -594.02m, Y = 539.10m
    oc_x, oc_y = -594.0, 539.1
    print(f"Siting Owen Hall at georeferenced center ({oc_x}, {oc_y})...")

    # Vertical Dimensions: 4 Stories (Floor height 3.8m, Total Roof Height 15.2m, Parapet 16.0m)
    h_floor = 3.8
    total_h = 15.2

    # -------------------------------------------------------------
    # 3. EXTERIOR ARCHITECTURE: 4 RESIDENTIAL WINGS & CENTRAL COMMONS
    # -------------------------------------------------------------
    # Total Footprint: X in [oc_x - 44.2, oc_x + 44.2] (width 88.4m)
    #                  Y in [oc_y - 54.0, oc_y + 54.0] (length 108.0m)
    # West Spine: X in [oc_x - 44.2, oc_x - 18.5] (width 25.7m, cx = oc_x - 31.35)
    #   NW Wing: Y in [oc_y + 13.0, oc_y + 54.0] (depth 41.0m, cy = oc_y + 33.5)
    #   SW Wing: Y in [oc_y - 54.0, oc_y - 13.0] (depth 41.0m, cy = oc_y - 33.5)
    # East Spine: X in [oc_x + 18.5, oc_x + 44.2] (width 25.7m, cx = oc_x + 31.35)
    #   NE Wing: Y in [oc_y + 13.0, oc_y + 54.0] (depth 41.0m, cy = oc_y + 33.5)
    #   SE Wing: Y in [oc_y - 54.0, oc_y - 13.0] (depth 41.0m, cy = oc_y - 33.5)
    # Central Commons Hub:
    #   X in [oc_x - 18.5, oc_x + 18.5] (width 37.0m)
    #   Y in [oc_y - 14.0, oc_y + 14.0] (depth 28.0m)
    # North Entrance Pavilion (facing West Stadium Ave):
    #   X in [oc_x - 11.0, oc_x + 11.0] (width 22.0m), Y in [oc_y + 14.0, oc_y + 26.0]
    # South Entrance Pavilion (facing Tarkington Hall):
    #   X in [oc_x - 11.0, oc_x + 11.0] (width 22.0m), Y in [oc_y - 26.0, oc_y - 14.0]

    wing_configs = [
        {"name": "NW_Wing", "cx": oc_x - 31.35, "cy": oc_y + 33.5, "sx": 25.7, "sy": 41.0, "hollow_gf": False},
        {"name": "SW_Wing", "cx": oc_x - 31.35, "cy": oc_y - 33.5, "sx": 25.7, "sy": 41.0, "hollow_gf": True},
        {"name": "NE_Wing", "cx": oc_x + 31.35, "cy": oc_y + 33.5, "sx": 25.7, "sy": 41.0, "hollow_gf": False},
        {"name": "SE_Wing", "cx": oc_x + 31.35, "cy": oc_y - 33.5, "sx": 25.7, "sy": 41.0, "hollow_gf": False},
        {"name": "Commons_Hub", "cx": oc_x, "cy": oc_y, "sx": 37.0, "sy": 28.0, "hollow_gf": True},
        {"name": "North_Entrance_Pavilion", "cx": oc_x, "cy": oc_y + 20.0, "sx": 22.0, "sy": 12.0, "hollow_gf": True},
        {"name": "South_Entrance_Pavilion", "cx": oc_x, "cy": oc_y - 20.0, "sx": 22.0, "sy": 12.0, "hollow_gf": False},
    ]

    for w in wing_configs:
        w_name = w["name"]
        cx, cy = w["cx"], w["cy"]
        sx, sy = w["sx"], w["sy"]
        hollow_gf = w["hollow_gf"]

        # Foundation / Limestone Water Table Base (0.0m to 1.5m)
        if not hollow_gf:
            create_box(
                f"Owen_{w_name}_Limestone_Base",
                loc=(cx, cy, 0.75),
                size=(sx + 0.3, sy + 0.3, 1.5),
                mat=mat_limestone,
                col=col_ext
            )
            # Main Red Brick Shaft (1.5m to 15.2m)
            create_box(
                f"Owen_{w_name}_Brick_Shaft",
                loc=(cx, cy, 1.5 + (total_h - 1.5) * 0.5),
                size=(sx, sy, total_h - 1.5),
                mat=mat_brick,
                col=col_ext
            )
        else:
            # Hollow Ground Floor with Perimeter Walls (z = 0.0 to 3.8m)
            create_box(f"Owen_{w_name}_GF_Wall_N", loc=(cx, cy + sy*0.5 - 0.2, 1.9), size=(sx, 0.4, 3.8), mat=mat_brick, col=col_ext)
            create_box(f"Owen_{w_name}_GF_Wall_S", loc=(cx, cy - sy*0.5 + 0.2, 1.9), size=(sx, 0.4, 3.8), mat=mat_brick, col=col_ext)
            create_box(f"Owen_{w_name}_GF_Wall_E", loc=(cx + sx*0.5 - 0.2, cy, 1.9), size=(0.4, sy, 3.8), mat=mat_brick, col=col_ext)
            create_box(f"Owen_{w_name}_GF_Wall_W", loc=(cx - sx*0.5 + 0.2, cy, 1.9), size=(0.4, sy, 3.8), mat=mat_brick, col=col_ext)
            
            # Upper Shaft (Floors 2-4: z = 3.8m to 15.2m)
            create_box(
                f"Owen_{w_name}_Upper_Brick_Shaft",
                loc=(cx, cy, 3.8 + (total_h - 3.8) * 0.5),
                size=(sx, sy, total_h - 3.8),
                mat=mat_brick,
                col=col_ext
            )
            # Structural Floor Slab at z = 3.8m
            create_box(
                f"Owen_{w_name}_Ceiling_Slab",
                loc=(cx, cy, 3.8),
                size=(sx + 0.1, sy + 0.1, 0.25),
                mat=mat_limestone,
                col=col_ext
            )

        # Limestone Horizontal Beltcourses across all 4 levels (z = 3.8, 7.6, 11.4, 15.2m)
        for fl_idx, fl_z in enumerate([3.8, 7.6, 11.4, 15.2]):
            create_box(
                f"Owen_{w_name}_Limestone_Belt_{fl_idx+1}",
                loc=(cx, cy, fl_z),
                size=(sx + 0.18, sy + 0.18, 0.22),
                mat=mat_limestone,
                col=col_ext
            )

        # Roof Parapet & Perimeter Coping Stone (z = 15.2m to 16.0m)
        create_box(
            f"Owen_{w_name}_Roof_Parapet_Coping",
            loc=(cx, cy, 15.7),
            size=(sx + 0.24, sy + 0.24, 0.40),
            mat=mat_limestone,
            col=col_ext
        )

        # Inset Roof Gravel Slab
        create_box(
            f"Owen_{w_name}_Roof_Membrane",
            loc=(cx, cy, 15.3),
            size=(sx - 0.8, sy - 0.8, 0.15),
            mat=mat_roof_gravel,
            col=col_ext
        )

    # 4. Roof Mechanical Housings & Chimney Stacks
    for p_idx, (px, py) in enumerate([
        (oc_x - 31.35, oc_y + 33.5),
        (oc_x + 31.35, oc_y + 33.5),
        (oc_x - 31.35, oc_y - 33.5),
        (oc_x + 31.35, oc_y - 33.5),
        (oc_x, oc_y)
    ]):
        create_box(f"Owen_Roof_Penthouse_{p_idx}", loc=(px, py, 17.5), size=(7.0, 5.5, 3.2), mat=mat_limestone, col=col_ext)
        create_box(f"Owen_Roof_HVAC_Louver_{p_idx}", loc=(px, py + 2.8, 17.5), size=(5.5, 0.2, 2.2), mat=mat_steel, col=col_ext)

    # 5. Monumental North Main Entrance Portico (Facing West Stadium Ave)
    ne_cx, ne_cy = oc_x, oc_y + 26.2
    create_box("Owen_North_Entrance_Plinth_Stairs", loc=(ne_cx, ne_cy + 1.5, 0.25), size=(16.0, 4.5, 0.5), mat=mat_limestone, col=col_ext)
    for p_col in [-6.0, -2.0, 2.0, 6.0]:
        create_box(f"Owen_North_Portico_Pier_{p_col}", loc=(ne_cx + p_col, ne_cy + 2.5, 3.2), size=(0.9, 0.9, 5.4), mat=mat_limestone, col=col_ext)
    create_box("Owen_North_Portico_Entablature", loc=(ne_cx, ne_cy + 2.5, 6.2), size=(16.4, 1.8, 0.8), mat=mat_limestone, col=col_ext)
    create_box("Owen_Bronze_Signage_Plaque", loc=(ne_cx, ne_cy + 3.42, 5.2), size=(8.5, 0.12, 0.85), mat=mat_bronze, col=col_ext)
    for d_i, d_x in enumerate([-3.5, 0.0, 3.5]):
        create_box(f"Owen_North_Glass_Door_{d_i}", loc=(ne_cx + d_x, ne_cy + 0.2, 1.8), size=(2.4, 0.15, 2.8), mat=mat_glass, col=col_ext)
        create_box(f"Owen_North_Door_Bronze_Frame_{d_i}", loc=(ne_cx + d_x, ne_cy + 0.2, 1.8), size=(2.55, 0.22, 2.95), mat=mat_bronze, col=col_ext)

    # Multi-story vertical glazed curtain wall bays above North portico
    for bay_i, bay_x in enumerate([ne_cx - 3.0, ne_cx, ne_cx + 3.0]):
        bay_w = 2.4 if bay_x == ne_cx else 2.0
        create_box(f"Owen_North_Portal_CurtainBay_Glass_{bay_i}", loc=(bay_x, ne_cy + 0.1, 9.5), size=(bay_w, 0.22, 9.8), mat=mat_glass, col=col_ext)
        create_box(f"Owen_North_Portal_CurtainBay_Frame_{bay_i}", loc=(bay_x, ne_cy + 0.12, 9.5), size=(bay_w + 0.25, 0.32, 10.1), mat=mat_limestone, col=col_ext)

    # 6. South Entrance Portico (Facing Tarkington Hall)
    se_cx, se_cy = oc_x, oc_y - 26.2
    create_box("Owen_South_Portico_Entablature", loc=(se_cx, se_cy - 1.2, 5.5), size=(14.0, 1.4, 0.7), mat=mat_limestone, col=col_ext)
    for p_col in [-4.5, 4.5]:
        create_box(f"Owen_South_Portico_Pier_{p_col}", loc=(se_cx + p_col, se_cy - 1.2, 2.8), size=(0.85, 0.85, 4.8), mat=mat_limestone, col=col_ext)
    create_box("Owen_South_Entrance_Glass_Doors", loc=(se_cx, se_cy - 0.2, 1.7), size=(4.8, 0.15, 2.6), mat=mat_glass, col=col_ext)

    # 7. Mid-Century Rhythmic Fenestration (288 Windows across 4 Floors)
    win_count = 0
    # East Facades (Facing Martin Jischke Dr) & West Facades
    for w_cfg in [
        {"cx": oc_x + 44.2, "y_start": oc_y - 50.0, "y_end": oc_y - 16.0, "step": 3.6, "side": "East_SE"},
        {"cx": oc_x + 44.2, "y_start": oc_y + 16.0, "y_end": oc_y + 50.0, "step": 3.6, "side": "East_NE"},
        {"cx": oc_x - 44.2, "y_start": oc_y - 50.0, "y_end": oc_y - 16.0, "step": 3.6, "side": "West_SW"},
        {"cx": oc_x - 44.2, "y_start": oc_y + 16.0, "y_end": oc_y + 50.0, "step": 3.6, "side": "West_NW"},
    ]:
        curr_y = w_cfg["y_start"]
        while curr_y <= w_cfg["y_end"]:
            for fl in range(4):
                w_z = 2.4 + fl * h_floor
                create_box(f"Owen_Win_{w_cfg['side']}_{win_count}", loc=(w_cfg["cx"], curr_y, w_z), size=(0.18, 1.9, 1.6), mat=mat_glass, col=col_ext)
                create_box(f"Owen_Sill_{w_cfg['side']}_{win_count}", loc=(w_cfg["cx"], curr_y, w_z - 0.88), size=(0.32, 2.1, 0.16), mat=mat_limestone, col=col_ext)
                win_count += 1
            curr_y += w_cfg["step"]

    # North & South Wing End Facades
    for w_cfg in [
        {"cy": oc_y + 54.0, "x_start": oc_x - 40.0, "x_end": oc_x - 22.0, "step": 3.6, "side": "North_NW"},
        {"cy": oc_y + 54.0, "x_start": oc_x + 22.0, "x_end": oc_x + 40.0, "step": 3.6, "side": "North_NE"},
        {"cy": oc_y - 54.0, "x_start": oc_x - 40.0, "x_end": oc_x - 22.0, "step": 3.6, "side": "South_SW"},
        {"cy": oc_y - 54.0, "x_start": oc_x + 22.0, "x_end": oc_x + 40.0, "step": 3.6, "side": "South_SE"},
    ]:
        curr_x = w_cfg["x_start"]
        while curr_x <= w_cfg["x_end"]:
            for fl in range(4):
                w_z = 2.4 + fl * h_floor
                create_box(f"Owen_Win_{w_cfg['side']}_{win_count}", loc=(curr_x, w_cfg["cy"], w_z), size=(1.9, 0.18, 1.6), mat=mat_glass, col=col_ext)
                create_box(f"Owen_Sill_{w_cfg['side']}_{win_count}", loc=(curr_x, w_cfg["cy"], w_z - 0.88), size=(2.1, 0.32, 0.16), mat=mat_limestone, col=col_ext)
                win_count += 1
            curr_x += w_cfg["step"]

    # East Courtyard Connector Wall Fenestration (Floors 2-4)
    for ey_i, ey_pos in enumerate([-8.0, -3.0, 3.0, 8.0]):
        for fl_i, fl_z in enumerate([5.8, 9.6, 13.4]):
            create_box(f"Owen_East_Connector_Win_{ey_i}_{fl_i}", loc=(oc_x + 18.55, oc_y + ey_pos, fl_z), size=(0.22, 2.4, 1.8), mat=mat_glass, col=col_ext)
            create_box(f"Owen_East_Connector_Sill_{ey_i}_{fl_i}", loc=(oc_x + 18.65, oc_y + ey_pos, fl_z - 0.98), size=(0.35, 2.6, 0.16), mat=mat_limestone, col=col_ext)

    print(f"Exterior fenestration complete: {win_count} window units modeled.")

    # =============================================================
    # 8. PHOTOREALISTIC INTERIORS: LOBBY, PIANO LOUNGE, STUDY, DORM
    # =============================================================
    print("Constructing Richard Owen Hall detailed interior spaces...")

    # A. MAIN LOBBY & HUSSAR FRONT DESK (North Commons Floor 1)
    lb_cx, lb_cy = oc_x, oc_y + 16.0
    create_box("Owen_Lobby_Terrazzo_Floor", loc=(lb_cx, lb_cy, 0.10), size=(24.0, 14.0, 0.15), mat=mat_terrazzo, col=col_int)
    create_box("Owen_Lobby_Reception_Desk_Base", loc=(lb_cx - 4.5, lb_cy - 2.5, 0.65), size=(6.5, 1.2, 1.1), mat=mat_oak, col=col_int)
    create_box("Owen_Lobby_Reception_Counter_BlackGranite", loc=(lb_cx - 4.5, lb_cy - 2.5, 1.25), size=(6.9, 1.4, 0.08), mat=mat_black_granite, col=col_int)
    create_box("Owen_Lobby_Mailbox_Wall", loc=(lb_cx + 7.0, lb_cy - 2.5, 1.8), size=(6.0, 0.6, 2.4), mat=mat_bronze, col=col_int)
    create_box("Owen_Hussar_Trophy_Case", loc=(lb_cx + 7.0, lb_cy + 3.5, 1.6), size=(5.0, 0.6, 2.2), mat=mat_glass, col=col_int)
    create_box("Owen_Hussar_Trophy_Frame", loc=(lb_cx + 7.0, lb_cy + 3.5, 1.6), size=(5.2, 0.7, 2.3), mat=mat_dark_oak, col=col_int)
    create_box("Owen_Lobby_Digital_Directory", loc=(lb_cx - 8.0, lb_cy + 2.0, 1.9), size=(0.12, 1.6, 2.4), mat=mat_display_glow, col=col_int)
    for c_i, c_y in enumerate([lb_cy + 1.0, lb_cy + 4.5]):
        create_box(f"Owen_Lobby_Lounge_Sofa_{c_i}", loc=(lb_cx - 4.0, c_y, 0.55), size=(2.6, 1.1, 0.75), mat=mat_carpet_burgundy, col=col_int)

    # Lobby Ceiling Downlights
    for li, (lx, ly) in enumerate([(lb_cx - 4.0, lb_cy), (lb_cx + 4.0, lb_cy), (lb_cx, lb_cy - 2.0)]):
        ldata = bpy.data.lights.new(f"Owen_Light_Lobby_{li}", "POINT")
        ldata.energy = 260.0
        ldata.color = (1.0, 0.96, 0.90)
        lobj = bpy.data.objects.new(f"Owen_Light_Lobby_{li}", ldata)
        lobj.location = (lx, ly, 3.4)
        col_int.objects.link(lobj)

    # B. OWEN MAIN RECREATIONAL LOUNGE & MUSICIAN'S CORNER (West Commons Floor 1)
    rl_cx, rl_cy = oc_x - 9.0, oc_y - 2.0
    create_box("Owen_RecLounge_Carpet_Floor", loc=(rl_cx, rl_cy, 0.10), size=(15.0, 18.0, 0.15), mat=mat_carpet_burgundy, col=col_int)
    
    # Signature Acoustic Upright Piano in Musician's Corner!
    create_box("Owen_Piano_Body", loc=(rl_cx - 5.5, rl_cy + 6.0, 0.75), size=(1.55, 0.65, 1.25), mat=mat_piano_black, col=col_int)
    create_box("Owen_Piano_Keyboard_Bed", loc=(rl_cx - 5.5, rl_cy + 5.65, 0.68), size=(1.45, 0.32, 0.12), mat=mat_white, col=col_int)
    create_box("Owen_Piano_Music_Stand", loc=(rl_cx - 5.5, rl_cy + 5.75, 1.05), size=(0.85, 0.08, 0.28), mat=mat_piano_black, col=col_int)
    create_box("Owen_Piano_Bench", loc=(rl_cx - 5.5, rl_cy + 5.0, 0.45), size=(0.95, 0.40, 0.48), mat=mat_piano_black, col=col_int)

    # Piano Warm Accent Spotlight
    p_sdata = bpy.data.lights.new("Owen_Light_PianoSpot", "SPOT")
    p_sdata.energy = 380.0
    p_sdata.color = (1.0, 0.95, 0.85)
    p_sdata.spot_size = math.radians(55.0)
    p_sobj = bpy.data.objects.new("Owen_Light_PianoSpot", p_sdata)
    p_sobj.location = (rl_cx - 5.5, rl_cy + 5.5, 3.2)
    p_sobj.rotation_euler = (0.0, 0.0, 0.0)
    col_int.objects.link(p_sobj)

    # Regulation 9-ft Billiard Table under Focused Spotlight
    create_box("Owen_PoolTable_Body", loc=(rl_cx + 1.5, rl_cy + 2.5, 0.55), size=(3.2, 1.9, 0.65), mat=mat_dark_oak, col=col_int)
    create_box("Owen_PoolTable_Felt", loc=(rl_cx + 1.5, rl_cy + 2.5, 0.88), size=(2.85, 1.55, 0.06), mat=mat_felt_green, col=col_int)
    create_box("Owen_PoolTable_LightFixture", loc=(rl_cx + 1.5, rl_cy + 2.5, 2.6), size=(2.4, 0.6, 0.35), mat=mat_bronze, col=col_int)
    
    b_sdata = bpy.data.lights.new("Owen_Light_PoolSpot", "SPOT")
    b_sdata.energy = 450.0
    b_sdata.color = (1.0, 0.97, 0.92)
    b_sdata.spot_size = math.radians(65.0)
    b_sobj = bpy.data.objects.new("Owen_Light_PoolSpot", b_sdata)
    b_sobj.location = (rl_cx + 1.5, rl_cy + 2.5, 2.5)
    col_int.objects.link(b_sobj)

    # Regulation Ping-Pong Table
    create_box("Owen_PingPong_Table", loc=(rl_cx - 2.5, rl_cy - 4.5, 0.76), size=(1.8, 3.0, 0.08), mat=mat_carpet_navy, col=col_int)
    create_box("Owen_PingPong_Net", loc=(rl_cx - 2.5, rl_cy - 4.5, 0.88), size=(2.0, 0.04, 0.16), mat=mat_white, col=col_int)

    # Leather Sectional Sofa & 75" TV
    create_box("Owen_RecLounge_TV", loc=(rl_cx + 6.8, rl_cy - 4.5, 2.0), size=(0.12, 2.2, 1.3), mat=mat_display_glow, col=col_int)
    create_box("Owen_RecLounge_Sofa_Base", loc=(rl_cx + 3.8, rl_cy - 4.5, 0.50), size=(2.8, 1.2, 0.65), mat=mat_black_granite, col=col_int)

    # Ambient Room Light
    r_ldata = bpy.data.lights.new("Owen_Light_RecLounge_Ambient", "POINT")
    r_ldata.energy = 240.0
    r_ldata.color = (1.0, 0.94, 0.86)
    r_lobj = bpy.data.objects.new("Owen_Light_RecLounge_Ambient", r_ldata)
    r_lobj.location = (rl_cx, rl_cy, 3.3)
    col_int.objects.link(r_lobj)

    # C. OWEN STUDY CENTER & IT COMPUTER LAB (East Commons Floor 1)
    sc_cx, sc_cy = oc_x + 9.0, oc_y - 2.0
    create_box("Owen_Study_Carpet_Floor", loc=(sc_cx, sc_cy, 0.10), size=(15.0, 18.0, 0.15), mat=mat_carpet_navy, col=col_int)
    
    # 2 Large Collaborative Oak Study Tables
    for st_i, st_y in enumerate([sc_cy - 3.5, sc_cy + 3.5]):
        create_box(f"Owen_Study_Table_{st_i}", loc=(sc_cx - 2.0, st_y, 0.76), size=(3.6, 1.4, 0.08), mat=mat_oak, col=col_int)
        for ch_i, ch_x in enumerate([sc_cx - 3.2, sc_cx - 2.0, sc_cx - 0.8]):
            create_box(f"Owen_Study_Chair_N_{st_i}_{ch_i}", loc=(ch_x, st_y + 0.95, 0.55), size=(0.55, 0.55, 0.85), mat=mat_dark_oak, col=col_int)
            create_box(f"Owen_Study_Chair_S_{st_i}_{ch_i}", loc=(ch_x, st_y - 0.95, 0.55), size=(0.55, 0.55, 0.85), mat=mat_dark_oak, col=col_int)

    # Computer Workstations with Dual Monitors
    for pc_i, pc_y in enumerate([sc_cy - 4.0, sc_cy - 1.5, sc_cy + 1.5, sc_cy + 4.0]):
        create_box(f"Owen_PC_Desk_{pc_i}", loc=(sc_cx + 5.2, pc_y, 0.74), size=(1.2, 1.6, 0.08), mat=mat_oak, col=col_int)
        create_box(f"Owen_PC_Screen_{pc_i}", loc=(sc_cx + 5.6, pc_y, 1.15), size=(0.1, 0.8, 0.5), mat=mat_display_glow, col=col_int)
        create_box(f"Owen_PC_Chair_{pc_i}", loc=(sc_cx + 4.2, pc_y, 0.55), size=(0.55, 0.55, 0.85), mat=mat_dark_oak, col=col_int)

    # University Network Print Station
    create_box("Owen_Network_Printer", loc=(sc_cx + 5.2, sc_cy + 6.8, 0.85), size=(1.1, 0.9, 1.1), mat=mat_white, col=col_int)

    # Study Center Lighting
    for s_li, (lx, ly) in enumerate([(sc_cx - 2.0, sc_cy), (sc_cx + 4.0, sc_cy)]):
        sldata = bpy.data.lights.new(f"Owen_Light_Study_{s_li}", "POINT")
        sldata.energy = 280.0
        sldata.color = (1.0, 0.98, 0.95)
        slobj = bpy.data.objects.new(f"Owen_Light_Study_{s_li}", sldata)
        slobj.location = (lx, ly, 3.4)
        col_int.objects.link(slobj)

    # D. AUTHENTIC STUDENT DOUBLE DORM ROOM (Room 216, SW Wing Floor 1)
    # Sited at SW wing: oc_x - 31.35 = -625.35, oc_y - 33.5 = 505.6
    rm_cx = oc_x - 34.0
    rm_cy = oc_y - 36.0
    create_box("Owen_Dorm_Room216_Floor", loc=(rm_cx, rm_cy, 0.08), size=(5.6, 4.4, 0.12), mat=mat_terrazzo, col=col_int)
    create_box("Owen_Dorm_Room216_Wall_N", loc=(rm_cx, rm_cy + 2.2, 1.9), size=(5.6, 0.2, 3.8), mat=mat_limestone, col=col_int)
    create_box("Owen_Dorm_Room216_Wall_S", loc=(rm_cx, rm_cy - 2.2, 1.9), size=(5.6, 0.2, 3.8), mat=mat_limestone, col=col_int)
    create_box("Owen_Dorm_Room216_Wall_E", loc=(rm_cx + 2.8, rm_cy, 1.9), size=(0.2, 4.4, 3.8), mat=mat_limestone, col=col_int)
    create_box("Owen_Dorm_Room216_Door", loc=(rm_cx + 2.8, rm_cy - 1.2, 1.4), size=(0.1, 1.0, 2.4), mat=mat_oak, col=col_int)

    # 2 Twin-XL Beds
    for bed_i, bed_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        create_box(f"Owen_Dorm_Bed_Frame_{bed_i}", loc=(rm_cx - 1.4, bed_y, 0.45), size=(2.2, 1.15, 0.6), mat=mat_oak, col=col_int)
        create_box(f"Owen_Dorm_Bed_Mattress_{bed_i}", loc=(rm_cx - 1.4, bed_y, 0.72), size=(2.1, 1.05, 0.25), mat=mat_carpet_navy, col=col_int)
        create_box(f"Owen_Dorm_Bed_Pillow_{bed_i}", loc=(rm_cx - 2.15, bed_y, 0.88), size=(0.55, 0.75, 0.15), mat=mat_white, col=col_int)

    # 2 Oak Study Desks with Hutch Bookshelves
    for dsk_i, dsk_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        create_box(f"Owen_Dorm_Desk_{dsk_i}", loc=(rm_cx + 1.6, dsk_y, 0.65), size=(1.35, 0.85, 0.76), mat=mat_oak, col=col_int)
        create_box(f"Owen_Dorm_Desk_Hutch_{dsk_i}", loc=(rm_cx + 2.1, dsk_y, 1.4), size=(0.35, 0.85, 0.85), mat=mat_oak, col=col_int)
        create_box(f"Owen_Dorm_Desk_Chair_{dsk_i}", loc=(rm_cx + 1.0, dsk_y, 0.55), size=(0.6, 0.6, 0.85), mat=mat_dark_oak, col=col_int)

    # Wardrobes on South Interior Wall (never blocking the window!)
    create_box("Owen_Dorm_Wardrobes", loc=(rm_cx + 0.2, rm_cy - 1.8, 1.4), size=(1.8, 0.65, 2.2), mat=mat_oak, col=col_int)

    # Signature Dual Window Box Cooling Fans (Framed in the West Window)
    create_box("Owen_Dorm_Window_Box_Fan_1", loc=(rm_cx - 2.7, rm_cy - 0.45, 1.8), size=(0.22, 0.55, 0.55), mat=mat_white, col=col_int)
    create_box("Owen_Dorm_Window_Box_Fan_2", loc=(rm_cx - 2.7, rm_cy + 0.45, 1.8), size=(0.22, 0.55, 0.55), mat=mat_white, col=col_int)

    # Dorm Ceiling Downlight & Study Lamps
    dddata = bpy.data.lights.new("Owen_Light_Dorm216_Ceiling", "POINT")
    dddata.energy = 160.0
    dddata.color = (1.0, 0.95, 0.88)
    ddobj = bpy.data.objects.new("Owen_Light_Dorm216_Ceiling", dddata)
    ddobj.location = (rm_cx, rm_cy, 3.2)
    col_int.objects.link(ddobj)

    for dl_i, dl_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        s_ldata = bpy.data.lights.new(f"Owen_Light_Desk_{dl_i}", "POINT")
        s_ldata.energy = 45.0
        s_ldata.color = (1.0, 0.98, 0.92)
        s_lobj = bpy.data.objects.new(f"Owen_Light_Desk_{dl_i}", s_ldata)
        s_lobj.location = (rm_cx + 1.5, dl_y, 1.6)
        col_int.objects.link(s_lobj)

    print("Owen Hall interior spaces (Lobby, Piano Lounge, Study Center, Room 216) completed.")

    # =============================================================
    # 9. COURTYARDS & SITE INTEGRATION (WEST & EAST COURTYARDS)
    # =============================================================
    print("Constructing Owen Hall courtyards and pedestrian approaches...")

    # A. WEST INNER COURTYARD (Between NW and SW Wings)
    # Center: X in [oc_x - 30.6, oc_x - 18.5], Y in [oc_y - 12.5, oc_y + 13.2]
    wcy_cx, wcy_cy = oc_x - 24.5, oc_y
    create_box("Owen_West_Courtyard_Brick_Plaza", loc=(wcy_cx, wcy_cy, 0.10), size=(12.0, 25.0, 0.14), mat=mat_brick, col=col_site)
    create_box("Owen_West_Courtyard_Lawn_Panel", loc=(wcy_cx, wcy_cy, 0.12), size=(8.0, 17.0, 0.12), mat=mat_felt_green, col=col_site)
    for sw_i, sw_y in enumerate([wcy_cy - 6.5, wcy_cy + 6.5]):
        create_box(f"Owen_West_Courtyard_Seatwall_{sw_i}", loc=(wcy_cx, sw_y, 0.35), size=(7.0, 0.65, 0.45), mat=mat_limestone, col=col_site)
        create_box(f"Owen_West_Courtyard_Teak_Top_{sw_i}", loc=(wcy_cx, sw_y, 0.60), size=(7.2, 0.75, 0.08), mat=mat_teak, col=col_site)
    create_box("Owen_West_Picnic_Table_Top", loc=(wcy_cx, wcy_cy, 0.78), size=(2.4, 1.2, 0.08), mat=mat_teak, col=col_site)
    create_box("Owen_West_Picnic_Bench_1", loc=(wcy_cx, wcy_cy - 0.9, 0.46), size=(2.4, 0.4, 0.06), mat=mat_teak, col=col_site)
    create_box("Owen_West_Picnic_Bench_2", loc=(wcy_cx, wcy_cy + 0.9, 0.46), size=(2.4, 0.4, 0.06), mat=mat_teak, col=col_site)

    # B. EAST INNER COURTYARD (Facing North Martin Jischke Drive)
    # Center: X in [oc_x + 18.5, oc_x + 30.8], Y in [oc_y - 12.5, oc_y + 13.2]
    ecy_cx, ecy_cy = oc_x + 24.5, oc_y
    create_box("Owen_East_Courtyard_Brick_Plaza", loc=(ecy_cx, ecy_cy, 0.10), size=(12.0, 25.0, 0.14), mat=mat_brick, col=col_site)
    create_box("Owen_East_Courtyard_Limestone_Planter", loc=(ecy_cx, ecy_cy, 0.35), size=(5.5, 5.5, 0.55), mat=mat_limestone, col=col_site)
    create_box("Owen_East_Courtyard_Planter_Lawn", loc=(ecy_cx, ecy_cy, 0.52), size=(4.5, 4.5, 0.22), mat=mat_felt_green, col=col_site)
    for ang_i, ang_deg in enumerate([45, 135, 225, 315]):
        rad = math.radians(ang_deg)
        create_box(f"Owen_East_Bench_{ang_i}", loc=(ecy_cx + 4.8 * math.cos(rad), ecy_cy + 4.8 * math.sin(rad), 0.42), size=(2.6, 0.65, 0.48), mat=mat_teak, col=col_site)

    # C. SURROUNDING PEDESTRIAN CONCOURSE & CONNECTORS
    create_box("Owen_Jischke_Pedestrian_Concourse", loc=(oc_x + 48.0, oc_y, 0.08), size=(8.0, 120.0, 0.12), mat=mat_limestone, col=col_site)
    create_box("Owen_Stadium_Ave_Sidewalk", loc=(oc_x, oc_y + 60.0, 0.08), size=(85.0, 8.0, 0.12), mat=mat_limestone, col=col_site)
    create_box("Owen_Tarkington_Connector_Walkway", loc=(oc_x, oc_y - 62.0, 0.08), size=(75.0, 10.0, 0.12), mat=mat_limestone, col=col_site)

    # Campus Victorian Lantern Posts
    for lp_i, (lpx, lpy) in enumerate([
        (oc_x + 46.0, oc_y + 56.0),
        (oc_x + 46.0, oc_y - 56.0),
        (oc_x - 46.0, oc_y + 56.0),
        (oc_x - 46.0, oc_y - 56.0)
    ]):
        create_cylinder(f"Owen_Lantern_Pole_{lp_i}", loc=(lpx, lpy, 2.2), radius=0.08, depth=4.2, mat=mat_bronze, col=col_site)
        create_box(f"Owen_Lantern_Head_{lp_i}", loc=(lpx, lpy, 4.4), size=(0.45, 0.45, 0.65), mat=mat_glass, col=col_site)

    # =============================================================
    # 10. DEDICATED INSPECTION CAMERAS SETUP
    # =============================================================
    cameras = [
        # 1. North Facade from West Stadium Ave
        {
            "name": "Cam_27_Owen_Hall_StadiumAve_StreetView",
            "loc": (oc_x, oc_y + 54.0, 6.5),
            "target": (oc_x, oc_y + 26.0, 4.5),
            "lens": 24.0,
            "col": col_ext
        },
        # 2. East Facade from North Martin Jischke Drive
        {
            "name": "Cam_28_Owen_Hall_Jischke_East_Courtyard",
            "loc": (oc_x + 70.0, oc_y, 8.5),
            "target": (oc_x + 31.35, oc_y, 6.0),
            "lens": 24.0,
            "col": col_ext
        },
        # 3. Main Recreational Lounge with Upright Piano
        {
            "name": "Cam_29_Owen_Hall_Lounge_Piano_Interior",
            "loc": (rl_cx + 4.5, rl_cy - 4.5, 1.8),
            "target": (rl_cx - 2.5, rl_cy + 2.5, 1.2),
            "lens": 20.0,
            "col": col_int
        },
        # 4. Owen Study Center & IT Computer Lab
        {
            "name": "Cam_30_Owen_Hall_StudyCenter_Interior",
            "loc": (sc_cx - 4.5, sc_cy - 4.5, 1.8),
            "target": (sc_cx + 2.0, sc_cy + 1.5, 1.2),
            "lens": 20.0,
            "col": col_int
        },
        # 5. Authentic Double Student Dorm Room 216
        {
            "name": "Cam_31_Owen_Hall_Student_Dorm_Interior",
            "loc": (rm_cx + 2.0, rm_cy, 1.8),
            "target": (rm_cx - 1.8, rm_cy, 1.2),
            "lens": 18.0,
            "col": col_int
        }
    ]

    for cfg in cameras:
        cname = cfg["name"]
        cdata = bpy.data.cameras.get(cname) or bpy.data.cameras.new(cname)
        cdata.lens = cfg["lens"]
        cdata.clip_end = 6000.0
        cobj = bpy.data.objects.get(cname)
        if not cobj:
            cobj = bpy.data.objects.new(cname, cdata)
            cfg["col"].objects.link(cobj)
        else:
            cobj.data = cdata
        cobj.location = cfg["loc"]
        look_at(cobj, cfg["target"])

    bpy.context.scene.camera = bpy.data.objects["Cam_27_Owen_Hall_StadiumAve_StreetView"]
    print("Dedicated Owen Hall inspection cameras calibrated.")

    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master scene successfully saved: {save_path}")
    print("Richard Owen Hall construction complete!")

if __name__ == "__main__":
    build_owen_hall()
