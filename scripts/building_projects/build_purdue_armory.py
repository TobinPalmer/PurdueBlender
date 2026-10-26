"""
Comprehensive Architectural Construction Script: Purdue Armory (AR - 1918)
Historical Background: Dedicated in 1918 during WWI; designed by Nicol, Scholer & Hoffman.
Features:
- Colossal $51.5m x 89.3m$ envelope with $19.5m$ barrel-vaulted arched roof
- Twin $22.0m$ Romanesque entrance towers with crenellated limestone battlements
- Monumental arched gable fanlight windows on North and South facades
- Romanesque carved limestone entrance portal on University St with 3D gold lettering
- Interior Great Drill Hall ($85m x 48m$ clear span) with 8 colossal three-hinged arched steel trusses
- Polished maple hardwood drill deck with athletic court lines and cadet formation markers
- ROTC Command Review Dais with 6 ceremonial military flags (US, Indiana, Army, Navy, Air Force, Space Force)
- Officer's Club & Cadet Heritage Lounge with walnut paneling, brass chandelier, and artifact displays
- 2nd-floor viewing mezzanine gallery with wrought-iron balustrades
- University Street parade plaza with twin historic 75mm artillery cannons on granite plinths, flagpole, bike racks, and lanterns
- 5 Precision-calibrated inspection cameras (Cam_87 to Cam_91)
"""

import bpy
import math
import mathutils
import os

def run():
    print("=== Commencing Construction of Purdue Armory (AR - 1918) ===")

    # Ensure collections exist
    col_ext = bpy.data.collections.get("57_Armory_Exterior")
    col_int = bpy.data.collections.get("58_Armory_Interiors_and_DrillHall")
    col_site = bpy.data.collections.get("59_Armory_Plaza_and_Site")

    if not col_ext:
        col_ext = bpy.data.collections.new("57_Armory_Exterior")
        bpy.context.scene.collection.children.link(col_ext)
    if not col_int:
        col_int = bpy.data.collections.new("58_Armory_Interiors_and_DrillHall")
        bpy.context.scene.collection.children.link(col_int)
    if not col_site:
        col_site = bpy.data.collections.new("59_Armory_Plaza_and_Site")
        bpy.context.scene.collection.children.link(col_site)

    # Clean out any previous objects in these 3 collections
    for col in [col_ext, col_int, col_site]:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Remove crude placeholder from 02_Campus_Buildings_Massing
    col_mass = bpy.data.collections.get("02_Campus_Buildings_Massing")
    if col_mass:
        for obj in list(col_mass.objects):
            if "armory" in obj.name.lower() or obj.name == "Armory (AR)":
                print(f"Removing placeholder object: {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)

    # Create Armory_Root empty
    root_obj = bpy.data.objects.get("Armory_Root")
    if not root_obj:
        root_obj = bpy.data.objects.new("Armory_Root", None)
        root_obj.empty_display_type = 'ARROWS'
        root_obj.empty_display_size = 5.0
        bpy.context.scene.collection.objects.link(root_obj)

    root_loc = (-218.55, 68.35, 0.0)
    root_obj.location = root_loc
    root_obj.rotation_euler = (0, 0, 0)

    # Explicit world transformation matrix
    M_WORLD = mathutils.Matrix.Translation(root_loc)

    # Material helper
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

    # Define Materials
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick") or get_mat("Purdue_Red_Brick", (0.50, 0.22, 0.18, 1.0), roughness=0.72)
    mat_stone = bpy.data.materials.get("Bedford_Indiana_Limestone") or get_mat("Bedford_Indiana_Limestone", (0.84, 0.83, 0.79, 1.0), roughness=0.55)
    mat_glass = bpy.data.materials.get("Solar_Ribbon_Glass") or get_mat("Solar_Ribbon_Glass", (0.15, 0.28, 0.38, 0.85), roughness=0.08, specular=0.98)
    mat_gold = bpy.data.materials.get("Purdue_Old_Gold") or get_mat("Purdue_Old_Gold", (0.85, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mat_bronze = get_mat("Armory_Dark_Bronze", (0.25, 0.20, 0.16, 1.0), roughness=0.35, metallic=0.85)
    mat_steel_truss = get_mat("Armory_Structural_Steel", (0.18, 0.20, 0.22, 1.0), roughness=0.40, metallic=0.88)
    mat_dark_oak = get_mat("Armory_Dark_Oak", (0.24, 0.14, 0.08, 1.0), roughness=0.32, specular=0.6)
    mat_maple_floor = get_mat("Armory_Polished_Maple", (0.82, 0.65, 0.42, 1.0), roughness=0.18, specular=0.85)
    mat_court_lines = get_mat("Armory_Court_Lines", (0.95, 0.95, 0.95, 1.0), roughness=0.3)
    mat_roof_copper = get_mat("Armory_Roof_Copper", (0.28, 0.42, 0.35, 1.0), roughness=0.65, metallic=0.4)
    mat_roof_membrane = get_mat("Armory_Roof_Gravel", (0.32, 0.31, 0.30, 1.0), roughness=0.85)
    mat_warm_glow = get_mat("Armory_Warm_Glow", (1.0, 0.88, 0.65, 1.0), roughness=0.2, emission=(1.0, 0.88, 0.65, 4.5))
    mat_highbay_glow = get_mat("Armory_Highbay_Glow", (0.95, 0.96, 1.0, 1.0), roughness=0.1, emission=(0.95, 0.96, 1.0, 6.0))
    mat_granite_pedestal = get_mat("Armory_Barre_Granite", (0.38, 0.38, 0.39, 1.0), roughness=0.45)
    mat_cannon_olive = get_mat("Armory_Cannon_Olive", (0.22, 0.26, 0.18, 1.0), roughness=0.40, metallic=0.75)
    mat_cannon_brass = get_mat("Armory_Cannon_Brass", (0.78, 0.62, 0.25, 1.0), roughness=0.25, metallic=0.90)
    mat_flag_us = get_mat("Armory_Flag_US", (0.75, 0.12, 0.15, 1.0), roughness=0.55)
    mat_flag_in = get_mat("Armory_Flag_Indiana", (0.08, 0.15, 0.45, 1.0), roughness=0.55)
    mat_flag_army = get_mat("Armory_Flag_Army", (0.12, 0.12, 0.12, 1.0), roughness=0.55)
    mat_flag_navy = get_mat("Armory_Flag_Navy", (0.05, 0.10, 0.35, 1.0), roughness=0.55)
    mat_leather_burgundy = get_mat("Armory_Leather_Burgundy", (0.28, 0.08, 0.10, 1.0), roughness=0.35, specular=0.6)
    mat_terrazzo = get_mat("Armory_Terrazzo_Cream", (0.86, 0.85, 0.82, 1.0), roughness=0.12, specular=0.95)

    # Geometry creation helpers
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

    def make_cylinder_local(name, col, loc, r, depth, mat=None, segments=24, rot=(0,0,0)):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        verts = []
        faces = []
        half_d = depth / 2.0
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            verts.append((x, y, -half_d))
            verts.append((x, y, half_d))
        for i in range(segments):
            i1 = i * 2
            i2 = i * 2 + 1
            i3 = ((i + 1) % segments) * 2
            i4 = ((i + 1) % segments) * 2 + 1
            faces.append((i1, i3, i4, i2))
        faces.append([i * 2 for i in range(segments)])
        faces.append([i * 2 + 1 for i in reversed(range(segments))])
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        if mat:
            obj.data.materials.append(mat)
        obj.parent = root_obj
        obj.location = loc
        obj.rotation_euler = rot
        col.objects.link(obj)
        return obj

    # =========================================================================
    # PART 1: EXTERIOR ENVELOPES & ROMANESQUE TOWERS
    # =========================================================================
    print("Building Part 1: Exterior Envelopes & Romanesque Towers...")

    # Continuous Bedford Limestone Water Table Base (0 to 1.5m)
    # North & South base
    make_box_local("Armory_Base_North", col_ext, (0.0, 44.15, 0.75), (51.5, 1.2, 1.5), mat_stone)
    make_box_local("Armory_Base_South", col_ext, (0.0, -44.15, 0.75), (51.5, 1.2, 1.5), mat_stone)
    # East & West base
    make_box_local("Armory_Base_East", col_ext, (25.25, 0.0, 0.75), (1.2, 87.1, 1.5), mat_stone)
    make_box_local("Armory_Base_West", col_ext, (-25.25, 0.0, 0.75), (1.2, 87.1, 1.5), mat_stone)

    # Perimeter Masonry Walls (1.5m to 12.5m eaves)
    # East wall along University St (width 1.0m, length 87.1m)
    make_box_local("Armory_Wall_East", col_ext, (25.25, 0.0, 7.0), (1.0, 87.1, 11.0), mat_brick)
    make_box_local("Armory_Wall_West", col_ext, (-25.25, 0.0, 7.0), (1.0, 87.1, 11.0), mat_brick)
    # North wall gable base & South wall gable base
    make_box_local("Armory_Wall_North_Low", col_ext, (0.0, 44.15, 6.75), (49.5, 1.0, 10.5), mat_brick)
    make_box_local("Armory_Wall_South_Low", col_ext, (0.0, -44.15, 6.75), (49.5, 1.0, 10.5), mat_brick)

    # Horizontal Limestone Beltcourses
    for bz in [4.5, 9.0, 12.5]:
        make_box_local(f"Armory_Belt_East_{bz}", col_ext, (25.4, 0.0, bz), (0.4, 88.0, 0.35), mat_stone)
        make_box_local(f"Armory_Belt_West_{bz}", col_ext, (-25.4, 0.0, bz), (0.4, 88.0, 0.35), mat_stone)
        make_box_local(f"Armory_Belt_North_{bz}", col_ext, (0.0, 44.3, bz), (50.5, 0.4, 0.35), mat_stone)
        make_box_local(f"Armory_Belt_South_{bz}", col_ext, (0.0, -44.3, bz), (50.5, 0.4, 0.35), mat_stone)

    # 10 Stepped Brick Buttress Piers along East and West facades
    for py in range(-40, 41, 9):
        # East piers
        make_box_local(f"Armory_Pier_East_{py}", col_ext, (25.9, py, 6.75), (0.9, 1.4, 11.5), mat_brick)
        make_box_local(f"Armory_Pier_Cap_East_{py}", col_ext, (25.9, py, 12.75), (1.1, 1.6, 0.5), mat_stone)
        # West piers
        make_box_local(f"Armory_Pier_West_{py}", col_ext, (-25.9, py, 6.75), (0.9, 1.4, 11.5), mat_brick)
        make_box_local(f"Armory_Pier_Cap_West_{py}", col_ext, (-25.9, py, 12.75), (1.1, 1.6, 0.5), mat_stone)

    # 18 Rhythmic Double-Hung Arched Window Bays (East & West)
    for wy in range(-36, 37, 9):
        # East windows
        make_box_local(f"Armory_Window_East_Low_{wy}", col_ext, (25.4, wy, 4.5), (0.3, 2.8, 2.6), mat_glass)
        make_box_local(f"Armory_Sill_East_Low_{wy}", col_ext, (25.55, wy, 3.1), (0.5, 3.1, 0.25), mat_stone)
        make_box_local(f"Armory_Window_East_High_{wy}", col_ext, (25.4, wy, 9.2), (0.3, 2.8, 3.2), mat_glass)
        make_box_local(f"Armory_Sill_East_High_{wy}", col_ext, (25.55, wy, 7.5), (0.5, 3.1, 0.25), mat_stone)
        # West windows
        make_box_local(f"Armory_Window_West_Low_{wy}", col_ext, (-25.4, wy, 4.5), (0.3, 2.8, 2.6), mat_glass)
        make_box_local(f"Armory_Sill_West_Low_{wy}", col_ext, (-25.55, wy, 3.1), (0.5, 3.1, 0.25), mat_stone)
        make_box_local(f"Armory_Window_West_High_{wy}", col_ext, (-25.4, wy, 9.2), (0.3, 2.8, 3.2), mat_glass)
        make_box_local(f"Armory_Sill_West_High_{wy}", col_ext, (-25.55, wy, 7.5), (0.5, 3.1, 0.25), mat_stone)

    # 4 Monumental Romanesque Corner Entrance Towers (22.0m height)
    # NE, NW, SE, SW towers (8.0m x 8.0m footprint)
    tower_locs = [
        ("NE", 21.75, 40.65),
        ("NW", -21.75, 40.65),
        ("SE", 21.75, -40.65),
        ("SW", -21.75, -40.65)
    ]
    for t_id, tx, ty in tower_locs:
        # Tower base and shaft
        make_box_local(f"Armory_Tower_Base_{t_id}", col_ext, (tx, ty, 0.75), (8.2, 8.2, 1.5), mat_stone)
        make_box_local(f"Armory_Tower_Shaft_{t_id}", col_ext, (tx, ty, 11.0), (8.0, 8.0, 19.0), mat_brick)
        make_box_local(f"Armory_Tower_Belt_{t_id}", col_ext, (tx, ty, 16.5), (8.4, 8.4, 0.4), mat_stone)
        make_box_local(f"Armory_Tower_Cornice_{t_id}", col_ext, (tx, ty, 20.6), (8.5, 8.5, 0.5), mat_stone)
        # Crenellated Limestone Battlements (Z = 20.8m to 22.2m)
        # 4 perimeter parapet strips with 3 crenel cutouts per edge
        for edge_x, edge_y, bw, bl in [
            (tx, ty + 4.1, 8.5, 0.5),
            (tx, ty - 4.1, 8.5, 0.5),
            (tx + 4.1, ty, 0.5, 8.5),
            (tx - 4.1, ty, 0.5, 8.5)
        ]:
            make_box_local(f"Armory_Battlement_{t_id}_{edge_x:.0f}_{edge_y:.0f}", col_ext, (edge_x, edge_y, 21.4), (bw, bl, 1.2), mat_stone)
        # Corner merlon accents
        for cx in [-4.0, 4.0]:
            for cy in [-4.0, 4.0]:
                make_box_local(f"Armory_Merlon_{t_id}_{cx}_{cy}", col_ext, (tx + cx, ty + cy, 22.0), (1.4, 1.4, 0.8), mat_stone)

        # Tower Romanesque Arched Windows / Slits
        for wz in [7.0, 12.0, 17.5]:
            out_x = tx + (4.1 if tx > 0 else -4.1)
            make_box_local(f"Armory_Tower_Win_{t_id}_{wz}", col_ext, (out_x, ty, wz), (0.3, 1.4, 2.5), mat_glass)
            make_box_local(f"Armory_Tower_Sill_{t_id}_{wz}", col_ext, (out_x, ty, wz - 1.35), (0.5, 1.6, 0.2), mat_stone)

    # Monumental Romanesque Arched Entrance Portico on University Street
    # Centered at X = 25.75, Y = 0.0
    make_box_local("Armory_Portico_Plinth", col_ext, (26.6, 0.0, 0.5), (2.2, 12.0, 1.0), mat_stone)
    make_box_local("Armory_Portico_Arch_L", col_ext, (26.3, -5.2, 4.5), (1.6, 1.8, 7.0), mat_stone)
    make_box_local("Armory_Portico_Arch_R", col_ext, (26.3, 5.2, 4.5), (1.6, 1.8, 7.0), mat_stone)
    make_box_local("Armory_Portico_Lintel", col_ext, (26.3, 0.0, 8.2), (1.6, 12.2, 1.2), mat_stone)
    make_box_local("Armory_Portico_Gable", col_ext, (26.3, 0.0, 9.4), (1.4, 11.0, 1.2), mat_stone)

    # 3D Old Gold Building Lettering on Portico Frieze: "PURDUE ARMORY"
    make_box_local("Armory_Frieze_Backplate", col_ext, (26.9, 0.0, 8.2), (0.1, 9.0, 0.9), mat_stone)
    armory_text = "PURDUE  ARMORY"
    t_start_y = -3.8
    t_spacing = 0.58
    for idx, char in enumerate(armory_text):
        if char != " ":
            make_box_local(f"Armory_Gold_Letter_{idx}", col_ext, (27.05, t_start_y + idx * t_spacing, 8.2), (0.12, 0.38, 0.55), mat_gold)

    # Triple Heavy Dark Oak Double Entrance Doors
    for dy in [-3.0, 0.0, 3.0]:
        make_box_local(f"Armory_Door_Frame_{dy}", col_ext, (25.6, dy, 2.6), (0.4, 2.2, 4.2), mat_dark_oak)
        make_box_local(f"Armory_Door_Leaf_L_{dy}", col_ext, (25.7, dy - 0.5, 2.4), (0.15, 0.95, 3.8), mat_dark_oak)
        make_box_local(f"Armory_Door_Leaf_R_{dy}", col_ext, (25.7, dy + 0.5, 2.4), (0.15, 0.95, 3.8), mat_dark_oak)
        make_box_local(f"Armory_Door_Transom_{dy}", col_ext, (25.7, dy, 4.4), (0.15, 2.0, 0.8), mat_glass)
        make_box_local(f"Armory_Door_Handle_{dy}", col_ext, (25.85, dy, 2.2), (0.1, 0.2, 0.4), mat_gold)

    # Stepped Granite Entrance Staircase (6 tiers)
    for st in range(6):
        st_x = 27.5 + st * 0.45
        st_z = 0.9 - st * 0.15
        make_box_local(f"Armory_Step_{st}", col_ext, (st_x, 0.0, st_z), (0.45, 13.0, 0.2), mat_granite_pedestal)
    # Limestone Cheek Walls flanking steps
    make_box_local("Armory_Cheek_Wall_North", col_ext, (28.6, 6.8, 0.7), (2.8, 0.6, 1.4), mat_stone)
    make_box_local("Armory_Cheek_Wall_South", col_ext, (28.6, -6.8, 0.7), (2.8, 0.6, 1.4), mat_stone)

    # Monumental Arched North & South Gable Fanlight Windows
    # North Fanlight (34m wide x 7.2m high, Z = 12.0m to 19.2m, Y = 44.15m)
    make_box_local("Armory_Fanlight_Glass_North", col_ext, (0.0, 44.15, 15.6), (34.0, 0.3, 6.8), mat_glass)
    make_box_local("Armory_Fanlight_Arch_North", col_ext, (0.0, 44.25, 19.3), (35.0, 0.6, 0.8), mat_stone)
    # Radial mullions for North Fanlight
    for mx in range(-15, 16, 5):
        make_box_local(f"Armory_Fanlight_Mullion_N_{mx}", col_ext, (mx, 44.2, 15.6), (0.2, 0.25, 6.6), mat_bronze)

    # South Fanlight (34m wide x 7.2m high, Z = 12.0m to 19.2m, Y = -44.15m)
    make_box_local("Armory_Fanlight_Glass_South", col_ext, (0.0, -44.15, 15.6), (34.0, 0.3, 6.8), mat_glass)
    make_box_local("Armory_Fanlight_Arch_South", col_ext, (0.0, -44.25, 19.3), (35.0, 0.6, 0.8), mat_stone)
    for mx in range(-15, 16, 5):
        make_box_local(f"Armory_Fanlight_Mullion_S_{mx}", col_ext, (mx, -44.2, 15.6), (0.2, 0.25, 6.6), mat_bronze)

    # Barrel-Vaulted Arched Roof Structure
    # Approximated by faceted segmented arch sections along X from -24.5 to +24.5
    # Apex at Z = 19.5, Eaves at Z = 12.5. R = 40m approximate curvature.
    num_segments = 14
    dx = 48.0 / num_segments
    for i in range(num_segments):
        x1 = -24.0 + i * dx
        x2 = x1 + dx
        xm = (x1 + x2) / 2.0
        # Parabolic height: z = 19.5 - 7.0 * (xm / 24.0)^2
        zm = 19.5 - 7.0 * (xm / 24.0)**2
        th = 0.4
        make_box_local(f"Armory_Roof_Seg_{i}", col_ext, (xm, 0.0, zm), (dx * 1.05, 87.5, th), mat_roof_copper)

    # Central Linear Ventilation Ridge Monitor (X = 0, Z = 19.8, width 6m, length 68m, height 1.4m)
    make_box_local("Armory_Ridge_Monitor", col_ext, (0.0, 0.0, 20.3), (6.2, 68.0, 1.2), mat_stone)
    make_box_local("Armory_Ridge_Louvers_East", col_ext, (3.15, 0.0, 20.3), (0.2, 67.0, 0.8), mat_bronze)
    make_box_local("Armory_Ridge_Louvers_West", col_ext, (-3.15, 0.0, 20.3), (0.2, 67.0, 0.8), mat_bronze)
    make_box_local("Armory_Ridge_Cap", col_ext, (0.0, 0.0, 21.0), (6.8, 68.4, 0.3), mat_roof_copper)

    # =========================================================================
    # PART 2: PHOTOREALISTIC INTERIORS & GREAT DRILL HALL
    # =========================================================================
    print("Building Part 2: Great Drill Hall, Steel Trusses, Dais & Officer's Club...")

    # Impermeable elevated foundation floor slab (Z = 0.40m, 85.0m x 48.0m)
    make_box_local("Armory_Drill_Floor_Slab", col_int, (0.0, 0.0, 0.20), (48.0, 85.0, 0.40), mat_maple_floor)

    # Inner perimeter enclosing walls (Z = 0.40m to 12.5m)
    make_box_local("Armory_Inner_Wall_East", col_int, (24.3, 0.0, 6.45), (0.4, 84.6, 12.1), mat_brick)
    make_box_local("Armory_Inner_Wall_West", col_int, (-24.3, 0.0, 6.45), (0.4, 84.6, 12.1), mat_brick)
    make_box_local("Armory_Inner_Wall_North", col_int, (0.0, 42.3, 6.45), (48.2, 0.4, 12.1), mat_brick)
    make_box_local("Armory_Inner_Wall_South", col_int, (0.0, -42.3, 6.45), (48.2, 0.4, 12.1), mat_brick)

    # Athletic & Military Drill Deck Floor Markings
    # Central basketball/volleyball court perimeter and key markings
    make_box_local("Armory_Court_Border_N", col_int, (0.0, 15.0, 0.41), (28.0, 0.2, 0.02), mat_court_lines)
    make_box_local("Armory_Court_Border_S", col_int, (0.0, -15.0, 0.41), (28.0, 0.2, 0.02), mat_court_lines)
    make_box_local("Armory_Court_Border_E", col_int, (14.0, 0.0, 0.41), (0.2, 30.0, 0.02), mat_court_lines)
    make_box_local("Armory_Court_Border_W", col_int, (-14.0, 0.0, 0.41), (0.2, 30.0, 0.02), mat_court_lines)
    make_box_local("Armory_Court_Center_Line", col_int, (0.0, 0.0, 0.41), (28.0, 0.2, 0.02), mat_court_lines)
    # Center-court gold Motion 'P' medallion
    make_box_local("Armory_Motion_P_Backplate", col_int, (0.0, 0.0, 0.415), (4.5, 4.5, 0.015), mat_gold)
    make_box_local("Armory_Motion_P_Inner", col_int, (0.0, 0.0, 0.42), (3.8, 3.8, 0.015), mat_bronze)

    # Cadet Formation Lines (spaced along the drill floor)
    for ly in range(-30, 31, 10):
        make_box_local(f"Armory_Formation_Line_{ly}", col_int, (0.0, ly, 0.41), (42.0, 0.15, 0.01), mat_court_lines)

    # 8 Colossal Three-Hinged Arched Structural Steel Trusses
    # Spanning across drill deck at Y = -35, -25, -15, -5, +5, +15, +25, +35
    truss_y_coords = [-35.0, -25.0, -15.0, -5.0, 5.0, 15.0, 25.0, 35.0]
    for tidx, ty in enumerate(truss_y_coords):
        # Heavy steel base thrust pedestals at X = -23.8 and +23.8
        make_box_local(f"Armory_Truss_Ped_E_{tidx}", col_int, (23.8, ty, 1.2), (1.2, 1.8, 1.6), mat_steel_truss)
        make_box_local(f"Armory_Truss_Ped_W_{tidx}", col_int, (-23.8, ty, 1.2), (1.2, 1.8, 1.6), mat_steel_truss)

        # Arched rib chord segments
        for i in range(num_segments):
            x1 = -23.5 + i * dx
            x2 = x1 + dx
            xm = (x1 + x2) / 2.0
            zm = 18.8 - 6.8 * (xm / 23.5)**2
            # Upper chord
            make_box_local(f"Armory_Truss_Chord_Top_{tidx}_{i}", col_int, (xm, ty, zm), (dx * 1.05, 0.45, 0.55), mat_steel_truss)
            # Lower chord (offset 1.2m below)
            make_box_local(f"Armory_Truss_Chord_Bot_{tidx}_{i}", col_int, (xm, ty, zm - 1.2), (dx * 1.05, 0.40, 0.45), mat_steel_truss)
            # Vertical and diagonal web struts
            make_box_local(f"Armory_Truss_Strut_V_{tidx}_{i}", col_int, (xm, ty, zm - 0.6), (0.2, 0.35, 1.2), mat_steel_truss)
            if i % 2 == 0:
                make_box_local(f"Armory_Truss_Strut_D_{tidx}_{i}", col_int, (xm, ty, zm - 0.6), (dx * 0.8, 0.25, 0.25), mat_steel_truss)

        # Central apex hinge pin at (0.0, ty, 18.8)
        make_box_local(f"Armory_Truss_Apex_Hinge_{tidx}", col_int, (0.0, ty, 18.8), (0.8, 0.8, 1.0), mat_steel_truss)

    # Longitudinal Steel Roof Purlins connecting trusses
    for px in [-20.0, -14.0, -8.0, 0.0, 8.0, 14.0, 20.0]:
        pz = 18.8 - 6.8 * (px / 23.5)**2
        make_box_local(f"Armory_Purlin_{px}", col_int, (px, 0.0, pz), (0.35, 78.0, 0.35), mat_steel_truss)

    # 16 High-Bay Suspended Metal-Halide LED Industrial Downlights
    for lx in [-12.0, 12.0]:
        for ly in range(-30, 31, 10):
            lz = 15.5
            make_box_local(f"Armory_Highbay_Housing_{lx}_{ly}", col_int, (lx, ly, lz + 0.3), (0.9, 0.9, 0.6), mat_steel_truss)
            make_box_local(f"Armory_Highbay_Lens_{lx}_{ly}", col_int, (lx, ly, lz), (0.8, 0.8, 0.1), mat_highbay_glow)
            # Add Blender point light
            l_data = bpy.data.lights.new(name=f"Armory_Light_Data_{lx}_{ly}", type='POINT')
            l_data.energy = 4200.0
            l_data.color = (0.96, 0.97, 1.0)
            l_obj = bpy.data.objects.new(f"Armory_Highbay_Light_{lx}_{ly}", l_data)
            l_obj.parent = root_obj
            l_obj.location = (lx, ly, lz - 0.2)
            col_int.objects.link(l_obj)

    # ROTC Command Review Dais & Flag Pavilion (North end, Y = 36.0m)
    make_box_local("Armory_Dais_Stage", col_int, (0.0, 36.0, 0.70), (14.0, 5.0, 0.60), mat_dark_oak)
    make_box_local("Armory_Dais_Steps", col_int, (0.0, 33.2, 0.55), (6.0, 0.8, 0.30), mat_dark_oak)
    make_box_local("Armory_Dais_Rostrum", col_int, (0.0, 35.5, 1.55), (1.4, 0.9, 1.1), mat_dark_oak)
    make_box_local("Armory_Dais_Mic", col_int, (0.0, 35.6, 2.2), (0.05, 0.05, 0.3), mat_bronze)
    make_box_local("Armory_Dais_Purdue_Seal", col_int, (0.0, 35.0, 1.55), (0.6, 0.05, 0.6), mat_gold)

    # Reviewing Officer Chairs on Dais
    for ox in [-2.5, 2.5]:
        make_box_local(f"Armory_Officer_Chair_{ox}", col_int, (ox, 37.0, 1.45), (0.8, 0.8, 0.9), mat_leather_burgundy)

    # 6 Ceremonial Military Flags on Brass Standards
    flag_defs = [
        ("US", -4.5, mat_flag_us),
        ("Indiana", -2.7, mat_flag_in),
        ("Army", -0.9, mat_flag_army),
        ("Navy", 0.9, mat_flag_navy),
        ("AirForce", 2.7, mat_flag_in),
        ("SpaceForce", 4.5, mat_flag_army)
    ]
    for f_name, fx, f_mat in flag_defs:
        # Brass pole
        make_box_local(f"Armory_Flagpole_{f_name}", col_int, (fx, 38.0, 2.2), (0.08, 0.08, 2.6), mat_gold)
        # Gold finial
        make_box_local(f"Armory_Finial_{f_name}", col_int, (fx, 38.0, 3.55), (0.18, 0.18, 0.25), mat_gold)
        # Fabric banner
        make_box_local(f"Armory_Banner_{f_name}", col_int, (fx + 0.6, 38.0, 2.7), (1.2, 0.04, 1.5), f_mat)

    # 2nd-Floor Perimeter Viewing Mezzanine Gallery (East & West walls at Z = 5.5m)
    # East Mezzanine
    make_box_local("Armory_Mezzanine_Slab_East", col_int, (22.2, 0.0, 5.5), (4.2, 80.0, 0.35), mat_maple_floor)
    make_box_local("Armory_Mezzanine_Railing_East", col_int, (20.1, 0.0, 6.2), (0.1, 80.0, 1.05), mat_bronze)
    # West Mezzanine
    make_box_local("Armory_Mezzanine_Slab_West", col_int, (-22.2, 0.0, 5.5), (4.2, 80.0, 0.35), mat_maple_floor)
    make_box_local("Armory_Mezzanine_Railing_West", col_int, (-20.1, 0.0, 6.2), (0.1, 80.0, 1.05), mat_bronze)

    # =========================================================================
    # PART 3: OFFICER'S CLUB & CADET HERITAGE LOUNGE
    # Sited on Floor 1 East Wing (X: 16m to 24m, Y: -12m to +12m, Z: 0.40m to 5.2m)
    # =========================================================================
    print("Building Officer's Club & Cadet Heritage Lounge...")

    # Enclosing walls for Officer's Club
    make_box_local("Armory_Club_Wall_West", col_int, (16.0, 0.0, 2.8), (0.4, 24.0, 4.8), mat_dark_oak)
    make_box_local("Armory_Club_Wall_North", col_int, (20.0, 12.0, 2.8), (8.0, 0.4, 4.8), mat_dark_oak)
    make_box_local("Armory_Club_Wall_South", col_int, (20.0, -12.0, 2.8), (8.0, 0.4, 4.8), mat_dark_oak)
    make_box_local("Armory_Club_Ceiling", col_int, (20.0, 0.0, 5.2), (8.0, 24.0, 0.2), mat_stone)

    # Rich Walnut Flooring & Wainscoting
    make_box_local("Armory_Club_Floor", col_int, (20.0, 0.0, 0.42), (7.8, 23.6, 0.04), mat_dark_oak)
    make_box_local("Armory_Club_Wainscot_W", col_int, (16.25, 0.0, 1.2), (0.1, 23.6, 1.5), mat_dark_oak)
    make_box_local("Armory_Club_Wainscot_E", col_int, (23.85, 0.0, 1.2), (0.1, 23.6, 1.5), mat_dark_oak)

    # Monumental 12-Arm Brass Ring Chandelier
    make_box_local("Armory_Chandelier_Ring", col_int, (20.0, 0.0, 4.2), (3.2, 3.2, 0.15), mat_gold)
    make_box_local("Armory_Chandelier_Stem", col_int, (20.0, 0.0, 4.7), (0.15, 0.15, 1.0), mat_gold)
    for c_ang in range(0, 360, 45):
        rad = math.radians(c_ang)
        cx = 20.0 + 1.6 * math.cos(rad)
        cy = 0.0 + 1.6 * math.sin(rad)
        make_box_local(f"Armory_Chandelier_Candle_{c_ang}", col_int, (cx, cy, 4.3), (0.15, 0.15, 0.35), mat_warm_glow)
    # Chandelier light
    l_club = bpy.data.lights.new(name="Armory_Club_Light_Data", type='POINT')
    l_club.energy = 2800.0
    l_club.color = (1.0, 0.88, 0.70)
    l_club_obj = bpy.data.objects.new("Armory_Club_Light", l_club)
    l_club_obj.parent = root_obj
    l_club_obj.location = (20.0, 0.0, 4.0)
    col_int.objects.link(l_club_obj)

    # 4 Military Artifact Display Cases (illuminated glass vitrines)
    for cidx, cy in enumerate([-8.0, -3.0, 3.0, 8.0]):
        make_box_local(f"Armory_Vitrine_Base_{cidx}", col_int, (23.2, cy, 0.85), (0.9, 2.2, 0.85), mat_dark_oak)
        make_box_local(f"Armory_Vitrine_Glass_{cidx}", col_int, (23.2, cy, 1.85), (0.8, 2.0, 1.15), mat_glass)
        make_box_local(f"Armory_Vitrine_Top_{cidx}", col_int, (23.2, cy, 2.45), (0.9, 2.2, 0.15), mat_dark_oak)
        # Interior artifact: historic cadet saber & medal
        make_box_local(f"Armory_Saber_{cidx}", col_int, (23.2, cy, 1.6), (0.05, 1.5, 0.05), mat_gold)
        make_box_local(f"Armory_Medal_{cidx}", col_int, (23.2, cy - 0.4, 1.4), (0.05, 0.2, 0.2), mat_gold)
        # Accent vitrine light
        make_box_local(f"Armory_Vitrine_Light_{cidx}", col_int, (23.2, cy, 2.35), (0.5, 1.5, 0.05), mat_warm_glow)

    # Executive Seating Suite: Mahogany Table, 4 Leather Wingback Chairs
    make_box_local("Armory_Club_Table", col_int, (19.5, -4.5, 0.85), (2.2, 1.4, 0.8), mat_dark_oak)
    chair_locs = [
        ("W1", 18.2, -4.5, 0),
        ("E1", 20.8, -4.5, math.pi),
        ("N1", 19.5, -3.3, -math.pi/2),
        ("S1", 19.5, -5.7, math.pi/2)
    ]
    for ch_id, chx, chy, ch_rot in chair_locs:
        make_box_local(f"Armory_Wingback_{ch_id}", col_int, (chx, chy, 1.0), (0.85, 0.85, 1.1), mat_leather_burgundy)

    # Chesterfield Leather Lounge Sofa (North end of club)
    make_box_local("Armory_Chesterfield_Sofa", col_int, (19.5, 5.5, 0.9), (1.2, 3.2, 0.95), mat_leather_burgundy)
    make_box_local("Armory_Club_Coffee_Table", col_int, (18.0, 5.5, 0.65), (1.0, 2.0, 0.45), mat_dark_oak)

    # Purdue Military Veterans Memorial Honor Roll on West Wall
    make_box_local("Armory_Honor_Roll_Backing", col_int, (16.25, 0.0, 2.6), (0.1, 4.5, 2.2), mat_dark_oak)
    make_box_local("Armory_Honor_Roll_Plaque", col_int, (16.32, 0.0, 2.6), (0.05, 4.2, 1.9), mat_gold)
    make_box_local("Armory_Honor_Roll_Header", col_int, (16.35, 0.0, 3.3), (0.06, 3.6, 0.4), mat_bronze)

    # =========================================================================
    # PART 3: CIVIC HARDSCAPE, PARADE PLAZA & ARTILLERY CANNONS
    # =========================================================================
    print("Building Part 3: Civic Hardscape, Artillery Cannons & Site Integration...")

    # Main University Street Parade Plaza (36m x 24m granite & brick concourse)
    make_box_local("Armory_Plaza_Deck", col_site, (36.0, 0.0, 0.12), (20.0, 48.0, 0.24), mat_granite_pedestal)

    # Twin Historic 75mm Artillery Cannons flanking arrival stairs
    for c_id, cy in [("North", 11.5), ("South", -11.5)]:
        # Heavy Barre granite pedestal plinth
        make_box_local(f"Armory_Cannon_Plinth_{c_id}", col_site, (32.0, cy, 0.5), (3.2, 2.2, 0.8), mat_granite_pedestal)
        make_box_local(f"Armory_Cannon_Plaque_{c_id}", col_site, (33.65, cy, 0.5), (0.05, 1.2, 0.5), mat_bronze)
        # Carriage frame
        make_box_local(f"Armory_Cannon_Carriage_{c_id}", col_site, (32.0, cy, 1.2), (2.4, 1.4, 0.6), mat_cannon_olive)
        # Spoked wheels (diameter 1.4m)
        make_cylinder_local(f"Armory_Cannon_Wheel_L_{c_id}", col_site, (32.0, cy - 0.85, 1.2), 0.70, 0.25, mat_cannon_olive, rot=(math.pi/2, 0, 0))
        make_cylinder_local(f"Armory_Cannon_Wheel_R_{c_id}", col_site, (32.0, cy + 0.85, 1.2), 0.70, 0.25, mat_cannon_olive, rot=(math.pi/2, 0, 0))
        # Cannon barrel tube (3.2m length, pointing east toward University St)
        make_cylinder_local(f"Armory_Cannon_Barrel_{c_id}", col_site, (32.8, cy, 1.4), 0.18, 3.2, mat_cannon_olive, rot=(0, math.pi/2 - 0.15, 0))
        # Brass breech block
        make_box_local(f"Armory_Cannon_Breech_{c_id}", col_site, (31.0, cy, 1.25), (0.5, 0.45, 0.45), mat_cannon_brass)

    # 15.0m Tapered Stainless Steel Flagpole
    make_cylinder_local("Armory_Flagpole_Shaft", col_site, (38.0, 0.0, 7.5), 0.12, 15.0, mat_cannon_brass)
    make_box_local("Armory_Flagpole_Plinth", col_site, (38.0, 0.0, 0.4), (1.6, 1.6, 0.6), mat_stone)
    make_box_local("Armory_Flagpole_Finial", col_site, (38.0, 0.0, 15.1), (0.35, 0.35, 0.35), mat_gold)
    # Flying United States Flag
    make_box_local("Armory_Flying_US_Flag", col_site, (39.5, 0.0, 13.8), (2.8, 0.06, 1.8), mat_flag_us)

    # Flanking Limestone Planters with Boxwoods
    make_box_local("Armory_Planter_North", col_site, (30.0, 20.0, 0.5), (4.5, 6.0, 0.8), mat_stone)
    make_box_local("Armory_Planter_South", col_site, (30.0, -20.0, 0.5), (4.5, 6.0, 0.8), mat_stone)
    boxwood_mat = bpy.data.materials.get("Purdue_Boxwood_Shrub") or mat_cannon_olive
    make_box_local("Armory_Shrub_North", col_site, (30.0, 20.0, 1.1), (3.8, 5.2, 0.7), boxwood_mat)
    make_box_local("Armory_Shrub_South", col_site, (30.0, -20.0, 1.1), (3.8, 5.2, 0.7), boxwood_mat)

    # Campus Teak Wood Benches
    bench_mat = bpy.data.materials.get("Campus_Teak_Wood_Bench") or mat_dark_oak
    for by in [-16.0, 16.0]:
        make_box_local(f"Armory_Bench_{by}", col_site, (31.0, by, 0.45), (0.7, 2.5, 0.55), bench_mat)

    # Bank of 12 Sheffield Bicycle Racks
    for ry in range(-6, 7, 2):
        make_box_local(f"Armory_Bike_Rack_{ry}", col_site, (42.0, ry + 16.0, 0.45), (1.2, 0.1, 0.9), mat_bronze)

    # Victorian Cast-Iron Lantern Posts with Warm Luminaires
    for lx, ly in [(30.0, -25.0), (30.0, 25.0), (44.0, -18.0), (44.0, 18.0)]:
        make_box_local(f"Armory_Lantern_Post_{lx}_{ly}", col_site, (lx, ly, 2.2), (0.25, 0.25, 4.4), mat_bronze)
        make_box_local(f"Armory_Lantern_Head_{lx}_{ly}", col_site, (lx, ly, 4.4), (0.6, 0.6, 0.8), mat_warm_glow)
        l_data = bpy.data.lights.new(name=f"Armory_Lantern_Light_Data_{lx}_{ly}", type='POINT')
        l_data.energy = 1800.0
        l_data.color = (1.0, 0.90, 0.75)
        l_obj = bpy.data.objects.new(f"Armory_Lantern_Light_{lx}_{ly}", l_data)
        l_obj.parent = root_obj
        l_obj.location = (lx, ly, 4.2)
        col_site.objects.link(l_obj)

    # =========================================================================
    # PART 4: PRECISION-CALIBRATED INSPECTION CAMERAS
    # 5 Dedicated Inspection Cameras (Cam_87 through Cam_91)
    # =========================================================================
    print("Calibrating 5 Precision Inspection Cameras with Explicit M_WORLD Matrix...")

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

    # 1. Cam_87: Hero University Street Arrival View
    # Stepped back across University St to frame the Romanesque arched entrance, gold lettering, twin towers, artillery cannon, and flagpole
    cam87_loc = local_to_world_explicit((52.0, -14.0, 4.5))
    cam87_target = local_to_world_explicit((24.0, 0.0, 9.0))
    set_camera("Cam_87_Armory_UniversitySt_Hero", cam87_loc, cam87_target, lens=28.0)

    # 2. Cam_88: The Great Drill Hall Interior (Colossal Trusses & Floor Sheen)
    # Positioned at the South end looking North down the full 85m clear length
    cam88_loc = local_to_world_explicit((0.0, -38.0, 3.2))
    cam88_target = local_to_world_explicit((0.0, 15.0, 6.0))
    set_camera("Cam_88_Armory_DrillHall_Colossal_Trusses_Interior", cam88_loc, cam88_target, lens=22.0)

    # 3. Cam_89: Officer's Club & Cadet Heritage Lounge
    # 3/4 interior perspective showcasing the brass chandelier, walnut paneling, military vitrines, and wingback chairs
    cam89_loc = local_to_world_explicit((17.2, -8.5, 2.2))
    cam89_target = local_to_world_explicit((21.5, 0.0, 2.0))
    set_camera("Cam_89_Armory_OfficersClub_Lounge_Interior", cam89_loc, cam89_target, lens=24.0)

    # 4. Cam_90: Viewing Mezzanine Gallery Overlook
    # Positioned on East mezzanine at Z = 6.8m looking 3/4 across the drill floor and colossal steel arches
    cam90_loc = local_to_world_explicit((21.0, 20.0, 6.8))
    cam90_target = local_to_world_explicit((-5.0, -5.0, 1.8))
    set_camera("Cam_90_Armory_Mezzanine_Overlook_Interior", cam90_loc, cam90_target, lens=24.0)

    # 5. Cam_91: North-East Precinct Aerial Overview
    # Elevated overview framing the barrel-vaulted roof, ridge monitor, twin towers, University St, and campus context
    cam91_loc = local_to_world_explicit((68.0, 62.0, 54.0))
    cam91_target = local_to_world_explicit((0.0, 0.0, 10.0))
    set_camera("Cam_91_Armory_Precinct_Aerial", cam91_loc, cam91_target, lens=28.0)

    print("=== Purdue Armory Construction Completed Successfully! ===")

if __name__ == "__main__":
    run()
