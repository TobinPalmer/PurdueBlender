import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import sys
from pathlib import Path
ROOT = Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')\nsys.path.insert(0, str(ROOT / 'materials'))\nimport pbr_upgrade as pbr

def build_elliott_hall():
    print("==================================================================")
    print("=== BUILDING EDWARD C. ELLIOTT HALL OF MUSIC (HOLLOW ENVELOPE) ==")
    print("==================================================================")

    # 1. Purge existing Elliott objects from any previous pass
    target_cols = [
        "33_Elliott_Hall_of_Music_Exterior",
        "34_Elliott_Hall_of_Music_Interiors_and_Theatre",
        "35_Elliott_Hall_of_Music_Plaza_and_Site"
    ]
    for cname in target_cols:
        c = bpy.data.collections.get(cname)
        if c:
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(c)

    # Setup Collections
    def get_or_create_col(name, parent=None):
        c = bpy.data.collections.get(name)
        if not c:
            c = bpy.data.collections.new(name)
            if parent:
                parent.children.link(c)
            else:
                bpy.context.scene.collection.children.link(c)
        return c

    col_ext = get_or_create_col("33_Elliott_Hall_of_Music_Exterior")
    col_int = get_or_create_col("34_Elliott_Hall_of_Music_Interiors_and_Theatre")
    col_site = get_or_create_col("35_Elliott_Hall_of_Music_Plaza_and_Site")

    # 2. Materials
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

    mat_stone = get_or_create_mat("Elliott_Bedford_Limestone", (0.80, 0.76, 0.68, 1.0), roughness=0.55)
    mat_brick = pbr.upgrade_brick(bpy.data.materials['Elliott_Purdue_Red_Brick'], tint=(.88,.84,.78,1))
    mat_dark_brick = get_or_create_mat("Elliott_Dark_Brick_Accent", (0.24, 0.08, 0.05, 1.0), roughness=0.72)
    mat_bronze = get_or_create_mat("Elliott_ArtDeco_Bronze", (0.38, 0.28, 0.14, 1.0), roughness=0.32, metallic=0.85)
    mat_gold = get_or_create_mat("Elliott_Gold_Leaf", (0.88, 0.72, 0.25, 1.0), roughness=0.22, metallic=0.92)
    mat_marquee_glow = get_or_create_mat("Elliott_Marquee_Glow", (1.0, 0.95, 0.85, 1.0), emission=(1.0, 0.95, 0.85, 1.0), emission_strength=4.5)
    mat_curtain = get_or_create_mat("Elliott_Burgundy_Velvet", (0.32, 0.02, 0.05, 1.0), roughness=0.88)
    mat_theatre_seat = get_or_create_mat("Elliott_Theatre_Seat_Velvet", (0.30, 0.03, 0.06, 1.0), roughness=0.80)
    mat_stage_oak = get_or_create_mat("Elliott_Stage_Oak_Deck", (0.24, 0.15, 0.09, 1.0), roughness=0.45)
    mat_terrazzo = get_or_create_mat("Elliott_Lobby_Terrazzo", (0.82, 0.78, 0.70, 1.0), roughness=0.22)
    mat_glass = get_or_create_mat("Elliott_Bronze_Glazing", (0.15, 0.18, 0.20, 1.0), roughness=0.08)
    mat_roof = get_or_create_mat("Elliott_Roof_Membrane", (0.28, 0.29, 0.30, 1.0), roughness=0.75)
    mat_paving = get_or_create_mat("Elliott_Plaza_Brick", (0.42, 0.18, 0.12, 1.0), roughness=0.65)
    mat_ceiling_baffle = get_or_create_mat("Elliott_Ceiling_Acoustic_Baffle", (0.18, 0.16, 0.15, 1.0), roughness=0.80)
    mat_sconce_glow = get_or_create_mat("Elliott_Warm_Sconce_Glow", (1.0, 0.82, 0.55, 1.0), emission=(1.0, 0.82, 0.55, 1.0), emission_strength=3.8)
    mat_int_wall = get_or_create_mat("Elliott_Auditorium_Acoustic_Wall", (0.45, 0.38, 0.32, 1.0), roughness=0.75)

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
    # 3. EXTERIOR ARCHITECTURE & HOLLOW AUDITORIUM ENVELOPE
    # Footprint: X in [-157.69, -63.93] (width = 93.76m, center X = -110.81m)
    #            Y in [11.65, 98.41] (depth = 86.77m, center Y = 55.03m)
    # -------------------------------------------------------------
    print("Building exterior architecture & hollow envelope...")

    # Hollow Auditorium Exterior Walls (Thickness 0.8m)
    # East exterior wall: X = -70.4
    add_box("ELLT_Auditorium_Wall_East", col_ext, (-70.4, 52.0, 11.25), (0.8, 52.0, 22.5), mat_brick)
    # West exterior wall: X = -151.6
    add_box("ELLT_Auditorium_Wall_West", col_ext, (-151.6, 52.0, 11.25), (0.8, 52.0, 22.5), mat_brick)
    # South dividing wall (Auditorium to Lobby): Y = 26.4
    # Portals for entry into Orchestra
    add_box("ELLT_Auditorium_Wall_South_L", col_ext, (-136.0, 26.4, 11.25), (28.0, 0.8, 22.5), mat_brick)
    add_box("ELLT_Auditorium_Wall_South_C", col_ext, (-111.0, 26.4, 14.25), (18.0, 0.8, 16.5), mat_brick) # Portal opening Z in [0, 6]
    add_box("ELLT_Auditorium_Wall_South_R", col_ext, (-86.0, 26.4, 11.25), (28.0, 0.8, 22.5), mat_brick)
    # North dividing wall (Auditorium to Stage Fly Tower): Y = 77.6
    # Left and Right stage walls flanking the Proscenium opening
    add_box("ELLT_Auditorium_Wall_North_W", col_ext, (-140.0, 77.6, 11.25), (22.0, 0.8, 22.5), mat_brick)
    add_box("ELLT_Auditorium_Wall_North_E", col_ext, (-82.0, 77.6, 11.25), (22.0, 0.8, 22.5), mat_brick)

    # Auditorium Roof Slab & Coping
    add_box("ELLT_Auditorium_Roof_Slab", col_ext, (-111.0, 52.0, 22.6), (82.0, 52.0, 0.5), mat_roof)
    add_box("ELLT_Auditorium_Limestone_Coping_E", col_ext, (-70.3, 52.0, 22.9), (1.2, 52.4, 0.4), mat_stone)
    add_box("ELLT_Auditorium_Limestone_Coping_W", col_ext, (-151.7, 52.0, 22.9), (1.2, 52.4, 0.4), mat_stone)

    # Base Water Table around Auditorium (Perimeter strips)
    add_box("ELLT_WaterTable_East", col_ext, (-70.1, 52.0, 0.8), (1.2, 52.4, 1.6), mat_stone)
    add_box("ELLT_WaterTable_West", col_ext, (-151.9, 52.0, 0.8), (1.2, 52.4, 1.6), mat_stone)

    # Horizontal Limestone Beltcourses (Z = 6.0m, 12.0m, 18.0m)
    for zb in [6.0, 12.0, 18.0]:
        add_box(f"ELLT_Beltcourse_East_{int(zb)}", col_ext, (-70.2, 52.0, zb), (0.6, 52.2, 0.35), mat_stone)
        add_box(f"ELLT_Beltcourse_West_{int(zb)}", col_ext, (-151.8, 52.0, zb), (0.6, 52.2, 0.35), mat_stone)

    # Stage Fly Loft Tower (North Side, rising to Z = 28.5m)
    # Hollow fly tower envelope:
    add_box("ELLT_FlyTower_Wall_North", col_ext, (-111.0, 97.6, 14.25), (50.0, 0.8, 28.5), mat_brick)
    add_box("ELLT_FlyTower_Wall_West", col_ext, (-135.6, 88.0, 14.25), (0.8, 20.0, 28.5), mat_brick)
    add_box("ELLT_FlyTower_Wall_East", col_ext, (-86.4, 88.0, 14.25), (0.8, 20.0, 28.5), mat_brick)
    add_box("ELLT_FlyTower_Roof", col_ext, (-111.0, 88.0, 28.6), (50.0, 20.0, 0.4), mat_roof)
    add_box("ELLT_FlyTower_Coping", col_ext, (-111.0, 88.0, 28.9), (50.8, 20.8, 0.3), mat_stone)

    # 4 Brick Pilasters on North Fly Tower
    for px in [-130.0, -117.0, -105.0, -92.0]:
        add_box(f"ELLT_FlyTower_Pilaster_{int(px)}", col_ext, (px, 98.2, 14.25), (1.6, 0.6, 28.5), mat_dark_brick)

    # WBAA Radio Transmitter Antenna Mast on Fly Tower Roof
    add_cyl("ELLT_WBAA_Antenna_Base", col_ext, (-111.0, 88.0, 29.5), 0.6, 1.8, mat_bronze)
    add_cyl("ELLT_WBAA_Antenna_Mast", col_ext, (-111.0, 88.0, 36.0), 0.12, 12.0, mat_bronze)
    add_cyl("ELLT_WBAA_Antenna_Crossarm", col_ext, (-111.0, 88.0, 41.5), 0.05, 3.2, mat_bronze)

    # North Stage Loading Dock & Service Entry
    add_box("ELLT_North_Loading_Dock_Slab", col_ext, (-111.0, 98.6, 0.6), (18.0, 2.4, 1.2), mat_stone)
    add_box("ELLT_North_Loading_Door_0", col_ext, (-115.0, 98.1, 2.5), (4.2, 0.3, 3.6), mat_bronze)
    add_box("ELLT_North_Loading_Door_1", col_ext, (-107.0, 98.1, 2.5), (4.2, 0.3, 3.6), mat_bronze)

    # Flanking Administrative Wings (East and West)
    add_box("ELLT_East_Admin_Wing", col_ext, (-66.0, 52.0, 8.25), (8.0, 52.0, 16.5), mat_brick)
    add_box("ELLT_East_Admin_Roof", col_ext, (-66.0, 52.0, 16.6), (7.8, 51.5, 0.3), mat_roof)
    add_box("ELLT_East_Admin_Coping", col_ext, (-66.0, 52.0, 16.8), (8.4, 52.4, 0.4), mat_stone)

    add_box("ELLT_West_Admin_Wing", col_ext, (-156.0, 52.0, 8.25), (8.0, 52.0, 16.5), mat_brick)
    add_box("ELLT_West_Admin_Roof", col_ext, (-156.0, 52.0, 16.6), (7.8, 51.5, 0.3), mat_roof)
    add_box("ELLT_West_Admin_Coping", col_ext, (-156.0, 52.0, 16.8), (8.4, 52.4, 0.4), mat_stone)

    # Windows on East & West Wings
    for side, wx in [("East", -61.9), ("West", -160.1)]:
        for fy in range(30, 75, 6):
            for fz in [3.0, 7.2, 11.4]:
                add_box(f"ELLT_Win_{side}_{fy}_{int(fz)}", col_ext, (wx, fy, fz), (0.2, 2.4, 2.2), mat_glass)
                add_box(f"ELLT_WinSill_{side}_{fy}_{int(fz)}", col_ext, (wx, fy, fz - 1.2), (0.35, 2.6, 0.2), mat_stone)

    # -------------------------------------------------------------
    # 4. MONUMENTAL ART DECO SOUTH ENTRANCE PORTICO & FACADE
    # Facing South along Third Street / Hovde Hall: Y in [11.65, 26.0]
    # Sited at X in [-140.0, -82.0] (width 58.0m), Z up to 23.5m
    # -------------------------------------------------------------
    print("Building monumental Art Deco limestone portico...")

    # Grand Stepped Plinth / Entrance Terraces (Limestone steps)
    add_box("ELLT_South_Plinth_Tier_1", col_ext, (-111.0, 12.0, 0.25), (66.0, 4.0, 0.5), mat_stone)
    add_box("ELLT_South_Plinth_Tier_2", col_ext, (-111.0, 13.5, 0.65), (62.0, 3.5, 0.5), mat_stone)
    add_box("ELLT_South_Plinth_Tier_3", col_ext, (-111.0, 15.0, 1.05), (58.0, 3.0, 0.5), mat_stone)

    # Flanking Solid Limestone End Pylons / Corner Pavilions (West and East)
    add_box("ELLT_South_Pylon_West", col_ext, (-136.5, 20.0, 11.0), (7.0, 8.0, 20.0), mat_stone)
    add_box("ELLT_South_Pylon_East", col_ext, (-85.5, 20.0, 11.0), (7.0, 8.0, 20.0), mat_stone)

    # Recessed South Entry Wall behind the piers (at Y = 18.2m)
    # Spans X in [-133.0, -89.0] (width 44.0m)
    add_box("ELLT_South_Recessed_Wall_Top", col_ext, (-111.0, 18.2, 20.5), (44.0, 0.5, 3.0), mat_stone)

    # 6 Monumental Art Deco Fluted Limestone Piers (creating 5 bays)
    pier_xs = [-133.0, -124.2, -115.4, -106.6, -97.8, -89.0]
    for i, px in enumerate(pier_xs):
        # Fluted pier
        add_box(f"ELLT_ArtDeco_Pier_{i}", col_ext, (px, 15.6, 11.0), (2.0, 1.6, 20.0), mat_stone)
        add_box(f"ELLT_ArtDeco_PierCap_{i}", col_ext, (px, 15.6, 21.2), (2.4, 1.9, 0.8), mat_stone)
        # Vertical fluting indentations
        add_box(f"ELLT_Pier_Flute_A_{i}", col_ext, (px - 0.42, 14.75, 11.0), (0.18, 0.2, 18.0), mat_dark_brick)
        add_box(f"ELLT_Pier_Flute_B_{i}", col_ext, (px + 0.42, 14.75, 11.0), (0.18, 0.2, 18.0), mat_dark_brick)

    # Monumental Art Deco Entablature & Stepped Parapet Header
    add_box("ELLT_ArtDeco_Entablature", col_ext, (-111.0, 16.0, 21.8), (52.0, 2.6, 1.8), mat_stone)
    add_box("ELLT_ArtDeco_Stepped_Pediment", col_ext, (-111.0, 16.2, 23.2), (32.0, 2.2, 1.4), mat_stone)

    # Inscription Frieze on Entablature Header
    add_box("ELLT_Inscription_Frieze_Band", col_ext, (-111.0, 14.65, 21.8), (42.0, 0.1, 1.2), mat_gold)

    # 5 Recessed Glazed Bays between the 6 Piers
    bay_centers = [(-128.6), (-119.8), (-111.0), (-102.2), (-93.4)]
    for i, bx in enumerate(bay_centers):
        # Upper 3-story vertical window ribbon with dark bronze mullions
        add_box(f"ELLT_Upper_Ribbon_Glass_{i}", col_ext, (bx, 18.2, 14.5), (6.4, 0.15, 11.0), mat_glass)
        add_box(f"ELLT_Upper_Bronze_Mullion_L_{i}", col_ext, (bx - 2.0, 18.1, 14.5), (0.15, 0.25, 11.0), mat_bronze)
        add_box(f"ELLT_Upper_Bronze_Mullion_R_{i}", col_ext, (bx + 2.0, 18.1, 14.5), (0.15, 0.25, 11.0), mat_bronze)
        for tz in [11.0, 15.0, 19.0]:
            add_box(f"ELLT_Bronze_Transom_{i}_{int(tz)}", col_ext, (bx, 18.1, tz), (6.4, 0.25, 0.15), mat_bronze)

        # Ground Floor Bronze Double Entry Doors (at Y = 18.2m)
        add_box(f"ELLT_Entry_Door_Frame_{i}", col_ext, (bx, 18.1, 2.8), (5.2, 0.25, 3.8), mat_bronze)
        add_box(f"ELLT_Entry_Door_Glass_{i}", col_ext, (bx, 18.05, 2.8), (4.8, 0.1, 3.4), mat_glass)
        add_box(f"ELLT_Entry_Door_Bronze_Mullion_{i}", col_ext, (bx, 18.0, 2.8), (0.18, 0.18, 3.4), mat_bronze)
        add_box(f"ELLT_Door_Pulls_{i}", col_ext, (bx, 17.9, 2.4), (0.4, 0.1, 0.7), mat_gold)

    # Cantilevered Historic Art Deco Marquee Canopy (Overhangs across all 5 bays)
    # Spans X in [-134.0, -88.0] (width 46.0m), Y in [11.5, 15.8], Z = 5.2m
    add_box("ELLT_Marquee_Canopy_Slab", col_ext, (-111.0, 13.65, 5.2), (46.0, 4.3, 0.5), mat_bronze)
    add_box("ELLT_Marquee_Fascia_Front", col_ext, (-111.0, 11.45, 5.2), (46.2, 0.2, 0.7), mat_bronze)
    add_box("ELLT_Marquee_Soffit_Glow", col_ext, (-111.0, 13.65, 4.92), (45.0, 4.0, 0.05), mat_marquee_glow)

    # 3D Illuminated Lettering on Marquee: "EDWARD C. ELLIOTT HALL OF MUSIC"
    add_box("ELLT_Marquee_Lettering_Sign", col_ext, (-111.0, 11.3, 5.2), (38.0, 0.08, 0.55), mat_gold)

    # -------------------------------------------------------------
    # 5. GRAND 6,005-SEAT PROSCENIUM THEATRE AUDITORIUM INTERIOR
    # Sited inside the hollow auditorium envelope:
    # X in [-148.0, -74.0] (width 74.0m), Y in [28.0, 76.0] (depth 48.0m)
    # -------------------------------------------------------------
    print("Building 6,005-seat proscenium theatre interior...")

    # Polished Theatre Ground Floor Slab
    add_box("ELLT_Auditorium_Interior_Floor", col_int, (-111.0, 52.0, 0.08), (74.0, 48.0, 0.15), mat_stone)
    add_box("ELLT_Auditorium_Interior_Ceiling", col_int, (-111.0, 52.0, 21.0), (74.0, 48.0, 0.4), mat_ceiling_baffle)
    add_box("ELLT_Auditorium_Interior_Wall_W", col_int, (-147.8, 52.0, 10.5), (0.2, 48.0, 21.0), mat_int_wall)
    add_box("ELLT_Auditorium_Interior_Wall_E", col_int, (-74.2, 52.0, 10.5), (0.2, 48.0, 21.0), mat_int_wall)

    # Monumental Proscenium Stage (North end: Y in [66.0, 84.0])
    # Stage Deck: 38.0m wide x 16.0m deep, elevated at Z = 1.6m
    add_box("ELLT_Proscenium_Stage_Deck", col_int, (-111.0, 74.0, 0.8), (38.0, 16.0, 1.6), mat_stage_oak)
    add_box("ELLT_Stage_Apron_Edge", col_int, (-111.0, 65.8, 0.8), (38.2, 0.4, 1.6), mat_stone)

    # Sunken Orchestra Pit (In front of stage: Y in [62.5, 65.5], Z = 0.5m)
    add_box("ELLT_Orchestra_Pit_Railing", col_int, (-111.0, 62.5, 0.8), (28.0, 0.15, 1.0), mat_bronze)

    # Monumental Proscenium Arch Framing the Stage
    # Opening: 34.0m wide x 11.0m high, Arch header at Z = 13.0m
    add_box("ELLT_Proscenium_Arch_Pillar_W", col_int, (-129.0, 66.0, 7.5), (2.8, 1.2, 13.0), mat_gold)
    add_box("ELLT_Proscenium_Arch_Pillar_E", col_int, (-93.0, 66.0, 7.5), (2.8, 1.2, 13.0), mat_gold)
    add_box("ELLT_Proscenium_Arch_Header", col_int, (-111.0, 66.0, 14.5), (38.8, 1.4, 2.2), mat_gold)

    # Grand Burgundy Velvet Curtain with Valance
    add_box("ELLT_Grand_Velvet_Curtain", col_int, (-111.0, 66.8, 7.5), (33.0, 0.2, 11.5), mat_curtain)
    add_box("ELLT_Grand_Curtain_Valance", col_int, (-111.0, 66.5, 13.2), (33.4, 0.4, 1.8), mat_curtain)

    # 1. Orchestra Main Level Seating (Stepped concrete riser bowl: Y in [32.0, 60.0])
    # 16 stepped tiers sloping up from Z = 0.2m (front) to Z = 4.8m (rear)
    for t in range(16):
        ty = 60.0 - t * 1.75
        tz = 0.2 + t * 0.28
        width = 44.0 + t * 1.5  # Fan-shaped widening toward the rear
        # Concrete seating riser tier
        add_box(f"ELLT_Orchestra_Riser_{t}", col_int, (-111.0, ty, tz / 2.0), (width, 1.7, tz), mat_stone)
        # Burgundy velvet seat row (divided into Left, Center, Right sections)
        add_box(f"ELLT_Orch_SeatRow_Center_{t}", col_int, (-111.0, ty + 0.2, tz + 0.45), (width * 0.52, 0.55, 0.75), mat_theatre_seat)
        add_box(f"ELLT_Orch_SeatRow_Left_{t}", col_int, (-111.0 - width * 0.35, ty + 0.2, tz + 0.45), (width * 0.22, 0.55, 0.75), mat_theatre_seat)
        add_box(f"ELLT_Orch_SeatRow_Right_{t}", col_int, (-111.0 + width * 0.35, ty + 0.2, tz + 0.45), (width * 0.22, 0.55, 0.75), mat_theatre_seat)

    # 2. Cantilevered First Balcony / Mezzanine (Y in [30.0, 48.0], Z = 7.5m to 12.0m)
    add_box("ELLT_Balcony_1_Slab", col_int, (-111.0, 39.0, 7.2), (64.0, 18.0, 0.8), mat_stone)
    add_box("ELLT_Balcony_1_Safety_Railing", col_int, (-111.0, 48.0, 8.2), (64.0, 0.2, 1.1), mat_bronze)
    for bt in range(8):
        bty = 47.0 - bt * 2.0
        btz = 7.6 + bt * 0.45
        add_box(f"ELLT_Balcony1_Riser_{bt}", col_int, (-111.0, bty, 7.2 + (btz - 7.2) / 2.0), (62.0, 1.9, btz - 7.2), mat_stone)
        add_box(f"ELLT_Balcony1_SeatRow_{bt}", col_int, (-111.0, bty + 0.2, btz + 0.45), (58.0, 0.55, 0.75), mat_theatre_seat)

    # 3. Cantilevered Second Balcony / Gallery (Y in [29.0, 40.0], Z = 13.5m to 17.5m)
    add_box("ELLT_Balcony_2_Slab", col_int, (-111.0, 34.5, 13.2), (60.0, 11.0, 0.8), mat_stone)
    add_box("ELLT_Balcony_2_Safety_Railing", col_int, (-111.0, 40.0, 14.2), (60.0, 0.2, 1.1), mat_bronze)
    for gt in range(5):
        gty = 39.0 - gt * 2.0
        gtz = 13.6 + gt * 0.55
        add_box(f"ELLT_Balcony2_SeatRow_{gt}", col_int, (-111.0, gty + 0.2, gtz + 0.45), (54.0, 0.55, 0.75), mat_theatre_seat)

    # Suspended Acoustic Sound Clouds / Baffles on Ceiling (4 giant stepped baffles)
    for ci, cy in enumerate([60.0, 50.0, 40.0, 32.0]):
        add_box(f"ELLT_Acoustic_Baffle_{ci}", col_int, (-111.0, cy, 19.5 - ci * 0.4), (58.0 - ci * 2.0, 7.5, 0.3), mat_ceiling_baffle)
        # Recessed downlights in each baffle
        for dlx in [-130.0, -120.0, -111.0, -102.0, -92.0]:
            add_cyl(f"ELLT_Ceiling_Downlight_{ci}_{int(dlx)}", col_int, (dlx, cy, 19.3 - ci * 0.4), 0.4, 0.1, mat_sconce_glow)

    # Art Deco Wall Sconces along East and West Auditorum Walls
    for sy in range(34, 64, 6):
        # West Wall Sconces
        add_box(f"ELLT_Sconce_W_{sy}", col_int, (-147.5, sy, 7.5), (0.2, 0.6, 1.6), mat_gold)
        add_box(f"ELLT_SconceGlow_W_{sy}", col_int, (-147.4, sy, 7.5), (0.1, 0.4, 1.4), mat_sconce_glow)
        # East Wall Sconces
        add_box(f"ELLT_Sconce_E_{sy}", col_int, (-74.5, sy, 7.5), (0.2, 0.6, 1.6), mat_gold)
        add_box(f"ELLT_SconceGlow_E_{sy}", col_int, (-74.6, sy, 7.5), (0.1, 0.4, 1.4), mat_sconce_glow)

    # -------------------------------------------------------------
    # 6. GRAND ART DECO ENTRANCE FOYER / LOBBY
    # Sited between South portico and auditorium: Y in [18.5, 26.0]
    # -------------------------------------------------------------
    print("Building grand Art Deco entrance foyer and box office...")

    # Polished Terrazzo Lobby Floor
    add_box("ELLT_Lobby_Terrazzo_Floor", col_int, (-111.0, 22.25, 0.08), (54.0, 7.5, 0.15), mat_terrazzo)
    add_box("ELLT_Lobby_Ceiling_Slab", col_int, (-111.0, 22.25, 5.0), (54.0, 7.5, 0.3), mat_stone)

    # Central Art Deco Ticket Box Office Booth
    add_box("ELLT_Box_Office_Oak_Counter", col_int, (-111.0, 24.2, 0.65), (8.0, 2.0, 1.1), mat_stage_oak)
    add_box("ELLT_Box_Office_Quartz_Top", col_int, (-111.0, 24.2, 1.25), (8.4, 2.2, 0.1), mat_stone)
    add_box("ELLT_Box_Office_Glass_Window", col_int, (-111.0, 23.2, 2.2), (8.0, 0.1, 1.8), mat_glass)
    add_box("ELLT_Box_Office_Brass_Wickets", col_int, (-111.0, 23.15, 1.8), (7.8, 0.15, 0.8), mat_gold)
    add_box("ELLT_Box_Office_Header_Sign", col_int, (-111.0, 23.1, 3.4), (6.5, 0.1, 0.5), mat_gold)

    # Grand Dual Terrazzo Staircases (East and West wings of lobby leading to Balcony)
    for side, sx in [("West", -132.0), ("East", -90.0)]:
        add_box(f"ELLT_Lobby_Stair_{side}", col_int, (sx, 22.2, 2.4), (5.0, 6.0, 4.6), mat_terrazzo)
        add_box(f"ELLT_Lobby_Balustrade_{side}", col_int, (sx + (2.6 if side == 'West' else -2.6), 22.2, 3.4), (0.2, 6.2, 1.1), mat_bronze)

    # Brass Chandelier Luminaires in Lobby
    for lx in [-125.0, -111.0, -97.0]:
        add_cyl(f"ELLT_Lobby_Chandelier_{int(lx)}", col_int, (lx, 21.0, 4.4), 0.8, 0.3, mat_gold)
        add_cyl(f"ELLT_Lobby_Chandelier_Glow_{int(lx)}", col_int, (lx, 21.0, 4.2), 0.6, 0.1, mat_marquee_glow)

    # -------------------------------------------------------------
    # 7. ARRIVAL PLAZA, CIRCULAR DRIVE & SITE INTEGRATION
    # South of portico: Y in [0.0, 12.0], X in [-150.0, -72.0]
    # -------------------------------------------------------------
    print("Building arrival plaza and site hardscape...")

    # Semicircular Brick & Concrete Arrival Plaza
    add_box("ELLT_South_Arrival_Plaza_Paving", col_site, (-111.0, 6.0, 0.05), (76.0, 12.0, 0.1), mat_paving)

    # Curved Limestone Seatwalls Flanking Entrance Plaza
    for side, cx in [("West", -144.0), ("East", -78.0)]:
        add_box(f"ELLT_Plaza_Seatwall_{side}", col_site, (cx, 6.0, 0.4), (2.0, 11.0, 0.75), mat_stone)
        add_box(f"ELLT_Plaza_Seatwall_Cap_{side}", col_site, (cx, 6.0, 0.8), (2.3, 11.3, 0.12), mat_stone)

    # Campus Teak Wood Benches along Plaza
    for bi, bx in enumerate([-136.0, -126.0, -96.0, -86.0]):
        add_box(f"ELLT_Plaza_Bench_Seat_{bi}", col_site, (bx, 3.5, 0.48), (2.6, 0.6, 0.1), mat_stage_oak)
        add_box(f"ELLT_Plaza_Bench_Back_{bi}", col_site, (bx, 3.2, 0.82), (2.6, 0.1, 0.6), mat_stage_oak)
        add_box(f"ELLT_Plaza_Bench_Leg_L_{bi}", col_site, (bx - 1.1, 3.5, 0.24), (0.1, 0.5, 0.48), mat_bronze)
        add_box(f"ELLT_Plaza_Bench_Leg_R_{bi}", col_site, (bx + 1.1, 3.5, 0.24), (0.1, 0.5, 0.48), mat_bronze)

    # Sheffield Bicycle Racks
    for ri, rx in enumerate([-102.0, -100.5, -99.0, -97.5, -96.0, -94.5]):
        add_box(f"ELLT_BikeRack_{ri}", col_site, (rx, 2.5, 0.45), (0.1, 1.2, 0.9), mat_bronze)

    # Campus Victorian Lantern Posts along Arrival Plaza
    for li, lx in enumerate([-140.0, -122.0, -100.0, -82.0]):
        add_cyl(f"ELLT_Campus_Lantern_Post_{li}", col_site, (lx, 1.5, 2.2), 0.08, 4.4, mat_bronze)
        add_box(f"ELLT_Campus_Lantern_Head_{li}", col_site, (lx, 1.5, 4.6), (0.45, 0.45, 0.7), mat_bronze)
        add_box(f"ELLT_Campus_Lantern_Glow_{li}", col_site, (lx, 1.5, 4.6), (0.32, 0.32, 0.5), mat_marquee_glow)

    # -------------------------------------------------------------
    # 8. DEDICATED HIGH-INTENSITY LIGHTING
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

    # Stage Show Lighting (Warm Spotlights on Curtain and Deck)
    add_light("ELLT_Stage_Wash_Center", col_int, 'SPOT', (-111.0, 64.0, 16.0), 22000.0, (1.0, 0.95, 0.88), Euler((math.radians(45.0), 0.0, 0.0)), spot_size=math.radians(70))
    add_light("ELLT_Stage_Key_W", col_int, 'SPOT', (-125.0, 60.0, 15.0), 14000.0, (1.0, 0.88, 0.75), Euler((math.radians(48.0), math.radians(22.0), 0.0)), spot_size=math.radians(55))
    add_light("ELLT_Stage_Key_E", col_int, 'SPOT', (-97.0, 60.0, 15.0), 14000.0, (1.0, 0.88, 0.75), Euler((math.radians(48.0), math.radians(-22.0), 0.0)), spot_size=math.radians(55))
    add_light("ELLT_Stage_Apron_Fill", col_int, 'AREA', (-111.0, 72.0, 12.0), 12000.0, (1.0, 0.92, 0.85), size=14.0)

    # Proscenium Arch Uplights
    add_light("ELLT_Proscenium_Uplight_W", col_int, 'SPOT', (-128.5, 66.2, 1.8), 4500.0, (1.0, 0.85, 0.5), Euler((math.radians(-80.0), 0.0, 0.0)), spot_size=math.radians(40))
    add_light("ELLT_Proscenium_Uplight_E", col_int, 'SPOT', (-93.5, 66.2, 1.8), 4500.0, (1.0, 0.85, 0.5), Euler((math.radians(-80.0), 0.0, 0.0)), spot_size=math.radians(40))

    # House Seating Downlights (Warm ambient illumination)
    for hx, hy in [(-125.0, 50.0), (-111.0, 50.0), (-97.0, 50.0), (-125.0, 38.0), (-111.0, 38.0), (-97.0, 38.0)]:
        add_light(f"ELLT_House_Downlight_{int(hx)}_{int(hy)}", col_int, 'AREA', (hx, hy, 18.0), 6000.0, (1.0, 0.90, 0.80), size=6.0)

    # Balcony Underdeck Warm Wash
    for bx in [-122.0, -111.0, -100.0]:
        add_light(f"ELLT_Balcony_Underwash_{int(bx)}", col_int, 'AREA', (bx, 42.0, 6.8), 3000.0, (1.0, 0.88, 0.76), size=4.0)

    # Grand Foyer / Lobby Chandelier Lights
    for lx in [-125.0, -111.0, -97.0]:
        add_light(f"ELLT_Lobby_Chandelier_Light_{int(lx)}", col_int, 'POINT', (lx, 21.0, 3.8), 2400.0, (1.0, 0.90, 0.78))
    add_light("ELLT_Box_Office_Accent", col_int, 'SPOT', (-111.0, 22.0, 4.2), 1800.0, (1.0, 0.92, 0.85), Euler((math.radians(35.0), 0.0, 0.0)), spot_size=math.radians(45))

    # South Marquee Downlights & Plaza Lanterns
    for mx in [-125.0, -111.0, -97.0]:
        add_light(f"ELLT_Marquee_Soffit_Light_{int(mx)}", col_ext, 'AREA', (mx, 13.8, 4.8), 4000.0, (1.0, 0.94, 0.86), size=3.5)

    for li, lx in enumerate([-140.0, -122.0, -100.0, -82.0]):
        add_light(f"ELLT_Plaza_Lantern_Light_{li}", col_site, 'POINT', (lx, 1.5, 4.6), 850.0, (1.0, 0.85, 0.65))

    # -------------------------------------------------------------
    # 9. CALIBRATED INSPECTION CAMERAS WITH OPTIMAL FOCAL LENGTHS
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

    # Cam 47: South Street View arrival facing monumental Art Deco Portico & Marquee
    # Placed at Y = -35.0m, Z = 6.0m, tilted slightly up (86 deg) with 28mm wide lens
    cam47 = add_cam("Cam_47_Elliott_Hall_South_StreetView", (-111.0, -32.0, 6.0), (86.0, 0.0, 0.0), focal_len=28.0)

    # Cam 48: Main Floor Orchestra interior facing proscenium arch, grand velvet curtain & stage
    # Placed at Y = 35.0m, Z = 3.5m, looking slightly up (84 deg) with 24mm wide lens
    cam48 = add_cam("Cam_48_Elliott_Hall_Proscenium_Auditorium_Interior", (-111.0, 35.0, 3.5), (84.0, 0.0, 0.0), focal_len=24.0)

    # Cam 49: Upper Tier Balcony sweeping overlook of the 6,005-seat bowl and stage
    # Placed at Y = 31.0m, Z = 15.0m, looking down (74 deg) with 22mm ultra-wide lens
    cam49 = add_cam("Cam_49_Elliott_Hall_Balcony_Overlook_Interior", (-111.0, 31.0, 15.0), (74.0, 0.0, 0.0), focal_len=22.0)

    # Cam 50: Art Deco Grand Foyer / Lobby with ticket box office and staircases
    # Placed at Y = 19.2m, Z = 1.8m, looking north (80 deg) with 22mm lens
    cam50 = add_cam("Cam_50_Elliott_Hall_Grand_Foyer_Lobby_Interior", (-111.0, 19.2, 1.8), (80.0, 0.0, 0.0), focal_len=22.0)

    # Cam 51: Aerial Precinct Overview connecting Elliott Hall to Centennial Mall, WALC & Bell Tower
    # Placed at (-60.0, -35.0, 45.0), looking northwest (62 deg pitch, 36 deg yaw)
    cam51 = add_cam("Cam_51_Elliott_Hall_CentennialMall_PrecinctView", (-60.0, -35.0, 45.0), (62.0, 0.0, 36.0), focal_len=30.0)

    bpy.context.scene.camera = cam47
    bpy.context.view_layer.update()

    # Save Master File
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Elliott Hall of Music v2 successfully built and saved to: {save_path}")

    total_objs = len(bpy.data.objects)
    total_cols = len(bpy.data.collections)
    print(f"Scene metrics: {total_objs} objects across {total_cols} collections.")

if __name__ == "__main__":
    build_elliott_hall()
