import bpy
import math
from mathutils import Vector, Euler

# 1. Shift Weist Plaza objects to X = -185.0, Y = 718.0 (clear of BRES, along Northwestern Ave corridor)
col_plaza = bpy.data.collections.get("44_Mackey_Arena_WoodenPlaza_and_Site")
if col_plaza:
    # Original plaza center was around (-241.59, 715.70)
    # Target center: (-185.0, 718.0) -> dx = 56.59, dy = 2.30
    dx = 56.59
    dy = 2.30
    for obj in col_plaza.objects:
        obj.location.x += dx
        obj.location.y += dy
    print(f"Shifted {len(col_plaza.objects)} plaza objects by dx={dx}, dy={dy}")

# 2. Update Cam_62 to frame the new plaza and Wooden statue
cam62 = bpy.data.objects.get("Cam_62_Mackey_Arena_North_WoodenPlaza_Hero")
if cam62:
    cam62.location = Vector((-172.0, 736.0, 2.8))
    # Look at statue at roughly (-185.0, 714.0, 2.0)
    target = Vector((-185.0, 714.0, 2.0))
    direction = target - cam62.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam62.rotation_euler = rot_quat.to_euler()
    cam62.data.lens = 32
    print("Updated Cam 62 position and orientation")

# 3. Refine Hardwood Maple Material
mat_maple = bpy.data.materials.get("MACK_Keady_Hardwood_Maple")
if mat_maple and mat_maple.node_tree:
    bsdf = mat_maple.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.92, 0.72, 0.44, 1.0) # warm honey amber
        bsdf.inputs["Roughness"].default_value = 0.08 # polished polyurethane
        print("Updated Keady Court hardwood material to warm honey amber")

# 4. Refine Glass Material for Backboards
mat_glass = bpy.data.materials.get("MACK_Clear_Tempered_Glass")
if mat_glass and mat_glass.node_tree:
    bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Transmission Weight"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.02
        bsdf.inputs["IOR"].default_value = 1.52
        mat_glass.blend_method = 'BLEND'
        print("Updated Backboard glass material with true transmission")

# 5. Add Text to Scoreboard Faces
col_interiors = bpy.data.collections.get("43_Mackey_Arena_Interiors_and_Court")

def get_or_create_mat(name, color, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = color
        if emission_strength > 0:
            bsdf.inputs["Emission Color"].default_value = color[:3] + (1.0,)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_led_white = get_or_create_mat("MACK_Scoreboard_LED_White", (1.0, 1.0, 1.0, 1.0), emission_strength=5.0)
mat_led_gold = get_or_create_mat("MACK_Scoreboard_LED_Gold", (0.98, 0.84, 0.25, 1.0), emission_strength=5.0)
mat_banner_gold = get_or_create_mat("MACK_Banner_Text_Gold", (0.98, 0.84, 0.25, 1.0), emission_strength=1.5)
mat_banner_white = get_or_create_mat("MACK_Banner_Text_White", (1.0, 1.0, 1.0, 1.0), emission_strength=1.5)

def create_3d_text(name, text, loc, rot, size, mat, collection, extrude=0.02):
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

# Scoreboard text at Z = 16.5m (Mackey Center is X = -209.59, Y = 657.70)
# Scoreboard main body is roughly 9.5m x 9.5m (half-width 4.75m)
mx = -209.59
my = 657.70
sz = 16.5
d_off = 4.80 # distance from center to display face

# South Face (facing -Y)
create_3d_text("MACK_SB_Score_South", "PURDUE  78   INDIANA  59", (mx, my - d_off, sz + 0.6), (math.radians(90), 0, 0), 0.70, mat_led_white, col_interiors)
create_3d_text("MACK_SB_Clock_South", "2nd Half   4:12   BONUS", (mx, my - d_off, sz - 0.7), (math.radians(90), 0, 0), 0.55, mat_led_gold, col_interiors)

# North Face (facing +Y)
create_3d_text("MACK_SB_Score_North", "PURDUE  78   INDIANA  59", (mx, my + d_off, sz + 0.6), (math.radians(90), 0, math.radians(180)), 0.70, mat_led_white, col_interiors)
create_3d_text("MACK_SB_Clock_North", "2nd Half   4:12   BONUS", (mx, my + d_off, sz - 0.7), (math.radians(90), 0, math.radians(180)), 0.55, mat_led_gold, col_interiors)

# East Face (facing +X)
create_3d_text("MACK_SB_Score_East", "PURDUE  78   INDIANA  59", (mx + d_off, my, sz + 0.6), (math.radians(90), 0, math.radians(270)), 0.70, mat_led_white, col_interiors)
create_3d_text("MACK_SB_Clock_East", "2nd Half   4:12   BONUS", (mx + d_off, my, sz - 0.7), (math.radians(90), 0, math.radians(270)), 0.55, mat_led_gold, col_interiors)

# West Face (facing -X)
create_3d_text("MACK_SB_Score_West", "PURDUE  78   INDIANA  59", (mx - d_off, my, sz + 0.6), (math.radians(90), 0, math.radians(90)), 0.70, mat_led_white, col_interiors)
create_3d_text("MACK_SB_Clock_West", "2nd Half   4:12   BONUS", (mx - d_off, my, sz - 0.7), (math.radians(90), 0, math.radians(90)), 0.55, mat_led_gold, col_interiors)

print("Created 3D live scoreboards on all 4 faces")

# 6. Add Jersey Numbers & Names onto Banner Slabs
banners_info = [
    ("MACK_Banner_Slab_Edey_15", "15", "EDEY"),
    ("MACK_Banner_Slab_Robinson_13", "13", "ROBINSON"),
    ("MACK_Banner_Slab_Mount_10", "10", "MOUNT"),
    ("MACK_Banner_Slab_Carroll_20", "20", "CARROLL"),
    ("MACK_Banner_Slab_Gearlds_3", "3", "GEARLDS"),
    ("MACK_Banner_Slab_White_22", "22", "WHITE"),
    ("MACK_Banner_Slab_Dischinger_43", "43", "DISCHINGER"),
    ("MACK_Banner_Slab_Wooden_13", "13", "WOODEN"),
    ("MACK_Banner_Slab_NCAA_2024", "2024", "FINAL FOUR"),
]

for slab_name, num_txt, name_txt in banners_info:
    slab = bpy.data.objects.get(slab_name)
    if slab:
        sloc = slab.location
        srot = slab.rotation_euler
        # Forward vector from rotation
        mat_rot = srot.to_matrix()
        # Normal to the banner face is roughly Y-axis local (or X-axis local)
        # Let's inspect slab rotation: srot.z = math.radians(angle)
        # In build script, banners were rotated around Z by angle.
        # Place text slightly in front of slab (0.04m)
        angle = srot.z
        # Normal facing outward
        norm_x = math.cos(angle)
        norm_y = math.sin(angle)
        
        # Front face
        t_loc_num = (sloc.x + 0.05 * norm_x, sloc.y + 0.05 * norm_y, sloc.z + 0.6)
        t_loc_name = (sloc.x + 0.05 * norm_x, sloc.y + 0.05 * norm_y, sloc.z - 0.6)
        t_rot = (math.radians(90), 0, angle + math.radians(90))
        create_3d_text(f"Text_{slab_name}_Num", num_txt, t_loc_num, t_rot, 0.70, mat_banner_gold, col_interiors, extrude=0.01)
        create_3d_text(f"Text_{slab_name}_Name", name_txt, t_loc_name, t_rot, 0.35, mat_banner_white, col_interiors, extrude=0.01)

print("Created 3D text labels for all 9 Ring of Honor banners")

# Save master blend file
master_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_path)
print(f"Master file successfully saved to {master_path}")
