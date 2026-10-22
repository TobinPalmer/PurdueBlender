import bpy
import bmesh
import mathutils
import math
import os

def assemble_all():
    print("=== STARTING PURDUE ENGINEERING PRECINCT ASSEMBLY ===")
    
    # -------------------------------------------------------------
    # 1. Align WALC to its Real-World Campus Coordinates
    # -------------------------------------------------------------
    print("1. Aligning WALC to surveyed campus coordinates...")
    walc_col_names = [
        '01 Exterior and plaza', '02 Interior architecture', '03 Mullins Reading Room',
        '04 Furniture and teaching rooms', '05 Review refinements', '06 Circulation and fidelity fixes',
        '07 Detail and classroom completion', '08 Final comparison refinements'
    ]
    
    # Parent collection for WALC
    master_walc_col = bpy.data.collections.get("Master_WALC_Detailed")
    if not master_walc_col:
        master_walc_col = bpy.data.collections.new("Master_WALC_Detailed")
        bpy.context.scene.collection.children.link(master_walc_col)
        
    # Check if WALC has already been translated
    walc_flag_name = "WALC_TRANSLATION_FLAG"
    if walc_flag_name not in bpy.data.objects:
        # Translation vector to place WALC on its surveyed campus coordinates
        dx_walc = 40.0
        dy_walc = 12.8
        dz_walc = 0.0
        walc_obj_count = 0
        
        for cname in walc_col_names:
            c = bpy.data.collections.get(cname)
            if c:
                if c.name in bpy.context.scene.collection.children:
                    bpy.context.scene.collection.children.unlink(c)
                if c.name not in master_walc_col.children:
                    master_walc_col.children.link(c)
                    
                for obj in c.objects:
                    obj.location.x += dx_walc
                    obj.location.y += dy_walc
                    obj.location.z += dz_walc
                    walc_obj_count += 1
                    
        # Add flag
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(dx_walc, dy_walc, dz_walc))
        flag = bpy.context.active_object
        flag.name = walc_flag_name
        master_walc_col.objects.link(flag)
        bpy.context.scene.collection.objects.unlink(flag)
        print(f"WALC translated ({dx_walc}, {dy_walc}): {walc_obj_count} objects aligned.")
    else:
        print("WALC already aligned to campus coordinates.")
        
    # Hide low-poly WALC placeholder in 02_Campus_Buildings_Massing
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if massing_col:
        for obj in massing_col.objects:
            if "WALC" in obj.name or "Wilmeth" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                print(f"Low-poly placeholder '{obj.name}' hidden in favor of detailed WALC.")

    # -------------------------------------------------------------
    # 2. Append Wiley Hall from Codex & Translate to Campus Site
    # -------------------------------------------------------------
    print("2. Appending Wiley Hall from Codex archive...")
    wiley_blend = r"C:\Users\Tobin\Documents\Codex\2026-10-21\inste\outputs\Wiley_Street_View_Reconstruction.blend"
    wiley_cols_to_load = [
        '01_Wiley_Masonry', '02_Windows_and_Frames', '03_Stair_Entrances', 
        '04_Roofs', '05_Site', '06_Landscape', '08_Dining_Hall_Side_Entrances',
        '11_Interior_Basement', '12_Interior_First_Floor', '13_Interior_Second_Floor',
        '14_Interior_Third_Floor', '15_Common_Block_Interiors', '16_Stairs_Lifts_Connectors'
    ]
    
    master_wiley_col = bpy.data.collections.get("06_Wiley_Hall_Detailed")
    if not master_wiley_col:
        master_wiley_col = bpy.data.collections.new("06_Wiley_Hall_Detailed")
        bpy.context.scene.collection.children.link(master_wiley_col)
        
    wiley_flag_name = "WILEY_IMPORT_FLAG"
    if wiley_flag_name not in bpy.data.objects and os.path.exists(wiley_blend):
        target_x, target_y = -599.2, 125.6
        wiley_obj_count = 0
        
        for cname in wiley_cols_to_load:
            if cname not in bpy.data.collections:
                try:
                    bpy.ops.wm.append(
                        filepath=os.path.join(wiley_blend, "Collection", cname),
                        directory=os.path.join(wiley_blend, "Collection"),
                        filename=cname
                    )
                except Exception as e:
                    print(f"Notice appending {cname}: {e}")
                    
            col = bpy.data.collections.get(cname)
            if col:
                if col.name in bpy.context.scene.collection.children:
                    bpy.context.scene.collection.children.unlink(col)
                if col.name not in master_wiley_col.children:
                    master_wiley_col.children.link(col)
                    
                for obj in col.objects:
                    obj.location.x += target_x
                    obj.location.y += target_y
                    wiley_obj_count += 1
                    
        # Add flag
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(target_x, target_y, 0))
        flag = bpy.context.active_object
        flag.name = wiley_flag_name
        master_wiley_col.objects.link(flag)
        bpy.context.scene.collection.objects.unlink(flag)
        print(f"Wiley Hall appended and placed at ({target_x}, {target_y}): {wiley_obj_count} objects.")
    else:
        print("Wiley Hall already present in scene.")
        
    # Hide low-poly Wiley placeholder in massing collection
    if massing_col:
        for obj in massing_col.objects:
            if "Wiley" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                print(f"Low-poly placeholder '{obj.name}' hidden in favor of detailed Wiley Hall.")

    # -------------------------------------------------------------
    # 3. Model Neil Armstrong Hall of Engineering (ARMS)
    # -------------------------------------------------------------
    print("3. Modeling Neil Armstrong Hall of Engineering (ARMS)...")
    build_neil_armstrong_hall(massing_col)

    # -------------------------------------------------------------
    # 4. Model The Engineering Fountain & Surrounding Mall Buildings
    # -------------------------------------------------------------
    print("4. Modeling The Engineering Fountain & Surrounding Mall...")
    build_engineering_fountain_and_mall(massing_col)
    
    # -------------------------------------------------------------
    # 5. Add Dedicated Inspection Cameras
    # -------------------------------------------------------------
    setup_precinct_cameras()
    
    print("=== PURDUE ENGINEERING PRECINCT ASSEMBLY COMPLETE ===")

# -----------------------------------------------------------------
# Neil Armstrong Hall of Engineering (ARMS)
# -----------------------------------------------------------------
def build_neil_armstrong_hall(massing_col):
    col_name = "07_Neil_Armstrong_Hall_Detailed"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
        
    # Hide low-poly Armstrong in massing collection
    if massing_col:
        for obj in massing_col.objects:
            if "Armstrong" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                
    # Materials
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick")
    mat_stone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_glass = bpy.data.materials.get("Campus_Reflective_Glass")
    mat_slate = bpy.data.materials.get("Roof_Dark_Slate")
    mat_gold = bpy.data.materials.get("Bell_Tower_Clock_Gold")
    mat_concrete = bpy.data.materials.get("Campus_Walkway_Concrete")
    
    # Material for curved aerodynamic green-blue solar glass
    mat_arms_glass = bpy.data.materials.get("ARMS_Solar_Curtain_Glass")
    if not mat_arms_glass:
        mat_arms_glass = bpy.data.materials.new(name="ARMS_Solar_Curtain_Glass")
        mat_arms_glass.use_nodes = True
        bsdf = next((n for n in mat_arms_glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.12, 0.28, 0.32, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.05
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.25
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = 0.85
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = 0.85
            if "IOR" in bsdf.inputs:
                bsdf.inputs["IOR"].default_value = 1.54
                
    # Architectural Site Origin for Armstrong:
    # Corner of Stadium Ave & Northwestern Ave. Center around X: -108.8, Y: 390.6
    cx, cy = -108.8, 390.6
    
    # 1. Main East Academic Wing (4 stories, 18m high, brick & limestone)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(cx + 35.0, cy - 8.0, 9.5),
        scale=(55.0, 24.0, 19.0)
    )
    east_wing = bpy.context.active_object
    east_wing.name = "ARMS_East_Academic_Wing"
    east_wing.data.materials.append(mat_brick)
    col.objects.link(east_wing)
    bpy.context.scene.collection.objects.unlink(east_wing)
    
    # East Wing limestone belt courses & parapet cap
    for zh in [5.0, 10.0, 15.0, 19.1]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(cx + 35.0, cy - 8.0, zh),
            scale=(55.6, 24.6, 0.45)
        )
        band = bpy.context.active_object
        band.name = f"ARMS_East_Limestone_Band_{int(zh)}"
        band.data.materials.append(mat_stone)
        col.objects.link(band)
        bpy.context.scene.collection.objects.unlink(band)
        
    # East Wing Ribbon Windows
    for zh in [3.0, 7.8, 12.8, 17.2]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(cx + 35.0, cy - 20.1, zh),
            scale=(52.0, 0.3, 1.8)
        )
        win = bpy.context.active_object
        win.name = f"ARMS_East_Ribbon_Win_{int(zh)}"
        win.data.materials.append(mat_glass)
        col.objects.link(win)
        bpy.context.scene.collection.objects.unlink(win)
        
    # 2. Main West Research Wing (4 stories, 18m high, brick & limestone)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(cx - 38.0, cy - 6.0, 9.5),
        scale=(52.0, 28.0, 19.0)
    )
    west_wing = bpy.context.active_object
    west_wing.name = "ARMS_West_Research_Wing"
    west_wing.data.materials.append(mat_brick)
    col.objects.link(west_wing)
    bpy.context.scene.collection.objects.unlink(west_wing)
    
    # West Wing limestone horizontal stringcourses
    for zh in [5.0, 10.0, 15.0, 19.1]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(cx - 38.0, cy - 6.0, zh),
            scale=(52.6, 28.6, 0.45)
        )
        band = bpy.context.active_object
        band.name = f"ARMS_West_Limestone_Band_{int(zh)}"
        band.data.materials.append(mat_stone)
        col.objects.link(band)
        bpy.context.scene.collection.objects.unlink(band)
        
    # 3. Sweeping Curved Glass Atrium Facade (Iconic Feature Facing Stadium & Northwestern)
    # Generate curved segmented curtain wall
    curve_bm = bmesh.new()
    curve_radius = 42.0
    curve_center = (cx - 2.0, cy - 28.0)
    start_angle = math.radians(45.0)
    end_angle = math.radians(135.0)
    steps = 20
    d_angle = (end_angle - start_angle) / steps
    atrium_h = 21.0 # Soaring 4.5-story atrium height
    
    bot_v = []
    top_v = []
    for s in range(steps + 1):
        ang = start_angle + s * d_angle
        vx = curve_center[0] + curve_radius * math.cos(ang)
        vy = curve_center[1] + curve_radius * math.sin(ang)
        vb = curve_bm.verts.new((vx, vy, 0.0))
        vt = curve_bm.verts.new((vx, vy, atrium_h))
        bot_v.append(vb)
        top_v.append(vt)
        
    curve_bm.verts.ensure_lookup_table()
    for s in range(steps):
        f = curve_bm.faces.new((bot_v[s], bot_v[s+1], top_v[s+1], top_v[s]))
        f.material_index = 0
        
    curve_mesh = bpy.data.meshes.new("ARMS_Curved_Curtain_Wall")
    curve_bm.to_mesh(curve_mesh)
    curve_bm.free()
    curve_obj = bpy.data.objects.new("ARMS_Curved_Curtain_Wall", curve_mesh)
    curve_mesh.materials.append(mat_arms_glass)
    col.objects.link(curve_obj)
    
    # 4. Vertical Structural Mullions and Canopy on Curved Facade
    for s in range(0, steps + 1, 2):
        ang = start_angle + s * d_angle
        mx = curve_center[0] + curve_radius * math.cos(ang)
        my = curve_center[1] + curve_radius * math.sin(ang)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(mx, my, atrium_h * 0.5),
            scale=(0.4, 0.4, atrium_h)
        )
        mul = bpy.context.active_object
        mul.name = f"ARMS_Mullion_{s}"
        mul.data.materials.append(mat_slate)
        col.objects.link(mul)
        bpy.context.scene.collection.objects.unlink(mul)
        
    # Dramatic Cantilevered Entrance Canopy
    canopy_x = cx - 2.0
    canopy_y = cy + 15.5
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(canopy_x, canopy_y, 5.5),
        scale=(22.0, 10.0, 0.6)
    )
    canopy = bpy.context.active_object
    canopy.name = "ARMS_Cantilever_Entrance_Canopy"
    canopy.rotation_euler[0] = math.radians(-3.0) # slight uplift
    canopy.data.materials.append(mat_slate)
    col.objects.link(canopy)
    bpy.context.scene.collection.objects.unlink(canopy)
    
    # 5. Kurz Atrium Interior Architecture (Skylight Roof Trusses & Suspended Space Model)
    # Atrium Roof Skylight
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(cx - 2.0, cy - 6.0, atrium_h + 0.3),
        scale=(36.0, 26.0, 0.8)
    )
    skylight = bpy.context.active_object
    skylight.name = "ARMS_Atrium_Skylight_Roof"
    skylight.data.materials.append(mat_arms_glass)
    col.objects.link(skylight)
    bpy.context.scene.collection.objects.unlink(skylight)
    
    # Suspended Spacecraft / Aircraft Artifact inside Atrium
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.8,
        depth=6.5,
        location=(cx - 2.0, cy - 6.0, 12.0),
        vertices=24
    )
    capsule = bpy.context.active_object
    capsule.name = "ARMS_KurzAtrium_Space_Artifact"
    capsule.rotation_euler = (math.radians(20.0), math.radians(15.0), math.radians(45.0))
    capsule.data.materials.append(mat_gold)
    col.objects.link(capsule)
    bpy.context.scene.collection.objects.unlink(capsule)
    
    # 6. Neil Armstrong Moon Walk Plaza & Student Memorial Statue
    plaza_x = cx - 2.0
    plaza_y = cy + 24.0
    # Circular Stone Paver Plaza
    bpy.ops.mesh.primitive_cylinder_add(
        radius=14.0,
        depth=0.15,
        location=(plaza_x, plaza_y, 0.08),
        vertices=32
    )
    plaza = bpy.context.active_object
    plaza.name = "ARMS_Neil_Armstrong_Moon_Plaza"
    plaza.data.materials.append(mat_concrete)
    col.objects.link(plaza)
    bpy.context.scene.collection.objects.unlink(plaza)
    
    # Stone Bench with Neil Armstrong bronze statue
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(plaza_x + 4.0, plaza_y - 2.0, 0.5),
        scale=(2.4, 0.8, 0.6)
    )
    bench = bpy.context.active_object
    bench.name = "ARMS_Statue_Stone_Bench"
    bench.data.materials.append(mat_stone)
    col.objects.link(bench)
    bpy.context.scene.collection.objects.unlink(bench)
    
    # Bronze Statue of Neil Armstrong (seated student pose)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.4,
        depth=1.3,
        location=(plaza_x + 4.0, plaza_y - 2.0, 1.2),
        vertices=16
    )
    statue = bpy.context.active_object
    statue.name = "Neil_Armstrong_Bronze_Statue"
    statue.data.materials.append(mat_gold)
    col.objects.link(statue)
    bpy.context.scene.collection.objects.unlink(statue)
    
    # Inlaid Bronze Lunar Bootprints trail across plaza
    for i, step_d in enumerate([-5.0, -3.0, -1.0, 1.0, 3.0]):
        foot_x = plaza_x + (step_d * 0.8)
        foot_y = plaza_y + step_d
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(foot_x, foot_y, 0.16),
            scale=(0.35, 0.18, 0.02)
        )
        boot = bpy.context.active_object
        boot.name = f"Apollo11_Lunar_Footprint_{i}"
        boot.rotation_euler[2] = math.radians(35.0 if i % 2 == 0 else 40.0)
        boot.data.materials.append(mat_gold)
        col.objects.link(boot)
        bpy.context.scene.collection.objects.unlink(boot)
        
    print("Neil Armstrong Hall of Engineering (ARMS) detailed model generated.")

# -----------------------------------------------------------------
# Engineering Fountain & Surrounding Mall Quadrangle
# -----------------------------------------------------------------
def build_engineering_fountain_and_mall(massing_col):
    col_name = "08_Engineering_Fountain_and_Mall"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
        
    mat_stone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_water = bpy.data.materials.get("Wabash_River_Water")
    mat_concrete = bpy.data.materials.get("Campus_Walkway_Concrete")
    mat_glass = bpy.data.materials.get("Campus_Reflective_Glass")
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick")
    mat_slate = bpy.data.materials.get("Roof_Dark_Slate")
    mat_gold = bpy.data.materials.get("Bell_Tower_Clock_Gold")
    mat_grass = bpy.data.materials.get("Purdue_Landscape_Green")
    
    # Fountain Center: Heart of the Engineering Mall (X = 0.0, Y = 195.0)
    fx, fy = 0.0, 195.0
    
    # 1. Outer Granite Sunken Basin (18m diameter)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=9.0,
        depth=0.9,
        location=(fx, fy, 0.25),
        vertices=48
    )
    basin = bpy.context.active_object
    basin.name = "Engineering_Fountain_Granite_Basin"
    basin.data.materials.append(mat_stone)
    col.objects.link(basin)
    bpy.context.scene.collection.objects.unlink(basin)
    
    # Water Surface inside Basin
    bpy.ops.mesh.primitive_cylinder_add(
        radius=8.4,
        depth=0.2,
        location=(fx, fy, 0.55),
        vertices=48
    )
    f_water = bpy.context.active_object
    f_water.name = "Engineering_Fountain_Water_Surface"
    f_water.data.materials.append(mat_water)
    col.objects.link(f_water)
    bpy.context.scene.collection.objects.unlink(f_water)
    
    # 2. Four Towering Concrete Quadrant Pylons (Class of 1939 Water Sculpture, 11.6m tall)
    pylon_h = 11.6
    pylon_radius = 2.2
    pylon_w = 1.1
    pylon_len = 3.6
    for angle in [45, 135, 225, 315]:
        px = fx + pylon_radius * math.cos(math.radians(angle))
        py = fy + pylon_radius * math.sin(math.radians(angle))
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(px, py, pylon_h * 0.5),
            scale=(pylon_w, pylon_len, pylon_h)
        )
        pylon = bpy.context.active_object
        pylon.name = f"Fountain_Sculpture_Pylon_{angle}"
        pylon.rotation_euler[2] = math.radians(angle)
        pylon.data.materials.append(mat_stone)
        col.objects.link(pylon)
        bpy.context.scene.collection.objects.unlink(pylon)
        
    # Central Cylindrical Water Core Column & Conical Nozzle
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.1,
        depth=pylon_h - 1.0,
        location=(fx, fy, (pylon_h - 1.0) * 0.5),
        vertices=32
    )
    core = bpy.context.active_object
    core.name = "Fountain_Water_Core_Column"
    core.data.materials.append(mat_stone)
    col.objects.link(core)
    bpy.context.scene.collection.objects.unlink(core)
    
    # Inverted Conical Water Delivery Head
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=0.6,
        radius2=2.2,
        depth=1.8,
        location=(fx, fy, pylon_h - 0.2)
    )
    nozzle = bpy.context.active_object
    nozzle.name = "Fountain_Water_Ejection_Nozzle"
    nozzle.data.materials.append(mat_gold)
    col.objects.link(nozzle)
    bpy.context.scene.collection.objects.unlink(nozzle)
    
    # Water Spray Plume Mesh
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=3.5,
        radius2=0.4,
        depth=7.0,
        location=(fx, fy, 4.5)
    )
    plume = bpy.context.active_object
    plume.name = "Fountain_Water_Spray_Cascade"
    plume.data.materials.append(mat_water)
    col.objects.link(plume)
    bpy.context.scene.collection.objects.unlink(plume)
    
    # 3. Surrounding Circular Plaza & Radial Benches
    bpy.ops.mesh.primitive_cylinder_add(
        radius=26.0,
        depth=0.12,
        location=(fx, fy, 0.06),
        vertices=48
    )
    f_plaza = bpy.context.active_object
    f_plaza.name = "Engineering_Mall_Fountain_Plaza"
    f_plaza.data.materials.append(mat_concrete)
    col.objects.link(f_plaza)
    bpy.context.scene.collection.objects.unlink(f_plaza)
    
    # 8 Perimeter Curved Bench Seatwalls
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        bx = fx + 21.0 * math.cos(math.radians(angle))
        by = fy + 21.0 * math.sin(math.radians(angle))
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(bx, by, 0.45),
            scale=(4.8, 0.8, 0.55)
        )
        f_bench = bpy.context.active_object
        f_bench.name = f"Fountain_Perimeter_Bench_{angle}"
        f_bench.rotation_euler[2] = math.radians(angle + 90)
        f_bench.data.materials.append(mat_stone)
        col.objects.link(f_bench)
        bpy.context.scene.collection.objects.unlink(f_bench)
        
    # 4. Engineering Mall Promenades & Symmetrical Green Quadrants
    # North-South Promenade (connecting Armstrong Hall down to WALC & Bell Tower)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(fx, fy + 70.0, 0.08),
        scale=(12.0, 180.0, 0.1)
    )
    prom_ns = bpy.context.active_object
    prom_ns.name = "Engineering_Mall_NorthSouth_Promenade"
    prom_ns.data.materials.append(mat_concrete)
    col.objects.link(prom_ns)
    bpy.context.scene.collection.objects.unlink(prom_ns)
    
    # East-West Promenade (connecting MSEE / EE across to ME / Physics)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(fx, fy, 0.08),
        scale=(160.0, 12.0, 0.1)
    )
    prom_ew = bpy.context.active_object
    prom_ew.name = "Engineering_Mall_EastWest_Promenade"
    prom_ew.data.materials.append(mat_concrete)
    col.objects.link(prom_ew)
    bpy.context.scene.collection.objects.unlink(prom_ew)
    
    # 5. MSEE-to-EE Glass Covered Skybridge
    # Modeled between MSEE (X=55, Y=190) and BHEE / EE (X=105, Y=160)
    sb_start = (55.0, 190.0)
    sb_end = (98.0, 160.0)
    sb_cx = (sb_start[0] + sb_end[0]) * 0.5
    sb_cy = (sb_start[1] + sb_end[1]) * 0.5
    sb_len = math.hypot(sb_end[0] - sb_start[0], sb_end[1] - sb_start[1])
    sb_ang = math.atan2(sb_end[1] - sb_start[1], sb_end[0] - sb_start[0])
    
    # Skybridge Body (enclosed 3rd floor connector, z = 11m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(sb_cx, sb_cy, 11.0),
        scale=(sb_len, 4.2, 3.8)
    )
    skybridge = bpy.context.active_object
    skybridge.name = "MSEE_to_EE_Skybridge_Enclosure"
    skybridge.rotation_euler[2] = sb_ang
    skybridge.data.materials.append(mat_glass)
    col.objects.link(skybridge)
    bpy.context.scene.collection.objects.unlink(skybridge)
    
    # Skybridge Roof & Floor Slabs
    for sz in [9.0, 13.0]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sb_cx, sb_cy, sz),
            scale=(sb_len + 0.4, 4.6, 0.4)
        )
        s_slab = bpy.context.active_object
        s_slab.name = f"Skybridge_Slab_{int(sz)}"
        s_slab.rotation_euler[2] = sb_ang
        s_slab.data.materials.append(mat_slate)
        col.objects.link(s_slab)
        bpy.context.scene.collection.objects.unlink(s_slab)
        
    print("The Engineering Fountain and Mall quadrangle generated.")

# -----------------------------------------------------------------
# Cameras
# -----------------------------------------------------------------
def setup_precinct_cameras():
    col = bpy.data.collections.get("05_Cameras_and_Views")
    if not col:
        col = bpy.data.collections.new("05_Cameras_and_Views")
        bpy.context.scene.collection.children.link(col)
        
    cameras = [
        {
            "name": "Cam_05_Neil_Armstrong_Facade",
            "loc": (-110.0, 445.0, 8.5),
            "rot": (math.radians(82.0), 0.0, math.radians(180.0)),
            "lens": 24.0
        },
        {
            "name": "Cam_06_Engineering_Fountain_Mall",
            "loc": (0.0, 145.0, 12.0),
            "rot": (math.radians(78.0), 0.0, 0.0),
            "lens": 28.0
        },
        {
            "name": "Cam_07_Wiley_Hall_StreetView",
            "loc": (-599.2, 70.0, 6.0),
            "rot": (math.radians(85.0), 0.0, 0.0),
            "lens": 28.0
        }
    ]
    
    for cfg in cameras:
        if cfg["name"] not in bpy.data.objects:
            cam_data = bpy.data.cameras.new(cfg["name"])
            cam_data.lens = cfg["lens"]
            cam_data.clip_end = 10000.0
            cam_obj = bpy.data.objects.new(cfg["name"], cam_data)
            cam_obj.location = cfg["loc"]
            cam_obj.rotation_euler = cfg["rot"]
            col.objects.link(cam_obj)
            
    print("Precinct evaluation cameras created.")

if __name__ == "__main__":
    assemble_all()
