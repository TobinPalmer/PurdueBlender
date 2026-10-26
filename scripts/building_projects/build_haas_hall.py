"""
Purdue University Digital Twin - Felix Haas Hall (HAAS - 1909 / Memorial Gymnasium) Builder
Location: 201 N. University St, West Lafayette, IN (Center: X = -221.45m, Y = -64.02m, Z = 0.0m)
Bounds: X in [-241.26, -201.64] (39.62m), Y in [-90.43, -37.61] (52.82m), Z in [0.00, 16.00m]
Architect: Mauran, Russell & Garden (1909) / Renamed 2006 for Provost Felix Haas.
Features:
- Beaux-Arts Classical Revival pavilion in Purdue Red Brick & Bedford Limestone
- The Legendary 17 Steps on the East Entrance (11 steps + landing + 6 steps) commemorating the 1903 Purdue Wreck
- Carved Limestone Portal Arch "MEMORIAL GYMNASIUM" & West Signage "FELIX HAAS HALL"
- Octagonal Oxidized Copper Cupola Spire (Z = 19.2m)
- 1903 Memorial Rotunda with Bronze Plaque, Trophy Vitrines, & Twin Oak Stairs
- 2nd-Floor Computer Science Collaborative Commons with Exposed Steel Trusses & Coding Pods
- 3rd-Floor Felix Haas Seminar Room with Portrait & Walnut Conference Suite
- 5 Calibrated Inspection Cameras Cam_97 through Cam_101
"""

import bpy
import math
import mathutils

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

def run_build():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened master blend successfully for Felix Haas Hall.")

    # 1. Purge / remove old placeholder
    massing_col = bpy.data.collections.get("02_Campus_Buildings_Massing")
    old_placeholder = bpy.data.objects.get("Haas (Felix) Hall (HAAS)")
    if old_placeholder and massing_col:
        print(f"Removing old placeholder: {old_placeholder.name}")
        massing_col.objects.unlink(old_placeholder)
        bpy.data.objects.remove(old_placeholder, do_unlink=True)

    # 2. Setup Collections
    def get_or_create_col(name, parent=None):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            if parent:
                parent.children.link(col)
            else:
                bpy.context.scene.collection.children.link(col)
        return col

    col_ext = get_or_create_col("63_Felix_Haas_Hall_Exterior")
    col_int = get_or_create_col("64_Felix_Haas_Hall_Interiors")
    col_site = get_or_create_col("65_Felix_Haas_Hall_Plaza_and_Site")
    col_cams = get_or_create_col("00_Inspection_Cameras")

    for c in [col_ext, col_int, col_site]:
        for o in list(c.objects):
            c.objects.unlink(o)
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Create Root Anchor
    root_obj = bpy.data.objects.new("HAAS_Root", None)
    root_obj.location = (-221.45, -64.02, 0.0)
    col_ext.objects.link(root_obj)

    # 4. Materials Setup
    def get_or_create_mat(name, color, roughness=0.5, metallic=0.0, transmission=0.0, emission=None, emission_strength=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if not bsdf:
                bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = transmission
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = transmission
            if emission:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission
        return mat

    mat_brick = bpy.data.materials.get("Purdue_Red_Brick") or get_or_create_mat("HAAS_Purdue_Red_Brick", (0.38, 0.14, 0.10, 1.0), roughness=0.75)
    mat_limestone = get_or_create_mat("HAAS_Bedford_Limestone", (0.84, 0.82, 0.77, 1.0), roughness=0.55)
    mat_slate_roof = get_or_create_mat("HAAS_Slate_Roof", (0.22, 0.24, 0.26, 1.0), roughness=0.65)
    mat_copper = get_or_create_mat("HAAS_Verdigris_Copper", (0.28, 0.58, 0.48, 1.0), roughness=0.45)
    mat_dark_oak = get_or_create_mat("HAAS_Dark_Oak", (0.16, 0.09, 0.05, 1.0), roughness=0.35)
    mat_honey_oak = get_or_create_mat("HAAS_Honey_Oak", (0.58, 0.40, 0.20, 1.0), roughness=0.32)
    mat_maple_floor = get_or_create_mat("HAAS_Maple_Hardwood", (0.68, 0.52, 0.32, 1.0), roughness=0.22)
    mat_terrazzo = get_or_create_mat("HAAS_Terrazzo_Cream", (0.86, 0.84, 0.80, 1.0), roughness=0.18)
    mat_terrazzo_dark = get_or_create_mat("HAAS_Terrazzo_Charcoal", (0.22, 0.22, 0.24, 1.0), roughness=0.22)
    mat_bronze = bpy.data.materials.get("Elliott_ArtDeco_Bronze") or get_or_create_mat("HAAS_Dark_Bronze", (0.20, 0.16, 0.12, 1.0), roughness=0.35, metallic=0.85)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_or_create_mat("HAAS_Purdue_Gold", (0.85, 0.68, 0.22, 1.0), roughness=0.25, metallic=0.90)
    mat_steel = get_or_create_mat("HAAS_Structural_Steel", (0.18, 0.20, 0.22, 1.0), roughness=0.40, metallic=0.80)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_or_create_mat("HAAS_Window_Glass", (0.04, 0.07, 0.12, 1.0), roughness=0.05, transmission=0.88)
    mat_plaque = get_or_create_mat("HAAS_Memorial_Bronze_Plaque", (0.45, 0.32, 0.15, 1.0), roughness=0.30, metallic=0.85)
    mat_whiteboard = get_or_create_mat("HAAS_Whiteboard", (0.95, 0.95, 0.95, 1.0), roughness=0.20)
    mat_screen = get_or_create_mat("HAAS_Screen_Emissive", (0.20, 0.40, 0.70, 1.0), roughness=0.30, emission=(0.30, 0.60, 1.0, 1.0), emission_strength=2.0)
    mat_leather = get_or_create_mat("HAAS_Leather_Burgundy", (0.24, 0.04, 0.06, 1.0), roughness=0.38)
    mat_persian_rug = get_or_create_mat("HAAS_Persian_Rug", (0.35, 0.08, 0.10, 1.0), roughness=0.85)
    mat_green_glass = get_or_create_mat("HAAS_Bankers_Green_Glass", (0.02, 0.35, 0.12, 1.0), roughness=0.15, transmission=0.75, emission=(0.05, 0.60, 0.20, 1.0), emission_strength=2.2)
    mat_brass = get_or_create_mat("HAAS_Polished_Brass", (0.90, 0.75, 0.30, 1.0), roughness=0.20, metallic=0.95)

    def create_box(name, col, loc, size, mat=None, parent=root_obj):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        if col != bpy.context.scene.collection:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        return obj

    def create_cylinder(name, col, loc, radius, depth, mat=None, parent=root_obj, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        if col != bpy.context.scene.collection:
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
        return obj

    print("Building 63_Felix_Haas_Hall_Exterior...")

    # Bounding Box Reference:
    # Center: X = -221.45, Y = -64.02, Z = 0.0
    # Width X = 39.62m -> local X in [-19.81, +19.81]
    # Length Y = 52.82m -> local Y in [-26.41, +26.41]
    # Height Z = 16.00m (eaves at 11.5m, roof ridge at 15.5m, cupola at 19.2m)

    # 1. Continuous Bedford Limestone Water Table Base (Z = 0.0 to 1.4m)
    create_box("HAAS_Water_Table_Base", col_ext, (0, 0, 0.7), (40.2, 53.4, 1.4), mat_limestone)

    # 2. Main Beaux-Arts Brick Pavilion Envelope (Z = 1.4m to 11.5m)
    # Exterior perimeter brick walls (0.6m thickness)
    create_box("HAAS_Brick_Wall_East", col_ext, (19.5, 0, 6.45), (0.6, 52.8, 10.1), mat_brick)
    create_box("HAAS_Brick_Wall_West", col_ext, (-19.5, 0, 6.45), (0.6, 52.8, 10.1), mat_brick)
    create_box("HAAS_Brick_Wall_North", col_ext, (0, 26.1, 6.45), (39.6, 0.6, 10.1), mat_brick)
    create_box("HAAS_Brick_Wall_South", col_ext, (0, -26.1, 6.45), (39.6, 0.6, 10.1), mat_brick)

    # Horizontal Limestone Beltcourses
    create_box("HAAS_Beltcourse_Floor2", col_ext, (0, 0, 4.3), (40.0, 53.2, 0.35), mat_limestone)
    create_box("HAAS_Beltcourse_Floor3", col_ext, (0, 0, 8.5), (40.0, 53.2, 0.35), mat_limestone)

    # Classical Limestone Cornice & Entablature with Dentils (Z = 11.5m)
    create_box("HAAS_Cornice_Entablature", col_ext, (0, 0, 11.5), (40.6, 53.8, 0.6), mat_limestone)

    # Corner Brick Pilasters with Carved Limestone Capitals (NE, NW, SE, SW)
    for px, py in [(-19.5, -26.1), (-19.5, 26.1), (19.5, -26.1), (19.5, 26.1)]:
        create_box(f"HAAS_Corner_Pilaster_{px}_{py}", col_ext, (px, py, 6.45), (1.4, 1.4, 10.1), mat_brick)
        create_box(f"HAAS_Corner_Capital_{px}_{py}", col_ext, (px, py, 11.4), (1.6, 1.6, 0.5), mat_limestone)

    # 3. Monumental East Entrance (Memorial Portal & The Legendary 17 Steps)
    # Sited on East Facade facing campus lawn: Local X = +19.81m
    # Portal Pavilion: 9.5m wide x 3.0m deep x 10.0m high
    create_box("HAAS_East_Portal_Stone_Pavilion", col_ext, (21.0, 0, 5.8), (2.8, 10.5, 9.6), mat_limestone)
    # Arched entrance opening through portal
    create_box("HAAS_East_Portal_Arch_Moulding", col_ext, (21.8, 0, 6.2), (1.2, 5.5, 7.8), mat_limestone)
    create_box("HAAS_East_Portal_Pediment", col_ext, (21.5, 0, 10.8), (2.4, 11.0, 1.4), mat_limestone)

    # Inscription on East Portal: "MEMORIAL GYMNASIUM"
    bpy.ops.object.text_add(location=(22.5, 3.4, 9.6), rotation=(math.pi/2, 0, -math.pi/2))
    txt = bpy.context.active_object
    txt.name = "HAAS_Portal_Inscription"
    txt.data.body = "MEMORIAL GYMNASIUM"
    txt.data.size = 0.38
    txt.data.extrude = 0.05
    txt.data.materials.append(mat_gold)
    txt.parent = root_obj
    col_ext.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # THE LEGENDARY 17 MEMORIAL STEPS:
    # 11 steps leading from plaza grade (Z=0) up to intermediate landing (Z=1.65m)
    # Intermediate landing: 4.5m x 9.5m at Z = 1.65m
    # 6 steps leading from intermediate landing through portal into rotunda floor (Z=2.55m)
    # Total = 11 + 6 = 17 steps!
    for s_idx in range(11):
        step_z = 0.15 * (s_idx + 1)
        step_x = 28.5 - s_idx * 0.55
        create_box(f"HAAS_Step_Lower_{s_idx+1}", col_ext, (step_x, 0, step_z / 2.0), (0.55, 9.5, step_z), mat_limestone)

    # Intermediate Memorial Landing (Z = 1.65m)
    create_box("HAAS_Memorial_Landing", col_ext, (22.2, 0, 0.825), (4.5, 9.5, 1.65), mat_limestone)

    # 6 Upper Steps (from landing into doorway)
    for s_idx in range(6):
        step_z = 1.65 + 0.15 * (s_idx + 1)
        step_x = 20.8 - s_idx * 0.45
        create_box(f"HAAS_Step_Upper_{s_idx+1}", col_ext, (step_x, 0, step_z / 2.0), (0.45, 6.0, step_z), mat_limestone)

    # Flanking Limestone Cheek Walls with Carved Scrolls and Bronze Urns
    for cy, cside in [(-5.0, "South"), (5.0, "North")]:
        create_box(f"HAAS_Cheek_Wall_{cside}", col_ext, (25.5, cy, 1.4), (7.0, 0.8, 2.8), mat_limestone)
        create_cylinder(f"HAAS_Urn_Base_{cside}", col_ext, (28.5, cy, 2.95), radius=0.45, depth=0.3, mat=mat_limestone)
        create_cylinder(f"HAAS_Urn_Bowl_{cside}", col_ext, (28.5, cy, 3.4), radius=0.40, depth=0.6, mat=mat_bronze)
        create_cylinder(f"HAAS_Urn_Boxwood_{cside}", col_ext, (28.5, cy, 3.85), radius=0.35, depth=0.45, mat=mat_copper)

    # Double Dark Oak Entrance Doors with Bronze Hardware on East Portal
    create_box("HAAS_East_Door_Leaves", col_ext, (19.4, 0, 3.8), (0.15, 3.4, 2.6), mat_dark_oak)
    create_box("HAAS_East_Door_Transom", col_ext, (19.4, 0, 5.4), (0.12, 3.4, 1.2), mat_glass)
    for dy in [-0.6, 0.6]:
        create_cylinder(f"HAAS_East_Door_Pull_{dy}", col_ext, (19.48, dy, 3.8), radius=0.03, depth=0.8, mat=mat_gold)

    # 4. West Entrance (University Street Frontage)
    # Sited on West Facade: Local X = -19.81m
    create_box("HAAS_West_Portico_Canopy", col_ext, (-21.5, 0, 4.4), (3.6, 8.5, 0.4), mat_limestone)
    for py in [-3.8, 3.8]:
        create_box(f"HAAS_West_Pier_{py}", col_ext, (-21.5, py, 2.2), (1.0, 1.0, 4.0), mat_limestone)

    # Signage on West Canopy: "FELIX HAAS HALL"
    bpy.ops.object.text_add(location=(-22.2, -3.2, 4.65), rotation=(math.pi/2, 0, math.pi/2))
    txt = bpy.context.active_object
    txt.name = "HAAS_West_Signage"
    txt.data.body = "FELIX HAAS HALL"
    txt.data.size = 0.42
    txt.data.extrude = 0.05
    txt.data.materials.append(mat_gold)
    txt.parent = root_obj
    col_ext.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # Address Plaque "201 N. UNIVERSITY STREET"
    bpy.ops.object.text_add(location=(-22.2, -2.4, 3.8), rotation=(math.pi/2, 0, math.pi/2))
    txt = bpy.context.active_object
    txt.name = "HAAS_Address_Signage"
    txt.data.body = "201 N. UNIVERSITY STREET"
    txt.data.size = 0.22
    txt.data.extrude = 0.03
    txt.data.materials.append(mat_bronze)
    txt.parent = root_obj
    col_ext.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # 5. Beaux-Arts Fenestration
    # Ground-Floor Rectangular Windows (Z = 2.4m, height 1.8m)
    for side, wx in [("East", 19.55), ("West", -19.55)]:
        for wy in [-20.0, -14.0, -8.0, 8.0, 14.0, 20.0]:
            create_box(f"HAAS_Win_Floor1_{side}_{wy}", col_ext, (wx, wy, 2.6), (0.2, 2.4, 1.8), mat_glass)
            create_box(f"HAAS_Sill_Floor1_{side}_{wy}", col_ext, (wx, wy, 1.6), (0.35, 2.6, 0.2), mat_limestone)

    # Second-Floor Monumental Arched Double-Height Windows (Z = 6.8m, height 3.6m)
    for side, wx in [("East", 19.55), ("West", -19.55)]:
        for wy in [-20.0, -14.0, -8.0, 8.0, 14.0, 20.0]:
            create_box(f"HAAS_Win_Floor2_{side}_{wy}", col_ext, (wx, wy, 6.8), (0.2, 2.6, 3.4), mat_glass)
            create_box(f"HAAS_Arch_Floor2_{side}_{wy}", col_ext, (wx, wy, 8.7), (0.3, 2.8, 0.4), mat_limestone)

    # 6. 4-Sided Hipped Slate Roof & Octagonal Verdigris Copper Cupola
    # Pitched hipped roof from Z = 11.5m to 15.5m (apex)
    # Modeled via layered stepping hip geometry
    for r_layer in range(8):
        lz = 11.5 + (r_layer + 1) * 0.5
        scale_fact = 1.0 - (r_layer + 1) * 0.09
        lw = 40.0 * scale_fact
        ll = 53.0 * scale_fact
        create_box(f"HAAS_Roof_Hip_Layer_{r_layer+1}", col_ext, (0, 0, lz), (lw, ll, 0.52), mat_slate_roof)

    # Octagonal Verdigris Copper Cupola (Z = 15.5m to 19.2m)
    create_cylinder("HAAS_Cupola_Base", col_ext, (0, 0, 15.8), radius=3.2, depth=0.8, mat=mat_limestone)
    create_cylinder("HAAS_Cupola_Drum", col_ext, (0, 0, 17.0), radius=2.8, depth=1.8, mat=mat_copper)
    create_cylinder("HAAS_Cupola_Dome", col_ext, (0, 0, 18.2), radius=2.9, depth=0.8, mat=mat_copper)
    create_cylinder("HAAS_Cupola_Spire", col_ext, (0, 0, 19.3), radius=0.08, depth=1.6, mat=mat_gold)

    print("Building 64_Felix_Haas_Hall_Interiors...")

    # =========================================================================
    # INTERIOR 1: 1903 Memorial Rotunda (Ground Floor, Z = 0.42m to 4.40m)
    # Sited inside the East portal volume: X in [5, 18], Y in [-12, +12]
    # Local Center: X = 11.5, Y = 0.0, Z = 0.42m
    # =========================================================================
    create_box("HAAS_Rotunda_Terrazzo_Floor", col_int, (11.5, 0, 0.44), (13.0, 22.0, 0.05), mat_terrazzo)
    create_box("HAAS_Rotunda_Border_Floor", col_int, (11.5, 0, 0.445), (13.0, 22.0, 0.04), mat_terrazzo_dark)
    create_box("HAAS_Rotunda_Wall_West", col_int, (5.0, 0, 2.4), (0.3, 22.0, 4.0), mat_limestone)
    create_box("HAAS_Rotunda_Wall_North", col_int, (11.5, 11.0, 2.4), (13.0, 0.3, 4.0), mat_dark_oak)
    create_box("HAAS_Rotunda_Wall_South", col_int, (11.5, -11.0, 2.4), (13.0, 0.3, 4.0), mat_dark_oak)
    create_box("HAAS_Rotunda_Ceiling", col_int, (11.5, 0, 4.35), (13.0, 22.0, 0.1), mat_limestone)

    # Historic Bronze 1903 Memorial Plaque on West Feature Wall
    create_box("HAAS_1903_Plaque_Frame", col_int, (5.18, 0, 2.3), (0.05, 3.6, 2.4), mat_dark_oak)
    create_box("HAAS_1903_Plaque_Plate", col_int, (5.22, 0, 2.3), (0.02, 3.4, 2.2), mat_plaque)

    bpy.ops.object.text_add(location=(5.25, 1.5, 2.9), rotation=(math.pi/2, 0, -math.pi/2))
    txt = bpy.context.active_object
    txt.name = "HAAS_1903_Plaque_Header"
    txt.data.body = "IN MEMORIAM - OCTOBER 31, 1903"
    txt.data.size = 0.18
    txt.data.extrude = 0.02
    txt.data.materials.append(mat_gold)
    txt.parent = root_obj
    col_int.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    bpy.ops.object.text_add(location=(5.25, 1.4, 2.5), rotation=(math.pi/2, 0, -math.pi/2))
    txt = bpy.context.active_object
    txt.name = "HAAS_1903_Plaque_Body"
    txt.data.body = "DEDICATED TO THE SEVENTEEN BOILERMAKERS"
    txt.data.size = 0.14
    txt.data.extrude = 0.015
    txt.data.materials.append(mat_gold)
    txt.parent = root_obj
    col_int.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    # Dedicated Spotlights for Memorial Plaque
    plaque_light = bpy.data.lights.new(name="HAAS_Plaque_Spot", type="SPOT")
    plaque_light.energy = 1400.0
    plaque_light.spot_size = math.radians(45)
    plaque_light.color = (1.0, 0.95, 0.85)
    plaque_light_obj = bpy.data.objects.new(name="HAAS_Plaque_Spot", object_data=plaque_light)
    plaque_light_obj.location = (-221.45 + 8.5, -64.02, 3.8)
    plaque_light_obj.rotation_euler = (0, math.radians(-50), 0)
    col_int.objects.link(plaque_light_obj)

    # 1903 Boilermakers Trophy & Football Vitrines
    for vy in [-4.5, 4.5]:
        create_box(f"HAAS_Vitrine_Base_{vy}", col_int, (11.5, vy, 0.95), (1.4, 2.6, 1.0), mat_dark_oak)
        create_box(f"HAAS_Vitrine_Glass_{vy}", col_int, (11.5, vy, 2.05), (1.3, 2.5, 1.2), mat_glass)
        create_box(f"HAAS_Vitrine_Cap_{vy}", col_int, (11.5, vy, 2.7), (1.4, 2.6, 0.12), mat_dark_oak)
        # Vintage leather football on pedestal
        create_cylinder(f"HAAS_Football_Plinth_{vy}", col_int, (11.5, vy, 1.6), radius=0.18, depth=0.3, mat=mat_limestone)
        create_box(f"HAAS_Vintage_Football_{vy}", col_int, (11.5, vy, 1.85), (0.28, 0.42, 0.28), mat_leather)
        # Interior vitrine light
        vlight = bpy.data.lights.new(name=f"HAAS_Vitrine_Light_{vy}", type="POINT")
        vlight.energy = 250.0
        vlight.color = (1.0, 0.95, 0.80)
        vlight_obj = bpy.data.objects.new(name=f"HAAS_Vitrine_Light_{vy}", object_data=vlight)
        vlight_obj.location = (-221.45 + 11.5, -64.02 + vy, 2.5)
        col_int.objects.link(vlight_obj)

    # Twin Sweeping Dark Oak Staircases (North and South walls) leading to Floor 2
    for sy, s_side in [(-9.0, "South"), (9.0, "North")]:
        for step in range(12):
            st_z = 0.44 + (step + 1) * 0.32
            st_x = 6.0 + step * 0.85
            create_box(f"HAAS_Stair_{s_side}_{step+1}", col_int, (st_x, sy, st_z / 2.0), (0.85, 2.8, st_z), mat_dark_oak)
        create_cylinder(f"HAAS_Stair_Newel_{s_side}", col_int, (6.0, sy, 2.0), radius=0.12, depth=1.6, mat=mat_dark_oak)

    # Grand 12-Arm Brass Ring Chandelier in Rotunda
    create_cylinder("HAAS_Rotunda_Chandelier_Ring", col_int, (11.5, 0, 3.8), radius=1.8, depth=0.08, mat=mat_brass)
    for ca in range(12):
        ang = ca * math.pi / 6.0
        cax = 11.5 + 1.8 * math.cos(ang)
        cay = 1.8 * math.sin(ang)
        create_cylinder(f"HAAS_Chandelier_Candle_{ca}", col_int, (cax, cay, 3.95), radius=0.035, depth=0.25, mat=mat_gold)

    chand_light = bpy.data.lights.new(name="HAAS_Rotunda_Chand_Light", type="POINT")
    chand_light.energy = 1100.0
    chand_light.color = (1.0, 0.88, 0.72)
    chand_obj = bpy.data.objects.new(name="HAAS_Rotunda_Chand_Light", object_data=chand_light)
    chand_obj.location = (-221.45 + 11.5, -64.02, 3.8)
    col_int.objects.link(chand_obj)

    # =========================================================================
    # INTERIOR 2: Computer Science Collaborative Commons (Floor 2, Z = 4.40m to 11.50m)
    # Historic Gym Floor volume: X in [-18, +18], Y in [-24, +24]
    # Center: X = 0.0, Y = 0.0, Z = 4.40m
    # =========================================================================
    create_box("HAAS_Commons_Floor_Maple", col_int, (0, 0, 4.42), (36.0, 48.0, 0.05), mat_maple_floor)
    create_box("HAAS_Commons_Ceiling", col_int, (0, 0, 11.45), (36.0, 48.0, 0.1), mat_limestone)

    # 4 Colossal Riveted Steel Roof Trusses spanning 36m clear span
    for ti, ty in enumerate([-16.0, -5.3, 5.3, 16.0]):
        create_box(f"HAAS_Truss_TopChord_{ti+1}", col_int, (0, ty, 10.8), (35.6, 0.35, 0.4), mat_steel)
        create_box(f"HAAS_Truss_BottomChord_{ti+1}", col_int, (0, ty, 9.2), (35.6, 0.35, 0.4), mat_steel)
        for tx in range(-16, 17, 4):
            create_box(f"HAAS_Truss_WebVert_{ti}_{tx}", col_int, (tx, ty, 10.0), (0.2, 0.25, 1.4), mat_steel)
            create_cylinder(f"HAAS_Truss_Gusset_{ti}_{tx}", col_int, (tx, ty, 10.0), radius=0.25, depth=0.3, mat=mat_steel)

    # 4 Collaborative Student Coding Workstations / Pods
    pod_coords = [(-7.5, -9.0), (-7.5, 9.0), (7.5, -9.0), (7.5, 9.0)]
    for pi, (px, py) in enumerate(pod_coords):
        # Collaborative oak study table (4.2m x 2.2m)
        create_box(f"HAAS_Pod_Table_{pi+1}", col_int, (px, py, 5.15), (4.2, 2.2, 0.06), mat_honey_oak)
        for lx in [px - 1.8, px + 1.8]:
            for ly in [py - 0.8, py + 0.8]:
                create_cylinder(f"HAAS_Pod_Leg_{pi}_{lx}_{ly}", col_int, (lx, ly, 4.78), radius=0.04, depth=0.72, mat=mat_steel)
        # Dual 27-inch coding monitors per side (4 monitors total per pod)
        for mi, mx in enumerate([px - 1.0, px + 1.0]):
            create_box(f"HAAS_Monitor_Base_{pi}_{mi}", col_int, (mx, py, 5.22), (0.35, 0.25, 0.02), mat_steel)
            create_box(f"HAAS_Monitor_Screen_{pi}_{mi}", col_int, (mx, py, 5.65), (0.75, 0.03, 0.45), mat_screen)
        # Student task chairs
        for ci, cy in enumerate([py - 1.4, py + 1.4]):
            for cx in [px - 1.2, px + 1.2]:
                create_cylinder(f"HAAS_Chair_Stem_{pi}_{cx}_{cy}", col_int, (cx, cy, 4.75), radius=0.035, depth=0.65, mat=mat_steel)
                create_box(f"HAAS_Chair_Seat_{pi}_{cx}_{cy}", col_int, (cx, cy, 5.10), (0.50, 0.50, 0.06), mat_dark_oak)
                create_box(f"HAAS_Chair_Back_{pi}_{cx}_{cy}", col_int, (cx, cy + (0.22 if cy>py else -0.22), 5.42), (0.46, 0.06, 0.42), mat_dark_oak)

    # Algorithm & Proof Whiteboards along North Wall (Y = 23.5m)
    for bi, bx in enumerate([-10.0, 0.0, 10.0]):
        create_box(f"HAAS_Whiteboard_Frame_{bi+1}", col_int, (bx, 23.8, 6.8), (6.5, 0.06, 2.4), mat_steel)
        create_box(f"HAAS_Whiteboard_Panel_{bi+1}", col_int, (bx, 23.77, 6.8), (6.3, 0.02, 2.2), mat_whiteboard)

    # Emissive Code / Algorithm Text on Whiteboards
    algorithms = [
        "DIJKSTRA(G, w, s): dist[v] = min(dist[v], dist[u] + w(u,v))",
        "FFT: X_k = \\sum x_n \\cdot e^{-i 2\\pi k n / N}",
        "QUICKSORT: T(n) = 2T(n/2) + O(n) \\implies O(n \\log n)"
    ]
    for bi, code in enumerate(algorithms):
        bx = -10.0 + bi * 10.0
        bpy.ops.object.text_add(location=(bx - 2.8, 23.75, 6.8), rotation=(math.pi/2, 0, 0))
        txt = bpy.context.active_object
        txt.name = f"HAAS_Algorithm_{bi+1}"
        txt.data.body = code
        txt.data.size = 0.22
        txt.data.extrude = 0.02
        txt.data.materials.append(mat_screen)
        txt.parent = root_obj
        col_int.objects.link(txt)
        bpy.context.scene.collection.objects.unlink(txt)

    # High-Bay Industrial Downlights in CS Commons
    for lx in [-12.0, 0.0, 12.0]:
        for ly in [-16.0, 0.0, 16.0]:
            light_data = bpy.data.lights.new(name=f"HAAS_HighBay_{lx}_{ly}", type="POINT")
            light_data.energy = 850.0
            light_data.color = (1.0, 0.98, 0.95)
            light_obj = bpy.data.objects.new(name=f"HAAS_HighBay_{lx}_{ly}", object_data=light_data)
            light_obj.location = (-221.45 + lx, -64.02 + ly, 10.8)
            col_int.objects.link(light_obj)

    # =========================================================================
    # INTERIOR 3: Felix Haas Faculty & Graduate Seminar Suite (Floor 3 / Mezzanine)
    # Sited along West side (overlooking University St): X in [-18, -4], Y in [-10, +10]
    # Center: X = -11.0, Y = 0.0, Z = 9.80m
    # =========================================================================
    create_box("HAAS_Seminar_Floor_Walnut", col_int, (-11.0, 0, 9.82), (12.0, 18.0, 0.05), mat_dark_oak)
    create_box("HAAS_Seminar_Persian_Rug", col_int, (-11.0, 0, 9.85), (6.0, 10.0, 0.04), mat_persian_rug)
    create_box("HAAS_Seminar_Wall_East", col_int, (-4.9, 0, 11.5), (0.2, 18.0, 3.4), mat_dark_oak)
    create_box("HAAS_Seminar_Wall_North", col_int, (-11.0, 9.1, 11.5), (12.0, 0.2, 3.4), mat_dark_oak)
    create_box("HAAS_Seminar_Wall_South", col_int, (-11.0, -9.1, 11.5), (12.0, 0.2, 3.4), mat_dark_oak)

    # Solid Walnut 12-Seat Conference Table
    create_box("HAAS_Seminar_Conf_Table", col_int, (-11.0, 0, 10.55), (2.8, 7.5, 0.08), mat_dark_oak)
    for py in [-2.4, 0.0, 2.4]:
        create_cylinder(f"HAAS_Seminar_Table_Base_{py}", col_int, (-11.0, py, 10.18), radius=0.40, depth=0.68, mat=mat_dark_oak)

    # 12 Executive Burgundy Leather Swivel Chairs
    for cy in [-2.8, -1.4, 0.0, 1.4, 2.8]:
        for cx, cside in [(-12.8, -1), (-9.2, 1)]:
            create_cylinder(f"HAAS_Chair_Stem_{cx}_{cy}", col_int, (cx, cy, 10.18), radius=0.04, depth=0.68, mat=mat_bronze)
            create_box(f"HAAS_Chair_Seat_{cx}_{cy}", col_int, (cx, cy, 10.55), (0.52, 0.52, 0.08), mat_leather)
            create_box(f"HAAS_Chair_Back_{cx}_{cy}", col_int, (cx + 0.24 * cside, cy, 10.90), (0.08, 0.48, 0.62), mat_leather)
    for hy, hrot in [(-4.2, 0), (4.2, math.pi)]:
        create_cylinder(f"HAAS_Chair_Head_Stem_{hy}", col_int, (-11.0, hy, 10.18), radius=0.04, depth=0.68, mat=mat_bronze)
        create_box(f"HAAS_Chair_Head_Seat_{hy}", col_int, (-11.0, hy, 10.55), (0.52, 0.52, 0.08), mat_leather)
        create_box(f"HAAS_Chair_Head_Back_{hy}", col_int, (-11.0, hy + (0.24 if hy>0 else -0.24), 10.90), (0.48, 0.08, 0.62), mat_leather)

    # Gold-Framed Oil Portrait of Provost Felix Haas on North Wall
    create_box("HAAS_Portrait_Frame", col_int, (-11.0, 8.95, 11.6), (1.4, 0.06, 1.8), mat_gold)
    create_box("HAAS_Portrait_Canvas", col_int, (-11.0, 8.92, 11.6), (1.2, 0.02, 1.6), mat_leather)
    # Picture light over portrait
    pic_light = bpy.data.lights.new(name="HAAS_Portrait_Pic_Light", type="SPOT")
    pic_light.energy = 450.0
    pic_light.spot_size = math.radians(45)
    pic_light.color = (1.0, 0.95, 0.85)
    pic_light_obj = bpy.data.objects.new(name="HAAS_Portrait_Pic_Light", object_data=pic_light)
    pic_light_obj.location = (-221.45 - 11.0, -64.02 + 8.5, 12.6)
    pic_light_obj.rotation_euler = (math.radians(-35), 0, 0)
    col_int.objects.link(pic_light_obj)

    # Glowing Green-Glass Banker's Lamps on Conference Table
    for ly in [-1.8, 1.8]:
        create_box(f"HAAS_Seminar_Banker_Shade_{ly}", col_int, (-11.0, ly, 10.82), (0.28, 0.16, 0.12), mat_green_glass)
        create_cylinder(f"HAAS_Seminar_Banker_Stand_{ly}", col_int, (-11.0, ly, 10.65), radius=0.02, depth=0.20, mat=mat_brass)
        blight = bpy.data.lights.new(name=f"HAAS_Seminar_Banker_Light_{ly}", type="POINT")
        blight.energy = 220.0
        blight.color = (0.75, 1.0, 0.75)
        blight_obj = bpy.data.objects.new(name=f"HAAS_Seminar_Banker_Light_{ly}", object_data=blight)
        blight_obj.location = (-221.45 - 11.0, -64.02 + ly, 10.85)
        col_int.objects.link(blight_obj)

    # Ceiling Lights in Seminar Suite
    for ly in [-4.0, 4.0]:
        clight = bpy.data.lights.new(name=f"HAAS_Seminar_Ceiling_{ly}", type="POINT")
        clight.energy = 600.0
        clight.color = (1.0, 0.96, 0.90)
        clight_obj = bpy.data.objects.new(name=f"HAAS_Seminar_Ceiling_{ly}", object_data=clight)
        clight_obj.location = (-221.45 - 11.0, -64.02 + ly, 12.8)
        col_int.objects.link(clight_obj)

    print("Building 65_Felix_Haas_Hall_Plaza_and_Site...")

    # 1. East Memorial Arrival Concourse (connecting 17 steps to campus walkway)
    create_box("HAAS_East_Memorial_Plaza", col_site, (33.0, 0, 0.05), (14.0, 24.0, 0.1), mat_limestone)

    # 2. West University Street Arrival Concourse
    create_box("HAAS_West_Street_Paving", col_site, (-25.5, 0, 0.05), (10.0, 48.0, 0.1), mat_brick)

    # 3. Limestone Planter Beds with Evergreen Boxwood Hedges
    for py, pside in [(-18.0, "South"), (18.0, "North")]:
        create_box(f"HAAS_Planter_Bed_{pside}", col_site, (28.0, py, 0.3), (5.0, 8.0, 0.5), mat_limestone)
        create_box(f"HAAS_Planter_Hedge_{pside}", col_site, (28.0, py, 0.65), (4.5, 7.5, 0.55), mat_copper)

    # 4. Campus Teak Wood Benches
    for by, brot in [(-12.0, 0), (12.0, 0)]:
        create_box(f"HAAS_Bench_Seat_{by}", col_site, (33.0, by, 0.45), (0.6, 2.2, 0.08), mat_honey_oak)
        create_box(f"HAAS_Bench_Back_{by}", col_site, (33.28, by, 0.75), (0.08, 2.2, 0.45), mat_honey_oak)
        create_box(f"HAAS_Bench_Legs_{by}", col_site, (33.0, by, 0.22), (0.55, 2.0, 0.42), mat_bronze)

    # 5. Bank of 12 Sheffield Bicycle Racks along University Street
    for ri in range(12):
        ry = -16.0 + ri * 1.2
        create_cylinder(f"HAAS_Bike_Rack_Arch_{ri+1}", col_site, (-25.0, ry, 0.45), radius=0.035, depth=0.9, mat=mat_bronze)
        create_box(f"HAAS_Bike_Rack_Crossbar_{ri+1}", col_site, (-25.0, ry, 0.85), (0.07, 0.85, 0.07), mat_bronze)

    # 6. Victorian Cast-Iron Lantern Posts with Warm Point Lights
    lantern_coords = [(34.0, -8.0), (34.0, 8.0), (-26.0, -14.0), (-26.0, 14.0)]
    for li, (lx, ly) in enumerate(lantern_coords):
        create_cylinder(f"HAAS_Lantern_Post_{li+1}", col_site, (lx, ly, 1.8), radius=0.10, depth=3.6, mat=mat_bronze)
        create_cylinder(f"HAAS_Lantern_Luminaire_{li+1}", col_site, (lx, ly, 3.7), radius=0.25, depth=0.45, mat=mat_gold)
        l_data = bpy.data.lights.new(name=f"HAAS_Lantern_Light_{li+1}", type="POINT")
        l_data.energy = 900.0
        l_data.color = (1.0, 0.85, 0.65)
        l_obj = bpy.data.objects.new(name=f"HAAS_Lantern_Light_{li+1}", object_data=l_data)
        l_obj.location = (-221.45 + lx, -64.02 + ly, 3.8)
        col_site.objects.link(l_obj)

    print("Calibrating Inspection Cameras Cam_97 through Cam_101...")

    def setup_camera(name, loc, rot_deg, lens=24.0):
        cam = bpy.data.objects.get(name)
        if not cam:
            cam_data = bpy.data.cameras.new(name=name)
            cam = bpy.data.objects.new(name=name, object_data=cam_data)
            col_cams.objects.link(cam)
        cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 1200.0
        cam.location = loc
        cam.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        return cam

    # Cam 97: Hero East Arrival Perspective (Memorial 17 Steps, Carved Portal, Roof, Cupola)
    # Sited east along the campus mall walkway looking West-Southwest at the 17 steps & portal
    setup_camera("Cam_97_HAAS_East_MemorialSteps_Hero", (-182.0, -64.02, 4.2), (82.0, 0.0, -90.0), lens=20.0)

    # Cam 98: 1903 Memorial Rotunda Interior
    # Looking from East entrance doorway westward toward the bronze 1903 memorial plaque, vitrines, and chandelier
    setup_camera("Cam_98_HAAS_1903_Memorial_Rotunda_Interior", (-205.0, -64.02, 2.8), (86.0, 0.0, -90.0), lens=18.0)

    # Cam 99: Computer Science Collaborative Commons Interior (Floor 2)
    # 3/4 elevated perspective looking across maple hardwood floor, exposed steel trusses, coding pods, and whiteboards
    setup_camera("Cam_99_HAAS_CS_Commons_Interior", (-234.0, -82.0, 7.8), (76.0, 0.0, -42.0), lens=18.0)

    # Cam 100: Felix Haas Faculty & Graduate Seminar Suite Interior (Floor 3)
    # 3/4 perspective across walnut conference table, burgundy leather chairs, banker's lamps, and portrait of Felix Haas
    setup_camera("Cam_100_HAAS_Faculty_Seminar_Interior", (-236.0, -71.0, 11.6), (75.0, 0.0, -35.0), lens=20.0)

    # Cam 101: Precinct Aerial Context
    # Elevated overview showing full Beaux-Arts pavilion, hipped slate roof, copper cupola, 17 steps, Armory and MATH integration
    setup_camera("Cam_101_HAAS_Precinct_Aerial", (-160.0, -115.0, 52.0), (58.0, 0.0, 36.0), lens=24.0)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Master Blend File saved successfully with Felix Haas Hall (HAAS)!")

if __name__ == "__main__":
    run_build()
