import bpy
import bmesh
import mathutils
import math

def upgrade_bell_tower_pass4():
    col_name = "04_Purdue_Bell_Tower_Detailed"
    if col_name not in bpy.data.collections:
        print(f"Collection {col_name} not found.")
        return
        
    col = bpy.data.collections[col_name]
    
    # Bell tower center coordinates
    tx, ty = -31.2, -12.5
    
    # 1. Fetch materials
    mat_brick = bpy.data.materials.get("Purdue_Red_Brick")
    mat_stone = bpy.data.materials.get("Indiana_Bedford_Limestone")
    mat_gold = bpy.data.materials.get("Bell_Tower_Clock_Gold")
    mat_copper = bpy.data.materials.get("Bell_Tower_Aged_Copper")
    mat_bell = bpy.data.materials.get("Carillon_Bronze_Bell")
    
    # Emissive dial backlight material
    mat_clock_glow = bpy.data.materials.get("Bell_Tower_Clock_Glow")
    if not mat_clock_glow:
        mat_clock_glow = bpy.data.materials.new(name="Bell_Tower_Clock_Glow")
        mat_clock_glow.use_nodes = True
        bsdf = next((n for n in mat_clock_glow.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (1.0, 0.98, 0.92, 1.0)
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (1.0, 0.95, 0.85, 1.0)
                bsdf.inputs["Emission Strength"].default_value = 1.8
                
    # 2. Re-sculpt Base with 4 Open Arched Breezeways ("Superstition Archways")
    # Instead of a solid plinth, 4 corner stone/brick piers creating a cruciform walk-through tunnel!
    pier_w = 1.8
    pier_span = 2.4
    arch_h = 6.2
    
    # Remove old solid base if present
    for obj_name in ["Bell_Tower_Limestone_Plinth", "Bell_Tower_Brick_Shaft"]:
        if obj_name in col.objects:
            obj = col.objects[obj_name]
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # Ground Base Plinth (4 corner L-shaped pedestals)
    for px in [-pier_span, pier_span]:
        for py in [-pier_span, pier_span]:
            # Limestone water table foot
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx + px, ty + py, 1.0), scale=(pier_w + 0.4, pier_w + 0.4, 2.0))
            p_foot = bpy.context.active_object
            p_foot.name = f"Bell_Tower_Foot_{px}_{py}"
            p_foot.data.materials.append(mat_stone)
            col.objects.link(p_foot)
            bpy.context.scene.collection.objects.unlink(p_foot)
            
            # Brick base pier up to arch spring (z=2.0 to 6.2m)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx + px, ty + py, 4.1), scale=(pier_w, pier_w, 4.2))
            p_brick = bpy.context.active_object
            p_brick.name = f"Bell_Tower_GroundPier_{px}_{py}"
            p_brick.data.materials.append(mat_brick)
            col.objects.link(p_brick)
            bpy.context.scene.collection.objects.unlink(p_brick)
            
    # 4 Arch Keystone Lintels bridging the piers (North, South, East, West)
    arch_span = 3.6
    for angle, ax, ay in [(0, 0, pier_span), (180, 0, -pier_span), (90, pier_span, 0), (270, -pier_span, 0)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(tx + ax, ty + ay, arch_h),
            scale=(pier_w if ax == 0 else 0.8, 0.8 if ax == 0 else pier_w, 0.9)
        )
        arch_l = bpy.context.active_object
        arch_l.name = f"Bell_Tower_ArchLintel_{angle}"
        arch_l.data.materials.append(mat_stone)
        col.objects.link(arch_l)
        bpy.context.scene.collection.objects.unlink(arch_l)
        
    # Bronze Purdue University Seal inlaid on breezeway center floor
    bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=0.06, location=(tx, ty, 0.12), vertices=32)
    seal = bpy.context.active_object
    seal.name = "Purdue_Bronze_Seal_Medallion"
    seal.data.materials.append(mat_gold)
    col.objects.link(seal)
    bpy.context.scene.collection.objects.unlink(seal)
    
    # Upper Main Brick Shaft (from z = 6.6m to 32.0m)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, ty, 19.3), scale=(6.2, 6.2, 25.4))
    shaft = bpy.context.active_object
    shaft.name = "Bell_Tower_Brick_Shaft_Upper"
    shaft.data.materials.append(mat_brick)
    col.objects.link(shaft)
    bpy.context.scene.collection.objects.unlink(shaft)
    
    # 3. Alternating Limestone Corner Quoins along Shaft
    quoin_w = 0.55
    quoin_h = 0.55
    quoin_proj = 3.12
    for q_z in range(8, 30, 2):
        is_long = (q_z % 4 == 0)
        q_len = 0.9 if is_long else 0.5
        for cx in [-1, 1]:
            for cy in [-1, 1]:
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(tx + cx * (quoin_proj - q_len * 0.5), ty + cy * quoin_proj, q_z),
                    scale=(q_len, quoin_w, quoin_h)
                )
                q_obj = bpy.context.active_object
                q_obj.name = f"Quoin_X_{q_z}_{cx}_{cy}"
                q_obj.data.materials.append(mat_stone)
                col.objects.link(q_obj)
                bpy.context.scene.collection.objects.unlink(q_obj)
                
    # 4. Belfry Dentil Brackets (under cornice slabs at z = 34.8m and 41.8m)
    dentil_size = 0.25
    for cornice_z in [34.7, 41.7]:
        for edge_pos in [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]:
            for side in [-3.25, 3.25]:
                # X-facing
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(tx + side, ty + edge_pos, cornice_z),
                    scale=(0.2, dentil_size, dentil_size)
                )
                d_x = bpy.context.active_object
                d_x.name = f"Dentil_{cornice_z}_{side}_{edge_pos}"
                d_x.data.materials.append(mat_stone)
                col.objects.link(d_x)
                bpy.context.scene.collection.objects.unlink(d_x)
                # Y-facing
                bpy.ops.mesh.primitive_cube_add(
                    size=1.0,
                    location=(tx + edge_pos, ty + side, cornice_z),
                    scale=(dentil_size, 0.2, dentil_size)
                )
                d_y = bpy.context.active_object
                d_y.name = f"Dentil_Y_{cornice_z}_{side}_{edge_pos}"
                d_y.data.materials.append(mat_stone)
                col.objects.link(d_y)
                bpy.context.scene.collection.objects.unlink(d_y)
                
    # 5. Upgraded Carillon with Flared Bronze Bells and Steel Suspension Gantry
    belfry_center_z = 38.5
    # Steel suspension I-beams
    for bx in [-1.5, 1.5]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(tx, ty + bx, belfry_center_z + 2.2),
            scale=(5.2, 0.2, 0.3)
        )
        beam = bpy.context.active_object
        beam.name = f"Carillon_GantryBeam_{bx}"
        beam.data.materials.append(mat_gold)
        col.objects.link(beam)
        bpy.context.scene.collection.objects.unlink(beam)
        
    # Bourdon Bell flared lip
    if "Bell_Tower_Bourdon_Bell" in col.objects:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=1.25,
            minor_radius=0.15,
            location=(tx, ty, belfry_center_z - 0.7)
        )
        lip = bpy.context.active_object
        lip.name = "Bourdon_Bell_FlaredLip"
        lip.data.materials.append(mat_bell)
        col.objects.link(lip)
        bpy.context.scene.collection.objects.unlink(lip)
        
    # 6. Clock Backlight & 3D Hands
    clock_z = 32.5
    for cname, ox, oy, rot_z in [("North", 0, 3.14, 0), ("South", 0, -3.14, math.pi), ("East", 3.14, 0, -math.pi/2), ("West", -3.14, 0, math.pi/2)]:
        # Glow dial disc
        bpy.ops.mesh.primitive_cylinder_add(radius=1.28, depth=0.04, location=(tx + ox, ty + oy, clock_z), vertices=32)
        glow_face = bpy.context.active_object
        glow_face.name = f"Clock_Glow_Dial_{cname}"
        glow_face.rotation_euler = (math.pi/2 if ox == 0 else 0, math.pi/2 if oy == 0 else 0, rot_z)
        glow_face.data.materials.append(mat_clock_glow)
        col.objects.link(glow_face)
        bpy.context.scene.collection.objects.unlink(glow_face)
        
        # 3D Clock Hands (Hour & Minute hands)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(tx + ox * 1.03, ty + oy * 1.03, clock_z + 0.3),
            scale=(0.06, 0.04, 0.8) if ox == 0 else (0.04, 0.06, 0.8)
        )
        hand_m = bpy.context.active_object
        hand_m.name = f"Clock_MinuteHand_{cname}"
        hand_m.data.materials.append(mat_gold)
        col.objects.link(hand_m)
        bpy.context.scene.collection.objects.unlink(hand_m)
        
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(tx + ox * 1.03, ty + oy * 1.03 + (0.2 if ox != 0 else 0), clock_z),
            scale=(0.08, 0.04, 0.5) if ox == 0 else (0.04, 0.08, 0.5)
        )
        hand_h = bpy.context.active_object
        hand_h.name = f"Clock_HourHand_{cname}"
        hand_h.data.materials.append(mat_gold)
        col.objects.link(hand_h)
        bpy.context.scene.collection.objects.unlink(hand_h)
        
    print("Pass 4 Bell Tower Gold Standard Upgrades Applied Successfully!")

if __name__ == "__main__":
    upgrade_bell_tower_pass4()
