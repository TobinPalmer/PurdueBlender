import bpy
import mathutils
from mathutils import Matrix, Vector
import math
import os

def import_walc_flawless():
    print("=========================================================")
    print("=== FLAWLESS FRESH IMPORT OF WALC WITH EXACT ISOMETRY ===")
    print("=========================================================")
    
    source_blend = r"C:\Users\Tobin\Documents\Codex\2026-10-21\use-the-blender-mcp-to-create-2\outputs\Purdue_WALC.blend"
    if not os.path.exists(source_blend):
        raise FileNotFoundError(f"Source file not found: {source_blend}")

    # -------------------------------------------------------------
    # 1. PURGE ALL EXISTING WALC OBJECTS AND COLLECTIONS
    # -------------------------------------------------------------
    print("Step 1: Purging all existing WALC objects and collections...")
    
    # Remove collections that match WALC patterns
    for c in list(bpy.data.collections):
        name_lower = c.name.lower()
        if any(k in name_lower for k in [
            'exterior and plaza', 'interior architecture', 'mullins reading',
            'furniture and teaching', 'review refinements', 'circulation and fidelity',
            'detail and classroom', 'final comparison', 'walc'
        ]):
            for o in list(c.objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
            
    # Also remove any loose objects in Scene Collection matching WALC keywords
    walc_keywords = [
        'walc', 'wilmeth', 'mullins', 'atrium daylight', 'reading room fill',
        'atrium practical', 'reading lateral bounce', 'theatre house lighting',
        'library diffuse fill', 'cafe identifier', 'building name', 'interior nameplate',
        'classroom room number', 'menu lettering', 'documented reading room artwork',
        '01 plaza reference', '02 aerial reference', '03 reading room reference',
        '04 atrium reference', '05 atrium stairs', '06 library stacks', '07 hiler theatre',
        '08 active learning', '09 basement'
    ]
    for o in list(bpy.data.objects):
        name_lower = o.name.lower()
        if any(k in name_lower for k in walc_keywords):
            if o.name.startswith("Cam_") and not "reference" in name_lower and not "plaza reference" in name_lower:
                continue
            if "apron" in name_lower or "road" in name_lower or "mall" in name_lower or "massing" in name_lower:
                continue
            bpy.data.objects.remove(o, do_unlink=True)
            
    print(f"Purge complete. Remaining scene objects: {len(bpy.data.objects)}")

    # -------------------------------------------------------------
    # 2. LOAD SOURCE SCENE FROM Purdue_WALC.blend
    # -------------------------------------------------------------
    print("Step 2: Loading source scene from Purdue_WALC.blend...")
    with bpy.data.libraries.load(source_blend) as (data_from, data_to):
        data_to.scenes = ['WALC | reference reconstruction.001']
        
    src_scene = data_to.scenes[0]
    print(f"Source scene loaded: '{src_scene.name}' with {len(src_scene.objects)} objects.")

    # -------------------------------------------------------------
    # 3. CREATE CLEAN COLLECTION HIERARCHY
    # -------------------------------------------------------------
    print("Step 3: Creating Master_WALC_Detailed collection hierarchy...")
    master_col = bpy.data.collections.new("Master_WALC_Detailed")
    bpy.context.scene.collection.children.link(master_col)
    
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
    
    # Store objects and their true local transforms (matrix_basis)
    object_orig_transforms = {}
    imported_objects = set()
    
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
                # Capture the true matrix_basis BEFORE touching the object
                object_orig_transforms[o] = o.matrix_basis.copy()
                target_col.objects.link(o)
                imported_objects.add(o)
                
    # Root objects (fonts, lights, cameras, artwork)
    lighting_col = bpy.data.collections.new("09_WALC_Lighting_Signage_and_Artwork")
    master_col.children.link(lighting_col)
    
    for o in src_scene.collection.objects:
        object_orig_transforms[o] = o.matrix_basis.copy()
        lighting_col.objects.link(o)
        imported_objects.add(o)
        
    print(f"Total objects imported across all 9 collections: {len(imported_objects)}")

    # Unlink and remove the temporary source scene
    bpy.data.scenes.remove(src_scene)

    # -------------------------------------------------------------
    # 4. RIGID ISOMETRY TRANSFORMATION MATRIX
    # -------------------------------------------------------------
    # Georeferenced Surveyed Center of WALC on Purdue Campus:
    # OSM Footprint: X in [10.08, 69.78] -> Center X = 39.93m
    #                Y in [-45.25, 42.82] -> Center Y = -1.22m
    #                Z = 0.00m (Campus ground level)
    # Rotation: -90 degrees around Z axis (-pi/2)
    # This transforms:
    # - Front facade (which faces -Y in source) to face -X (West toward Centennial Mall & Bell Tower)
    # - Long axis (which runs along X, span 78-94m) to run along Y (North-South)
    
    trans_vec = Vector((39.93, -1.22, 0.0))
    rot_angle = -math.pi / 2.0
    
    M_trans = Matrix.Translation(trans_vec)
    M_rot = Matrix.Rotation(rot_angle, 4, 'Z')
    M_world = M_trans @ M_rot
    
    print("\nTransformation Isometry Matrix:")
    for row in M_world:
        print("  ", [round(v, 4) for v in row])

    # Apply M_world @ orig_matrix to every single object
    transformed_count = 0
    for o in imported_objects:
        orig_mat = object_orig_transforms[o]
        new_mat = M_world @ orig_mat
        o.matrix_world = new_mat
        transformed_count += 1
        
    bpy.context.view_layer.update()
    print(f"Successfully transformed all {transformed_count} objects with identical isometry.")

    # -------------------------------------------------------------
    # 5. RIGOROUS GEOMETRIC VERIFICATION
    # -------------------------------------------------------------
    print("\n=== VERIFICATION OF OBJECT LOCATIONS AND BOUNDS ===")
    
    # Check Building Name Font
    for o in imported_objects:
        if "building name" in o.name.lower():
            print(f"Building Name: loc={tuple(round(x, 2) for x in o.location)}, rot={tuple(round(math.degrees(x), 1) for x in o.rotation_euler)}")
        if "cafe identifier" in o.name.lower():
            print(f"Cafe Identifier: loc={tuple(round(x, 2) for x in o.location)}, rot={tuple(round(math.degrees(x), 1) for x in o.rotation_euler)}")
        if "reading carpet" in o.name.lower():
            print(f"Reading Carpet: loc={tuple(round(x, 2) for x in o.location)}")
        if "atrium daylight" in o.name.lower() and not "." in o.name:
            print(f"Atrium Daylight Light: loc={tuple(round(x, 2) for x in o.location)}")

    # Check overall mesh bounding box
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
                
    print(f"\nTotal Mesh Objects in WALC: {mesh_count}")
    print(f"Global Mesh Bounding Box: X=[{min_x:.2f}, {max_x:.2f}] (span={max_x - min_x:.2f}m)")
    print(f"                          Y=[{min_y:.2f}, {max_y:.2f}] (span={max_y - min_y:.2f}m)")
    print(f"                          Z=[{min_z:.2f}, {max_z:.2f}] (span={max_z - min_z:.2f}m)")
    print(f"Center: X={(min_x + max_x)/2:.2f}, Y={(min_y + max_y)/2:.2f}")

    # Re-align entrance brick apron
    apron = bpy.data.objects.get("WALC_Entrance_Herringbone_Brick_Apron")
    if apron:
        apron.location = (10.0, -1.2, 0.11)
        apron.scale = (18.0 / 55.0, 88.0 / 85.0, 1.0)
        apron.rotation_euler = (0.0, 0.0, 0.0)
        print("Aligned WALC_Entrance_Herringbone_Brick_Apron along West facade.")

    # Calibrate inspection camera Cam_10_WALC_Precinct_CentennialMall
    cam = bpy.data.objects.get("Cam_10_WALC_Precinct_CentennialMall")
    if cam:
        cam.location = (-35.0, -1.2, 14.0)
        direction = Vector((39.93, -1.22, 8.0)) - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam
        print("Calibrated Cam_10_WALC_Precinct_CentennialMall looking East toward WALC.")

    # Save master file
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master file saved successfully: {save_path}")

if __name__ == "__main__":
    import_walc_flawless()
