"""
Photorealistic Georeferenced Ross-Ade Stadium Construction Script
Purdue University Digital Twin Project
Master Blend: purdue_campus_master.blend

Geospatial Alignment:
- Origin: Purdue Bell Tower (40.4274, -86.9137)
- Stadium Center: X = -403.2m, Y = 805.2m
- Real Footprint: 217.1m wide x 295.5m long (OSM Way 614516704)
- Field Orientation: North-South
"""

import bpy
import bmesh
import mathutils
import math
import os

# -------------------------------------------------------------
# Configuration & Spatial Anchor
# -------------------------------------------------------------
CENTER_X = -403.2
CENTER_Y = 805.2
FIELD_Z = 0.0

# Collections
COL_NAMES = {
    'field_bowl': '23_Ross_Ade_Field_and_Bowl',
    'pavilion': '24_Ross_Ade_West_Pavilion_and_Suites',
    'south_endzone': '25_Ross_Ade_South_Endzone_Renovation',
    'exterior_site': '26_Ross_Ade_Gates_Lighting_and_Site',
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

def setup_stadium_materials():
    mats = {}
    mats['turf'] = get_or_create_mat("RossAde_Turf_Green", (0.04, 0.16, 0.03, 1.0), roughness=0.88)
    mats['endzone_gold'] = get_or_create_mat("RossAde_Endzone_Gold", (0.78, 0.63, 0.35, 1.0), roughness=0.7)
    mats['endzone_letter'] = get_or_create_mat("RossAde_Endzone_Letter_Black", (0.02, 0.02, 0.02, 1.0), roughness=0.6)
    mats['markings'] = get_or_create_mat("RossAde_Field_Markings_White", (0.95, 0.95, 0.95, 1.0), roughness=0.5)
    mats['goalpost'] = get_or_create_mat("RossAde_Goalpost_Yellow", (0.96, 0.74, 0.05, 1.0), roughness=0.35, metallic=0.15)
    mats['concrete'] = get_or_create_mat("RossAde_Concrete_Structure", (0.44, 0.44, 0.43, 1.0), roughness=0.82)
    mats['seat_gold'] = get_or_create_mat("RossAde_Seat_Gold", (0.80, 0.64, 0.26, 1.0), roughness=0.42, metallic=0.08)
    mats['seat_black'] = get_or_create_mat("RossAde_Seat_Black", (0.03, 0.03, 0.03, 1.0), roughness=0.45)
    mats['seat_bleacher'] = get_or_create_mat("RossAde_Bleachers_Aluminum", (0.72, 0.72, 0.74, 1.0), roughness=0.35, metallic=0.75)
    mats['brick'] = get_or_create_mat("RossAde_Purdue_Red_Brick", (0.47, 0.15, 0.10, 1.0), roughness=0.85)
    mats['limestone'] = get_or_create_mat("RossAde_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mats['glass'] = get_or_create_mat("RossAde_Solar_Ribbon_Glass", (0.02, 0.05, 0.07, 1.0), roughness=0.06, metallic=0.1, transmission=0.88, ior=1.52)
    mats['dark_metal'] = get_or_create_mat("RossAde_Steel_Lattice_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.45, metallic=0.85)
    mats['screen_led'] = get_or_create_mat("RossAde_Rohrman_Screen_LED", (0.92, 0.85, 0.65, 1.0), roughness=0.2, emission=(0.95, 0.88, 0.70, 1.0), emission_str=4.5)
    mats['wordmark_gold'] = get_or_create_mat("RossAde_Wordmark_Gold_Emissive", (0.85, 0.68, 0.32, 1.0), roughness=0.3, emission=(0.90, 0.75, 0.35, 1.0), emission_str=3.0)
    mats['banner_gold'] = get_or_create_mat("RossAde_Championship_Banner_Gold", (0.76, 0.59, 0.20, 1.0), roughness=0.7)
    mats['floodlight_glow'] = get_or_create_mat("RossAde_Floodlight_Head_Emissive", (1.0, 0.98, 0.92, 1.0), roughness=0.1, emission=(1.0, 0.98, 0.92, 1.0), emission_str=20.0)
    mats['pavement'] = get_or_create_mat("RossAde_Plaza_Brick_Pavers", (0.52, 0.22, 0.14, 1.0), roughness=0.8)
    return mats

# -------------------------------------------------------------
# Component 1: Field of Play & Goalposts (Rohrman Field)
# -------------------------------------------------------------
def build_rohrman_field(col, mats):
    print("Building Rohrman Field playing surface...")
    
    # 1. Total Turf Apron (64m wide x 130m long)
    apron = create_box(
        "RossAde_Field_Turf_Apron",
        (CENTER_X, CENTER_Y, FIELD_Z + 0.05),
        (66.0, 130.0, 0.1),
        mats['turf'],
        col
    )
    
    # 2. Main Field of Play (48.76m wide x 91.44m long)
    # Spans from Y = CENTER_Y - 45.72 to CENTER_Y + 45.72 (Y: 759.48 to 850.92)
    play_field = create_box(
        "RossAde_Field_Of_Play_Turf",
        (CENTER_X, CENTER_Y, FIELD_Z + 0.1),
        (48.76, 91.44, 0.08),
        mats['turf'],
        col
    )
    
    # 3. South Endzone (Y: 750.34 to 759.48, width 48.76, length 9.14)
    south_ez = create_box(
        "RossAde_South_Endzone_Purdue_Gold",
        (CENTER_X, CENTER_Y - 50.29, FIELD_Z + 0.11),
        (48.76, 9.14, 0.08),
        mats['endzone_gold'],
        col
    )
    
    # South Endzone Lettering "PURDUE" Block Elements
    # 6 block letters: P, U, R, D, U, E
    letter_w = 4.2
    letter_h = 5.8
    spacing = 6.8
    for i, char in enumerate(['P', 'U', 'R', 'D', 'U', 'E']):
        lx = CENTER_X - 17.0 + i * spacing
        ly = CENTER_Y - 50.29
        create_box(
            f"RossAde_South_EZ_Letter_{char}_{i}",
            (lx, ly, FIELD_Z + 0.16),
            (letter_w, letter_h, 0.04),
            mats['endzone_letter'],
            col
        )
    
    # 4. North Endzone (Y: 850.92 to 860.06, width 48.76, length 9.14)
    north_ez = create_box(
        "RossAde_North_Endzone_Boilermakers_Gold",
        (CENTER_X, CENTER_Y + 50.29, FIELD_Z + 0.11),
        (48.76, 9.14, 0.08),
        mats['endzone_gold'],
        col
    )
    
    # North Endzone Lettering "BOILERMAKERS" / "PURDUE"
    for i, char in enumerate(['P', 'U', 'R', 'D', 'U', 'E']):
        lx = CENTER_X - 17.0 + i * spacing
        ly = CENTER_Y + 50.29
        create_box(
            f"RossAde_North_EZ_Letter_{char}_{i}",
            (lx, ly, FIELD_Z + 0.16),
            (letter_w, letter_h, 0.04),
            mats['endzone_letter'],
            col
        )
        
    # 5. Midfield Giant Motion 'P' Logo (Center at 805.2, -403.2)
    # Outer gold P block (12m x 15m), inner black accents
    create_box(
        "RossAde_Midfield_Motion_P_Backing",
        (CENTER_X, CENTER_Y, FIELD_Z + 0.13),
        (13.5, 16.5, 0.04),
        mats['endzone_letter'],
        col
    )
    create_box(
        "RossAde_Midfield_Motion_P_Gold_Face",
        (CENTER_X, CENTER_Y, FIELD_Z + 0.16),
        (11.8, 14.8, 0.04),
        mats['endzone_gold'],
        col
    )
    # Inner cutout to sculpt the 'P' loop
    create_box(
        "RossAde_Midfield_Motion_P_Loop_Cut",
        (CENTER_X + 1.8, CENTER_Y + 2.2, FIELD_Z + 0.18),
        (4.2, 5.2, 0.04),
        mats['turf'],
        col
    )
    
    # 6. Yard Lines (Every 5 yards = 4.572m, total 19 lines from Y=-41.15 to +41.15)
    for i in range(-9, 10):
        y_pos = CENTER_Y + i * 4.572
        line_thick = 0.25 if i != 0 else 0.45
        create_box(
            f"RossAde_YardLine_{i*5}",
            (CENTER_X, y_pos, FIELD_Z + 0.14),
            (48.76, line_thick, 0.03),
            mats['markings'],
            col
        )
        # Side numbers (10, 20, 30, 40, 50, etc.)
        if i in [-8, -6, -4, -2, 0, 2, 4, 6, 8]:
            # West sideline numbers
            create_box(
                f"RossAde_YardNumber_West_{i*5}",
                (CENTER_X - 16.5, y_pos, FIELD_Z + 0.15),
                (1.8, 2.4, 0.02),
                mats['markings'],
                col
            )
            # East sideline numbers
            create_box(
                f"RossAde_YardNumber_East_{i*5}",
                (CENTER_X + 16.5, y_pos, FIELD_Z + 0.15),
                (1.8, 2.4, 0.02),
                mats['markings'],
                col
            )
            
    # Sideline continuous white boundary stripes (West & East)
    create_box(
        "RossAde_Sideline_Stripe_West",
        (CENTER_X - 24.38, CENTER_Y, FIELD_Z + 0.14),
        (1.2, 109.73, 0.03),
        mats['markings'],
        col
    )
    create_box(
        "RossAde_Sideline_Stripe_East",
        (CENTER_X + 24.38, CENTER_Y, FIELD_Z + 0.14),
        (1.2, 109.73, 0.03),
        mats['markings'],
        col
    )
    # Endline continuous white boundary stripes (South & North)
    create_box(
        "RossAde_Endline_Stripe_South",
        (CENTER_X, CENTER_Y - 54.86, FIELD_Z + 0.14),
        (49.96, 1.2, 0.03),
        mats['markings'],
        col
    )
    create_box(
        "RossAde_Endline_Stripe_North",
        (CENTER_X, CENTER_Y + 54.86, FIELD_Z + 0.14),
        (49.96, 1.2, 0.03),
        mats['markings'],
        col
    )
    
    # 7. NCAA Regulation Slingshot Goalposts (South & North Endlines)
    # Gooseneck post: Z: 0 to 3.05m, horizontal gooseneck 1.8m, crossbar 5.64m wide, uprights 9.14m tall
    for end_name, y_endline, y_dir in [("South", CENTER_Y - 54.86, -1.0), ("North", CENTER_Y + 54.86, 1.0)]:
        # Base pad (cylinder)
        create_cylinder(
            f"RossAde_Goalpost_{end_name}_Pad",
            (CENTER_X, y_endline + y_dir * 1.8, FIELD_Z + 0.9),
            0.35, 1.8,
            mats['goalpost'],
            col
        )
        # Main vertical post
        create_cylinder(
            f"RossAde_Goalpost_{end_name}_Mast",
            (CENTER_X, y_endline + y_dir * 1.8, FIELD_Z + 1.8),
            0.15, 3.6,
            mats['goalpost'],
            col
        )
        # Gooseneck arm extending to endline
        create_box(
            f"RossAde_Goalpost_{end_name}_Gooseneck",
            (CENTER_X, y_endline + y_dir * 0.9, FIELD_Z + 3.05),
            (0.28, 1.9, 0.28),
            mats['goalpost'],
            col
        )
        # Crossbar (5.64m wide at Z = 3.05m exactly over endline)
        create_box(
            f"RossAde_Goalpost_{end_name}_Crossbar",
            (CENTER_X, y_endline, FIELD_Z + 3.05),
            (5.64, 0.24, 0.24),
            mats['goalpost'],
            col
        )
        # West & East Uprights (9.14m tall)
        create_cylinder(
            f"RossAde_Goalpost_{end_name}_Upright_West",
            (CENTER_X - 2.82, y_endline, FIELD_Z + 3.05 + 4.57),
            0.12, 9.14,
            mats['goalpost'],
            col
        )
        create_cylinder(
            f"RossAde_Goalpost_{end_name}_Upright_East",
            (CENTER_X + 2.82, y_endline, FIELD_Z + 3.05 + 4.57),
            0.12, 9.14,
            mats['goalpost'],
            col
        )
        # Netting support stanchions behind goalpost
        create_box(
            f"RossAde_Netting_Support_{end_name}",
            (CENTER_X, y_endline + y_dir * 6.0, FIELD_Z + 7.5),
            (16.0, 0.3, 15.0),
            mats['dark_metal'],
            col
        )
        
    # 8. Team Benches & Sideline Amenities
    # Home Sideline (West, X = CENTER_X - 28.0m)
    create_box(
        "RossAde_Home_Team_Bench_West",
        (CENTER_X - 28.5, CENTER_Y, FIELD_Z + 0.5),
        (1.2, 38.0, 0.6),
        mats['seat_gold'],
        col
    )
    create_box(
        "RossAde_Home_Coaching_Box_West",
        (CENTER_X - 27.0, CENTER_Y, FIELD_Z + 0.12),
        (3.0, 48.0, 0.05),
        mats['markings'],
        col
    )
    # Visitor Sideline (East, X = CENTER_X + 28.0m)
    create_box(
        "RossAde_Visitor_Team_Bench_East",
        (CENTER_X + 28.5, CENTER_Y, FIELD_Z + 0.5),
        (1.2, 38.0, 0.6),
        mats['seat_black'],
        col
    )
    create_box(
        "RossAde_Visitor_Coaching_Box_East",
        (CENTER_X + 27.0, CENTER_Y, FIELD_Z + 0.12),
        (3.0, 48.0, 0.05),
        mats['markings'],
        col
    )
    
    # 8 Corner Pylons (Orange/Gold markers)
    pylon_mat = mats['goalpost']
    pylon_coords = [
        (CENTER_X - 24.38, CENTER_Y - 54.86),
        (CENTER_X + 24.38, CENTER_Y - 54.86),
        (CENTER_X - 24.38, CENTER_Y - 45.72),
        (CENTER_X + 24.38, CENTER_Y - 45.72),
        (CENTER_X - 24.38, CENTER_Y + 45.72),
        (CENTER_X + 24.38, CENTER_Y + 45.72),
        (CENTER_X - 24.38, CENTER_Y + 54.86),
        (CENTER_X + 24.38, CENTER_Y + 54.86),
    ]
    for idx, (px, py) in enumerate(pylon_coords):
        create_box(
            f"RossAde_Pylon_{idx}",
            (px, py, FIELD_Z + 0.25),
            (0.18, 0.18, 0.45),
            pylon_mat,
            col
        )


# -------------------------------------------------------------
# Component 2: The Horseshoe Bowl (Lower, Concourse, Upper Tiers)
# -------------------------------------------------------------
def build_horseshoe_bowl(col, mats):
    print("Building Ross-Ade Stadium horseshoe bowl seating grandstand...")
    
    # 1. Lower Bowl Stepped Tiers (East and West sidelines)
    # Slopes from field perimeter (X = ±30m, Z = 0.8m) to concourse (X = ±58m, Z = 9.2m)
    # 18 distinct seating tiers on each sideline
    tier_count_lower = 18
    dx_lower = (58.0 - 30.0) / tier_count_lower # ~1.55m per tier
    dz_lower = (9.2 - 0.8) / tier_count_lower   # ~0.46m per tier
    
    for i in range(tier_count_lower):
        z_t = 0.8 + i * dz_lower
        w_t = dx_lower * 1.05
        # West Sideline Lower Tier
        x_w = CENTER_X - (30.0 + i * dx_lower)
        # Alternate seat colors (Gold and Black sections)
        seat_mat = mats['seat_gold'] if (i // 3) % 2 == 0 else mats['seat_black']
        
        # Concrete riser slab
        create_box(
            f"RossAde_LowerBowl_West_Riser_{i}",
            (x_w, CENTER_Y, z_t),
            (w_t, 114.0, dz_lower),
            mats['concrete'],
            col
        )
        # Seating rows on top of riser
        create_box(
            f"RossAde_LowerBowl_West_Seats_{i}",
            (x_w, CENTER_Y, z_t + dz_lower * 0.5 + 0.22),
            (w_t * 0.75, 112.0, 0.40),
            seat_mat,
            col
        )
        
        # East Sideline Lower Tier
        x_e = CENTER_X + (30.0 + i * dx_lower)
        create_box(
            f"RossAde_LowerBowl_East_Riser_{i}",
            (x_e, CENTER_Y, z_t),
            (w_t, 114.0, dz_lower),
            mats['concrete'],
            col
        )
        create_box(
            f"RossAde_LowerBowl_East_Seats_{i}",
            (x_e, CENTER_Y, z_t + dz_lower * 0.5 + 0.22),
            (w_t * 0.75, 112.0, 0.40),
            seat_mat,
            col
        )
        
    # 2. North Horseshoe Curve (Semicircular curve connecting East and West)
    # Radii from R_inner = 30m to R_outer = 60m, spanning angle from 0 to 180 degrees (North half)
    segments = 36
    d_theta = math.pi / segments
    for s in range(segments):
        theta = s * d_theta
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        # North curve center is at CENTER_X, CENTER_Y + 45.0m
        arc_y_center = CENTER_Y + 48.0
        
        for i in range(0, tier_count_lower, 2):
            r = 30.0 + i * dx_lower
            z_t = 0.8 + i * dz_lower
            px = CENTER_X - r * cos_t
            py = arc_y_center + r * sin_t
            
            # Semicircular wedge block
            wedge = create_box(
                f"RossAde_NorthCurve_Lower_S{s}_T{i}",
                (px, py, z_t),
                (dx_lower * 2.2, r * d_theta * 1.15, dz_lower * 2.0),
                mats['concrete'],
                col
            )
            wedge.rotation_euler[2] = -theta
            
            # Bleachers for North Student Section
            bleach = create_box(
                f"RossAde_NorthCurve_Bleacher_S{s}_T{i}",
                (px, py, z_t + dz_lower + 0.2),
                (dx_lower * 1.8, r * d_theta * 1.1, 0.35),
                mats['seat_bleacher'],
                col
            )
            bleach.rotation_euler[2] = -theta

    # 3. Mid-Concourse Ring Walkway & Vomitory Tunnels (Z = 9.2m to 10.2m)
    # West concourse
    create_box(
        "RossAde_Concourse_Walkway_West",
        (CENTER_X - 60.5, CENTER_Y, 9.2),
        (5.0, 120.0, 0.4),
        mats['concrete'],
        col
    )
    # East concourse
    create_box(
        "RossAde_Concourse_Walkway_East",
        (CENTER_X + 60.5, CENTER_Y, 9.2),
        (5.0, 120.0, 0.4),
        mats['concrete'],
        col
    )
    # North curve concourse
    for s in range(0, segments, 2):
        theta = s * d_theta
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        px = CENTER_X - 60.5 * cos_t
        py = CENTER_Y + 48.0 + 60.5 * sin_t
        c_block = create_box(
            f"RossAde_Concourse_North_S{s}",
            (px, py, 9.2),
            (5.5, 60.5 * d_theta * 2.2, 0.4),
            mats['concrete'],
            col
        )
        c_block.rotation_euler[2] = -theta

    # 12 Vomitory Portals (Tunnels cutting through lower bowl to concourses)
    # 5 on West, 5 on East, 2 on North
    for idx, vy in enumerate([-40.0, -20.0, 0.0, 20.0, 40.0]):
        # West portal
        create_box(
            f"RossAde_Vomitory_West_{idx}",
            (CENTER_X - 48.0, CENTER_Y + vy, 5.5),
            (22.0, 3.6, 3.2),
            mats['dark_metal'],
            col
        )
        # Portal opening arch frame
        create_box(
            f"RossAde_Vomitory_West_Arch_{idx}",
            (CENTER_X - 37.0, CENTER_Y + vy, 4.0),
            (1.2, 4.2, 3.8),
            mats['limestone'],
            col
        )
        # East portal
        create_box(
            f"RossAde_Vomitory_East_{idx}",
            (CENTER_X + 48.0, CENTER_Y + vy, 5.5),
            (22.0, 3.6, 3.2),
            mats['dark_metal'],
            col
        )
        create_box(
            f"RossAde_Vomitory_East_Arch_{idx}",
            (CENTER_X + 37.0, CENTER_Y + vy, 4.0),
            (1.2, 4.2, 3.8),
            mats['limestone'],
            col
        )
        
    # 4. Upper Bowl Grandstand Tiers (Slopes from Z = 9.8m to Z = 23.5m)
    # East Upper Deck (Extends out to X = CENTER_X + 88.0m)
    tier_count_upper = 22
    dx_upper = (88.0 - 63.0) / tier_count_upper # ~1.14m per tier
    dz_upper = (23.5 - 9.8) / tier_count_upper   # ~0.62m per tier
    
    for i in range(tier_count_upper):
        z_t = 9.8 + i * dz_upper
        w_t = dx_upper * 1.05
        seat_mat = mats['seat_gold'] if (i // 4) % 2 == 1 else mats['seat_black']
        
        # East Upper Deck Tier
        x_e = CENTER_X + (63.0 + i * dx_upper)
        create_box(
            f"RossAde_UpperBowl_East_Riser_{i}",
            (x_e, CENTER_Y, z_t),
            (w_t, 126.0, dz_upper),
            mats['concrete'],
            col
        )
        create_box(
            f"RossAde_UpperBowl_East_Seats_{i}",
            (x_e, CENTER_Y, z_t + dz_upper * 0.5 + 0.24),
            (w_t * 0.78, 124.0, 0.44),
            seat_mat,
            col
        )
        
    # North Upper Horseshoe Curve (Student Section Bleachers upper deck)
    for s in range(segments):
        theta = s * d_theta
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        arc_y_center = CENTER_Y + 48.0
        
        for i in range(0, tier_count_upper, 2):
            r = 63.0 + i * dx_upper
            z_t = 9.8 + i * dz_upper
            px = CENTER_X - r * cos_t
            py = arc_y_center + r * sin_t
            
            wedge = create_box(
                f"RossAde_NorthCurve_Upper_S{s}_T{i}",
                (px, py, z_t),
                (dx_upper * 2.2, r * d_theta * 1.15, dz_upper * 2.0),
                mats['concrete'],
                col
            )
            wedge.rotation_euler[2] = -theta
            
            bleach = create_box(
                f"RossAde_NorthCurve_Upper_Bleacher_S{s}_T{i}",
                (px, py, z_t + dz_upper + 0.22),
                (dx_upper * 1.8, r * d_theta * 1.1, 0.40),
                mats['seat_bleacher'],
                col
            )
            bleach.rotation_euler[2] = -theta

    # Upper rim safety perimeter parapet walls
    # East upper parapet (X = CENTER_X + 89.0m, Z = 24.2m)
    create_box(
        "RossAde_UpperRim_Parapet_East",
        (CENTER_X + 89.0, CENTER_Y, 24.5),
        (1.4, 130.0, 1.8),
        mats['brick'],
        col
    )
    create_box(
        "RossAde_UpperRim_Coping_East",
        (CENTER_X + 89.0, CENTER_Y, 25.5),
        (1.8, 130.5, 0.3),
        mats['limestone'],
        col
    )
    
    # North upper rim parapet curve
    for s in range(0, segments, 2):
        theta = s * d_theta
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        px = CENTER_X - 89.0 * cos_t
        py = CENTER_Y + 48.0 + 89.0 * sin_t
        p_block = create_box(
            f"RossAde_UpperRim_North_Parapet_S{s}",
            (px, py, 24.5),
            (1.4, 89.0 * d_theta * 2.2, 1.8),
            mats['brick'],
            col
        )
        p_block.rotation_euler[2] = -theta

    # North End Auxiliary Scoreboard & Video Ribbon
    create_box(
        "RossAde_North_Auxiliary_Scoreboard",
        (CENTER_X, CENTER_Y + 138.0, 26.0),
        (28.0, 1.5, 7.5),
        mats['screen_led'],
        col
    )
    create_box(
        "RossAde_North_Auxiliary_Scoreboard_Truss",
        (CENTER_X, CENTER_Y + 138.8, 26.0),
        (29.0, 1.8, 8.5),
        mats['dark_metal'],
        col
    )


# -------------------------------------------------------------
# Component 3: West Pavilion (Shively & Buchanan Suites + Press Box)
# -------------------------------------------------------------
def build_west_pavilion(col, mats):
    print("Building West Pavilion, Shively & Buchanan Suites, and Press Box...")
    
    # West Pavilion bounds:
    # X spans from CENTER_X - 63.0m (inner face) to CENTER_X - 98.0m (outer street face)
    # Y spans from CENTER_Y - 55.0m to CENTER_Y + 55.0m (110m long)
    # Z spans from 10.0m (concourse roof) up to 36.5m (media deck)
    pav_cx = CENTER_X - 80.5
    pav_width = 35.0
    pav_length = 110.0
    
    # 1. Main Structural Brick & Concrete Mass
    pav_mass = create_box(
        "RossAde_WestPavilion_MainMass",
        (pav_cx, CENTER_Y, 23.0),
        (pav_width, pav_length, 26.0),
        mats['brick'],
        col
    )
    
    # 2. Horizontal Bedford Limestone Beltcourses across the 4 levels
    # Levels at Z = 14.5m, 19.5m, 25.0m, 30.5m, 36.0m
    for idx, bz in enumerate([14.5, 19.5, 25.0, 30.5, 36.0]):
        create_box(
            f"RossAde_WestPavilion_Beltcourse_{idx}",
            (pav_cx, CENTER_Y, bz),
            (pav_width + 0.8, pav_length + 0.8, 0.6),
            mats['limestone'],
            col
        )
        
    # 3. Level 1: Shively Club Lounge & Field-Facing Terrace (Z = 12.0m to 17.5m)
    # Continuous panoramic glass ribbon overlooking Rohrman Field on the east face
    create_box(
        "RossAde_ShivelyClub_Glass_Ribbon",
        (CENTER_X - 63.5, CENTER_Y, 15.5),
        (0.6, 106.0, 3.8),
        mats['glass'],
        col
    )
    # Outdoor club seating terrace along the edge
    create_box(
        "RossAde_ShivelyClub_Patio_Terrace",
        (CENTER_X - 61.2, CENTER_Y, 13.0),
        (4.2, 108.0, 0.4),
        mats['concrete'],
        col
    )
    # Shively club seating rows
    create_box(
        "RossAde_ShivelyClub_Seats",
        (CENTER_X - 61.2, CENTER_Y, 13.5),
        (2.8, 104.0, 0.5),
        mats['seat_gold'],
        col
    )
    
    # 4. Level 2: Buchanan Luxury Executive Suites (Z = 18.0m to 23.5m)
    # Continuous panoramic solar curtain wall
    create_box(
        "RossAde_BuchananSuites_Curtain_Glass",
        (CENTER_X - 63.5, CENTER_Y, 21.0),
        (0.6, 106.0, 4.2),
        mats['glass'],
        col
    )
    # Vertical mullions every 5 meters
    for idx in range(-10, 11):
        my = CENTER_Y + idx * 5.2
        create_box(
            f"RossAde_Buchanan_Mullion_{idx}",
            (CENTER_X - 63.2, my, 21.0),
            (0.8, 0.35, 4.6),
            mats['wordmark_gold'],
            col
        )
        
    # 5. Level 3: Upper Club & Presidential Suites (Z = 24.0m to 29.5m)
    create_box(
        "RossAde_UpperSuites_Curtain_Glass",
        (CENTER_X - 63.5, CENTER_Y, 27.0),
        (0.6, 106.0, 4.2),
        mats['glass'],
        col
    )
    for idx in range(-10, 11):
        my = CENTER_Y + idx * 5.2
        create_box(
            f"RossAde_UpperSuites_Mullion_{idx}",
            (CENTER_X - 63.2, my, 27.0),
            (0.8, 0.35, 4.6),
            mats['dark_metal'],
            col
        )

    # 6. Level 4: Press Box & Media Broadcast Tier (Z = 30.0m to 35.5m)
    # Broadcast booths with angled glare-reduction glazing
    create_box(
        "RossAde_PressBox_Broadcast_Glass",
        (CENTER_X - 63.5, CENTER_Y, 32.8),
        (0.6, 106.0, 3.8),
        mats['glass'],
        col
    )
    # Overhanging Cantilevered Roof Canopy (Extends out to shade press box)
    create_box(
        "RossAde_PressBox_Cantilever_Canopy",
        (CENTER_X - 66.5, CENTER_Y, 35.6),
        (9.5, 112.0, 0.8),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_PressBox_Canopy_Fascia",
        (CENTER_X - 61.5, CENTER_Y, 35.6),
        (0.6, 112.2, 0.9),
        mats['wordmark_gold'],
        col
    )

    # 7. Media Camera Platform & Film Deck (Z = 36.0m to 37.5m)
    create_box(
        "RossAde_Roof_FilmDeck_Slab",
        (pav_cx, CENTER_Y, 36.2),
        (pav_width - 2.0, pav_length - 4.0, 0.5),
        mats['concrete'],
        col
    )
    # Safety perimeter balustrade railing
    create_box(
        "RossAde_FilmDeck_Railing_East",
        (CENTER_X - 65.0, CENTER_Y, 37.0),
        (0.2, 106.0, 1.1),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_FilmDeck_Railing_West",
        (pav_cx - pav_width * 0.48, CENTER_Y, 37.0),
        (0.2, 106.0, 1.1),
        mats['dark_metal'],
        col
    )
    # Broadcast camera tripods / consoles
    for idx, cy in enumerate([-30.0, -10.0, 0.0, 10.0, 30.0]):
        create_cylinder(
            f"RossAde_FilmDeck_CamPlatform_{idx}",
            (CENTER_X - 66.5, CENTER_Y + cy, 37.2),
            1.2, 0.4,
            mats['dark_metal'],
            col
        )
        
    # HVAC Enclosures & Communications Antenna Masts on roof
    create_box(
        "RossAde_Pavilion_HVAC_Unit_1",
        (pav_cx - 6.0, CENTER_Y - 25.0, 38.0),
        (8.0, 12.0, 3.2),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_Pavilion_HVAC_Unit_2",
        (pav_cx - 6.0, CENTER_Y + 25.0, 38.0),
        (8.0, 12.0, 3.2),
        mats['dark_metal'],
        col
    )
    create_cylinder(
        "RossAde_Antenna_Mast_North",
        (pav_cx, CENTER_Y + 45.0, 42.0),
        0.2, 12.0,
        mats['dark_metal'],
        col
    )
    create_cylinder(
        "RossAde_Antenna_Mast_South",
        (pav_cx, CENTER_Y - 45.0, 42.0),
        0.2, 12.0,
        mats['dark_metal'],
        col
    )


# -------------------------------------------------------------
# Component 4: South Endzone Renovation & Rohrman Video Board
# -------------------------------------------------------------
def build_south_endzone_renovation(col, mats):
    print("Building 2023-2024 South Endzone renovation, Rohrman Video Board, and Tiller Tunnel...")
    
    # 1. Rohrman Family Video Board
    # Positioned at Y = CENTER_Y - 95.0m (tight to south patio concourse)
    # Dimensions: 150 ft 4 in wide (45.82m) x 56 ft 9 in tall (17.3m)
    board_y = CENTER_Y - 95.0
    board_z = 24.5 # Screen center height
    screen_w = 45.82
    screen_h = 17.3
    
    # Main Ultra-HD LED Display Screen
    create_box(
        "RossAde_Rohrman_VideoBoard_LED_Screen",
        (CENTER_X, board_y, board_z),
        (screen_w, 0.6, screen_h),
        mats['screen_led'],
        col
    )
    # Display Screen Outer Bezel Frame
    create_box(
        "RossAde_Rohrman_VideoBoard_Bezel",
        (CENTER_X, board_y - 0.1, board_z),
        (screen_w + 1.2, 0.8, screen_h + 1.2),
        mats['dark_metal'],
        col
    )
    
    # North-Facing Backlit "PURDUE" Wordmark on top of the Video Board
    # Position: on top truss at Z = board_z + screen_h * 0.5 + 2.2m
    wordmark_z = board_z + screen_h * 0.5 + 2.4
    create_box(
        "RossAde_VideoBoard_Top_Truss",
        (CENTER_X, board_y, wordmark_z - 1.2),
        (screen_w + 2.0, 2.4, 2.2),
        mats['dark_metal'],
        col
    )
    # Emissive Gold 3D "PURDUE" letters
    for i, char in enumerate(['P', 'U', 'R', 'D', 'U', 'E']):
        wx = CENTER_X - 15.0 + i * 6.0
        create_box(
            f"RossAde_VideoBoard_Wordmark_{char}_{i}",
            (wx, board_y + 0.4, wordmark_z),
            (3.8, 0.6, 3.2),
            mats['wordmark_gold'],
            col
        )
        
    # South-Facing Backlit Giant Motion "P" Logo (Facing Tower Dr / Campus)
    create_box(
        "RossAde_VideoBoard_Rear_Motion_P_Backing",
        (CENTER_X, board_y - 1.2, board_z),
        (16.0, 0.5, 14.0),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_VideoBoard_Rear_Motion_P_Gold",
        (CENTER_X, board_y - 1.4, board_z),
        (14.0, 0.4, 12.0),
        mats['wordmark_gold'],
        col
    )
    
    # Video Board Structural Steel Lattice Pylons (4 major columns)
    # Rising from ground (Z = 0) up to Z = 36m
    for idx, px in enumerate([CENTER_X - 20.0, CENTER_X - 7.0, CENTER_X + 7.0, CENTER_X + 20.0]):
        create_box(
            f"RossAde_VideoBoard_Pylon_{idx}",
            (px, board_y - 1.8, 17.5),
            (2.2, 2.2, 35.0),
            mats['dark_metal'],
            col
        )
        # Cross braces between pylons
        create_box(
            f"RossAde_VideoBoard_CrossBrace_Low_{idx}",
            (px, board_y - 1.8, 8.0),
            (6.5, 0.4, 0.4),
            mats['dark_metal'],
            col
        )
        create_box(
            f"RossAde_VideoBoard_CrossBrace_Mid_{idx}",
            (px, board_y - 1.8, 16.0),
            (6.5, 0.4, 0.4),
            mats['dark_metal'],
            col
        )
        
    # Catwalks and Audio Line-Array Speaker Systems flanking the video board
    create_box(
        "RossAde_Audio_Speaker_Array_West",
        (CENTER_X - screen_w * 0.5 - 2.5, board_y, board_z),
        (3.0, 1.8, screen_h * 0.8),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_Audio_Speaker_Array_East",
        (CENTER_X + screen_w * 0.5 + 2.5, board_y, board_z),
        (3.0, 1.8, screen_h * 0.8),
        mats['dark_metal'],
        col
    )
    
    # 2. Tyler Trent Student Section & South Endzone Patio Terraces (2023-2024 Renovation)
    # Replaces old bleachers with 6 multi-tiered safe-standing terraces from Y = CENTER_Y - 60m to -85m
    terrace_count = 6
    dy_terrace = 4.2
    dz_terrace = 1.1
    for t in range(terrace_count):
        ty = CENTER_Y - 58.0 - t * dy_terrace
        tz = 1.2 + t * dz_terrace
        # Concrete safe-standing terrace slab
        create_box(
            f"RossAde_TylerTrent_Terrace_{t}",
            (CENTER_X, ty, tz),
            (72.0, dy_terrace * 1.05, dz_terrace),
            mats['concrete'],
            col
        )
        # Black powder-coated safety drink rails / handrails
        create_box(
            f"RossAde_TylerTrent_Rail_{t}",
            (CENTER_X, ty + dy_terrace * 0.4, tz + dz_terrace * 0.5 + 0.55),
            (70.0, 0.15, 1.1),
            mats['dark_metal'],
            col
        )
        create_box(
            f"RossAde_TylerTrent_BarTop_{t}",
            (CENTER_X, ty + dy_terrace * 0.4, tz + dz_terrace * 0.5 + 1.1),
            (70.0, 0.45, 0.08),
            mats['limestone'],
            col
        )
        
    # South Concourse Connector (Pedestrian bridge connecting East and West concourses)
    # Spans across south endzone behind Tyler Trent section at Z = 8.5m
    create_box(
        "RossAde_South_Concourse_Connector_Slab",
        (CENTER_X, CENTER_Y - 86.0, 8.5),
        (96.0, 8.0, 0.6),
        mats['concrete'],
        col
    )
    create_box(
        "RossAde_South_Concourse_Railing_North",
        (CENTER_X, CENTER_Y - 82.2, 9.4),
        (96.0, 0.2, 1.2),
        mats['dark_metal'],
        col
    )
    create_box(
        "RossAde_South_Concourse_Railing_South",
        (CENTER_X, CENTER_Y - 89.8, 9.4),
        (96.0, 0.2, 1.2),
        mats['dark_metal'],
        col
    )
    # Brick support piers under South Connector
    for idx, cx in enumerate([-40.0, -20.0, 0.0, 20.0, 40.0]):
        create_box(
            f"RossAde_South_Concourse_Pier_{idx}",
            (CENTER_X + cx, CENTER_Y - 86.0, 4.2),
            (3.0, 3.0, 8.4),
            mats['brick'],
            col
        )
        
    # 3. Joe Tiller Tunnel (Team Entrance Portal)
    # Connects player locker rooms / Kozuch Center to Rohrman Field at Northeast / East sideline
    tunnel_x = CENTER_X + 38.0
    tunnel_y = CENTER_Y - 58.0
    # Tunnel brick portal walls
    create_box(
        "RossAde_TillerTunnel_WestWall",
        (tunnel_x - 3.2, tunnel_y, 2.5),
        (0.8, 16.0, 5.0),
        mats['brick'],
        col
    )
    create_box(
        "RossAde_TillerTunnel_EastWall",
        (tunnel_x + 3.2, tunnel_y, 2.5),
        (0.8, 16.0, 5.0),
        mats['brick'],
        col
    )
    # Portal lintel beam with bronze signage
    create_box(
        "RossAde_TillerTunnel_Lintel",
        (tunnel_x, tunnel_y + 7.5, 4.8),
        (7.2, 1.2, 1.2),
        mats['limestone'],
        col
    )
    create_box(
        "RossAde_TillerTunnel_Signage_Plaque",
        (tunnel_x, tunnel_y + 8.1, 4.8),
        (5.8, 0.1, 0.8),
        mats['wordmark_gold'],
        col
    )
    # Sloping player entrance ramp
    create_box(
        "RossAde_TillerTunnel_Ramp",
        (tunnel_x, tunnel_y, 0.1),
        (5.6, 16.0, 0.2),
        mats['turf'],
        col
    )


# -------------------------------------------------------------
# Component 5: Stadium Floodlight Monolith Towers & Lighting
# -------------------------------------------------------------
def build_floodlight_towers(col, mats):
    print("Building 4 monumental 48m stadium floodlight lattice towers...")
    
    # 4 Quadrants: NW, SW, NE, SE
    # Northwest: X = CENTER_X - 85.0m, Y = CENTER_Y + 75.0m
    # Southwest: X = CENTER_X - 85.0m, Y = CENTER_Y - 75.0m
    # Northeast: X = CENTER_X + 85.0m, Y = CENTER_Y + 75.0m
    # Southeast: X = CENTER_X + 85.0m, Y = CENTER_Y - 75.0m
    tower_locs = [
        ("NW", CENTER_X - 85.0, CENTER_Y + 75.0, 1.0, -1.0),
        ("SW", CENTER_X - 85.0, CENTER_Y - 75.0, 1.0, 1.0),
        ("NE", CENTER_X + 85.0, CENTER_Y + 75.0, -1.0, -1.0),
        ("SE", CENTER_X + 85.0, CENTER_Y - 75.0, -1.0, 1.0),
    ]
    
    for quad, tx, ty, aim_x, aim_y in tower_locs:
        # 1. Main Tapered Steel Lattice Mast (Height = 48.0m)
        create_box(
            f"RossAde_Floodlight_Mast_Base_{quad}",
            (tx, ty, 12.0),
            (4.0, 4.0, 24.0),
            mats['dark_metal'],
            col
        )
        create_box(
            f"RossAde_Floodlight_Mast_Mid_{quad}",
            (tx, ty, 30.0),
            (3.0, 3.0, 16.0),
            mats['dark_metal'],
            col
        )
        create_box(
            f"RossAde_Floodlight_Mast_Top_{quad}",
            (tx, ty, 42.0),
            (2.2, 2.2, 10.0),
            mats['dark_metal'],
            col
        )
        
        # 2. Angled Head Rack (12m wide x 4.5m tall, tilted 40 deg towards field)
        rack_z = 47.5
        rack_obj = create_box(
            f"RossAde_Floodlight_HeadRack_{quad}",
            (tx + aim_x * 2.0, ty + aim_y * 2.0, rack_z),
            (11.0, 1.2, 4.5),
            mats['dark_metal'],
            col
        )
        # Aim orientation towards field center
        rack_angle = math.atan2(-aim_y, -aim_x)
        rack_obj.rotation_euler[2] = rack_angle
        
        # 3. Floodlight Pods Array (3 rows of 10 emissive lights = 30 fixtures)
        for r in range(3):
            for c in range(8):
                fx = (c - 3.5) * 1.2
                fz = rack_z + (r - 1) * 1.2
                pod = create_box(
                    f"RossAde_Floodlight_Pod_{quad}_R{r}_C{c}",
                    (tx + aim_x * 2.5 + fx * math.cos(rack_angle + math.pi/2),
                     ty + aim_y * 2.5 + fx * math.sin(rack_angle + math.pi/2),
                     fz),
                    (0.9, 0.4, 0.9),
                    mats['floodlight_glow'],
                    col
                )
                pod.rotation_euler[2] = rack_angle


# -------------------------------------------------------------
# Component 6: Exterior Concourses, Monumental Arches, & Plazas
# -------------------------------------------------------------
def build_exterior_gates_and_plazas(col, mats):
    print("Building exterior concourses, monumental arched gates, and plazas...")
    
    # 1. Outer Stadium Brick Perimeter Enclosure Wall
    # Encloses the entire bowl perimeter up to Z = 11.5m
    # East wall
    create_box(
        "RossAde_ExteriorWall_East",
        (CENTER_X + 90.5, CENTER_Y, 5.8),
        (2.0, 136.0, 11.5),
        mats['brick'],
        col
    )
    create_box(
        "RossAde_ExteriorWall_East_Coping",
        (CENTER_X + 90.5, CENTER_Y, 11.8),
        (2.6, 136.8, 0.6),
        mats['limestone'],
        col
    )
    
    # West street-level facade along John R. Wooden Dr
    create_box(
        "RossAde_ExteriorWall_West",
        (CENTER_X - 98.5, CENTER_Y, 5.8),
        (2.0, 126.0, 11.5),
        mats['brick'],
        col
    )
    create_box(
        "RossAde_ExteriorWall_West_Coping",
        (CENTER_X - 98.5, CENTER_Y, 11.8),
        (2.6, 126.8, 0.6),
        mats['limestone'],
        col
    )
    
    # North curve exterior facade
    segments = 24
    d_theta = math.pi / segments
    for s in range(0, segments, 2):
        theta = s * d_theta
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        px = CENTER_X - 91.0 * cos_t
        py = CENTER_Y + 48.0 + 91.0 * sin_t
        w_block = create_box(
            f"RossAde_ExteriorWall_North_S{s}",
            (px, py, 5.8),
            (2.0, 91.0 * d_theta * 2.2, 11.5),
            mats['brick'],
            col
        )
        w_block.rotation_euler[2] = -theta
        
    # 2. Monumental Entrance Gates (Gate A, B, C, D, E, F)
    # Arched brick pavilions with Bedford limestone architraves and keystones
    gates = [
        ("Gate_A_Southwest", CENTER_X - 85.0, CENTER_Y - 90.0),
        ("Gate_B_West_Central", CENTER_X - 99.0, CENTER_Y - 20.0),
        ("Gate_C_West_North", CENTER_X - 99.0, CENTER_Y + 20.0),
        ("Gate_D_North_Apex", CENTER_X, CENTER_Y + 140.0),
        ("Gate_E_East_North", CENTER_X + 91.5, CENTER_Y + 20.0),
        ("Gate_F_East_South", CENTER_X + 91.5, CENTER_Y - 20.0),
        ("Gate_G_Southeast", CENTER_X + 75.0, CENTER_Y - 90.0)
    ]
    for g_name, gx, gy in gates:
        # Gate Brick Piers
        create_box(
            f"RossAde_{g_name}_Pier_L",
            (gx - 2.8, gy, 4.5),
            (1.6, 1.6, 9.0),
            mats['brick'],
            col
        )
        create_box(
            f"RossAde_{g_name}_Pier_R",
            (gx + 2.8, gy, 4.5),
            (1.6, 1.6, 9.0),
            mats['brick'],
            col
        )
        # Stone Pier Caps
        create_box(
            f"RossAde_{g_name}_Cap_L",
            (gx - 2.8, gy, 9.2),
            (2.0, 2.0, 0.5),
            mats['limestone'],
            col
        )
        create_box(
            f"RossAde_{g_name}_Cap_R",
            (gx + 2.8, gy, 9.2),
            (2.0, 2.0, 0.5),
            mats['limestone'],
            col
        )
        # Arch Header & Keystones
        create_box(
            f"RossAde_{g_name}_ArchHeader",
            (gx, gy, 8.6),
            (7.2, 1.8, 1.2),
            mats['limestone'],
            col
        )
        # Bronze Lettering Signage Plaque
        create_box(
            f"RossAde_{g_name}_Signage",
            (gx, gy - 0.95, 8.6),
            (5.4, 0.1, 0.8),
            mats['wordmark_gold'],
            col
        )
        # Black Wrought-Iron Turnstiles / Gates
        create_box(
            f"RossAde_{g_name}_Turnstiles",
            (gx, gy, 1.5),
            (4.8, 1.2, 3.0),
            mats['dark_metal'],
            col
        )
        
    # 3. Exterior Circulation Ramps & Grand Stairs (West & East concourses)
    # Ramps ascending from Z = 0 to Z = 9.2m
    create_box(
        "RossAde_ExteriorRamp_West",
        (CENTER_X - 94.0, CENTER_Y - 50.0, 4.6),
        (6.0, 42.0, 0.5),
        mats['concrete'],
        col
    )
    create_box(
        "RossAde_ExteriorRamp_East",
        (CENTER_X + 86.0, CENTER_Y - 50.0, 4.6),
        (6.0, 42.0, 0.5),
        mats['concrete'],
        col
    )
    
    # 4. Purdue Championship Banners along Exterior Brick Bays
    # 10 large banners celebrating Big Ten Championships and Legends
    for idx in range(-4, 5):
        by = CENTER_Y + idx * 14.0
        # East facade banner
        create_box(
            f"RossAde_Banner_East_{idx}",
            (CENTER_X + 91.8, by, 7.5),
            (0.1, 4.2, 6.5),
            mats['banner_gold'],
            col
        )
        # West facade banner
        create_box(
            f"RossAde_Banner_West_{idx}",
            (CENTER_X - 99.8, by, 7.5),
            (0.1, 4.2, 6.5),
            mats['banner_gold'],
            col
        )
        
    # 5. Exterior Surrounding Plaza Paving (John R. Wooden Dr / Tower Dr / Northwestern Ave)
    create_box(
        "RossAde_Surrounding_Plaza_Paving",
        (CENTER_X, CENTER_Y, FIELD_Z + 0.02),
        (225.0, 305.0, 0.08),
        mats['pavement'],
        col
    )


# -------------------------------------------------------------
# Component 7: Calibrate 5 Dedicated Inspection Cameras
# -------------------------------------------------------------
def calibrate_stadium_cameras(col):
    print("Calibrating 5 dedicated inspection cameras for Ross-Ade Stadium...")
    
    cameras_def = [
        {
            'name': 'Cam_32_Ross_Ade_Field_50YardLine_Hero',
            'loc': (CENTER_X - 22.0, CENTER_Y, 2.0),
            'target': (CENTER_X, CENTER_Y, 2.5),
            'lens': 24.0,
            'desc': 'Field-level hero shot at the 50-yard line capturing Motion P, endzones, and the bowl'
        },
        {
            'name': 'Cam_33_Ross_Ade_SouthEndzone_VideoBoard',
            'loc': (CENTER_X, CENTER_Y + 15.0, 6.5),
            'target': (CENTER_X, CENTER_Y - 95.0, 24.0),
            'lens': 28.0,
            'desc': 'View looking south at the Rohrman Video Board, Tyler Trent standing section, and Tiller Tunnel'
        },
        {
            'name': 'Cam_34_Ross_Ade_WestPavilion_Suites',
            'loc': (CENTER_X + 25.0, CENTER_Y, 8.0),
            'target': (CENTER_X - 80.0, CENTER_Y, 24.0),
            'lens': 32.0,
            'desc': 'View from east grandstand across the field looking at Buchanan/Shively suites and Press Box'
        },
        {
            'name': 'Cam_35_Ross_Ade_NorthBowl_StudentSection',
            'loc': (CENTER_X, CENTER_Y - 25.0, 10.0),
            'target': (CENTER_X, CENTER_Y + 90.0, 16.0),
            'lens': 28.0,
            'desc': 'View looking north across the horseshoe curve, student section bleachers, and auxiliary board'
        },
        {
            'name': 'Cam_36_Ross_Ade_StadiumAve_ExteriorGate',
            'loc': (CENTER_X - 118.0, CENTER_Y - 95.0, 4.0),
            'target': (CENTER_X - 85.0, CENTER_Y - 80.0, 12.0),
            'lens': 28.0,
            'desc': 'Street-level perspective looking at Southwest Gate A, brick facade, banners, and floodlight tower'
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
    print("STARTING ROSS-ADE STADIUM PHOTOREALISTIC BUILD")
    print(f"Center: ({CENTER_X}, {CENTER_Y}), Elevation: {FIELD_Z}")
    print("==================================================")
    
    # 1. Initialize Collections
    col_field = get_or_create_col(COL_NAMES['field_bowl'])
    col_pav = get_or_create_col(COL_NAMES['pavilion'])
    col_south = get_or_create_col(COL_NAMES['south_endzone'])
    col_ext = get_or_create_col(COL_NAMES['exterior_site'])
    col_cams = get_or_create_col(COL_NAMES['cameras'])
    
    # Clear previous stadium objects if rerunning
    clear_collection_objects(col_field)
    clear_collection_objects(col_pav)
    clear_collection_objects(col_south)
    clear_collection_objects(col_ext)
    
    # 2. Materials
    mats = setup_stadium_materials()
    
    # 3. Build Components
    build_rohrman_field(col_field, mats)
    build_horseshoe_bowl(col_field, mats)
    build_west_pavilion(col_pav, mats)
    build_south_endzone_renovation(col_south, mats)
    build_floodlight_towers(col_ext, mats)
    build_exterior_gates_and_plazas(col_ext, mats)
    
    # 4. Calibrate Cameras
    calibrate_stadium_cameras(col_cams)
    
    # 5. Set Hero Camera active
    hero_cam = bpy.data.objects.get('Cam_32_Ross_Ade_Field_50YardLine_Hero')
    if hero_cam:
        bpy.context.scene.camera = hero_cam
        
    print("==================================================")
    print("ROSS-ADE STADIUM MODELING COMPLETE")
    print(f"Field & Bowl Objects: {len(col_field.objects)}")
    print(f"West Pavilion Objects: {len(col_pav.objects)}")
    print(f"South Endzone Objects: {len(col_south.objects)}")
    print(f"Exterior & Lighting Objects: {len(col_ext.objects)}")
    print("==================================================")

if __name__ == '__main__':
    main()
