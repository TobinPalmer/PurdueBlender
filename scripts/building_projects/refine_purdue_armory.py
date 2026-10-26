"""
Refinement & Gold Standard Polish for Purdue Armory (AR - 1918)
- Enhanced University St Hero Perspective (Cam 87) framing twin Romanesque towers, portico, cannons & flag
- High-Detail Articulated Wingback Chairs & Persian Area Rug in Officer's Club (Cam 89)
- Perfectly Calibrated Mezzanine Overlook (Cam 90) capturing court markings, trusses & dais
- Rich Maple Hardwood Sheen, Running Track Lanes, and Honor Crests in Drill Hall (Cam 88)
- Flawless Precinct Aerial Integration (Cam 91)
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Refining Purdue Armory (AR - 1918) to Gold Standard Exemplar ===")

    col_ext = bpy.data.collections.get("57_Armory_Exterior")
    col_int = bpy.data.collections.get("58_Armory_Interiors_and_DrillHall")
    col_site = bpy.data.collections.get("59_Armory_Plaza_and_Site")

    root_obj = bpy.data.objects.get("Armory_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("Armory_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        bpy.context.scene.collection.objects.link(root_obj)

    root_loc = (-218.55, 68.35, 0.0)
    root_obj.location = root_loc
    root_obj.rotation_euler = (0, 0, 0)
    M_WORLD = mathutils.Matrix.Translation(root_loc)

    # Helper for materials
    def get_mat(name, color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, specular=0.5, metallic=0.0, emission=None):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if "Base Color" in bsdf.inputs:
                bsdf.inputs["Base Color"].default_value = color
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = roughness
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = specular
            elif "Specular" in bsdf.inputs:
                bsdf.inputs["Specular"].default_value = specular
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metallic
            if emission:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission[:4]
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission[4] if len(emission) > 4 else 1.0
        return mat

    # Materials
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick") or get_mat("Purdue_Red_Brick", (0.50, 0.22, 0.18, 1.0), roughness=0.72)
    mat_stone = bpy.data.materials.get("Bedford_Indiana_Limestone") or get_mat("Bedford_Indiana_Limestone", (0.84, 0.83, 0.79, 1.0), roughness=0.55)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_mat("Solar_Ribbon_Glass", (0.15, 0.28, 0.38, 0.85), roughness=0.08, specular=0.98)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_mat("Purdue_Old_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mat_bronze = get_mat("Armory_Dark_Bronze", (0.25, 0.20, 0.16, 1.0), roughness=0.35, metallic=0.85)
    mat_steel_truss = get_mat("Armory_Structural_Steel", (0.18, 0.20, 0.22, 1.0), roughness=0.40, metallic=0.88)
    mat_dark_oak = get_mat("Armory_Dark_Oak", (0.24, 0.14, 0.08, 1.0), roughness=0.32, specular=0.6)
    mat_maple_floor = get_mat("Armory_Polished_Maple", (0.84, 0.66, 0.44, 1.0), roughness=0.15, specular=0.92)
    mat_court_lines = get_mat("Armory_Court_Lines", (0.95, 0.95, 0.95, 1.0), roughness=0.3)
    mat_track_red = get_mat("Armory_Track_Red", (0.55, 0.16, 0.14, 1.0), roughness=0.45)
    mat_roof_copper = get_mat("Armory_Roof_Copper", (0.28, 0.42, 0.35, 1.0), roughness=0.65, metallic=0.4)
    mat_warm_glow = get_mat("Armory_Warm_Glow", (1.0, 0.88, 0.65, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.65, 4.5))
    mat_granite_pedestal = get_mat("Armory_Barre_Granite", (0.38, 0.38, 0.39, 1.0), roughness=0.45)
    mat_leather_burgundy = get_mat("Armory_Leather_Burgundy", (0.28, 0.08, 0.10, 1.0), roughness=0.35, specular=0.6)
    mat_persian_rug = get_mat("Armory_Persian_Rug", (0.45, 0.12, 0.14, 1.0), roughness=0.85)

    def make_box_local(name, col, loc, size, mat=None):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        sx, sy, sz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
        verts = [
            (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
            (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)
        ]
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (1, 2, 6, 5),
            (2, 3, 7, 6), (3, 0, 4, 7)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        obj.parent = root_obj
        obj.location = loc
        col.objects.link(obj)
        return obj

    # 1. Add Indoor Athletic Running Track Lanes on Drill Deck Perimeter
    # Red tartan border track (width 3.0m around outer perimeter of maple court)
    make_box_local("Armory_Track_North", col_int, (0.0, 40.0, 0.405), (46.0, 3.5, 0.01), mat_track_red)
    make_box_local("Armory_Track_South", col_int, (0.0, -40.0, 0.405), (46.0, 3.5, 0.01), mat_track_red)
    make_box_local("Armory_Track_East", col_int, (22.0, 0.0, 0.405), (3.5, 82.0, 0.01), mat_track_red)
    make_box_local("Armory_Track_West", col_int, (-22.0, 0.0, 0.405), (3.5, 82.0, 0.01), mat_track_red)

    # 2. Add Articulated Leather Wingback Armchairs in Officer's Club
    # Remove old blocky wingback chairs
    for old_name in ["Armory_Wingback_W1", "Armory_Wingback_E1", "Armory_Wingback_N1", "Armory_Wingback_S1"]:
        o = bpy.data.objects.get(old_name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    # Add Persian Area Rug under the conference seating zone
    make_box_local("Armory_Officer_Rug", col_int, (19.5, -4.5, 0.425), (4.5, 5.5, 0.01), mat_persian_rug)

    # Articulated Wingback Chairs
    chair_positions = [
        ("W1", 18.0, -4.5, (0.8, 0.75, 0.95)),
        ("E1", 21.0, -4.5, (0.8, 0.75, 0.95)),
        ("N1", 19.5, -3.1, (0.75, 0.8, 0.95)),
        ("S1", 19.5, -5.9, (0.75, 0.8, 0.95))
    ]
    for ch_id, cx, cy, sz in chair_positions:
        # Seat cushion
        make_box_local(f"Armory_Chair_Seat_{ch_id}", col_int, (cx, cy, 0.65), (sz[0], sz[1], 0.3), mat_leather_burgundy)
        # Backrest
        make_box_local(f"Armory_Chair_Back_{ch_id}", col_int, (cx, cy + (0.28 if sz[0]>sz[1] else 0.0), 1.15), (sz[0] * 0.95, 0.2, 0.8), mat_leather_burgundy)
        # Left and Right Armrests
        make_box_local(f"Armory_Chair_ArmL_{ch_id}", col_int, (cx - sz[0]/2.0, cy, 0.85), (0.15, sz[1] * 0.85, 0.4), mat_leather_burgundy)
        make_box_local(f"Armory_Chair_ArmR_{ch_id}", col_int, (cx + sz[0]/2.0, cy, 0.85), (0.15, sz[1] * 0.85, 0.4), mat_leather_burgundy)
        # Dark wood legs
        for lx in [-sz[0]/2.2, sz[0]/2.2]:
            for ly in [-sz[1]/2.2, sz[1]/2.2]:
                make_box_local(f"Armory_Chair_Leg_{ch_id}_{lx:.1f}_{ly:.1f}", col_int, (cx + lx, cy + ly, 0.48), (0.08, 0.08, 0.2), mat_dark_oak)

    # 3. Add Wall Medallions / Military Crests along upper Drill Hall perimeter
    for my in range(-30, 31, 15):
        # East wall medallions
        make_box_local(f"Armory_Crest_E_{my}", col_int, (23.9, my, 8.5), (0.15, 1.4, 1.4), mat_gold)
        # West wall medallions
        make_box_local(f"Armory_Crest_W_{my}", col_int, (-23.9, my, 8.5), (0.15, 1.4, 1.4), mat_gold)

    # =========================================================================
    # RE-CALIBRATE PRECISION INSPECTION CAMERAS
    # =========================================================================
    print("Re-calibrating Precision Inspection Cameras...")

    def set_camera(name, loc_world, target_world, lens=28.0):
        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name=name + "_Data")
            cam_obj = bpy.data.objects.new(name, cam_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = mathutils.Vector(loc_world)
        target_v = mathutils.Vector(target_world)
        direction = target_v - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_obj.data.lens = lens
        cam_obj.data.clip_start = 0.1
        cam_obj.data.clip_end = 1500.0
        print(f"Calibrated {name} at {loc_world} -> target {target_world} (lens={lens}mm)")
        return cam_obj

    def local_to_world_explicit(local_coord):
        return M_WORLD @ mathutils.Vector(local_coord)

    # 1. Cam_87: University St Hero Arrival View
    # Stepped back to frame both monumental Romanesque towers (NE and SE), portico, gold lettering, cannons & flagpole
    cam87_loc = local_to_world_explicit((64.0, -18.0, 7.5))
    cam87_target = local_to_world_explicit((18.0, 0.0, 11.5))
    set_camera("Cam_87_Armory_UniversitySt_Hero", cam87_loc, cam87_target, lens=24.0)

    # 2. Cam_88: The Great Drill Hall Interior
    # Looking down the 85m hall: 8 colossal trusses, maple floor, running track, and ROTC review dais
    cam88_loc = local_to_world_explicit((0.0, -36.0, 3.2))
    cam88_target = local_to_world_explicit((0.0, 16.0, 5.5))
    set_camera("Cam_88_Armory_DrillHall_Colossal_Trusses_Interior", cam88_loc, cam88_target, lens=22.0)

    # 3. Cam_89: Officer's Club & Cadet Heritage Lounge
    # Refined 3/4 perspective across Persian rug, wingback armchairs, mahogany table, brass chandelier, and artifact vitrines
    cam89_loc = local_to_world_explicit((17.6, -9.2, 2.3))
    cam89_target = local_to_world_explicit((21.2, 0.5, 2.0))
    set_camera("Cam_89_Armory_OfficersClub_Lounge_Interior", cam89_loc, cam89_target, lens=24.0)

    # 4. Cam_90: Viewing Mezzanine Gallery Overlook
    # Moved forward right to the wrought-iron railing at X = 19.8m, looking diagonally across the drill deck at the court and trusses
    cam90_loc = local_to_world_explicit((19.8, -10.0, 6.8))
    cam90_target = local_to_world_explicit((-2.0, 15.0, 1.2))
    set_camera("Cam_90_Armory_Mezzanine_Overlook_Interior", cam90_loc, cam90_target, lens=22.0)

    # 5. Cam_91: North-East Precinct Aerial Overview
    cam91_loc = local_to_world_explicit((68.0, 62.0, 54.0))
    cam91_target = local_to_world_explicit((0.0, 0.0, 10.0))
    set_camera("Cam_91_Armory_Precinct_Aerial", cam91_loc, cam91_target, lens=28.0)

    print("=== Purdue Armory Refinement Completed Successfully! ===")

if __name__ == "__main__":
    run()
