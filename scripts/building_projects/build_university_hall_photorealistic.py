import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

def build_university_hall():
    print("==================================================================")
    print("=== BUILDING UNIVERSITY HALL (UNIV - 1877) & JOHN PURDUE GRAVE ==")
    print("==================================================================")

    # 1. Purge low-poly massing placeholder
    old_block = bpy.data.objects.get("University Hall (UNIV)")
    if old_block:
        bpy.data.objects.remove(old_block, do_unlink=True)
        print("Removed low-poly University Hall placeholder block.")

    # Purge any existing objects in target collections if re-running
    target_cols = [
        "36_University_Hall_Exterior",
        "37_University_Hall_Interiors",
        "38_University_Hall_Grave_and_MemorialMall"
    ]
    for cname in target_cols:
        c = bpy.data.collections.get(cname)
        if c:
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(c)

    # 2. Setup Collections
    def get_or_create_col(name, parent=None):
        c = bpy.data.collections.get(name)
        if not c:
            c = bpy.data.collections.new(name)
            if parent:
                parent.children.link(c)
            else:
                bpy.context.scene.collection.children.link(c)
        return c

    col_ext = get_or_create_col("36_University_Hall_Exterior")
    col_int = get_or_create_col("37_University_Hall_Interiors")
    col_site = get_or_create_col("38_University_Hall_Grave_and_MemorialMall")

    # 3. Materials Setup
    def get_or_create_mat(name, color, roughness=0.4, metallic=0.0, emission=None, emission_strength=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
            if emission:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            else:
                bsdf.inputs["Emission Strength"].default_value = 0.0
        return mat

    mat_brick = get_or_create_mat("Univ_Weathered_Red_Brick", (0.38, 0.14, 0.09, 1.0), roughness=0.75)
    mat_stone = get_or_create_mat("Univ_Bedford_Limestone", (0.82, 0.78, 0.70, 1.0), roughness=0.52)
    mat_slate = get_or_create_mat("Univ_Slate_Roof", (0.22, 0.23, 0.25, 1.0), roughness=0.65)
    mat_copper = get_or_create_mat("Univ_Verdigris_Copper", (0.28, 0.52, 0.44, 1.0), roughness=0.45)
    mat_walnut = get_or_create_mat("Univ_Dark_Walnut", (0.16, 0.10, 0.06, 1.0), roughness=0.38)
    mat_mahogany = get_or_create_mat("Univ_Antique_Mahogany", (0.22, 0.08, 0.05, 1.0), roughness=0.32)
    mat_bronze = get_or_create_mat("Univ_Bronze", (0.38, 0.28, 0.14, 1.0), roughness=0.35, metallic=0.88)
    mat_gold = get_or_create_mat("Univ_Gold_Accent", (0.85, 0.70, 0.24, 1.0), roughness=0.25, metallic=0.90)
    mat_granite = get_or_create_mat("Univ_Barre_Granite", (0.18, 0.18, 0.20, 1.0), roughness=0.15)
    mat_parquet = get_or_create_mat("Univ_Parquet_Wood", (0.42, 0.28, 0.15, 1.0), roughness=0.30)
    mat_bankers_lamp = get_or_create_mat("Univ_Bankers_Lamp_Green", (0.05, 0.35, 0.12, 1.0), roughness=0.12)
    mat_lamp_glow = get_or_create_mat("Univ_Bankers_Lamp_Glow", (1.0, 0.90, 0.70, 1.0), emission=(1.0, 0.90, 0.70, 1.0), emission_strength=5.0)
    mat_leather = get_or_create_mat("Univ_Burgundy_Leather", (0.28, 0.04, 0.06, 1.0), roughness=0.45)
    mat_glass = get_or_create_mat("Univ_Window_Glass", (0.18, 0.22, 0.24, 1.0), roughness=0.08)
    mat_chalkboard = get_or_create_mat("Univ_Chalkboard_Slate", (0.12, 0.14, 0.13, 1.0), roughness=0.60)
    mat_plaster = get_or_create_mat("Univ_Interior_Plaster", (0.88, 0.86, 0.82, 1.0), roughness=0.80)
    mat_paving = get_or_create_mat("Univ_Walkway_Brick", (0.44, 0.18, 0.12, 1.0), roughness=0.65)
    mat_hedge = get_or_create_mat("Univ_Garden_Boxwood", (0.12, 0.28, 0.10, 1.0), roughness=0.70)

    # Helper mesh builders
    def add_box(name, col, loc, dim, mat):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= dim[0]
            v.co.y *= dim[1]
            v.co.z *= dim[2]
        bm.to_mesh(mesh)
        bm.free()
        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        return obj

    def add_cyl(name, col, loc, r, h, mat, segs=16):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r, depth=h)
        bm.to_mesh(mesh)
        bm.free()
        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        return obj

    # -------------------------------------------------------------
    # 4. EXTERIOR ARCHITECTURE & HOLLOW ENVELOPE (1877 VICTORIAN)
    # Footprint: X in [-137.57, -115.66] (width = 21.91m, center X = -126.61m)
    #            Y in [-258.15, -214.91] (length = 43.24m, center Y = -236.53m)
    # -------------------------------------------------------------
    print("Building exterior architecture & hollow envelope...")

    cx = -126.61
    cy = -236.53
    width_x = 21.92
    length_y = 43.24
    eave_z = 12.6

    # A. Continuous Indiana Bedford Limestone Water Table Base (Z = 0 to 1.2m)
    add_box("UNIV_WaterTable_East", col_ext, (-115.66 + 0.3, cy, 0.6), (0.6, length_y + 0.6, 1.2), mat_stone)
    add_box("UNIV_WaterTable_West", col_ext, (-137.57 - 0.3, cy, 0.6), (0.6, length_y + 0.6, 1.2), mat_stone)
    add_box("UNIV_WaterTable_North", col_ext, (cx, -214.91 + 0.3, 0.6), (width_x + 0.6, 0.6, 1.2), mat_stone)
    add_box("UNIV_WaterTable_South", col_ext, (cx, -258.15 - 0.3, 0.6), (width_x + 0.6, 0.6, 1.2), mat_stone)

    # B. Hollow Exterior Brick Walls (Z = 1.2m to 12.6m, thickness 0.6m)
    # East Exterior Wall (facing Memorial Mall): X = -115.66 - 0.3 = -115.96
    add_box("UNIV_Wall_East_NorthSection", col_ext, (-115.96, cy + 12.0, 6.9), (0.6, 18.0, 11.4), mat_brick)
    add_box("UNIV_Wall_East_SouthSection", col_ext, (-115.96, cy - 12.0, 6.9), (0.6, 18.0, 11.4), mat_brick)
    # East Entrance Portico Wall opening Z in [1.2, 5.0]
    add_box("UNIV_Wall_East_CenterUpper", col_ext, (-115.96, cy, 8.8), (0.6, 7.24, 7.6), mat_brick)

    # West Exterior Wall (facing Beering Hall): X = -137.57 + 0.3 = -137.27
    add_box("UNIV_Wall_West", col_ext, (-137.27, cy, 6.9), (0.6, length_y, 11.4), mat_brick)

    # North Exterior Wall (facing Matthews Hall): Y = -214.91 - 0.3 = -215.21
    add_box("UNIV_Wall_North", col_ext, (cx, -215.21, 6.9), (width_x, 0.6, 11.4), mat_brick)

    # South Exterior Wall (facing Founders Park & Loeb Fountain): Y = -258.15 + 0.3 = -257.85
    add_box("UNIV_Wall_South", col_ext, (cx, -257.85, 6.9), (width_x, 0.6, 11.4), mat_brick)

    # C. Bedford Limestone Quoins on All 4 Corners & Pavilions
    # Corners: (X, Y) = (-115.66, -214.91), (-137.57, -214.91), (-115.66, -258.15), (-137.57, -258.15)
    for qx, qy in [(-115.66, -214.91), (-137.57, -214.91), (-115.66, -258.15), (-137.57, -258.15)]:
        for qz in range(2, 13, 2):
            qsize = (1.1, 0.7, 0.45) if (qz // 2) % 2 == 0 else (0.7, 1.1, 0.45)
            add_box(f"UNIV_Quoin_{int(qx)}_{int(qy)}_{qz}", col_ext, (qx, qy, qz), qsize, mat_stone)

    # D. Horizontal Limestone Beltcourses (Z = 4.2m, 8.4m, 12.6m)
    for bz in [4.2, 8.4, 12.6]:
        add_box(f"UNIV_Beltcourse_E_{int(bz)}", col_ext, (-115.66, cy, bz), (0.35, length_y + 0.4, 0.25), mat_stone)
        add_box(f"UNIV_Beltcourse_W_{int(bz)}", col_ext, (-137.57, cy, bz), (0.35, length_y + 0.4, 0.25), mat_stone)
        add_box(f"UNIV_Beltcourse_N_{int(bz)}", col_ext, (cx, -214.91, bz), (width_x + 0.4, 0.35, 0.25), mat_stone)
        add_box(f"UNIV_Beltcourse_S_{int(bz)}", col_ext, (cx, -258.15, bz), (width_x + 0.4, 0.35, 0.25), mat_stone)

    # E. Victorian Arched Window Bays & Limestone Hood Moulds / Keystones
    # East and West facades: 8 window bays per floor (Z = 2.6m, 6.2m, 10.4m)
    for side, wx, sign_x in [("East", -115.66, 0.15), ("West", -137.57, -0.15)]:
        for f_idx, fz in enumerate([2.6, 6.4, 10.4]):
            for wy in range(int(cy - 18.0), int(cy + 19.0), 5):
                # Skip center east bay on ground floor (that's the entrance)
                if side == "East" and f_idx == 0 and abs(wy - cy) < 4.0:
                    continue
                # Arched window glass
                add_box(f"UNIV_Win_{side}_{wy}_{int(fz)}", col_ext, (wx, wy, fz), (0.1, 2.0, 2.4), mat_glass)
                # Limestone Sill
                add_box(f"UNIV_WinSill_{side}_{wy}_{int(fz)}", col_ext, (wx + sign_x * 0.15, wy, fz - 1.25), (0.4, 2.3, 0.2), mat_stone)
                # Arched Hood Mould & Keystone
                add_box(f"UNIV_WinHood_{side}_{wy}_{int(fz)}", col_ext, (wx + sign_x * 0.15, wy, fz + 1.25), (0.35, 2.2, 0.25), mat_stone)
                add_box(f"UNIV_WinKeystone_{side}_{wy}_{int(fz)}", col_ext, (wx + sign_x * 0.2, wy, fz + 1.4), (0.4, 0.35, 0.35), mat_stone)

    # F. Steep Mansard Slate Roof with Slate Shingles (Z = 12.6m to 16.5m)
    # The Mansard slopes inward steeply on all 4 sides
    add_box("UNIV_Mansard_Roof_Core", col_ext, (cx, cy, 14.55), (width_x - 1.2, length_y - 1.2, 3.9), mat_slate)
    add_box("UNIV_Mansard_Roof_Deck", col_ext, (cx, cy, 16.6), (width_x - 3.4, length_y - 3.4, 0.3), mat_slate)
    # Wrought iron roof cresting along top deck
    add_box("UNIV_Roof_WroughtIron_Cresting", col_ext, (cx, cy, 17.2), (width_x - 3.2, length_y - 3.2, 0.8), mat_bronze)

    # Mansard Dormer Windows (6 dormers along East & West slopes)
    for side, dx in [("East", -115.66 - 0.9), ("West", -137.57 + 0.9)]:
        for dy in [cy - 14.0, cy - 7.0, cy + 7.0, cy + 14.0]:
            add_box(f"UNIV_Dormer_Body_{side}_{int(dy)}", col_ext, (dx, dy, 14.6), (1.6, 1.8, 2.2), mat_brick)
            add_box(f"UNIV_Dormer_Glass_{side}_{int(dy)}", col_ext, (dx + (0.8 if side == 'East' else -0.8), dy, 14.6), (0.1, 1.3, 1.7), mat_glass)
            add_box(f"UNIV_Dormer_Pediment_{side}_{int(dy)}", col_ext, (dx, dy, 15.9), (1.9, 2.0, 0.4), mat_stone)

    # G. Monumental Central Victorian Bell Tower / Cupola (Rising to Z = 25.5m)
    # Tower base: 8.4m x 8.4m, centered at (cx, cy)
    add_box("UNIV_Tower_Brick_Shaft", col_ext, (cx, cy, 16.0), (8.4, 8.4, 6.8), mat_brick)
    add_box("UNIV_Tower_Stone_Cornice", col_ext, (cx, cy, 19.5), (9.0, 9.0, 0.5), mat_stone)

    # 4 Cardinal Clock Faces at Z = 18.0m (East, West, North, South)
    for cdir, cloc, crot in [
        ("East", (cx + 4.25, cy, 18.0), (0, 90, 0)),
        ("West", (cx - 4.25, cy, 18.0), (0, -90, 0)),
        ("North", (cx, cy + 4.25, 18.0), (90, 0, 0)),
        ("South", (cx, cy - 4.25, 18.0), (-90, 0, 0))
    ]:
        add_box(f"UNIV_Clock_Bezel_{cdir}", col_ext, cloc, (0.15 if 'East' in cdir or 'West' in cdir else 2.4, 2.4 if 'East' in cdir or 'West' in cdir else 0.15, 2.4), mat_stone)
        add_cyl(f"UNIV_Clock_Face_{cdir}", col_ext, cloc, 0.95, 0.18, mat_gold)

    # Open Bell Belfry (Z = 19.8m to 23.0m) with 4 Arched Corner Piers
    for px, py in [(cx - 3.6, cy - 3.6), (cx + 3.6, cy - 3.6), (cx - 3.6, cy + 3.6), (cx + 3.6, cy + 3.6)]:
        add_box(f"UNIV_Belfry_Pier_{int(px)}_{int(py)}", col_ext, (px, py, 21.4), (1.4, 1.4, 3.2), mat_brick)

    add_box("UNIV_Belfry_Roof_Slab", col_ext, (cx, cy, 23.2), (8.8, 8.8, 0.4), mat_stone)

    # Historic 1877 Bronze Bell inside Belfry
    add_cyl("UNIV_Historic_Bronze_Bell", col_ext, (cx, cy, 21.4), 0.9, 1.4, mat_bronze, segs=24)
    add_box("UNIV_Bell_Yoke_Beam", col_ext, (cx, cy, 22.3), (0.3, 2.4, 0.4), mat_walnut)

    # Copper Spire / Cupola & Ornamental Weathervane (Z = 23.4m to 26.5m)
    add_box("UNIV_Copper_Cupola_Base", col_ext, (cx, cy, 23.8), (6.4, 6.4, 0.8), mat_copper)
    add_cyl("UNIV_Cupola_Spire_Spire", col_ext, (cx, cy, 25.2), 1.6, 2.0, mat_copper, segs=8)
    add_cyl("UNIV_Cupola_Finial_Rod", col_ext, (cx, cy, 26.8), 0.05, 1.8, mat_gold)
    add_box("UNIV_Cupola_Weathervane_Arrow", col_ext, (cx, cy, 27.2), (1.4, 0.08, 0.3), mat_gold)

    # H. Monumental East Entrance Portico & Staircase (facing Memorial Mall)
    # Portico at X = -115.66 to -111.66 (depth 4.0m), Y in [cy - 3.8, cy + 3.8] (width 7.6m)
    # Grand Limestone Steps rising from Z = 0 to 1.6m
    for st in range(8):
        s_z = 0.1 + st * 0.2
        s_y_span = 7.6
        s_x_loc = -111.4 + st * 0.45
        add_box(f"UNIV_East_Step_{st}", col_ext, (s_x_loc, cy, s_z / 2.0), (0.45, s_y_span, s_z), mat_stone)

    # Portico Columns & Arched Header
    add_box("UNIV_Portico_Slab", col_ext, (-113.66, cy, 1.5), (4.0, 7.6, 0.3), mat_stone)
    add_box("UNIV_Portico_Col_North", col_ext, (-112.2, cy + 3.2, 3.4), (1.0, 1.0, 3.5), mat_stone)
    add_box("UNIV_Portico_Col_South", col_ext, (-112.2, cy - 3.2, 3.4), (1.0, 1.0, 3.5), mat_stone)
    add_box("UNIV_Portico_Entablature", col_ext, (-113.66, cy, 5.3), (4.2, 7.8, 0.6), mat_stone)
    add_box("UNIV_Portico_Pediment", col_ext, (-113.66, cy, 6.1), (3.6, 6.0, 1.0), mat_stone)

    # Gold Inscription on Portico Header: "UNIVERSITY HALL - 1877"
    add_box("UNIV_Portico_Sign_Band", col_ext, (-111.8, cy, 5.3), (0.05, 5.5, 0.4), mat_gold)

    # Heavy Carved Walnut Double Doors
    add_box("UNIV_Main_Double_Doors", col_ext, (-115.8, cy, 2.9), (0.2, 2.8, 2.6), mat_walnut)
    add_box("UNIV_Door_Knobs_Hardware", col_ext, (-115.65, cy, 2.6), (0.1, 0.3, 0.5), mat_bronze)
    # Fanlight transom window above doors
    add_box("UNIV_Door_Transom_Fanlight", col_ext, (-115.8, cy, 4.4), (0.1, 2.8, 1.0), mat_glass)

    # -------------------------------------------------------------
    # 5. JOHN PURDUE'S GRAVE & MEMORIAL MALL INTEGRATION
    # Sited on axis directly East of entrance: X = -105.0m, Y = cy (-236.53m)
    # -------------------------------------------------------------
    print("Building John Purdue's Grave Monument and seated bronze statue...")

    gx = -105.0
    gy = cy

    # Brick Plaza Walkway connecting East Steps to Grave and Memorial Mall
    add_box("UNIV_Memorial_Walkway_Brick", col_site, (-108.5, cy, 0.05), (10.0, 5.0, 0.1), mat_paving)

    # Circular Granite Curb Border around Grave (Diameter 6.4m)
    add_cyl("UNIV_Grave_Circular_Curb", col_site, (gx, gy, 0.15), 3.2, 0.3, mat_stone, segs=32)
    # Manicured Boxwood Garden Bed inside Curb
    add_cyl("UNIV_Grave_Garden_Bed", col_site, (gx, gy, 0.28), 2.9, 0.15, mat_hedge, segs=32)

    # Central Polished Dark Barre Granite Sarcophagus / Headstone Marker
    # Dimensions: 2.2m x 1.2m x 0.45m
    add_box("UNIV_Grave_Granite_Monument", col_site, (gx, gy, 0.55), (2.2, 1.2, 0.45), mat_granite)
    # Inscription Plaque: "JOHN PURDUE / BORN OCT. 31, 1802 / DIED SEPT. 12, 1876"
    add_box("UNIV_Grave_Bronze_Inscription", col_site, (gx, gy, 0.79), (1.8, 0.8, 0.03), mat_gold)

    # Historic Cast-Iron Ornamental Corner Posts around Grave Plot
    for cpi, (cpx, cpy) in enumerate([(gx - 2.2, gy - 2.2), (gx + 2.2, gy - 2.2), (gx - 2.2, gy + 2.2), (gx + 2.2, gy + 2.2)]):
        add_cyl(f"UNIV_Grave_Iron_Post_{cpi}", col_site, (cpx, cpy, 0.55), 0.08, 0.8, mat_bronze)
        add_cyl(f"UNIV_Grave_Post_Finial_{cpi}", col_site, (cpx, cpy, 1.0), 0.12, 0.2, mat_gold)

    # Bronze Statue of John Purdue Seated on a Dark Oak Campus Bench
    # Sited at (X = -101.5, Y = cy + 3.0) facing southwest toward his grave and University Hall
    bx = -101.5
    by = cy + 3.0
    # Campus Bench
    add_box("UNIV_Statue_Bench_Seat", col_site, (bx, by, 0.48), (2.4, 0.6, 0.1), mat_walnut)
    add_box("UNIV_Statue_Bench_Back", col_site, (bx + 0.28, by, 0.85), (2.4, 0.1, 0.6), mat_walnut)
    add_box("UNIV_Statue_Bench_Leg_L", col_site, (bx, by - 1.0, 0.24), (0.5, 0.1, 0.48), mat_bronze)
    add_box("UNIV_Statue_Bench_Leg_R", col_site, (bx, by + 1.0, 0.24), (0.5, 0.1, 0.48), mat_bronze)

    # Life-Size Bronze Statue of John Purdue (frock coat, vest, top hat on bench beside him)
    add_box("UNIV_Statue_JohnPurdue_Torso", col_site, (bx, by - 0.4, 0.95), (0.45, 0.4, 0.75), mat_bronze)
    add_cyl("UNIV_Statue_JohnPurdue_Head", col_site, (bx, by - 0.4, 1.45), 0.14, 0.28, mat_bronze)
    add_box("UNIV_Statue_JohnPurdue_Legs", col_site, (bx - 0.18, by - 0.4, 0.48), (0.45, 0.35, 0.6), mat_bronze)
    add_cyl("UNIV_Statue_TopHat_on_Bench", col_site, (bx, by + 0.4, 0.68), 0.18, 0.25, mat_bronze)
    add_cyl("UNIV_Statue_WalkingCane", col_site, (bx - 0.32, by - 0.25, 0.45), 0.03, 0.9, mat_gold)

    # Victorian Campus Lanterns flanking the Grave plaza
    for li, ly in enumerate([cy - 5.5, cy + 5.5]):
        add_cyl(f"UNIV_Memorial_Lantern_Post_{li}", col_site, (-105.0, ly, 2.2), 0.08, 4.4, mat_bronze)
        add_box(f"UNIV_Memorial_Lantern_Head_{li}", col_site, (-105.0, ly, 4.6), (0.45, 0.45, 0.7), mat_bronze)
        add_box(f"UNIV_Memorial_Lantern_Glow_{li}", col_site, (-105.0, ly, 4.6), (0.32, 0.32, 0.5), mat_lamp_glow)

    # -------------------------------------------------------------
    # 6. DETAILED PHOTOREALISTIC INTERIORS
    # -------------------------------------------------------------
    print("Building detailed interiors (John Purdue Study, Commons, Lecture Hall)...")

    # Interior Floor Slabs (Z = 0.08m, 4.2m, 8.4m, 12.6m)
    add_box("UNIV_Interior_Floor_Ground", col_int, (cx, cy, 0.08), (width_x - 1.2, length_y - 1.2, 0.15), mat_parquet)
    add_box("UNIV_Interior_Floor_First", col_int, (cx, cy, 4.2), (width_x - 1.2, length_y - 1.2, 0.3), mat_parquet)
    add_box("UNIV_Interior_Floor_Second", col_int, (cx, cy, 8.4), (width_x - 1.2, length_y - 1.2, 0.3), mat_parquet)
    add_box("UNIV_Interior_Ceiling_Second", col_int, (cx, cy, 12.4), (width_x - 1.2, length_y - 1.2, 0.3), mat_plaster)

    # =============================================================
    # ROOM A: JOHN PURDUE MEMORIAL PRESIDENTIAL STUDY & ARCHIVE (FLOOR 1)
    # Sited in East Wing at Floor 1: X in [-126.0, -116.5], Y in [cy, cy + 18.0], Z in [4.2, 8.2]
    # =============================================================
    sx = -121.2
    sy = cy + 9.0

    # Room Partition Walls (Victorian Dark Walnut Wainscoting & Ivory Plaster)
    add_box("UNIV_Study_Partition_West", col_int, (-126.2, sy, 6.3), (0.3, 17.5, 3.8), mat_walnut)
    add_box("UNIV_Study_Partition_South", col_int, (sx, cy + 0.3, 6.3), (9.8, 0.3, 3.8), mat_walnut)
    add_box("UNIV_Study_Partition_North", col_int, (sx, cy + 17.7, 6.3), (9.8, 0.3, 3.8), mat_walnut)

    # Persian Medallion Area Rug over Parquet Flooring
    add_box("UNIV_Study_Persian_Rug", col_int, (sx, sy, 4.36), (6.5, 9.0, 0.02), mat_leather)

    # President John Purdue's Carved Antique Mahogany Executive Pedestal Desk
    # Sited at (sx + 1.2, sy), facing west toward the room entrance
    p_desk_x = sx + 1.2
    p_desk_y = sy
    add_box("UNIV_Study_Mahogany_Desk_Top", col_int, (p_desk_x, p_desk_y, 5.15), (1.4, 2.4, 0.1), mat_mahogany)
    add_box("UNIV_Study_Desk_Pedestal_L", col_int, (p_desk_x, p_desk_y - 0.8, 4.75), (1.2, 0.6, 0.7), mat_mahogany)
    add_box("UNIV_Study_Desk_Pedestal_R", col_int, (p_desk_x, p_desk_y + 0.8, 4.75), (1.2, 0.6, 0.7), mat_mahogany)

    # Antique Green Glass Banker's Desk Lamp with Brass Base
    add_cyl("UNIV_Study_BankersLamp_Base", col_int, (p_desk_x + 0.3, p_desk_y + 0.6, 5.24), 0.12, 0.08, mat_bronze)
    add_cyl("UNIV_Study_BankersLamp_Stem", col_int, (p_desk_x + 0.3, p_desk_y + 0.6, 5.42), 0.03, 0.28, mat_bronze)
    add_box("UNIV_Study_BankersLamp_Shade", col_int, (p_desk_x + 0.3, p_desk_y + 0.6, 5.58), (0.16, 0.28, 0.12), mat_bankers_lamp)
    add_box("UNIV_Study_BankersLamp_Bulb", col_int, (p_desk_x + 0.3, p_desk_y + 0.6, 5.54), (0.08, 0.18, 0.06), mat_lamp_glow)

    # Desk Accessories: Antique Leather Ledger, Brass Quill Stand, Purdue Charter Scroll
    add_box("UNIV_Study_Ledger_Book", col_int, (p_desk_x, p_desk_y - 0.3, 5.23), (0.35, 0.45, 0.06), mat_walnut)
    add_cyl("UNIV_Study_Inkwell_Stand", col_int, (p_desk_x + 0.3, p_desk_y - 0.6, 5.24), 0.06, 0.08, mat_bronze)
    add_cyl("UNIV_Study_Charter_Scroll", col_int, (p_desk_x - 0.2, p_desk_y + 0.4, 5.23), 0.05, 0.4, mat_stone)

    # President's High-Back Tufted Burgundy Leather Swivel Chair
    add_box("UNIV_Study_ExecChair_Seat", col_int, (p_desk_x + 0.9, p_desk_y, 4.85), (0.65, 0.65, 0.15), mat_leather)
    add_box("UNIV_Study_ExecChair_Back", col_int, (p_desk_x + 1.2, p_desk_y, 5.4), (0.15, 0.65, 0.95), mat_leather)
    add_box("UNIV_Study_ExecChair_Arm_L", col_int, (p_desk_x + 0.9, p_desk_y - 0.35, 5.2), (0.6, 0.1, 0.4), mat_walnut)
    add_box("UNIV_Study_ExecChair_Arm_R", col_int, (p_desk_x + 0.9, p_desk_y + 0.35, 5.2), (0.6, 0.1, 0.4), mat_walnut)

    # Chesterfield Tufted Burgundy Leather Armchairs for Guests
    for ci, cy_arm in enumerate([sy - 1.8, sy + 1.8]):
        add_box(f"UNIV_Study_Chesterfield_Seat_{ci}", col_int, (sx - 1.2, cy_arm, 4.75), (0.8, 0.8, 0.2), mat_leather)
        add_box(f"UNIV_Study_Chesterfield_Back_{ci}", col_int, (sx - 1.6, cy_arm, 5.2), (0.2, 0.8, 0.7), mat_leather)
        add_box(f"UNIV_Study_Chesterfield_ArmL_{ci}", col_int, (sx - 1.2, cy_arm - 0.45, 5.0), (0.8, 0.15, 0.4), mat_leather)
        add_box(f"UNIV_Study_Chesterfield_ArmR_{ci}", col_int, (sx - 1.2, cy_arm + 0.45, 5.0), (0.8, 0.15, 0.4), mat_leather)

    # Floor-to-Ceiling Glass-Fronted Antique Oak Bookcases along North Wall
    add_box("UNIV_Study_Bookcase_Oak", col_int, (sx + 0.5, cy + 17.3, 6.2), (7.0, 0.6, 3.8), mat_walnut)
    add_box("UNIV_Study_Bookcase_Glass", col_int, (sx + 0.5, cy + 17.0, 6.2), (6.8, 0.05, 3.6), mat_glass)
    add_box("UNIV_Study_Bookcase_Trim", col_int, (sx + 0.5, cy + 17.0, 8.05), (7.2, 0.7, 0.3), mat_walnut)

    # Gilded Baroque Frame holding John Purdue's Historic Oil Portrait on South Wall
    add_box("UNIV_Study_Portrait_GoldFrame", col_int, (sx, cy + 0.45, 6.6), (2.2, 0.1, 1.8), mat_gold)
    add_box("UNIV_Study_Portrait_Canvas", col_int, (sx, cy + 0.48, 6.6), (1.9, 0.05, 1.5), mat_mahogany)
    # Accent picture spotlight over portrait
    add_box("UNIV_Study_Portrait_Lamp", col_int, (sx, cy + 0.65, 7.6), (0.6, 0.15, 0.1), mat_gold)

    # =============================================================
    # ROOM B: GROUND FLOOR STUDENT COLLABORATIVE STUDY COMMONS
    # Sited at Ground Floor South Wing: X in [-136.0, -117.0], Y in [-256.0, -238.0], Z in [0.08, 4.0]
    # =============================================================
    cx_room = cx
    cy_commons = cy - 10.0

    # Long Solid Oak Collaborative Study Tables with Brass Reading Lamps
    for ti, ty_tab in enumerate([cy_commons - 4.5, cy_commons + 4.5]):
        # Study Table
        add_box(f"UNIV_Commons_Table_Top_{ti}", col_int, (cx_room, ty_tab, 0.82), (1.6, 5.4, 0.08), mat_walnut)
        add_box(f"UNIV_Commons_Table_LegL_{ti}", col_int, (cx_room, ty_tab - 2.5, 0.41), (1.4, 0.12, 0.82), mat_bronze)
        add_box(f"UNIV_Commons_Table_LegR_{ti}", col_int, (cx_room, ty_tab + 2.5, 0.41), (1.4, 0.12, 0.82), mat_bronze)

        # 3 Brass Banker's Lamps on each study table
        for li, ly_lamp in enumerate([ty_tab - 1.8, ty_tab, ty_tab + 1.8]):
            add_cyl(f"UNIV_Commons_LampBase_{ti}_{li}", col_int, (cx_room, ly_lamp, 0.88), 0.1, 0.06, mat_bronze)
            add_box(f"UNIV_Commons_LampShade_{ti}_{li}", col_int, (cx_room, ly_lamp, 1.15), (0.15, 0.25, 0.12), mat_bankers_lamp)
            add_box(f"UNIV_Commons_LampBulb_{ti}_{li}", col_int, (cx_room, ly_lamp, 1.12), (0.08, 0.18, 0.05), mat_lamp_glow)

        # Study Task Chairs around each table (4 per side = 8 chairs)
        for chi in range(4):
            ch_y = ty_tab - 1.8 + chi * 1.2
            # West side chairs
            add_box(f"UNIV_Commons_Chair_W_{ti}_{chi}", col_int, (cx_room - 1.1, ch_y, 0.48), (0.5, 0.5, 0.1), mat_walnut)
            add_box(f"UNIV_Commons_Back_W_{ti}_{chi}", col_int, (cx_room - 1.35, ch_y, 0.85), (0.1, 0.5, 0.65), mat_walnut)
            # East side chairs
            add_box(f"UNIV_Commons_Chair_E_{ti}_{chi}", col_int, (cx_room + 1.1, ch_y, 0.48), (0.5, 0.5, 0.1), mat_walnut)
            add_box(f"UNIV_Commons_Back_E_{ti}_{chi}", col_int, (cx_room + 1.35, ch_y, 0.85), (0.1, 0.5, 0.65), mat_walnut)

    # Lounge Armchairs & Coffee Table in center of Commons
    add_box("UNIV_Commons_Coffee_Table", col_int, (cx_room, cy_commons, 0.45), (1.2, 1.8, 0.1), mat_walnut)
    add_box("UNIV_Commons_Lounge_Armchair_N", col_int, (cx_room, cy_commons + 1.5, 0.55), (0.8, 0.8, 0.6), mat_leather)
    add_box("UNIV_Commons_Lounge_Armchair_S", col_int, (cx_room, cy_commons - 1.5, 0.55), (0.8, 0.8, 0.6), mat_leather)

    # =============================================================
    # ROOM C: HISTORIC 1877 LECTURE HALL / CHAPEL (FLOOR 2)
    # Sited at Floor 2 South Wing: X in [-136.0, -117.0], Y in [-256.0, -236.0], Z in [8.4, 12.4]
    # =============================================================
    cy_lec = cy - 10.0

    # Raised Oak Speaker's Dais at North end of room
    add_box("UNIV_Lecture_Speaker_Dais", col_int, (cx_room, cy_lec + 7.5, 8.65), (12.0, 3.2, 0.5), mat_parquet)
    # Carved Walnut Rostrum / Lecture Podium
    add_box("UNIV_Lecture_Walnut_Podium", col_int, (cx_room, cy_lec + 7.0, 9.45), (0.9, 0.7, 1.1), mat_walnut)
    add_box("UNIV_Lecture_Podium_Seal", col_int, (cx_room, cy_lec + 6.62, 9.45), (0.35, 0.05, 0.35), mat_gold)

    # Historic Slate Chalkboards with Walnut Frame on North Wall
    add_box("UNIV_Lecture_Chalkboard_Slate", col_int, (cx_room, cy_lec + 8.8, 10.2), (8.0, 0.05, 1.8), mat_chalkboard)
    add_box("UNIV_Lecture_Chalkboard_Frame", col_int, (cx_room, cy_lec + 8.78, 10.2), (8.3, 0.08, 2.0), mat_walnut)

    # 4 Stepped Tiered Curved Wooden Student Benches
    for bi in range(4):
        b_y = cy_lec + 4.0 - bi * 2.2
        b_z = 8.4 + bi * 0.35
        # Riser tier slab
        add_box(f"UNIV_Lecture_Riser_{bi}", col_int, (cx_room, b_y, 8.4 + (b_z - 8.4) / 2.0), (14.0, 2.0, b_z - 8.4 + 0.1), mat_parquet)
        # Student oak bench seat
        add_box(f"UNIV_Lecture_BenchSeat_{bi}", col_int, (cx_room, b_y + 0.3, b_z + 0.48), (13.6, 0.45, 0.08), mat_walnut)
        add_box(f"UNIV_Lecture_BenchBack_{bi}", col_int, (cx_room, b_y + 0.52, b_z + 0.85), (13.6, 0.08, 0.65), mat_walnut)
        # Continuous student writing desk shelf
        add_box(f"UNIV_Lecture_DeskShelf_{bi}", col_int, (cx_room, b_y - 0.4, b_z + 0.76), (13.6, 0.4, 0.06), mat_walnut)

    # -------------------------------------------------------------
    # 7. DEDICATED HIGH-INTENSITY LIGHTING
    # -------------------------------------------------------------
    print("Installing dedicated lighting...")

    def add_light(name, col, ltype, loc, energy, color=(1.0, 0.95, 0.88), rot=None, size=1.0, spot_size=math.radians(60)):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = energy
        ldata.color = color
        if ltype == 'AREA':
            ldata.size = size
        elif ltype == 'SPOT':
            ldata.spot_size = spot_size
            ldata.spot_blend = 0.25
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = loc
        if rot:
            lobj.rotation_euler = rot
        col.objects.link(lobj)
        return lobj

    # A. John Purdue Study Lighting
    # Desk Banker's Lamp focused warm spot
    add_light("UNIV_Light_Study_DeskSpot", col_int, 'SPOT', (p_desk_x + 0.3, p_desk_y + 0.6, 5.5), 450.0, (1.0, 0.90, 0.70), spot_size=math.radians(65))
    # Ambient warm chandelier in study
    add_light("UNIV_Light_Study_Chandelier", col_int, 'POINT', (sx, sy, 7.4), 850.0, (1.0, 0.92, 0.80))
    # Portrait accent spot
    add_light("UNIV_Light_Study_PortraitSpot", col_int, 'SPOT', (sx, cy + 2.0, 7.5), 350.0, (1.0, 0.95, 0.85), Euler((math.radians(45.0), 0.0, 0.0)), spot_size=math.radians(45))

    # B. Student Study Commons Lighting
    for li, ly_down in enumerate([cy_commons - 4.5, cy_commons + 4.5]):
        add_light(f"UNIV_Light_Commons_Downlight_{li}", col_int, 'AREA', (cx_room, ly_down, 3.8), 950.0, (1.0, 0.92, 0.82), size=3.5)

    # C. Historic Lecture Hall Lighting
    for li, ly_lec in enumerate([cy_lec - 2.0, cy_lec + 5.0]):
        add_light(f"UNIV_Light_Lecture_Chandelier_{li}", col_int, 'POINT', (cx_room, ly_lec, 11.6), 1200.0, (1.0, 0.92, 0.80))
    add_light("UNIV_Light_Lecture_PodiumSpot", col_int, 'SPOT', (cx_room, cy_lec + 4.5, 11.8), 650.0, (1.0, 0.95, 0.85), Euler((math.radians(35.0), 0.0, 0.0)), spot_size=math.radians(50))

    # D. Exterior Grave & Entrance Plaza Lighting
    add_light("UNIV_Light_Portico_Downlight", col_ext, 'POINT', (-113.6, cy, 5.0), 850.0, (1.0, 0.92, 0.82))
    for li, ly in enumerate([cy - 5.5, cy + 5.5]):
        add_light(f"UNIV_Light_Grave_Lantern_{li}", col_site, 'POINT', (-105.0, ly, 4.6), 650.0, (1.0, 0.85, 0.65))

    # -------------------------------------------------------------
    # 8. DEDICATED CALIBRATED INSPECTION CAMERAS
    # -------------------------------------------------------------
    print("Calibrating dedicated inspection cameras...")

    cam_col = bpy.data.collections.get("00_Inspection_Cameras") or bpy.context.scene.collection

    def add_cam(name, loc, rot_deg, focal_len=35.0):
        cam = bpy.data.objects.get(name)
        if not cam:
            cd = bpy.data.cameras.new(name)
            cam = bpy.data.objects.new(name, cd)
            cam_col.objects.link(cam)
        cam.location = loc
        cam.rotation_euler = Euler((math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2])), 'XYZ')
        cam.data.lens = focal_len
        cam.data.clip_start = 0.1
        cam.data.clip_end = 1500.0
        return cam

    # Cam 52: East Street View from Memorial Mall:
    # Captures John Purdue's Grave in foreground, seated bronze statue, East portico, Mansard roof, and central clock tower
    # Placed at (X = -92.0, Y = cy - 4.0, Z = 3.2), looking west-northwest (pitch = 84 deg, yaw = -20 deg)
    cam52 = add_cam("Cam_52_University_Hall_East_MemorialMall_StreetView", (-92.0, cy - 4.0, 3.2), (84.0, 0.0, math.radians(-70.0)), focal_len=24.0)

    # Cam 53: John Purdue's Presidential Study (Floor 1 East Wing):
    # Placed at (sx - 2.8, sy - 3.5, 5.5) looking northeast toward mahogany desk, green banker's lamp, portrait, and bookcases
    cam53 = add_cam("Cam_53_University_Hall_JohnPurdue_Study_Interior", (sx - 2.6, sy - 3.2, 5.5), (82.0, 0.0, math.radians(-40.0)), focal_len=20.0)

    # Cam 54: Student Collaborative Study Commons (Ground Floor South Wing):
    # Placed at (cx_room - 4.5, cy_commons - 6.5, 1.8) looking northeast across study tables, banker's lamps, and lounge
    cam54 = add_cam("Cam_54_University_Hall_Student_Study_Commons_Interior", (cx_room - 4.5, cy_commons - 6.5, 1.8), (82.0, 0.0, math.radians(-35.0)), focal_len=20.0)

    # Cam 55: Historic 1877 Lecture Hall / Chapel (Floor 2):
    # Placed at rear of student tiers (cx_room, cy_lec - 5.0, 10.6) looking forward down to podium dais and chalkboards
    cam55 = add_cam("Cam_55_University_Hall_Historic_LectureHall_Interior", (cx_room, cy_lec - 5.0, 10.6), (82.0, 0.0, 0.0), focal_len=22.0)

    # Cam 56: Founders Park & Memorial Mall Aerial Precinct View:
    # Placed at (X = -65.0, Y = -290.0, Z = 38.0) looking northwest toward University Hall, John Purdue's Grave, Beering Hall, and Founders Park
    cam56 = add_cam("Cam_56_University_Hall_FoundersPark_Aerial", (-65.0, -290.0, 38.0), (64.0, 0.0, math.radians(42.0)), focal_len=30.0)

    bpy.context.scene.camera = cam52
    bpy.context.view_layer.update()

    # Save Master File
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"University Hall & John Purdue Grave successfully built and saved to: {save_path}")

    total_objs = len(bpy.data.objects)
    total_cols = len(bpy.data.collections)
    print(f"Scene metrics: {total_objs} objects across {total_cols} collections.")

if __name__ == "__main__":
    build_university_hall()
