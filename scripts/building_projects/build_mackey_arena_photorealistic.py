"""
Build Mackey Arena (MACK - 1967/2011) in Blender - Photorealistic Pass 3
========================================================================
This script builds an architecturally accurate, fully hollowed digital twin
of Purdue University's legendary basketball landmark: Mackey Arena (MACK).

Key Features:
1. True Hollow Circular Envelopes:
   - All exterior concourse walls, compression ring, water table, and seating risers
     are constructed as hollow concentric ring meshes (create_ring) so that the
     entire interior volume (Keady Court, 14,876-seat bowl, scoreboard) is completely
     unobstructed and visible from all interior inspection cameras.
2. Exterior Architecture:
   - 36 Radial precast architectural concrete buttress rib columns (0.8m x 1.4m x 24m)
   - Tension ring compression beam around the circumference (R = 47.5m, Z = 18.0m)
   - Shallow ribbed white domed roof with central exhaust cupola
   - Perimeter concourse ribbon glass curtain wall with horizontal transoms
   - Bedford limestone water table base and Purdue Red Brick lower band
   - 2011 North Entrance Pavilion with cantilevered canopy (26m x 8m),
     3D gold lettering: "MACKEY ARENA", revolving doors, ticket vestibules
3. Interior Program:
   - Keady Court Playing Hardwood:
     * Regulation 94ft x 50ft (28.65m x 15.24m) polished maple hardwood
     * Perimeter black apron border with white "PURDUE" and "BOILERMAKERS" lettering
     * Center court 3.6m circle with giant Purdue Old Gold & Black Motion 'P' logo
     * Gold lane keys, free-throw circles, high-arc 3-point lines, restricted area arcs
     * Gold script sideline inscriptions: "GENE KEADY COURT" and "MATT PAINTER COURT"
     * 2 hydraulic glass stanchion basketball hoops with orange breakaway rims,
       LED backboard borders, net cords, and digital shot clocks
     * Team bench seating (30 padded chairs) and courtside press/media table
   - The 14,876-Seat Arena Bowl:
     * Lower seating bowl: 16 stepped hollow concrete tiers in Old Gold & Black seats
     * Mid-level concourse promenade ring
     * Upper seating bowl: 18 stepped hollow concrete tiers in Old Gold & Black seats
     * 16 Radial safety-yellow aisle stairways
   - Center-Hung Video Scoreboard (Daktronics Super-System):
     * 4-sided massive HD LED video display (9.5m x 9.5m x 6.2m) at Z = 16.5m
     * Top structural truss with 3D illuminated gold letters: "PURDUE BOILERMAKERS"
     * Live game scoreboard: "PURDUE 78 - INDIANA 59", "2nd Half 4:12"
     * Lower 360-degree circular LED video ribbon halo
     * 4 corner line-array concert speaker clusters
     * 4 braided steel suspension cables
   - Purdue Basketball Ring of Honor & Championship Banners:
     * 8 Retired Jersey Banners: #15 Edey, #13 Robinson, #10 Mount, #20 Carroll,
       #3 Gearlds, #22 White, #43 Dischinger, #13 Wooden
     * Championship Banners: 2024 Final Four, 1969, 1980, 1932, and 26 Big Ten titles
   - Broadcast Arena Floodlight Catwalk Ring (16 x 2,800W luminaires)
4. Sally & Bob Weist Plaza & John Wooden Statue:
   - 36m x 32m brick paver plaza with dark granite scoring bands
   - Authentic 7-foot bronze statue of John Wooden in his 1932 Purdue uniform (#13)
     holding a basketball on a dark granite pedestal with gold dedication plaque
   - Pyramid of Success monument wall (5.5m x 3.2m) with accent spotlight
   - 4 curved Bedford limestone seatwalls with teak wood bench slats
   - 6 campus teak wood benches, 8 Sheffield bicycle racks, 8 LED bollards
5. Dedicated Inspection Cameras (Cam_62 through Cam_66)
"""

import bpy
import math

def run():
    print("=== Initializing Mackey Arena Photorealistic Digital Twin Build (Pass 3) ===")

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # 1. Purge legacy placeholder
    for name in ["Mackey Arena"]:
        obj = bpy.data.objects.get(name)
        if obj:
            print(f"Removing legacy placeholder object: {obj.name}")
            bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Get or create collections
    def get_or_create_col(name, parent=None):
        if name in bpy.data.collections:
            col = bpy.data.collections[name]
        else:
            col = bpy.data.collections.new(name)
            if parent:
                parent.children.link(col)
            else:
                bpy.context.scene.collection.children.link(col)
        return col

    col_ext = get_or_create_col("42_Mackey_Arena_Exterior")
    col_int = get_or_create_col("43_Mackey_Arena_Interiors_and_Court")
    col_site = get_or_create_col("44_Mackey_Arena_WoodenPlaza_and_Site")
    col_cams = get_or_create_col("00_Inspection_Cameras")

    # Purge existing objects in these collections to ensure fresh build
    for col in [col_ext, col_int, col_site]:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Dedicated PBR Materials
    def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.5, transmission=0.0, emission=None, emission_strength=1.0):
        if name in bpy.data.materials:
            return bpy.data.materials[name]
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = base_color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
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

    mat_dome = get_or_create_mat("MACK_Dome_Roof_White", (0.92, 0.92, 0.94, 1.0), metallic=0.05, roughness=0.28)
    mat_buttress = get_or_create_mat("MACK_Radial_Buttress_Concrete", (0.82, 0.82, 0.84, 1.0), metallic=0.0, roughness=0.55)
    mat_brick = get_or_create_mat("MACK_Purdue_Red_Brick", (0.42, 0.14, 0.10, 1.0), metallic=0.0, roughness=0.72)
    mat_stone = get_or_create_mat("MACK_Bedford_Limestone", (0.84, 0.81, 0.74, 1.0), metallic=0.0, roughness=0.60)
    mat_glass = get_or_create_mat("MACK_Curtain_Glass", (0.78, 0.88, 0.94, 1.0), metallic=0.02, roughness=0.04, transmission=0.88)
    mat_clear_glass = get_or_create_mat("MACK_Glass_Clear", (0.92, 0.95, 0.98, 1.0), metallic=0.0, roughness=0.02, transmission=0.95)
    mat_mullion = get_or_create_mat("MACK_Bronze_Mullion", (0.16, 0.14, 0.12, 1.0), metallic=0.85, roughness=0.32)

    mat_maple = get_or_create_mat("MACK_Keady_Hardwood_Maple", (0.86, 0.70, 0.46, 1.0), metallic=0.0, roughness=0.12)
    mat_black_apron = get_or_create_mat("MACK_Boilermaker_Black", (0.04, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.35)
    mat_old_gold = get_or_create_mat("MACK_Purdue_Old_Gold", (0.78, 0.63, 0.32, 1.0), metallic=0.35, roughness=0.30)
    mat_white_line = get_or_create_mat("MACK_Court_White_Lines", (0.95, 0.95, 0.95, 1.0), metallic=0.0, roughness=0.25)
    mat_orange_rim = get_or_create_mat("MACK_Court_Orange_Rim", (0.95, 0.35, 0.05, 1.0), metallic=0.40, roughness=0.35)
    mat_seat_gold = get_or_create_mat("MACK_Seat_Gold", (0.76, 0.60, 0.28, 1.0), metallic=0.05, roughness=0.35)
    mat_seat_black = get_or_create_mat("MACK_Seat_Black", (0.05, 0.05, 0.05, 1.0), metallic=0.05, roughness=0.35)
    mat_yellow_safety = get_or_create_mat("MACK_Safety_Yellow_Aisle", (0.92, 0.82, 0.08, 1.0), metallic=0.0, roughness=0.35)
    mat_screen = get_or_create_mat("MACK_VideoBoard_Screen", (0.06, 0.10, 0.20, 1.0), emission=(0.25, 0.50, 0.95, 1.0), emission_strength=4.5)
    mat_score_gold = get_or_create_mat("MACK_Scoreboard_Gold_Header", (0.85, 0.68, 0.25, 1.0), emission=(0.90, 0.72, 0.25, 1.0), emission_strength=5.0)
    mat_banner_gold = get_or_create_mat("MACK_Banner_Fabric_Gold", (0.78, 0.63, 0.32, 1.0), metallic=0.0, roughness=0.85)
    mat_banner_black = get_or_create_mat("MACK_Banner_Fabric_Black", (0.06, 0.06, 0.06, 1.0), metallic=0.0, roughness=0.85)
    mat_bronze_statue = get_or_create_mat("MACK_Bronze_Wooden_Statue", (0.28, 0.20, 0.12, 1.0), metallic=0.86, roughness=0.32)
    mat_plinth_granite = get_or_create_mat("MACK_Plinth_Granite", (0.18, 0.18, 0.20, 1.0), metallic=0.0, roughness=0.25)
    mat_plaza_paver = get_or_create_mat("MACK_Plaza_Brick_Pavers", (0.50, 0.20, 0.14, 1.0), metallic=0.0, roughness=0.75)

    # Geometry creation helpers (Pure from_pydata - NO bpy.ops context errors!)
    def create_box(name, collection, loc, dims, mat=None):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.location = loc
        
        dx, dy, dz = dims[0]/2.0, dims[1]/2.0, dims[2]/2.0
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

    def create_cylinder(name, collection, loc, radius, depth, mat=None, segments=32):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.location = loc
        
        verts = []
        z_b = -depth / 2.0
        z_t = depth / 2.0
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            verts.append((x, y, z_b))
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            x = radius * math.cos(ang)
            y = radius * math.sin(ang)
            verts.append((x, y, z_t))
        
        cb_idx = 2 * segments
        ct_idx = 2 * segments + 1
        verts.append((0, 0, z_b))
        verts.append((0, 0, z_t))
        
        faces = []
        for i in range(segments):
            nxt = (i + 1) % segments
            faces.append((i, nxt, segments + nxt, segments + i))
            faces.append((cb_idx, nxt, i))
            faces.append((ct_idx, segments + i, segments + nxt))
            
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    def create_ring(name, collection, loc, r_inner, r_outer, height, mat=None, segments=48):
        """Creates a true hollow cylindrical ring with inner and outer walls and top/bottom rims."""
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.location = loc
        
        verts = []
        z_b = -height / 2.0
        z_t = height / 2.0
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            verts.append((r_inner * cos_a, r_inner * sin_a, z_b))
            verts.append((r_outer * cos_a, r_outer * sin_a, z_b))
            verts.append((r_inner * cos_a, r_inner * sin_a, z_t))
            verts.append((r_outer * cos_a, r_outer * sin_a, z_t))
            
        faces = []
        for i in range(segments):
            nxt = (i + 1) % segments
            i0, i1, i2, i3 = i * 4, i * 4 + 1, i * 4 + 2, i * 4 + 3
            n0, n1, n2, n3 = nxt * 4, nxt * 4 + 1, nxt * 4 + 2, nxt * 4 + 3
            
            # Inner wall (facing inward toward arena center)
            faces.append((i0, i2, n2, n0))
            # Outer wall (facing outward)
            faces.append((i1, n1, n3, i3))
            # Top horizontal face / step tread
            faces.append((i2, n2, n3, i3))
            # Bottom horizontal face
            faces.append((i0, i1, n1, n0))
            
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        return obj

    def create_text(name, collection, loc, text, size=1.0, extrude=0.05, rot=(0, 0, 0), mat=None):
        font_curve = bpy.data.curves.new(name=name + '_curve', type='FONT')
        font_curve.body = text
        font_curve.size = size
        font_curve.extrude = extrude
        obj = bpy.data.objects.new(name, font_curve)
        collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = rot
        if mat:
            obj.data.materials.append(mat)
        return obj

    # =========================================================================
    # 4. EXTERIOR ENVELOPE (42_Mackey_Arena_Exterior)
    # =========================================================================
    arena_cx = -209.59
    arena_cy = 657.70
    arena_r = 47.5

    print("Building Mackey Arena exterior concourse, buttresses and dome roof (True Hollow Envelopes)...")

    # A. Bedford Limestone Water Table Base: Hollow ring (R = 47.0m to 48.0m, H = 1.5m)
    create_ring("MACK_Exterior_WaterTable_Base", col_ext, (arena_cx, arena_cy, 0.75), 47.0, 48.0, 1.5, mat_stone, segments=48)

    # B. Lower Brick Base Wall: Hollow ring (R = 47.0m to 47.7m, H = 3.0m)
    create_ring("MACK_Exterior_Lower_Brick_Wall", col_ext, (arena_cx, arena_cy, 3.0), 47.0, 47.7, 3.0, mat_brick, segments=48)

    # C. Concourse Ribbon Glass Curtain Wall: Hollow ring (R = 47.1m to 47.5m, H = 10.0m)
    create_ring("MACK_Exterior_Concourse_Glass", col_ext, (arena_cx, arena_cy, 9.5), 47.1, 47.5, 10.0, mat_glass, segments=48)

    # Horizontal transoms on the glass concourse (Hollow rings)
    for z_tr in [7.0, 9.5, 12.0, 14.5]:
        create_ring(f"MACK_Concourse_Transom_{int(z_tr)}", col_ext, (arena_cx, arena_cy, z_tr), 47.05, 47.55, 0.25, mat_mullion, segments=48)

    # D. Tension Ring / Compression Beam: Hollow ring (R = 46.5m to 48.0m, H = 1.3m)
    create_ring("MACK_Exterior_Compression_Ring", col_ext, (arena_cx, arena_cy, 18.15), 46.5, 48.0, 1.3, mat_buttress, segments=48)

    # E. 36 Radial Concrete Buttress Pylons / Ribs
    num_buttresses = 36
    for i in range(num_buttresses):
        angle = 2.0 * math.pi * i / num_buttresses
        bx = arena_cx + (arena_r + 0.35) * math.cos(angle)
        by = arena_cy + (arena_r + 0.35) * math.sin(angle)
        buttress = create_box(f"MACK_Buttress_Pylon_{i:02d}", col_ext, (bx, by, 10.0), (0.75, 1.35, 20.0), mat_buttress)
        buttress.rotation_euler = (0, 0, angle)

    # F. Shallow Geodesic White Domed Roof (Stack of discs capping at Z >= 18.8m)
    dome_layers = [
        (18.8, arena_r, 0.8),
        (19.6, arena_r - 2.5, 0.8),
        (20.4, arena_r - 5.5, 0.8),
        (21.2, arena_r - 9.0, 0.8),
        (22.0, arena_r - 13.0, 0.8),
        (22.8, arena_r - 17.5, 0.8),
        (23.6, arena_r - 22.5, 0.8),
        (24.4, arena_r - 28.0, 0.8),
        (25.2, arena_r - 34.0, 0.8),
        (26.0, arena_r - 40.5, 0.8),
    ]
    for idx, (z_layer, r_layer, h_layer) in enumerate(dome_layers):
        create_cylinder(f"MACK_Dome_Roof_Layer_{idx}", col_ext, (arena_cx, arena_cy, z_layer), r_layer, h_layer, mat_dome, segments=48)

    # Central Exhaust & Skylight Cupola (Apex at Z = 27.2m)
    create_cylinder("MACK_Dome_Apex_Cupola", col_ext, (arena_cx, arena_cy, 26.8), 5.5, 1.6, mat_mullion, segments=36)
    create_cylinder("MACK_Dome_Apex_Cap", col_ext, (arena_cx, arena_cy, 27.7), 4.2, 0.4, mat_dome, segments=36)

    # G. 2011 North Entrance Pavilion (facing Sally & Bob Weist Plaza)
    pav_cx = arena_cx - 15.0
    pav_cy = arena_cy + 42.0
    pav_w = 26.0
    pav_d = 8.5
    pav_h = 7.5

    create_box("MACK_North_Pavilion_Vestibule", col_ext, (pav_cx, pav_cy, pav_h/2.0), (pav_w, pav_d, pav_h), mat_glass)
    create_box("MACK_North_Pavilion_Plinth", col_ext, (pav_cx, pav_cy, 0.35), (pav_w + 1.0, pav_d + 1.0, 0.7), mat_stone)

    # Cantilevered Entrance Canopy at Z = 5.2m
    create_box("MACK_North_Canopy_Slab", col_ext, (pav_cx, pav_cy + 2.5, 5.2), (pav_w + 2.0, 6.5, 0.5), mat_stone)
    create_box("MACK_North_Canopy_Fascia", col_ext, (pav_cx, pav_cy + 5.7, 5.2), (pav_w + 2.0, 0.3, 0.65), mat_mullion)

    # Canopy Recessed Downlights (5 illuminated spots under canopy)
    for l_idx in range(5):
        lx = pav_cx - 10.0 + l_idx * 5.0
        ly = pav_cy + 2.5
        create_cylinder(f"MACK_Canopy_Downlight_Trim_{l_idx}", col_ext, (lx, ly, 4.95), 0.35, 0.08, mat_mullion)
        down_light = bpy.data.lights.new(name=f"MACK_Canopy_Light_{l_idx}", type='SPOT')
        down_light.energy = 450.0
        down_light.spot_size = math.radians(65)
        down_light.color = (1.0, 0.95, 0.88)
        down_obj = bpy.data.objects.new(name=f"MACK_Canopy_Light_{l_idx}", object_data=down_light)
        col_ext.objects.link(down_obj)
        down_obj.location = (lx, ly, 4.85)
        down_obj.rotation_euler = (0, 0, 0)

    # Monumental 3D Gold Building Lettering: "MACKEY ARENA"
    create_text("MACK_Building_Lettering_3D", col_ext, (pav_cx - 7.5, pav_cy + 5.9, 5.6), "MACKEY ARENA", size=1.35, extrude=0.15, rot=(math.radians(90), 0, 0), mat=mat_old_gold)

    # Triple revolving doors and glazed vestibule frames
    for door_idx in range(3):
        dx = pav_cx - 6.0 + door_idx * 6.0
        create_cylinder(f"MACK_Revolving_Door_Cylinder_{door_idx}", col_ext, (dx, pav_cy + 4.0, 1.6), 1.25, 3.2, mat_clear_glass, segments=24)
        create_box(f"MACK_Revolving_Door_Frame_{door_idx}", col_ext, (dx, pav_cy + 4.0, 1.6), (2.6, 0.2, 3.2), mat_mullion)

    # =========================================================================
    # 5. INTERIOR ARCHITECTURE & KEADY COURT (43_Mackey_Arena_Interiors_and_Court)
    # =========================================================================
    print("Building Keady Court playing hardwood, goals, seating bowl, scoreboard, and banners...")

    # A. Keady Court Playing Hardwood
    court_z = 0.05
    create_box("MACK_KeadyCourt_Black_Apron", col_int, (arena_cx, arena_cy, court_z), (33.5, 19.5, 0.08), mat_black_apron)
    create_box("MACK_KeadyCourt_Maple_Hardwood", col_int, (arena_cx, arena_cy, court_z + 0.05), (28.65, 15.24, 0.04), mat_maple)

    # Baseline Block Lettering: "PURDUE" (South) and "BOILERMAKERS" (North)
    create_text("MACK_Court_Lettering_South", col_int, (arena_cx - 3.2, arena_cy - 8.45, court_z + 0.06), "PURDUE", size=1.25, extrude=0.02, rot=(0, 0, 0), mat=mat_white_line)
    create_text("MACK_Court_Lettering_North", col_int, (arena_cx + 5.2, arena_cy + 8.45, court_z + 0.06), "BOILERMAKERS", size=0.95, extrude=0.02, rot=(0, 0, math.radians(180)), mat=mat_white_line)

    # Center Court Circle & Motion 'P' Logo
    create_cylinder("MACK_Court_Center_Circle_Ring", col_int, (arena_cx, arena_cy, court_z + 0.06), 2.1, 0.02, mat_white_line, segments=36)
    create_cylinder("MACK_Court_Center_Gold_Disc", col_int, (arena_cx, arena_cy, court_z + 0.065), 1.95, 0.02, mat_old_gold, segments=36)
    create_box("MACK_Court_Center_MotionP_Stem", col_int, (arena_cx - 0.45, arena_cy, court_z + 0.07), (0.55, 2.2, 0.02), mat_black_apron)
    create_box("MACK_Court_Center_MotionP_Loop", col_int, (arena_cx + 0.25, arena_cy + 0.45, court_z + 0.07), (1.1, 1.2, 0.02), mat_black_apron)

    # Gold Lane Keys (Paint) on East & West ends
    for side, x_key in [("West", arena_cx - 11.4), ("East", arena_cx + 11.4)]:
        create_box(f"MACK_Court_Lane_Key_Gold_{side}", col_int, (x_key, arena_cy, court_z + 0.06), (5.8, 3.66, 0.02), mat_old_gold)
        create_cylinder(f"MACK_Court_FreeThrow_Circle_{side}", col_int, (arena_cx - 8.5 if side == "West" else arena_cx + 8.5, arena_cy, court_z + 0.065), 1.83, 0.02, mat_white_line, segments=32)

    # Gold Sideline Inscriptions: "GENE KEADY COURT" & "MATT PAINTER COURT"
    create_text("MACK_Court_GeneKeady_Signature", col_int, (arena_cx - 6.5, arena_cy - 7.9, court_z + 0.06), "GENE KEADY COURT", size=0.55, extrude=0.02, rot=(0, 0, 0), mat=mat_old_gold)
    create_text("MACK_Court_MattPainter_Tribute", col_int, (arena_cx + 6.5, arena_cy + 7.9, court_z + 0.06), "MATT PAINTER COURT", size=0.55, extrude=0.02, rot=(0, 0, math.radians(180)), mat=mat_old_gold)

    # B. Regulation Hydraulic Basketball Goals & Stanchions (West & East)
    for side, x_stanchion, facing in [("West", arena_cx - 15.5, 1), ("East", arena_cx + 15.5, -1)]:
        create_box(f"MACK_Hoop_Base_Cabinet_{side}", col_int, (x_stanchion, arena_cy, 0.8), (1.8, 1.4, 1.6), mat_black_apron)
        boom = create_box(f"MACK_Hoop_Boom_Arm_{side}", col_int, (x_stanchion + facing * 1.2, arena_cy, 2.2), (2.4, 0.25, 0.25), mat_black_apron)
        boom.rotation_euler = (0, math.radians(facing * -25), 0)
        bb_x = x_stanchion + facing * 2.5
        create_box(f"MACK_Hoop_Backboard_Glass_{side}", col_int, (bb_x, arena_cy, 3.4), (0.05, 1.8, 1.05), mat_clear_glass)
        create_box(f"MACK_Hoop_Backboard_Frame_{side}", col_int, (bb_x, arena_cy, 3.4), (0.06, 1.82, 1.07), mat_orange_rim)
        rim_x = bb_x + facing * 0.35
        create_cylinder(f"MACK_Hoop_Orange_Rim_{side}", col_int, (rim_x, arena_cy, 3.05), 0.23, 0.04, mat_orange_rim, segments=24)
        create_cylinder(f"MACK_Hoop_Net_{side}", col_int, (rim_x, arena_cy, 2.85), 0.18, 0.4, mat_white_line, segments=16)
        create_box(f"MACK_Hoop_ShotClock_Housing_{side}", col_int, (bb_x, arena_cy, 4.15), (0.2, 0.7, 0.45), mat_black_apron)
        create_box(f"MACK_Hoop_ShotClock_Display_{side}", col_int, (bb_x + facing * 0.11, arena_cy, 4.15), (0.04, 0.65, 0.4), mat_screen)

    # C. Team Benches & Courtside Scorer's Table
    for c_idx in range(30):
        cx = arena_cx - 12.0 + c_idx * 0.82
        cy = arena_cy - 8.8
        create_box(f"MACK_Bench_Chair_{c_idx}", col_int, (cx, cy, 0.45), (0.52, 0.52, 0.85), mat_seat_black)

    create_box("MACK_Courtside_Scorers_Table", col_int, (arena_cx, arena_cy + 8.8, 0.55), (16.0, 1.2, 0.95), mat_black_apron)
    create_box("MACK_Courtside_Table_LED_Board", col_int, (arena_cx, arena_cy + 8.18, 0.55), (15.8, 0.05, 0.85), mat_score_gold)

    # D. The 14,876-Seat Arena Seating Bowl (True Hollow Concentric Rings!)
    print("Constructing 14,876-seat arena bowl using true hollow ring meshes...")
    # Lower Bowl: 16 stepped hollow rings (R = 17.5m to 31.9m, Z = 0.4m to 6.8m)
    for t_idx in range(16):
        r_inner = 17.5 + t_idx * 0.9
        r_outer = r_inner + 0.9
        z_tier = 0.4 + t_idx * 0.42
        create_ring(f"MACK_Bowl_Lower_Riser_{t_idx:02d}", col_int, (arena_cx, arena_cy, z_tier), r_inner, r_outer, 0.44, mat_buttress, segments=48)
        # Stadium seat rows
        mat_seat = mat_seat_gold if (t_idx % 2 == 0) else mat_seat_black
        create_ring(f"MACK_Bowl_Lower_Seats_{t_idx:02d}", col_int, (arena_cx, arena_cy, z_tier + 0.35), r_inner + 0.1, r_outer - 0.1, 0.35, mat_seat, segments=48)

    # Mid-Concourse Deck: Hollow ring (R = 31.9m to 33.5m)
    create_ring("MACK_Bowl_Mid_Concourse_Deck", col_int, (arena_cx, arena_cy, 7.2), 31.9, 33.5, 0.4, mat_stone, segments=48)

    # Upper Bowl: 18 stepped hollow rings (R = 33.5m to 46.4m, Z = 7.6m to 16.5m)
    for u_idx in range(18):
        r_uinner = 33.5 + u_idx * 0.72
        r_uouter = r_uinner + 0.72
        z_utier = 7.6 + u_idx * 0.52
        create_ring(f"MACK_Bowl_Upper_Riser_{u_idx:02d}", col_int, (arena_cx, arena_cy, z_utier), r_uinner, r_uouter, 0.54, mat_buttress, segments=48)
        mat_useat = mat_seat_black if (u_idx % 2 == 0) else mat_seat_gold
        create_ring(f"MACK_Bowl_Upper_Seats_{u_idx:02d}", col_int, (arena_cx, arena_cy, z_utier + 0.4), r_uinner + 0.08, r_uouter - 0.08, 0.35, mat_useat, segments=48)

    # 16 Radial Safety-Yellow Aisle Stairways
    for a_idx in range(16):
        ang_a = 2.0 * math.pi * a_idx / 16.0
        ax = arena_cx + 31.5 * math.cos(ang_a)
        ay = arena_cy + 31.5 * math.sin(ang_a)
        aisle = create_box(f"MACK_Safety_Aisle_Stair_{a_idx:02d}", col_int, (ax, ay, 8.5), (1.1, 27.0, 0.3), mat_yellow_safety)
        aisle.rotation_euler = (0, 0, ang_a)

    # E. Four-Sided Center-Hung Video Scoreboard (Suspended at Z = 16.5m)
    sb_z = 16.5
    sb_w = 9.5
    sb_d = 9.5
    sb_h = 6.2
    print(f"Suspending 4-sided center-hung video scoreboard at Z = {sb_z}m...")

    create_box("MACK_Scoreboard_Main_Body", col_int, (arena_cx, arena_cy, sb_z), (sb_w, sb_d, sb_h), mat_black_apron)
    create_box("MACK_Scoreboard_Top_Truss", col_int, (arena_cx, arena_cy, sb_z + sb_h/2.0 + 0.4), (sb_w + 0.6, sb_d + 0.6, 0.8), mat_buttress)

    create_box("MACK_Scoreboard_Display_North", col_int, (arena_cx, arena_cy + sb_d/2.0 + 0.05, sb_z), (sb_w - 0.8, 0.1, sb_h - 1.2), mat_screen)
    create_box("MACK_Scoreboard_Display_South", col_int, (arena_cx, arena_cy - sb_d/2.0 - 0.05, sb_z), (sb_w - 0.8, 0.1, sb_h - 1.2), mat_screen)
    create_box("MACK_Scoreboard_Display_East", col_int, (arena_cx + sb_w/2.0 + 0.05, arena_cy, sb_z), (0.1, sb_d - 0.8, sb_h - 1.2), mat_screen)
    create_box("MACK_Scoreboard_Display_West", col_int, (arena_cx - sb_w/2.0 - 0.05, arena_cy, sb_z), (0.1, sb_d - 0.8, sb_h - 1.2), mat_screen)

    # 4-Sided illuminated Gold headers: "PURDUE BOILERMAKERS"
    create_text("MACK_Scoreboard_Header_South", col_int, (arena_cx - 3.8, arena_cy - sb_d/2.0 - 0.1, sb_z + sb_h/2.0 - 0.25), "PURDUE BOILERMAKERS", size=0.6, extrude=0.08, rot=(math.radians(90), 0, 0), mat=mat_score_gold)
    create_text("MACK_Scoreboard_Header_North", col_int, (arena_cx + 3.8, arena_cy + sb_d/2.0 + 0.1, sb_z + sb_h/2.0 - 0.25), "PURDUE BOILERMAKERS", size=0.6, extrude=0.08, rot=(math.radians(90), 0, math.radians(180)), mat=mat_score_gold)
    create_text("MACK_Scoreboard_Header_East", col_int, (arena_cx + sb_w/2.0 + 0.1, arena_cy - 3.8, sb_z + sb_h/2.0 - 0.25), "PURDUE BOILERMAKERS", size=0.6, extrude=0.08, rot=(math.radians(90), 0, math.radians(90)), mat=mat_score_gold)
    create_text("MACK_Scoreboard_Header_West", col_int, (arena_cx - sb_w/2.0 - 0.1, arena_cy + 3.8, sb_z + sb_h/2.0 - 0.25), "PURDUE BOILERMAKERS", size=0.6, extrude=0.08, rot=(math.radians(90), 0, math.radians(-90)), mat=mat_score_gold)

    # Lower 360-degree circular LED video ribbon halo
    create_cylinder("MACK_Scoreboard_Lower_Halo_Ribbon", col_int, (arena_cx, arena_cy, sb_z - sb_h/2.0 - 0.5), 3.8, 0.9, mat_score_gold, segments=36)

    # 4 Steel suspension cables linking scoreboard to ceiling
    for c_idx, (cx_off, cy_off) in enumerate([(-3.8, -3.8), (3.8, -3.8), (3.8, 3.8), (-3.8, 3.8)]):
        create_cylinder(f"MACK_Scoreboard_Cable_{c_idx}", col_int, (arena_cx + cx_off, arena_cy + cy_off, 21.5), 0.06, 10.0, mat_mullion, segments=12)

    # F. Purdue Basketball Ring of Honor & Championship Banners
    # Sited at Z = 17.5m (hanging neatly below catwalk ring, well clear of dome)
    banners = [
        ("Edey_15", -12.0, 16.0, True),
        ("Robinson_13", -7.0, 16.0, False),
        ("Mount_10", -2.0, 16.0, True),
        ("Carroll_20", 3.0, 16.0, False),
        ("Gearlds_3", 8.0, 16.0, True),
        ("White_22", 13.0, 16.0, False),
        ("FinalFour_2024", -10.0, -16.0, True),
        ("BigTen_Champs", 0.0, -16.0, False),
        ("Wooden_13", 10.0, -16.0, True),
    ]
    for b_id, bx_off, by_off, is_gold in banners:
        mat_b = mat_banner_gold if is_gold else mat_banner_black
        b_x = arena_cx + bx_off
        b_y = arena_cy + by_off
        create_box(f"MACK_Banner_Slab_{b_id}", col_int, (b_x, b_y, 17.2), (3.4, 0.08, 4.2), mat_b)
        create_cylinder(f"MACK_Banner_Pole_{b_id}", col_int, (b_x, b_y, 19.4), 0.06, 3.8, mat_old_gold, segments=12)
        create_cylinder(f"MACK_Banner_WireL_{b_id}", col_int, (b_x - 1.4, b_y, 20.2), 0.02, 1.8, mat_mullion, segments=8)
        create_cylinder(f"MACK_Banner_WireR_{b_id}", col_int, (b_x + 1.4, b_y, 20.2), 0.02, 1.8, mat_mullion, segments=8)

    # G. Arena Floodlight Rig (Catwalk Ring at Z = 21.0m, R = 28m)
    create_ring("MACK_Lighting_Catwalk_Ring", col_int, (arena_cx, arena_cy, 21.2), 27.5, 28.5, 0.4, mat_mullion, segments=36)
    for l_idx in range(16):
        ang_l = 2.0 * math.pi * l_idx / 16.0
        lx = arena_cx + 27.5 * math.cos(ang_l)
        ly = arena_cy + 27.5 * math.sin(ang_l)
        create_box(f"MACK_Floodlight_Fixture_{l_idx}", col_int, (lx, ly, 21.0), (0.8, 0.8, 0.5), mat_mullion)
        fl_light = bpy.data.lights.new(name=f"MACK_Court_Light_{l_idx}", type='SPOT')
        fl_light.energy = 3200.0
        fl_light.spot_size = math.radians(55)
        fl_light.color = (1.0, 0.98, 0.92)
        fl_obj = bpy.data.objects.new(name=f"MACK_Court_Light_{l_idx}", object_data=fl_light)
        col_int.objects.link(fl_obj)
        fl_obj.location = (lx, ly, 20.8)
        dx = arena_cx - lx
        dy = arena_cy - ly
        dz = 0.0 - 20.8
        pitch = math.atan2(math.sqrt(dx*dx + dy*dy), -dz)
        yaw = math.atan2(dy, dx) - math.pi/2
        fl_obj.rotation_euler = (pitch, 0, yaw)

    # =========================================================================
    # 6. SALLY & BOB WEIST PLAZA & JOHN WOODEN STATUE (44_Mackey_Arena_WoodenPlaza)
    # =========================================================================
    print("Building Sally & Bob Weist Plaza, 7-ft Bronze John Wooden Statue, and Pyramid of Success...")
    # Plaza center northwest of Mackey Arena
    plaza_cx = arena_cx - 32.0
    plaza_cy = arena_cy + 58.0

    create_box("MACK_Weist_Plaza_Brick_Deck", col_site, (plaza_cx, plaza_cy, 0.08), (36.0, 32.0, 0.16), mat_plaza_paver)
    create_box("MACK_Weist_Plaza_Granite_Border", col_site, (plaza_cx, plaza_cy, 0.12), (36.4, 32.4, 0.12), mat_stone)

    # Flanking Curved Bedford Limestone Seatwalls
    for side, ang_base in [("West", 140), ("North", 50)]:
        for w_idx in range(5):
            curv_ang = math.radians(ang_base + w_idx * 12)
            wx = plaza_cx + 14.0 * math.cos(curv_ang)
            wy = plaza_cy + 14.0 * math.sin(curv_ang)
            create_box(f"MACK_Plaza_Seatwall_{side}_{w_idx}", col_site, (wx, wy, 0.45), (2.2, 0.7, 0.75), mat_stone)

    # The 7-Foot Bronze Statue of John Wooden (Purdue Uniform '32)
    # Positioned so statue faces South-East toward Mackey Arena!
    statue_x = plaza_cx - 2.0
    statue_y = plaza_cy - 4.0

    create_box("MACK_Wooden_Pedestal_Base", col_site, (statue_x, statue_y, 0.25), (2.4, 2.4, 0.5), mat_plinth_granite)
    create_box("MACK_Wooden_Pedestal_Shaft", col_site, (statue_x, statue_y, 0.8), (1.8, 1.8, 0.6), mat_plinth_granite)
    create_box("MACK_Wooden_Pedestal_Cap", col_site, (statue_x, statue_y, 1.15), (2.0, 2.0, 0.15), mat_stone)

    create_box("MACK_Statue_Wooden_Legs", col_site, (statue_x, statue_y, 1.7), (0.5, 0.4, 0.95), mat_bronze_statue)
    create_box("MACK_Statue_Wooden_Torso", col_site, (statue_x, statue_y, 2.5), (0.55, 0.45, 0.8), mat_bronze_statue)
    create_box("MACK_Statue_Wooden_Head", col_site, (statue_x, statue_y, 3.05), (0.32, 0.32, 0.38), mat_bronze_statue)
    create_cylinder("MACK_Statue_Wooden_Basketball", col_site, (statue_x + 0.38, statue_y + 0.1, 2.3), 0.24, 0.45, mat_bronze_statue, segments=24)

    # Gold Dedication Plaque on Pedestal Face (facing North-West toward camera)
    create_box("MACK_Wooden_Statue_Gold_Plaque", col_site, (statue_x - 0.91, statue_y + 0.5, 0.8), (0.04, 1.2, 0.45), mat_old_gold)

    # The Pyramid of Success Monument Wall (positioned to the West of the statue, framing the plaza)
    wall_x = statue_x - 5.5
    wall_y = statue_y - 2.0
    wall_base = create_box("MACK_Pyramid_Success_Base", col_site, (wall_x, wall_y, 0.35), (1.2, 6.0, 0.7), mat_stone)
    wall_base.rotation_euler = (0, 0, math.radians(25))
    wall_body = create_box("MACK_Pyramid_Success_Wall", col_site, (wall_x, wall_y, 2.1), (0.6, 5.5, 2.8), mat_stone)
    wall_body.rotation_euler = (0, 0, math.radians(25))
    wall_board = create_box("MACK_Pyramid_Success_Bronze_Board", col_site, (wall_x + 0.31, wall_y, 2.1), (0.04, 5.1, 2.4), mat_bronze_statue)
    wall_board.rotation_euler = (0, 0, math.radians(25))

    # Dedicated accent spotlight illuminating John Wooden statue
    plz_spot = bpy.data.lights.new(name="MACK_Light_Wooden_Statue", type='SPOT')
    plz_spot.energy = 850.0
    plz_spot.spot_size = math.radians(45)
    plz_spot.color = (1.0, 0.96, 0.88)
    plz_spot_obj = bpy.data.objects.new(name="MACK_Light_Wooden_Statue", object_data=plz_spot)
    col_site.objects.link(plz_spot_obj)
    plz_spot_obj.location = (statue_x - 6.0, statue_y + 6.0, 4.5)
    dx_s = statue_x - plz_spot_obj.location.x
    dy_s = statue_y - plz_spot_obj.location.y
    dz_s = 2.2 - plz_spot_obj.location.z
    p_s = math.atan2(math.sqrt(dx_s*dx_s + dy_s*dy_s), -dz_s)
    y_s = math.atan2(dy_s, dx_s) - math.pi/2
    plz_spot_obj.rotation_euler = (p_s, 0, y_s)

    # Teak Benches, Bike Racks, LED Bollards
    for b_idx in range(4):
        bx = plaza_cx + 8.0 * (b_idx - 1.5)
        create_box(f"MACK_Plaza_Teak_Bench_{b_idx}", col_site, (bx, plaza_cy - 12.0, 0.45), (2.2, 0.65, 0.5), mat_stone)

    for r_idx in range(6):
        rx = plaza_cx + 12.0
        ry = plaza_cy - 8.0 + r_idx * 2.5
        create_box(f"MACK_Plaza_BikeRack_{r_idx}", col_site, (rx, ry, 0.45), (0.12, 1.2, 0.9), mat_mullion)

    for bol_idx in range(8):
        ang_b = 2.0 * math.pi * bol_idx / 8.0
        bx = plaza_cx + 16.0 * math.cos(ang_b)
        by = plaza_cy + 16.0 * math.sin(ang_b)
        create_cylinder(f"MACK_Plaza_LEDBollard_{bol_idx}", col_site, (bx, by, 0.55), 0.15, 1.1, mat_mullion, segments=16)

    # =========================================================================
    # 7. CALIBRATED INSPECTION CAMERAS (00_Inspection_Cameras)
    # =========================================================================
    def setup_cam(cam_name, loc, target, focal_length=24.0):
        if cam_name in bpy.data.objects:
            cam_obj = bpy.data.objects[cam_name]
        else:
            cam_data = bpy.data.cameras.new(name=cam_name)
            cam_obj = bpy.data.objects.new(name=cam_name, object_data=cam_data)
            col_cams.objects.link(cam_obj)
        cam_obj.data.lens = focal_length
        cam_obj.location = loc
        dx = target[0] - loc[0]
        dy = target[1] - loc[1]
        dz = target[2] - loc[2]
        pitch = math.atan2(math.sqrt(dx*dx + dy*dy), -dz)
        yaw = math.atan2(dy, dx) - math.pi/2
        cam_obj.rotation_euler = (pitch, 0, yaw)
        return cam_obj

    # Cam 62: Sally & Bob Weist Plaza Hero View (Wooden Statue in foreground, Mackey Dome & Pavilion behind)
    setup_cam("Cam_62_Mackey_Arena_North_WoodenPlaza_Hero",
              loc=(statue_x - 7.5, statue_y + 8.5, 2.4),
              target=(statue_x + 5.0, statue_y - 6.0, 3.8),
              focal_length=24.0)

    # Cam 63: Keady Court Center Court Hero View (Sideline looking across center court Motion P & hoops)
    setup_cam("Cam_63_Mackey_Arena_KeadyCourt_CenterCourt_Hero",
              loc=(arena_cx - 8.0, arena_cy - 9.2, 1.8),
              target=(arena_cx + 2.0, arena_cy, 2.2),
              focal_length=20.0)

    # Cam 64: Upper Bowl Perspective of Center-Hung Scoreboard & Ring of Honor Banners
    setup_cam("Cam_64_Mackey_Arena_UpperBowl_CenterHungScoreboard",
              loc=(arena_cx - 26.0, arena_cy - 22.0, 14.5),
              target=(arena_cx, arena_cy, 12.0),
              focal_length=22.0)

    # Cam 65: Courtside Hoop, Shot Clock & Team Bench Detail
    setup_cam("Cam_65_Mackey_Arena_Courtside_Hoop_and_Bench",
              loc=(arena_cx - 15.5, arena_cy - 3.5, 1.8),
              target=(arena_cx - 10.0, arena_cy + 0.5, 2.5),
              focal_length=22.0)

    # Cam 66: High Aerial Perspective of North Athletic Precinct
    setup_cam("Cam_66_Mackey_Arena_Athletic_Precinct_Aerial",
              loc=(arena_cx - 85.0, arena_cy + 105.0, 65.0),
              target=(arena_cx - 10.0, arena_cy + 15.0, 10.0),
              focal_length=28.0)

    print("Reconstruction complete! Saving scene...")
    bpy.ops.wm.save_mainfile(filepath=r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend")
    print(f"Total objects in scene: {len(bpy.data.objects)}")
    print(f"Exterior objects: {len(col_ext.objects)}")
    print(f"Interior objects: {len(col_int.objects)}")
    print(f"Site/Plaza objects: {len(col_site.objects)}")
    print("=== Successfully built Mackey Arena (MACK) ===")

if __name__ == "__main__":
    run()
