import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def build_benjamin_harrison_hall_attempt5():
    # Clear existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 1. Setup Scene & Collection
    scene = bpy.context.scene
    scene.name = "Building_benjamin_harrison_hall"
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'

    coll = bpy.data.collections.new("Asset_benjamin_harrison_hall")
    scene.collection.children.link(coll)

    # Official Rings (29 vertices)
    official_ring = [
        (-1139.761, -266.327), (-1139.894, -256.911), (-1138.459, -256.880), (-1138.323, -250.796),
        (-1135.091, -250.869), (-1135.104, -240.869), (-1118.663, -240.715), (-1118.771, -229.260),
        (-1140.731, -229.331), (-1140.609, -217.081), (-1074.179, -216.778), (-1073.887, -229.276),
        (-1086.581, -229.159), (-1086.546, -240.461), (-1081.166, -240.425), (-1080.890, -279.059),
        (-1086.258, -279.141), (-1086.193, -290.632), (-1073.725, -290.575), (-1073.752, -302.755),
        (-1140.274, -303.152), (-1140.389, -290.868), (-1118.441, -290.843), (-1118.436, -279.352),
        (-1142.413, -279.508), (-1142.536, -267.898), (-1143.864, -267.907), (-1143.871, -266.578),
        (-1139.761, -266.327)
    ]

    # Helper: Create Realistic Procedural Shaders
    def create_material(name, shader_type="principled", **kwargs):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (400, 0)

        if shader_type == "brick":
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (150, 0)
            
            tex_coord = nodes.new('ShaderNodeTexCoord')
            tex_coord.location = (-750, 0)
            
            # Purdue Dark Red-Brown Variegated Blend
            noise_med = nodes.new('ShaderNodeTexNoise')
            noise_med.location = (-550, 100)
            noise_med.inputs['Scale'].default_value = 5.0
            noise_med.inputs['Detail'].default_value = 4.0
            
            color_ramp = nodes.new('ShaderNodeValToRGB')
            color_ramp.location = (-350, 100)
            color_ramp.color_ramp.elements[0].position = 0.20
            color_ramp.color_ramp.elements[0].color = (0.34, 0.12, 0.08, 1.0) # Burnt brick red
            color_ramp.color_ramp.elements[1].position = 0.80
            color_ramp.color_ramp.elements[1].color = (0.48, 0.19, 0.11, 1.0) # Russet terracotta
            
            noise_fine = nodes.new('ShaderNodeTexNoise')
            noise_fine.location = (-550, -150)
            noise_fine.inputs['Scale'].default_value = 20.0
            
            bump = nodes.new('ShaderNodeBump')
            bump.location = (-100, -150)
            bump.inputs['Strength'].default_value = 0.22
            
            links.new(tex_coord.outputs['Object'], noise_med.inputs['Vector'])
            links.new(noise_med.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
            
            links.new(tex_coord.outputs['Object'], noise_fine.inputs['Vector'])
            links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
            
            bsdf.inputs['Roughness'].default_value = 0.78
            links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            return mat

        elif shader_type == "limestone":
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (150, 0)
            
            tex_coord = nodes.new('ShaderNodeTexCoord')
            tex_coord.location = (-750, 0)
            
            noise = nodes.new('ShaderNodeTexNoise')
            noise.location = (-550, 50)
            noise.inputs['Scale'].default_value = 8.0
            
            color_mix = nodes.new('ShaderNodeMix')
            color_mix.location = (-300, 50)
            color_mix.data_type = 'RGBA'
            color_mix.inputs['A'].default_value = (0.76, 0.73, 0.67, 1.0) # Warm buff limestone
            color_mix.inputs['B'].default_value = (0.82, 0.79, 0.73, 1.0) # Light cream limestone
            
            bump = nodes.new('ShaderNodeBump')
            bump.location = (-100, -100)
            bump.inputs['Strength'].default_value = 0.08
            
            links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
            links.new(noise.outputs['Fac'], color_mix.inputs['Factor'])
            links.new(color_mix.outputs['Result'], bsdf.inputs['Base Color'])
            
            links.new(noise.outputs['Fac'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
            
            bsdf.inputs['Roughness'].default_value = 0.65
            links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            return mat

        elif shader_type == "glass":
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (150, 0)
            bsdf.inputs['Base Color'].default_value = (0.04, 0.08, 0.12, 1.0) # Deep solar reflective glass
            bsdf.inputs['Roughness'].default_value = 0.02
            bsdf.inputs['Metallic'].default_value = 0.10
            bsdf.inputs['IOR'].default_value = 1.52
            if 'Transmission Weight' in bsdf.inputs:
                bsdf.inputs['Transmission Weight'].default_value = 0.88
            elif 'Transmission' in bsdf.inputs:
                bsdf.inputs['Transmission'].default_value = 0.88
            links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            return mat

        else:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (150, 0)
            base_col = kwargs.get('base_color', (0.5, 0.5, 0.5, 1.0))
            bsdf.inputs['Base Color'].default_value = base_col
            bsdf.inputs['Roughness'].default_value = kwargs.get('roughness', 0.5)
            bsdf.inputs['Metallic'].default_value = kwargs.get('metallic', 0.0)
            links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            return mat

    mat_brick = create_material("Purdue_Red_Brick", shader_type="brick")
    mat_limestone = create_material("Indiana_Bedford_Limestone", shader_type="limestone")
    mat_glass = create_material("Solar_Ribbon_Glass", shader_type="glass")
    mat_spandrel = create_material("Harrison_Enamel_Spandrel", base_color=(0.14, 0.26, 0.32, 1.0), roughness=0.20)
    mat_aluminum = create_material("Anodized_Aluminum", base_color=(0.82, 0.82, 0.84, 1.0), metallic=0.88, roughness=0.25)
    mat_bronze = create_material("Aged_Architectural_Bronze", base_color=(0.34, 0.24, 0.15, 1.0), metallic=0.80, roughness=0.30)
    mat_roof = create_material("Roof_Membrane", base_color=(0.18, 0.18, 0.19, 1.0), roughness=0.85)
    mat_concrete = create_material("Concrete_Pavement", base_color=(0.66, 0.65, 0.63, 1.0), roughness=0.72)
    mat_screen = create_material("Solar_Screen_Concrete", base_color=(0.78, 0.76, 0.72, 1.0), roughness=0.68)
    mat_louver = create_material("Dark_Mechanical_Louver", base_color=(0.14, 0.14, 0.15, 1.0), metallic=0.75, roughness=0.45)
    mat_shrub = create_material("Foundation_Planting_Green", base_color=(0.10, 0.24, 0.08, 1.0), roughness=0.85)
    mat_bike_rack = create_material("Bicycle_Rack_Black_Steel", base_color=(0.06, 0.06, 0.06, 1.0), metallic=0.85, roughness=0.35)

    def create_box(name, min_pt, max_pt, mat, parent_coll=coll):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()
        
        v0 = bm.verts.new((min_pt[0], min_pt[1], min_pt[2]))
        v1 = bm.verts.new((max_pt[0], min_pt[1], min_pt[2]))
        v2 = bm.verts.new((max_pt[0], max_pt[1], min_pt[2]))
        v3 = bm.verts.new((min_pt[0], max_pt[1], min_pt[2]))
        v4 = bm.verts.new((min_pt[0], min_pt[1], max_pt[2]))
        v5 = bm.verts.new((max_pt[0], min_pt[1], max_pt[2]))
        v6 = bm.verts.new((max_pt[0], max_pt[1], max_pt[2]))
        v7 = bm.verts.new((min_pt[0], max_pt[1], max_pt[2]))
        
        bm.faces.new((v0, v1, v2, v3))
        bm.faces.new((v4, v7, v6, v5))
        bm.faces.new((v0, v4, v5, v1))
        bm.faces.new((v1, v5, v6, v2))
        bm.faces.new((v2, v6, v7, v3))
        bm.faces.new((v3, v7, v4, v0))
        
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat)
        parent_coll.objects.link(obj)
        return obj

    # 2. Site Context
    create_box("Site_Lawn_Ground", (-1185.0, -345.0, -0.06), (-1035.0, -175.0, 0.0), mat_concrete)
    create_box("Site_MacArthur_Drive", (-1185.0, -345.0, 0.0), (-1155.0, -175.0, 0.02), mat_roof)
    create_box("Site_Courtyard_Walkway", (-1155.0, -280.0, 0.0), (-1136.0, -245.0, 0.04), mat_concrete)

    # 3. Ground Floor Indiana Limestone Base (Exact 29-vertex Footprint)
    # Z = 0.0m to 3.8m
    base_mesh = bpy.data.meshes.new("HARR_Ground_Plinth_Base")
    base_obj = bpy.data.objects.new("HARR_Ground_Plinth_Base", base_mesh)
    bm_base = bmesh.new()
    
    verts_bottom = [bm_base.verts.new((p[0], p[1], 0.0)) for p in official_ring[:-1]]
    verts_top = [bm_base.verts.new((p[0], p[1], 3.8)) for p in official_ring[:-1]]
    
    n_v = len(verts_bottom)
    for i in range(n_v):
        ni = (i + 1) % n_v
        bm_base.faces.new((verts_bottom[i], verts_bottom[ni], verts_top[ni], verts_top[i]))
    
    bm_base.faces.new(verts_bottom)
    bm_base.faces.new(reversed(verts_top))
    
    bm_base.to_mesh(base_mesh)
    bm_base.free()
    base_mesh.materials.append(mat_limestone)
    coll.objects.link(base_obj)

    # Limestone Belt Course / Water Table Trim at Z = 3.65 to 3.82m
    belt_mesh = bpy.data.meshes.new("HARR_Limestone_Belt_Course")
    belt_obj = bpy.data.objects.new("HARR_Limestone_Belt_Course", belt_mesh)
    bm_belt = bmesh.new()
    
    belt_ring = []
    for i in range(n_v):
        p_prev = Vector(official_ring[(i - 1) % n_v])
        p_curr = Vector(official_ring[i])
        p_next = Vector(official_ring[(i + 1) % n_v])
        d1 = (p_curr - p_prev).normalized()
        d2 = (p_next - p_curr).normalized()
        norm1 = Vector((-d1.y, d1.x))
        norm2 = Vector((-d2.y, d2.x))
        avg_norm = (norm1 + norm2).normalized()
        offset_p = p_curr + avg_norm * 0.10
        belt_ring.append((offset_p.x, offset_p.y))

    v_b_bot = [bm_belt.verts.new((p[0], p[1], 3.65)) for p in belt_ring]
    v_b_top = [bm_belt.verts.new((p[0], p[1], 3.82)) for p in belt_ring]
    for i in range(n_v):
        ni = (i + 1) % n_v
        bm_belt.faces.new((v_b_bot[i], v_b_bot[ni], v_b_top[ni], v_b_top[i]))
    bm_belt.to_mesh(belt_mesh)
    bm_belt.free()
    belt_mesh.materials.append(mat_limestone)
    coll.objects.link(belt_obj)

    # Ground Floor Recessed Foundation Windows / Louvers
    for w_idx in range(12):
        gx = -1136.0 + w_idx * 5.2
        create_box(f"HARR_Ground_Win_N_{w_idx}", (gx - 1.2, -216.74, 1.2), (gx + 1.2, -216.66, 2.4), mat_glass)
        create_box(f"HARR_Ground_Frame_N_{w_idx}", (gx - 1.25, -216.76, 1.15), (gx + 1.25, -216.64, 2.45), mat_aluminum)
    for w_idx in range(12):
        gx = -1136.0 + w_idx * 5.2
        create_box(f"HARR_Ground_Win_S_{w_idx}", (gx - 1.2, -303.26, 1.2), (gx + 1.2, -303.18, 2.4), mat_glass)
        create_box(f"HARR_Ground_Frame_S_{w_idx}", (gx - 1.25, -303.28, 1.15), (gx + 1.25, -303.16, 2.45), mat_aluminum)

    # 4. North Residential Tower (Floors 2-9, Z = 3.8m to 26.6m)
    nw_x_min, nw_x_max = -1140.61, -1074.18
    nw_y_min, nw_y_max = -229.33, -216.78
    z_floor2 = 3.80
    z_roof = 26.60
    z_parapet = 27.60

    create_box("HARR_North_Tower_Brick_Core", (nw_x_min, nw_y_min, z_floor2), (nw_x_max, nw_y_max, z_roof), mat_brick)
    create_box("HARR_North_Tower_Parapet_N", (nw_x_min, nw_y_max - 0.35, z_roof), (nw_x_max, nw_y_max, z_parapet), mat_brick)
    create_box("HARR_North_Tower_Parapet_S", (nw_x_min, nw_y_min, z_roof), (nw_x_max, nw_y_min + 0.35, z_parapet), mat_brick)
    create_box("HARR_North_Tower_Parapet_W", (nw_x_min, nw_y_min, z_roof), (nw_x_min + 0.35, nw_y_max, z_parapet), mat_brick)
    create_box("HARR_North_Tower_Parapet_E", (nw_x_max - 0.35, nw_y_min, z_roof), (nw_x_max, nw_y_max, z_parapet), mat_brick)
    create_box("HARR_North_Tower_Roof_Deck", (nw_x_min + 0.35, nw_y_min + 0.35, z_roof - 0.05), (nw_x_max - 0.35, nw_y_max - 0.35, z_roof), mat_roof)
    create_box("HARR_North_Tower_Coping_N", (nw_x_min - 0.05, nw_y_max - 0.40, z_parapet), (nw_x_max + 0.05, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone)
    create_box("HARR_North_Tower_Coping_S", (nw_x_min - 0.05, nw_y_min - 0.05, z_parapet), (nw_x_max + 0.05, nw_y_min + 0.40, z_parapet + 0.12), mat_limestone)
    create_box("HARR_North_Tower_Coping_W", (nw_x_min - 0.05, nw_y_min - 0.05, z_parapet), (nw_x_min + 0.40, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone)
    create_box("HARR_North_Tower_Coping_E", (nw_x_max - 0.40, nw_y_min - 0.05, z_parapet), (nw_x_max + 0.05, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone)

    # Detailed North Penthouse
    ph_n_xmin, ph_n_xmax = -1114.5, -1100.5
    ph_n_ymin, ph_n_ymax = -226.5, -219.5
    create_box("HARR_North_Penthouse_Brick", (ph_n_xmin, ph_n_ymin, z_roof), (ph_n_xmax, ph_n_ymax, 30.2), mat_brick)
    create_box("HARR_North_Penthouse_Coping", (ph_n_xmin - 0.1, ph_n_ymin - 0.1, 30.2), (ph_n_xmax + 0.1, ph_n_ymax + 0.1, 30.35), mat_limestone)
    create_box("HARR_North_Penthouse_Roof_Slab", (ph_n_xmin, ph_n_ymin, 30.15), (ph_n_xmax, ph_n_ymax, 30.20), mat_roof)
    create_box("HARR_North_PH_Louver_N", (ph_n_xmin + 1.5, ph_n_ymax - 0.02, 27.2), (ph_n_xmax - 1.5, ph_n_ymax + 0.08, 29.8), mat_louver)
    create_box("HARR_North_PH_Louver_S", (ph_n_xmin + 1.5, ph_n_ymin - 0.08, 27.2), (ph_n_xmax - 1.5, ph_n_ymin + 0.02, 29.8), mat_louver)
    create_box("HARR_North_PH_Louver_W", (ph_n_xmin - 0.08, ph_n_ymin + 1.2, 27.2), (ph_n_xmin + 0.02, ph_n_ymax - 1.2, 29.8), mat_louver)
    create_box("HARR_North_PH_Louver_E", (ph_n_xmax - 0.02, ph_n_ymin + 1.2, 27.2), (ph_n_xmax + 0.08, ph_n_ymax - 1.2, 29.8), mat_louver)
    create_box("HARR_North_PH_Door", (ph_n_xmin + 0.5, ph_n_ymin - 0.06, z_roof), (ph_n_xmin + 1.5, ph_n_ymin + 0.02, z_roof + 2.2), mat_aluminum)
    for hvac_x in [-1126.0, -1120.0, -1094.0, -1088.0]:
        create_box(f"HARR_North_HVAC_Body_{hvac_x}", (hvac_x - 1.5, -225.0, z_roof), (hvac_x + 1.5, -221.5, z_roof + 1.6), mat_aluminum)
        create_box(f"HARR_North_HVAC_Fan_{hvac_x}", (hvac_x - 0.8, -224.0, z_roof + 1.6), (hvac_x + 0.8, -222.5, z_roof + 1.9), mat_louver)

    # 5. South Residential Tower (Floors 2-9, Z = 3.8m to 26.6m)
    sw_x_min, sw_x_max = -1140.39, -1073.72
    sw_y_min, sw_y_max = -303.15, -290.58

    create_box("HARR_South_Tower_Brick_Core", (sw_x_min, sw_y_min, z_floor2), (sw_x_max, sw_y_max, z_roof), mat_brick)
    create_box("HARR_South_Tower_Parapet_N", (sw_x_min, sw_y_max - 0.35, z_roof), (sw_x_max, sw_y_max, z_parapet), mat_brick)
    create_box("HARR_South_Tower_Parapet_S", (sw_x_min, sw_y_min, z_roof), (sw_x_max, sw_y_min + 0.35, z_parapet), mat_brick)
    create_box("HARR_South_Tower_Parapet_W", (sw_x_min, sw_y_min, z_roof), (sw_x_min + 0.35, sw_y_max, z_parapet), mat_brick)
    create_box("HARR_South_Tower_Parapet_E", (sw_x_max - 0.35, sw_y_min, z_roof), (sw_x_max, sw_y_max, z_parapet), mat_brick)
    create_box("HARR_South_Tower_Roof_Deck", (sw_x_min + 0.35, sw_y_min + 0.35, z_roof - 0.05), (sw_x_max - 0.35, sw_y_max - 0.35, z_roof), mat_roof)
    create_box("HARR_South_Tower_Coping_N", (sw_x_min - 0.05, sw_y_max - 0.40, z_parapet), (sw_x_max + 0.05, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone)
    create_box("HARR_South_Tower_Coping_S", (sw_x_min - 0.05, sw_y_min - 0.05, z_parapet), (sw_x_max + 0.05, sw_y_min + 0.40, z_parapet + 0.12), mat_limestone)
    create_box("HARR_South_Tower_Coping_W", (sw_x_min - 0.05, sw_y_min - 0.05, z_parapet), (sw_x_min + 0.40, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone)
    create_box("HARR_South_Tower_Coping_E", (sw_x_max - 0.40, sw_y_min - 0.05, z_parapet), (sw_x_max + 0.05, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone)

    # Detailed South Penthouse
    ph_s_xmin, ph_s_xmax = -1114.5, -1100.5
    ph_s_ymin, ph_s_ymax = -300.2, -293.2
    create_box("HARR_South_Penthouse_Brick", (ph_s_xmin, ph_s_ymin, z_roof), (ph_s_xmax, ph_s_ymax, 30.2), mat_brick)
    create_box("HARR_South_Penthouse_Coping", (ph_s_xmin - 0.1, ph_s_ymin - 0.1, 30.2), (ph_s_xmax + 0.1, ph_s_ymax + 0.1, 30.35), mat_limestone)
    create_box("HARR_South_Penthouse_Roof_Slab", (ph_s_xmin, ph_s_ymin, 30.15), (ph_s_xmax, ph_s_ymax, 30.20), mat_roof)
    create_box("HARR_South_PH_Louver_N", (ph_s_xmin + 1.5, ph_s_ymax - 0.02, 27.2), (ph_s_xmax - 1.5, ph_s_ymax + 0.08, 29.8), mat_louver)
    create_box("HARR_South_PH_Louver_S", (ph_s_xmin + 1.5, ph_s_ymin - 0.08, 27.2), (ph_s_xmax - 1.5, ph_s_ymin + 0.02, 29.8), mat_louver)
    create_box("HARR_South_PH_Louver_W", (ph_s_xmin - 0.08, ph_s_ymin + 1.2, 27.2), (ph_s_xmin + 0.02, ph_s_ymax - 1.2, 29.8), mat_louver)
    create_box("HARR_South_PH_Louver_E", (ph_s_xmax - 0.02, ph_s_ymin + 1.2, 27.2), (ph_s_xmax + 0.08, ph_s_ymax - 1.2, 29.8), mat_louver)
    create_box("HARR_South_PH_Door", (ph_s_xmin + 0.5, ph_s_ymax - 0.02, z_roof), (ph_s_xmin + 1.5, ph_s_ymax + 0.06, z_roof + 2.2), mat_aluminum)
    for hvac_x in [-1126.0, -1120.0, -1094.0, -1088.0]:
        create_box(f"HARR_South_HVAC_Body_{hvac_x}", (hvac_x - 1.5, -298.5, z_roof), (hvac_x + 1.5, -295.0, z_roof + 1.6), mat_aluminum)
        create_box(f"HARR_South_HVAC_Fan_{hvac_x}", (hvac_x - 0.8, -297.5, z_roof + 1.6), (hvac_x + 0.8, -296.0, z_roof + 1.9), mat_louver)

    # 6. Central Connecting Pavilion (2 stories, Z = 3.8m to 7.4m)
    create_box("HARR_Center_Pavilion_Main_Brick", (-1118.66, -290.7, 3.8), (-1086.55, -229.3, 7.4), mat_brick)
    create_box("HARR_Center_Pavilion_East_Block", (-1086.58, -279.14, 3.8), (-1080.89, -240.42, 7.4), mat_brick)
    create_box("HARR_Center_East_Notch_N", (-1086.58, -240.42, 3.8), (-1086.20, -229.28, 7.4), mat_brick)
    create_box("HARR_Center_East_Notch_S", (-1086.58, -290.63, 3.8), (-1086.20, -279.14, 7.4), mat_brick)

    # East Facade Fenestration (Lounge / Study windows)
    for ey_idx in range(6):
        ey = -275.0 + ey_idx * 5.8
        create_box(f"HARR_Center_East_Win_{ey_idx}", (-1080.85, ey - 1.2, 4.4), (-1080.75, ey + 1.2, 6.8), mat_glass)
        create_box(f"HARR_Center_East_Frame_{ey_idx}", (-1080.88, ey - 1.25, 4.35), (-1080.73, ey + 1.25, 6.85), mat_aluminum)

    # West Courtyard Pavilion Body:
    # Notice: At the courtyard front (Y = -264.0 to -246.0), the brick core is inset to X = -1134.5m
    # so that the large 2-story glass curtain wall and the decorative solar screen are fully open and visible!
    create_box("HARR_Center_West_Pavilion_S", (-1142.41, -279.51, 3.8), (-1118.66, -266.33, 7.4), mat_brick)
    create_box("HARR_Center_West_Entrance_Bay", (-1143.87, -267.90, 3.8), (-1118.66, -264.00, 7.4), mat_brick)
    # Courtyard lounge body (inset to allow screen)
    create_box("HARR_Center_West_Courtyard_Core", (-1134.50, -264.00, 3.8), (-1118.66, -240.87, 7.4), mat_brick)
    create_box("HARR_Center_West_North_Transition", (-1118.77, -240.87, 3.8), (-1118.44, -229.26, 7.4), mat_brick)

    # Parapet and Coping around all Central Pavilion Roofs (Z = 7.4m to 7.9m)
    create_box("HARR_Center_Roof_Deck", (-1142.0, -279.0, 7.35), (-1081.0, -240.5, 7.40), mat_roof)
    create_box("HARR_Center_Parapet_East_Wall", (-1081.25, -279.20, 7.40), (-1080.85, -240.40, 7.90), mat_brick)
    create_box("HARR_Center_Coping_East_Wall", (-1081.30, -279.25, 7.90), (-1080.75, -240.35, 8.02), mat_limestone)
    create_box("HARR_Center_Parapet_West_S", (-1142.50, -279.60, 7.40), (-1142.10, -264.00, 7.90), mat_brick)
    create_box("HARR_Center_Coping_West_S", (-1142.55, -279.65, 7.90), (-1142.00, -263.95, 8.02), mat_limestone)
    create_box("HARR_Center_Parapet_West_N", (-1135.00, -264.00, 7.40), (-1134.60, -240.80, 7.90), mat_brick)
    create_box("HARR_Center_Coping_West_N", (-1135.05, -264.05, 7.90), (-1134.50, -240.75, 8.02), mat_limestone)

    # 7. Iconic Central Pavilion Brise-Soleil / Decorative Concrete Solar Screen
    # Spans from Y = -264.0 to -246.0 at X = -1137.5m, Z = 1.0m to 7.2m
    # Behind the screen: large 2-story glass curtain wall!
    create_box("HARR_Center_Courtyard_Glazing", (-1134.60, -264.0, 1.0), (-1134.52, -246.0, 7.2), mat_glass)
    # Mullions for curtain wall behind screen
    for cmy_idx, cmy in enumerate(range(-264, -245, 3)):
        create_box(f"HARR_Courtyard_Mullion_{cmy_idx}", (-1134.65, cmy - 0.06, 1.0), (-1134.45, cmy + 0.06, 7.2), mat_aluminum)

    # Architectural Precast Concrete Brise-Soleil Grid:
    screen_mesh = bpy.data.meshes.new("HARR_West_Solar_Screen_Grid")
    screen_obj = bpy.data.objects.new("HARR_West_Solar_Screen_Grid", screen_mesh)
    bm_scr = bmesh.new()

    cell_w = 0.72
    cell_h = 0.54
    th = 0.16
    x_scr = -1137.8
    y_start = -263.8
    y_end = -246.0
    ny_cells = int((y_end - y_start) / cell_w)
    nz_cells = 11 # up to 7.0m

    for iy in range(ny_cells):
        for iz in range(nz_cells):
            cy0 = y_start + iy * cell_w
            cy1 = cy0 + cell_w
            cz0 = 1.10 + iz * cell_h
            cz1 = cz0 + cell_h
            # Outer cell frame
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, (cy0+cy1)/2, cz0)) @ Matrix.Diagonal((th, cell_w, 0.07, 1.0)))
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, cy0, (cz0+cz1)/2)) @ Matrix.Diagonal((th, 0.07, cell_h, 1.0)))
            # Geometric screen cross pattern
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, (cy0+cy1)/2, (cz0+cz1)/2)) @ Matrix.Diagonal((th*0.7, 0.05, cell_h*0.5, 1.0)))

    bm_scr.to_mesh(screen_mesh)
    bm_scr.free()
    screen_mesh.materials.append(mat_screen)
    coll.objects.link(screen_obj)

    # Precast Limestone Boundary Piers framing the solar screen
    create_box("HARR_Screen_End_Pier_S", (x_scr - 0.25, -264.15, 0.0), (x_scr + 0.25, -263.75, 7.4), mat_limestone)
    create_box("HARR_Screen_End_Pier_N", (x_scr - 0.25, -246.35, 0.0), (x_scr + 0.25, -245.95, 7.4), mat_limestone)
    create_box("HARR_Screen_Top_Beam", (x_scr - 0.25, -264.15, 7.05), (x_scr + 0.25, -245.95, 7.4), mat_limestone)

    # 8. West Main Entrance Complete Overhaul
    ent_x = -1143.87
    ent_y_min, ent_y_max = -269.8, -264.2
    
    # Entrance Steps & Terrace
    create_box("HARR_Entrance_Terrace_Plinth", (-1148.5, -271.5, 0.0), (-1143.5, -262.5, 0.60), mat_concrete)
    for step_i in range(5):
        s_z = step_i * 0.12
        s_x_edge = -1151.5 + step_i * 0.60
        create_box(f"HARR_Entrance_Step_{step_i}", (s_x_edge, -271.0, 0.0), (-1148.5, -263.0, s_z + 0.12), mat_concrete)

    # Tubular Aluminum Railings
    rail_mesh = bpy.data.meshes.new("HARR_Entrance_Tubular_Railings")
    rail_obj = bpy.data.objects.new("HARR_Entrance_Tubular_Railings", rail_mesh)
    bm_rail = bmesh.new()

    for ry in [-263.2, -267.0, -270.8]:
        for px in [-1151.0, -1149.2, -1147.5, -1145.5, -1143.8]:
            pz_base = 0.60 if px > -1148.5 else (0.12 + (-px - 1148.5) * 0.20)
            bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((px, ry, pz_base + 0.45)) @ Matrix.Diagonal((0.05, 0.05, 0.90, 1.0)))
        bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((-1147.5, ry, 1.45)) @ Matrix.Diagonal((7.5, 0.05, 0.05, 1.0)))
        bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((-1147.5, ry, 1.00)) @ Matrix.Diagonal((7.5, 0.04, 0.04, 1.0)))

    bm_rail.to_mesh(rail_mesh)
    bm_rail.free()
    rail_mesh.materials.append(mat_aluminum)
    coll.objects.link(rail_obj)

    # Wide Storefront Vestibule (Glass Curtain Wall & Double Commercial Doors)
    create_box("HARR_Storefront_Glazing", (ent_x - 0.02, ent_y_min, 0.60), (ent_x + 0.05, ent_y_max, 3.60), mat_glass)
    for my_idx, my in enumerate([-269.8, -268.4, -267.0, -265.6, -264.2]):
        create_box(f"HARR_Storefront_Mullion_{my_idx}", (ent_x - 0.06, my - 0.05, 0.60), (ent_x + 0.08, my + 0.05, 3.60), mat_aluminum)
    create_box("HARR_Storefront_Transom", (ent_x - 0.06, ent_y_min, 2.40), (ent_x + 0.08, ent_y_max, 2.50), mat_aluminum)
    create_box("HARR_Storefront_Header", (ent_x - 0.06, ent_y_min, 3.55), (ent_x + 0.08, ent_y_max, 3.65), mat_aluminum)
    # Double Doors
    create_box("HARR_Door_Leaf_L", (ent_x - 0.08, -268.35, 0.60), (ent_x + 0.06, -267.05, 2.40), mat_aluminum)
    create_box("HARR_Door_Leaf_R", (ent_x - 0.08, -266.95, 0.60), (ent_x + 0.06, -265.65, 2.40), mat_aluminum)
    create_box("HARR_Door_Glass_L", (ent_x - 0.07, -268.20, 0.75), (ent_x + 0.05, -267.20, 2.25), mat_glass)
    create_box("HARR_Door_Glass_R", (ent_x - 0.07, -266.80, 0.75), (ent_x + 0.05, -265.80, 2.25), mat_glass)
    create_box("HARR_Door_Pull_L", (ent_x - 0.12, -267.15, 1.30), (ent_x - 0.07, -267.08, 1.70), mat_bronze)
    create_box("HARR_Door_Pull_R", (ent_x - 0.12, -266.92, 1.30), (ent_x - 0.07, -266.85, 1.70), mat_bronze)

    # Cantilevered Entrance Canopy with Fascia & Downlights (Width 5.6m, neatly over doors)
    create_box("HARR_Entrance_Canopy_Slab", (ent_x - 4.2, -270.0, 3.60), (ent_x + 0.5, -264.0, 3.88), mat_limestone)
    create_box("HARR_Entrance_Canopy_Fascia", (ent_x - 4.25, -270.05, 3.80), (ent_x + 0.55, -263.95, 3.92), mat_aluminum)
    for dl_y in [-268.5, -267.0, -265.5]:
        for dl_x in [ent_x - 2.8, ent_x - 1.4]:
            create_box(f"HARR_Canopy_Soffit_Light_{dl_x}_{dl_y}", (dl_x - 0.2, dl_y - 0.2, 3.58), (dl_x + 0.2, dl_y + 0.2, 3.60), mat_aluminum)

    # Dimensional Cast Bronze Lettering "HARRISON HALL"
    # Positioned on the South Tower brick return wall beside entrance (matches archival photo)
    font_curve = bpy.data.curves.new(name="Harrison_Sign_Font", type='FONT')
    font_curve.body = "HARRISON HALL"
    font_curve.size = 0.52
    font_curve.extrude = 0.06
    font_curve.bevel_depth = 0.015
    sign_obj = bpy.data.objects.new("HARR_Sign_Harrison_Hall", font_curve)
    sign_obj.location = Vector((-1142.50, -272.2, 4.35))
    sign_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(-90.0))
    sign_obj.data.materials.append(mat_bronze)
    coll.objects.link(sign_obj)

    # Horizontal Ashlar Panel Joints on Limestone Wall
    for aj_z in [1.25, 2.50]:
        create_box(f"HARR_Ashlar_Joint_{aj_z}", (-1144.0, -279.5, aj_z), (-1134.0, -263.0, aj_z + 0.02), mat_concrete)

    # Architectural Bronze Wall Sconces
    for sc_y in [-272.5, -263.2, -259.0]:
        create_box(f"HARR_Wall_Sconce_{sc_y}", (-1142.60, sc_y - 0.15, 3.20), (-1142.42, sc_y + 0.15, 3.75), mat_bronze)

    # Planters & Bicycle Racks
    create_box("HARR_Entrance_Planter_Curb", (-1143.5, -279.0, 0.0), (-1141.5, -273.8, 0.40), mat_limestone)
    create_box("HARR_Entrance_Shrubs", (-1143.3, -278.8, 0.40), (-1141.7, -274.0, 1.30), mat_shrub)
    for b_idx, by in enumerate([-278.0, -277.0, -276.0, -275.0]):
        create_box(f"HARR_Bike_Rack_Loop_{b_idx}", (-1145.2, by - 0.03, 0.0), (-1144.2, by + 0.03, 0.90), mat_bike_rack)
        create_box(f"HARR_Bicycle_Frame_{b_idx}", (-1145.5, by - 0.10, 0.20), (-1143.9, by + 0.10, 0.85), mat_aluminum)

    # 9. 3D Architectural Window Bay Assemblies with Frames, Awning Transoms & Teal Spandrels
    def generate_detailed_window_bays(facade_id, start_x, end_x, wall_y, normal_y, bay_count, is_x_facade=True):
        dx = (end_x - start_x) / bay_count
        win_w = min(1.55, abs(dx) * 0.58)
        
        mesh_win = bpy.data.meshes.new(f"HARR_{facade_id}_Glass")
        obj_win = bpy.data.objects.new(f"HARR_{facade_id}_Glass", mesh_win)
        bm_win = bmesh.new()

        mesh_spand = bpy.data.meshes.new(f"HARR_{facade_id}_Spandrels")
        obj_spand = bpy.data.objects.new(f"HARR_{facade_id}_Spandrels", mesh_spand)
        bm_spand = bmesh.new()

        mesh_frame = bpy.data.meshes.new(f"HARR_{facade_id}_Frames")
        obj_frame = bpy.data.objects.new(f"HARR_{facade_id}_Frames", mesh_frame)
        bm_frame = bmesh.new()

        for bay_i in range(bay_count):
            if is_x_facade:
                bc_x = start_x + (bay_i + 0.5) * dx
                bc_y = wall_y
            else:
                bc_x = wall_y
                bc_y = start_x + (bay_i + 0.5) * dx

            for fl in range(8):
                fl_z0 = z_floor2 + fl * 2.85
                spand_z0 = fl_z0
                spand_z1 = fl_z0 + 0.95
                win_z0 = fl_z0 + 0.95
                win_z1 = fl_z0 + 2.75
                
                # 1. Teal Enamel Spandrel Panel
                if is_x_facade:
                    bmesh.ops.create_cube(bm_spand, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.02, (spand_z0+spand_z1)/2)) @ Matrix.Diagonal((win_w, 0.04, 0.95, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.03, spand_z0)) @ Matrix.Diagonal((win_w + 0.04, 0.06, 0.05, 1.0)))
                else:
                    bmesh.ops.create_cube(bm_spand, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.02, bc_y, (spand_z0+spand_z1)/2)) @ Matrix.Diagonal((0.04, win_w, 0.95, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.03, bc_y, spand_z0)) @ Matrix.Diagonal((0.06, win_w + 0.04, 0.05, 1.0)))

                # 2. Window Glazing & Extruded Awning Transoms
                if is_x_facade:
                    bmesh.ops.create_cube(bm_win, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.02, (win_z0+win_z1)/2)) @ Matrix.Diagonal((win_w - 0.08, 0.02, 1.76, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x - win_w/2, bc_y + normal_y * 0.05, (win_z0+win_z1)/2)) @ Matrix.Diagonal((0.06, 0.10, 1.80, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + win_w/2, bc_y + normal_y * 0.05, (win_z0+win_z1)/2)) @ Matrix.Diagonal((0.06, 0.10, 1.80, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.04, win_z0 + 0.58)) @ Matrix.Diagonal((win_w, 0.06, 0.04, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.04, win_z0 + 1.18)) @ Matrix.Diagonal((win_w, 0.06, 0.04, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.06, win_z0)) @ Matrix.Diagonal((win_w + 0.08, 0.12, 0.06, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x, bc_y + normal_y * 0.06, win_z1)) @ Matrix.Diagonal((win_w + 0.08, 0.12, 0.06, 1.0)))
                else:
                    bmesh.ops.create_cube(bm_win, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.02, bc_y, (win_z0+win_z1)/2)) @ Matrix.Diagonal((0.02, win_w - 0.08, 1.76, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.05, bc_y - win_w/2, (win_z0+win_z1)/2)) @ Matrix.Diagonal((0.10, 0.06, 1.80, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.05, bc_y + win_w/2, (win_z0+win_z1)/2)) @ Matrix.Diagonal((0.10, 0.06, 1.80, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.04, bc_y, win_z0 + 0.58)) @ Matrix.Diagonal((0.06, win_w, 0.04, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.04, bc_y, win_z0 + 1.18)) @ Matrix.Diagonal((0.06, win_w, 0.04, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.06, bc_y, win_z0)) @ Matrix.Diagonal((0.12, win_w + 0.08, 0.06, 1.0)))
                    bmesh.ops.create_cube(bm_frame, size=1.0, matrix=Matrix.Translation((bc_x + normal_y * 0.06, bc_y, win_z1)) @ Matrix.Diagonal((0.12, win_w + 0.08, 0.06, 1.0)))

        bm_win.to_mesh(mesh_win)
        bm_win.free()
        mesh_win.materials.append(mat_glass)
        coll.objects.link(obj_win)

        bm_spand.to_mesh(mesh_spand)
        bm_spand.free()
        mesh_spand.materials.append(mat_spandrel)
        coll.objects.link(obj_spand)

        bm_frame.to_mesh(mesh_frame)
        bm_frame.free()
        mesh_frame.materials.append(mat_aluminum)
        coll.objects.link(obj_frame)

    # North Tower Window Bays
    generate_detailed_window_bays("NorthTower_North", nw_x_min + 2.5, nw_x_max - 2.5, nw_y_max, normal_y=1.0, bay_count=18, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_South_W", nw_x_min + 2.0, -1119.5, nw_y_min, normal_y=-1.0, bay_count=7, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_South_E", -1085.5, nw_x_max - 2.0, nw_y_min, normal_y=-1.0, bay_count=4, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_West", nw_y_min + 1.8, nw_y_max - 1.8, nw_x_min, normal_y=-1.0, bay_count=3, is_x_facade=False)
    generate_detailed_window_bays("NorthTower_East", nw_y_min + 1.8, nw_y_max - 1.8, nw_x_max, normal_y=1.0, bay_count=3, is_x_facade=False)

    # South Tower Window Bays
    generate_detailed_window_bays("SouthTower_South", sw_x_min + 2.5, sw_x_max - 2.5, sw_y_min, normal_y=-1.0, bay_count=18, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_North_W", sw_x_min + 2.0, -1119.5, sw_y_max, normal_y=1.0, bay_count=7, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_North_E", -1085.5, sw_x_max - 2.0, sw_y_max, normal_y=1.0, bay_count=4, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_West", sw_y_min + 1.8, sw_y_max - 1.8, sw_x_min, normal_y=-1.0, bay_count=3, is_x_facade=False)
    generate_detailed_window_bays("SouthTower_East", sw_y_min + 1.8, sw_y_max - 1.8, sw_x_max, normal_y=1.0, bay_count=3, is_x_facade=False)

    # 10. Lighting Setup
    sun_data = bpy.data.lights.new(name="Sun_Purdue_Daylight", type='SUN')
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.98, 0.94)
    sun_obj = bpy.data.objects.new("Sun_Purdue_Daylight", sun_data)
    sun_obj.rotation_euler = (math.radians(46.0), math.radians(24.0), math.radians(-50.0))
    coll.objects.link(sun_obj)

    scene.world = bpy.data.worlds.new("Purdue_World")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.75, 0.85, 0.95, 1.0)
        bg_node.inputs['Strength'].default_value = 0.75

    # 11. Inspection Cameras
    # Cam 1: Top-down Orthographic (North Up, East Right)
    cam1_data = bpy.data.cameras.new("Cam_TopDown_Footprint")
    cam1_data.type = 'ORTHO'
    cam1_data.ortho_scale = 185.0
    cam1_obj = bpy.data.objects.new("Cam_TopDown_Footprint", cam1_data)
    cam1_obj.location = Vector((-1107.92, -260.19, 130.0))
    cam1_obj.rotation_euler = (0.0, 0.0, 0.0)
    coll.objects.link(cam1_obj)

    # Cam 2: Hero Perspective View
    cam2_data = bpy.data.cameras.new("Cam_Hero_Perspective")
    cam2_data.type = 'PERSP'
    cam2_data.lens = 30.0
    cam2_obj = bpy.data.objects.new("Cam_Hero_Perspective", cam2_data)
    cam2_obj.location = Vector((-1190.0, -350.0, 50.0))
    dir2 = (Vector((-1107.9, -260.2, 14.0)) - cam2_obj.location).normalized()
    cam2_obj.rotation_euler = dir2.to_track_quat('-Z', 'Y').to_euler()
    coll.objects.link(cam2_obj)

    # Cam 3: Street-Level West Entrance View (Matching Archival Photo harrison_arch_photo.jpg)
    # Camera standing back in courtyard looking towards entrance:
    # Right: South Tower with limestone base, "HARRISON HALL" bronze letters, shrubs, bike racks
    # Center: Canopy, entrance steps, handrails, commercial double doors
    # Left: 2-story decorative solar screen wall (brise-soleil) and North Tower rising behind it
    cam3_data = bpy.data.cameras.new("Cam_West_Entrance")
    cam3_data.type = 'PERSP'
    cam3_data.lens = 25.0
    cam3_obj = bpy.data.objects.new("Cam_West_Entrance", cam3_data)
    cam3_obj.location = Vector((-1162.0, -272.0, 2.0))
    dir3 = (Vector((-1140.0, -266.0, 4.2)) - cam3_obj.location).normalized()
    cam3_obj.rotation_euler = dir3.to_track_quat('-Z', 'Y').to_euler()
    coll.objects.link(cam3_obj)

    # Render settings
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        try:
            scene.render.engine = 'BLENDER_EEVEE'
        except Exception:
            pass

    # Save Blend file
    out_blend = r"c:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\benjamin_harrison_hall.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Successfully saved {out_blend}")

    # Render Attempt 5 Views
    renders = [
        (cam1_obj, "harrison_attempt5_topdown.png"),
        (cam2_obj, "harrison_attempt5_hero.png"),
        (cam3_obj, "harrison_attempt5_entrance.png")
    ]
    
    render_paths = []
    render_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'audit', 'benjamin_harrison_hall'))
    os.makedirs(render_dir, exist_ok=True)
    for cam, fname in renders:
        scene.camera = cam
        out_path = os.path.join(render_dir, fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        render_paths.append(out_path)
        print(f"Rendered {out_path}")

    return out_blend, render_paths

if __name__ == "__main__":
    build_benjamin_harrison_hall_attempt5()
