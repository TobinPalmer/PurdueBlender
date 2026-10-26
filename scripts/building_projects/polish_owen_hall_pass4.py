import bpy
import bmesh
import mathutils
import math

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

def create_cylinder(name, loc, radius, depth, mat=None, col=None, verts=20):
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

def apply_owen_pass4_polish():
    print("=== APPLYING PASS 4 ARCHITECTURAL POLISH TO RICHARD OWEN HALL ===")

    col_ext = bpy.data.collections.get("20_Owen_Hall_Exterior")
    col_int = bpy.data.collections.get("21_Owen_Hall_Interiors")
    col_site = bpy.data.collections.get("22_Owen_Hall_Courtyards_and_Site")

    mat_glass = bpy.data.materials.get("Beering_Solar_Ribbon_Glass") or bpy.data.materials.get("Owen_Window_Glass")
    mat_limestone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_dark_oak = bpy.data.materials.get("Beering_Executive_Dark_Oak")
    mat_steel = bpy.data.materials.get("Tark_Stainless_Steel") or bpy.data.materials.get("Owen_Stainless_Steel")
    mat_black_paint = bpy.data.materials.get("Purdue_Polished_Black_Granite")

    oc_x, oc_y = -594.0, 539.1

    # -------------------------------------------------------------
    # 1. NORTH COURTYARD INNER WING FENESTRATION DENSITY
    # -------------------------------------------------------------
    # Add windows with limestone sills along the inner courtyard-facing flanks of NW and NE wings
    # NW wing inner east wall: X = oc_x - 18.55 = -612.55
    # NE wing inner west wall: X = oc_x + 18.55 = -575.45
    for wing_side, wx in [("NW_Inner_East", oc_x - 18.55), ("NE_Inner_West", oc_x + 18.55)]:
        for y_i, y_pos in enumerate([oc_y + 22.0, oc_y + 30.0, oc_y + 38.0]):
            for fl_i, fl_z in enumerate([5.8, 9.6, 13.4]):
                create_box(
                    f"Owen_{wing_side}_Win_{y_i}_{fl_i}",
                    loc=(wx, y_pos, fl_z),
                    size=(0.22, 2.0, 1.8),
                    mat=mat_glass,
                    col=col_ext
                )
                create_box(
                    f"Owen_{wing_side}_Sill_{y_i}_{fl_i}",
                    loc=(wx + (0.1 if "NW" in wing_side else -0.1), y_pos, fl_z - 0.98),
                    size=(0.35, 2.2, 0.16),
                    mat=mat_limestone,
                    col=col_ext
                )
    print("North courtyard inner wing fenestration installed (18 additional window bays).")

    # -------------------------------------------------------------
    # 2. EXTERIOR BICYCLE PARKING HOOPS (TWO BANKS OF 6 RACKS)
    # -------------------------------------------------------------
    # Bank 1: Near North Portico entrance steps
    for b1_i in range(6):
        rx = oc_x - 14.0 + b1_i * 1.1
        ry = oc_y + 24.5
        # Inverted-U rack
        create_cylinder(f"Owen_North_BikeRack_PostL_{b1_i}", loc=(rx - 0.35, ry, 0.45), radius=0.035, depth=0.9, mat=mat_black_paint, col=col_site)
        create_cylinder(f"Owen_North_BikeRack_PostR_{b1_i}", loc=(rx + 0.35, ry, 0.45), radius=0.035, depth=0.9, mat=mat_black_paint, col=col_site)
        create_box(f"Owen_North_BikeRack_Top_{b1_i}", loc=(rx, ry, 0.90), size=(0.76, 0.07, 0.07), mat=mat_black_paint, col=col_site)

    # Bank 2: Along East Courtyard concourse
    for b2_i in range(6):
        rx = oc_x + 38.0
        ry = oc_y - 8.0 + b2_i * 1.1
        create_cylinder(f"Owen_East_BikeRack_PostL_{b2_i}", loc=(rx, ry - 0.35, 0.45), radius=0.035, depth=0.9, mat=mat_black_paint, col=col_site)
        create_cylinder(f"Owen_East_BikeRack_PostR_{b2_i}", loc=(rx, ry + 0.35, 0.45), radius=0.035, depth=0.9, mat=mat_black_paint, col=col_site)
        create_box(f"Owen_East_BikeRack_Top_{b2_i}", loc=(rx, ry, 0.90), size=(0.07, 0.76, 0.07), mat=mat_black_paint, col=col_site)
    print("Exterior bicycle parking racks installed at North portico and East courtyard.")

    # -------------------------------------------------------------
    # 3. ROOM 216 DETAIL POLISH (BASEBOARD & STUDY PROPS)
    # -------------------------------------------------------------
    rm_cx = oc_x - 34.0
    rm_cy = oc_y - 36.0

    # Baseboard mouldings along North, South, East walls
    create_box("Owen_Dorm216_Baseboard_N", loc=(rm_cx, rm_cy + 2.1, 0.14), size=(5.5, 0.06, 0.12), mat=mat_dark_oak, col=col_int)
    create_box("Owen_Dorm216_Baseboard_S", loc=(rm_cx, rm_cy - 2.1, 0.14), size=(5.5, 0.06, 0.12), mat=mat_dark_oak, col=col_int)
    create_box("Owen_Dorm216_Baseboard_E", loc=(rm_cx + 2.7, rm_cy, 0.14), size=(0.06, 4.2, 0.12), mat=mat_dark_oak, col=col_int)

    # Desk study props (laptop and textbooks)
    for d_i, d_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        # Open laptop with glowing screen
        create_box(f"Owen_Dorm216_Laptop_Base_{d_i}", loc=(rm_cx + 1.5, d_y, 0.77), size=(0.35, 0.25, 0.02), mat=mat_steel, col=col_int)
        create_box(f"Owen_Dorm216_Laptop_Screen_{d_i}", loc=(rm_cx + 1.62, d_y, 0.88), size=(0.02, 0.25, 0.20), mat=mat_steel, col=col_int)
        # Stacked textbooks
        create_box(f"Owen_Dorm216_Books_{d_i}", loc=(rm_cx + 1.9, d_y - 0.25, 0.80), size=(0.24, 0.18, 0.08), mat=mat_dark_oak, col=col_int)
    print("Room 216 baseboards and student desk accessories added.")

    # Save Master Blend File
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master scene successfully saved with Pass 4 polish: {save_path}")

if __name__ == "__main__":
    apply_owen_pass4_polish()
