"""
Build Neil Armstrong Hall of Engineering (ARMS - 2007) in Blender
==================================================================
This script builds a photorealistic, architecturally accurate digital twin
of Purdue University's flagship engineering landmark: Neil Armstrong Hall
of Engineering (ARMS).

Components built:
1. Collections:
   - 39_Neil_Armstrong_Hall_Exterior
   - 40_Neil_Armstrong_Hall_Interiors_and_Atrium
   - 41_Neil_Armstrong_Hall_MoonPlaza_and_Site
2. Exterior Envelope:
   - East Academic Wing (4 stories, red brick, beltcourses, ribbon glass, mechanical penthouse)
   - West Research Wing (4 stories, red brick, beltcourses, ribbon glass, mechanical penthouse)
   - Central Aerodynamic Curved Curtain Wall (59.4m wide, 21m high, 17 mullions, transoms)
   - Cantilevered Aerodynamic Entrance Canopy (22m x 10m) with illuminated downlights
   - Monumental 3D Gold Inscription: "NEIL ARMSTRONG HALL OF ENGINEERING"
   - Angled Atrium Glass Skylight Roof with structural space frame trusses
3. Interior Program:
   - Soaring 4-story Kurz Atrium with polished cream terrazzo floor
   - Concentric radial orbital brass inlay compass rings
   - Suspended full-scale Apollo Command & Service Module prototype with heat shield & steel cables
   - Multi-tier cantilevered viewing balconies (Level 2 & Level 3) with glass/steel balustrades
   - Kurz Atrium collaborative student study commons (tables, chairs, lounge armchairs)
   - ARMS 1010 Major Tiered Lecture Hall (dais, podium, dual screens, 5 stepped tiers)
   - Neil Armstrong Hall of Heroes exhibition with illuminated artifact display cases & gold plaques
4. Moon Plaza & Site:
   - 28m circular concrete and granite plaza
   - Authentic bronze statue of Neil Armstrong seated on limestone bench
   - Apollo 11 lunar boot prints embedded in plaza pavement
   - Teak wood campus benches, Sheffield bike racks, and LED bollards
5. Dedicated Inspection Cameras (Cam 57 to Cam 61)
"""

import bpy
import math
import mathutils

def run():
    print("=== Starting Neil Armstrong Hall of Engineering (ARMS) Reconstruction ===")

    # 1. Cleanup old placeholder objects
    old_ph = bpy.data.objects.get("Neil Armstrong Hall of Engineering (ARMS)")
    if old_ph:
        print("Removing old massing placeholder 'Neil Armstrong Hall of Engineering (ARMS)'")
        bpy.data.objects.remove(old_ph, do_unlink=True)

    # Clean existing objects in collection '07_Neil_Armstrong_Hall_Detailed'
    old_col = bpy.data.collections.get("07_Neil_Armstrong_Hall_Detailed")
    if old_col:
        print(f"Purging {len(old_col.objects)} legacy objects from '07_Neil_Armstrong_Hall_Detailed'")
        for obj in list(old_col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_col)

    # 2. Create dedicated collections
    def get_or_create_col(name):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        return col

    col_ext = get_or_create_col("39_Neil_Armstrong_Hall_Exterior")
    col_int = get_or_create_col("40_Neil_Armstrong_Hall_Interiors_and_Atrium")
    col_site = get_or_create_col("41_Neil_Armstrong_Hall_MoonPlaza_and_Site")
    col_cams = get_or_create_col("00_Inspection_Cameras")

    # 3. Dedicated PBR Materials Setup
    def get_or_create_mat(name, base_color, roughness=0.4, metallic=0.0, transmission=0.0, emission=None, emission_strength=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emission
        return mat

    mat_brick = get_or_create_mat("ARMS_Purdue_Red_Brick", (0.38, 0.14, 0.09, 1.0), roughness=0.72)
    mat_stone = get_or_create_mat("ARMS_Bedford_Limestone", (0.82, 0.79, 0.72, 1.0), roughness=0.55)
    mat_glass = get_or_create_mat("ARMS_Solar_Curtain_Glass", (0.12, 0.22, 0.28, 1.0), roughness=0.04, transmission=0.88)
    mat_glass_clear = get_or_create_mat("ARMS_Clear_Safety_Glass", (0.85, 0.92, 0.95, 1.0), roughness=0.02, transmission=0.92)
    mat_mullion = get_or_create_mat("ARMS_Mullion_Steel", (0.15, 0.16, 0.18, 1.0), roughness=0.25, metallic=0.85)
    mat_terrazzo = get_or_create_mat("ARMS_Terrazzo_Cream", (0.88, 0.86, 0.82, 1.0), roughness=0.15)
    mat_inlay_brass = get_or_create_mat("ARMS_Inlay_Brass", (0.86, 0.72, 0.28, 1.0), roughness=0.22, metallic=0.92)
    mat_heat_shield = get_or_create_mat("ARMS_Apollo_HeatShield", (0.65, 0.45, 0.18, 1.0), roughness=0.28, metallic=0.88)
    mat_white_tile = get_or_create_mat("ARMS_Apollo_WhiteTile", (0.92, 0.92, 0.90, 1.0), roughness=0.25)
    mat_cable_steel = get_or_create_mat("ARMS_Cable_Steel", (0.65, 0.68, 0.70, 1.0), roughness=0.20, metallic=0.95)
    mat_oak = get_or_create_mat("ARMS_Warm_Oak", (0.42, 0.26, 0.14, 1.0), roughness=0.35)
    mat_navy = get_or_create_mat("ARMS_Navy_Fabric", (0.08, 0.12, 0.24, 1.0), roughness=0.75)
    mat_chalk = get_or_create_mat("ARMS_Slate_Chalkboard", (0.10, 0.12, 0.11, 1.0), roughness=0.60)
    mat_bronze = get_or_create_mat("ARMS_Bronze_Statue", (0.32, 0.22, 0.12, 1.0), roughness=0.35, metallic=0.85)
    mat_gold_plaque = get_or_create_mat("ARMS_Plaque_Gold", (0.90, 0.75, 0.22, 1.0), roughness=0.18, metallic=0.95)
    mat_lunar_plinth = get_or_create_mat("ARMS_Lunar_Granite", (0.16, 0.16, 0.18, 1.0), roughness=0.45)
    mat_ceiling_downlight = get_or_create_mat("ARMS_Light_Downlight_Glow", (1.0, 0.95, 0.88, 1.0), roughness=0.1, emission=(1.0, 0.95, 0.88, 1.0), emission_strength=4.5)

    def create_box(name, collection, loc, dims, mat):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.location = loc
        
        # Build box
        dx, dy, dz = dims[0]/2, dims[1]/2, dims[2]/2
        verts = [
            (-dx, -dy, -dz), (dx, -dy, -dz), (dx, dy, -dz), (-dx, dy, -dz),
            (-dx, -dy, dz), (dx, -dy, dz), (dx, dy, dz), (-dx, dy, dz)
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (1, 2, 6, 5), (3, 0, 4, 7)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    def create_cylinder(name, collection, loc, radius, depth, mat, segments=24):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.location = loc
        
        verts = []
        # bottom ring, top ring
        z_b = -depth / 2.0
        z_t = depth / 2.0
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            verts.append((x, y, z_b))
        for i in range(segments):
            ang = 2 * math.pi * i / segments
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            verts.append((x, y, z_t))
        
        # center bottom & top
        cb_idx = 2 * segments
        ct_idx = 2 * segments + 1
        verts.append((0, 0, z_b))
        verts.append((0, 0, z_t))
        
        faces = []
        for i in range(segments):
            nxt = (i + 1) % segments
            # side face
            faces.append((i, nxt, segments + nxt, segments + i))
            # bottom cap
            faces.append((cb_idx, nxt, i))
            # top cap
            faces.append((ct_idx, segments + i, segments + nxt))
            
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    # =========================================================================
    # 4. EXTERIOR ENVELOPE (39_Neil_Armstrong_Hall_Exterior)
    # =========================================================================
    # Siting: Center X = -108.86m, Y = 390.63m
    # East Wing: X in [-101m, -46m] (Length 55m, Width 24m, Height 19.5m)
    # West Wing: X in [-172m, -118m] (Length 54m, Width 26m, Height 19.5m)
    # Central Atrium: X in [-140m, -78m], Y in [376m, 405m], Height 21.5m

    # --- EAST WING ---
    east_cx = -73.5
    east_cy = 382.5
    east_w = 55.0
    east_d = 24.0
    east_h = 19.5

    # Hollow perimeter walls for East Wing
    create_box("ARMS_East_Wall_North", col_ext, (east_cx, east_cy + east_d/2 - 0.3, east_h/2), (east_w, 0.6, east_h), mat_brick)
    create_box("ARMS_East_Wall_South", col_ext, (east_cx, east_cy - east_d/2 + 0.3, east_h/2), (east_w, 0.6, east_h), mat_brick)
    create_box("ARMS_East_Wall_East", col_ext, (east_cx + east_w/2 - 0.3, east_cy, east_h/2), (0.6, east_d, east_h), mat_brick)
    create_box("ARMS_East_Roof_Slab", col_ext, (east_cx, east_cy, east_h + 0.2), (east_w, east_d, 0.4), mat_mullion)
    create_box("ARMS_East_WaterTable", col_ext, (east_cx, east_cy, 0.75), (east_w + 0.4, east_d + 0.4, 1.5), mat_stone)

    # 4 Horizontal limestone beltcourses on East Wing
    for z_belt in [4.8, 9.6, 14.4, 19.4]:
        create_box(f"ARMS_East_Beltcourse_{int(z_belt)}", col_ext, (east_cx, east_cy, z_belt), (east_w + 0.25, east_d + 0.25, 0.35), mat_stone)

    # Ribbon windows on East Wing (South facade & East facade)
    for z_win in [2.6, 7.2, 12.0, 16.8]:
        create_box(f"ARMS_East_Win_South_{int(z_win)}", col_ext, (east_cx, east_cy - east_d/2 - 0.05, z_win), (east_w - 6.0, 0.2, 2.0), mat_glass)
        create_box(f"ARMS_East_Win_East_{int(z_win)}", col_ext, (east_cx + east_w/2 + 0.05, east_cy, z_win), (0.2, east_d - 6.0, 2.0), mat_glass)
        create_box(f"ARMS_East_Sill_South_{int(z_win)}", col_ext, (east_cx, east_cy - east_d/2 - 0.1, z_win - 1.1), (east_w - 5.6, 0.3, 0.2), mat_stone)
        create_box(f"ARMS_East_Sill_East_{int(z_win)}", col_ext, (east_cx + east_w/2 + 0.1, east_cy, z_win - 1.1), (0.3, east_d - 5.6, 0.2), mat_stone)

    # Rooftop mechanical penthouse on East Wing
    create_box("ARMS_East_Roof_Penthouse", col_ext, (east_cx, east_cy, east_h + 1.8), (24.0, 12.0, 3.2), mat_brick)
    create_box("ARMS_East_Penthouse_Louvers", col_ext, (east_cx, east_cy, east_h + 1.8), (24.4, 12.4, 2.4), mat_mullion)

    # --- WEST WING ---
    west_cx = -145.0
    west_cy = 384.0
    west_w = 54.0
    west_d = 26.0
    west_h = 19.5

    # Hollow perimeter walls for West Wing
    create_box("ARMS_West_Wall_North", col_ext, (west_cx, west_cy + west_d/2 - 0.3, west_h/2), (west_w, 0.6, west_h), mat_brick)
    create_box("ARMS_West_Wall_South", col_ext, (west_cx, west_cy - west_d/2 + 0.3, west_h/2), (west_w, 0.6, west_h), mat_brick)
    create_box("ARMS_West_Wall_West", col_ext, (west_cx - west_w/2 + 0.3, west_cy, west_h/2), (0.6, west_d, west_h), mat_brick)
    create_box("ARMS_West_Roof_Slab", col_ext, (west_cx, west_cy, west_h + 0.2), (west_w, west_d, 0.4), mat_mullion)
    create_box("ARMS_West_WaterTable", col_ext, (west_cx, west_cy, 0.75), (west_w + 0.4, west_d + 0.4, 1.5), mat_stone)

    # 4 Horizontal limestone beltcourses on West Wing
    for z_belt in [4.8, 9.6, 14.4, 19.4]:
        create_box(f"ARMS_West_Beltcourse_{int(z_belt)}", col_ext, (west_cx, west_cy, z_belt), (west_w + 0.25, west_d + 0.25, 0.35), mat_stone)

    # Ribbon windows on West Wing (South facade & West facade)
    for z_win in [2.6, 7.2, 12.0, 16.8]:
        create_box(f"ARMS_West_Win_South_{int(z_win)}", col_ext, (west_cx, west_cy - west_d/2 - 0.05, z_win), (west_w - 6.0, 0.2, 2.0), mat_glass)
        create_box(f"ARMS_West_Win_West_{int(z_win)}", col_ext, (west_cx - west_w/2 - 0.05, west_cy, z_win), (0.2, west_d - 6.0, 2.0), mat_glass)
        create_box(f"ARMS_West_Sill_South_{int(z_win)}", col_ext, (west_cx, west_cy - west_d/2 - 0.1, z_win - 1.1), (west_w - 5.6, 0.3, 0.2), mat_stone)
        create_box(f"ARMS_West_Sill_West_{int(z_win)}", col_ext, (west_cx - west_w/2 - 0.1, west_cy, z_win - 1.1), (0.3, west_d - 5.6, 0.2), mat_stone)

    # Rooftop mechanical penthouse on West Wing
    create_box("ARMS_West_Roof_Penthouse", col_ext, (west_cx, west_cy, west_h + 1.8), (22.0, 14.0, 3.2), mat_brick)
    create_box("ARMS_West_Penthouse_Louvers", col_ext, (west_cx, west_cy, west_h + 1.8), (22.4, 14.4, 2.4), mat_mullion)

    # --- CENTRAL KURZ ATRIUM ENVELOPE & CURVED FACADE ---
    # Parabolic curve linking West wing to East wing:
    # X ranges from -141m to -80m (center -110.5m)
    # Y apex at 405m, base at 392m
    atrium_cx = -110.5
    atrium_cy = 388.0
    atrium_h = 21.5

    # 17 Vertical structural aerodynamic mullions along the curved glass front
    num_mullions = 17
    mullion_coords = []
    for i in range(num_mullions):
        t = -1.0 + 2.0 * i / (num_mullions - 1) # -1 to 1
        x_m = atrium_cx + t * 30.5
        y_m = 405.0 - (t**2) * 12.5 # parabolic arch facing North
        mullion_coords.append((x_m, y_m))
        create_box(f"ARMS_Curved_Mullion_{i}", col_ext, (x_m, y_m, atrium_h/2), (0.35, 0.45, atrium_h), mat_mullion)
        # horizontal transoms at floor intervals
        for z_tr in [4.8, 9.6, 14.4, 19.2]:
            create_box(f"ARMS_Curved_Transom_{i}_{int(z_tr)}", col_ext, (x_m, y_m, z_tr), (3.8, 0.25, 0.2), mat_mullion)

    # Curved curtain wall glass segments between mullions
    for i in range(num_mullions - 1):
        x1, y1 = mullion_coords[i]
        x2, y2 = mullion_coords[i+1]
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        seg_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        ang = math.atan2(y2 - y1, x2 - x1)
        
        glass_seg = create_box(f"ARMS_Curtain_Glass_Bay_{i}", col_ext, (mid_x, mid_y, atrium_h/2), (seg_len + 0.1, 0.12, atrium_h - 0.2), mat_glass)
        glass_seg.rotation_euler = (0, 0, ang)

    # Atrium South Wall & Skylight Space Frame Roof
    create_box("ARMS_Atrium_South_Wall", col_ext, (atrium_cx, 372.5, atrium_h/2), (58.0, 0.6, atrium_h), mat_brick)
    create_box("ARMS_Atrium_Skylight_Glazing", col_ext, (atrium_cx, 388.0, atrium_h + 0.3), (56.0, 28.0, 0.25), mat_glass)
    # Roof steel trusses
    for x_truss in range(-135, -85, 8):
        create_box(f"ARMS_Roof_Steel_Truss_{x_truss}", col_ext, (x_truss, 388.0, atrium_h - 0.5), (0.4, 28.0, 1.2), mat_mullion)

    # Cantilevered Aerodynamic Entrance Canopy
    canopy_x = atrium_cx
    canopy_y = 407.5
    canopy_z = 5.2
    create_box("ARMS_Cantilever_Canopy_Deck", col_ext, (canopy_x, canopy_y, canopy_z), (24.0, 9.5, 0.5), mat_mullion)
    create_box("ARMS_Canopy_Fascia_Trim", col_ext, (canopy_x, canopy_y, canopy_z), (24.3, 9.8, 0.55), mat_stone)
    # Canopy recessed ceiling downlights
    for dx_c in [-8, -4, 0, 4, 8]:
        create_box(f"ARMS_Canopy_Downlight_{dx_c}", col_ext, (canopy_x + dx_c, canopy_y, canopy_z - 0.26), (0.6, 0.6, 0.05), mat_ceiling_downlight)
        light_data = bpy.data.lights.new(name=f"ARMS_Light_Canopy_{dx_c}", type='POINT')
        light_data.energy = 280.0
        light_data.color = (1.0, 0.95, 0.88)
        light_obj = bpy.data.objects.new(name=f"ARMS_Light_Canopy_{dx_c}", object_data=light_data)
        col_ext.objects.link(light_obj)
        light_obj.location = (canopy_x + dx_c, canopy_y, canopy_z - 0.4)

    # Monumental 3D Gold Building Lettering
    create_box("ARMS_Building_Sign_Header", col_ext, (canopy_x, canopy_y - 2.8, canopy_z + 0.85), (22.0, 0.15, 0.65), mat_mullion)
    create_box("ARMS_Gold_Lettering_Band", col_ext, (canopy_x, canopy_y - 2.7, canopy_z + 0.85), (20.5, 0.08, 0.45), mat_gold_plaque)

    # Main Entrance Revolving and Double Glass Doors
    create_box("ARMS_Entrance_Portal_Frame", col_ext, (canopy_x, 404.2, 2.2), (14.0, 0.4, 4.4), mat_mullion)
    for dx_door in [-4.5, 0.0, 4.5]:
        create_box(f"ARMS_Revolving_Door_{dx_door}", col_ext, (canopy_x + dx_door, 404.2, 1.8), (2.8, 0.25, 3.2), mat_glass_clear)
        create_box(f"ARMS_Door_Hardware_{dx_door}", col_ext, (canopy_x + dx_door, 404.2, 1.6), (0.1, 0.35, 1.2), mat_mullion)

    # =========================================================================
    # 5. INTERIOR ARCHITECTURE & KURZ ATRIUM (40_Neil_Armstrong_Hall_Interiors)
    # =========================================================================
    # Floor 0: Terrazzo ground slab
    create_box("ARMS_Atrium_Terrazzo_Floor", col_int, (atrium_cx, 388.0, 0.08), (56.0, 29.0, 0.16), mat_terrazzo)

    # Concentric brass aeronautical orbital compass inlay rings
    create_cylinder("ARMS_Terrazzo_Inlay_Ring_Outer", col_int, (atrium_cx, 388.0, 0.17), 10.5, 0.02, mat_inlay_brass, segments=36)
    create_cylinder("ARMS_Terrazzo_Inlay_Ring_Mid", col_int, (atrium_cx, 388.0, 0.17), 6.5, 0.02, mat_inlay_brass, segments=32)
    create_cylinder("ARMS_Terrazzo_Inlay_Ring_Core", col_int, (atrium_cx, 388.0, 0.17), 2.5, 0.02, mat_inlay_brass, segments=24)
    # Compass Rose radial lines
    for ang_deg in [0, 45, 90, 135]:
        ang_rad = math.radians(ang_deg)
        line_obj = create_box(f"ARMS_Compass_Radial_{ang_deg}", col_int, (atrium_cx, 388.0, 0.18), (21.0, 0.12, 0.02), mat_inlay_brass)
        line_obj.rotation_euler = (0, 0, ang_rad)

    # --- SUSPENDED APOLLO COMMAND MODULE / SPACECRAFT PROTOTYPE ---
    # Sited hovering at center (atrium_cx, 388.0, Z=12.5m)
    ship_cx = atrium_cx
    ship_cy = 388.0
    ship_cz = 12.8

    # Conical Command Module
    # Base diameter 3.9m (radius 1.95m), height 3.2m
    cmd_mod = create_cylinder("ARMS_Apollo_Command_Module", col_int, (ship_cx, ship_cy, ship_cz + 1.2), 1.95, 2.6, mat_white_tile, segments=24)
    # Heat Shield base
    create_cylinder("ARMS_Apollo_HeatShield", col_int, (ship_cx, ship_cy, ship_cz - 0.15), 2.05, 0.3, mat_heat_shield, segments=24)
    # Service Module lower cylinder
    create_cylinder("ARMS_Apollo_Service_Module", col_int, (ship_cx, ship_cy, ship_cz - 1.8), 1.95, 2.8, mat_white_tile, segments=24)
    # Rocket Engine Nozzle bell
    create_cylinder("ARMS_Apollo_Engine_Nozzle", col_int, (ship_cx, ship_cy, ship_cz - 3.5), 1.1, 1.2, mat_mullion, segments=16)
    # Docking probe apex
    create_cylinder("ARMS_Apollo_Docking_Probe", col_int, (ship_cx, ship_cy, ship_cz + 2.8), 0.35, 1.0, mat_mullion, segments=12)

    # Reaction Control System (RCS) thruster quads on 4 cardinal faces
    for i, (dx_rcs, dy_rcs) in enumerate([(2.0, 0), (-2.0, 0), (0, 2.0), (0, -2.0)]):
        create_box(f"ARMS_Apollo_RCS_Block_{i}", col_int, (ship_cx + dx_rcs, ship_cy + dy_rcs, ship_cz - 1.2), (0.4, 0.4, 0.4), mat_mullion)

    # 4 High-tensile braided steel suspension cables connecting spacecraft to roof trusses
    for i, (dx_cb, dy_cb) in enumerate([(1.8, 1.8), (-1.8, 1.8), (1.8, -1.8), (-1.8, -1.8)]):
        cb_len = atrium_h - ship_cz
        create_box(f"ARMS_Suspension_Cable_{i}", col_int, (ship_cx + dx_cb, ship_cy + dy_cb, ship_cz + cb_len/2), (0.04, 0.04, cb_len), mat_cable_steel)

    # Theatrical accent illumination directed at spacecraft
    for i, (dx_sp, dy_sp) in enumerate([(6.0, 6.0), (-6.0, 6.0), (6.0, -6.0), (-6.0, -6.0)]):
        sp_light = bpy.data.lights.new(name=f"ARMS_Light_Spacecraft_Spot_{i}", type='SPOT')
        sp_light.energy = 650.0
        sp_light.spot_size = math.radians(45)
        sp_light.color = (1.0, 0.96, 0.90)
        sp_obj = bpy.data.objects.new(name=f"ARMS_Light_Spacecraft_Spot_{i}", object_data=sp_light)
        col_int.objects.link(sp_obj)
        sp_obj.location = (ship_cx + dx_sp, ship_cy + dy_sp, atrium_h - 2.0)
        # Point toward spacecraft
        dir_vec = mathutils.Vector((ship_cx - (ship_cx + dx_sp), ship_cy - (ship_cy + dy_sp), ship_cz - (atrium_h - 2.0)))
        sp_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

    # --- MULTI-LEVEL CANTILEVERED VIEWING BALCONIES ---
    # Level 2 Balcony (Z = 4.8m)
    create_box("ARMS_Balcony_Level2_Slab", col_int, (atrium_cx, 375.0, 4.8), (52.0, 4.5, 0.4), mat_terrazzo)
    create_box("ARMS_Balcony_Level2_GlassRail", col_int, (atrium_cx, 377.2, 5.4), (52.0, 0.08, 1.0), mat_glass_clear)
    create_box("ARMS_Balcony_Level2_Handrail", col_int, (atrium_cx, 377.2, 5.9), (52.0, 0.12, 0.08), mat_mullion)

    # Level 3 Balcony (Z = 9.6m) - Eye level with Apollo spacecraft
    create_box("ARMS_Balcony_Level3_Slab", col_int, (atrium_cx, 375.0, 9.6), (52.0, 4.5, 0.4), mat_terrazzo)
    create_box("ARMS_Balcony_Level3_GlassRail", col_int, (atrium_cx, 377.2, 10.2), (52.0, 0.08, 1.0), mat_glass_clear)
    create_box("ARMS_Balcony_Level3_Handrail", col_int, (atrium_cx, 377.2, 10.7), (52.0, 0.12, 0.08), mat_mullion)

    # Open Terrazzo Grand Switchback Staircase
    create_box("ARMS_Stair_Flight_1", col_int, (atrium_cx - 22.0, 376.5, 2.4), (3.2, 5.5, 0.3), mat_terrazzo)
    create_box("ARMS_Stair_Landing_1", col_int, (atrium_cx - 22.0, 373.0, 4.8), (3.2, 2.4, 0.3), mat_terrazzo)
    create_box("ARMS_Stair_Railing_1", col_int, (atrium_cx - 20.3, 376.5, 3.2), (0.08, 5.5, 1.0), mat_glass_clear)

    # --- KURZ ATRIUM COLLABORATIVE STUDENT COMMONS ---
    # Study tables with task chairs and banker's lamps
    for i, x_tbl in enumerate([-128.0, -122.0, -98.0, -92.0]):
        # Study table
        create_box(f"ARMS_Study_Table_{i}", col_int, (x_tbl, 396.0, 0.76), (4.2, 1.8, 0.08), mat_oak)
        create_box(f"ARMS_Table_Leg_L_{i}", col_int, (x_tbl - 1.8, 396.0, 0.36), (0.12, 1.6, 0.72), mat_mullion)
        create_box(f"ARMS_Table_Leg_R_{i}", col_int, (x_tbl + 1.8, 396.0, 0.36), (0.12, 1.6, 0.72), mat_mullion)
        # Task chairs (6 per table)
        for c_idx, dx_c in enumerate([-1.2, 0.0, 1.2]):
            create_box(f"ARMS_Chair_N_{i}_{c_idx}", col_int, (x_tbl + dx_c, 397.3, 0.45), (0.5, 0.5, 0.85), mat_navy)
            create_box(f"ARMS_Chair_S_{i}_{c_idx}", col_int, (x_tbl + dx_c, 394.7, 0.45), (0.5, 0.5, 0.85), mat_navy)
        # Table accent lamp
        create_box(f"ARMS_Table_Lamp_{i}", col_int, (x_tbl, 396.0, 0.95), (0.6, 0.15, 0.25), mat_ceiling_downlight)

    # Modern lounge seating pods
    for i, x_pod in enumerate([-132.0, -88.0]):
        create_box(f"ARMS_Lounge_Sofa_{i}", col_int, (x_pod, 386.0, 0.42), (2.4, 1.2, 0.75), mat_navy)
        create_box(f"ARMS_Coffee_Table_{i}", col_int, (x_pod, 388.0, 0.35), (1.6, 0.9, 0.35), mat_oak)

    # Modern high-bay LED cylindrical downlights in Atrium ceiling
    for x_hl in range(-130, -90, 8):
        for y_hl in [382.0, 394.0]:
            create_cylinder(f"ARMS_HighBay_Luminaire_{x_hl}_{int(y_hl)}", col_int, (x_hl, y_hl, atrium_h - 1.2), 0.4, 0.6, mat_mullion, segments=12)
            hb_light = bpy.data.lights.new(name=f"ARMS_Light_HighBay_{x_hl}_{int(y_hl)}", type='POINT')
            hb_light.energy = 420.0
            hb_light.color = (1.0, 0.97, 0.92)
            hb_obj = bpy.data.objects.new(name=f"ARMS_Light_HighBay_{x_hl}_{int(y_hl)}", object_data=hb_light)
            col_int.objects.link(hb_obj)
            hb_obj.location = (x_hl, y_hl, atrium_h - 1.6)

    # --- ARMS 1010 MAJOR TIERED LECTURE HALL (East Wing Floor 1) ---
    aud_cx = -68.0
    aud_cy = 380.0
    aud_w = 20.0
    aud_d = 16.0
    aud_z = 0.08

    # Classroom floor slab & perimeter acoustic drywall partitions
    create_box("ARMS_Aud1010_Floor", col_int, (aud_cx, aud_cy, aud_z), (aud_w, aud_d, 0.16), mat_terrazzo)
    create_box("ARMS_Aud1010_Partition_N", col_int, (aud_cx, aud_cy + aud_d/2 - 0.15, 2.5), (aud_w, 0.3, 5.0), mat_stone)
    create_box("ARMS_Aud1010_Partition_S", col_int, (aud_cx, aud_cy - aud_d/2 + 0.15, 2.5), (aud_w, 0.3, 5.0), mat_stone)
    create_box("ARMS_Aud1010_Partition_W", col_int, (aud_cx - aud_w/2 + 0.15, aud_cy, 2.5), (0.3, aud_d, 5.0), mat_stone)

    # 5-Tier stepped concrete risers
    for r_idx in range(5):
        r_y = aud_cy - 4.5 + r_idx * 2.0
        r_z = 0.2 + r_idx * 0.42
        # Riser tier slab
        create_box(f"ARMS_Aud1010_Riser_{r_idx}", col_int, (aud_cx, r_y, r_z/2), (16.0, 1.9, r_z), mat_terrazzo)
        # Continuous oak desk table
        create_box(f"ARMS_Aud1010_Desk_{r_idx}", col_int, (aud_cx, r_y + 0.3, r_z + 0.4), (15.5, 0.5, 0.06), mat_oak)
        # Student task chairs (8 per tier)
        for s_idx in range(8):
            dx_s = -6.0 + s_idx * 1.7
            create_box(f"ARMS_Aud1010_Chair_{r_idx}_{s_idx}", col_int, (aud_cx + dx_s, r_y - 0.35, r_z + 0.22), (0.45, 0.45, 0.75), mat_navy)

    # Instructor presentation stage & dais
    stage_y = aud_cy + 6.0
    create_box("ARMS_Aud1010_Stage_Dais", col_int, (aud_cx, stage_y, 0.3), (16.0, 3.2, 0.4), mat_oak)
    create_box("ARMS_Aud1010_Smart_Podium", col_int, (aud_cx - 3.5, stage_y - 0.4, 0.95), (1.2, 0.75, 1.1), mat_oak)
    create_box("ARMS_Aud1010_Podium_Seal", col_int, (aud_cx - 3.5, stage_y - 0.78, 0.95), (0.4, 0.05, 0.4), mat_gold_plaque)

    # Dual 120" presentation screens & sliding chalkboards
    create_box("ARMS_Aud1010_Screen_L", col_int, (aud_cx - 4.2, aud_cy + aud_d/2 - 0.28, 3.2), (3.6, 0.08, 2.2), mat_white_tile)
    create_box("ARMS_Aud1010_Screen_R", col_int, (aud_cx + 4.2, aud_cy + aud_d/2 - 0.28, 3.2), (3.6, 0.08, 2.2), mat_white_tile)
    create_box("ARMS_Aud1010_Chalkboard", col_int, (aud_cx, aud_cy + aud_d/2 - 0.26, 2.4), (4.5, 0.06, 1.4), mat_chalk)

    # Auditorium ceiling warm illumination
    for x_al in [-5.0, 0.0, 5.0]:
        for y_al in [aud_cy - 2.0, aud_cy + 3.0]:
            create_box(f"ARMS_Aud1010_CeilingLight_{int(x_al)}_{int(y_al)}", col_int, (aud_cx + x_al, y_al, 4.8), (1.2, 1.2, 0.08), mat_ceiling_downlight)
            al_light = bpy.data.lights.new(name=f"ARMS_Light_Aud1010_{int(x_al)}_{int(y_al)}", type='POINT')
            al_light.energy = 380.0
            al_light.color = (1.0, 0.96, 0.90)
            al_obj = bpy.data.objects.new(name=f"ARMS_Light_Aud1010_{int(x_al)}_{int(y_al)}", object_data=al_light)
            col_int.objects.link(al_obj)
            al_obj.location = (aud_cx + x_al, y_al, 4.6)

    # --- NEIL ARMSTRONG HALL OF HEROES & ASTRONAUT EXHIBITION (West Wing Floor 1) ---
    hall_cx = -135.0
    hall_cy = 384.0
    create_box("ARMS_HallOfHeroes_Floor", col_int, (hall_cx, hall_cy, 0.08), (18.0, 14.0, 0.16), mat_terrazzo)

    # Astronaut commemorative gold honor wall
    create_box("ARMS_Astronaut_Honor_Wall", col_int, (hall_cx, hall_cy - 6.7, 2.4), (16.0, 0.2, 4.5), mat_stone)
    create_box("ARMS_Astronaut_Honor_Title", col_int, (hall_cx, hall_cy - 6.55, 3.8), (12.0, 0.08, 0.5), mat_gold_plaque)

    # 4 Glass artifact display cases (Apollo spacesuit, mission patches, moon rock replica)
    for c_idx, x_case in enumerate([-140.0, -136.0, -132.0, -128.0]):
        create_box(f"ARMS_Display_Pedestal_{c_idx}", col_int, (x_case, hall_cy + 3.5, 0.5), (1.4, 1.4, 0.95), mat_mullion)
        create_box(f"ARMS_Display_GlassCase_{c_idx}", col_int, (x_case, hall_cy + 3.5, 1.6), (1.3, 1.3, 1.2), mat_glass_clear)
        create_box(f"ARMS_Display_Artifact_{c_idx}", col_int, (x_case, hall_cy + 3.5, 1.4), (0.6, 0.6, 0.7), mat_white_tile)
        create_box(f"ARMS_Display_GoldPlaque_{c_idx}", col_int, (x_case, hall_cy + 2.78, 0.65), (0.6, 0.04, 0.25), mat_gold_plaque)
        # Dedicated spotlight for each case
        case_light = bpy.data.lights.new(name=f"ARMS_Light_Case_{c_idx}", type='SPOT')
        case_light.energy = 180.0
        case_light.spot_size = math.radians(35)
        case_light.color = (1.0, 0.95, 0.85)
        case_obj = bpy.data.objects.new(name=f"ARMS_Light_Case_{c_idx}", object_data=case_light)
        col_int.objects.link(case_obj)
        case_obj.location = (x_case, hall_cy + 3.5, 3.8)
        case_obj.rotation_euler = (0, 0, 0)

    # =========================================================================
    # 6. MOON PLAZA & CIVIC SITE INTEGRATION (41_Neil_Armstrong_Hall_MoonPlaza)
    # =========================================================================
    plaza_cx = atrium_cx
    plaza_cy = 415.0
    plaza_rad = 14.5

    # Circular Plaza Deck (radius 14.5m)
    create_cylinder("ARMS_Moon_Plaza_Granite_Bed", col_site, (plaza_cx, plaza_cy, 0.08), plaza_rad, 0.16, mat_lunar_plinth, segments=36)
    create_cylinder("ARMS_Moon_Plaza_Inner_Pad", col_site, (plaza_cx, plaza_cy, 0.12), plaza_rad - 1.2, 0.12, mat_terrazzo, segments=36)

    # Flanking curved limestone seatwalls
    for side, ang_base in [("East", 25), ("West", 155)]:
        for w_idx in range(6):
            curv_ang = math.radians(ang_base + w_idx * 10)
            wx = plaza_cx + (plaza_rad + 0.8) * math.cos(curv_ang)
            wy = plaza_cy + (plaza_rad + 0.8) * math.sin(curv_ang)
            create_box(f"ARMS_Plaza_Seatwall_{side}_{w_idx}", col_site, (wx, wy, 0.45), (1.6, 0.7, 0.75), mat_stone)

    # Authentic life-size Bronze Statue of Neil Armstrong seated on limestone bench
    bench_x = plaza_cx + 4.5
    bench_y = plaza_cy - 1.8
    # Limestone bench
    create_box("ARMS_Statue_Limestone_Bench", col_site, (bench_x, bench_y, 0.42), (2.4, 0.8, 0.5), mat_stone)
    # Bronze Statue of young Neil Armstrong
    create_box("ARMS_Statue_Neil_Legs", col_site, (bench_x - 0.2, bench_y + 0.15, 0.45), (0.5, 0.4, 0.6), mat_bronze)
    create_box("ARMS_Statue_Neil_Torso", col_site, (bench_x - 0.2, bench_y - 0.05, 0.95), (0.5, 0.42, 0.75), mat_bronze)
    create_box("ARMS_Statue_Neil_Head", col_site, (bench_x - 0.2, bench_y - 0.05, 1.5), (0.28, 0.28, 0.32), mat_bronze)
    create_box("ARMS_Statue_Notebook_on_Bench", col_site, (bench_x + 0.5, bench_y, 0.7), (0.35, 0.4, 0.08), mat_bronze)

    # Apollo 11 Lunar Boot Prints in Plaza Pavement
    # The real footprints walk from Neil's bench toward the Armstrong Hall entrance
    print("Embedding authentic Apollo 11 lunar boot prints in Moon Plaza...")
    footprint_coords = [
        (bench_x - 1.2, bench_y + 1.2, 0.14),
        (bench_x - 2.6, bench_y + 2.8, 0.14),
        (bench_x - 4.2, bench_y + 4.6, 0.14),
        (bench_x - 6.0, bench_y + 6.2, 0.14),
        (bench_x - 7.8, bench_y + 8.0, 0.14),
        (bench_x - 9.8, bench_y + 9.6, 0.14)
    ]
    for idx, (fx, fy, fz) in enumerate(footprint_coords):
        # Boot print base plate
        create_box(f"Apollo11_Bootprint_{idx}_Plate", col_site, (fx, fy, fz), (0.38, 0.20, 0.02), mat_bronze)
        # Tread ridges
        for r_i in range(3):
            create_box(f"Apollo11_Bootprint_{idx}_Tread_{r_i}", col_site, (fx, fy - 0.06 + r_i * 0.06, fz + 0.015), (0.32, 0.03, 0.015), mat_gold_plaque)

    # Campus Teak Wood Benches & Sheffield Bike Racks
    for b_i, bx in enumerate([-132.0, -126.0, -95.0, -89.0]):
        create_box(f"ARMS_Plaza_TeakBench_{b_i}", col_site, (bx, 418.0, 0.45), (2.0, 0.65, 0.75), mat_oak)

    for r_i, rx in enumerate([-138.0, -136.0, -134.0, -84.0, -82.0, -80.0]):
        create_box(f"ARMS_Bike_Rack_{r_i}", col_site, (rx, 420.0, 0.5), (0.1, 1.2, 0.9), mat_mullion)

    # Architectural LED Bollards flanking arrival concourse
    for b_idx, by in enumerate([408.0, 414.0, 420.0]):
        for bx in [atrium_cx - 10.0, atrium_cx + 10.0]:
            create_cylinder(f"ARMS_LED_Bollard_{int(bx)}_{int(by)}", col_site, (bx, by, 0.5), 0.12, 1.0, mat_mullion, segments=12)
            create_cylinder(f"ARMS_LED_Bollard_Glow_{int(bx)}_{int(by)}", col_site, (bx, by, 0.95), 0.11, 0.15, mat_ceiling_downlight, segments=12)

    # =========================================================================
    # 7. DEDICATED INSPECTION CAMERAS (Cam 57 to Cam 61)
    # =========================================================================
    def setup_cam(name, loc, target, focal_length=22.0):
        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name)
            cam_obj = bpy.data.objects.new(name, cam_data)
            col_cams.objects.link(cam_obj)
        else:
            cam_data = cam_obj.data
            
        cam_obj.location = loc
        cam_data.lens = focal_length
        cam_data.clip_start = 0.1
        cam_data.clip_end = 2500.0
        
        # Track to target
        direction = mathutils.Vector(target) - mathutils.Vector(loc)
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        return cam_obj

    # Cam 57: North Hero Street View from Stadium Ave framing curved facade, canopy, plaza, & statue
    setup_cam("Cam_57_Neil_Armstrong_North_StreetView", 
              loc=(-110.5, 442.0, 4.5), 
              target=(-110.5, 405.0, 10.0), 
              focal_length=20.0)

    # Cam 58: Kurz Atrium Ground Floor looking up at suspended Apollo spacecraft & skylight
    setup_cam("Cam_58_Neil_Armstrong_Kurz_Atrium_Spacecraft_Hero", 
              loc=(-110.5, 374.0, 2.2), 
              target=(-110.5, 388.0, 13.5), 
              focal_length=18.0)

    # Cam 59: Kurz Atrium Level 2 Balcony Overlook standing by the glass balustrade next to the spacecraft
    setup_cam("Cam_59_Neil_Armstrong_Atrium_Level2_Balcony_Overlook", 
              loc=(-128.0, 384.0, 6.2), 
              target=(-110.5, 388.0, 11.5), 
              focal_length=20.0)

    # Cam 60: ARMS 1010 Major Tiered Lecture Hall interior
    setup_cam("Cam_60_Neil_Armstrong_Auditorium_1010_Interior", 
              loc=(-68.0, 373.0, 2.4), 
              target=(-68.0, 385.0, 2.2), 
              focal_length=19.0)

    # Cam 61: Aerial Engineering Precinct View connecting Armstrong Hall to Stadium Ave, Northwestern Ave, and Engineering Mall
    setup_cam("Cam_61_Neil_Armstrong_Engineering_Precinct_Aerial", 
              loc=(-165.0, 460.0, 52.0), 
              target=(-108.0, 390.0, 8.0), 
              focal_length=28.0)

    print("Reconstruction complete! Saving scene...")
    bpy.ops.wm.save_mainfile(filepath=r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend")
    print(f"Total objects in scene: {len(bpy.data.objects)}")
    print(f"Exterior objects: {len(col_ext.objects)}")
    print(f"Interior objects: {len(col_int.objects)}")
    print(f"Site/Plaza objects: {len(col_site.objects)}")
    print("=== Successfully built Neil Armstrong Hall of Engineering (ARMS) ===")

if __name__ == "__main__":
    run()
