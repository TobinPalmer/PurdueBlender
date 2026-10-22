import bpy
import bmesh
import mathutils
import math
import os

def create_cube_mesh(name, location, scale, material=None, col=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    if material:
        mesh.materials.append(material)
    if col:
        col.objects.link(obj)
    return obj

def clean_or_create_collection(col_name, parent_col=None):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def correct_walc_orientation_and_detail_surroundings():
    print("=== 1. CORRECTING WALC ORIENTATION (-90 DEGREE ROTATION TO REAL CAMPUS AXIS) ===")
    
    walc_col_names = [
        '01 Exterior and plaza', '02 Interior architecture', '03 Mullins Reading Room',
        '04 Furniture and teaching rooms', '05 Review refinements', '06 Circulation and fidelity fixes',
        '07 Detail and classroom completion', '08 Final comparison refinements'
    ]
    
    # Campus surveyed center for WALC
    center_x = 40.0
    center_y = -1.2
    
    rot_flag = "WALC_ROTATION_APPLIED_FLAG"
    if rot_flag not in bpy.data.objects:
        rot_angle = math.radians(-90.0)
        cos_r = math.cos(rot_angle)
        sin_r = math.sin(rot_angle)
        
        rotated_count = 0
        for cname in walc_col_names:
            c = bpy.data.collections.get(cname)
            if c:
                for obj in c.objects:
                    # 1. Rotate location around (center_x, center_y)
                    ox = obj.location.x - center_x
                    oy = obj.location.y - center_y
                    rx = ox * cos_r - oy * sin_r
                    ry = ox * sin_r + oy * cos_r
                    obj.location.x = center_x + rx
                    obj.location.y = center_y + ry
                    
                    # 2. Add -90 degrees to object's rotation
                    obj.rotation_euler[2] += rot_angle
                    rotated_count += 1
                    
        # Add flag via data API
        flag = bpy.data.objects.new(rot_flag, None)
        flag.location = (center_x, center_y, 0)
        flag_col = bpy.data.collections.get("Master_WALC_Detailed")
        if flag_col:
            flag_col.objects.link(flag)
        else:
            bpy.context.scene.collection.objects.link(flag)
            
        print(f"WALC orientation corrected: {rotated_count} objects rotated -90 degrees to face West toward Centennial Mall & Bell Tower!")
    else:
        print("WALC rotation already applied.")
        
    # Re-align WALC entrance apron in 01_Purdue_Road_Network
    if "WALC_Entrance_Herringbone_Brick_Apron" in bpy.data.objects:
        apron = bpy.data.objects["WALC_Entrance_Herringbone_Brick_Apron"]
        apron.location = (10.0, -1.2, 0.11)
        apron.scale = (18.0, 88.0, 0.02)
        print("WALC brick entrance apron re-aligned along West facade.")

    # -------------------------------------------------------------
    # 2. Model Buildings Surrounding WALC to Matching High Fidelity
    # -------------------------------------------------------------
    print("=== 2. MODELING SURROUNDING BUILDINGS TO MATCH WALC QUALITY ===")
    
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick")
    mat_stone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_glass = bpy.data.materials.get("Campus_Reflective_Glass")
    mat_slate = bpy.data.materials.get("Roof_Dark_Slate")
    mat_copper = bpy.data.materials.get("Bell_Tower_Aged_Copper")
    
    # A. Mechanical Engineering (ME) & Gatewood Wing (North of WALC)
    build_mechanical_engineering_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate, mat_copper)
    
    # B. Potter Engineering Center (POTR) (East of WALC / Potter Quad)
    build_potter_center_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate)
    
    # C. Electrical Engineering (EE / BHEE) (Northeast of WALC)
    build_electrical_engineering_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate)
    
    # D. Setup Camera to inspect WALC and surroundings
    setup_walc_surroundings_camera()
    print("=== WALC ORIENTATION AND SURROUNDING BUILDINGS COMPLETE ===")

# -----------------------------------------------------------------
# A. Mechanical Engineering Building (ME) & Gatewood Wing
# -----------------------------------------------------------------
def build_mechanical_engineering_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate, mat_copper):
    col = clean_or_create_collection("09_Mechanical_Engineering_Detailed")
    
    if massing_col:
        for obj in massing_col.objects:
            if "Mechanical Engineering (ME)" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                
    # 1. Main Historic 4-Story Masonry Core (18.5m height)
    create_cube_mesh(
        "ME_Historic_Core_Masonry",
        location=(70.0, 95.0, 9.25),
        scale=(75.0, 32.0, 18.5),
        material=mat_brick,
        col=col
    )
    
    # Limestone Water Table Plinth (z=0 to 2.5m)
    create_cube_mesh(
        "ME_Historic_Limestone_Plinth",
        location=(70.0, 95.0, 1.25),
        scale=(75.8, 32.8, 2.5),
        material=mat_stone,
        col=col
    )
    
    # Limestone Belt Courses & Cornice
    for zh in [6.5, 11.5, 16.5, 18.7]:
        create_cube_mesh(
            f"ME_Limestone_Belt_{int(zh)}",
            location=(70.0, 95.0, zh),
            scale=(75.6, 32.6, 0.45),
            material=mat_stone,
            col=col
        )
        
    # Grand Arched Entrance Portico (Facing West toward Engineering Mall)
    create_cube_mesh(
        "ME_West_Arched_Entrance_Portico",
        location=(32.0, 95.0, 7.5),
        scale=(5.5, 14.0, 15.0),
        material=mat_stone,
        col=col
    )
    
    # 2. Gatewood Wing (Modern Limestone & Solar Glass Wing facing WALC North Breezeway)
    create_cube_mesh(
        "ME_Gatewood_Wing_Structure",
        location=(42.0, 70.0, 10.5),
        scale=(34.0, 16.0, 21.0),
        material=mat_stone,
        col=col
    )
    
    # Gatewood Glass Curtain Wall facing South (toward WALC!)
    create_cube_mesh(
        "ME_Gatewood_South_Glass_CurtainWall",
        location=(42.0, 61.8, 10.5),
        scale=(30.0, 0.4, 18.0),
        material=mat_glass,
        col=col
    )
    
    # Gatewood Dark Slate Roof & Copper Flashing
    create_cube_mesh(
        "ME_Gatewood_Roof_Cap",
        location=(42.0, 70.0, 21.3),
        scale=(34.6, 16.6, 0.6),
        material=mat_slate,
        col=col
    )
    print("Mechanical Engineering Building & Gatewood Wing detailed.")

# -----------------------------------------------------------------
# B. Potter Engineering Center (POTR)
# -----------------------------------------------------------------
def build_potter_center_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate):
    col = clean_or_create_collection("10_Potter_Engineering_Detailed")
    
    if massing_col:
        for obj in massing_col.objects:
            if "Potter" in obj.name or "POTR" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                
    # 3-Story Brick & Limestone Library/Research Building (15.5m high)
    create_cube_mesh(
        "Potter_Center_Masonry_Core",
        location=(82.0, -10.0, 7.75),
        scale=(46.0, 68.0, 15.5),
        material=mat_brick,
        col=col
    )
    
    # Limestone Base & Belt Bands
    for zh in [1.8, 6.2, 11.2, 15.7]:
        create_cube_mesh(
            f"Potter_Limestone_Band_{int(zh)}",
            location=(82.0, -10.0, zh),
            scale=(46.6, 68.6, 0.4),
            material=mat_stone,
            col=col
        )
        
    # Recessed Ribbon Glazing on West Facade facing Potter Quad & WALC
    for zh in [4.0, 8.8, 13.5]:
        create_cube_mesh(
            f"Potter_West_Ribbon_Glass_{int(zh)}",
            location=(58.8, -10.0, zh),
            scale=(0.3, 58.0, 1.8),
            material=mat_glass,
            col=col
        )
        
    # Potter Quad Terraced Plaza Paving (between WALC and Potter)
    create_cube_mesh(
        "Potter_Quad_Terrace_Plaza",
        location=(54.0, -10.0, 0.11),
        scale=(9.0, 64.0, 0.04),
        material=mat_stone,
        col=col
    )
    print("Potter Engineering Center & Potter Quad detailed.")

# -----------------------------------------------------------------
# C. Electrical Engineering (EE / BHEE)
# -----------------------------------------------------------------
def build_electrical_engineering_detailed(massing_col, mat_brick, mat_stone, mat_glass, mat_slate):
    col = clean_or_create_collection("11_Electrical_Engineering_Detailed")
    
    if massing_col:
        for obj in massing_col.objects:
            if "Electrical Engineering" in obj.name or "BHEE" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                
    # 4-Story Historic Collegiate Brick Hall (18.0m high)
    create_cube_mesh(
        "EE_Historic_Masonry_Core",
        location=(145.0, 135.0, 9.0),
        scale=(88.0, 95.0, 18.0),
        material=mat_brick,
        col=col
    )
    
    # Limestone Water Table & String Courses
    for zh in [2.2, 7.0, 12.0, 18.2]:
        create_cube_mesh(
            f"EE_Limestone_StringCourse_{int(zh)}",
            location=(145.0, 135.0, zh),
            scale=(88.8, 95.8, 0.45),
            material=mat_stone,
            col=col
        )
        
    # Classical Arched Entrance Portal on West Facade
    create_cube_mesh(
        "EE_Grand_Arched_Entrance_Portal",
        location=(100.2, 135.0, 8.0),
        scale=(4.0, 16.0, 16.0),
        material=mat_stone,
        col=col
    )
    
    # Slate Hip Roof Cap
    create_cube_mesh(
        "EE_Collegiate_Roof_Cap",
        location=(145.0, 135.0, 19.0),
        scale=(89.0, 96.0, 1.8),
        material=mat_slate,
        col=col
    )
    print("Electrical Engineering Building (BHEE) detailed.")

# -----------------------------------------------------------------
# D. Inspection Camera
# -----------------------------------------------------------------
def setup_walc_surroundings_camera():
    col = clean_or_create_collection("05_Cameras_and_Views")
    cam_name = "Cam_10_WALC_Precinct_CentennialMall"
    if cam_name not in bpy.data.objects:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_data.lens = 24.0
        cam_data.clip_end = 10000.0
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        cam_obj.location = (-65.0, -10.0, 12.0)
        cam_obj.rotation_euler = (math.radians(80.0), 0.0, math.radians(-90.0))
        col.objects.link(cam_obj)
        
    bpy.context.scene.camera = bpy.data.objects[cam_name]
    print(f"Active camera set to {cam_name}")

if __name__ == "__main__":
    correct_walc_orientation_and_detail_surroundings()
