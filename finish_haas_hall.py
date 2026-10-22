"""
Fast, direct finishing and rendering of Felix Haas Hall (HAAS - 1909)
in C:\\Users\\Tobin\\Documents\\Blender\\purdue_campus_master.blend
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
OUTPUT_DIR = r"C:\Users\Tobin\.gemini\antigravity\brain\7d054314-203a-4c1a-bb2d-ad8b0fc54e25"

def run_finish():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened master blend successfully.")

    col_ext = bpy.data.collections.get("63_Felix_Haas_Hall_Exterior")
    col_int = bpy.data.collections.get("64_Felix_Haas_Hall_Interiors")
    col_site = bpy.data.collections.get("65_Felix_Haas_Hall_Plaza_and_Site")
    col_cams = bpy.data.collections.get("00_Inspection_Cameras")

    root_obj = bpy.data.objects.get("HAAS_Root")

    # Materials
    mat_limestone = bpy.data.materials.get("HAAS_Bedford_Limestone")
    mat_slate = bpy.data.materials.get("HAAS_Slate_Roof")
    mat_copper = bpy.data.materials.get("HAAS_Verdigris_Copper")
    mat_dark_oak = bpy.data.materials.get("HAAS_Dark_Oak")
    mat_gold = bpy.data.materials.get("HAAS_Purdue_Gold") or bpy.data.materials.get("Purdue_Old_Gold")

    # 1. Remove the solid slabs that clipped interiors
    solid_slabs = [
        "HAAS_Water_Table_Base",
        "HAAS_Beltcourse_Floor2",
        "HAAS_Beltcourse_Floor3",
        "HAAS_Cornice_Entablature"
    ]
    # Also remove stepped roof layers
    for r_idx in range(1, 9):
        solid_slabs.append(f"HAAS_Roof_Hip_Layer_{r_idx}")

    for sname in solid_slabs:
        obj = bpy.data.objects.get(sname)
        if obj:
            col_ext.objects.unlink(obj)
            bpy.data.objects.remove(obj)
            print(f"Removed solid slab: {sname}")

    def quick_box(name, col, loc, size, mat=None):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        o = bpy.context.active_object
        o.name = name
        o.scale = size
        if mat:
            o.data.materials.append(mat)
        if root_obj:
            o.parent = root_obj
        if col != bpy.context.scene.collection:
            col.objects.link(o)
            bpy.context.scene.collection.objects.unlink(o)
        return o

    # 2. Add hollow perimeter framing strips
    # Water Table (Z = 0.0 to 1.4m)
    quick_box("HAAS_Water_Table_East", col_ext, (19.8, 0, 0.7), (0.7, 53.4, 1.4), mat_limestone)
    quick_box("HAAS_Water_Table_West", col_ext, (-19.8, 0, 0.7), (0.7, 53.4, 1.4), mat_limestone)
    quick_box("HAAS_Water_Table_North", col_ext, (0, 26.35, 0.7), (39.0, 0.7, 1.4), mat_limestone)
    quick_box("HAAS_Water_Table_South", col_ext, (0, -26.35, 0.7), (39.0, 0.7, 1.4), mat_limestone)

    # Beltcourse Floor 2 (Z = 4.3m)
    quick_box("HAAS_Beltcourse2_East", col_ext, (19.8, 0, 4.3), (0.4, 53.2, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse2_West", col_ext, (-19.8, 0, 4.3), (0.4, 53.2, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse2_North", col_ext, (0, 26.4, 4.3), (39.6, 0.4, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse2_South", col_ext, (0, -26.4, 4.3), (39.6, 0.4, 0.35), mat_limestone)

    # Beltcourse Floor 3 (Z = 8.5m)
    quick_box("HAAS_Beltcourse3_East", col_ext, (19.8, 0, 8.5), (0.4, 53.2, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse3_West", col_ext, (-19.8, 0, 8.5), (0.4, 53.2, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse3_North", col_ext, (0, 26.4, 8.5), (39.6, 0.4, 0.35), mat_limestone)
    quick_box("HAAS_Beltcourse3_South", col_ext, (0, -26.4, 8.5), (39.6, 0.4, 0.35), mat_limestone)

    # Cornice (Z = 11.5m)
    quick_box("HAAS_Cornice_East", col_ext, (20.0, 0, 11.5), (0.8, 53.8, 0.6), mat_limestone)
    quick_box("HAAS_Cornice_West", col_ext, (-20.0, 0, 11.5), (0.8, 53.8, 0.6), mat_limestone)
    quick_box("HAAS_Cornice_North", col_ext, (0, 26.6, 11.5), (40.0, 0.8, 0.6), mat_limestone)
    quick_box("HAAS_Cornice_South", col_ext, (0, -26.6, 11.5), (40.0, 0.8, 0.6), mat_limestone)

    # 3. Continuous 4-sided pitched hipped roof mesh
    old_roof = bpy.data.objects.get("HAAS_Hipped_Roof")
    if old_roof:
        col_ext.objects.unlink(old_roof)
        bpy.data.objects.remove(old_roof)

    mesh_data = bpy.data.meshes.new("HAAS_Hipped_Roof_Mesh")
    w2 = 20.1
    l2 = 26.7
    z_base = 11.5
    z_ridge = 15.8
    r_l2 = 13.0
    verts = [
        (-w2, -l2, z_base),
        (w2, -l2, z_base),
        (w2, l2, z_base),
        (-w2, l2, z_base),
        (0.0, -r_l2, z_ridge),
        (0.0, r_l2, z_ridge),
    ]
    faces = [
        (0, 1, 4),
        (1, 2, 5, 4),
        (2, 3, 5),
        (3, 0, 4, 5),
    ]
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()
    roof_obj = bpy.data.objects.new("HAAS_Hipped_Roof", mesh_data)
    roof_obj.parent = root_obj
    if mat_slate:
        roof_obj.data.materials.append(mat_slate)
    col_ext.objects.link(roof_obj)

    # 4. Update Cameras with verified clear lines of sight
    def set_cam(name, loc, rot_deg, lens=22.0):
        c = bpy.data.objects.get(name)
        if not c:
            cd = bpy.data.cameras.new(name=name)
            c = bpy.data.objects.new(name=name, object_data=cd)
            col_cams.objects.link(c)
        c.data.lens = lens
        c.data.clip_start = 0.1
        c.data.clip_end = 1500.0
        c.location = loc
        c.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        return c

    # Cam 97: Hero East Arrival Perspective (Memorial 17 Steps, Carved Portal, Roof, Cupola)
    # Sited at Southeast approach along Memorial Mall walkway looking West-Northwest at 17 steps and portal
    set_cam("Cam_97_HAAS_East_MemorialSteps_Hero", (-180.0, -76.0, 4.2), (86.0, 0.0, 64.0), lens=20.0)

    # Cam 98: 1903 Memorial Rotunda Interior
    # Inside rotunda looking West-Southwest directly at Bronze 1903 Memorial Plaque, vitrines, and chandelier
    set_cam("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", (-208.5, -60.0, 2.3), (88.0, 0.0, 118.0), lens=18.0)

    # Cam 99: Computer Science Collaborative Commons Interior (Floor 2)
    # Looking across maple hardwood floor, exposed riveted steel trusses, coding pods, and whiteboards
    set_cam("Cam_99_HAAS_CS_Commons_Interior", (-234.0, -82.0, 6.8), (82.0, 0.0, -45.0), lens=18.0)

    # Cam 100: Felix Haas Faculty & Graduate Seminar Suite Interior (Floor 3)
    # Looking towards walnut table, banker's lamps, and portrait of Felix Haas
    set_cam("Cam_100_HAAS_Faculty_Seminar_Interior", (-236.0, -70.0, 10.85), (86.0, 0.0, -35.0), lens=20.0)

    # Cam 101: Precinct Aerial Context
    # Elevated overview showing full Beaux-Arts pavilion, hipped slate roof, copper cupola, 17 steps, Armory and MATH integration
    set_cam("Cam_101_HAAS_Precinct_Aerial", (-155.0, -120.0, 58.0), (56.0, 0.0, 34.0), lens=22.0)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master blend file updated and saved successfully in Documents\\Blender!")

    # 5. Render All 5 Inspection Cameras
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, "RenderEngineEEVEENext") else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    if scene.world and scene.world.node_tree:
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.75, 0.85, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 1.0

    cams_to_render = [
        ("Cam_97_HAAS_East_MemorialSteps_Hero", "haas_cam97_east_memorialsteps_hero.png"),
        ("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", "haas_cam98_rotunda_1903_memorial.png"),
        ("Cam_99_HAAS_CS_Commons_Interior", "haas_cam99_cs_commons_interior.png"),
        ("Cam_100_HAAS_Faculty_Seminar_Interior", "haas_cam100_faculty_seminar_interior.png"),
        ("Cam_101_HAAS_Precinct_Aerial", "haas_cam101_precinct_aerial.png"),
    ]

    for cam_name, out_file in cams_to_render:
        c_obj = bpy.data.objects.get(cam_name)
        if not c_obj:
            print(f"Camera {cam_name} not found!")
            continue
        scene.camera = c_obj
        out_path = os.path.join(OUTPUT_DIR, out_file)
        scene.render.filepath = out_path
        print(f"Rendering {cam_name} -> {out_path}...")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {cam_name} successfully!")

if __name__ == "__main__":
    run_finish()
