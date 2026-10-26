import bpy
import mathutils
from mathutils import Matrix, Vector
import math
import os

def import_walc_from_scratch():
    print("=========================================================")
    print("=== IMPORTING WALC FROM SCRATCH WITH EQUAL TRANSFORMS ===")
    print("=========================================================")
    
    source_blend = r"C:\Users\Tobin\Documents\Codex\2026-10-21\use-the-blender-mcp-to-create-2\outputs\Purdue_WALC.blend"
    if not os.path.exists(source_blend):
        raise FileNotFoundError(f"Source file not found: {source_blend}")
        
    # 1. First, make sure any leftover collections/objects are cleaned
    old_col_names = [
        '01 Exterior and plaza', '02 Interior architecture', '03 Mullins Reading Room',
        '04 Furniture and teaching rooms', '05 Review refinements', '06 Circulation and fidelity fixes',
        '07 Detail and classroom completion', '08 Final comparison refinements',
        'Master_WALC_Detailed', '00_WALC_Features_and_Lighting'
    ]
    for cname in old_col_names:
        c = bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
            
    # Also clean orphaned stub collections
    for c in list(bpy.data.collections):
        if any(k in c.name.lower() for k in ['exterior and plaza', 'interior architecture', 'mullins reading', 'furniture and teaching', 'review refinements', 'circulation and fidelity', 'detail and classroom', 'final comparison', 'walc']):
            for o in list(c.objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
            
    # 2. Append the scene from Purdue_WALC.blend to get all collections and objects
    with bpy.data.libraries.load(source_blend) as (data_from, data_to):
        data_to.scenes = ['WALC | reference reconstruction.001']
        
    src_scene = data_to.scenes[0]
    print(f"Loaded source scene '{src_scene.name}' with {len(src_scene.objects)} objects.")
    
    # Create the master WALC collection in current scene
    master_col = bpy.data.collections.new("Master_WALC_Detailed")
    bpy.context.scene.collection.children.link(master_col)
    
    # Mapping of child collections
    imported_objects = set()
    
    # Process child collections from source scene
    collection_mapping = {
        '01 Exterior and plaza': '01_WALC_Exterior_and_Plaza',
        '02 Interior architecture': '02_WALC_Interior_Architecture',
        '03 Mullins Reading Room': '03_WALC_Mullins_Reading_Room',
        '04 Furniture and teaching rooms': '04_WALC_Furniture_and_Classrooms',
        '05 Review refinements': '05_WALC_Review_Refinements',
        '06 Circulation and fidelity fixes': '06_WALC_Circulation_and_Stairs',
        '07 Detail and classroom completion': '07_WALC_Detail_and_Auditorium',
        '08 Final comparison refinements': '08_WALC_Final_Fidelity_Refinements'
    }
    
    for src_cname, target_cname in collection_mapping.items():
        src_c = None
        for c in src_scene.collection.children:
            if src_cname in c.name:
                src_c = c
                break
        
        target_col = bpy.data.collections.new(target_cname)
        master_col.children.link(target_col)
        
        if src_c:
            for o in src_c.objects:
                target_col.objects.link(o)
                imported_objects.add(o)
                
    # Process objects that were directly in Scene Collection of src_scene (fonts, lights, cameras, artwork)
    lighting_col = bpy.data.collections.new("09_WALC_Lighting_Signage_and_Artwork")
    master_col.children.link(lighting_col)
    
    for o in src_scene.collection.objects:
        lighting_col.objects.link(o)
        imported_objects.add(o)
        
    print(f"Total objects imported across all WALC collections: {len(imported_objects)}")
    
    # 3. Clean up the temporary source scene from bpy.data.scenes
    bpy.data.scenes.remove(src_scene)
    
    # 4. Rigorous Isometry Transformation Matrix
    # Origin in Purdue Campus Coordinates (center of surveyed OSM footprint):
    # OSM WALC bounds: X=[10.08, 69.78] -> Center X = 39.93m
    #                  Y=[-45.25, 42.82] -> Center Y = -1.22m
    #                  Z=0.0m (Plaza grade)
    # Rotation: -90 degrees (-pi/2) around Z so front facade facing -Y now faces -X (West toward Centennial Mall & Bell Tower)
    
    trans_vec = Vector((39.93, -1.22, 0.0))
    rot_angle = -math.pi / 2.0
    
    M_trans = Matrix.Translation(trans_vec)
    M_rot = Matrix.Rotation(rot_angle, 4, 'Z')
    M_world = M_trans @ M_rot
    
    print("Transformation Matrix:")
    for row in M_world:
        print("  ", [round(val, 4) for val in row])
        
    # Apply transformation equally to every single imported object
    transformed_count = 0
    for o in imported_objects:
        # Guarantee object has no parent
        o.parent = None
        # Apply the exact matrix
        o.matrix_world = M_world @ o.matrix_world
        transformed_count += 1
        
    bpy.context.view_layer.update()
    print(f"Successfully transformed {transformed_count} WALC objects with identical isometry matrix.")
    
    # 5. Verification of Bounding Box
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')
    
    mesh_count = 0
    for o in imported_objects:
        if o.type == 'MESH':
            mesh_count += 1
            for corner in o.bound_box:
                wco = o.matrix_world @ Vector(corner)
                min_x = min(min_x, wco.x)
                max_x = max(max_x, wco.x)
                min_y = min(min_y, wco.y)
                max_y = max(max_y, wco.y)
                min_z = min(min_z, wco.z)
                max_z = max(max_z, wco.z)
                
    print("\n=== VERIFICATION RESULTS ===")
    print(f"Transformed Mesh Objects: {mesh_count}")
    print(f"Global Bounding Box: X=[{min_x:.2f}, {max_x:.2f}] (span={max_x-min_x:.2f}m)")
    print(f"                     Y=[{min_y:.2f}, {max_y:.2f}] (span={max_y-min_y:.2f}m)")
    print(f"                     Z=[{min_z:.2f}, {max_z:.2f}] (span={max_z-min_z:.2f}m)")
    print(f"Center: X={(min_x+max_x)/2:.2f}, Y={(min_y+max_y)/2:.2f}")
    
    # Check specific landmark objects
    bldg_name = bpy.data.objects.get("Building name")
    if bldg_name:
        print(f"Building Name Location: {tuple(round(x, 2) for x in bldg_name.location)}, Rot: {tuple(round(math.degrees(x), 1) for x in bldg_name.rotation_euler)}")
    
    cafe_id = bpy.data.objects.get("Cafe identifier")
    if cafe_id:
        print(f"Cafe Identifier Location: {tuple(round(x, 2) for x in cafe_id.location)}, Rot: {tuple(round(math.degrees(x), 1) for x in cafe_id.rotation_euler)}")
        
    reading_carpet = bpy.data.objects.get("Reading carpet")
    if reading_carpet:
        print(f"Reading Carpet Location: {tuple(round(x, 2) for x in reading_carpet.location)}")
        
    # Re-align WALC entrance apron in 01_Purdue_Road_Network if present
    apron = bpy.data.objects.get("WALC_Entrance_Herringbone_Brick_Apron")
    if apron:
        apron.location = (10.0, -1.2, 0.11)
        apron.scale = (18.0 / 55.0, 88.0 / 85.0, 1.0)
        apron.rotation_euler = (0.0, 0.0, 0.0)
        print("WALC entrance brick apron re-aligned along West facade.")
        
    # Set up inspection camera Cam_10_WALC_Precinct_CentennialMall
    cam = bpy.data.objects.get("Cam_10_WALC_Precinct_CentennialMall")
    if cam:
        cam.location = (-35.0, -1.2, 14.0)
        direction = Vector((39.93, -1.22, 8.0)) - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam
        print("Cam_10_WALC_Precinct_CentennialMall calibrated looking East at WALC.")

    # Save master blend file
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Saved master file to {save_path}")

if __name__ == "__main__":
    import_walc_from_scratch()
