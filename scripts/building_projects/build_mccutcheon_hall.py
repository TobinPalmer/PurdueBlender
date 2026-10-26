import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def build_mccutcheon_hall():
    print("=========================================================================")
    print("=== CONSTRUCTING JOHN T. MCCUTCHEON RESIDENCE HALL (MCUT - FID 57)   ===")
    print("=========================================================================")

    # Clear existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 1. Setup Scene & Master Collection
    scene = bpy.context.scene
    scene.name = "Building_mccutcheon_hall"
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'

    coll_root = bpy.data.collections.new("Asset_mccutcheon_hall")
    scene.collection.children.link(coll_root)

    # Sub-collections for organization
    coll_structure = bpy.data.collections.new("MCUT_Structure")
    coll_fenestration = bpy.data.collections.new("MCUT_Fenestration")
    coll_roof = bpy.data.collections.new("MCUT_Roof_and_Penthouses")
    coll_entrance = bpy.data.collections.new("MCUT_Entrance_and_Details")
    coll_site = bpy.data.collections.new("MCUT_Site_and_Context")
    coll_cams = bpy.data.collections.new("00_Inspection_Cameras")

    for c in [coll_structure, coll_fenestration, coll_roof, coll_entrance, coll_site, coll_cams]:
        coll_root.children.link(c)

    # Official Rings (27 vertices)
    official_ring = [
        (-1189.776492561541, -217.4265406429936),
        (-1189.7024819003602, -229.7906482804956),
        (-1207.7898011249636, -229.80402384736635),
        (-1207.7794201374224, -241.2250169644244),
        (-1191.210577542163, -241.1170263894428),
        (-1191.1949464386678, -251.27308940226158),
        (-1187.8227251248527, -251.2698786912938),
        (-1187.8149217857126, -257.21965144297656),
        (-1186.541660694394, -257.2615213622612),
        (-1186.4818922017882, -266.57030136103003),
        (-1183.5300131479828, -266.53892988515054),
        (-1183.4438075034102, -279.8589736640156),
        (-1207.4667102435271, -279.9538262644114),
        (-1207.4227211617283, -291.32610052546397),
        (-1189.1024158858495, -291.2181458493751),
        (-1189.0692146209904, -303.5169956559389),
        (-1252.1331193469694, -303.85725168591534),
        (-1252.212191877842, -291.60708192668153),
        (-1239.8991073108803, -291.5159106243982),
        (-1239.8486301683633, -280.1072274688363),
        (-1245.1920767321963, -280.2837747510375),
        (-1245.586966702124, -241.41155564775772),
        (-1240.1126684862058, -241.31754053381428),
        (-1240.1811868800007, -230.015322973793),
        (-1252.7984642107865, -230.00250605996825),
        (-1252.7770971710875, -217.80439954729445),
        (-1189.776492561541, -217.4265406429936)
    ]

    official_center = (-1218.9750479185961, -260.9137241466736)

    # 2. Material System Setup (Procedural Photorealistic Shaders)
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
            noise_fine.inputs['Scale'].default_value = 22.0
            
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

        elif shader_type == "emission":
            bsdf = nodes.new('ShaderNodeEmission')
            bsdf.location = (150, 0)
            bsdf.inputs['Color'].default_value = kwargs.get('color', (0.1, 1.0, 0.1, 1.0))
            bsdf.inputs['Strength'].default_value = kwargs.get('strength', 2.0)
            links.new(bsdf.outputs['Emission'], out.inputs['Surface'])
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
    mat_spandrel = create_material("McCutcheon_Enamel_Spandrel", base_color=(0.14, 0.26, 0.32, 1.0), roughness=0.18, metallic=0.05)
    mat_aluminum = create_material("Anodized_Aluminum", base_color=(0.82, 0.82, 0.84, 1.0), metallic=0.88, roughness=0.25)
    mat_bronze = create_material("Aged_Architectural_Bronze", base_color=(0.34, 0.24, 0.15, 1.0), metallic=0.80, roughness=0.30)
    mat_roof = create_material("Roof_Membrane", base_color=(0.18, 0.18, 0.19, 1.0), roughness=0.85)
    mat_concrete = create_material("Concrete_Pavement", base_color=(0.66, 0.65, 0.63, 1.0), roughness=0.72)
    mat_screen = create_material("Solar_Screen_Concrete", base_color=(0.78, 0.76, 0.72, 1.0), roughness=0.68)
    mat_louver = create_material("Dark_Mechanical_Louver", base_color=(0.14, 0.14, 0.15, 1.0), metallic=0.75, roughness=0.45)
    mat_shrub = create_material("Foundation_Planting_Green", base_color=(0.10, 0.24, 0.08, 1.0), roughness=0.85)
    mat_bark = create_material("Tree_Bark_Brown", base_color=(0.20, 0.14, 0.10, 1.0), roughness=0.90)
    mat_leaves = create_material("Tree_Foliage_Green", base_color=(0.12, 0.28, 0.09, 1.0), roughness=0.80)
    mat_bike_rack = create_material("Bicycle_Rack_Black_Steel", base_color=(0.06, 0.06, 0.06, 1.0), metallic=0.85, roughness=0.35)
    mat_gis = create_material("Official_GIS_Ring_Overlay", shader_type="emission", color=(0.1, 1.0, 0.1, 1.0), strength=2.5)

    def create_box(name, min_pt, max_pt, mat, parent_coll=coll_structure):
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

    # 3. Official Footprint GIS Verification Overlay Curve
    curve_data = bpy.data.curves.new(name="MCUT_Official_Footprint_Overlay", type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(official_ring) - 1)
    for idx, pt in enumerate(official_ring):
        polyline.points[idx].co = (pt[0], pt[1], 0.08, 1.0)
    polyline.use_cyclic_u = True
    curve_data.bevel_depth = 0.08
    curve_obj = bpy.data.objects.new("MCUT_Official_Footprint_Overlay", curve_data)
    curve_obj.data.materials.append(mat_gis)
    coll_site.objects.link(curve_obj)

    # 4. Site Context & Roads (MacArthur Drive on East, McCutcheon Drive on West, Lawns)
    create_box("Site_Lawn_Base", (-1285.0, -345.0, -0.06), (-1145.0, -175.0, 0.0), mat_concrete, coll_site)
    create_box("Site_MacArthur_Drive", (-1172.0, -345.0, 0.0), (-1155.0, -175.0, 0.02), mat_roof, coll_site)
    create_box("Site_McCutcheon_Drive", (-1285.0, -345.0, 0.0), (-1268.0, -175.0, 0.02), mat_roof, coll_site)
    create_box("Site_East_Courtyard_Plaza", (-1200.0, -282.0, 0.0), (-1172.0, -240.0, 0.04), mat_concrete, coll_site)

    # 5. Ground Floor Indiana Limestone Plinth Base (Exact 27-vertex Footprint)
    # Z = 0.0m to 2.20m (Photorealistic height matching harrison_arch_photo.jpg)
    z_plinth = 2.20
    base_mesh = bpy.data.meshes.new("MCUT_Ground_Plinth_Base")
    base_obj = bpy.data.objects.new("MCUT_Ground_Plinth_Base", base_mesh)
    bm_base = bmesh.new()
    
    ring_unique = official_ring[:-1]
    n_v = len(ring_unique)
    verts_bottom = [bm_base.verts.new((p[0], p[1], 0.0)) for p in ring_unique]
    verts_top = [bm_base.verts.new((p[0], p[1], z_plinth)) for p in ring_unique]
    
    for i in range(n_v):
        ni = (i + 1) % n_v
        bm_base.faces.new((verts_bottom[i], verts_bottom[ni], verts_top[ni], verts_top[i]))
    
    bm_base.faces.new(verts_bottom)
    bm_base.faces.new(reversed(verts_top))
    
    bm_base.to_mesh(base_mesh)
    bm_base.free()
    base_mesh.materials.append(mat_limestone)
    coll_structure.objects.link(base_obj)

    # Limestone Belt Course / Water Table Trim at Z = 2.10 to 2.25m
    belt_mesh = bpy.data.meshes.new("MCUT_Limestone_Belt_Course")
    belt_obj = bpy.data.objects.new("MCUT_Limestone_Belt_Course", belt_mesh)
    bm_belt = bmesh.new()
    
    belt_ring = []
    for i in range(n_v):
        p_prev = Vector(ring_unique[(i - 1) % n_v])
        p_curr = Vector(ring_unique[i])
        p_next = Vector(ring_unique[(i + 1) % n_v])
        d1 = (p_curr - p_prev).normalized()
        d2 = (p_next - p_curr).normalized()
        norm1 = Vector((-d1.y, d1.x))
        norm2 = Vector((-d2.y, d2.x))
        avg_norm = (norm1 + norm2).normalized()
        offset_p = p_curr + avg_norm * 0.10
        belt_ring.append((offset_p.x, offset_p.y))

    v_b_bot = [bm_belt.verts.new((p[0], p[1], 2.10)) for p in belt_ring]
    v_b_top = [bm_belt.verts.new((p[0], p[1], 2.25)) for p in belt_ring]
    for i in range(n_v):
        ni = (i + 1) % n_v
        bm_belt.faces.new((v_b_bot[i], v_b_bot[ni], v_b_top[ni], v_b_top[i]))
    bm_belt.to_mesh(belt_mesh)
    bm_belt.free()
    belt_mesh.materials.append(mat_limestone)
    coll_structure.objects.link(belt_obj)

    # Ground Floor Foundation Windows with Aluminum Frames
    for w_idx in range(12):
        gx = -1248.0 + w_idx * 5.0
        create_box(f"MCUT_Ground_Win_N_{w_idx}", (gx - 1.2, -217.40, 0.7), (gx + 1.2, -217.32, 1.8), mat_glass, coll_fenestration)
        create_box(f"MCUT_Ground_Frame_N_{w_idx}", (gx - 1.25, -217.42, 0.65), (gx + 1.25, -217.30, 1.85), mat_aluminum, coll_fenestration)
    for w_idx in range(12):
        gx = -1248.0 + w_idx * 5.0
        create_box(f"MCUT_Ground_Win_S_{w_idx}", (gx - 1.2, -303.96, 0.7), (gx + 1.2, -303.88, 1.8), mat_glass, coll_fenestration)
        create_box(f"MCUT_Ground_Frame_S_{w_idx}", (gx - 1.25, -303.98, 0.65), (gx + 1.25, -303.86, 1.85), mat_aluminum, coll_fenestration)

    # 6. North Residential Tower (Floors 1-9 Brick Core, Z = 2.20m to 26.6m)
    nw_x_min, nw_x_max = -1252.78, -1189.70
    nw_y_min, nw_y_max = -229.80, -217.43
    z_floor2 = 3.80
    z_roof = 26.60
    z_parapet = 27.60

    create_box("MCUT_North_Tower_Brick_Core", (nw_x_min, nw_y_min, z_plinth), (nw_x_max, nw_y_max, z_roof), mat_brick, coll_structure)
    create_box("MCUT_North_Tower_Parapet_N", (nw_x_min, nw_y_max - 0.35, z_roof), (nw_x_max, nw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_North_Tower_Parapet_S", (nw_x_min, nw_y_min, z_roof), (nw_x_max, nw_y_min + 0.35, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_North_Tower_Parapet_W", (nw_x_min, nw_y_min, z_roof), (nw_x_min + 0.35, nw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_North_Tower_Parapet_E", (nw_x_max - 0.35, nw_y_min, z_roof), (nw_x_max, nw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_North_Tower_Roof_Deck", (nw_x_min + 0.35, nw_y_min + 0.35, z_roof - 0.05), (nw_x_max - 0.35, nw_y_max - 0.35, z_roof), mat_roof, coll_roof)
    create_box("MCUT_North_Tower_Coping_N", (nw_x_min - 0.05, nw_y_max - 0.40, z_parapet), (nw_x_max + 0.05, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_North_Tower_Coping_S", (nw_x_min - 0.05, nw_y_min - 0.05, z_parapet), (nw_x_max + 0.05, nw_y_min + 0.40, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_North_Tower_Coping_W", (nw_x_min - 0.05, nw_y_min - 0.05, z_parapet), (nw_x_min + 0.40, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_North_Tower_Coping_E", (nw_x_max - 0.40, nw_y_min - 0.05, z_parapet), (nw_x_max + 0.05, nw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)

    # North Tower Mechanical Penthouse
    ph_n_xmin, ph_n_xmax = -1228.0, -1214.0
    ph_n_ymin, ph_n_ymax = -226.5, -219.5
    create_box("MCUT_North_Penthouse_Brick", (ph_n_xmin, ph_n_ymin, z_roof), (ph_n_xmax, ph_n_ymax, 30.2), mat_brick, coll_roof)
    create_box("MCUT_North_Penthouse_Coping", (ph_n_xmin - 0.1, ph_n_ymin - 0.1, 30.2), (ph_n_xmax + 0.1, ph_n_ymax + 0.1, 30.35), mat_limestone, coll_roof)
    create_box("MCUT_North_Penthouse_Roof_Slab", (ph_n_xmin, ph_n_ymin, 30.15), (ph_n_xmax, ph_n_ymax, 30.20), mat_roof, coll_roof)
    create_box("MCUT_North_PH_Louver_N", (ph_n_xmin + 1.5, ph_n_ymax - 0.02, 27.2), (ph_n_xmax - 1.5, ph_n_ymax + 0.08, 29.8), mat_louver, coll_roof)
    create_box("MCUT_North_PH_Louver_S", (ph_n_xmin + 1.5, ph_n_ymin - 0.08, 27.2), (ph_n_xmax - 1.5, ph_n_ymin + 0.02, 29.8), mat_louver, coll_roof)
    create_box("MCUT_North_PH_Louver_W", (ph_n_xmin - 0.08, ph_n_ymin + 1.2, 27.2), (ph_n_xmin + 0.02, ph_n_ymax - 1.2, 29.8), mat_louver, coll_roof)
    create_box("MCUT_North_PH_Louver_E", (ph_n_xmax - 0.02, ph_n_ymin + 1.2, 27.2), (ph_n_xmax + 0.08, ph_n_ymax - 1.2, 29.8), mat_louver, coll_roof)
    create_box("MCUT_North_PH_Door", (ph_n_xmin + 0.5, ph_n_ymin - 0.06, z_roof), (ph_n_xmin + 1.5, ph_n_ymin + 0.02, z_roof + 2.2), mat_aluminum, coll_roof)
    for hvac_x in [-1240.0, -1234.0, -1206.0, -1200.0]:
        create_box(f"MCUT_North_HVAC_Body_{hvac_x}", (hvac_x - 1.5, -225.0, z_roof), (hvac_x + 1.5, -221.5, z_roof + 1.6), mat_aluminum, coll_roof)
        create_box(f"MCUT_North_HVAC_Fan_{hvac_x}", (hvac_x - 0.8, -224.0, z_roof + 1.6), (hvac_x + 0.8, -222.5, z_roof + 1.9), mat_louver, coll_roof)

    # 7. South Residential Tower (Floors 1-9 Brick Core, Z = 2.20m to 26.6m)
    sw_x_min, sw_x_max = -1252.13, -1189.07
    sw_y_min, sw_y_max = -303.86, -291.22

    create_box("MCUT_South_Tower_Brick_Core", (sw_x_min, sw_y_min, z_plinth), (sw_x_max, sw_y_max, z_roof), mat_brick, coll_structure)
    create_box("MCUT_South_Tower_Parapet_N", (sw_x_min, sw_y_max - 0.35, z_roof), (sw_x_max, sw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_South_Tower_Parapet_S", (sw_x_min, sw_y_min, z_roof), (sw_x_max, sw_y_min + 0.35, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_South_Tower_Parapet_W", (sw_x_min, sw_y_min, z_roof), (sw_x_min + 0.35, sw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_South_Tower_Parapet_E", (sw_x_max - 0.35, sw_y_min, z_roof), (sw_x_max, sw_y_max, z_parapet), mat_brick, coll_structure)
    create_box("MCUT_South_Tower_Roof_Deck", (sw_x_min + 0.35, sw_y_min + 0.35, z_roof - 0.05), (sw_x_max - 0.35, sw_y_max - 0.35, z_roof), mat_roof, coll_roof)
    create_box("MCUT_South_Tower_Coping_N", (sw_x_min - 0.05, sw_y_max - 0.40, z_parapet), (sw_x_max + 0.05, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_South_Tower_Coping_S", (sw_x_min - 0.05, sw_y_min - 0.05, z_parapet), (sw_x_max + 0.05, sw_y_min + 0.40, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_South_Tower_Coping_W", (sw_x_min - 0.05, sw_y_min - 0.05, z_parapet), (sw_x_min + 0.40, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)
    create_box("MCUT_South_Tower_Coping_E", (sw_x_max - 0.40, sw_y_min - 0.05, z_parapet), (sw_x_max + 0.05, sw_y_max + 0.05, z_parapet + 0.12), mat_limestone, coll_structure)

    # South Tower Mechanical Penthouse
    ph_s_xmin, ph_s_xmax = -1228.0, -1214.0
    ph_s_ymin, ph_s_ymax = -301.5, -294.5
    create_box("MCUT_South_Penthouse_Brick", (ph_s_xmin, ph_s_ymin, z_roof), (ph_s_xmax, ph_s_ymax, 30.2), mat_brick, coll_roof)
    create_box("MCUT_South_Penthouse_Coping", (ph_s_xmin - 0.1, ph_s_ymin - 0.1, 30.2), (ph_s_xmax + 0.1, ph_s_ymax + 0.1, 30.35), mat_limestone, coll_roof)
    create_box("MCUT_South_Penthouse_Roof_Slab", (ph_s_xmin, ph_s_ymin, 30.15), (ph_s_xmax, ph_s_ymax, 30.20), mat_roof, coll_roof)
    create_box("MCUT_South_PH_Louver_N", (ph_s_xmin + 1.5, ph_s_ymax - 0.02, 27.2), (ph_s_xmax - 1.5, ph_s_ymax + 0.08, 29.8), mat_louver, coll_roof)
    create_box("MCUT_South_PH_Louver_S", (ph_s_xmin + 1.5, ph_s_ymin - 0.08, 27.2), (ph_s_xmax - 1.5, ph_s_ymin + 0.02, 29.8), mat_louver, coll_roof)
    create_box("MCUT_South_PH_Louver_W", (ph_s_xmin - 0.08, ph_s_ymin + 1.2, 27.2), (ph_s_xmin + 0.02, ph_s_ymax - 1.2, 29.8), mat_louver, coll_roof)
    create_box("MCUT_South_PH_Louver_E", (ph_s_xmax - 0.02, ph_s_ymin + 1.2, 27.2), (ph_s_xmax + 0.08, ph_s_ymax - 1.2, 29.8), mat_louver, coll_roof)
    create_box("MCUT_South_PH_Door", (ph_s_xmin + 0.5, ph_s_ymax - 0.02, z_roof), (ph_s_xmin + 1.5, ph_s_ymax + 0.06, z_roof + 2.2), mat_aluminum, coll_roof)
    for hvac_x in [-1240.0, -1234.0, -1206.0, -1200.0]:
        create_box(f"MCUT_South_HVAC_Body_{hvac_x}", (hvac_x - 1.5, -299.5, z_roof), (hvac_x + 1.5, -296.0, z_roof + 1.6), mat_aluminum, coll_roof)
        create_box(f"MCUT_South_HVAC_Fan_{hvac_x}", (hvac_x - 0.8, -298.5, z_roof + 1.6), (hvac_x + 0.8, -297.0, z_roof + 1.9), mat_louver, coll_roof)

    # 8. Central Connecting Pavilion (2 stories, Z = 2.20m to 7.4m)
    # Brick massings perfectly bounded to official footprint:
    # Main Central Core
    create_box("MCUT_Center_Pavilion_Main_Brick", (-1240.0, -291.3, z_plinth), (-1207.5, -229.8, 7.4), mat_brick, coll_structure)
    # West Courtyard Block
    create_box("MCUT_Center_West_Block", (-1245.4, -280.2, z_plinth), (-1240.0, -241.4, 7.4), mat_brick, coll_structure)
    create_box("MCUT_Center_West_Notch_N", (-1240.1, -241.4, z_plinth), (-1240.0, -230.0, 7.4), mat_brick, coll_structure)
    create_box("MCUT_Center_West_Notch_S", (-1240.1, -291.5, z_plinth), (-1240.0, -280.2, 7.4), mat_brick, coll_structure)

    # East Lounge Block (projecting east to -1183.44)
    create_box("MCUT_Center_East_Lounge_Block", (-1207.5, -279.9, z_plinth), (-1183.44, -266.5, 7.4), mat_brick, coll_structure)
    # East Entrance Vestibule Core
    create_box("MCUT_Center_East_Entrance_Bay", (-1207.5, -266.5, z_plinth), (-1186.5, -257.2, 7.4), mat_brick, coll_structure)
    # East Courtyard Lounge Link (recessed behind the solar screen and curtain wall)
    create_box("MCUT_Center_East_Courtyard_Core", (-1207.5, -257.2, z_plinth), (-1195.0, -241.1, 7.4), mat_brick, coll_structure)
    create_box("MCUT_Center_East_North_Transition", (-1207.8, -241.2, z_plinth), (-1189.7, -229.8, 7.4), mat_brick, coll_structure)

    # Modular Roof Decks for Central Pavilion (Zero Overhang, Perfectly Matching Walls)
    create_box("MCUT_Center_Roof_Main", (-1240.0, -291.3, 7.35), (-1207.5, -229.8, 7.40), mat_roof, coll_roof)
    create_box("MCUT_Center_Roof_West", (-1245.4, -280.2, 7.35), (-1240.0, -241.4, 7.40), mat_roof, coll_roof)
    create_box("MCUT_Center_Roof_East_Lounge", (-1207.5, -279.9, 7.35), (-1183.44, -266.5, 7.40), mat_roof, coll_roof)
    create_box("MCUT_Center_Roof_East_Entrance", (-1207.5, -266.5, 7.35), (-1186.5, -257.2, 7.40), mat_roof, coll_roof)
    create_box("MCUT_Center_Roof_East_Courtyard", (-1207.5, -257.2, 7.35), (-1188.0, -241.1, 7.40), mat_roof, coll_roof)
    create_box("MCUT_Center_Roof_East_North_Trans", (-1207.8, -241.2, 7.35), (-1189.7, -229.8, 7.40), mat_roof, coll_roof)

    # Parapets and Copings for Central Pavilion (Z = 7.4m to 7.9m)
    create_box("MCUT_Center_Parapet_East_Lounge", (-1183.75, -279.95, 7.40), (-1183.40, -266.50, 7.90), mat_brick, coll_structure)
    create_box("MCUT_Center_Coping_East_Lounge", (-1183.80, -280.00, 7.90), (-1183.35, -266.45, 8.02), mat_limestone, coll_structure)
    create_box("MCUT_Center_Parapet_West_Wall", (-1245.60, -280.35, 7.40), (-1245.20, -241.35, 7.90), mat_brick, coll_structure)
    create_box("MCUT_Center_Coping_West_Wall", (-1245.65, -280.40, 7.90), (-1245.15, -241.30, 8.02), mat_limestone, coll_structure)

    # Windows on West Facade of Central Pavilion
    for wy_idx in range(6):
        wy = -276.0 + wy_idx * 6.0
        create_box(f"MCUT_Center_West_Win_{wy_idx}", (-1245.45, wy - 1.2, 3.8), (-1245.35, wy + 1.2, 6.8), mat_glass, coll_fenestration)
        create_box(f"MCUT_Center_West_Frame_{wy_idx}", (-1245.48, wy - 1.25, 3.75), (-1245.32, wy + 1.25, 6.85), mat_aluminum, coll_fenestration)

    # 9. Iconic East Courtyard Decorative Precast Concrete Solar Screen (Brise-Soleil)
    # Precast Concrete Solar Screen Lattice Grid at X = -1188.0, Z = 0.5m to 7.2m
    # Behind the screen: large 2-story glass curtain wall at X = -1191.0!
    create_box("MCUT_Courtyard_Curtain_Glazing", (-1191.10, -257.0, 0.5), (-1191.02, -241.5, 7.2), mat_glass, coll_fenestration)
    for cmy_idx, cmy in enumerate(range(-257, -241, 3)):
        create_box(f"MCUT_Courtyard_Mullion_{cmy_idx}", (-1191.15, cmy - 0.06, 0.5), (-1190.95, cmy + 0.06, 7.2), mat_aluminum, coll_fenestration)

    # Precast Concrete Solar Screen Lattice Grid:
    screen_mesh = bpy.data.meshes.new("MCUT_East_Solar_Screen_Grid")
    screen_obj = bpy.data.objects.new("MCUT_East_Solar_Screen_Grid", screen_mesh)
    bm_scr = bmesh.new()

    cell_w = 0.72
    cell_h = 0.54
    th = 0.16
    x_scr = -1188.0
    y_start = -256.8
    y_end = -241.5
    ny_cells = int((y_end - y_start) / cell_w)
    nz_cells = 12

    for iy in range(ny_cells):
        for iz in range(nz_cells):
            cy0 = y_start + iy * cell_w
            cy1 = cy0 + cell_w
            cz0 = 0.60 + iz * cell_h
            cz1 = cz0 + cell_h
            # Outer cell frame
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, (cy0+cy1)/2, cz0)) @ Matrix.Diagonal((th, cell_w, 0.07, 1.0)))
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, cy0, (cz0+cz1)/2)) @ Matrix.Diagonal((th, 0.07, cell_h, 1.0)))
            # Geometric screen cross pattern
            bmesh.ops.create_cube(bm_scr, size=1.0, matrix=Matrix.Translation((x_scr, (cy0+cy1)/2, (cz0+cz1)/2)) @ Matrix.Diagonal((th*0.7, 0.05, cell_h*0.5, 1.0)))

    bm_scr.to_mesh(screen_mesh)
    bm_scr.free()
    screen_mesh.materials.append(mat_screen)
    coll_entrance.objects.link(screen_obj)

    # Precast Limestone Boundary Piers framing the solar screen
    create_box("MCUT_Screen_End_Pier_S", (x_scr - 0.25, -257.15, 0.0), (x_scr + 0.25, -256.75, 7.4), mat_limestone, coll_entrance)
    create_box("MCUT_Screen_End_Pier_N", (x_scr - 0.25, -241.85, 0.0), (x_scr + 0.25, -241.45, 7.4), mat_limestone, coll_entrance)
    create_box("MCUT_Screen_Top_Beam", (x_scr - 0.25, -257.15, 7.05), (x_scr + 0.25, -241.45, 7.4), mat_limestone, coll_entrance)

    # 10. East Main Entrance Complete Architecture
    # Facing MacArthur Drive at X = -1186.5m, Y = -266.5 to -257.2
    ent_x = -1186.5
    ent_y_min, ent_y_max = -266.0, -258.0
    
    # Entrance Steps & Terrace Plinth
    create_box("MCUT_Entrance_Terrace_Plinth", (ent_x - 0.5, -267.5, 0.0), (ent_x + 4.5, -257.0, 0.60), mat_concrete, coll_entrance)
    for step_i in range(5):
        s_z = step_i * 0.12
        s_x_edge = ent_x + 4.5 + step_i * 0.60
        create_box(f"MCUT_Entrance_Step_{step_i}", (s_x_edge, -267.0, 0.0), (s_x_edge + 0.60, -257.5, 0.60 - s_z), mat_concrete, coll_entrance)

    # Tubular Aluminum Railings
    rail_mesh = bpy.data.meshes.new("MCUT_Entrance_Tubular_Railings")
    rail_obj = bpy.data.objects.new("MCUT_Entrance_Tubular_Railings", rail_mesh)
    bm_rail = bmesh.new()

    for ry in [-267.2, -262.5, -257.3]:
        for px in [ent_x + 0.5, ent_x + 2.5, ent_x + 4.5, ent_x + 6.0, ent_x + 7.5]:
            pz_base = 0.60 if px <= ent_x + 4.5 else (0.60 - (px - (ent_x + 4.5)) * 0.20)
            bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((px, ry, pz_base + 0.45)) @ Matrix.Diagonal((0.05, 0.05, 0.90, 1.0)))
        bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((ent_x + 4.0, ry, 1.45)) @ Matrix.Diagonal((7.5, 0.05, 0.05, 1.0)))
        bmesh.ops.create_cube(bm_rail, size=1.0, matrix=Matrix.Translation((ent_x + 4.0, ry, 1.00)) @ Matrix.Diagonal((7.5, 0.04, 0.04, 1.0)))

    bm_rail.to_mesh(rail_mesh)
    bm_rail.free()
    rail_mesh.materials.append(mat_aluminum)
    coll_entrance.objects.link(rail_obj)

    # Wide Storefront Vestibule (Glass Curtain Wall & Double Commercial Doors)
    create_box("MCUT_Storefront_Glazing", (ent_x - 0.05, ent_y_min, 0.60), (ent_x + 0.05, ent_y_max, 3.60), mat_glass, coll_entrance)
    for my_idx, my in enumerate([-266.0, -264.0, -262.0, -260.0, -258.0]):
        create_box(f"MCUT_Storefront_Mullion_{my_idx}", (ent_x - 0.08, my - 0.05, 0.60), (ent_x + 0.08, my + 0.05, 3.60), mat_aluminum, coll_entrance)
    create_box("MCUT_Storefront_Transom", (ent_x - 0.08, ent_y_min, 2.40), (ent_x + 0.08, ent_y_max, 2.50), mat_aluminum, coll_entrance)
    create_box("MCUT_Storefront_Header", (ent_x - 0.08, ent_y_min, 3.55), (ent_x + 0.08, ent_y_max, 3.65), mat_aluminum, coll_entrance)
    
    # Double Doors
    create_box("MCUT_Door_Leaf_L", (ent_x - 0.06, -263.95, 0.60), (ent_x + 0.06, -262.05, 2.40), mat_aluminum, coll_entrance)
    create_box("MCUT_Door_Leaf_R", (ent_x - 0.06, -261.95, 0.60), (ent_x + 0.06, -260.05, 2.40), mat_aluminum, coll_entrance)
    create_box("MCUT_Door_Glass_L", (ent_x - 0.05, -263.80, 0.75), (ent_x + 0.05, -262.20, 2.25), mat_glass, coll_entrance)
    create_box("MCUT_Door_Glass_R", (ent_x - 0.05, -261.80, 0.75), (ent_x + 0.05, -260.20, 2.25), mat_glass, coll_entrance)
    create_box("MCUT_Door_Pull_L", (ent_x + 0.08, -262.25, 1.30), (ent_x + 0.13, -262.18, 1.70), mat_bronze, coll_entrance)
    create_box("MCUT_Door_Pull_R", (ent_x + 0.08, -261.82, 1.30), (ent_x + 0.13, -261.75, 1.70), mat_bronze, coll_entrance)

    # Cantilevered Entrance Canopy with Fascia & Downlights (Projects East)
    create_box("MCUT_Entrance_Canopy_Slab", (ent_x - 0.5, -265.0, 3.60), (ent_x + 4.5, -259.0, 3.88), mat_limestone, coll_entrance)
    create_box("MCUT_Entrance_Canopy_Fascia", (ent_x - 0.55, -265.05, 3.80), (ent_x + 4.55, -258.95, 3.92), mat_aluminum, coll_entrance)
    for dl_y in [-263.5, -262.0, -260.5]:
        for dl_x in [ent_x + 1.5, ent_x + 3.2]:
            create_box(f"MCUT_Canopy_Soffit_Light_{dl_x}_{dl_y}", (dl_x - 0.2, dl_y - 0.2, 3.58), (dl_x + 0.2, dl_y + 0.2, 3.60), mat_aluminum, coll_entrance)

    # Dimensional Cast Bronze Lettering "MCCUTCHEON HALL"
    # Mounted on the return brick wall facing MacArthur Drive at X = -1183.35, Y = -274.0, Z = 4.10m
    # (Matches exact position and scale seen in harrison_arch_photo.jpg)
    font_curve1 = bpy.data.curves.new(name="McCutcheon_Sign_Wall_Font", type='FONT')
    font_curve1.body = "MCCUTCHEON HALL"
    font_curve1.size = 0.50
    font_curve1.extrude = 0.06
    font_curve1.bevel_depth = 0.015
    sign_obj1 = bpy.data.objects.new("MCUT_Sign_McCutcheon_Hall_Wall", font_curve1)
    sign_obj1.location = Vector((-1183.32, -274.2, 4.10))
    sign_obj1.rotation_euler = (math.radians(90.0), 0.0, math.radians(90.0))
    sign_obj1.data.materials.append(mat_bronze)
    coll_entrance.objects.link(sign_obj1)

    # Horizontal Ashlar Panel Joints on Limestone Wall (at Z = 0.70m and 1.40m)
    for aj_z in [0.70, 1.40]:
        create_box(f"MCUT_Ashlar_Joint_{aj_z}", (ent_x - 0.1, -267.5, aj_z), (-1183.4, -257.0, aj_z + 0.02), mat_concrete, coll_entrance)

    # Architectural Bronze Wall Sconces
    for sc_y in [-265.5, -258.5, -256.5]:
        create_box(f"MCUT_Wall_Sconce_{sc_y}", (ent_x + 0.05, sc_y - 0.15, 2.80), (ent_x + 0.25, sc_y + 0.15, 3.35), mat_bronze, coll_entrance)

    # Planters & Bicycle Racks (as seen in archival photo)
    create_box("MCUT_Entrance_Planter_Curb", (-1183.0, -271.5, 0.0), (-1180.5, -267.5, 0.40), mat_limestone, coll_entrance)
    create_box("MCUT_Entrance_Shrubs", (-1182.8, -271.3, 0.40), (-1180.7, -267.7, 1.30), mat_shrub, coll_entrance)
    
    # Bicycle racks with parked bicycles
    for b_idx, by in enumerate([-277.0, -276.0, -275.0, -274.0, -273.0]):
        create_box(f"MCUT_Bike_Rack_Loop_{b_idx}", (-1180.5, by - 0.03, 0.0), (-1179.5, by + 0.03, 0.90), mat_bike_rack, coll_entrance)
        create_box(f"MCUT_Bicycle_Frame_{b_idx}", (-1180.8, by - 0.10, 0.20), (-1179.2, by + 0.10, 0.85), mat_aluminum, coll_entrance)

    # Realistic Organic Courtyard Trees (multi-lobed canopy, matching archival photo)
    def create_organic_tree(name, root_x, root_y, height=7.5, radius=3.2):
        # Trunk
        mesh_trunk = bpy.data.meshes.new(f"{name}_Trunk")
        obj_trunk = bpy.data.objects.new(f"{name}_Trunk", mesh_trunk)
        bm_t = bmesh.new()
        bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=8, radius1=0.35, radius2=0.18, depth=height*0.55, matrix=Matrix.Translation((root_x, root_y, height*0.275)))
        bm_t.to_mesh(mesh_trunk)
        bm_t.free()
        mesh_trunk.materials.append(mat_bark)
        coll_site.objects.link(obj_trunk)

        # Foliage Clusters
        mesh_fol = bpy.data.meshes.new(f"{name}_Foliage")
        obj_fol = bpy.data.objects.new(f"{name}_Foliage", mesh_fol)
        bm_f = bmesh.new()
        clusters = [
            (root_x, root_y, height * 0.70, radius * 0.9),
            (root_x - radius*0.35, root_y + radius*0.25, height * 0.65, radius * 0.65),
            (root_x + radius*0.35, root_y - radius*0.20, height * 0.75, radius * 0.65),
            (root_x + radius*0.15, root_y + radius*0.35, height * 0.85, radius * 0.55)
        ]
        for cx, cy, cz, cr in clusters:
            bmesh.ops.create_icosphere(bm_f, subdivisions=2, radius=cr, matrix=Matrix.Translation((cx, cy, cz)))
        bm_f.to_mesh(mesh_fol)
        bm_f.free()
        mesh_fol.materials.append(mat_leaves)
        coll_site.objects.link(obj_fol)

    create_organic_tree("MCUT_Courtyard_Tree_1", -1172.0, -243.0, height=8.5, radius=3.4)
    create_organic_tree("MCUT_Courtyard_Tree_2", -1176.0, -238.0, height=7.2, radius=2.8)

    # 11. 3D Architectural Window Bay Assemblies with Frames, Awning Transoms & Teal Spandrels
    def generate_detailed_window_bays(facade_id, start_x, end_x, wall_y, normal_y, bay_count, is_x_facade=True):
        dx = (end_x - start_x) / bay_count
        win_w = min(1.55, abs(dx) * 0.58)
        
        mesh_win = bpy.data.meshes.new(f"MCUT_{facade_id}_Glass")
        obj_win = bpy.data.objects.new(f"MCUT_{facade_id}_Glass", mesh_win)
        bm_win = bmesh.new()

        mesh_spand = bpy.data.meshes.new(f"MCUT_{facade_id}_Spandrels")
        obj_spand = bpy.data.objects.new(f"MCUT_{facade_id}_Spandrels", mesh_spand)
        bm_spand = bmesh.new()

        mesh_frame = bpy.data.meshes.new(f"MCUT_{facade_id}_Frames")
        obj_frame = bpy.data.objects.new(f"MCUT_{facade_id}_Frames", mesh_frame)
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

                # 2. Window Glazing & Extruded Awning Transoms (3 awning tiers matching harrison_historic_photo.jpg)
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
        coll_fenestration.objects.link(obj_win)

        bm_spand.to_mesh(mesh_spand)
        bm_spand.free()
        mesh_spand.materials.append(mat_spandrel)
        coll_fenestration.objects.link(obj_spand)

        bm_frame.to_mesh(mesh_frame)
        bm_frame.free()
        mesh_frame.materials.append(mat_aluminum)
        coll_fenestration.objects.link(obj_frame)

    # North Tower Window Bays
    generate_detailed_window_bays("NorthTower_North", nw_x_min + 2.5, nw_x_max - 2.5, nw_y_max, normal_y=1.0, bay_count=17, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_South_W", nw_x_min + 2.0, -1240.2, nw_y_min, normal_y=-1.0, bay_count=3, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_South_E", -1207.8, nw_x_max - 2.0, nw_y_min, normal_y=-1.0, bay_count=5, is_x_facade=True)
    generate_detailed_window_bays("NorthTower_West", nw_y_min + 1.8, nw_y_max - 1.8, nw_x_min, normal_y=-1.0, bay_count=3, is_x_facade=False)
    generate_detailed_window_bays("NorthTower_East", nw_y_min + 1.8, nw_y_max - 1.8, nw_x_max, normal_y=1.0, bay_count=3, is_x_facade=False)

    # South Tower Window Bays
    generate_detailed_window_bays("SouthTower_South", sw_x_min + 2.5, sw_x_max - 2.5, sw_y_min, normal_y=-1.0, bay_count=17, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_North_W", sw_x_min + 2.0, -1239.9, sw_y_max, normal_y=1.0, bay_count=3, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_North_E", -1207.4, sw_x_max - 2.0, sw_y_max, normal_y=1.0, bay_count=5, is_x_facade=True)
    generate_detailed_window_bays("SouthTower_West", sw_y_min + 1.8, sw_y_max - 1.8, sw_x_min, normal_y=-1.0, bay_count=3, is_x_facade=False)
    generate_detailed_window_bays("SouthTower_East", sw_y_min + 1.8, sw_y_max - 1.8, sw_x_max, normal_y=1.0, bay_count=3, is_x_facade=False)

    # 12. Interior: Missing floorplans explicitly treated as unverified shell
    create_box("MCUT_Interior_North_Tower_Unverified_Shell", (-1252.0, -229.3, 0.2), (-1190.2, -217.9, 26.2), mat_concrete, coll_structure)
    create_box("MCUT_Interior_South_Tower_Unverified_Shell", (-1251.6, -303.3, 0.2), (-1189.6, -291.7, 26.2), mat_concrete, coll_structure)
    create_box("MCUT_Interior_Central_Pavilion_Unverified_Shell", (-1239.5, -279.8, 0.2), (-1207.8, -241.6, 7.2), mat_concrete, coll_structure)

    # 13. Lighting Setup (Natural Purdue Daylight Sun + Ambient Sky)
    sun_data = bpy.data.lights.new(name="Sun_Purdue_Daylight", type='SUN')
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.98, 0.94)
    sun_obj = bpy.data.objects.new("Sun_Purdue_Daylight", sun_data)
    sun_obj.rotation_euler = (math.radians(46.0), math.radians(-24.0), math.radians(50.0))
    coll_site.objects.link(sun_obj)

    scene.world = bpy.data.worlds.new("Purdue_World")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.75, 0.85, 0.95, 1.0)
        bg_node.inputs['Strength'].default_value = 0.75

    # 14. Inspection Cameras
    # Cam 1: Top-down Orthographic (North Up, East Right)
    cam1_data = bpy.data.cameras.new("Cam_TopDown_Footprint")
    cam1_data.type = 'ORTHO'
    cam1_data.ortho_scale = 175.0
    cam1_obj = bpy.data.objects.new("Cam_TopDown_Footprint", cam1_data)
    cam1_obj.location = Vector((official_center[0], official_center[1], 140.0))
    cam1_obj.rotation_euler = (0.0, 0.0, 0.0)
    coll_cams.objects.link(cam1_obj)

    # Cam 2: Hero Perspective View (South-East looking North-West)
    cam2_data = bpy.data.cameras.new("Cam_Hero_Perspective")
    cam2_data.type = 'PERSP'
    cam2_data.lens = 30.0
    cam2_obj = bpy.data.objects.new("Cam_Hero_Perspective", cam2_data)
    cam2_obj.location = Vector((-1135.0, -350.0, 50.0))
    dir2 = (Vector((official_center[0], official_center[1], 14.0)) - cam2_obj.location).normalized()
    cam2_obj.rotation_euler = dir2.to_track_quat('-Z', 'Y').to_euler()
    coll_cams.objects.link(cam2_obj)

    # Cam 3: Street-Level East Entrance View (Matching Archival Photo Composition)
    # Camera standing back in East courtyard/plaza looking towards entrance:
    # Right: North Tower with limestone base and 2-story decorative solar screen (brise-soleil)
    # Center: Cantilevered canopy, arrival steps, aluminum handrails, commercial double doors
    # Left: South Tower with limestone base, "MCCUTCHEON HALL" bronze lettering, shrubs, bike racks
    cam3_data = bpy.data.cameras.new("Cam_East_Entrance")
    cam3_data.type = 'PERSP'
    cam3_data.lens = 24.0
    cam3_obj = bpy.data.objects.new("Cam_East_Entrance", cam3_data)
    cam3_obj.location = Vector((-1156.0, -263.5, 2.2))
    dir3 = (Vector((-1186.5, -260.5, 4.5)) - cam3_obj.location).normalized()
    cam3_obj.rotation_euler = dir3.to_track_quat('-Z', 'Y').to_euler()
    coll_cams.objects.link(cam3_obj)

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
    out_blend = r"c:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\mccutcheon_hall.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Successfully saved {out_blend}")

    # Render Attempt 1 Views
    renders = [
        (cam1_obj, "mccutcheon_attempt1_topdown.png"),
        (cam2_obj, "mccutcheon_attempt1_hero.png"),
        (cam3_obj, "mccutcheon_attempt1_entrance.png")
    ]
    
    render_paths = []
    for cam, fname in renders:
        scene.camera = cam
        out_path = os.path.abspath(fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        render_paths.append(out_path)
        print(f"Rendered {out_path}")

    return out_blend, render_paths

if __name__ == "__main__":
    build_mccutcheon_hall()
