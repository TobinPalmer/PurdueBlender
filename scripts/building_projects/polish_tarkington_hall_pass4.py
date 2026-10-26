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

def create_cylinder(name, loc, radius, depth, mat=None, col=None, verts=24):
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

def apply_tarkington_pass4_polish():
    print("=== APPLYING PASS 4 ARCHITECTURAL POLISH TO TARKINGTON HALL ===")

    col_ext = bpy.data.collections.get("17_Tarkington_Hall_Exterior")
    col_int = bpy.data.collections.get("18_Tarkington_Hall_Interiors")
    col_site = bpy.data.collections.get("19_Tarkington_Hall_Courtyards_and_Site")

    mat_glass = bpy.data.materials.get("Beering_Solar_Ribbon_Glass") or bpy.data.materials.get("Tark_Window_Glass")
    mat_limestone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_bronze = bpy.data.materials.get("Tark_Architectural_Bronze")
    mat_steel = bpy.data.materials.get("Tark_Stainless_Steel")
    mat_oak = bpy.data.materials.get("Beering_Honey_Oak_Woodwork")
    mat_dark_oak = bpy.data.materials.get("Beering_Executive_Dark_Oak")

    tc_x, tc_y = -595.0, 353.0

    # -------------------------------------------------------------
    # 1. FIX DORM 118 WARDROBE OCCLUSION
    # -------------------------------------------------------------
    # In Dorm 118, move Tark_Dorm_Wardrobes away from the west window
    # to the south interior partition wall, opening the window and box fans completely!
    rm_cx = tc_x - 34.0 # -629.0
    rm_cy = tc_y - 36.0 # 317.0
    
    wardrobe = bpy.data.objects.get("Tark_Dorm_Wardrobes")
    if wardrobe:
        # Reposition against the south wall at (rm_cx, rm_cy - 1.7, 1.4)
        wardrobe.location = (rm_cx + 0.2, rm_cy - 1.8, 1.4)
        wardrobe.dimensions = (1.8, 0.65, 2.2)
        print("Dorm 118 wardrobe relocated to south interior wall; window wall cleared.")

    # -------------------------------------------------------------
    # 2. COMMONS SOUTH FACADE CURTAIN WALL BAYS (ABOVE PORTICO)
    # -------------------------------------------------------------
    # Add three 3-story vertical glazed curtain wall bays above South portico (z = 4.0 to 14.5m)
    for bay_i, bay_x in enumerate([-598.0, -595.0, -592.0]):
        bay_w = 2.2 if bay_x == -595.0 else 1.8
        # Glazed curtain bay
        create_box(
            f"Tark_South_Portal_CurtainBay_Glass_{bay_i}",
            loc=(bay_x, tc_y - 28.1, 9.2),
            size=(bay_w, 0.22, 9.8),
            mat=mat_glass,
            col=col_ext
        )
        # Vertical Limestone Pier Trim
        create_box(
            f"Tark_South_Portal_CurtainBay_Frame_{bay_i}",
            loc=(bay_x, tc_y - 28.08, 9.2),
            size=(bay_w + 0.25, 0.32, 10.1),
            mat=mat_limestone,
            col=col_ext
        )
    print("South facade multi-story curtain wall bays installed above portico.")

    # -------------------------------------------------------------
    # 3. EAST COURTYARD CONNECTOR WALL WINDOWS
    # -------------------------------------------------------------
    # Add double-casement window bays on the East wall of Commons facing East Courtyard
    # X = tc_x + 18.0 = -577.0, Y in [tc_y - 10.0, tc_y + 10.0]
    for ey_i, ey_pos in enumerate([-8.0, -3.0, 3.0, 8.0]):
        for fl_i, fl_z in enumerate([5.8, 9.6, 13.4]):
            create_box(
                f"Tark_East_Courtyard_Connector_Win_{ey_i}_{fl_i}",
                loc=(tc_x + 18.05, tc_y + ey_pos, fl_z),
                size=(0.22, 2.4, 1.8),
                mat=mat_glass,
                col=col_ext
            )
            create_box(
                f"Tark_East_Courtyard_Connector_Sill_{ey_i}_{fl_i}",
                loc=(tc_x + 18.15, tc_y + ey_pos, fl_z - 0.98),
                size=(0.35, 2.6, 0.16),
                mat=mat_limestone,
                col=col_ext
            )
    print("East courtyard connector wall fenestration added.")

    # -------------------------------------------------------------
    # 4. INTERIOR LIGHTING OVERHAUL (PETE'S ZA, SHARK TANK, LOBBY, DORM)
    # -------------------------------------------------------------
    # Remove old lights if any
    for o in list(bpy.data.objects):
        if "Tark_Light_" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    # A. Pete's Za Interior Downlights (4 Ceiling Points)
    pz_cx, pz_cy = tc_x - 8.5, tc_y + 3.0
    for pz_li, (lx, ly) in enumerate([
        (pz_cx - 3.5, pz_cy - 2.0),
        (pz_cx + 3.5, pz_cy - 2.0),
        (pz_cx - 3.5, pz_cy + 3.5),
        (pz_cx + 3.5, pz_cy + 3.5)
    ]):
        ldata = bpy.data.lights.new(f"Tark_Light_PetesZa_{pz_li}", "POINT")
        ldata.energy = 220.0
        ldata.color = (1.0, 0.94, 0.85)
        lobj = bpy.data.objects.new(f"Tark_Light_PetesZa_{pz_li}", ldata)
        lobj.location = (lx, ly, 3.4)
        col_int.objects.link(lobj)

    # Supercharge Pete's Za Sign Emission
    mat_sign = bpy.data.materials.get("Tark_PetesZa_Red_Sign")
    if mat_sign and mat_sign.use_nodes:
        bsdf = next((n for n in mat_sign.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf and "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 8.5
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (1.0, 0.12, 0.08, 1.0)

    # Pete's Za 6 High-Top Swivel Barstools
    for t_i, (tx, ty) in enumerate([(pz_cx + 4.0, pz_cy - 1.0), (pz_cx + 4.0, pz_cy + 3.0)]):
        for s_i, ang_deg in enumerate([0, 120, 240]):
            rad = math.radians(ang_deg)
            sx = tx + 0.95 * math.cos(rad)
            sy = ty + 0.95 * math.sin(rad)
            create_cylinder(f"Tark_PetesZa_Barstool_Seat_{t_i}_{s_i}", loc=(sx, sy, 0.72), radius=0.22, depth=0.08, mat=mat_dark_oak, col=col_int)
            create_cylinder(f"Tark_PetesZa_Barstool_Stem_{t_i}_{s_i}", loc=(sx, sy, 0.36), radius=0.04, depth=0.72, mat=mat_steel, col=col_int)

    # B. Shark Tank Downward Billiard Spots & Ambient Lights
    st_cx, st_cy = tc_x + 8.5, tc_y + 3.0
    for pool_i, pool_y in enumerate([st_cy - 2.5, st_cy + 4.5]):
        # Downward spotlight focused directly on green felt
        sdata = bpy.data.lights.new(f"Tark_Light_SharkTank_PoolSpot_{pool_i}", "SPOT")
        sdata.energy = 450.0
        sdata.color = (1.0, 0.97, 0.92)
        sdata.spot_size = math.radians(65.0)
        sdata.spot_blend = 0.25
        sobj = bpy.data.objects.new(f"Tark_Light_SharkTank_PoolSpot_{pool_i}", sdata)
        sobj.location = (st_cx - 2.2, pool_y, 2.5)
        sobj.rotation_euler = (0.0, 0.0, 0.0)
        col_int.objects.link(sobj)

    # Gaming & Lounge Area Warm Ambient Point Light
    gdata = bpy.data.lights.new("Tark_Light_SharkTank_GamingAmbient", "POINT")
    gdata.energy = 260.0
    gdata.color = (1.0, 0.92, 0.82)
    gobj = bpy.data.objects.new("Tark_Light_SharkTank_GamingAmbient", gdata)
    gobj.location = (st_cx + 4.5, st_cy + 3.0, 3.3)
    col_int.objects.link(gobj)

    # C. Main Lobby Terrazzo Ceiling Lights
    lb_cx, lb_cy = tc_x, tc_y - 18.0
    for lb_li, (lx, ly) in enumerate([(lb_cx - 4.5, lb_cy), (lb_cx + 4.5, lb_cy), (lb_cx, lb_cy + 4.0)]):
        ldata = bpy.data.lights.new(f"Tark_Light_Lobby_{lb_li}", "POINT")
        ldata.energy = 280.0
        ldata.color = (1.0, 0.96, 0.90)
        lobj = bpy.data.objects.new(f"Tark_Light_Lobby_{lb_li}", ldata)
        lobj.location = (lx, ly, 3.4)
        col_int.objects.link(lobj)

    # D. Dorm 118 Ceiling Downlight & Study Lamps
    ddata = bpy.data.lights.new("Tark_Light_Dorm118_Ceiling", "POINT")
    ddata.energy = 160.0
    ddata.color = (1.0, 0.95, 0.88)
    dobj = bpy.data.objects.new("Tark_Light_Dorm118_Ceiling", ddata)
    dobj.location = (rm_cx, rm_cy, 3.2)
    col_int.objects.link(dobj)

    for dl_i, dl_y in enumerate([rm_cy - 1.2, rm_cy + 1.2]):
        s_ldata = bpy.data.lights.new(f"Tark_Light_Desk_{dl_i}", "POINT")
        s_ldata.energy = 45.0
        s_ldata.color = (1.0, 0.98, 0.92)
        s_lobj = bpy.data.objects.new(f"Tark_Light_Desk_{dl_i}", s_ldata)
        s_lobj.location = (rm_cx + 1.5, dl_y, 1.6)
        col_int.objects.link(s_lobj)

    print("Comprehensive interior lighting and downlight fixtures installed.")

    # Save Master Blend File
    save_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
    bpy.ops.wm.save_mainfile(filepath=save_path)
    print(f"Master scene successfully saved with Pass 4 polish: {save_path}")

if __name__ == "__main__":
    apply_tarkington_pass4_polish()
