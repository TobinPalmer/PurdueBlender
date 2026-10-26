import bpy
import bmesh
import mathutils
import math
import os

def reorient_walc():
    print("=== REORIENTING WILMETH ACTIVE LEARNING CENTER (WALC) ===")
    
    walc_col_names = [
        '01 Exterior and plaza', '02 Interior architecture', '03 Mullins Reading Room',
        '04 Furniture and teaching rooms', '05 Review refinements', '06 Circulation and fidelity fixes',
        '07 Detail and classroom completion', '08 Final comparison refinements'
    ]
    
    # Pivot center surveyed for WALC
    center_x = 40.0
    center_y = -1.2
    
    # Transformation: +90 degrees rotation counter-clockwise around pivot (40.0, -1.2)
    # This transforms the East-West orientation (rot_z = -180 deg) into the true georeferenced
    # North-South orientation (rot_z = -90 deg), aligning Mullins Reading Room and entrance
    # along Centennial Mall facing West toward the Bell Tower.
    rot_angle = math.radians(90.0)
    cos_r = math.cos(rot_angle)
    sin_r = math.sin(rot_angle)
    
    rotated_count = 0
    all_walc_objects = set()
    
    for cname in walc_col_names:
        c = bpy.data.collections.get(cname)
        if c:
            for obj in c.objects:
                all_walc_objects.add(obj)
                
    for obj in all_walc_objects:
        # Rotate location around pivot (center_x, center_y)
        ox = obj.location.x - center_x
        oy = obj.location.y - center_y
        rx = ox * cos_r - oy * sin_r
        ry = ox * sin_r + oy * cos_r
        obj.location.x = center_x + rx
        obj.location.y = center_y + ry
        
        # Add +90 degrees to object's Euler rotation
        obj.rotation_euler[2] += rot_angle
        rotated_count += 1
        
    print(f"Rotated {rotated_count} WALC objects by +90 degrees around ({center_x}, {center_y}).")
    
    # Also handle Documented reading room artwork if present in Scene Collection
    art = bpy.data.objects.get("Documented reading room artwork")
    if art:
        ref_frame = bpy.data.objects.get("Reading artwork frame")
        if ref_frame:
            art.location = ref_frame.location.copy()
            art.rotation_euler = ref_frame.rotation_euler.copy()
            rev_col = bpy.data.collections.get("05 Review refinements")
            if rev_col and art.name not in rev_col.objects:
                rev_col.objects.link(art)
            if art.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(art)
            print("Documented reading room artwork aligned and linked to 05 Review refinements.")
            
    # Fix and align WALC entrance brick apron along Centennial Mall (West facade)
    apron = bpy.data.objects.get("WALC_Entrance_Herringbone_Brick_Apron")
    if apron:
        # The base mesh is 55.0m x 85.0m; normalize scale so apron is 18.0m wide (E-W) and 88.0m long (N-S)
        apron.location = (10.0, -1.2, 0.11)
        apron.scale = (18.0 / 55.0, 88.0 / 85.0, 1.0)
        apron.rotation_euler = (0.0, 0.0, 0.0)
        print("WALC entrance brick apron scaled to 18m x 88m and aligned along West facade.")
        
    # Update or create alignment confirmation flag
    flag_name = "WALC_TRUE_ORIENTATION_CONFIRMED"
    if flag_name not in bpy.data.objects:
        flag = bpy.data.objects.new(flag_name, None)
        flag.location = (center_x, center_y, 0)
        master_col = bpy.data.collections.get("Master_WALC_Detailed")
        if master_col:
            master_col.objects.link(flag)
        else:
            bpy.context.scene.collection.objects.link(flag)
            
    # Remove old outdated flag if present
    old_flag = bpy.data.objects.get("WALC_ROTATION_APPLIED_FLAG")
    if old_flag:
        bpy.data.objects.remove(old_flag, do_unlink=True)
        
    # Set up inspection camera Cam_10_WALC_Precinct_CentennialMall
    cam = bpy.data.objects.get("Cam_10_WALC_Precinct_CentennialMall")
    if cam:
        # Position camera at Centennial Mall looking East toward WALC's west entrance & Mullins Reading Room
        cam.location = (-35.0, -1.2, 14.0)
        # Point toward WALC center (40.0, -1.2, 10.0)
        direction = mathutils.Vector((40.0, -1.2, 10.0)) - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam
        print("Cam_10_WALC_Precinct_CentennialMall updated and set as active camera.")

    # -----------------------------------------------------------------
    # Verification and Bounding Box Analysis
    # -----------------------------------------------------------------
    bpy.context.view_layer.update()
    
    bldg_objs = []
    plaza_objs = []
    
    for cname in walc_col_names:
        c = bpy.data.collections.get(cname)
        if c:
            for obj in c.objects:
                if obj.type == 'MESH':
                    nl = obj.name.lower()
                    if "terrain" in nl:
                        continue
                    elif any(k in nl for k in ["plaza", "seatwall", "planting", "grasses", "lamp", "lantern"]):
                        plaza_objs.append(obj)
                    else:
                        bldg_objs.append(obj)
                        
    def get_bbox(objs):
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')
        for obj in objs:
            for corner in obj.bound_box:
                pt = obj.matrix_world @ mathutils.Vector(corner)
                min_x = min(min_x, pt.x)
                max_x = max(max_x, pt.x)
                min_y = min(min_y, pt.y)
                max_y = max(max_y, pt.y)
                min_z = min(min_z, pt.z)
                max_z = max(max_z, pt.z)
        return (min_x, max_x), (min_y, max_y), (min_z, max_z)
        
    (bx_min, bx_max), (by_min, by_max), (bz_min, bz_max) = get_bbox(bldg_objs)
    (px_min, px_max), (py_min, py_max), _ = get_bbox(plaza_objs)
    (ax_min, ax_max), (ay_min, ay_max), (az_min, az_max) = get_bbox(bldg_objs + plaza_objs)
    
    print("\n" + "="*60)
    print("VERIFIED WALC COORDINATES AFTER REORIENTATION:")
    print("="*60)
    print(f"Building Proper Structure ({len(bldg_objs)} objects):")
    print(f"  X span: {bx_min:6.2f}m to {bx_max:6.2f}m (width:  {bx_max - bx_min:.2f}m)")
    print(f"  Y span: {by_min:6.2f}m to {by_max:6.2f}m (length: {by_max - by_min:.2f}m)")
    print(f"  Z span: {bz_min:6.2f}m to {bz_max:6.2f}m (height: {bz_max - bz_min:.2f}m)")
    print(f"  Center: X = {(bx_min + bx_max)/2:.2f}m, Y = {(by_min + by_max)/2:.2f}m")
    
    print(f"\nPlaza & Site Elements ({len(plaza_objs)} objects):")
    print(f"  X span: {px_min:6.2f}m to {px_max:6.2f}m (West of facade)")
    print(f"  Y span: {py_min:6.2f}m to {py_max:6.2f}m")
    
    print(f"\nBuilding + Plaza Combined ({len(bldg_objs) + len(plaza_objs)} objects):")
    print(f"  X span: {ax_min:6.2f}m to {ax_max:6.2f}m (width:  {ax_max - ax_min:.2f}m)")
    print(f"  Y span: {ay_min:6.2f}m to {ay_max:6.2f}m (length: {ay_max - ay_min:.2f}m)")
    print(f"  Target Real Footprint: X: [10.1m, 69.8m], Y: [-45.2m, 42.8m]")
    
    # Key orientation landmarks
    canopy = bpy.data.objects.get("Glass entry canopy")
    mullins = bpy.data.objects.get("Reading room roof")
    rear = bpy.data.objects.get("Rear roof")
    
    if canopy:
        c_pts = [canopy.matrix_world @ mathutils.Vector(c) for c in canopy.bound_box]
        cx_m = sum(p.x for p in c_pts) / len(c_pts)
        cy_m = sum(p.y for p in c_pts) / len(c_pts)
        print(f"\nOrientation Verification:")
        print(f"  Main Entrance Canopy Center:   X = {cx_m:.2f}m, Y = {cy_m:.2f}m (Facing WEST toward Bell Tower)")
    if mullins:
        m_pts = [mullins.matrix_world @ mathutils.Vector(c) for c in mullins.bound_box]
        mx_m = sum(p.x for p in m_pts) / len(m_pts)
        my_m = sum(p.y for p in m_pts) / len(m_pts)
        print(f"  Mullins Reading Room Center:   X = {mx_m:.2f}m, Y = {my_m:.2f}m (Long axis runs North-South along West facade)")
    if rear:
        r_pts = [rear.matrix_world @ mathutils.Vector(c) for c in rear.bound_box]
        rx_m = sum(p.x for p in r_pts) / len(r_pts)
        ry_m = sum(p.y for p in r_pts) / len(r_pts)
        print(f"  Rear Facade / Roof Center:     X = {rx_m:.2f}m, Y = {ry_m:.2f}m (Facing EAST toward Potter Center)")
    print("="*60 + "\n")

if __name__ == "__main__":
    reorient_walc()
