import bpy
import math
from mathutils import Vector, Euler

print("--- Starting Purdue Memorial Union (PMU - 1924/2021) Construction ---")

# 1. Purge low-poly placeholder 'Purdue Student Union'
pmu_ph = bpy.data.objects.get("Purdue Student Union")
if pmu_ph:
    print(f"Removing low-poly placeholder: {pmu_ph.name}")
    bpy.data.objects.remove(pmu_ph, do_unlink=True)

# 2. Setup Collections
def get_or_create_collection(name, parent_col=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

col_exterior = get_or_create_collection("45_Purdue_Memorial_Union_Exterior")
col_interiors = get_or_create_collection("46_Purdue_Memorial_Union_Interiors")
col_site = get_or_create_collection("47_Purdue_Memorial_Union_Plaza_and_Site")
col_cams = get_or_create_collection("00_Inspection_Cameras")

# 3. Setup PBR Materials
def get_or_create_mat(name, color, roughness=0.5, metallic=0.0, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_color and emission_strength > 0:
            bsdf.inputs["Emission Color"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_brick = get_or_create_mat("PMU_Red_Brick_Gothic", (0.55, 0.18, 0.12, 1.0), roughness=0.75)
mat_limestone = get_or_create_mat("PMU_Bedford_Limestone", (0.82, 0.80, 0.74, 1.0), roughness=0.60)
mat_slate = get_or_create_mat("PMU_Slate_Roof", (0.22, 0.25, 0.28, 1.0), roughness=0.45)
mat_glass = get_or_create_mat("PMU_Lead_Gothic_Glass", (0.12, 0.16, 0.22, 1.0), roughness=0.10, metallic=0.1)
mat_stained = get_or_create_mat("PMU_Stained_Glass_Lancet", (0.85, 0.35, 0.15, 1.0), roughness=0.20, emission_color=(0.95, 0.45, 0.15, 1.0), emission_strength=2.5)
mat_timber = get_or_create_mat("PMU_Dark_Oak_Timber", (0.18, 0.10, 0.05, 1.0), roughness=0.40)
mat_parquet = get_or_create_mat("PMU_GreatHall_Parquet", (0.50, 0.32, 0.18, 1.0), roughness=0.22)
mat_crest_gold = get_or_create_mat("PMU_Memorial_Crest_Gold", (0.95, 0.80, 0.25, 1.0), roughness=0.25, metallic=0.85, emission_color=(0.95, 0.80, 0.25, 1.0), emission_strength=1.5)
mat_crest_black = get_or_create_mat("PMU_Memorial_Crest_Black", (0.05, 0.05, 0.05, 1.0), roughness=0.30)
mat_terrazzo = get_or_create_mat("PMU_Dining_Terrazzo", (0.85, 0.85, 0.83, 1.0), roughness=0.18)
mat_booth = get_or_create_mat("PMU_Dining_Booth_Leather", (0.60, 0.15, 0.12, 1.0), roughness=0.35)
mat_steel = get_or_create_mat("PMU_Stainless_Steel", (0.85, 0.85, 0.88, 1.0), roughness=0.20, metallic=0.90)
mat_bronze = get_or_create_mat("PMU_Bronze_Hardware", (0.65, 0.48, 0.20, 1.0), roughness=0.30, metallic=0.85)
mat_granite = get_or_create_mat("PMU_Granite_Paver", (0.42, 0.42, 0.44, 1.0), roughness=0.55)
mat_gold_text = get_or_create_mat("PMU_Signage_Gold", (0.98, 0.82, 0.25, 1.0), roughness=0.20, metallic=0.90, emission_color=(0.98, 0.82, 0.25, 1.0), emission_strength=2.0)
mat_ember = get_or_create_mat("PMU_Fireplace_Ember", (1.0, 0.35, 0.05, 1.0), roughness=0.80, emission_color=(1.0, 0.35, 0.05, 1.0), emission_strength=8.0)
mat_lantern = get_or_create_mat("PMU_Lantern_Glow", (1.0, 0.90, 0.70, 1.0), roughness=0.2, emission_color=(1.0, 0.90, 0.70, 1.0), emission_strength=5.0)

# 4. Helper Mesh Creation via from_pydata
def create_box(name, x_min, x_max, y_min, y_max, z_min, z_max, mat, collection):
    verts = [
        (x_min, y_min, z_min), (x_max, y_min, z_min), (x_max, y_max, z_min), (x_min, y_max, z_min),
        (x_min, y_min, z_max), (x_max, y_min, z_max), (x_max, y_max, z_max), (x_min, y_max, z_max)
    ]
    faces = [
        (0, 1, 2, 3), # bottom
        (4, 7, 6, 5), # top
        (0, 4, 5, 1), # front (-Y)
        (1, 5, 6, 2), # right (+X)
        (2, 6, 7, 3), # back (+Y)
        (3, 7, 4, 0)  # left (-X)
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_gable_roof(name, x_min, x_max, y_min, y_max, z_base, z_ridge, mat, collection, axis='Y'):
    mesh = bpy.data.meshes.new(name + "_mesh")
    if axis == 'Y': # Ridge runs along Y
        x_mid = (x_min + x_max) / 2.0
        verts = [
            (x_min, y_min, z_base), (x_max, y_min, z_base), (x_max, y_max, z_base), (x_min, y_max, z_base),
            (x_mid, y_min, z_ridge), (x_mid, y_max, z_ridge)
        ]
        faces = [
            (0, 1, 2, 3), # base
            (0, 4, 1),    # front gable
            (3, 2, 5),    # back gable
            (0, 3, 5, 4), # west slope
            (1, 4, 5, 2)  # east slope
        ]
    else: # Ridge runs along X
        y_mid = (y_min + y_max) / 2.0
        verts = [
            (x_min, y_min, z_base), (x_max, y_min, z_base), (x_max, y_max, z_base), (x_min, y_max, z_base),
            (x_min, y_mid, z_ridge), (x_max, y_mid, z_ridge)
        ]
        faces = [
            (0, 1, 2, 3), # base
            (0, 3, 4),    # west gable
            (1, 5, 2),    # east gable
            (0, 4, 5, 1), # south slope
            (3, 2, 5, 4)  # north slope
        ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_cylinder(name, x, y, z_min, z_max, radius, segments, mat, collection):
    verts = []
    dz = z_max - z_min
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        verts.append((x + radius * math.cos(a), y + radius * math.sin(a), z_min))
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        verts.append((x + radius * math.cos(a), y + radius * math.sin(a), z_max))
    
    faces = []
    # bottom face
    faces.append([i for i in range(segments)])
    # top face
    faces.append([segments + i for i in reversed(range(segments))])
    # side faces
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, next_i, segments + next_i, segments + i))
    
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_3d_text(name, text, loc, rot, size, mat, collection, extrude=0.04):
    curve_data = bpy.data.curves.new(name=name, type='FONT')
    curve_data.body = text
    curve_data.size = size
    curve_data.extrude = extrude
    curve_data.align_x = 'CENTER'
    curve_data.align_y = 'CENTER'
    obj = bpy.data.objects.new(name=name, object_data=curve_data)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

# 5. Build PMU Exterior Architectural Composition
print("Building PMU Exterior Structure...")

# Water table base (Bedford Limestone, Z: 0.0 to 1.5m)
# Main body X: [165.7, 265.9], Y: [-317.2, -209.3]
# Central South Wing: X: [185.0, 246.0], Y: [-317.2, -260.0]
# West Wing: X: [165.7, 195.0], Y: [-300.0, -215.0]
# East Wing: X: [236.0, 265.9], Y: [-300.0, -215.0]
# North Wing: X: [185.0, 246.0], Y: [-245.0, -209.3]

# Exterior Hollow Walls & Water Table Bases:
# South Facade Water Table & Brick Wall (X: 185 to 246, Y: -317.2 to -315.8)
create_box("PMU_Base_South", 185.0, 246.0, -317.2, -315.8, 0.0, 1.5, mat_limestone, col_exterior)
create_box("PMU_Wall_South_L", 185.0, 208.0, -317.2, -315.8, 1.5, 18.2, mat_brick, col_exterior)
create_box("PMU_Wall_South_R", 224.0, 246.0, -317.2, -315.8, 1.5, 18.2, mat_brick, col_exterior)

# South Main Entrance Gothic Tower (X: 208.0 to 224.0, Y: -317.8 to -303.0)
# Tower base & walls rising to Z = 27.0m
create_box("PMU_Tower_Base_Limestone", 208.0, 224.0, -317.8, -303.0, 0.0, 1.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Wall_Front", 208.0, 224.0, -317.8, -316.4, 7.5, 25.5, mat_brick, col_exterior)
create_box("PMU_Tower_Wall_West", 208.0, 209.4, -317.8, -303.0, 1.5, 25.5, mat_brick, col_exterior)
create_box("PMU_Tower_Wall_East", 222.6, 224.0, -317.8, -303.0, 1.5, 25.5, mat_brick, col_exterior)
# Tower Arch Entrance Portal (Z = 0.0 to 7.5m, open arch in center)
create_box("PMU_Tower_Portal_Pillar_W", 208.0, 211.5, -317.8, -316.4, 0.0, 7.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Portal_Pillar_E", 220.5, 224.0, -317.8, -316.4, 0.0, 7.5, mat_limestone, col_exterior)
create_box("PMU_Tower_Portal_Lintel", 211.5, 220.5, -317.8, -316.4, 6.0, 7.5, mat_limestone, col_exterior)

# Tower 4 Octagonal Corner Turrets (Z: 24.0 to 28.5m)
turret_coords = [(208.2, -317.6), (223.8, -317.6), (208.2, -303.2), (223.8, -303.2)]
for idx, (tx, ty) in enumerate(turret_coords):
    create_cylinder(f"PMU_Tower_Turret_{idx}", tx, ty, 24.0, 28.5, 1.2, 8, mat_limestone, col_exterior)

# Tower Crenellated Parapet
create_box("PMU_Tower_Parapet_Front", 208.0, 224.0, -317.8, -316.4, 25.5, 27.0, mat_limestone, col_exterior)
create_box("PMU_Tower_Parapet_West", 208.0, 209.4, -317.8, -303.0, 25.5, 27.0, mat_limestone, col_exterior)
create_box("PMU_Tower_Parapet_East", 222.6, 224.0, -317.8, -303.0, 25.5, 27.0, mat_limestone, col_exterior)

# West Wing (X: 165.7 to 195.0, Y: -300.0 to -215.0)
create_box("PMU_Base_West", 165.7, 167.1, -300.0, -215.0, 0.0, 1.5, mat_limestone, col_exterior)
create_box("PMU_Wall_West", 165.7, 167.1, -300.0, -215.0, 4.2, 18.2, mat_brick, col_exterior)
# Ground Floor Gothic Loggia / Arcade along West Facade (Z: 0.0 to 4.2m)
# 8 Arched Openings facing Stewart Center
for i in range(9):
    py = -300.0 + i * (85.0 / 8.0)
    create_box(f"PMU_Loggia_Pier_{i}", 165.7, 167.5, py - 0.6, py + 0.6, 0.0, 4.2, mat_limestone, col_exterior)
create_box("PMU_Loggia_Spandrel", 165.7, 167.5, -300.0, -215.0, 3.6, 4.2, mat_limestone, col_exterior)
create_box("PMU_Loggia_Floor", 165.7, 172.0, -300.0, -215.0, 0.0, 0.2, mat_limestone, col_exterior)
create_box("PMU_Loggia_Ceiling", 165.7, 172.0, -300.0, -215.0, 4.0, 4.2, mat_limestone, col_exterior)

# East Wing along Grant Street (X: 236.0 to 265.9, Y: -300.0 to -215.0)
create_box("PMU_Base_East", 264.5, 265.9, -300.0, -215.0, 0.0, 1.5, mat_limestone, col_exterior)
create_box("PMU_Wall_East", 264.5, 265.9, -300.0, -215.0, 1.5, 18.2, mat_brick, col_exterior)

# North Facade Walls (Y: -210.7 to -209.3, X: 165.7 to 265.9)
create_box("PMU_Base_North", 165.7, 265.9, -210.7, -209.3, 0.0, 1.5, mat_limestone, col_exterior)
create_box("PMU_Wall_North", 165.7, 265.9, -210.7, -209.3, 1.5, 18.2, mat_brick, col_exterior)

# Beltcourses on all wings (Bedford Limestone)
for bz in [4.2, 8.8, 13.5, 18.2]:
    create_box(f"PMU_Beltcourse_South_{bz}", 184.8, 246.2, -317.4, -315.6, bz - 0.2, bz + 0.2, mat_limestone, col_exterior)
    create_box(f"PMU_Beltcourse_West_{bz}", 165.5, 167.3, -300.2, -214.8, bz - 0.2, bz + 0.2, mat_limestone, col_exterior)
    create_box(f"PMU_Beltcourse_East_{bz}", 264.3, 266.1, -300.2, -214.8, bz - 0.2, bz + 0.2, mat_limestone, col_exterior)

# Gabled Slate Roofs
# Central South Wing Gable (Ridge along Y: X: 185.0 to 246.0, Y: -316.0 to -260.0)
create_gable_roof("PMU_Roof_South_Wing", 185.0, 246.0, -316.0, -260.0, 18.2, 23.5, mat_slate, col_exterior, axis='Y')
# West Wing Gable (Ridge along Y: X: 165.7 to 195.0, Y: -300.0 to -215.0)
create_gable_roof("PMU_Roof_West_Wing", 165.7, 195.0, -300.0, -215.0, 18.2, 22.8, mat_slate, col_exterior, axis='Y')
# East Wing Gable (Ridge along Y: X: 236.0 to 265.9, Y: -300.0 to -215.0)
create_gable_roof("PMU_Roof_East_Wing", 236.0, 265.9, -300.0, -215.0, 18.2, 22.8, mat_slate, col_exterior, axis='Y')
# North Connecting Gable (Ridge along X: X: 185.0 to 246.0, Y: -245.0 to -210.0)
create_gable_roof("PMU_Roof_North_Wing", 185.0, 246.0, -245.0, -210.0, 18.2, 22.5, mat_slate, col_exterior, axis='X')

# Gothic Windows & Stained Glass on South Facade (Great Hall Windows at Z = 5.5 to 11.5m)
for idx, wx in enumerate([189.0, 195.0, 201.0, 229.0, 235.0, 241.0]):
    # Window Frame & Mullions
    create_box(f"PMU_Window_Frame_S_{idx}", wx - 1.6, wx + 1.6, -317.4, -315.6, 5.5, 11.5, mat_limestone, col_exterior)
    create_box(f"PMU_Window_Glass_S_{idx}", wx - 1.3, wx + 1.3, -316.7, -316.3, 5.8, 11.2, mat_stained, col_exterior)

# West Facade Gothic Casement Windows
for idx, wy in enumerate(range(-290, -220, 12)):
    for wz in [5.5, 10.0, 14.5]:
        create_box(f"PMU_Win_W_{idx}_{wz}", 165.5, 167.3, wy - 1.5, wy + 1.5, wz, wz + 2.8, mat_limestone, col_exterior)
        create_box(f"PMU_Glass_W_{idx}_{wz}", 166.2, 166.6, wy - 1.2, wy + 1.2, wz + 0.2, wz + 2.6, mat_glass, col_exterior)

# Oriel Bay Windows on South-East and South-West corners
for ox, oy, name in [(187.0, -317.0, "SW"), (244.0, -317.0, "SE")]:
    create_box(f"PMU_Oriel_{name}_Base", ox - 2.5, ox + 2.5, oy - 2.0, oy, 4.0, 5.2, mat_limestone, col_exterior)
    create_box(f"PMU_Oriel_{name}_Body", ox - 2.5, ox + 2.5, oy - 2.0, oy, 5.2, 12.0, mat_limestone, col_exterior)
    create_box(f"PMU_Oriel_{name}_Glass", ox - 2.2, ox + 2.2, oy - 2.1, oy - 1.9, 5.8, 11.4, mat_glass, col_exterior)
    create_box(f"PMU_Oriel_{name}_Roof", ox - 2.6, ox + 2.6, oy - 2.2, oy + 0.2, 12.0, 13.5, mat_slate, col_exterior)

# 3D Gold Building Signage above South Entrance Portal
create_3d_text("PMU_Sign_South_Portico", "PURDUE  MEMORIAL  UNION", (216.0, -318.0, 8.2), (math.radians(90), 0, 0), 0.75, mat_gold_text, col_exterior, extrude=0.04)

print("Exterior composition completed successfully.")

# 6. Build PMU Interior Architecture: The Great Hall & The 2021 Dining Court
print("Building PMU Interiors...")

# --- THE GREAT HALL OF THE UNION (Floor 1 / Main Floor, Z = 4.2m to 14.5m) ---
# Room Dimensions: X: [194.0, 238.0] (width 44m), Y: [-310.0, -276.0] (depth 34m)
gh_x_min, gh_x_max = 194.0, 238.0
gh_y_min, gh_y_max = -310.0, -276.0
gh_z_floor = 4.20
gh_z_ceil = 14.20

# Great Hall Parquet Hardwood Floor
create_box("PMU_GreatHall_Floor_Parquet", gh_x_min, gh_x_max, gh_y_min, gh_y_max, gh_z_floor, gh_z_floor + 0.15, mat_parquet, col_interiors)
# Great Hall Dark Oak Timber Ceiling Slab
create_box("PMU_GreatHall_Ceiling_Timber", gh_x_min, gh_x_max, gh_y_min, gh_y_max, gh_z_ceil - 0.3, gh_z_ceil, mat_timber, col_interiors)

# Great Hall Dark Oak Wainscoting on perimeter walls (Z: 4.35 to 7.5m)
create_box("PMU_GH_Wainscot_North", gh_x_min, gh_x_max, gh_y_max - 0.4, gh_y_max, gh_z_floor + 0.15, 7.5, mat_timber, col_interiors)
create_box("PMU_GH_Wainscot_South", gh_x_min, gh_x_max, gh_y_min, gh_y_min + 0.4, gh_z_floor + 0.15, 7.5, mat_timber, col_interiors)
create_box("PMU_GH_Wainscot_West", gh_x_min, gh_x_min + 0.4, gh_y_min, gh_y_max, gh_z_floor + 0.15, 7.5, mat_timber, col_interiors)
create_box("PMU_GH_Wainscot_East", gh_x_max - 0.4, gh_x_max, gh_y_min, gh_y_max, gh_z_floor + 0.15, 7.5, mat_timber, col_interiors)

# SACRED PURDUE MEMORIAL UNION FLOOR CREST (Center of Great Hall: X=216.0, Y=-293.0)
# Students walk around this medallion in solemn reverence
crest_cx, crest_cy = 216.0, -293.0
create_cylinder("PMU_Memorial_Crest_Outer_Ring", crest_cx, crest_cy, gh_z_floor + 0.15, gh_z_floor + 0.165, 2.8, 48, mat_crest_gold, col_interiors)
create_cylinder("PMU_Memorial_Crest_Inner_Black", crest_cx, crest_cy, gh_z_floor + 0.165, gh_z_floor + 0.175, 2.5, 48, mat_crest_black, col_interiors)
# Gold Memorial Cross Inlay
create_box("PMU_Memorial_Cross_V", crest_cx - 0.35, crest_cx + 0.35, crest_cy - 1.8, crest_cy + 1.8, gh_z_floor + 0.175, gh_z_floor + 0.185, mat_crest_gold, col_interiors)
create_box("PMU_Memorial_Cross_H", crest_cx - 1.4, crest_cx + 1.4, crest_cy - 0.35, crest_cy + 0.35, gh_z_floor + 0.175, gh_z_floor + 0.185, mat_crest_gold, col_interiors)
create_cylinder("PMU_Memorial_Cross_Center", crest_cx, crest_cy, gh_z_floor + 0.18, gh_z_floor + 0.19, 0.7, 24, mat_crest_gold, col_interiors)

# Timber Hammerbeam Roof Trusses (6 trusses spanning North-South across X)
for idx, tx in enumerate(range(198, 236, 7)):
    create_box(f"PMU_Hammerbeam_Beam_{idx}", tx - 0.35, tx + 0.35, gh_y_min, gh_y_max, gh_z_ceil - 1.4, gh_z_ceil - 0.3, mat_timber, col_interiors)
    create_box(f"PMU_Hammerbeam_PostL_{idx}", tx - 0.35, tx + 0.35, gh_y_min, gh_y_min + 3.0, gh_z_ceil - 2.8, gh_z_ceil - 1.4, mat_timber, col_interiors)
    create_box(f"PMU_Hammerbeam_PostR_{idx}", tx - 0.35, tx + 0.35, gh_y_max - 3.0, gh_y_max, gh_z_ceil - 2.8, gh_z_ceil - 1.4, mat_timber, col_interiors)

# Monumental Limestone Fireplace on North Wall (X: 211.5 to 220.5, Y: -277.5 to -276.0)
create_box("PMU_Fireplace_Hearth", 210.5, 221.5, -278.2, -276.0, gh_z_floor + 0.15, gh_z_floor + 0.45, mat_limestone, col_interiors)
create_box("PMU_Fireplace_Jamb_L", 211.0, 212.8, -277.5, -276.0, gh_z_floor + 0.45, 8.5, mat_limestone, col_interiors)
create_box("PMU_Fireplace_Jamb_R", 219.2, 221.0, -277.5, -276.0, gh_z_floor + 0.45, 8.5, mat_limestone, col_interiors)
create_box("PMU_Fireplace_Mantel", 210.0, 222.0, -278.0, -276.0, 7.8, 8.6, mat_limestone, col_interiors)
create_box("PMU_Fireplace_Overmantel", 211.5, 220.5, -277.2, -276.0, 8.6, 13.0, mat_limestone, col_interiors)
# Fireplace Firebox & Glowing Embers
create_box("PMU_Fireplace_Firebox", 212.8, 219.2, -277.0, -276.0, gh_z_floor + 0.45, 7.2, mat_crest_black, col_interiors)
create_box("PMU_Fireplace_Embers", 213.5, 218.5, -276.8, -276.1, gh_z_floor + 0.45, gh_z_floor + 0.85, mat_ember, col_interiors)

# Fireplace Point Light
light_data = bpy.data.lights.new(name="PMU_Fireplace_Flame_Light", type='POINT')
light_data.energy = 850.0
light_data.color = (1.0, 0.45, 0.12)
light_data.shadow_soft_size = 0.4
light_obj = bpy.data.objects.new(name="PMU_Fireplace_Flame_Light", object_data=light_data)
light_obj.location = (216.0, -276.4, gh_z_floor + 1.2)
col_interiors.objects.link(light_obj)

# 4 Wrought-Iron Gothic Chandeliers suspended from Hammerbeams
ch_coords = [(205.0, -300.0), (227.0, -300.0), (205.0, -286.0), (227.0, -286.0)]
for idx, (cx, cy) in enumerate(ch_coords):
    create_cylinder(f"PMU_Chandelier_Ring_{idx}", cx, cy, 9.5, 9.7, 1.4, 16, mat_timber, col_interiors)
    create_box(f"PMU_Chandelier_Chain_{idx}", cx - 0.05, cx + 0.05, cy - 0.05, cy + 0.05, 9.7, gh_z_ceil - 0.5, mat_bronze, col_interiors)
    # Candle Glow Luminaires
    for ci in range(6):
        ca = 2.0 * math.pi * ci / 6
        lx = cx + 1.2 * math.cos(ca)
        ly = cy + 1.2 * math.sin(ca)
        create_cylinder(f"PMU_Candle_{idx}_{ci}", lx, ly, 9.7, 10.1, 0.08, 8, mat_crest_gold, col_interiors)
    # Warm Point Light
    cld = bpy.data.lights.new(name=f"PMU_Chandelier_Light_{idx}", type='POINT')
    cld.energy = 1600.0
    cld.color = (1.0, 0.88, 0.65)
    cld.shadow_soft_size = 0.6
    clo = bpy.data.objects.new(name=f"PMU_Chandelier_Light_{idx}", object_data=cld)
    clo.location = (cx, cy, 9.3)
    col_interiors.objects.link(clo)

# Great Hall Chesterfield Leather Lounges & Study Tables
# Flanking lounge zones
for idx, sy in enumerate([-304.0, -282.0]):
    # Leather Chesterfield Sofas
    create_box(f"PMU_Chesterfield_W_{idx}", 197.0, 203.0, sy - 1.2, sy + 1.2, gh_z_floor + 0.15, gh_z_floor + 1.1, mat_booth, col_interiors)
    create_box(f"PMU_Chesterfield_E_{idx}", 229.0, 235.0, sy - 1.2, sy + 1.2, gh_z_floor + 0.15, gh_z_floor + 1.1, mat_booth, col_interiors)
    # Coffee Tables
    create_box(f"PMU_CoffeeTable_W_{idx}", 198.0, 202.0, sy + 1.8, sy + 2.8, gh_z_floor + 0.15, gh_z_floor + 0.65, mat_timber, col_interiors)
    create_box(f"PMU_CoffeeTable_E_{idx}", 230.0, 234.0, sy + 1.8, sy + 2.8, gh_z_floor + 0.15, gh_z_floor + 0.65, mat_timber, col_interiors)

# Study Tables with Brass Banker's Lamps
for idx, ty in enumerate([-302.0, -284.0]):
    create_box(f"PMU_StudyTable_W_{idx}", 206.0, 210.0, ty - 1.4, ty + 1.4, gh_z_floor + 0.15, gh_z_floor + 0.95, mat_timber, col_interiors)
    create_box(f"PMU_StudyTable_E_{idx}", 222.0, 226.0, ty - 1.4, ty + 1.4, gh_z_floor + 0.15, gh_z_floor + 0.95, mat_timber, col_interiors)
    # Banker's lamp glow
    create_box(f"PMU_BankerLamp_W_{idx}", 207.8, 208.2, ty - 0.2, ty + 0.2, gh_z_floor + 0.95, gh_z_floor + 1.35, mat_stained, col_interiors)
    create_box(f"PMU_BankerLamp_E_{idx}", 223.8, 224.2, ty - 0.2, ty + 0.2, gh_z_floor + 0.95, gh_z_floor + 1.35, mat_stained, col_interiors)

# --- THE PMU GROUND FLOOR DINING COURT (2021 TRANSFORMATION, Z = 0.0m to 4.2m) ---
# Room Dimensions: X: [192.0, 242.0] (width 50m), Y: [-268.0, -225.0] (depth 43m)
dc_x_min, dc_x_max = 192.0, 242.0
dc_y_min, dc_y_max = -268.0, -225.0
dc_z_floor = 0.05
dc_z_ceil = 4.10

# Polished Terrazzo Flooring
create_box("PMU_Dining_Floor_Terrazzo", dc_x_min, dc_x_max, dc_y_min, dc_y_max, dc_z_floor, dc_z_floor + 0.1, mat_terrazzo, col_interiors)
create_box("PMU_Dining_Ceiling_Industrial", dc_x_min, dc_x_max, dc_y_min, dc_y_max, dc_z_ceil - 0.1, dc_z_ceil, mat_timber, col_interiors)

# Historic Structural Stone Arches dividing dining hall (Pillars at X: 204, 216, 228)
for px in [204.0, 216.0, 228.0]:
    for py in [-260.0, -245.0, -230.0]:
        create_box(f"PMU_Dining_Arch_Pillar_{px}_{py}", px - 0.6, px + 0.6, py - 0.6, py + 0.6, dc_z_floor + 0.1, dc_z_ceil - 0.1, mat_limestone, col_interiors)

# Restaurant Counter Bays:
# 1. Walk-On's Sports Bistreaux (West flank: X: 193.0 to 195.0, Y: -264.0 to -248.0)
create_box("PMU_WalkOns_Counter", 193.0, 195.2, -264.0, -248.0, dc_z_floor + 0.1, dc_z_floor + 1.25, mat_timber, col_interiors)
create_box("PMU_WalkOns_Top", 192.8, 195.4, -264.2, -247.8, dc_z_floor + 1.20, dc_z_floor + 1.28, mat_limestone, col_interiors)
# 4 TV Monitors above Walk-On's counter
for tv_i, tvy in enumerate(range(-262, -248, 4)):
    create_box(f"PMU_WalkOns_TV_{tv_i}", 194.2, 194.6, tvy - 1.2, tvy + 1.2, 2.6, 3.8, mat_glass, col_interiors)

# 2. BBQ District (North-West flank: X: 198.0 to 214.0, Y: -227.0 to -225.2)
create_box("PMU_BBQ_Counter", 198.0, 214.0, -227.0, -225.2, dc_z_floor + 0.1, dc_z_floor + 1.25, mat_steel, col_interiors)
create_box("PMU_BBQ_Top", 197.8, 214.2, -227.2, -225.0, dc_z_floor + 1.20, dc_z_floor + 1.28, mat_limestone, col_interiors)
create_box("PMU_BBQ_MenuBoard", 200.0, 212.0, -226.5, -226.3, 2.8, 3.8, mat_stained, col_interiors)

# 3. Zen Asian Bowls (North-East flank: X: 220.0 to 236.0, Y: -227.0 to -225.2)
create_box("PMU_Zen_Counter", 220.0, 236.0, -227.0, -225.2, dc_z_floor + 0.1, dc_z_floor + 1.25, mat_timber, col_interiors)
create_box("PMU_Zen_Top", 219.8, 236.2, -227.2, -225.0, dc_z_floor + 1.20, dc_z_floor + 1.28, mat_limestone, col_interiors)
create_box("PMU_Zen_Slatted_Canopy", 219.5, 236.5, -228.0, -225.0, 3.2, 3.5, mat_timber, col_interiors)

# 4. Starbucks Kiosk (East flank: X: 239.0 to 241.0, Y: -264.0 to -250.0)
create_box("PMU_Starbucks_Counter", 239.0, 241.0, -264.0, -250.0, dc_z_floor + 0.1, dc_z_floor + 1.25, mat_timber, col_interiors)
create_box("PMU_Starbucks_Top", 238.8, 241.2, -264.2, -249.8, dc_z_floor + 1.20, dc_z_floor + 1.28, mat_limestone, col_interiors)
create_box("PMU_Starbucks_PastryCase", 239.2, 240.8, -258.0, -254.0, dc_z_floor + 1.28, dc_z_floor + 2.0, mat_glass, col_interiors)

# Central Seating: Bar-height community tables with stools
for idx, cy in enumerate([-255.0, -242.0, -232.0]):
    create_box(f"PMU_CommunityTable_{idx}", 210.0, 222.0, cy - 0.6, cy + 0.6, dc_z_floor + 0.1, dc_z_floor + 1.15, mat_timber, col_interiors)
    # Stools
    for sx in range(211, 222, 2):
        create_cylinder(f"PMU_Stool_S_{idx}_{sx}", sx, cy - 1.1, dc_z_floor + 0.1, dc_z_floor + 0.85, 0.22, 12, mat_steel, col_interiors)
        create_cylinder(f"PMU_Stool_N_{idx}_{sx}", sx, cy + 1.1, dc_z_floor + 0.1, dc_z_floor + 0.85, 0.22, 12, mat_steel, col_interiors)

# Modern Industrial Pendant Lights in Dining Court
for px in [205.0, 216.0, 227.0]:
    for py in [-255.0, -242.0, -232.0]:
        create_box(f"PMU_Pendant_Cord_{px}_{py}", px - 0.03, px + 0.03, py - 0.03, py + 0.03, 2.8, dc_ceil - 0.1 if 'dc_ceil' in locals() else dc_z_ceil - 0.1, mat_crest_black, col_interiors)
        create_cylinder(f"PMU_Pendant_Shade_{px}_{py}", px, py, 2.5, 2.8, 0.35, 12, mat_crest_black, col_interiors)
        # Downlight
        pld = bpy.data.lights.new(name=f"PMU_Dining_Light_{px}_{py}", type='POINT')
        pld.energy = 650.0
        pld.color = (1.0, 0.95, 0.85)
        pld.shadow_soft_size = 0.5
        plo = bpy.data.objects.new(name=f"PMU_Dining_Light_{px}_{py}", object_data=pld)
        plo.location = (px, py, 2.4)
        col_interiors.objects.link(plo)

print("Interiors completed successfully.")

# 7. Build PMU Grand Terrace, Balustrade Stairs & West Courtyard Site
print("Building PMU Site Hardscape & Plazas...")

# South Grand Entrance Terrace along State Street (X: 198.0 to 234.0, Y: -328.0 to -317.8)
create_box("PMU_Terrace_Plaza_Deck", 198.0, 234.0, -328.0, -317.8, 0.0, 1.2, mat_limestone, col_site)
# Grand Stepped Balustrade Stairs leading down to State Street sidewalk (Y: -334.0 to -328.0)
for step_i in range(6):
    sy_min = -334.0 + step_i * 1.0
    sy_max = -328.0
    sz_top = 0.2 + step_i * 0.2
    create_box(f"PMU_Grand_Stairs_{step_i}", 206.0, 226.0, sy_min, sy_max, 0.0, sz_top, mat_limestone, col_site)

# Limestone Balustrade flanking stairs
create_box("PMU_Balustrade_West", 204.8, 205.8, -334.0, -317.8, 0.0, 2.3, mat_limestone, col_site)
create_box("PMU_Balustrade_East", 226.2, 227.2, -334.0, -317.8, 0.0, 2.3, mat_limestone, col_site)

# West Courtyard between PMU and Stewart Center (X: 145.0 to 165.7, Y: -300.0 to -215.0)
create_box("PMU_West_Courtyard_Paving", 145.0, 165.7, -300.0, -215.0, 0.0, 0.08, mat_granite, col_site)
# Central Lawn Panels in West Courtyard
create_box("PMU_West_Lawn_Panel_S", 147.0, 160.0, -290.0, -260.0, 0.08, 0.18, mat_limestone, col_site)
create_box("PMU_West_Lawn_Panel_N", 147.0, 160.0, -250.0, -225.0, 0.08, 0.18, mat_limestone, col_site)

# Curved Limestone Seatwalls in West Courtyard
for sw_i, swy in enumerate([-275.0, -238.0]):
    create_box(f"PMU_Seatwall_W_{sw_i}", 150.0, 158.0, swy - 0.6, swy + 0.6, 0.08, 0.65, mat_limestone, col_site)

# Teak Benches & Bike Racks in West Courtyard
for b_i, by in enumerate([-285.0, -265.0, -245.0, -230.0]):
    create_box(f"PMU_Teak_Bench_{b_i}", 162.5, 164.5, by - 0.4, by + 0.4, 0.08, 0.55, mat_timber, col_site)

# Victorian Cast-Iron Lantern Posts along West Walkway & South Terrace
lantern_coords = [
    (163.5, -295.0), (163.5, -270.0), (163.5, -245.0), (163.5, -220.0),
    (202.0, -326.0), (230.0, -326.0)
]
for idx, (lx, ly) in enumerate(lantern_coords):
    create_cylinder(f"PMU_Lantern_Post_{idx}", lx, ly, 0.08, 3.8, 0.12, 8, mat_crest_black, col_site)
    create_box(f"PMU_Lantern_Head_{idx}", lx - 0.3, lx + 0.3, ly - 0.3, ly + 0.3, 3.8, 4.4, mat_lantern, col_site)
    # Warm Luminaire Light
    lld = bpy.data.lights.new(name=f"PMU_Lantern_Light_{idx}", type='POINT')
    lld.energy = 550.0
    lld.color = (1.0, 0.88, 0.65)
    lld.shadow_soft_size = 0.3
    llo = bpy.data.objects.new(name=f"PMU_Lantern_Light_{idx}", object_data=lld)
    llo.location = (lx, ly, 4.1)
    col_site.objects.link(llo)

print("Site hardscape and courtyard completed.")

# 8. Create and Calibrate 5 Dedicated Inspection Cameras
print("Setting up Inspection Cameras...")

cameras_data = [
    ("Cam_67_PMU_StateStreet_South_Hero", Vector((216.0, -355.0, 4.5)), Vector((216.0, -305.0, 14.0)), 28.0),
    ("Cam_68_PMU_GreatHall_MemorialCross_Interior", Vector((202.0, -302.0, 5.6)), Vector((216.0, -290.0, 5.0)), 24.0),
    ("Cam_69_PMU_DiningCourt_Commons_Interior", Vector((201.0, -262.0, 1.8)), Vector((218.0, -244.0, 1.8)), 24.0),
    ("Cam_70_PMU_WestCourtyard_Stewart_Interface", Vector((142.0, -275.0, 4.2)), Vector((175.0, -260.0, 10.0)), 32.0),
    ("Cam_71_PMU_StateStreet_GrantStreet_Aerial", Vector((310.0, -370.0, 68.0)), Vector((216.0, -263.0, 12.0)), 35.0)
]

for cam_name, loc, target, focal_len in cameras_data:
    old_cam = bpy.data.objects.get(cam_name)
    if old_cam:
        bpy.data.objects.remove(old_cam, do_unlink=True)
    
    cam_data = bpy.data.cameras.new(cam_name)
    cam_data.lens = focal_len
    cam_data.clip_start = 0.1
    cam_data.clip_end = 2000.0
    
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    cam_obj.location = loc
    direction = target - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    col_cams.objects.link(cam_obj)
    print(f"Calibrated camera {cam_name}")

# Save master file
master_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_path)
print(f"Master file saved to {master_path}")
print("--- PMU Construction Script Completed Successfully ---")
