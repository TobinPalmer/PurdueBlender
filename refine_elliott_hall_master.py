import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

def refine_elliott_hall():
    print("==================================================================")
    print("=== REFINING EDWARD C. ELLIOTT HALL OF MUSIC (FINAL POLISH) ======")
    print("==================================================================")

    col_ext = bpy.data.collections.get("33_Elliott_Hall_of_Music_Exterior")
    col_int = bpy.data.collections.get("34_Elliott_Hall_of_Music_Interiors_and_Theatre")
    col_site = bpy.data.collections.get("35_Elliott_Hall_of_Music_Plaza_and_Site")

    # Helper mesh builder
    def add_box(name, col, loc, dim, mat):
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
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
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
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

    mat_stone = bpy.data.materials.get("Elliott_Bedford_Limestone")
    mat_brick = bpy.data.materials.get("Elliott_Purdue_Red_Brick")
    mat_dark_brick = bpy.data.materials.get("Elliott_Dark_Brick_Accent")
    mat_bronze = bpy.data.materials.get("Elliott_ArtDeco_Bronze")
    mat_gold = bpy.data.materials.get("Elliott_Gold_Leaf")
    mat_curtain = bpy.data.materials.get("Elliott_Burgundy_Velvet")
    mat_theatre_seat = bpy.data.materials.get("Elliott_Theatre_Seat_Velvet")
    mat_stage_oak = bpy.data.materials.get("Elliott_Stage_Oak_Deck")
    mat_terrazzo = bpy.data.materials.get("Elliott_Lobby_Terrazzo")
    mat_marquee_glow = bpy.data.materials.get("Elliott_Marquee_Glow")
    mat_paving = bpy.data.materials.get("Elliott_Plaza_Brick")
    mat_carpet = bpy.data.materials.get("Elliott_Burgundy_Velvet")

    # 1. Front Corner Transition Return Walls (Closing the facade between portico and auditorium wings)
    # West Return: X in [-152.0, -140.0], Y in [20.0, 26.4], Z in [0, 22.5]
    add_box("ELLT_Auditorium_Front_Return_W", col_ext, (-146.0, 23.2, 11.25), (12.0, 6.4, 22.5), mat_brick)
    add_box("ELLT_Auditorium_Return_Coping_W", col_ext, (-146.0, 23.2, 22.8), (12.4, 6.8, 0.4), mat_stone)
    add_box("ELLT_Auditorium_Return_WaterTable_W", col_ext, (-146.0, 20.0, 0.8), (12.2, 0.6, 1.6), mat_stone)

    # East Return: X in [-82.0, -70.0], Y in [20.0, 26.4], Z in [0, 22.5]
    add_box("ELLT_Auditorium_Front_Return_E", col_ext, (-76.0, 23.2, 11.25), (12.0, 6.4, 22.5), mat_brick)
    add_box("ELLT_Auditorium_Return_Coping_E", col_ext, (-76.0, 23.2, 22.8), (12.4, 6.8, 0.4), mat_stone)
    add_box("ELLT_Auditorium_Return_WaterTable_E", col_ext, (-76.0, 20.0, 0.8), (12.2, 0.6, 1.6), mat_stone)

    # Beltcourses on front returns
    for zb in [6.0, 12.0, 18.0]:
        add_box(f"ELLT_Return_Beltcourse_W_{int(zb)}", col_ext, (-146.0, 19.9, zb), (12.2, 0.4, 0.35), mat_stone)
        add_box(f"ELLT_Return_Beltcourse_E_{int(zb)}", col_ext, (-76.0, 19.9, zb), (12.2, 0.4, 0.35), mat_stone)

    # 2. Art Deco Stepped Chevrons on South Facade Monumental Portico
    for px in [-133.0, -124.2, -115.4, -106.6, -97.8, -89.0]:
        # Bronze sconce luminaire on each pier at Z = 4.2m
        add_box(f"ELLT_Pier_Bronze_Sconce_{int(px)}", col_ext, (px, 14.7, 4.2), (0.4, 0.25, 0.8), mat_bronze)
        add_box(f"ELLT_Pier_Sconce_Glow_{int(px)}", col_ext, (px, 14.6, 4.2), (0.25, 0.15, 0.6), mat_marquee_glow)

    # 3. Proscenium Arch Art Deco Decorative Chevrons & Purdue Seal Medallion
    add_cyl("ELLT_Proscenium_Seal_Medallion", col_int, (-111.0, 65.5, 14.5), 1.2, 0.15, mat_gold)
    add_box("ELLT_Proscenium_Chevron_L", col_int, (-116.0, 65.6, 14.5), (6.0, 0.1, 0.4), mat_gold)
    add_box("ELLT_Proscenium_Chevron_R", col_int, (-106.0, 65.6, 14.5), (6.0, 0.1, 0.4), mat_gold)

    # 4. Aisles with Burgundy Carpet Runners in Orchestra Bowl
    # Center Aisle: X in [-112.2, -109.8], Y in [32.0, 62.0]
    add_box("ELLT_Aisle_Carpet_Center", col_int, (-111.0, 47.0, 2.5), (2.0, 30.0, 0.05), mat_carpet)
    add_box("ELLT_Aisle_Carpet_Left", col_int, (-128.0, 47.0, 2.5), (1.8, 30.0, 0.05), mat_carpet)
    add_box("ELLT_Aisle_Carpet_Right", col_int, (-94.0, 47.0, 2.5), (1.8, 30.0, 0.05), mat_carpet)

    # 5. Fine-Tuned Inspection Cameras
    cam47 = bpy.data.objects.get("Cam_47_Elliott_Hall_South_StreetView")
    # Placed on north sidewalk of Third Street outside PSYC, looking up at portico
    cam47.location = (-111.0, -18.0, 4.8)
    cam47.rotation_euler = Euler((math.radians(82.0), 0.0, 0.0))
    cam47.data.lens = 20.0

    cam48 = bpy.data.objects.get("Cam_48_Elliott_Hall_Proscenium_Auditorium_Interior")
    # Placed at rear orchestra center aisle, elevated above seats, looking down-forward to proscenium
    cam48.location = (-111.0, 34.0, 5.2)
    cam48.rotation_euler = Euler((math.radians(81.5), 0.0, 0.0))
    cam48.data.lens = 19.0

    cam49 = bpy.data.objects.get("Cam_49_Elliott_Hall_Balcony_Overlook_Interior")
    # Placed at upper balcony railing, overlooking the 6,005 seat auditorium bowl
    cam49.location = (-111.0, 37.0, 16.2)
    cam49.rotation_euler = Euler((math.radians(70.0), 0.0, 0.0))
    cam49.data.lens = 18.0

    cam50 = bpy.data.objects.get("Cam_50_Elliott_Hall_Grand_Foyer_Lobby_Interior")
    # Placed at 3/4 angle in the grand foyer showing terrazzo floor, box office, staircases, and chandeliers
    cam50.location = (-125.0, 19.5, 2.2)
    # Target (-105.0, 24.0, 2.2): dx = 20, dy = 4.5 -> yaw = -atan2(20, 4.5) in Euler
    cam50.rotation_euler = Euler((math.radians(84.0), 0.0, math.radians(-70.0)))
    cam50.data.lens = 18.0

    cam51 = bpy.data.objects.get("Cam_51_Elliott_Hall_CentennialMall_PrecinctView")
    # Aerial precinct view looking northwest toward Elliott Hall and Centennial Mall
    cam51.location = (-55.0, -38.0, 42.0)
    cam51.rotation_euler = Euler((math.radians(64.0), 0.0, math.radians(40.0)))
    cam51.data.lens = 28.0

    bpy.context.view_layer.update()
    bpy.ops.wm.save_mainfile()
    print("Elliott Hall refined and saved successfully!")

if __name__ == "__main__":
    refine_elliott_hall()
