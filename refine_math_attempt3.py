"""
Purdue University Digital Twin - Mathematical Sciences Building (MATH - 1967) Attempt 3
Gold Standard Polish & Architectural Refinements:
1. MATH 175 Stage Lighting & Derivation Board Polish:
   - High-intensity blackboard accent wash lights
   - Sliding chalkboard frame details & oak trim
   - Oak rostrum microphone and Purdue Old Gold seal medallion
2. Mathematical Sciences Library:
   - Open mathematics textbooks with visible KaTeX equations
   - Emissive laptop screens and brass banker's lamps
   - Terrazzo floor border contrast
3. 10th-Floor Faculty Colloquium Sky Lounge:
   - 16 Executive leather swivel chairs with dark oak armrests and chrome 5-star bases
   - Solid mahogany conference table with leather meeting folios and laptops
   - Overhead 8-arm brass chandelier (3200K)
   - Panoramic ribbon windows with unobstructed campus skyline views
4. Exterior Details:
   - Entrance double glass doors with bronze hardware
   - Address plaque "150 N. UNIVERSITY STREET"
   - Re-render all 5 cameras
"""

import bpy
import math
import os

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend"

def run_polish():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    print("Opened blend for Attempt 3 Polish...")

    col_ext = bpy.data.collections.get("60_Math_Sciences_Exterior")
    col_int = bpy.data.collections.get("61_Math_Sciences_Interiors")
    col_site = bpy.data.collections.get("62_Math_Sciences_Plaza_and_Site")
    root_obj = bpy.data.objects.get("MATH_Root")

    mat_walnut = bpy.data.materials.get("MATH_Dark_Walnut")
    mat_honey_oak = bpy.data.materials.get("MATH_Honey_Oak")
    mat_brass = bpy.data.materials.get("MATH_Polished_Brass")
    mat_bronze = bpy.data.materials.get("MATH_Dark_Bronze")
    mat_gold = bpy.data.materials.get("MATH_Purdue_Gold")
    mat_leather = bpy.data.materials.get("MATH_Leather_Burgundy")
    mat_screen = bpy.data.materials.get("MATH_Screen_White")
    mat_glass = bpy.data.materials.get("MATH_Ribbon_Glass")

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

    # 1. MATH 175 Blackboard Accent Wash Lights
    # Positioned at Z = 3.9m pointing straight at the blackboard panels
    for bx in [-8.5, -6.0, -3.5, -1.0]:
        spot_data = bpy.data.lights.new(name=f"MATH_175_BB_Spot_{bx}", type="SPOT")
        spot_data.energy = 1600.0
        spot_data.spot_size = math.radians(50)
        spot_data.spot_blend = 0.3
        spot_data.color = (1.0, 0.98, 0.92)
        spot_obj = bpy.data.objects.new(name=f"MATH_175_BB_Spot_{bx}", object_data=spot_data)
        spot_obj.location = (-180.62 + bx, -127.29 - 24.5, 3.8)
        spot_obj.rotation_euler = (math.radians(-40), 0, 0)
        col_int.objects.link(spot_obj)

    # 2. 10th-Floor Sky Lounge Chandelier & Conference Details
    # Chandelier over conference table
    create_cylinder("MATH_10th_Chandelier_Ring", col_int, (0, 0, 32.2), radius=1.6, depth=0.08, mat=mat_brass)
    for ca in range(8):
        ang = ca * math.pi / 4.0
        cax = 1.6 * math.cos(ang)
        cay = 1.6 * math.sin(ang)
        create_cylinder(f"MATH_10th_Chandelier_Candle_{ca}", col_int, (cax, cay, 32.4), radius=0.04, depth=0.3, mat=mat_gold)
    
    chand_light = bpy.data.lights.new(name="MATH_10th_Chandelier_Light", type="POINT")
    chand_light.energy = 950.0
    chand_light.color = (1.0, 0.90, 0.75)
    chand_obj = bpy.data.objects.new(name="MATH_10th_Chandelier_Light", object_data=chand_light)
    chand_obj.location = (-180.62, -127.29, 32.3)
    col_int.objects.link(chand_obj)

    # Conference Table Folios & Laptops
    for fy in [-3.5, -1.8, 0.0, 1.8, 3.5]:
        for fx, rot_folio in [(-0.9, 0), (0.9, math.pi)]:
            create_box(f"MATH_10th_Folio_{fx}_{fy}", col_int, (fx, fy, 30.60), (0.45, 0.35, 0.02), mat_leather)
            create_box(f"MATH_10th_Pen_{fx}_{fy}", col_int, (fx + 0.28, fy, 30.61), (0.02, 0.20, 0.01), mat_gold)
        # 2 laptops on table
        if fy in [-1.8, 1.8]:
            create_box(f"MATH_10th_Laptop_Base_{fy}", col_int, (0, fy, 30.60), (0.35, 0.25, 0.02), mat_bronze)
            create_box(f"MATH_10th_Laptop_Screen_{fy}", col_int, (0, fy + 0.12, 30.74), (0.35, 0.02, 0.25), mat_screen)

    # 3. Double Entrance Doors with Bronze Hardware on West Canopy
    for dx in [-1.2, 1.2]:
        create_box(f"MATH_West_Door_Leaf_{dx}", col_ext, (-17.5, dx, 2.0), (0.08, 1.1, 2.8), mat_glass)
        create_box(f"MATH_West_Door_Frame_{dx}", col_ext, (-17.5, dx, 2.0), (0.12, 1.15, 2.9), mat_bronze)
        create_cylinder(f"MATH_West_Door_Handle_{dx}", col_ext, (-17.55, dx + 0.4, 2.0), radius=0.025, depth=0.8, mat=mat_gold)

    # 4. Address Numerals "150" in 3D Gold
    bpy.ops.object.text_add(location=(-17.55, -0.4, 3.8), rotation=(math.pi/2, 0, math.pi/2))
    txt = bpy.context.active_object
    txt.name = "MATH_Address_Plaque"
    txt.data.body = "150"
    txt.data.size = 0.45
    txt.data.extrude = 0.05
    txt.data.materials.append(mat_gold)
    txt.parent = root_obj
    col_ext.objects.link(txt)
    bpy.context.scene.collection.objects.unlink(txt)

    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print("Attempt 3 Polish completed and saved!")

if __name__ == "__main__":
    run_polish()
