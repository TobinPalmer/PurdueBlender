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

def create_cylinder(name, loc, radius, depth, mat=None, col=None, verts=24):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=radius, radius2=radius, depth=depth)
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

def build_south_hall():
    print("=== MODELING PURDUE SOUTH HALL (EXTERIOR & INTERIOR ARCHITECTURE) ===")
    
    col_ext = clean_or_create_col("12_South_Hall_Exterior")
    col_int = clean_or_create_col("13_South_Hall_Interiors")
    
    # Hide low-poly placeholder in massing collection
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if massing_col:
        for obj in massing_col.objects:
            if "1558636642" in obj.name or "House_1558636642" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                print(f"Hidden low-poly placeholder: {obj.name}")
                
    # Materials Setup
    mat_brick = get_or_make_mat("SouthHall_Purdue_Red_Brick", (0.55, 0.22, 0.16, 1.0), roughness=0.82)
    mat_stone = get_or_make_mat("SouthHall_Bedford_Limestone", (0.84, 0.81, 0.76, 1.0), roughness=0.65)
    mat_glass = get_or_make_mat("SouthHall_Solar_Curtain_Glass", (0.10, 0.18, 0.22, 1.0), roughness=0.04, transmission=0.88)
    mat_metal = get_or_make_mat("SouthHall_Charcoal_Metal_Panels", (0.18, 0.19, 0.20, 1.0), roughness=0.40, metallic=0.6)
    mat_roof = get_or_make_mat("SouthHall_Membrane_Roof", (0.28, 0.28, 0.29, 1.0), roughness=0.85)
    
    # Interior Materials
    mat_terrazzo = get_or_make_mat("SouthHall_Lobby_Terrazzo", (0.88, 0.86, 0.82, 1.0), roughness=0.18)
    mat_oak = get_or_make_mat("SouthHall_Warm_Oak_Woodwork", (0.65, 0.48, 0.28, 1.0), roughness=0.45)
    mat_carpet = get_or_make_mat("SouthHall_Commercial_Carpet_Tile", (0.22, 0.25, 0.28, 1.0), roughness=0.95)
    mat_screen = get_or_make_mat("SouthHall_DataMine_Digital_Screen", (0.05, 0.05, 0.05, 1.0), roughness=0.2, emission=(0.85, 0.95, 1.0, 1.0), emission_strength=2.2)
    mat_whiteboard = get_or_make_mat("SouthHall_Whiteboard_Gloss", (0.96, 0.96, 0.96, 1.0), roughness=0.10)
    mat_billiard = get_or_make_mat("SouthHall_Billiard_Felt_Green", (0.08, 0.32, 0.18, 1.0), roughness=0.88)
    mat_gold_accent = get_or_make_mat("SouthHall_Gold_Acoustic_Fabric", (0.85, 0.65, 0.15, 1.0), roughness=0.75)
    mat_bedding = get_or_make_mat("SouthHall_Dorm_Navy_Bedding", (0.12, 0.18, 0.32, 1.0), roughness=0.85)
    mat_wall_white = get_or_make_mat("SouthHall_Interior_Wall_OffWhite", (0.92, 0.91, 0.88, 1.0), roughness=0.80)
    
    # -------------------------------------------------------------
    # 1. South Hall Site Coordinates & Envelope Dimensions
    # -------------------------------------------------------------
    # 201 N. MacArthur Drive. Center at X = -1096.0, Y = -151.0
    # 8 stories tall: Total Height = 28.5m (94 ft)
    # Footprint: 104m East-West length x 48m North-South width
    cx, cy = -1096.0, -151.0
    b_len = 104.0
    b_wid = 48.0
    b_h = 28.5
    
    print("Building South Hall 8-Story Exterior Facade...")
    
    # A. Ground Floor Podium (Floors 1 & 2 - The Data Mine & Commons)
    # Soaring double-height glass curtain wall base (z = 0 to 7.2m)
    create_box(
        "SouthHall_GroundFloor_Glass_Podium",
        loc=(cx, cy, 3.6),
        size=(b_len + 0.2, b_wid + 0.2, 7.2),
        mat=mat_glass,
        col=col_ext
    )
    
    # Ground Floor Limestone Pier Columns (spacing every 12m)
    for x_step in range(-48, 50, 12):
        for side in [-b_wid*0.5, b_wid*0.5]:
            create_box(
                f"SouthHall_Podium_Limestone_Pier_{x_step}_{int(side)}",
                loc=(cx + x_step, cy + side, 3.6),
                size=(0.9, 0.9, 7.2),
                mat=mat_stone,
                col=col_ext
            )
            
    # B. Upper Residential Floors (Floors 3 through 8 - Stories 3 to 8, z = 7.2m to 28.5m)
    create_box(
        "SouthHall_Residential_Masonry_Core",
        loc=(cx, cy, 17.85),
        size=(b_len, b_wid, 21.3),
        mat=mat_brick,
        col=col_ext
    )
    
    # Limestone Belt Courses at Each Floor Level (Levels 2, 3, 4, 5, 6, 7, 8 & Parapet)
    for fl_z in [7.2, 10.75, 14.3, 17.85, 21.4, 24.95, 28.5]:
        create_box(
            f"SouthHall_Limestone_Belt_Level_{int(fl_z*10)}",
            loc=(cx, cy, fl_z),
            size=(b_len + 0.6, b_wid + 0.6, 0.4),
            mat=mat_stone,
            col=col_ext
        )
        
    # Vertical Brick Pilasters & Charcoal Spandrel Window Bays
    # Front Facade (Facing MacArthur Drive / East, X = +b_len*0.5)
    for y_pos in range(int(-b_wid*0.5 + 4), int(b_wid*0.5 - 2), 6):
        # Vertical brick pilaster
        create_box(
            f"SouthHall_MacArthur_Vertical_Pilaster_{y_pos}",
            loc=(cx + b_len*0.5 + 0.3, cy + y_pos, 17.85),
            size=(0.6, 1.2, 21.3),
            mat=mat_brick,
            col=col_ext
        )
        # Charcoal architectural spandrel panels between windows
        for fl_z in [9.0, 12.5, 16.1, 19.6, 23.2, 26.7]:
            create_box(
                f"SouthHall_SpandrelPanel_{y_pos}_{int(fl_z*10)}",
                loc=(cx + b_len*0.5 + 0.1, cy + y_pos + 3.0, fl_z),
                size=(0.2, 4.0, 1.8),
                mat=mat_metal,
                col=col_ext
            )
            # Window glass
            create_box(
                f"SouthHall_DormWindow_{y_pos}_{int(fl_z*10)}",
                loc=(cx + b_len*0.5 + 0.15, cy + y_pos + 3.0, fl_z + 1.1),
                size=(0.15, 3.8, 1.4),
                mat=mat_glass,
                col=col_ext
            )
            
    # C. Soaring Corner Study Lounges (Floor-to-Ceiling Glass Corners on Floors 2–8)
    for cx_mult in [-1, 1]:
        for cy_mult in [-1, 1]:
            create_box(
                f"SouthHall_CornerLounge_CurtainWall_{cx_mult}_{cy_mult}",
                loc=(cx + cx_mult * (b_len*0.5 - 5.0), cy + cy_mult * (b_wid*0.5 - 5.0), 17.85),
                size=(10.5, 10.5, 21.3),
                mat=mat_glass,
                col=col_ext
            )
            
    # D. Monumental MacArthur Drive Entrance Portal & Canopy
    # Located on East facade facing MacArthur Drive: (cx + b_len*0.5, cy, z = 4.2)
    canopy_x = cx + b_len*0.5 + 4.5
    create_box(
        "SouthHall_MacArthur_Entrance_Canopy",
        loc=(canopy_x, cy, 4.8),
        size=(9.0, 16.0, 0.5),
        mat=mat_metal,
        col=col_ext
    )
    # Entrance Glass Vestibule & Revolving Doors
    create_box(
        "SouthHall_Entrance_Vestibule_Glass",
        loc=(cx + b_len*0.5 + 0.5, cy, 2.4),
        size=(2.0, 14.0, 4.8),
        mat=mat_glass,
        col=col_ext
    )
    # Dressed Limestone Signage Portal
    create_box(
        "SouthHall_Limestone_Signage_Pylon",
        loc=(canopy_x + 3.5, cy - 9.0, 1.8),
        size=(0.8, 4.2, 3.6),
        mat=mat_stone,
        col=col_ext
    )
    
    # E. Enclosed Skybridge Connector to Hillenbrand Hall
    # Spanning North from South Hall into Hillenbrand Dining Court (42m length)
    bridge_len = 40.0
    bridge_y = cy + b_wid*0.5 + bridge_len*0.5
    create_box(
        "SouthHall_Hillenbrand_Skybridge_Connector",
        loc=(cx, bridge_y, 4.5),
        size=(5.5, bridge_len, 6.0),
        mat=mat_glass,
        col=col_ext
    )
    for bz in [1.5, 7.5]:
        create_box(
            f"SouthHall_Skybridge_Slab_{int(bz)}",
            loc=(cx, bridge_y, bz),
            size=(5.9, bridge_len, 0.4),
            mat=mat_metal,
            col=col_ext
        )
        
    # F. Rooftop Mechanical Penthouse Screen
    create_box(
        "SouthHall_Rooftop_Mechanical_Penthouse",
        loc=(cx, cy, 30.2),
        size=(36.0, 20.0, 3.4),
        mat=mat_metal,
        col=col_ext
    )
    
    # -------------------------------------------------------------
    # 2. Detailed Photorealistic Interior Architecture
    # -------------------------------------------------------------
    print("Building South Hall Photorealistic Interiors...")
    
    # Floor 1 Ground Slab (Terrazzo)
    create_box(
        "SouthHall_GroundFloor_Terrazzo_Slab",
        loc=(cx, cy, 0.1),
        size=(b_len - 0.4, b_wid - 0.4, 0.2),
        mat=mat_terrazzo,
        col=col_int
    )
    
    # A. Reception & Commons Welcome Lobby (East wing, Ground Floor)
    # Curved Welcome Desk
    create_box(
        "SouthHall_Lobby_Reception_Desk_Base",
        loc=(cx + 28.0, cy, 0.65),
        size=(3.2, 8.5, 1.1),
        mat=mat_oak,
        col=col_int
    )
    # Solid White Quartz Countertop
    create_box(
        "SouthHall_Reception_Quartz_Countertop",
        loc=(cx + 28.0, cy, 1.18),
        size=(3.5, 8.8, 0.1),
        mat=mat_stone,
        col=col_int
    )
    # Lobby Lounge Sofa Islands & Seating Pods
    for so_y in [-10.0, 10.0]:
        create_box(
            f"SouthHall_Lobby_Modular_Sofa_{int(so_y)}",
            loc=(cx + 34.0, cy + so_y, 0.5),
            size=(3.8, 7.5, 0.85),
            mat=mat_metal,
            col=col_int
        )
        create_box(
            f"SouthHall_Lobby_Lounge_Armchair_Gold_{int(so_y)}",
            loc=(cx + 38.0, cy + so_y, 0.55),
            size=(1.4, 1.4, 0.9),
            mat=mat_gold_accent,
            col=col_int
        )
        
    # B. The Data Mine Learning Labs (Center Wing - 9 Collaborative Suites)
    # Demising Glass Partitions separating the collaborative labs
    for lab_idx in range(-3, 4):
        lx = cx + lab_idx * 11.5
        # Lab dividing glass wall
        create_box(
            f"DataMine_Lab_Glass_Partition_{lab_idx+4}",
            loc=(lx, cy + 6.0, 3.0),
            size=(0.15, 20.0, 5.8),
            mat=mat_glass,
            col=col_int
        )
        # Collaboration Team Table in each lab
        create_box(
            f"DataMine_Lab_Team_Table_{lab_idx+4}",
            loc=(lx + 5.5, cy + 6.0, 0.75),
            size=(4.8, 2.2, 0.75),
            mat=mat_oak,
            col=col_int
        )
        # 75-Inch Wall-Mounted Digital Presentation Display (Emissive screen)
        create_box(
            f"DataMine_Lab_75in_Digital_Display_{lab_idx+4}",
            loc=(lx, cy + 6.0, 2.4),
            size=(0.08, 1.8, 1.05),
            mat=mat_screen,
            col=col_int
        )
        # Magnetic Whiteboard Wall
        create_box(
            f"DataMine_Lab_Magnetic_Whiteboard_{lab_idx+4}",
            loc=(lx + 5.5, cy + 15.8, 2.0),
            size=(4.5, 0.08, 1.8),
            mat=mat_whiteboard,
            col=col_int
        )
        
    # C. Recreation & Gaming Lounge (West Wing Ground Floor)
    # Regulation Tournament Slate Billiard Table
    create_box(
        "SouthHall_Billiard_Table_Frame",
        loc=(cx - 35.0, cy - 8.0, 0.45),
        size=(3.1, 1.7, 0.8),
        mat=mat_oak,
        col=col_int
    )
    # Emerald Green Felt Playing Surface
    create_box(
        "SouthHall_Billiard_Table_Green_Felt",
        loc=(cx - 35.0, cy - 8.0, 0.88),
        size=(2.8, 1.4, 0.06),
        mat=mat_billiard,
        col=col_int
    )
    # Ping Pong / Table Tennis Table
    create_box(
        "SouthHall_TableTennis_Table",
        loc=(cx - 35.0, cy + 8.0, 0.78),
        size=(3.0, 1.6, 0.76),
        mat=mat_metal,
        col=col_int
    )
    # Video Gaming Alcove Wall Displays
    for gi in [-3.0, 3.0]:
        create_box(
            f"SouthHall_Gaming_Wall_Display_{int(gi)}",
            loc=(cx - 45.0, cy + gi, 2.2),
            size=(0.08, 1.6, 0.95),
            mat=mat_screen,
            col=col_int
        )
        
    # D. Retail Dining (*Sushi Boss* Counter & Seating)
    # Located in South-East Ground Floor Corner: (cx + 25.0, cy - 14.0)
    create_box(
        "SouthHall_SushiBoss_Service_Counter",
        loc=(cx + 22.0, cy - 14.0, 0.6),
        size=(2.4, 9.5, 1.1),
        mat=mat_metal,
        col=col_int
    )
    # Refrigerated Glass Display & Sneeze Guard
    create_box(
        "SouthHall_SushiBoss_Refrigerated_Display",
        loc=(cx + 22.0, cy - 14.0, 1.35),
        size=(1.2, 8.5, 0.5),
        mat=mat_glass,
        col=col_int
    )
    # Overhead Digital Menu Boards (3-screen array)
    create_box(
        "SouthHall_SushiBoss_Overhead_Menu_Screens",
        loc=(cx + 22.0, cy - 14.0, 3.2),
        size=(0.1, 7.5, 1.1),
        mat=mat_screen,
        col=col_int
    )
    # Touchscreen Ordering Kiosk
    create_box(
        "SouthHall_SushiBoss_Touchscreen_Kiosk",
        loc=(cx + 17.0, cy - 18.0, 1.1),
        size=(0.6, 0.6, 1.6),
        mat=mat_metal,
        col=col_int
    )
    
    # -------------------------------------------------------------
    # 3. Upper Residential Floors (Floor 2 Representative Level)
    # -------------------------------------------------------------
    # Floor 2 Slab (z = 7.2m)
    create_box(
        "SouthHall_Floor2_Carpet_Slab",
        loc=(cx, cy, 7.3),
        size=(b_len - 0.4, b_wid - 0.4, 0.2),
        mat=mat_carpet,
        col=col_int
    )
    
    # Central Double-Loaded Residential Corridor (2.2m width along X)
    # Demising Corridor Walls
    for side in [-2.0, 2.0]:
        create_box(
            f"SouthHall_Floor2_Corridor_Wall_{'North' if side>0 else 'South'}",
            loc=(cx, cy + side * 1.8, 9.0),
            size=(b_len - 2.0, 0.2, 3.2),
            mat=mat_wall_white,
            col=col_int
        )
        
    # Representative Student Dorm Suite (Room 214 - Single/Double Room)
    # Location: North side of corridor (cx - 15.0, cy + 12.0)
    suite_cx, suite_cy = cx - 15.0, cy + 12.0
    # Room demising walls (2.6m x 5.15m interior)
    create_box(
        "SouthHall_Dorm_Room214_WestWall",
        loc=(suite_cx - 2.6, suite_cy, 9.0),
        size=(0.15, 6.2, 3.2),
        mat=mat_wall_white,
        col=col_int
    )
    create_box(
        "SouthHall_Dorm_Room214_EastWall",
        loc=(suite_cx + 2.6, suite_cy, 9.0),
        size=(0.15, 6.2, 3.2),
        mat=mat_wall_white,
        col=col_int
    )
    # Twin-XL Bed Frame & Mattress
    create_box(
        "SouthHall_Dorm_TwinXL_BedFrame",
        loc=(suite_cx - 1.6, suite_cy + 1.2, 7.8),
        size=(1.1, 2.15, 0.7),
        mat=mat_oak,
        col=col_int
    )
    create_box(
        "SouthHall_Dorm_Navy_Quilted_Mattress",
        loc=(suite_cx - 1.6, suite_cy + 1.2, 8.2),
        size=(1.0, 2.05, 0.25),
        mat=mat_bedding,
        col=col_int
    )
    # Solid Oak Study Desk & Hutch
    create_box(
        "SouthHall_Dorm_StudyDesk",
        loc=(suite_cx + 1.6, suite_cy + 1.2, 8.0),
        size=(0.85, 1.35, 0.75),
        mat=mat_oak,
        col=col_int
    )
    create_box(
        "SouthHall_Dorm_Desk_Hutch_Bookshelf",
        loc=(suite_cx + 1.6, suite_cy + 1.2, 8.8),
        size=(0.35, 1.35, 0.8),
        mat=mat_oak,
        col=col_int
    )
    # Ergonomic Student Desk Chair
    create_box(
        "SouthHall_Dorm_Desk_Chair",
        loc=(suite_cx + 1.0, suite_cy + 1.2, 7.9),
        size=(0.6, 0.6, 0.85),
        mat=mat_metal,
        col=col_int
    )
    # Wardrobe Closet & 3-Drawer Dresser
    create_box(
        "SouthHall_Dorm_Wardrobe_Closet",
        loc=(suite_cx - 1.6, suite_cy - 1.8, 8.6),
        size=(0.85, 1.1, 2.0),
        mat=mat_oak,
        col=col_int
    )
    create_box(
        "SouthHall_Dorm_3Drawer_Dresser",
        loc=(suite_cx + 1.6, suite_cy - 1.8, 8.0),
        size=(0.7, 0.95, 0.85),
        mat=mat_oak,
        col=col_int
    )
    
    # -------------------------------------------------------------
    # 4. Setup Dedicated Inspection Cameras
    # -------------------------------------------------------------
    setup_south_hall_cameras(cx, cy, b_len, b_wid)
    print("=== PURDUE SOUTH HALL MODELING COMPLETED SUCCESSFULLY ===")

def setup_south_hall_cameras(cx, cy, b_len, b_wid):
    col = clean_or_create_col("05_Cameras_and_Views")
    
    cameras = [
        # 1. Street View facing South Hall Main Entrance from MacArthur Drive
        {
            "name": "Cam_11_South_Hall_MacArthur_StreetView",
            "loc": (cx + b_len*0.5 + 32.0, cy - 8.0, 3.2),
            "rot": (math.radians(85.0), 0.0, math.radians(72.0)),
            "lens": 24.0
        },
        # 2. Interior View inside Ground Floor Lobby & Data Mine Labs
        {
            "name": "Cam_12_South_Hall_DataMine_Lobby_Interior",
            "loc": (cx + 32.0, cy - 8.0, 2.0),
            "rot": (math.radians(88.0), 0.0, math.radians(-115.0)),
            "lens": 20.0 # Wide angle for interior
        },
        # 3. Interior View inside Student Dormitory Room (Room 214)
        {
            "name": "Cam_13_South_Hall_Student_Dorm_Interior",
            "loc": (cx - 15.0, cy + 9.5, 8.5),
            "rot": (math.radians(82.0), 0.0, 0.0),
            "lens": 18.0 # Ultra-wide for dorm room
        }
    ]
    
    for cfg in cameras:
        if cfg["name"] not in bpy.data.objects:
            cdata = bpy.data.cameras.new(cfg["name"])
            cdata.lens = cfg["lens"]
            cdata.clip_end = 5000.0
            cobj = bpy.data.objects.new(cfg["name"], cdata)
            cobj.location = cfg["loc"]
            cobj.rotation_euler = cfg["rot"]
            col.objects.link(cobj)
            
    # Set active camera to Cam_11
    bpy.context.scene.camera = bpy.data.objects["Cam_11_South_Hall_MacArthur_StreetView"]
    print("South Hall Street View and Interior cameras calibrated.")

if __name__ == "__main__":
    build_south_hall()
