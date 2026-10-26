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

def create_cone(name, loc, r1, r2, depth, mat=None, col=None, verts=32):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=verts,
        radius1=r1,
        radius2=r2,
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
        return bpy.data.collections[col_name]
    c = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(c)
    return c

def get_or_make_mat(name, base_color, roughness=0.7, metallic=0.0, transmission=0.0, emission=None, emission_strength=1.0, ior=1.333):
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
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def build_fountains():
    print("=== FINISHING BOTH ENGINEERING FOUNTAIN & LOEB FOUNTAIN ===")
    
    col_eng = clean_or_create_col("08_Engineering_Fountain_and_Mall")
    col_loeb = clean_or_create_col("16_Loeb_Fountain_and_Founders_Park")
    
    # -------------------------------------------------------------
    # Shared & Fountain-Specific Materials
    # -------------------------------------------------------------
    # Engineering Fountain
    mat_white_conc = get_or_make_mat("Purdue_Precast_White_Concrete", (0.92, 0.91, 0.89, 1.0), roughness=0.75)
    mat_chrome_mirror = get_or_make_mat("Fountain_Mirrored_Stainless_Steel", (0.95, 0.96, 0.98, 1.0), roughness=0.04, metallic=1.0)
    mat_steel_grate = get_or_make_mat("Fountain_Perforated_Steel_Grate", (0.45, 0.46, 0.48, 1.0), roughness=0.35, metallic=0.9)
    mat_stone = get_or_make_mat("Beering_Bedford_Limestone", (0.84, 0.82, 0.77, 1.0), roughness=0.62)
    mat_brick = get_or_make_mat("SouthHall_Purdue_Red_Brick", (0.54, 0.22, 0.16, 1.0), roughness=0.82)
    mat_teak = get_or_make_mat("Campus_Teak_Wood_Bench", (0.42, 0.26, 0.14, 1.0), roughness=0.55)
    mat_bronze = get_or_make_mat("Purdue_Sculpture_Cast_Bronze", (0.35, 0.28, 0.18, 1.0), roughness=0.45, metallic=0.8)
    
    # Loeb Fountain Granite & Water
    mat_black_granite = get_or_make_mat("Loeb_Polished_Black_Granite", (0.10, 0.10, 0.12, 1.0), roughness=0.12, metallic=0.1)
    mat_gray_granite = get_or_make_mat("Loeb_Thermal_Barre_Granite", (0.58, 0.58, 0.60, 1.0), roughness=0.60)
    mat_water_stream = get_or_make_mat("Fountain_Aerated_Water_Stream", (0.75, 0.90, 0.98, 1.0), roughness=0.15, transmission=0.82, ior=1.333)
    mat_water_spray = get_or_make_mat("Fountain_Frothy_Water_Spray", (0.92, 0.96, 1.0, 1.0), roughness=0.35, transmission=0.65, emission=(0.85, 0.95, 1.0, 1.0), emission_strength=1.4)
    mat_uplight = get_or_make_mat("Fountain_LED_Uplight_Emissive", (0.8, 0.95, 1.0, 1.0), roughness=0.1, emission=(0.7, 0.95, 1.0, 1.0), emission_strength=15.0)

    # =============================================================
    # 1. FINISHING THE ENGINEERING FOUNTAIN (Class of 1939 Water Sculpture)
    # =============================================================
    ef_cx, ef_cy = 0.0, 195.0
    print("Elevating Engineering Fountain to Full Photorealism...")
    
    # Dedication Plaque on Limestone Pedestal (South arrival threshold)
    create_box(
        "EngFountain_Dedication_Limestone_Plinth",
        loc=(ef_cx, ef_cy - 14.5, 0.5),
        size=(1.6, 0.9, 1.0),
        mat=mat_stone,
        col=col_eng
    )
    create_box(
        "EngFountain_Class1939_Bronze_Plaque",
        loc=(ef_cx, ef_cy - 14.96, 0.65),
        size=(1.2, 0.04, 0.7),
        mat=mat_bronze,
        col=col_eng
    )
    
    # 4 Flush Ground-Recessed LED Uplights at base of each pylon
    # Illuminates the soaring parabolic concrete fins and water column
    for ang in [45, 135, 225, 315]:
        rad = math.radians(ang)
        ux = ef_cx + 1.6 * math.cos(rad)
        uy = ef_cy + 1.6 * math.sin(rad)
        create_cylinder(
            f"EngFountain_LED_Uplight_Fixture_{ang}",
            loc=(ux, uy, 0.09),
            radius=0.22,
            depth=0.04,
            mat=mat_uplight,
            col=col_eng,
            verts=20
        )
        
    # Additional Aerated Foam Ring around the 2001 Stainless Safety Cylinder Base
    create_cylinder(
        "EngFountain_Aerated_Base_Foam_Pool",
        loc=(ef_cx, ef_cy, 0.12),
        radius=1.85,
        depth=0.14,
        mat=mat_water_spray,
        col=col_eng,
        verts=32
    )
    
    # Fine Vertical Hydraulic Core Geyser Jet (11.58m high, shooting upward through cylinder)
    create_cone(
        "EngFountain_Central_Supercharged_Geyser_Column",
        loc=(ef_cx, ef_cy, 6.8),
        r1=0.48,
        r2=0.22,
        depth=9.2,
        mat=mat_water_stream,
        col=col_eng,
        verts=32
    )
    
    # 4 Cascading Parabolic Water Curtains (falling down the inside face of each pylon)
    for ang in [45, 135, 225, 315]:
        rad = math.radians(ang)
        fx = ef_cx + 2.2 * math.cos(rad)
        fy = ef_cy + 2.2 * math.sin(rad)
        create_cone(
            f"EngFountain_Waterfall_Curtain_Sheet_{ang}",
            loc=(fx, fy, 4.8),
            r1=0.85,
            r2=0.25,
            depth=8.0,
            mat=mat_water_stream,
            col=col_eng,
            verts=20
        )
        
    # 8 Teak wood slat bench seats around the perimeter plaza
    for ang_b in range(0, 360, 45):
        rad_b = math.radians(ang_b)
        bx = ef_cx + 21.0 * math.cos(rad_b)
        by = ef_cy + 21.0 * math.sin(rad_b)
        # Teak wood seat top over concrete bench base
        create_box(
            f"EngFountain_Teak_Bench_Seat_{ang_b}",
            loc=(bx, by, 0.52),
            size=(3.8, 0.75, 0.08),
            mat=mat_teak,
            col=col_eng
        )
    print("Engineering Fountain photorealistic water hydraulics & hardscape finished.")

    # =============================================================
    # 2. BUILDING THE LOEB FOUNTAIN IN FOUNDERS PARK
    # =============================================================
    # Location: Center of Founders Park (South of University Hall, East of Beering Hall)
    # Center: X = -50.0m, Y = -255.0m
    lf_cx, lf_cy = -50.0, -255.0
    print(f"Constructing Loeb Play Fountain in Founders Park at ({lf_cx}, {lf_cy})...")
    
    # A. Founders Park Outer Pedestrian Concourse & Promenade (44m diameter circle)
    create_cylinder(
        "FoundersPark_Loeb_Outer_Promenade_Paving",
        loc=(lf_cx, lf_cy, 0.08),
        radius=22.0,
        depth=0.10,
        mat=mat_stone,
        col=col_loeb,
        verts=48
    )
    
    # Concentric brick paver decorative inlay ring (Radius = 16.0m to 19.0m)
    create_cylinder(
        "FoundersPark_Brick_Inlay_Band",
        loc=(lf_cx, lf_cy, 0.09),
        radius=18.5,
        depth=0.08,
        mat=mat_brick,
        col=col_loeb,
        verts=48
    )
    
    # 4 Curved Granite Seatwalls enclosing Founders Park at R = 14.0m
    # Segmented across the 4 quadrant arcs
    for q_idx, q_ang_start in enumerate([20, 110, 200, 290]):
        for arc_step in range(3):
            arc_ang = math.radians(q_ang_start + arc_step * 18.0)
            sw_x = lf_cx + 14.2 * math.cos(arc_ang)
            sw_y = lf_cy + 14.2 * math.sin(arc_ang)
            create_box(
                f"Loeb_Courtyard_Seatwall_{q_idx}_{arc_step}",
                loc=(sw_x, sw_y, 0.42),
                size=(3.8, 0.75, 0.65),
                mat=mat_gray_granite,
                col=col_loeb
            )
            create_box(
                f"Loeb_Courtyard_Seatwall_Cap_{q_idx}_{arc_step}",
                loc=(sw_x, sw_y, 0.78),
                size=(4.0, 0.90, 0.12),
                mat=mat_black_granite,
                col=col_loeb
            )
            create_box(
                f"Loeb_Courtyard_Teak_Slat_{q_idx}_{arc_step}",
                loc=(sw_x, sw_y, 0.86),
                size=(3.6, 0.70, 0.06),
                mat=mat_teak,
                col=col_loeb
            )
            
    # B. The Interactive Loeb Fountain Granite Dry-Deck (20m Diameter)
    # Outer Granite Basin Rim / Dry Deck (Radius = 10.0m)
    create_cylinder(
        "LoebFountain_Granite_DryDeck_Plaza",
        loc=(lf_cx, lf_cy, 0.10),
        radius=10.0,
        depth=0.12,
        mat=mat_gray_granite,
        col=col_loeb,
        verts=48
    )
    # Polished Black Granite Concentric Scoring Ring (Radius = 7.5m)
    create_cylinder(
        "LoebFountain_Polished_Black_Granite_Ring",
        loc=(lf_cx, lf_cy, 0.11),
        radius=7.6,
        depth=0.10,
        mat=mat_black_granite,
        col=col_loeb,
        verts=48
    )
    # Circular Stainless Steel Flush Perimeter Drainage Trench (Radius = 7.3m)
    create_cylinder(
        "LoebFountain_Perimeter_Drain_Grate_Trench",
        loc=(lf_cx, lf_cy, 0.115),
        radius=7.35,
        depth=0.08,
        mat=mat_steel_grate,
        col=col_loeb,
        verts=48
    )
    
    # Raised Central Granite Stage Platform (Radius = 3.6m, Height = 0.18m above deck)
    create_cylinder(
        "LoebFountain_Central_Raised_Granite_Platform",
        loc=(lf_cx, lf_cy, 0.18),
        radius=3.6,
        depth=0.16,
        mat=mat_gray_granite,
        col=col_loeb,
        verts=36
    )
    # Central Bullseye Inlaid Ring in Polished Black Granite
    create_cylinder(
        "LoebFountain_Center_Bullseye_Granite_Inlay",
        loc=(lf_cx, lf_cy, 0.20),
        radius=1.4,
        depth=0.14,
        mat=mat_black_granite,
        col=col_loeb,
        verts=32
    )
    # Central Stainless Drain Grate
    create_cylinder(
        "LoebFountain_Center_Drain_Grate",
        loc=(lf_cx, lf_cy, 0.205),
        radius=0.9,
        depth=0.12,
        mat=mat_steel_grate,
        col=col_loeb,
        verts=24
    )
    
    # C. Ring of 16 Signature Granite Bollard Columns (Radius = 8.2m)
    # Each fitted with interior plumbing and inward-firing arching laminar jets
    print("Erecting 16 Signature Granite Bollard Columns with Inward Laminar Jets...")
    for b_idx in range(16):
        b_ang = math.radians(b_idx * 22.5)
        bx = lf_cx + 8.2 * math.cos(b_ang)
        by = lf_cy + 8.2 * math.sin(b_ang)
        # Cylindrical Granite Bollard Column
        create_cylinder(
            f"LoebFountain_Granite_Bollard_{b_idx}",
            loc=(bx, by, 0.52),
            radius=0.28,
            depth=0.85,
            mat=mat_black_granite,
            col=col_loeb,
            verts=20
        )
        # Stainless steel nozzle top cap
        create_cylinder(
            f"LoebFountain_Bollard_Nozzle_Cap_{b_idx}",
            loc=(bx, by, 0.96),
            radius=0.30,
            depth=0.06,
            mat=mat_chrome_mirror,
            col=col_loeb,
            verts=20
        )
        # Inward arching laminar water jet streams spraying toward the central platform
        # Modeled as a parabolic water stream segment angled inward
        arc_mid_x = (bx + lf_cx) * 0.5
        arc_mid_y = (by + lf_cy) * 0.5
        create_cone(
            f"LoebFountain_Inward_Laminar_Stream_{b_idx}",
            loc=(arc_mid_x, arc_mid_y, 1.35),
            r1=0.09,
            r2=0.04,
            depth=3.8,
            mat=mat_water_stream,
            col=col_loeb,
            verts=12
        )
        
    # D. Active Water Hydraulics (2,200 GPM Recycled Flow)
    print("Simulating Loeb Fountain Hydraulic Water Columns & Mist Plumes...")
    # 1. Main High-Pressure Central Geyser Jet Column (shoots 8.8m / 29ft high)
    create_cone(
        "LoebFountain_Core_Supercharged_Geyser_Jet",
        loc=(lf_cx, lf_cy, 4.6),
        r1=0.42,
        r2=0.15,
        depth=8.8,
        mat=mat_water_stream,
        col=col_loeb,
        verts=28
    )
    # Geyser plume crown spray
    create_cylinder(
        "LoebFountain_Geyser_Peak_Spray_Crown",
        loc=(lf_cx, lf_cy, 8.9),
        radius=0.95,
        depth=0.8,
        mat=mat_water_spray,
        col=col_loeb,
        verts=24
    )
    
    # 2. Intermediate Ring of 8 Vertical Frothy Bubbler Jets (Radius = 2.4m, Height = 2.6m)
    for j_i in range(8):
        j_ang = math.radians(j_i * 45.0)
        jx = lf_cx + 2.4 * math.cos(j_ang)
        jy = lf_cy + 2.4 * math.sin(j_ang)
        create_cone(
            f"LoebFountain_Bubbler_Vertical_Jet_{j_i}",
            loc=(jx, jy, 1.45),
            r1=0.16,
            r2=0.07,
            depth=2.5,
            mat=mat_water_spray,
            col=col_loeb,
            verts=16
        )
        
    # 3. Active Play Surface Water Film / Frothy Recirculation Layer
    create_cylinder(
        "LoebFountain_Active_Deck_Water_Film",
        loc=(lf_cx, lf_cy, 0.22),
        radius=7.2,
        depth=0.04,
        mat=mat_water_spray,
        col=col_loeb,
        verts=36
    )
    
    # E. Founders Park Dedication Bronze Plaque & Lantern Posts
    create_box(
        "LoebFountain_Dedication_Granite_Pedestal",
        loc=(lf_cx, lf_cy - 12.5, 0.5),
        size=(1.5, 0.8, 0.9),
        mat=mat_gray_granite,
        col=col_loeb
    )
    create_box(
        "LoebFountain_Solomon_Loeb_Bronze_Plaque",
        loc=(lf_cx, lf_cy - 12.92, 0.65),
        size=(1.1, 0.04, 0.6),
        mat=mat_bronze,
        col=col_loeb
    )
    
    # 4 Traditional Cast-Iron Campus Lantern Posts at Park Quadrants
    for l_idx, (lx_off, ly_off) in enumerate([(-18, -18), (18, -18), (-18, 18), (18, 18)]):
        create_cylinder(
            f"FoundersPark_Campus_LampPost_Base_{l_idx}",
            loc=(lf_cx + lx_off, lf_cy + ly_off, 0.3),
            radius=0.25,
            depth=0.6,
            mat=mat_chrome_mirror,
            col=col_loeb,
            verts=16
        )
        create_cylinder(
            f"FoundersPark_Campus_LampPost_Shaft_{l_idx}",
            loc=(lf_cx + lx_off, lf_cy + ly_off, 2.5),
            radius=0.08,
            depth=4.4,
            mat=mat_chrome_mirror,
            col=col_loeb,
            verts=16
        )
        create_box(
            f"FoundersPark_Campus_Lantern_Head_{l_idx}",
            loc=(lf_cx + lx_off, lf_cy + ly_off, 4.9),
            size=(0.45, 0.45, 0.75),
            mat=mat_uplight,
            col=col_loeb
        )

    # =============================================================
    # 3. SETUP CALIBRATED INSPECTION CAMERAS FOR BOTH FOUNTAINS
    # =============================================================
    setup_fountain_inspection_cameras(ef_cx, ef_cy, lf_cx, lf_cy)
    print("=== BOTH ENGINEERING AND LOEB FOUNTAINS SUCCESSFULLY COMPLETED ===")

def setup_fountain_inspection_cameras(ef_cx, ef_cy, lf_cx, lf_cy):
    col = clean_or_create_col("05_Cameras_and_Views")
    
    cameras = [
        # 1. Engineering Fountain Hero Ground View (West-South-West looking toward ARMS)
        {
            "name": "Cam_18_Engineering_Fountain_Hero_GroundView",
            "loc": (ef_cx - 16.0, ef_cy - 18.0, 3.2),
            "rot": (math.radians(82.0), 0.0, math.radians(-38.0)),
            "lens": 22.0
        },
        # 2. Engineering Fountain Night Illuminations & Parabolic Pylons
        {
            "name": "Cam_19_Engineering_Fountain_Night_Lighting_Plume",
            "loc": (ef_cx + 12.0, ef_cy - 14.0, 4.5),
            "rot": (math.radians(78.0), 0.0, math.radians(42.0)),
            "lens": 24.0
        },
        # 3. Loeb Fountain Founders Park Plaza Arrival View (from University Hall walkway)
        {
            "name": "Cam_20_Loeb_Fountain_FoundersPark_PlazaView",
            "loc": (lf_cx - 18.0, lf_cy + 18.0, 4.2),
            "rot": (math.radians(80.0), 0.0, math.radians(-135.0)),
            "lens": 22.0
        },
        # 4. Loeb Fountain Interactive Deck & Inward Laminar Jets Close-Up
        {
            "name": "Cam_21_Loeb_Fountain_Interactive_Jets_Detail",
            "loc": (lf_cx + 8.5, lf_cy - 7.5, 1.8),
            "rot": (math.radians(84.0), 0.0, math.radians(48.0)),
            "lens": 20.0
        }
    ]
    
    for cfg in cameras:
        if cfg["name"] not in bpy.data.objects:
            cdata = bpy.data.cameras.new(cfg["name"])
            cdata.lens = cfg["lens"]
            cdata.clip_end = 6000.0
            cobj = bpy.data.objects.new(cfg["name"], cdata)
            cobj.location = cfg["loc"]
            cobj.rotation_euler = cfg["rot"]
            col.objects.link(cobj)
        else:
            cobj = bpy.data.objects[cfg["name"]]
            cobj.location = cfg["loc"]
            cobj.rotation_euler = cfg["rot"]
            cobj.data.lens = cfg["lens"]
            
    # Set active camera to Cam_18
    bpy.context.scene.camera = bpy.data.objects["Cam_18_Engineering_Fountain_Hero_GroundView"]
    print("Dedicated fountain inspection cameras calibrated.")

if __name__ == "__main__":
    build_fountains()
