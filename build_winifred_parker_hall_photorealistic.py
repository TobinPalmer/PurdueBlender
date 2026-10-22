"""
Photorealistic Georeferenced Winifred Parker Hall Construction Script
Purdue University Digital Twin Project
Master Blend: purdue_campus_master.blend

Geospatial Alignment:
- Origin: Purdue Bell Tower (40.4274, -86.9137)
- Coordinates: Center at X = -562.6m, Y = 49.5m (Elevation Z = 0.0m)
- Footprint: 54.5m wide x 79.6m long (OSM Way 327303065)
- Address: 1196 Third Street, West Lafayette, IN 47907
"""

import bpy
import bmesh
import mathutils
import math
import os

# -------------------------------------------------------------
# Configuration & Spatial Anchor
# -------------------------------------------------------------
CENTER_X = -562.65
CENTER_Y = 49.53
GROUND_Z = 0.0

COL_NAMES = {
    'exterior': '27_Winifred_Parker_Hall_Exterior',
    'interiors': '28_Winifred_Parker_Hall_Interiors',
    'courtyard': '29_Winifred_Parker_Hall_Courtyard_and_Site',
    'cameras': '05_Cameras_and_Views'
}

# -------------------------------------------------------------
# Mesh Helper Functions
# -------------------------------------------------------------
def get_or_create_col(col_name):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    return col

def clear_collection_objects(col):
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

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

# -------------------------------------------------------------
# Material Factory
# -------------------------------------------------------------
def get_or_create_mat(name, base_color, roughness=0.6, metallic=0.0, transmission=0.0, emission=None, emission_str=1.0, ior=1.45):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
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

def setup_materials():
    mats = {}
    mats['brick'] = get_or_create_mat("Parker_Purdue_Red_Brick", (0.50, 0.16, 0.11, 1.0), roughness=0.85)
    mats['limestone'] = get_or_create_mat("Parker_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mats['glass'] = get_or_create_mat("Parker_Solar_Curtain_Glass", (0.02, 0.05, 0.07, 1.0), roughness=0.05, metallic=0.1, transmission=0.88, ior=1.52)
    mats['bronze'] = get_or_create_mat("Parker_Bronze_Mullion", (0.12, 0.10, 0.08, 1.0), roughness=0.4, metallic=0.85)
    mats['roof'] = get_or_create_mat("Parker_Roof_Membrane", (0.32, 0.32, 0.31, 1.0), roughness=0.9)
    mats['starbucks_green'] = get_or_create_mat("Parker_Starbucks_Green", (0.005, 0.12, 0.05, 1.0), roughness=0.4)
    mats['starbucks_logo'] = get_or_create_mat("Parker_Starbucks_Logo", (0.92, 0.98, 0.92, 1.0), roughness=0.2, emission=(0.85, 1.0, 0.85, 1.0), emission_str=4.0)
    mats['wood_walnut'] = get_or_create_mat("Parker_Wood_Floor_Walnut", (0.28, 0.15, 0.08, 1.0), roughness=0.45)
    mats['terrazzo'] = get_or_create_mat("Parker_Terrazzo_Cream", (0.86, 0.84, 0.78, 1.0), roughness=0.22)
    mats['quartz'] = get_or_create_mat("Parker_White_Quartz", (0.92, 0.92, 0.91, 1.0), roughness=0.25)
    mats['oak'] = get_or_create_mat("Parker_Oak_Furniture", (0.62, 0.44, 0.24, 1.0), roughness=0.5)
    mats['fabric_navy'] = get_or_create_mat("Parker_Fabric_Navy", (0.04, 0.08, 0.22, 1.0), roughness=0.8)
    mats['warm_glow'] = get_or_create_mat("Parker_Warm_Ceiling_Glow", (1.0, 0.92, 0.78, 1.0), roughness=0.2, emission=(1.0, 0.92, 0.78, 1.0), emission_str=3.0)
    mats['sign_gold'] = get_or_create_mat("Parker_Signage_Gold", (0.85, 0.70, 0.30, 1.0), roughness=0.35, metallic=0.85)
    mats['concrete'] = get_or_create_mat("Parker_Plaza_Concrete", (0.55, 0.55, 0.54, 1.0), roughness=0.8)
    mats['paver_brick'] = get_or_create_mat("Parker_Plaza_Paver_Brick", (0.46, 0.18, 0.12, 1.0), roughness=0.85)
    mats['grass'] = get_or_create_mat("Parker_Courtyard_Lawn", (0.08, 0.22, 0.05, 1.0), roughness=0.9)
    return mats


# -------------------------------------------------------------
# Component 1: Exterior Wings, Architecture & Fenestration
# -------------------------------------------------------------
def build_exterior_wings(col, mats):
    print("Building Winifred Parker Hall exterior wings and architectural articulation...")
    
    # Building height: 5 stories + parapet = 20.2m
    b_height = 20.2
    h_z = b_height * 0.5

    # 1. South Wing (Third Street Frontage)
    # Bounds: X in [-589.9, -535.4], Y in [11.9, 28.3], width ~54.5m, depth ~16.4m
    s_cx = (-589.9 + -535.4) / 2.0 # -562.65
    s_cy = (11.9 + 28.3) / 2.0     # 20.1
    s_w = 54.5
    s_d = 16.4
    create_box("Parker_SouthWing_MainMass", (s_cx, s_cy, h_z), (s_w, s_d, b_height), mats['brick'], col)
    
    # 2. East Wing (Running North along Parker Quad)
    # Bounds: X in [-548.2, -535.4], Y in [28.3, 82.5], width ~12.8m, length ~54.2m
    e_cx = (-548.2 + -535.4) / 2.0 # -541.8
    e_cy = (28.3 + 82.5) / 2.0     # 55.4
    e_w = 12.8
    e_d = 54.2
    create_box("Parker_EastWing_MainMass", (e_cx, e_cy, h_z), (e_w, e_d, b_height), mats['brick'], col)
    
    # 3. North Wing (Projecting West from East Wing)
    # Bounds: X in [-565.0, -538.0], Y in [73.2, 89.3], width ~27.0m, depth ~16.1m
    n_cx = (-565.0 + -538.0) / 2.0 # -551.5
    n_cy = (73.2 + 89.3) / 2.0     # 81.25
    n_w = 27.0
    n_d = 16.1
    create_box("Parker_NorthWing_MainMass", (n_cx, n_cy, h_z), (n_w, n_d, b_height), mats['brick'], col)

    # 4. Center Wing Finger (Extending West into inner courtyard)
    # Bounds: X in [-565.4, -548.1], Y in [42.3, 58.9], width ~17.3m, depth ~16.6m
    c_cx = (-565.4 + -548.1) / 2.0 # -556.75
    c_cy = (42.3 + 58.9) / 2.0     # 50.6
    c_w = 17.3
    c_d = 16.6
    create_box("Parker_CenterFinger_MainMass", (c_cx, c_cy, h_z), (c_w, c_d, b_height), mats['brick'], col)

    # ---------------------------------------------------------
    # Bedford Limestone Water Table & Horizontal Beltcourses
    # ---------------------------------------------------------
    # Ground water table base (Z = 0 to 1.2m)
    create_box("Parker_Base_WaterTable_South", (s_cx, s_cy, 0.6), (s_w + 0.5, s_d + 0.5, 1.2), mats['limestone'], col)
    create_box("Parker_Base_WaterTable_East", (e_cx, e_cy, 0.6), (e_w + 0.5, e_d + 0.5, 1.2), mats['limestone'], col)
    create_box("Parker_Base_WaterTable_North", (n_cx, n_cy, 0.6), (n_w + 0.5, n_d + 0.5, 1.2), mats['limestone'], col)
    create_box("Parker_Base_WaterTable_Center", (c_cx, c_cy, 0.6), (c_w + 0.5, c_d + 0.5, 1.2), mats['limestone'], col)

    # Floor Beltcourses at Z = 4.2m (floor 2), 7.4m (floor 3), 10.6m (floor 4), 13.8m (floor 5), 17.0m (floor 6), 20.2m (parapet coping)
    floors_z = [4.2, 7.4, 10.6, 13.8, 17.0, 20.2]
    for idx, fz in enumerate(floors_z):
        is_coping = (idx == len(floors_z) - 1)
        bh = 0.5 if is_coping else 0.35
        # South wing beltcourses
        create_box(f"Parker_Beltcourse_South_{idx}", (s_cx, s_cy, fz), (s_w + 0.4, s_d + 0.4, bh), mats['limestone'], col)
        # East wing beltcourses
        create_box(f"Parker_Beltcourse_East_{idx}", (e_cx, e_cy, fz), (e_w + 0.4, e_d + 0.4, bh), mats['limestone'], col)
        # North wing beltcourses
        create_box(f"Parker_Beltcourse_North_{idx}", (n_cx, n_cy, fz), (n_w + 0.4, n_d + 0.4, bh), mats['limestone'], col)
        # Center finger beltcourses
        create_box(f"Parker_Beltcourse_Center_{idx}", (c_cx, c_cy, fz), (c_w + 0.4, c_d + 0.4, bh), mats['limestone'], col)

    # ---------------------------------------------------------
    # Roof Gravel Membrane & HVAC Mechanical Penthouses
    # ---------------------------------------------------------
    # Roof slabs
    create_box("Parker_Roof_South", (s_cx, s_cy, 20.0), (s_w - 0.6, s_d - 0.6, 0.3), mats['roof'], col)
    create_box("Parker_Roof_East", (e_cx, e_cy, 20.0), (e_w - 0.6, e_d - 0.6, 0.3), mats['roof'], col)
    create_box("Parker_Roof_North", (n_cx, n_cy, 20.0), (n_w - 0.6, n_d - 0.6, 0.3), mats['roof'], col)
    create_box("Parker_Roof_Center", (c_cx, c_cy, 20.0), (c_w - 0.6, c_d - 0.6, 0.3), mats['roof'], col)

    # 3 Mechanical Penthouses with bronze HVAC louvers
    penthouses = [
        ("South", s_cx, s_cy, 12.0, 8.0),
        ("East", e_cx, e_cy + 10.0, 7.0, 14.0),
        ("North", n_cx, n_cy, 12.0, 7.0)
    ]
    for p_name, px, py, pw, pd in penthouses:
        create_box(f"Parker_Penthouse_{p_name}", (px, py, 21.8), (pw, pd, 3.2), mats['limestone'], col)
        # Louver screens
        create_box(f"Parker_Penthouse_{p_name}_Louvers", (px, py, 21.8), (pw + 0.2, pd + 0.2, 2.4), mats['bronze'], col)

    # ---------------------------------------------------------
    # South Facade: Ground Floor Starbucks & Main Entrance
    # ---------------------------------------------------------
    # Starbucks Storefront Glazing (West half of South facade: X in [-589.9, -568.0], Y = 11.7m, Z = 0 to 4.2m)
    sb_cx = (-589.9 + -568.0) / 2.0 # -578.95
    sb_w = 21.9
    create_box("Parker_Starbucks_Storefront_Glass", (sb_cx, 11.65, 2.4), (sb_w, 0.3, 3.2), mats['glass'], col)
    # Storefront Bronze Mullions
    for m in range(7):
        mx = -589.9 + m * (sb_w / 6.0)
        create_box(f"Parker_Starbucks_Mullion_{m}", (mx, 11.60, 2.4), (0.15, 0.4, 3.3), mats['bronze'], col)
    # Starbucks Transom Fascia & Signage Backing
    create_box("Parker_Starbucks_Fascia", (sb_cx, 11.60, 4.0), (sb_w + 0.4, 0.5, 0.8), mats['starbucks_green'], col)
    # Illuminated Starbucks Siren Logo Roundel (2.0m diameter)
    create_cylinder("Parker_Starbucks_Exterior_Siren", (sb_cx, 11.35, 4.0), 0.9, 0.2, mats['starbucks_logo'], col)
    # "STARBUCKS" Bronze/White Lettering Bar
    create_box("Parker_Starbucks_Lettering_Bar", (sb_cx, 11.35, 3.1), (7.5, 0.15, 0.5), mats['starbucks_logo'], col)

    # Monumental Main Building Entrance (Center of South Facade: X in [-566.0, -554.0], Y = 11.7m)
    ent_cx = -560.0
    # Monumental Limestone Portico Surround
    create_box("Parker_MainEntrance_Surround", (ent_cx, 11.45, 2.8), (12.0, 0.9, 4.4), mats['limestone'], col)
    # Portico Canopy & Entablature
    create_box("Parker_MainEntrance_Canopy", (ent_cx, 11.1, 4.6), (13.2, 2.2, 0.6), mats['bronze'], col)
    # Double Glazed Entrance Doors
    create_box("Parker_MainEntrance_Glazing", (ent_cx, 11.45, 2.2), (10.0, 0.2, 3.2), mats['glass'], col)
    create_box("Parker_MainEntrance_DoorFrames", (ent_cx, 11.42, 2.2), (10.2, 0.3, 3.3), mats['bronze'], col)
    # Gold Lettering Signage: "WINIFRED PARKER HALL"
    create_box("Parker_Signage_Plaque", (ent_cx, 10.95, 4.6), (8.5, 0.1, 0.7), mats['sign_gold'], col)
    # Address plaque: "1196 THIRD STREET"
    create_box("Parker_Address_Plaque", (ent_cx, 10.95, 3.8), (4.2, 0.1, 0.4), mats['sign_gold'], col)

    # Third Street Market Storefront (East half of South facade: X in [-552.0, -538.0])
    mkt_cx = -545.0
    mkt_w = 14.0
    create_box("Parker_Market_Storefront_Glass", (mkt_cx, 11.65, 2.4), (mkt_w, 0.3, 3.2), mats['glass'], col)
    for m in range(5):
        mx = -552.0 + m * (mkt_w / 4.0)
        create_box(f"Parker_Market_Mullion_{m}", (mx, 11.60, 2.4), (0.15, 0.4, 3.3), mats['bronze'], col)

    # ---------------------------------------------------------
    # Upper Levels Rhythmic Fenestration (Floors 2 to 6)
    # ---------------------------------------------------------
    # South Facade Upper Windows: 12 bays across floors 2 to 6 (5 floors x 12 = 60 windows)
    for floor_idx, fz in enumerate([5.8, 9.0, 12.2, 15.4, 18.6]):
        for bay in range(12):
            wx = -586.0 + bay * 4.4
            create_box(f"Parker_Win_South_F{floor_idx}_B{bay}", (wx, 11.65, fz), (2.4, 0.3, 2.1), mats['glass'], col)
            create_box(f"Parker_Sill_South_F{floor_idx}_B{bay}", (wx, 11.55, fz - 1.15), (2.6, 0.5, 0.25), mats['limestone'], col)
            create_box(f"Parker_Spandrel_South_F{floor_idx}_B{bay}", (wx, 11.60, fz + 1.25), (2.5, 0.4, 0.4), mats['bronze'], col)

    # East Facade Windows (Facing Parker Quad): 14 bays across floors 2 to 6
    for floor_idx, fz in enumerate([5.8, 9.0, 12.2, 15.4, 18.6]):
        for bay in range(13):
            ey = 29.0 + bay * 4.0
            # 2-story glass curtain wall lounges at center bays (bays 5, 6, 7)
            if bay in [5, 6, 7] and floor_idx in [0, 1]:
                create_box(f"Parker_Curtain_East_L1_B{bay}", (-535.2, ey, 7.4), (0.3, 3.6, 5.8), mats['glass'], col)
                create_box(f"Parker_Curtain_East_L1_Mull_{bay}", (-535.1, ey, 7.4), (0.4, 0.2, 6.0), mats['bronze'], col)
            elif bay in [5, 6, 7] and floor_idx in [2, 3]:
                create_box(f"Parker_Curtain_East_L2_B{bay}", (-535.2, ey, 13.8), (0.3, 3.6, 5.8), mats['glass'], col)
                create_box(f"Parker_Curtain_East_L2_Mull_{bay}", (-535.1, ey, 13.8), (0.4, 0.2, 6.0), mats['bronze'], col)
            else:
                create_box(f"Parker_Win_East_F{floor_idx}_B{bay}", (-535.2, ey, fz), (0.3, 2.2, 2.1), mats['glass'], col)
                create_box(f"Parker_Sill_East_F{floor_idx}_B{bay}", (-535.1, ey, fz - 1.15), (0.5, 2.4, 0.25), mats['limestone'], col)

    # West Facade Windows (Facing Russell St): 8 bays across floors 2 to 6
    for floor_idx, fz in enumerate([5.8, 9.0, 12.2, 15.4, 18.6]):
        for bay in range(8):
            wy = 30.0 + bay * 3.8
            create_box(f"Parker_Win_West_F{floor_idx}_B{bay}", (-565.6, wy, fz), (0.3, 2.2, 2.1), mats['glass'], col)
            create_box(f"Parker_Sill_West_F{floor_idx}_B{bay}", (-565.7, wy, fz - 1.15), (0.5, 2.4, 0.25), mats['limestone'], col)

    # North Facade Windows: 6 bays across floors 2 to 6
    for floor_idx, fz in enumerate([5.8, 9.0, 12.2, 15.4, 18.6]):
        for bay in range(6):
            nx = -562.0 + bay * 4.2
            create_box(f"Parker_Win_North_F{floor_idx}_B{bay}", (nx, 89.5, fz), (2.2, 0.3, 2.1), mats['glass'], col)
            create_box(f"Parker_Sill_North_F{floor_idx}_B{bay}", (nx, 89.6, fz - 1.15), (2.4, 0.5, 0.25), mats['limestone'], col)


# -------------------------------------------------------------
# Component 2: Finished Photorealistic Interiors
# -------------------------------------------------------------
def build_photorealistic_interiors(col, mats):
    print("Building Winifred Parker Hall ground-floor Starbucks, lobby, and student suites...")
    
    # ---------------------------------------------------------
    # 1. Campus Starbucks (Ground Floor Southwest: X in [-588, -568], Y in [13, 27], Z = 0 to 4.2m)
    # ---------------------------------------------------------
    sb_cx = -578.0
    sb_cy = 20.0
    # Warm walnut wood-plank flooring
    create_box("Parker_Starbucks_Floor", (sb_cx, sb_cy, 0.05), (19.0, 13.0, 0.1), mats['wood_walnut'], col)
    # Warm acoustic ceiling with recessed warm downlight glow
    create_box("Parker_Starbucks_Ceiling", (sb_cx, sb_cy, 4.0), (19.0, 13.0, 0.2), mats['warm_glow'], col)

    # L-Shaped Barista Service Counter (Dark Oak with White Quartz countertop)
    # Front counter (length 8.5m)
    create_box("Parker_Starbucks_FrontCounter_Base", (-574.0, 22.0, 0.55), (8.5, 1.2, 1.1), mats['oak'], col)
    create_box("Parker_Starbucks_FrontCounter_Top", (-574.0, 22.0, 1.15), (8.7, 1.4, 0.1), mats['quartz'], col)
    # Return counter (length 5.0m)
    create_box("Parker_Starbucks_ReturnCounter_Base", (-578.0, 24.5, 0.55), (1.2, 4.0, 1.1), mats['oak'], col)
    create_box("Parker_Starbucks_ReturnCounter_Top", (-578.0, 24.5, 1.15), (1.4, 4.2, 0.1), mats['quartz'], col)

    # Dual Mastrena II Espresso Machines
    create_box("Parker_Starbucks_Espresso_1", (-575.5, 22.0, 1.5), (0.9, 0.8, 0.6), mats['bronze'], col)
    create_box("Parker_Starbucks_Espresso_2", (-573.5, 22.0, 1.5), (0.9, 0.8, 0.6), mats['bronze'], col)
    # Glass Refrigerated Pastry Display Case
    create_box("Parker_Starbucks_PastryCase", (-571.5, 22.0, 1.5), (1.8, 0.9, 0.6), mats['glass'], col)
    # POS Checkout Terminals
    create_box("Parker_Starbucks_POS_1", (-576.8, 21.8, 1.35), (0.4, 0.4, 0.3), mats['bronze'], col)
    create_box("Parker_Starbucks_POS_2", (-570.2, 21.8, 1.35), (0.4, 0.4, 0.3), mats['bronze'], col)

    # Back Bar Counter & Syrup Dispensers
    create_box("Parker_Starbucks_BackBar", (-574.0, 25.5, 0.55), (8.5, 1.0, 1.1), mats['quartz'], col)
    # Overhead Warm LED Menu Boards (4 panels)
    for b in range(4):
        bx = -576.5 + b * 1.8
        create_box(f"Parker_Starbucks_MenuBoard_{b}", (bx, 22.0, 3.0), (1.6, 0.1, 0.9), mats['warm_glow'], col)

    # Interior Feature Wall with Illuminated Starbucks Siren Logo
    create_box("Parker_Starbucks_FeatureWall", (-568.5, 20.0, 2.0), (0.3, 13.0, 4.0), mats['starbucks_green'], col)
    create_cylinder("Parker_Starbucks_Interior_Siren", (-568.3, 20.0, 2.4), 1.1, 0.1, mats['starbucks_logo'], col)

    # Cafe Dining High-Top Tables & Swivel Barstools
    for idx in range(3):
        tx = -584.0 + idx * 3.5
        # High top table
        create_cylinder(f"Parker_SB_Table_{idx}", (tx, 15.5, 0.55), 0.6, 1.1, mats['bronze'], col)
        create_cylinder(f"Parker_SB_Top_{idx}", (tx, 15.5, 1.12), 0.75, 0.06, mats['quartz'], col)
        # Barstools
        create_cylinder(f"Parker_SB_StoolA_{idx}", (tx - 0.7, 15.5, 0.4), 0.22, 0.8, mats['oak'], col)
        create_cylinder(f"Parker_SB_StoolB_{idx}", (tx + 0.7, 15.5, 0.4), 0.22, 0.8, mats['oak'], col)

    # Lounge Area with Soft Armchairs and Low Table
    create_box("Parker_SB_Lounge_Sofa", (-584.0, 19.5, 0.5), (3.2, 1.2, 0.8), mats['fabric_navy'], col)
    create_box("Parker_SB_CoffeeTable", (-584.0, 17.5, 0.25), (2.0, 1.0, 0.4), mats['oak'], col)
    create_box("Parker_SB_Armchair_1", (-586.0, 17.5, 0.5), (1.0, 1.0, 0.8), mats['fabric_navy'], col)
    create_box("Parker_SB_Armchair_2", (-582.0, 17.5, 0.5), (1.0, 1.0, 0.8), mats['fabric_navy'], col)

    # ---------------------------------------------------------
    # 2. Main Building Reception Lobby & Student Commons
    # ---------------------------------------------------------
    # Center of ground floor: X in [-566, -550], Y in [13, 28]
    lob_cx = -558.0
    lob_cy = 20.5
    # Polished cream terrazzo flooring
    create_box("Parker_Lobby_Terrazzo_Floor", (lob_cx, lob_cy, 0.05), (16.0, 14.0, 0.1), mats['terrazzo'], col)
    create_box("Parker_Lobby_Ceiling", (lob_cx, lob_cy, 4.0), (16.0, 14.0, 0.2), mats['warm_glow'], col)

    # Reception Front Desk (Oak Slat Front with White Quartz Counter)
    create_box("Parker_Reception_Desk_Base", (lob_cx + 2.0, lob_cy + 3.0, 0.55), (4.8, 1.4, 1.1), mats['oak'], col)
    create_box("Parker_Reception_Desk_Top", (lob_cx + 2.0, lob_cy + 3.0, 1.15), (5.0, 1.6, 0.1), mats['quartz'], col)
    create_box("Parker_Reception_PC", (lob_cx + 2.0, lob_cy + 3.0, 1.45), (0.6, 0.3, 0.45), mats['bronze'], col)

    # Smart Parcel Locker Wall (Automated student package pickup bank)
    create_box("Parker_Parcel_Lockers", (lob_cx - 6.5, lob_cy + 3.5, 1.4), (0.8, 5.0, 2.6), mats['bronze'], col)

    # Digital Interactive Campus Directory Display
    create_box("Parker_Digital_Directory", (lob_cx - 6.5, lob_cy - 2.5, 1.6), (0.2, 1.2, 1.8), mats['warm_glow'], col)

    # Collaborative Student Lounge Upholstery
    create_box("Parker_Lobby_Modular_Sofa", (lob_cx + 2.0, lob_cy - 3.0, 0.45), (5.0, 1.8, 0.75), mats['fabric_navy'], col)
    create_box("Parker_Lobby_Coffee_Table", (lob_cx + 2.0, lob_cy - 1.2, 0.25), (3.6, 0.9, 0.4), mats['oak'], col)

    # ---------------------------------------------------------
    # 3. Authentic Student Suite (Floor 2 Model Suite: X in [-548, -536], Y in [30, 46])
    # ---------------------------------------------------------
    suite_cx = -542.0
    suite_cy = 38.0
    suite_z = 5.8
    # Suite Floor slab
    create_box("Parker_Suite_Floor", (suite_cx, suite_cy, suite_z - 1.5), (11.5, 15.0, 0.15), mats['wood_walnut'], col)
    create_box("Parker_Suite_Ceiling", (suite_cx, suite_cy, suite_z + 1.5), (11.5, 15.0, 0.15), mats['warm_glow'], col)

    # Common Living Room Area (South half of suite: Y in [30, 37])
    # Living room sectional sofa
    create_box("Parker_Suite_Living_Sofa", (suite_cx, 33.0, suite_z - 0.9), (3.6, 1.4, 0.8), mats['fabric_navy'], col)
    create_box("Parker_Suite_Living_CoffeeTable", (suite_cx, 34.5, suite_z - 1.1), (2.0, 0.8, 0.4), mats['oak'], col)
    # Media console & 55" TV
    create_box("Parker_Suite_TV_Console", (suite_cx, 36.5, suite_z - 1.0), (2.4, 0.6, 0.6), mats['oak'], col)
    create_box("Parker_Suite_TV_Screen", (suite_cx, 36.5, suite_z - 0.2), (1.4, 0.1, 0.8), mats['bronze'], col)

    # Bedroom 1 (North-East quadrant of suite: X in [-541, -536], Y in [38, 45])
    # Two Twin-XL Beds
    create_box("Parker_Bed1_A", (-538.5, 43.5, suite_z - 1.0), (1.1, 2.1, 0.6), mats['fabric_navy'], col)
    create_box("Parker_Bed1_B", (-538.5, 40.5, suite_z - 1.0), (1.1, 2.1, 0.6), mats['fabric_navy'], col)
    # Dual Oak Study Desks with Hutch Shelves
    create_box("Parker_Desk1_A", (-536.8, 43.5, suite_z - 0.9), (0.8, 1.4, 0.75), mats['oak'], col)
    create_box("Parker_Desk1_B", (-536.8, 40.5, suite_z - 0.9), (0.8, 1.4, 0.75), mats['oak'], col)
    # Task chairs
    create_box("Parker_Chair1_A", (-537.6, 43.5, suite_z - 0.9), (0.5, 0.5, 0.8), mats['bronze'], col)
    create_box("Parker_Chair1_B", (-537.6, 40.5, suite_z - 0.9), (0.5, 0.5, 0.8), mats['bronze'], col)

    # Double-Vanity Shared Bathroom
    create_box("Parker_Bath_Vanity", (-546.0, 38.0, suite_z - 0.9), (0.9, 2.8, 0.85), mats['quartz'], col)
    create_box("Parker_Bath_Mirror", (-546.4, 38.0, suite_z - 0.1), (0.1, 2.6, 1.0), mats['glass'], col)
    create_cylinder("Parker_Bath_Sink_1", (-545.9, 37.2, suite_z - 0.45), 0.25, 0.2, mats['quartz'], col)
    create_cylinder("Parker_Bath_Sink_2", (-545.9, 38.8, suite_z - 0.45), 0.25, 0.2, mats['quartz'], col)


# -------------------------------------------------------------
# Component 3: Third Street Promenade & Inner Parker Quad
# -------------------------------------------------------------
def build_site_and_courtyards(col, mats):
    print("Building Third Street promenade, Starbucks patio terrace, and inner Parker Quad courtyard...")
    
    # ---------------------------------------------------------
    # 1. Third Street Promenade Paving & Pedestrian Corridor
    # ---------------------------------------------------------
    # Spans along the South of the building: X in [-595, -530], Y in [-5, 11]
    p_cx = -562.5
    p_cy = 3.0
    # Main herringbone red brick promenade surface
    create_box("Parker_ThirdSt_Brick_Promenade", (p_cx, p_cy, GROUND_Z + 0.05), (68.0, 16.0, 0.1), mats['paver_brick'], col)
    # Concrete curbs & bands
    create_box("Parker_ThirdSt_Concrete_Curb_South", (p_cx, -4.5, GROUND_Z + 0.15), (68.0, 0.6, 0.3), mats['concrete'], col)
    create_box("Parker_ThirdSt_Concrete_Curb_North", (p_cx, 10.5, GROUND_Z + 0.15), (68.0, 0.6, 0.3), mats['concrete'], col)

    # ---------------------------------------------------------
    # 2. Starbucks Outdoor Dining Patio (Third Street Terrace)
    # ---------------------------------------------------------
    # Located in front of Starbucks: X in [-588, -568], Y in [2, 10]
    patio_cx = -578.0
    patio_cy = 6.0
    # Architectural concrete patio terrace slab
    create_box("Parker_Starbucks_Patio_Slab", (patio_cx, patio_cy, GROUND_Z + 0.08), (20.0, 8.0, 0.15), mats['concrete'], col)

    # 4 Outdoor Teak Dining Tables with Umbrellas
    for idx, tx in enumerate([-585.0, -580.5, -576.0, -571.5]):
        # Table
        create_cylinder(f"Parker_Patio_Table_{idx}", (tx, patio_cy, GROUND_Z + 0.45), 0.6, 0.75, mats['oak'], col)
        # Umbrella pole & canopy in Starbucks forest green
        create_cylinder(f"Parker_Patio_UmbrellaPole_{idx}", (tx, patio_cy, GROUND_Z + 1.4), 0.04, 2.6, mats['bronze'], col)
        create_cylinder(f"Parker_Patio_UmbrellaCanopy_{idx}", (tx, patio_cy, GROUND_Z + 2.5), 1.3, 0.5, mats['starbucks_green'], col)
        # Chairs
        create_cylinder(f"Parker_Patio_ChairA_{idx}", (tx - 0.75, patio_cy, GROUND_Z + 0.25), 0.22, 0.5, mats['bronze'], col)
        create_cylinder(f"Parker_Patio_ChairB_{idx}", (tx + 0.75, patio_cy, GROUND_Z + 0.25), 0.22, 0.5, mats['bronze'], col)

    # Bicycle Parking Bank along Third Street (12 Sheffield bike racks)
    for b in range(10):
        bx = -558.0 + b * 1.5
        create_box(f"Parker_BikeRack_{b}", (bx, 6.0, GROUND_Z + 0.5), (0.1, 1.2, 0.9), mats['bronze'], col)

    # ---------------------------------------------------------
    # 3. Inner Parker Quad Courtyard (Connecting to Frieda Parker Hall)
    # ---------------------------------------------------------
    # Courtyard center: X in [-535, -480], Y in [30, 85]
    quad_cx = -510.0
    quad_cy = 58.0
    # Central manicured lawn panel
    create_box("Parker_Quad_Lawn", (quad_cx, quad_cy, GROUND_Z + 0.06), (36.0, 48.0, 0.1), mats['grass'], col)

    # Curved Precast Concrete Seatwalls with Teak Tops
    # Curved wall arc 1
    create_box("Parker_Quad_Seatwall_1", (quad_cx - 10.0, quad_cy - 12.0, GROUND_Z + 0.3), (16.0, 0.6, 0.6), mats['concrete'], col)
    create_box("Parker_Quad_Seatwall_Top_1", (quad_cx - 10.0, quad_cy - 12.0, GROUND_Z + 0.62), (16.2, 0.8, 0.06), mats['oak'], col)
    # Curved wall arc 2
    create_box("Parker_Quad_Seatwall_2", (quad_cx - 10.0, quad_cy + 12.0, GROUND_Z + 0.3), (16.0, 0.6, 0.6), mats['concrete'], col)
    create_box("Parker_Quad_Seatwall_Top_2", (quad_cx - 10.0, quad_cy + 12.0, GROUND_Z + 0.62), (16.2, 0.8, 0.06), mats['oak'], col)

    # Diagonal Promenade Walkways connecting to Frieda Parker Hall
    create_box("Parker_Quad_Walkway_North", (quad_cx - 8.0, quad_cy + 20.0, GROUND_Z + 0.08), (28.0, 3.5, 0.12), mats['concrete'], col)
    create_box("Parker_Quad_Walkway_South", (quad_cx - 8.0, quad_cy - 20.0, GROUND_Z + 0.08), (28.0, 3.5, 0.12), mats['concrete'], col)

    # 4 Cast-Iron Campus Lantern Posts in Courtyard
    for idx, (lx, ly) in enumerate([(quad_cx - 12.0, quad_cy - 8.0), (quad_cx - 12.0, quad_cy + 8.0), (quad_cx + 8.0, quad_cy - 8.0), (quad_cx + 8.0, quad_cy + 8.0)]):
        create_cylinder(f"Parker_Lantern_Pole_{idx}", (lx, ly, GROUND_Z + 2.0), 0.1, 4.0, mats['bronze'], col)
        create_cylinder(f"Parker_Lantern_Glow_{idx}", (lx, ly, GROUND_Z + 4.1), 0.25, 0.4, mats['warm_glow'], col)


# -------------------------------------------------------------
# Component 4: Calibrate 5 Dedicated Inspection Cameras
# -------------------------------------------------------------
def calibrate_parker_cameras(col):
    print("Calibrating 5 dedicated inspection cameras for Winifred Parker Hall...")
    
    cameras_def = [
        {
            'name': 'Cam_37_Winifred_Parker_ThirdSt_StreetView',
            'loc': (-562.6, -18.0, 4.5),
            'target': (-562.6, 20.0, 8.0),
            'lens': 24.0,
            'desc': 'Street-level view looking north from Third Street at the monumental entrance and Starbucks storefront'
        },
        {
            'name': 'Cam_38_Winifred_Parker_Starbucks_Interior',
            'loc': (-584.0, 14.0, 1.8),
            'target': (-574.0, 22.0, 1.6),
            'lens': 22.0,
            'desc': 'Interior view inside campus Starbucks: barista bar, espresso machines, pastry case, and siren medallion'
        },
        {
            'name': 'Cam_39_Winifred_Parker_Main_Lobby_Interior',
            'loc': (-564.0, 14.0, 1.8),
            'target': (-556.0, 22.0, 1.6),
            'lens': 24.0,
            'desc': 'Interior view inside Main Reception Lobby: terrazzo floor, oak desk, locker wall, and student lounge'
        },
        {
            'name': 'Cam_40_Winifred_Parker_Student_Suite_Interior',
            'loc': (-546.0, 32.0, 6.6),
            'target': (-539.0, 40.0, 5.8),
            'lens': 20.0,
            'desc': 'Interior view inside Floor 2 model suite: common living room, sofa, TV, bedrooms, and vanity bathroom'
        },
        {
            'name': 'Cam_41_Winifred_Parker_Inner_Courtyard',
            'loc': (-495.0, 58.0, 7.5),
            'target': (-542.0, 55.0, 10.0),
            'lens': 26.0,
            'desc': 'Courtyard view from Parker Quad looking at East Wing, 2-story glass lounges, seatwalls, and lawn'
        }
    ]
    
    for cam_info in cameras_def:
        cname = cam_info['name']
        if cname in bpy.data.objects:
            cam_obj = bpy.data.objects[cname]
        else:
            cam_data = bpy.data.cameras.new(cname)
            cam_obj = bpy.data.objects.new(cname, cam_data)
            col.objects.link(cam_obj)
            
        cam_obj.location = cam_info['loc']
        cam_obj.data.lens = cam_info['lens']
        cam_obj.data.clip_end = 2500.0
        
        # Track to target
        t_loc = mathutils.Vector(cam_info['target'])
        c_loc = mathutils.Vector(cam_info['loc'])
        dir_vec = t_loc - c_loc
        rot_quat = dir_vec.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        print(f"  Calibrated camera: {cname} at {cam_obj.location}")


# -------------------------------------------------------------
# Master Execution Flow
# -------------------------------------------------------------
def main():
    print("==================================================")
    print("STARTING WINIFRED PARKER HALL PHOTOREALISTIC BUILD")
    print(f"Center: ({CENTER_X}, {CENTER_Y}), Elevation: {GROUND_Z}")
    print("==================================================")

    # 1. Remove old massing placeholder from 02_Campus_Buildings_Massing if present
    old_obj = bpy.data.objects.get('Winifred Parker Hall')
    if old_obj and '02_Campus_Buildings_Massing' in [c.name for c in old_obj.users_collection]:
        bpy.data.objects.remove(old_obj, do_unlink=True)
        print("  Removed low-poly massing placeholder from 02_Campus_Buildings_Massing")

    # 2. Initialize Collections
    col_ext = get_or_create_col(COL_NAMES['exterior'])
    col_int = get_or_create_col(COL_NAMES['interiors'])
    col_site = get_or_create_col(COL_NAMES['courtyard'])
    col_cams = get_or_create_col(COL_NAMES['cameras'])

    clear_collection_objects(col_ext)
    clear_collection_objects(col_int)
    clear_collection_objects(col_site)

    # 3. Materials
    mats = setup_materials()

    # 4. Build Components
    build_exterior_wings(col_ext, mats)
    build_photorealistic_interiors(col_int, mats)
    build_site_and_courtyards(col_site, mats)

    # 5. Calibrate Cameras
    calibrate_parker_cameras(col_cams)

    # 6. Set Hero Camera Active
    hero_cam = bpy.data.objects.get('Cam_37_Winifred_Parker_ThirdSt_StreetView')
    if hero_cam:
        bpy.context.scene.camera = hero_cam

    print("==================================================")
    print("WINIFRED PARKER HALL MODELING COMPLETE")
    print(f"Exterior Objects: {len(col_ext.objects)}")
    print(f"Interiors Objects: {len(col_int.objects)}")
    print(f"Courtyard & Site Objects: {len(col_site.objects)}")
    print("==================================================")

if __name__ == '__main__':
    main()
