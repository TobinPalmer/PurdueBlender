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

def build_beering_hall():
    print("=== MODELING PURDUE BEERING HALL (BRNG) - ATTEMPTS 1, 2 & 3 ===")
    
    col_ext = clean_or_create_col("14_Beering_Hall_Exterior")
    col_int = clean_or_create_col("15_Beering_Hall_Interiors")
    
    # Hide low-poly placeholder in massing collection
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if massing_col:
        for obj in massing_col.objects:
            if "Beering" in obj.name or "BRNG" in obj.name:
                obj.hide_viewport = True
                obj.hide_render = True
                print(f"Hidden low-poly massing placeholder: {obj.name}")
                
    # -------------------------------------------------------------
    # Materials Setup
    # -------------------------------------------------------------
    mat_brick = get_or_make_mat("Beering_Purdue_Red_Brick", (0.54, 0.22, 0.16, 1.0), roughness=0.82)
    mat_stone = get_or_make_mat("Beering_Bedford_Limestone", (0.84, 0.82, 0.77, 1.0), roughness=0.62)
    mat_glass = get_or_make_mat("Beering_Solar_Ribbon_Glass", (0.12, 0.20, 0.25, 1.0), roughness=0.04, transmission=0.88)
    mat_metal = get_or_make_mat("Beering_Architectural_Bronze_Metal", (0.24, 0.20, 0.16, 1.0), roughness=0.42, metallic=0.7)
    mat_copper_dome = get_or_make_mat("Beering_Verdigris_Copper_Dome", (0.28, 0.52, 0.44, 1.0), roughness=0.55, metallic=0.3)
    mat_roof = get_or_make_mat("Beering_Roof_Membrane", (0.30, 0.30, 0.31, 1.0), roughness=0.85)
    
    # Interior Materials
    mat_terrazzo = get_or_make_mat("Beering_Lobby_Terrazzo", (0.86, 0.84, 0.80, 1.0), roughness=0.20)
    mat_oak = get_or_make_mat("Beering_Honey_Oak_Woodwork", (0.62, 0.44, 0.24, 1.0), roughness=0.45)
    mat_dark_oak = get_or_make_mat("Beering_Executive_Dark_Oak", (0.32, 0.20, 0.12, 1.0), roughness=0.40)
    mat_carpet_blue = get_or_make_mat("Beering_Vision21_Carpet_Navy", (0.12, 0.16, 0.26, 1.0), roughness=0.92)
    mat_leather_chair = get_or_make_mat("Beering_Executive_Leather_Black", (0.08, 0.08, 0.09, 1.0), roughness=0.35)
    mat_screen = get_or_make_mat("Beering_AV_Display_Emissive", (0.05, 0.05, 0.05, 1.0), roughness=0.2, emission=(0.90, 0.95, 1.0, 1.0), emission_strength=2.5)
    mat_chalkboard = get_or_make_mat("Beering_Classroom_Chalkboard_Green", (0.12, 0.25, 0.18, 1.0), roughness=0.65)
    mat_wall_ivory = get_or_make_mat("Beering_Interior_Wall_Ivory", (0.91, 0.90, 0.87, 1.0), roughness=0.80)
    mat_pavers = get_or_make_mat("Beering_Plaza_Brick_Pavers", (0.48, 0.22, 0.18, 1.0), roughness=0.86)
    mat_gold = get_or_make_mat("Beering_Purdue_Gold_Medallion", (0.88, 0.70, 0.18, 1.0), roughness=0.35, metallic=0.7)

    # -------------------------------------------------------------
    # PASS 1 & 2: EXTERIOR ARCHITECTURE & WINGS
    # -------------------------------------------------------------
    # Footprint bounds: X in [-238.0, -162.4], Y in [-240.4, -165.0]
    
    # Wing A: 3-Story Classroom Wing (West along University St)
    # Center: X = -223.0, Y = -202.7, Size = (30.0m x 75.4m x 12.0m)
    cw_x, cw_y = -223.0, -202.7
    cw_w, cw_l, cw_h = 30.0, 75.4, 12.0
    
    print("Building Wing A: 3-Story Classroom Wing...")
    create_box(
        "BRNG_Classroom_Wing_Masonry",
        loc=(cw_x, cw_y, cw_h * 0.5),
        size=(cw_w, cw_l, cw_h),
        mat=mat_brick,
        col=col_ext
    )
    # Limestone Water Table base
    create_box(
        "BRNG_Classroom_Wing_Limestone_Base",
        loc=(cw_x, cw_y, 0.9),
        size=(cw_w + 0.4, cw_l + 0.4, 1.8),
        mat=mat_stone,
        col=col_ext
    )
    # Belt courses on Classroom wing
    for fl_z in [4.0, 8.0, 12.0]:
        create_box(
            f"BRNG_Classroom_BeltCourse_{int(fl_z)}m",
            loc=(cw_x, cw_y, fl_z),
            size=(cw_w + 0.3, cw_l + 0.3, 0.35),
            mat=mat_stone,
            col=col_ext
        )
        
    # Classroom wing window ribbons along University Street (West facade: X = cw_x - cw_w*0.5)
    for y_step in range(int(cw_y - cw_l*0.5 + 5), int(cw_y + cw_l*0.5 - 5), 5):
        for fl_z in [2.5, 6.5, 10.5]:
            # Recessed ribbon window
            create_box(
                f"BRNG_Classroom_Window_{y_step}_{int(fl_z*10)}",
                loc=(cw_x - cw_w*0.5 - 0.05, y_step + 1.8, fl_z),
                size=(0.2, 3.2, 1.8),
                mat=mat_glass,
                col=col_ext
            )
            # Limestone sill & lintel
            create_box(
                f"BRNG_Classroom_Sill_{y_step}_{int(fl_z*10)}",
                loc=(cw_x - cw_w*0.5 + 0.05, y_step + 1.8, fl_z - 0.95),
                size=(0.35, 3.4, 0.15),
                mat=mat_stone,
                col=col_ext
            )
            
    # Monumental West Entrance Portal on University Street
    create_box(
        "BRNG_West_Entrance_Limestone_Portico",
        loc=(cw_x - cw_w*0.5 - 1.2, cw_y, 3.2),
        size=(2.4, 12.0, 6.4),
        mat=mat_stone,
        col=col_ext
    )
    create_box(
        "BRNG_West_Entrance_Glazed_Doors",
        loc=(cw_x - cw_w*0.5 - 0.2, cw_y, 2.0),
        size=(0.4, 9.0, 4.0),
        mat=mat_glass,
        col=col_ext
    )
    create_box(
        "BRNG_West_Entrance_Limestone_Pediment",
        loc=(cw_x - cw_w*0.5 - 1.2, cw_y, 6.8),
        size=(2.6, 12.6, 0.9),
        mat=mat_stone,
        col=col_ext
    )

    # Wing B: 7-Story Office Tower (East stepped back toward Memorial Mall)
    # Extends from X = -208.0 to -162.4 (width = 45.6m), Y = -165.0 to -203.0 (depth = 38.0m)
    tw_x, tw_y = -185.2, -184.0
    tw_w, tw_l = 45.6, 38.0
    tw_h = 26.6
    
    print("Building Wing B: 7-Story Office Tower...")
    create_box(
        "BRNG_Office_Tower_Masonry",
        loc=(tw_x, tw_y, tw_h * 0.5),
        size=(tw_w, tw_l, tw_h),
        mat=mat_brick,
        col=col_ext
    )
    # Tower Limestone base
    create_box(
        "BRNG_Office_Tower_Limestone_Base",
        loc=(tw_x, tw_y, 0.9),
        size=(tw_w + 0.4, tw_l + 0.4, 1.8),
        mat=mat_stone,
        col=col_ext
    )
    # Tower belt courses (Levels 2 through 7)
    for fl_z in [4.0, 7.8, 11.6, 15.4, 19.2, 23.0, 26.6]:
        create_box(
            f"BRNG_Tower_BeltCourse_{int(fl_z*10)}",
            loc=(tw_x, tw_y, fl_z),
            size=(tw_w + 0.35, tw_l + 0.35, 0.4),
            mat=mat_stone,
            col=col_ext
        )
        
    # Stepped setback on upper levels (Floors 6 & 7) to respect University Hall tradition
    create_box(
        "BRNG_Tower_Floor7_Setback_Balcony",
        loc=(tw_x + tw_w*0.5 - 3.0, tw_y, 23.2),
        size=(6.0, tw_l - 4.0, 0.4),
        mat=mat_stone,
        col=col_ext
    )
    
    # Tower Windows (East & North facades)
    for x_step in range(int(tw_x - tw_w*0.5 + 4), int(tw_x + tw_w*0.5 - 4), 4):
        for fl_z in [5.8, 9.6, 13.4, 17.2, 21.0, 24.8]:
            # North facade windows
            create_box(
                f"BRNG_Tower_Window_N_{x_step}_{int(fl_z*10)}",
                loc=(x_step + 1.5, tw_y + tw_l*0.5 + 0.05, fl_z),
                size=(2.5, 0.2, 1.9),
                mat=mat_glass,
                col=col_ext
            )
            # Spandrel
            create_box(
                f"BRNG_Tower_Spandrel_N_{x_step}_{int(fl_z*10)}",
                loc=(x_step + 1.5, tw_y + tw_l*0.5 + 0.1, fl_z - 1.1),
                size=(2.5, 0.15, 0.5),
                mat=mat_metal,
                col=col_ext
            )

    # Wing C: 7-Story Circular Rotunda Drum & "Jedi Council Room"
    # Center: X = -195.0, Y = -225.0, Radius = 7.0m (Diameter 14.0m), Height = 27.5m
    rc_x, rc_y = -195.0, -225.0
    rc_r = 7.0
    rc_h = 27.5
    
    print("Building Wing C: 7-Story Circular Rotunda & Vision 21 Drum...")
    # Main masonry drum up to 6th floor (z = 0 to 23.0m)
    create_cylinder(
        "BRNG_Rotunda_Masonry_Drum_Core",
        loc=(rc_x, rc_y, 11.5),
        radius=rc_r,
        depth=23.0,
        mat=mat_brick,
        col=col_ext,
        verts=36
    )
    # Limestone base cylinder
    create_cylinder(
        "BRNG_Rotunda_Limestone_Base",
        loc=(rc_x, rc_y, 0.9),
        radius=rc_r + 0.25,
        depth=1.8,
        mat=mat_stone,
        col=col_ext,
        verts=36
    )
    # Limestone belt rings on rotunda drum
    for fl_z in [4.0, 7.8, 11.6, 15.4, 19.2, 23.0]:
        create_cylinder(
            f"BRNG_Rotunda_BeltRing_{int(fl_z*10)}",
            loc=(rc_x, rc_y, fl_z),
            radius=rc_r + 0.2,
            depth=0.4,
            mat=mat_stone,
            col=col_ext,
            verts=36
        )
        
    # Vertical Limestone Pilasters dividing the circular rotunda facets
    for ang_deg in range(0, 360, 30):
        rad = math.radians(ang_deg)
        px = rc_x + (rc_r + 0.15) * math.cos(rad)
        py = rc_y + (rc_r + 0.15) * math.sin(rad)
        create_box(
            f"BRNG_Rotunda_Pilaster_{ang_deg}",
            loc=(px, py, 11.5),
            size=(0.5, 0.5, 23.0),
            mat=mat_stone,
            col=col_ext
        )
        
    # 7th Floor "Jedi Council Room" (Vision 21) Panoramic Ribbon Glass Ring
    # z = 23.0 to 26.8m (height = 3.8m)
    create_cylinder(
        "BRNG_Vision21_JediCouncil_Panoramic_Glass_Ring",
        loc=(rc_x, rc_y, 24.9),
        radius=rc_r + 0.05,
        depth=3.8,
        mat=mat_glass,
        col=col_ext,
        verts=36
    )
    # Upper limestone cornice band over Vision 21
    create_cylinder(
        "BRNG_Vision21_Cornice_Band",
        loc=(rc_x, rc_y, 26.9),
        radius=rc_r + 0.4,
        depth=0.5,
        mat=mat_stone,
        col=col_ext,
        verts=36
    )
    # Oxidized Copper Domed Roof Cap over Vision 21
    # Modeled as stepped conic copper dome
    create_cylinder(
        "BRNG_Vision21_Copper_Dome_Tier1",
        loc=(rc_x, rc_y, 27.5),
        radius=rc_r + 0.1,
        depth=0.8,
        mat=mat_copper_dome,
        col=col_ext,
        verts=36
    )
    create_cylinder(
        "BRNG_Vision21_Copper_Dome_Tier2",
        loc=(rc_x, rc_y, 28.2),
        radius=rc_r * 0.65,
        depth=0.7,
        mat=mat_copper_dome,
        col=col_ext,
        verts=28
    )
    # Bronze Crown Finial on Dome Peak
    create_cylinder(
        "BRNG_Vision21_Dome_Finial",
        loc=(rc_x, rc_y, 29.1),
        radius=0.25,
        depth=1.2,
        mat=mat_metal,
        col=col_ext,
        verts=16
    )

    # South Courtyard Plaza & Paved Arrival Terrace
    # Sits between the classroom wing and office wing: centered around X = -180 to -215, Y = -215 to -245
    print("Building South Courtyard Plaza & Seatwall Terraces...")
    create_box(
        "BRNG_Courtyard_Brick_Plaza_Slab",
        loc=(-195.0, -225.0, 0.06),
        size=(55.0, 45.0, 0.12),
        mat=mat_pavers,
        col=col_ext
    )
    # Concentric curved limestone seatwalls enclosing the rotunda garden
    for r_seat in [11.0, 16.0]:
        for ang_deg in range(120, 330, 25):
            rad = math.radians(ang_deg)
            sx = rc_x + r_seat * math.cos(rad)
            sy = rc_y + r_seat * math.sin(rad)
            create_box(
                f"BRNG_Courtyard_Seatwall_{int(r_seat)}_{ang_deg}",
                loc=(sx, sy, 0.45),
                size=(3.2, 0.7, 0.7),
                mat=mat_stone,
                col=col_ext
            )
            create_box(
                f"BRNG_Courtyard_Seatwall_Cap_{int(r_seat)}_{ang_deg}",
                loc=(sx, sy, 0.85),
                size=(3.4, 0.85, 0.12),
                mat=mat_stone,
                col=col_ext
            )

    # -------------------------------------------------------------
    # PASS 3: PHOTOREALISTIC INTERIOR ARCHITECTURE
    # -------------------------------------------------------------
    print("Building Photorealistic Interiors: Lobby, BRNG 2280 Lecture Hall & Jedi Council Room...")
    
    # 1. Ground Floor Welcome Lobby & Student Advising Hub
    # Located at center of classroom wing: X = cw_x, Y = cw_y, z = 0.1m
    create_box(
        "BRNG_Lobby_Terrazzo_Floor_Slab",
        loc=(cw_x, cw_y, 0.1),
        size=(cw_w - 0.5, 30.0, 0.15),
        mat=mat_terrazzo,
        col=col_int
    )
    # Curved Oak Student Advising & Information Counter
    create_box(
        "BRNG_Lobby_Advising_Desk_Oak_Base",
        loc=(cw_x + 4.0, cw_y, 0.65),
        size=(2.8, 8.5, 1.1),
        mat=mat_oak,
        col=col_int
    )
    create_box(
        "BRNG_Lobby_Advising_Desk_Quartz_Counter",
        loc=(cw_x + 4.0, cw_y, 1.18),
        size=(3.1, 8.8, 0.1),
        mat=mat_stone,
        col=col_int
    )
    # Wall-mounted Building Directory & Digital Announcement Displays
    for dy in [-6.0, 6.0]:
        create_box(
            f"BRNG_Lobby_Directory_Display_{int(dy)}",
            loc=(cw_x - cw_w*0.5 + 0.25, cw_y + dy, 2.2),
            size=(0.08, 1.8, 1.1),
            mat=mat_screen,
            col=col_int
        )
    # Lounge seating pods in lobby
    for ly in [-9.0, 9.0]:
        create_box(
            f"BRNG_Lobby_Modular_Sofa_{int(ly)}",
            loc=(cw_x + 8.0, cw_y + ly, 0.45),
            size=(2.4, 6.0, 0.8),
            mat=mat_carpet_blue,
            col=col_int
        )

    # 2. BRNG 2280 Major Tiered Lecture Hall (Floor 2 - 130 Seats)
    # Located in classroom wing north sector: X = cw_x, Y = cw_y + 20.0, z = 4.0m to 7.5m
    lh_cx, lh_cy = cw_x, cw_y + 20.0
    lh_w, lh_l = 24.0, 20.0
    
    # Tiered Riser Stepped Floor (5 ascending terraces from front to back)
    for step_i in range(5):
        tz = 4.0 + step_i * 0.45
        ty = (lh_cy - lh_l*0.5 + 4.0) + step_i * 2.8
        create_box(
            f"BRNG2280_Seating_Tier_Platform_{step_i}",
            loc=(lh_cx, ty, tz - 0.22),
            size=(lh_w - 2.0, 2.7, 0.45),
            mat=mat_carpet_blue,
            col=col_int
        )
        # Continuous student lecture table
        create_box(
            f"BRNG2280_Student_Lecture_Table_{step_i}",
            loc=(lh_cx, ty + 0.6, tz + 0.4),
            size=(lh_w - 4.0, 0.6, 0.75),
            mat=mat_oak,
            col=col_int
        )
        # Ergonomic student lecture task chairs
        for chair_x in range(int(lh_cx - lh_w*0.5 + 3), int(lh_cx + lh_w*0.5 - 2), 2):
            create_box(
                f"BRNG2280_Chair_{step_i}_{chair_x}",
                loc=(chair_x, ty - 0.3, tz + 0.45),
                size=(0.55, 0.55, 0.85),
                mat=mat_metal,
                col=col_int
            )
            
    # Front Lecture Dais & Oak Stage
    create_box(
        "BRNG2280_Front_Stage_Dais",
        loc=(lh_cx, lh_cy - lh_l*0.5 + 1.8, 4.1),
        size=(lh_w - 2.0, 3.2, 0.2),
        mat=mat_oak,
        col=col_int
    )
    # Multimedia Teaching Console / Smart Podium
    create_box(
        "BRNG2280_Instructor_Smart_Podium",
        loc=(lh_cx - 4.5, lh_cy - lh_l*0.5 + 2.0, 4.75),
        size=(1.2, 0.85, 1.1),
        mat=mat_dark_oak,
        col=col_int
    )
    # Dual Overhead Projection Screens (Emissive)
    for ps_x in [-5.0, 5.0]:
        create_box(
            f"BRNG2280_Projection_Screen_{int(ps_x)}",
            loc=(lh_cx + ps_x, lh_cy - lh_l*0.5 + 0.1, 6.2),
            size=(4.8, 0.08, 2.6),
            mat=mat_screen,
            col=col_int
        )
    # Triple sliding chalkboards
    create_box(
        "BRNG2280_Sliding_Chalkboards",
        loc=(lh_cx, lh_cy - lh_l*0.5 + 0.05, 5.2),
        size=(16.0, 0.05, 1.6),
        mat=mat_chalkboard,
        col=col_int
    )

    # 3. Vision 21 Conference Room ("Jedi Council Chamber") - Floor 7
    # Located inside the circular rotunda at z = 23.5m to 26.8m, center at (rc_x, rc_y)
    v21_z = 23.5
    print("Building Vision 21 'Jedi Council Chamber' on Floor 7...")
    
    # Circular navy carpet floor with central medallion
    create_cylinder(
        "BRNG_Vision21_Floor_Carpet",
        loc=(rc_x, rc_y, v21_z + 0.05),
        radius=rc_r - 0.3,
        depth=0.1,
        mat=mat_carpet_blue,
        col=col_int,
        verts=36
    )
    # Purdue Bronze/Gold Medallion in Room Center
    create_cylinder(
        "BRNG_Vision21_Central_Gold_Medallion",
        loc=(rc_x, rc_y, v21_z + 0.11),
        radius=1.8,
        depth=0.02,
        mat=mat_gold,
        col=col_int,
        verts=32
    )
    
    # Custom 12-Seat Circular Boardroom Table (Diameter = 4.4m, Radius = 2.2m)
    # Modeled as concentric hollow ring or faceted polygon
    for t_seg in range(12):
        t_ang = math.radians(t_seg * 30.0)
        tx = rc_x + 2.2 * math.cos(t_ang)
        ty = rc_y + 2.2 * math.sin(t_ang)
        create_box(
            f"BRNG_Vision21_Table_Segment_{t_seg}",
            loc=(tx, ty, v21_z + 0.75),
            size=(1.2, 1.1, 0.08),
            mat=mat_dark_oak,
            col=col_int
        )
        create_box(
            f"BRNG_Vision21_Table_Leg_{t_seg}",
            loc=(tx, ty, v21_z + 0.36),
            size=(0.15, 0.15, 0.72),
            mat=mat_metal,
            col=col_int
        )
        
    # 12 Executive High-Back Leather Swivel Chairs (The "Jedi Council" Seating)
    for c_i in range(12):
        c_ang = math.radians(c_i * 30.0)
        cx_pos = rc_x + 3.2 * math.cos(c_ang)
        cy_pos = rc_y + 3.2 * math.sin(c_ang)
        # Chair seat & back
        create_box(
            f"BRNG_Vision21_Jedi_Chair_Seat_{c_i}",
            loc=(cx_pos, cy_pos, v21_z + 0.5),
            size=(0.7, 0.7, 0.12),
            mat=mat_leather_chair,
            col=col_int
        )
        create_box(
            f"BRNG_Vision21_Jedi_Chair_Back_{c_i}",
            loc=(cx_pos + 0.25 * math.cos(c_ang), cy_pos + 0.25 * math.sin(c_ang), v21_z + 1.0),
            size=(0.65, 0.18, 0.95),
            mat=mat_leather_chair,
            col=col_int
        )
        create_box(
            f"BRNG_Vision21_Jedi_Chair_Pedestal_{c_i}",
            loc=(cx_pos, cy_pos, v21_z + 0.25),
            size=(0.12, 0.12, 0.48),
            mat=mat_metal,
            col=col_int
        )

    # -------------------------------------------------------------
    # PASS 4: SETUP CALIBRATED INSPECTION CAMERAS
    # -------------------------------------------------------------
    setup_beering_hall_cameras(cw_x, cw_y, tw_x, tw_y, rc_x, rc_y, v21_z, lh_cx, lh_cy)
    print("=== PURDUE BEERING HALL MODELING COMPLETED SUCCESSFULLY ===")

def setup_beering_hall_cameras(cw_x, cw_y, tw_x, tw_y, rc_x, rc_y, v21_z, lh_cx, lh_cy):
    col = clean_or_create_col("05_Cameras_and_Views")
    
    cameras = [
        # 1. Street View facing Beering Hall from University Street (looking East)
        {
            "name": "Cam_14_Beering_Hall_UniversitySt_StreetView",
            "loc": (cw_x - 45.0, cw_y, 4.5),
            "rot": (math.radians(82.0), 0.0, math.radians(-90.0)),
            "lens": 24.0
        },
        # 2. Courtyard Perspective showing the 7-story Rotunda Drum & Stepped Office Tower
        {
            "name": "Cam_15_Beering_Hall_Rotunda_Courtyard",
            "loc": (rc_x + 28.0, rc_y - 28.0, 6.0),
            "rot": (math.radians(78.0), 0.0, math.radians(45.0)),
            "lens": 22.0
        },
        # 3. Inside the 7th Floor "Jedi Council Room" (Vision 21 Conference Room)
        {
            "name": "Cam_16_Beering_Hall_JediCouncil_Vision21_Interior",
            "loc": (rc_x - 3.8, rc_y - 2.8, v21_z + 1.6),
            "rot": (math.radians(76.0), 0.0, math.radians(-42.0)),
            "lens": 18.0 # Wide angle for circular chamber
        },
        # 4. Inside Tiered Lecture Hall BRNG 2280
        {
            "name": "Cam_17_Beering_Hall_Lecture_BRNG2280_Interior",
            "loc": (lh_cx + 7.5, lh_cy + 8.5, 6.8),
            "rot": (math.radians(72.0), 0.0, math.radians(145.0)),
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
            
    # Set active camera to Cam_14
    bpy.context.scene.camera = bpy.data.objects["Cam_14_Beering_Hall_UniversitySt_StreetView"]
    print("Beering Hall inspection cameras calibrated.")

if __name__ == "__main__":
    build_beering_hall()
