"""
Pass 2 Polish: Open-Air Breezeway Portal & High-Detail Restaurant Interiors
for Frieda Parker Hall (Purdue University Digital Twin)
Master Blend: purdue_campus_master.blend
"""

import bpy
import bmesh
import mathutils
import math

CENTER_X = -504.75
CENTER_Y = 97.34
GROUND_Z = 0.0

def get_col(name):
    return bpy.data.collections.get(name)

def get_or_create_mat(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, emission=None, emission_str=1.0, ior=1.45):
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_str
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_str
    return mat

def create_box(name, loc, size, mat=None, col=None):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
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
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
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

def polish_frieda_pass2():
    col_ext = get_col('30_Frieda_Parker_Hall_Exterior')
    col_int = get_col('31_Frieda_Parker_Hall_Interiors_and_Dining')
    col_site = get_col('32_Frieda_Parker_Hall_Courtyard_and_Site')

    # Materials
    mat_limestone = get_or_create_mat("Frieda_Bedford_Limestone", (0.76, 0.73, 0.65, 1.0), roughness=0.70)
    mat_sign_gold = get_or_create_mat("Frieda_Signage_Gold", (0.88, 0.72, 0.28, 1.0), roughness=0.3, metallic=0.85)
    mat_cfa_red = get_or_create_mat("ChickFilA_Red", (0.85, 0.02, 0.05, 1.0), roughness=0.35)
    mat_cfa_logo = get_or_create_mat("ChickFilA_Logo_Emissive", (0.95, 0.08, 0.10, 1.0), roughness=0.2, emission=(0.95, 0.08, 0.10, 1.0), emission_str=4.5)
    mat_jm_navy = get_or_create_mat("JerseyMikes_Navy", (0.01, 0.08, 0.22, 1.0), roughness=0.35)
    mat_jm_red = get_or_create_mat("JerseyMikes_Red", (0.82, 0.10, 0.12, 1.0), roughness=0.4)
    mat_jm_menu = get_or_create_mat("JerseyMikes_Menu_Glow", (0.95, 0.95, 0.85, 1.0), roughness=0.2, emission=(0.95, 0.95, 0.85, 1.0), emission_str=4.0)
    mat_warm_glow = get_or_create_mat("Dining_Warm_Ceiling_Glow", (1.0, 0.92, 0.78, 1.0), roughness=0.2, emission=(1.0, 0.92, 0.78, 1.0), emission_str=3.5)
    mat_bronze = get_or_create_mat("Frieda_Bronze_Mullion", (0.12, 0.10, 0.08, 1.0), roughness=0.4, metallic=0.85)
    mat_stainless = get_or_create_mat("Dining_Stainless_Steel", (0.85, 0.85, 0.87, 1.0), roughness=0.25, metallic=0.9)
    mat_quartz = get_or_create_mat("Dining_White_Quartz", (0.92, 0.92, 0.91, 1.0), roughness=0.25)
    mat_booth_red = get_or_create_mat("Dining_Booth_Upholstery", (0.72, 0.15, 0.12, 1.0), roughness=0.5)
    mat_wood = get_or_create_mat("Dining_Wood_Furniture", (0.58, 0.40, 0.22, 1.0), roughness=0.45)
    mat_concrete = get_or_create_mat("Frieda_Plaza_Concrete", (0.55, 0.55, 0.54, 1.0), roughness=0.8)

    # ---------------------------------------------------------
    # 1. FIX BREEZEWAY PORTAL (Remove solid block, create true open pedestrian archway)
    # ---------------------------------------------------------
    # Purge the solid blocks that were obstructing the breezeway
    for b_name in ["Frieda_Breezeway_Portal_East", "Frieda_Breezeway_Portal_West"]:
        old_obj = bpy.data.objects.get(b_name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

    # Construct East Portal Open Arch (X = -477.0m, Opening: Y in [93.0, 103.0], Z = 0 to 7.8m)
    # Left Pier (South flank: Y = 92.5)
    create_box("Frieda_Breezeway_Pier_East_S", (-477.0, 92.4, 3.9), (1.1, 1.2, 7.8), mat_limestone, col_ext)
    # Right Pier (North flank: Y = 103.5)
    create_box("Frieda_Breezeway_Pier_East_N", (-477.0, 103.6, 3.9), (1.1, 1.2, 7.8), mat_limestone, col_ext)
    # Arch Header Lintel Beam (Spans across at Z = 7.6m)
    create_box("Frieda_Breezeway_Lintel_East", (-477.0, 98.0, 7.5), (1.2, 12.4, 0.8), mat_limestone, col_ext)

    # Construct West Portal Open Arch (X = -495.0m, Opening: Y in [93.0, 103.0], Z = 0 to 7.8m)
    create_box("Frieda_Breezeway_Pier_West_S", (-495.0, 92.4, 3.9), (1.1, 1.2, 7.8), mat_limestone, col_ext)
    create_box("Frieda_Breezeway_Pier_West_N", (-495.0, 103.6, 3.9), (1.1, 1.2, 7.8), mat_limestone, col_ext)
    create_box("Frieda_Breezeway_Lintel_West", (-495.0, 98.0, 7.5), (1.2, 12.4, 0.8), mat_limestone, col_ext)

    # Breezeway interior ceiling recessed downlights
    for ly in [95.0, 98.0, 101.0]:
        create_cylinder(f"Frieda_Breezeway_Downlight_{ly}", (-486.0, ly, 7.6), 0.35, 0.1, mat_warm_glow, col_ext)

    # ---------------------------------------------------------
    # 2. CHICK-FIL-A RESTAURANT POLISH
    # ---------------------------------------------------------
    # Red accent pendant lights over Chick-fil-A dining booths
    for idx, by in enumerate([53.0, 57.5, 62.0]):
        create_cylinder(f"Frieda_CFA_Pendant_Cord_{idx}", (-483.0, by, 3.2), 0.015, 1.4, mat_bronze, col_int)
        create_cylinder(f"Frieda_CFA_Pendant_Shade_{idx}", (-483.0, by, 2.45), 0.25, 0.22, mat_cfa_red, col_int)
        create_cylinder(f"Frieda_CFA_Pendant_Bulb_{idx}", (-483.0, by, 2.35), 0.08, 0.10, mat_warm_glow, col_int)

    # Counter order trays & waffle fry holders
    for idx, ry in enumerate([54.0, 57.5, 61.0]):
        create_box(f"Frieda_CFA_OrderTray_{idx}", (-488.9, ry, 1.26), (0.4, 0.6, 0.04), mat_cfa_red, col_int)

    # ---------------------------------------------------------
    # 3. JERSEY MIKE'S SUBS POLISH
    # ---------------------------------------------------------
    # Sub counter bread rack & condiment dispensers
    create_box("Frieda_JM_BreadRack", (-489.2, 79.0, 1.6), (0.4, 2.4, 0.6), mat_wood, col_int)
    # Oil & Vinegar bottles (Red & Yellow)
    create_cylinder("Frieda_JM_VinegarBottle", (-488.7, 82.5, 1.35), 0.05, 0.25, mat_jm_red, col_int)
    create_cylinder("Frieda_JM_OilBottle", (-488.7, 82.7, 1.35), 0.05, 0.25, mat_sign_gold, col_int)

    # Navy accent pendant lights over Jersey Mike's dining tables
    for idx, by in enumerate([76.0, 80.5, 85.0]):
        create_cylinder(f"Frieda_JM_Pendant_Cord_{idx}", (-483.0, by, 3.2), 0.015, 1.4, mat_bronze, col_int)
        create_cylinder(f"Frieda_JM_Pendant_Shade_{idx}", (-483.0, by, 2.45), 0.25, 0.22, mat_jm_navy, col_int)
        create_cylinder(f"Frieda_JM_Pendant_Bulb_{idx}", (-483.0, by, 2.35), 0.08, 0.10, mat_warm_glow, col_int)

    # ---------------------------------------------------------
    # 4. RECALIBRATE INSPECTION CAMERAS
    # ---------------------------------------------------------
    # Cam_42 East Street View: Pulled back along Russell Street to frame both restaurants, outdoor patio, and open breezeway
    cam42 = bpy.data.objects.get('Cam_42_Frieda_Parker_East_StreetView')
    if cam42:
        cam42.location = (-448.0, 75.0, 6.2)
        t_loc = mathutils.Vector((-486.0, 85.0, 8.5))
        c_loc = mathutils.Vector(cam42.location)
        cam42.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam42.data.lens = 22.0

    # Cam_46 Breezeway Portal: Framed looking straight through the clear open archway to Parker Quad
    cam46 = bpy.data.objects.get('Cam_46_Frieda_Parker_Breezeway_Portal')
    if cam46:
        cam46.location = (-466.0, 98.0, 2.4)
        t_loc = mathutils.Vector((-500.0, 98.0, 3.2))
        c_loc = mathutils.Vector(cam46.location)
        cam46.rotation_euler = (t_loc - c_loc).to_track_quat('-Z', 'Y').to_euler()
        cam46.data.lens = 24.0

    print("Pass 2 Polish completed successfully!")

if __name__ == '__main__':
    polish_frieda_pass2()
