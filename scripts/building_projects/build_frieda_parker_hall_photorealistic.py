"""
Photorealistic Georeferenced Frieda Parker Hall & Restaurant Interiors Script
Purdue University Digital Twin Project
Master Blend: purdue_campus_master.blend

Geospatial Alignment:
- Origin: Purdue Bell Tower (40.4274, -86.9137)
- Center: X = -504.75m, Y = 97.34m (Elevation Z = 0.0m)
- Footprint: 60.9m wide x 99.3m long (OSM Way 886353320)
- Height: 6 stories tall (22.8m parapet, 25.5m penthouses, 570 beds)
- Ground-Floor Restaurants: Chick-fil-A, Jersey Mike's Subs, Central Dining Commons, 2-Story Open-Air Breezeway
"""

import bpy
import bmesh
import mathutils
import math
import os

# -------------------------------------------------------------
# Configuration & Spatial Anchor
# -------------------------------------------------------------
CENTER_X = -504.75
CENTER_Y = 97.34
GROUND_Z = 0.0
BUILDING_H = 22.8

COL_NAMES = {
    'exterior': '30_Frieda_Parker_Hall_Exterior',
    'interiors': '31_Frieda_Parker_Hall_Interiors_and_Dining',
    'courtyard': '32_Frieda_Parker_Hall_Courtyard_and_Site',
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
    mats['brick'] = get_or_create_mat("Frieda_Purdue_Red_Brick", (0.49, 0.16, 0.11, 1.0), roughness=0.85)
    mats['limestone'] = get_or_create_mat("Frieda_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mats['glass'] = get_or_create_mat("Frieda_Solar_Curtain_Glass", (0.02, 0.05, 0.07, 1.0), roughness=0.05, metallic=0.1, transmission=0.88, ior=1.52)
    mats['bronze'] = get_or_create_mat("Frieda_Bronze_Mullion", (0.12, 0.10, 0.08, 1.0), roughness=0.4, metallic=0.85)
    mats['roof'] = get_or_create_mat("Frieda_Roof_Membrane", (0.32, 0.32, 0.31, 1.0), roughness=0.9)
    mats['cfa_red'] = get_or_create_mat("ChickFilA_Red", (0.85, 0.02, 0.05, 1.0), roughness=0.35)
    mats['cfa_logo'] = get_or_create_mat("ChickFilA_Logo_Emissive", (0.95, 0.08, 0.10, 1.0), roughness=0.2, emission=(0.95, 0.08, 0.10, 1.0), emission_str=4.5)
    mats['jm_navy'] = get_or_create_mat("JerseyMikes_Navy", (0.01, 0.08, 0.22, 1.0), roughness=0.35)
    mats['jm_red'] = get_or_create_mat("JerseyMikes_Red", (0.82, 0.10, 0.12, 1.0), roughness=0.4)
    mats['jm_menu'] = get_or_create_mat("JerseyMikes_Menu_Glow", (0.95, 0.95, 0.85, 1.0), roughness=0.2, emission=(0.95, 0.95, 0.85, 1.0), emission_str=4.0)
    mats['terrazzo'] = get_or_create_mat("Dining_Terrazzo_Floor", (0.84, 0.82, 0.76, 1.0), roughness=0.22)
    mats['stainless'] = get_or_create_mat("Dining_Stainless_Steel", (0.85, 0.85, 0.87, 1.0), roughness=0.25, metallic=0.9)
    mats['quartz'] = get_or_create_mat("Dining_White_Quartz", (0.92, 0.92, 0.91, 1.0), roughness=0.25)
    mats['booth_red'] = get_or_create_mat("Dining_Booth_Upholstery", (0.72, 0.15, 0.12, 1.0), roughness=0.5)
    mats['wood'] = get_or_create_mat("Dining_Wood_Furniture", (0.58, 0.40, 0.22, 1.0), roughness=0.45)
    mats['warm_glow'] = get_or_create_mat("Dining_Warm_Ceiling_Glow", (1.0, 0.92, 0.78, 1.0), roughness=0.2, emission=(1.0, 0.92, 0.78, 1.0), emission_str=3.2)
    mats['sign_gold'] = get_or_create_mat("Frieda_Signage_Gold", (0.88, 0.72, 0.28, 1.0), roughness=0.3, metallic=0.85)
    mats['concrete'] = get_or_create_mat("Frieda_Plaza_Concrete", (0.55, 0.55, 0.54, 1.0), roughness=0.8)
    mats['paver_brick'] = get_or_create_mat("Frieda_Plaza_Paver_Brick", (0.46, 0.18, 0.12, 1.0), roughness=0.85)
    mats['wall_ivory'] = get_or_create_mat("Frieda_Wall_Ivory", (0.92, 0.90, 0.85, 1.0), roughness=0.8)
    return mats


# -------------------------------------------------------------
# Component 1: Exterior Wings, Breezeway Portal & Fenestration
# -------------------------------------------------------------
def build_exterior_wings(col, mats):
    print("Building Frieda Parker Hall 6-story exterior wings, breezeway, and fenestration...")
    
    # Building height: 6 stories + parapet = 22.8m
    # Ground floor is Z = 0.0 to 4.2m (hollowed out for dining restaurants and breezeway)
    # Upper floors: Z = 4.2m to 22.8m (height = 18.6m)
    upper_h = 18.6
    upper_z = 4.2 + upper_h * 0.5 # 13.5m

    # 1. East Wing (Monumental Street-Fronting Spine along Russell St / 4th St)
    # Bounds: X in [-495.0, -477.0] (width 18.0m), Y in [48.0, 147.0] (length 99.0m)
    # The East Wing is divided into South-East Wing and North-East Wing by the open-air breezeway at Y in [93.0, 103.0]
    e_cx = (-495.0 + -477.0) / 2.0 # -486.0m
    e_w = 18.0
    
    # South-East Upper Wing: Y in [48.0, 93.0], length 45.0m
    create_box("Frieda_EastWing_Upper_South", (e_cx, 70.5, upper_z), (e_w, 45.0, upper_h), mats['brick'], col)
    # North-East Upper Wing: Y in [103.0, 147.0], length 44.0m
    create_box("Frieda_EastWing_Upper_North", (e_cx, 125.0, upper_z), (e_w, 44.0, upper_h), mats['brick'], col)
    # Breezeway Upper Bridge (Floors 3 to 6 span across the breezeway: Y in [93.0, 103.0], Z in [8.0, 22.8])
    create_box("Frieda_Breezeway_Upper_Bridge", (e_cx, 98.0, 15.4), (e_w, 10.0, 14.8), mats['brick'], col)

    # 2. West Projecting Wing (Facing Parker Quad and Co-Rec)
    # Bounds: X in [-535.2, -495.0] (width 40.2m), Y in [100.5, 120.4] (depth 19.9m)
    w_cx = (-535.2 + -495.0) / 2.0 # -515.1m
    w_cy = (100.5 + 120.4) / 2.0   # 110.45m
    w_w = 40.2
    w_d = 19.9
    create_box("Frieda_WestWing_Upper", (w_cx, w_cy, upper_z), (w_w, w_d, upper_h), mats['brick'], col)

    # 3. North Wing Cap (Projecting West at North Apex)
    # Bounds: X in [-524.7, -495.0], Y in [120.4, 146.6]
    n_cx = (-524.7 + -495.0) / 2.0 # -509.85m
    n_cy = (120.4 + 146.6) / 2.0   # 133.5m
    create_box("Frieda_NorthWing_Upper", (n_cx, n_cy, upper_z), (29.7, 26.2, upper_h), mats['brick'], col)

    # ---------------------------------------------------------
    # 2-Story Open-Air Pedestrian Breezeway Portal (Y in [93.0, 103.0], Z = 0 to 7.8m)
    # ---------------------------------------------------------
    # Signature architectural feature cutting East-West through the building
    # Breezeway floor walkway
    create_box("Frieda_Breezeway_Paved_Floor", (e_cx, 98.0, 0.08), (e_w + 4.0, 10.0, 0.12), mats['concrete'], col)
    # Breezeway 2-story ceiling with recessed downlights
    create_box("Frieda_Breezeway_Ceiling", (e_cx, 98.0, 7.8), (e_w, 10.0, 0.4), mats['limestone'], col)
    # Monumental Limestone Arch Portal Piers (East and West portals)
    create_box("Frieda_Breezeway_Portal_East", (-477.0, 98.0, 4.0), (0.8, 11.2, 8.0), mats['limestone'], col)
    create_box("Frieda_Breezeway_Portal_West", (-495.0, 98.0, 4.0), (0.8, 11.2, 8.0), mats['limestone'], col)
    # Portal Signage Header: "FRIEDA PARKER HALL"
    create_box("Frieda_Breezeway_SignHeader_East", (-476.5, 98.0, 7.6), (0.2, 8.5, 0.8), mats['sign_gold'], col)
    create_box("Frieda_Breezeway_SignHeader_West", (-495.5, 98.0, 7.6), (0.2, 8.5, 0.8), mats['sign_gold'], col)

    # ---------------------------------------------------------
    # Bedford Limestone Water Table & Horizontal Beltcourses
    # ---------------------------------------------------------
    # Ground water table strips along exterior walls (Z = 0 to 1.2m)
    create_box("Frieda_WaterTable_East", (-477.0, 97.5, 0.6), (0.4, 99.0, 1.2), mats['limestone'], col)
    create_box("Frieda_WaterTable_South", (-486.0, 48.0, 0.6), (18.0, 0.4, 1.2), mats['limestone'], col)
    create_box("Frieda_WaterTable_North", (-486.0, 146.8, 0.6), (18.0, 0.4, 1.2), mats['limestone'], col)
    create_box("Frieda_WaterTable_West", (-535.2, 110.5, 0.6), (0.4, 20.0, 1.2), mats['limestone'], col)

    # Horizontal Limestone Beltcourses at floor slabs across all 6 levels
    # Z = 4.2m (floor 2), 7.4m (floor 3), 10.6m (floor 4), 13.8m (floor 5), 17.0m (floor 6), 20.2m (floor 7), 22.8m (parapet coping)
    floors_z = [4.2, 7.4, 10.6, 13.8, 17.0, 20.2, 22.8]
    for idx, fz in enumerate(floors_z):
        is_coping = (idx == len(floors_z) - 1)
        bh = 0.5 if is_coping else 0.35
        # East facade beltcourses
        create_box(f"Frieda_Belt_East_{idx}", (-477.0, 97.5, fz), (0.5, 99.4, bh), mats['limestone'], col)
        # South facade beltcourses
        create_box(f"Frieda_Belt_South_{idx}", (-486.0, 48.0, fz), (18.4, 0.5, bh), mats['limestone'], col)
        # North facade beltcourses
        create_box(f"Frieda_Belt_North_{idx}", (-500.0, 146.8, fz), (46.0, 0.5, bh), mats['limestone'], col)
        # West facade beltcourses
        create_box(f"Frieda_Belt_West_{idx}", (-535.2, 110.5, fz), (0.5, 20.4, bh), mats['limestone'], col)

    # ---------------------------------------------------------
    # Roof Gravel Membrane & HVAC Mechanical Penthouses
    # ---------------------------------------------------------
    create_box("Frieda_Roof_East_South", (e_cx, 70.5, 22.6), (e_w - 0.6, 44.0, 0.3), mats['roof'], col)
    create_box("Frieda_Roof_East_North", (e_cx, 125.0, 22.6), (e_w - 0.6, 43.0, 0.3), mats['roof'], col)
    create_box("Frieda_Roof_West", (w_cx, w_cy, 22.6), (w_w - 0.6, w_d - 0.6, 0.3), mats['roof'], col)

    # 3 Mechanical Penthouses with bronze louvers
    for idx, (px, py, pw, pd) in enumerate([(-486.0, 68.0, 12.0, 7.0), (-486.0, 128.0, 12.0, 7.0), (-515.0, 110.5, 8.0, 12.0)]):
        create_box(f"Frieda_Penthouse_{idx}", (px, py, 24.2), (pw, pd, 3.2), mats['limestone'], col)
        create_box(f"Frieda_Penthouse_Louvers_{idx}", (px, py, 24.2), (pw + 0.2, pd + 0.2, 2.4), mats['bronze'], col)

    # ---------------------------------------------------------
    # Ground Floor Storefront Glazing for Chick-fil-A & Jersey Mike's
    # ---------------------------------------------------------
    # Chick-fil-A East Storefront (Facing Russell St: Y in [52.0, 72.0], Z = 0 to 4.2m)
    create_box("Frieda_ChickFilA_Storefront_Glass", (-476.9, 62.0, 2.2), (0.3, 19.5, 3.4), mats['glass'], col)
    for m in range(6):
        my = 53.0 + m * 3.6
        create_box(f"Frieda_CFA_Mullion_{m}", (-476.8, my, 2.2), (0.4, 0.15, 3.5), mats['bronze'], col)
    # Chick-fil-A Exterior Red Fascia & Script Signage
    create_box("Frieda_CFA_Exterior_Fascia", (-476.7, 62.0, 4.0), (0.4, 20.0, 0.8), mats['cfa_red'], col)
    create_box("Frieda_CFA_Exterior_Sign", (-476.4, 62.0, 4.0), (0.1, 12.0, 0.6), mats['cfa_logo'], col)

    # Jersey Mike's East Storefront (Facing Russell St: Y in [74.0, 92.0], Z = 0 to 4.2m)
    create_box("Frieda_JerseyMikes_Storefront_Glass", (-476.9, 83.0, 2.2), (0.3, 17.5, 3.4), mats['glass'], col)
    for m in range(5):
        my = 75.0 + m * 4.0
        create_box(f"Frieda_JM_Mullion_{m}", (-476.8, my, 2.2), (0.4, 0.15, 3.5), mats['bronze'], col)
    # Jersey Mike's Exterior Navy Fascia & Red Signage
    create_box("Frieda_JM_Exterior_Fascia", (-476.7, 83.0, 4.0), (0.4, 18.0, 0.8), mats['jm_navy'], col)
    create_box("Frieda_JM_Exterior_Sign", (-476.4, 83.0, 4.0), (0.1, 11.0, 0.6), mats['jm_red'], col)

    # ---------------------------------------------------------
    # Upper Levels Rhythmic Fenestration (Floors 2 to 6)
    # ---------------------------------------------------------
    # East Facade Windows (Floors 2 to 6, 20 bays total)
    for floor_idx, fz in enumerate([5.8, 9.0, 12.2, 15.4, 18.6]):
        for bay in range(20):
            wy = 50.0 + bay * 4.6
            # Skip breezeway opening on lower level
            if 93.0 <= wy <= 103.0 and floor_idx == 0:
                continue
            create_box(f"Frieda_Win_East_F{floor_idx}_B{bay}", (-476.9, wy, fz), (0.3, 2.3, 2.1), mats['glass'], col)
            create_box(f"Frieda_Sill_East_F{floor_idx}_B{bay}", (-476.8, wy, fz - 1.15), (0.5, 2.5, 0.25), mats['limestone'], col)
            create_box(f"Frieda_Spandrel_East_F{floor_idx}_B{bay}", (-476.85, wy, fz + 1.25), (0.4, 2.4, 0.4), mats['bronze'], col)

    # West Facade Multi-Story Glass Curtain Wall Study Lounges (Facing Parker Quad)
    # 2-story curtain wall bays at floors 2-3 and floors 4-5
    for l_idx, (lz, lh) in enumerate([(7.4, 5.8), (13.8, 5.8)]):
        create_box(f"Frieda_Curtain_Quad_L{l_idx}", (-535.1, 110.5, lz), (0.3, 16.0, lh), mats['glass'], col)
        for m in range(5):
            my = 104.0 + m * 3.2
            create_box(f"Frieda_Curtain_Quad_Mull_{l_idx}_{m}", (-535.0, my, lz), (0.4, 0.15, lh + 0.2), mats['bronze'], col)


# -------------------------------------------------------------
# Component 2: Finished Restaurants & Food Court Interiors
# -------------------------------------------------------------
def build_restaurant_interiors(col, mats):
    print("Building Chick-fil-A, Jersey Mike's Subs, and Central Dining Commons interiors...")
    
    # Ground floor ceiling slab (Z = 4.2m)
    create_box("Frieda_Ground_Ceiling_Slab", (-486.0, 72.0, 4.1), (18.0, 48.0, 0.2), mats['concrete'], col)
    # Ground floor perimeter interior walls (Ivory)
    create_box("Frieda_Dining_Wall_South", (-486.0, 48.2, 2.1), (17.6, 0.2, 4.0), mats['wall_ivory'], col)
    create_box("Frieda_Dining_Wall_North", (-486.0, 92.8, 2.1), (17.6, 0.2, 4.0), mats['wall_ivory'], col)
    create_box("Frieda_Dining_Wall_West", (-494.8, 70.5, 2.1), (0.2, 44.0, 4.0), mats['wall_ivory'], col)

    # ---------------------------------------------------------
    # 1. CHICK-FIL-A RESTAURANT (Ground Floor South: Y in [49.0, 70.0])
    # ---------------------------------------------------------
    cfa_cy = 58.0
    # Chick-fil-A Terrazzo flooring with red border
    create_box("Frieda_CFA_Floor", (-486.0, cfa_cy, 0.08), (17.0, 18.0, 0.12), mats['terrazzo'], col)

    # Chick-fil-A Service Order Counter (White Quartz Counter with Red Apron)
    # Counter runs North-South at X = -489.0m, Y in [52.0, 64.0] (length 12.0m)
    create_box("Frieda_CFA_Counter_Base", (-489.0, 58.0, 0.65), (1.2, 11.5, 1.05), mats['cfa_red'], col)
    create_box("Frieda_CFA_Counter_Top", (-489.0, 58.0, 1.20), (1.4, 11.8, 0.08), mats['quartz'], col)

    # 3 Touchscreen POS Registers & Mobile Order Pickup Sign
    for r in range(3):
        ry = 54.5 + r * 3.5
        create_box(f"Frieda_CFA_POS_{r}", (-488.9, ry, 1.48), (0.4, 0.45, 0.4), mats['bronze'], col)
    create_box("Frieda_CFA_MobilePickup_Sign", (-488.9, 63.5, 1.55), (0.3, 1.2, 0.45), mats['cfa_logo'], col)

    # Commercial Kitchen Behind Counter (X in [-494.5, -490.5])
    # Commercial Pressure Fryers & Open Fryers (Stainless Steel)
    create_box("Frieda_CFA_Fryers_Bank", (-492.5, 54.5, 0.65), (1.1, 4.2, 1.1), mats['stainless'], col)
    # Stainless Steel Chicken Holding Warming Chutes
    create_box("Frieda_CFA_WarmingChutes", (-491.5, 58.0, 1.1), (0.9, 3.8, 0.8), mats['stainless'], col)
    # Waffle Potato Fry Station & Bun Toaster
    create_box("Frieda_CFA_FryStation", (-492.5, 62.0, 0.65), (1.1, 3.0, 1.1), mats['stainless'], col)

    # Dual Multi-Flavor Soda Fountain Towers
    create_box("Frieda_CFA_SodaTower_1", (-488.8, 52.0, 1.55), (0.6, 0.8, 0.7), mats['stainless'], col)
    create_box("Frieda_CFA_SodaTower_2", (-488.8, 64.0, 1.55), (0.6, 0.8, 0.7), mats['stainless'], col)

    # 4 Overhead Digital Menu Screens (Showing Sandwiches, Nuggets, Waffle Fries)
    for idx in range(4):
        my = 54.5 + idx * 2.4
        create_box(f"Frieda_CFA_MenuScreen_{idx}", (-489.0, my, 2.9), (0.08, 2.0, 1.0), mats['warm_glow'], col)
        create_box(f"Frieda_CFA_MenuFrame_{idx}", (-489.0, my, 2.9), (0.10, 2.1, 1.1), mats['cfa_red'], col)

    # Chick-fil-A Signature Feature Wall & Script Logo
    create_box("Frieda_CFA_FeatureWall", (-494.6, cfa_cy, 2.1), (0.2, 18.0, 4.0), mats['cfa_red'], col)
    create_box("Frieda_CFA_Script_Logo", (-494.4, cfa_cy, 2.5), (0.08, 8.5, 1.4), mats['cfa_logo'], col)

    # Chick-fil-A Dining Section (Red Upholstered Booths & Laminate Tables)
    for b in range(3):
        by = 53.0 + b * 4.5
        # Red booth seats
        create_box(f"Frieda_CFA_Booth_Bench1_{b}", (-483.0, by - 1.0, 0.5), (2.4, 0.7, 0.85), mats['booth_red'], col)
        create_box(f"Frieda_CFA_Booth_Bench2_{b}", (-483.0, by + 1.0, 0.5), (2.4, 0.7, 0.85), mats['booth_red'], col)
        # Dining table
        create_box(f"Frieda_CFA_Booth_Table_{b}", (-483.0, by, 0.45), (2.2, 0.9, 0.75), mats['wood'], col)

    # ---------------------------------------------------------
    # 2. JERSEY MIKE'S SUBS (Ground Floor North: Y in [72.0, 92.0])
    # ---------------------------------------------------------
    jm_cy = 82.0
    # Flooring
    create_box("Frieda_JM_Floor", (-486.0, jm_cy, 0.08), (17.0, 19.0, 0.12), mats['terrazzo'], col)

    # Jersey Mike's Deli Assembly Counter (Navy Blue Base, Quartz Top, Glass Sneeze Guard)
    # Runs North-South at X = -489.0m, Y in [75.0, 87.0] (length 12.0m)
    create_box("Frieda_JM_Counter_Base", (-489.0, 81.0, 0.65), (1.2, 11.5, 1.05), mats['jm_navy'], col)
    create_box("Frieda_JM_Counter_Top", (-489.0, 81.0, 1.20), (1.4, 11.8, 0.08), mats['quartz'], col)
    # Glass sneeze guard
    create_box("Frieda_JM_SneezeGuard", (-488.5, 81.0, 1.55), (0.1, 11.2, 0.6), mats['glass'], col)

    # Meat & Cheese Deli Slicer Station
    create_box("Frieda_JM_DeliSlicer", (-489.0, 76.5, 1.48), (0.8, 0.9, 0.5), mats['stainless'], col)
    # Sub Assembly Sandwich Prep Pans (Lettuce, tomato, oil & vinegar bottles)
    create_box("Frieda_JM_SubPrepPans", (-489.0, 80.5, 1.28), (0.7, 4.5, 0.15), mats['stainless'], col)
    # Touch POS checkout registers
    create_box("Frieda_JM_POS_1", (-488.9, 85.0, 1.48), (0.4, 0.45, 0.4), mats['bronze'], col)
    create_box("Frieda_JM_POS_2", (-488.9, 86.5, 1.48), (0.4, 0.45, 0.4), mats['bronze'], col)

    # Wire Chips Display Rack & Fountain Beverage Station
    create_box("Frieda_JM_ChipsRack", (-488.8, 74.0, 1.1), (0.7, 1.8, 1.8), mats['bronze'], col)
    create_box("Frieda_JM_DrinkDispenser", (-488.8, 72.5, 1.45), (0.8, 1.2, 0.9), mats['stainless'], col)

    # Overhead Sub Menu Boards (Deep Navy Blue & Red Trim with Illumination)
    for idx in range(3):
        my = 78.0 + idx * 3.0
        create_box(f"Frieda_JM_MenuBoard_{idx}", (-489.0, my, 2.9), (0.08, 2.6, 1.0), mats['jm_menu'], col)
        create_box(f"Frieda_JM_MenuFrame_{idx}", (-489.0, my, 2.9), (0.10, 2.7, 1.1), mats['jm_navy'], col)

    # Jersey Mike's Feature Wall (Navy with Surfboard & Red Brand Script)
    create_box("Frieda_JM_FeatureWall", (-494.6, jm_cy, 2.1), (0.2, 19.0, 4.0), mats['jm_navy'], col)
    create_box("Frieda_JM_BrandLogo", (-494.4, jm_cy, 2.6), (0.08, 7.5, 1.2), mats['jm_red'], col)
    create_box("Frieda_JM_Surfboard_Graphic", (-494.4, jm_cy - 4.5, 2.0), (0.08, 0.6, 2.8), mats['quartz'], col)

    # Jersey Mike's Dining Tables & Seating
    for b in range(3):
        by = 76.0 + b * 4.5
        create_box(f"Frieda_JM_DiningTable_{b}", (-483.0, by, 0.45), (2.0, 1.0, 0.75), mats['wood'], col)
        # Chairs on both sides
        for c in range(2):
            create_box(f"Frieda_JM_ChairA_{b}_{c}", (-484.2, by - 0.35 + c * 0.7, 0.45), (0.45, 0.45, 0.8), mats['bronze'], col)
            create_box(f"Frieda_JM_ChairB_{b}_{c}", (-481.8, by - 0.35 + c * 0.7, 0.45), (0.45, 0.45, 0.8), mats['bronze'], col)

    # ---------------------------------------------------------
    # 3. CENTRAL DINING COMMONS / FOOD COURT SEATING HUB
    # ---------------------------------------------------------
    # High-traffic student food court seating along the east glass facade (X in [-485.0, -478.0], Y in [60.0, 85.0])
    # Central Bar-Height Community Table (X = -481.0, Y in [66.0, 78.0], length 12.0m)
    create_box("Frieda_Commons_CommTable_Base", (-480.0, 72.0, 0.62), (1.1, 10.0, 1.05), mats['bronze'], col)
    create_box("Frieda_Commons_CommTable_Top", (-480.0, 72.0, 1.18), (1.3, 10.2, 0.08), mats['wood'], col)
    for s in range(8):
        sy = 67.5 + s * 1.3
        create_cylinder(f"Frieda_Commons_Stool_E_{s}", (-479.0, sy, 0.42), 0.22, 0.75, mats['bronze'], col)
        create_cylinder(f"Frieda_Commons_Stool_W_{s}", (-481.0, sy, 0.42), 0.22, 0.75, mats['bronze'], col)

    # Trash / Recycling / Liquid Compost Station
    create_box("Frieda_Waste_Station", (-485.5, 71.0, 0.7), (1.4, 2.4, 1.3), mats['stainless'], col)


# -------------------------------------------------------------
# Component 3: Courtyard, Site & Breezeway Hardscaping
# -------------------------------------------------------------
def build_site_and_courtyards(col, mats):
    print("Building Frieda Parker Hall outdoor dining terrace, breezeway promenade, and quad integration...")
    
    # ---------------------------------------------------------
    # 1. Russell Street Outdoor Dining Terrace (East of building: X in [-477.0, -468.0], Y in [50.0, 95.0])
    # ---------------------------------------------------------
    t_cx = -472.5
    t_cy = 72.5
    # Architectural concrete outdoor patio terrace slab
    create_box("Frieda_Outdoor_Patio_Slab", (t_cx, t_cy, GROUND_Z + 0.08), (8.5, 46.0, 0.12), mats['concrete'], col)

    # 6 Outdoor Dining Tables with Umbrellas (3 for Chick-fil-A in Red, 3 for Jersey Mike's in Navy)
    for idx, (ty, u_mat) in enumerate([(56.0, mats['cfa_red']), (62.0, mats['cfa_red']), (68.0, mats['cfa_red']),
                                        (76.0, mats['jm_navy']), (82.0, mats['jm_navy']), (88.0, mats['jm_navy'])]):
        create_cylinder(f"Frieda_Patio_Table_{idx}", (t_cx, ty, GROUND_Z + 0.45), 0.6, 0.75, mats['wood'], col)
        create_cylinder(f"Frieda_Patio_Pole_{idx}", (t_cx, ty, GROUND_Z + 1.4), 0.04, 2.6, mats['bronze'], col)
        create_cylinder(f"Frieda_Patio_Canopy_{idx}", (t_cx, ty, GROUND_Z + 2.5), 1.3, 0.5, u_mat, col)
        # Chairs
        create_cylinder(f"Frieda_Patio_ChairA_{idx}", (t_cx - 0.75, ty, GROUND_Z + 0.25), 0.22, 0.5, mats['bronze'], col)
        create_cylinder(f"Frieda_Patio_ChairB_{idx}", (t_cx + 0.75, ty, GROUND_Z + 0.25), 0.22, 0.5, mats['bronze'], col)

    # Sheffield Bicycle Parking Bank along Russell Street
    for b in range(12):
        by = 52.0 + b * 1.5
        create_box(f"Frieda_BikeRack_{b}", (-467.5, by, GROUND_Z + 0.5), (0.1, 1.2, 0.9), mats['bronze'], col)

    # ---------------------------------------------------------
    # 2. Breezeway Pedestrian Connecting Promenade (East-West Promenade)
    # ---------------------------------------------------------
    # Spans from Russell Street (X = -465) through the breezeway (X = -486) into the Parker Quad (X = -505)
    create_box("Frieda_Breezeway_Connector_Path", (-485.0, 98.0, GROUND_Z + 0.06), (42.0, 8.0, 0.1), mats['paver_brick'], col)


# -------------------------------------------------------------
# Component 4: Calibrate 5 Dedicated Inspection Cameras
# -------------------------------------------------------------
def calibrate_frieda_cameras(col):
    print("Calibrating 5 dedicated inspection cameras for Frieda Parker Hall...")
    
    cameras_def = [
        {
            'name': 'Cam_42_Frieda_Parker_East_StreetView',
            'loc': (-458.0, 85.0, 5.5),
            'target': (-486.0, 90.0, 10.0),
            'lens': 24.0,
            'desc': 'Street view looking west from Russell Street at Frieda Parker Hall, restaurant storefronts, and breezeway'
        },
        {
            'name': 'Cam_43_Frieda_Parker_ChickFilA_Interior',
            'loc': (-482.0, 52.0, 1.6),
            'target': (-491.0, 59.0, 1.5),
            'lens': 22.0,
            'desc': 'Interior view inside Chick-fil-A: red service counter, POS terminals, fryers, menu screens, and logo'
        },
        {
            'name': 'Cam_44_Frieda_Parker_JerseyMikes_Interior',
            'loc': (-482.0, 88.0, 1.6),
            'target': (-491.0, 81.0, 1.5),
            'lens': 22.0,
            'desc': 'Interior view inside Jersey Mike\'s Subs: sub assembly line, deli slicer, menu boards, and navy feature wall'
        },
        {
            'name': 'Cam_45_Frieda_Parker_Dining_Commons_Interior',
            'loc': (-479.0, 60.0, 1.7),
            'target': (-481.0, 75.0, 1.4),
            'lens': 22.0,
            'desc': 'Interior view of central dining commons: terrazzo floor, community high-top table, booths, and food court'
        },
        {
            'name': 'Cam_46_Frieda_Parker_Breezeway_Portal',
            'loc': (-468.0, 98.0, 2.5),
            'target': (-490.0, 98.0, 4.0),
            'lens': 24.0,
            'desc': 'Eye-level perspective looking straight through the signature 2-story open-air pedestrian breezeway portal'
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
    print("STARTING FRIEDA PARKER HALL PHOTOREALISTIC BUILD")
    print(f"Center: ({CENTER_X}, {CENTER_Y}), Elevation: {GROUND_Z}")
    print("==================================================")

    # 1. Remove old massing placeholder from 02_Campus_Buildings_Massing if present
    old_obj = bpy.data.objects.get('Frieda Parker Hall')
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
    build_restaurant_interiors(col_int, mats)
    build_site_and_courtyards(col_site, mats)

    # 5. Calibrate Cameras
    calibrate_frieda_cameras(col_cams)

    # 6. Set Hero Camera Active
    hero_cam = bpy.data.objects.get('Cam_42_Frieda_Parker_East_StreetView')
    if hero_cam:
        bpy.context.scene.camera = hero_cam

    print("==================================================")
    print("FRIEDA PARKER HALL MODELING COMPLETE")
    print(f"Exterior Objects: {len(col_ext.objects)}")
    print(f"Interiors Objects: {len(col_int.objects)}")
    print(f"Courtyard & Site Objects: {len(col_site.objects)}")
    print("==================================================")

if __name__ == '__main__':
    main()
