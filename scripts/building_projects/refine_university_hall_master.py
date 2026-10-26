import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

def refine_university_hall():
    print("==================================================================")
    print("=== REFINING UNIVERSITY HALL (UNIV - 1877) - POLISH PASS =========")
    print("==================================================================")

    col_ext = bpy.data.collections.get("36_University_Hall_Exterior")
    col_int = bpy.data.collections.get("37_University_Hall_Interiors")
    col_site = bpy.data.collections.get("38_University_Hall_Grave_and_MemorialMall")

    # Helper mesh builders
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

    def point_at(obj, target):
        direction = target - obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        obj.rotation_euler = rot_quat.to_euler()

    mat_walnut = bpy.data.materials.get("Univ_Dark_Walnut")
    mat_gold = bpy.data.materials.get("Univ_Gold_Accent")
    mat_lamp_glow = bpy.data.materials.get("Univ_Bankers_Lamp_Glow")
    mat_parquet = bpy.data.materials.get("Univ_Parquet_Wood")
    mat_leather = bpy.data.materials.get("Univ_Burgundy_Leather")

    cx = -126.61
    cy = -236.53
    width_x = 21.92
    sx = -121.2
    sy = cy + 9.0
    cx_room = cx
    cy_commons = cy - 10.0
    cy_lec = cy - 10.0

    # 1. Polish John Purdue's Study:
    # Wall sconces on walnut walls
    for sc_y in [sy - 3.5, sy + 3.5]:
        add_box(f"UNIV_Study_Sconce_W_{int(sc_y)}", col_int, (-126.0, sc_y, 6.2), (0.2, 0.4, 0.6), mat_gold)
        add_cyl(f"UNIV_Study_SconceGlow_W_{int(sc_y)}", col_int, (-125.8, sc_y, 6.2), 0.1, 0.25, mat_lamp_glow)

    # Exposed walnut ceiling beams in Study
    for b_y in range(int(cy + 2.0), int(cy + 17.0), 3):
        add_box(f"UNIV_Study_Ceiling_Beam_{int(b_y)}", col_int, (sx, b_y, 8.05), (9.8, 0.35, 0.3), mat_walnut)

    # 2. Polish Student Commons:
    # Exposed timber ceiling beams
    for b_y in range(int(cy_commons - 8.0), int(cy_commons + 9.0), 4):
        add_box(f"UNIV_Commons_Beam_{int(b_y)}", col_int, (cx_room, b_y, 4.05), (width_x - 1.4, 0.4, 0.3), mat_walnut)
        # Hanging brass pendant lamps
        for b_x in [cx_room - 4.0, cx_room, cx_room + 4.0]:
            add_cyl(f"UNIV_Commons_Pendant_{int(b_x)}_{int(b_y)}", col_int, (b_x, b_y, 3.4), 0.25, 0.2, mat_gold)
            add_cyl(f"UNIV_Commons_PendantGlow_{int(b_x)}_{int(b_y)}", col_int, (b_x, b_y, 3.3), 0.18, 0.08, mat_lamp_glow)

    # 3. Polish Historic Lecture Hall:
    # Center aisle cutting through bench tiers
    for bi in range(4):
        # Aisle opening: remove center of bench seat and replace with L and R benches
        old_seat = bpy.data.objects.get(f"UNIV_Lecture_BenchSeat_{bi}")
        if old_seat:
            bpy.data.objects.remove(old_seat, do_unlink=True)
        old_back = bpy.data.objects.get(f"UNIV_Lecture_BenchBack_{bi}")
        if old_back:
            bpy.data.objects.remove(old_back, do_unlink=True)
        old_desk = bpy.data.objects.get(f"UNIV_Lecture_DeskShelf_{bi}")
        if old_desk:
            bpy.data.objects.remove(old_desk, do_unlink=True)

        b_y = cy_lec + 4.0 - bi * 2.2
        b_z = 8.4 + bi * 0.35
        w_side = 5.6
        # Left side bench
        add_box(f"UNIV_Lec_BenchSeat_L_{bi}", col_int, (cx_room - 3.6, b_y + 0.3, b_z + 0.48), (w_side, 0.45, 0.08), mat_walnut)
        add_box(f"UNIV_Lec_BenchBack_L_{bi}", col_int, (cx_room - 3.6, b_y + 0.52, b_z + 0.85), (w_side, 0.08, 0.65), mat_walnut)
        add_box(f"UNIV_Lec_DeskShelf_L_{bi}", col_int, (cx_room - 3.6, b_y - 0.4, b_z + 0.76), (w_side, 0.4, 0.06), mat_walnut)
        # Right side bench
        add_box(f"UNIV_Lec_BenchSeat_R_{bi}", col_int, (cx_room + 3.6, b_y + 0.3, b_z + 0.48), (w_side, 0.45, 0.08), mat_walnut)
        add_box(f"UNIV_Lec_BenchBack_R_{bi}", col_int, (cx_room + 3.6, b_y + 0.52, b_z + 0.85), (w_side, 0.08, 0.65), mat_walnut)
        add_box(f"UNIV_Lec_DeskShelf_R_{bi}", col_int, (cx_room + 3.6, b_y - 0.4, b_z + 0.76), (w_side, 0.4, 0.06), mat_walnut)

    # 4. Refine Lighting Intensities:
    l_desk = bpy.data.objects.get("UNIV_Light_Study_DeskSpot")
    if l_desk:
        l_desk.data.energy = 850.0
    l_chand = bpy.data.objects.get("UNIV_Light_Study_Chandelier")
    if l_chand:
        l_chand.data.energy = 1800.0
    l_port = bpy.data.objects.get("UNIV_Light_Study_PortraitSpot")
    if l_port:
        l_port.data.energy = 650.0

    # 5. Precision Camera Framing:
    # Cam 52: Step back along Memorial Mall to frame John Purdue's grave, statue, entrance, and full cupola spire
    cam52 = bpy.data.objects.get("Cam_52_University_Hall_East_MemorialMall_StreetView")
    cam52.location = Vector((-78.0, cy - 6.0, 3.6))
    point_at(cam52, Vector((-120.0, cy, 9.5)))
    cam52.data.lens = 20.0

    # Cam 53: John Purdue's Study Interior (looking at desk, banker's lamp, portrait, and bookcases)
    cam53 = bpy.data.objects.get("Cam_53_University_Hall_JohnPurdue_Study_Interior")
    cam53.location = Vector((sx - 2.8, sy - 3.8, 5.4))
    point_at(cam53, Vector((sx + 1.0, sy + 0.8, 5.3)))
    cam53.data.lens = 19.0

    # Cam 54: Student Study Commons (3/4 angle across oak tables and banker's lamps)
    cam54 = bpy.data.objects.get("Cam_54_University_Hall_Student_Study_Commons_Interior")
    cam54.location = Vector((cx_room - 6.5, cy_commons - 7.5, 2.0))
    point_at(cam54, Vector((cx_room + 0.5, cy_commons + 1.0, 1.4)))
    cam54.data.lens = 19.0

    # Cam 55: Historic Lecture Hall (3/4 theatrical angle from rear corner toward dais and chalkboard)
    cam55 = bpy.data.objects.get("Cam_55_University_Hall_Historic_LectureHall_Interior")
    cam55.location = Vector((cx_room - 5.5, cy_lec - 4.5, 10.6))
    point_at(cam55, Vector((cx_room, cy_lec + 6.5, 9.5)))
    cam55.data.lens = 19.0

    # Cam 56: Founders Park Aerial
    cam56 = bpy.data.objects.get("Cam_56_University_Hall_FoundersPark_Aerial")
    cam56.location = Vector((-68.0, -295.0, 40.0))
    point_at(cam56, Vector((cx, cy, 11.0)))
    cam56.data.lens = 28.0

    bpy.context.view_layer.update()
    bpy.ops.wm.save_mainfile()
    print("University Hall refined and saved successfully!")

if __name__ == "__main__":
    refine_university_hall()
