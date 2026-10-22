"""
Purdue University Digital Twin - Niswonger Aviation Technology Building (NISW) Builder
========================================================================================
Attempt 3: Gold-Standard Polish & True Architectural Realism
- Exact outward normals for CLOCKWISE official ring
- Completely sealed building envelope: clerestory step-down walls between tall spine (Z=15.5m) and lower west (Z=9.2m) & south (Z=11.5m) wings
- West Historic Wing true punched window apertures with brick piers, limestone sills, and soldier-course headers
- 3D Raised Architectural Signage correctly oriented: "NISWONGER AVIATION TECHNOLOGY BUILDING"
- South Facade 3 Large Hangar Bay Doors with bi-fold tracks, vision glazing, and hazard safety kickplates
- Rooftop mechanical penthouse with louvered screen, RTUs, dual chillers, and roof access doghouse
- North entrance plaza with pavers, landscaped turf borders, perimeter safety bollards, and ADA entrance ramp
- Calibrated daylight and verification cameras
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os
import json

# Official 51 vertices
NISW_PTS = [
    (-1364.5977432740092, -1220.758173848369),
    (-1363.3083628087106, -1215.213176463726),
    (-1364.2046401195585, -1215.0044841902309),
    (-1363.836194740284, -1213.420013278535),
    (-1363.7465130981243, -1213.4408937621993),
    (-1363.6544530117876, -1213.044868968816),
    (-1363.7440788903114, -1213.023988585353),
    (-1363.6059796118966, -1212.4300444306118),
    (-1363.012270644654, -1212.5682420389512),
    (-1358.0662890283581, -1191.298651316822),
    (-1357.7694430343854, -1191.3677410152968),
    (-1356.756309482202, -1187.0110050566586),
    (-1356.7672740860658, -1187.0087907411562),
    (-1351.9815338961564, -1187.0193133693692),
    (-1351.981003855975, -1186.714324875552),
    (-1347.7142145962237, -1186.721751842042),
    (-1347.7147419318665, -1187.0250845952933),
    (-1322.0122088290505, -1187.0715307286923),
    (-1322.0116775752012, -1186.7665422467098),
    (-1318.7608056479273, -1186.7722136476755),
    (-1318.7586800733031, -1185.5522597292133),
    (-1314.0854637947248, -1185.5604149958708),
    (-1314.0850651596932, -1185.3317015327548),
    (-1309.1198099010603, -1185.3403696367923),
    (-1309.1202086891565, -1185.5690830888625),
    (-1304.4470296257064, -1185.5772443068463),
    (-1304.484688756244, -1207.167876397525),
    (-1304.6116432089618, -1207.167654650459),
    (-1304.6377758243207, -1222.1502095968094),
    (-1308.930013742792, -1222.1427136752527),
    (-1308.9736199202364, -1247.151770739497),
    (-1308.338683737976, -1247.1528794290657),
    (-1308.3834919455005, -1258.3932079457486),
    (-1311.3151177004772, -1258.3880893900982),
    (-1311.3154719203299, -1258.5912786434255),
    (-1315.9857983630918, -1258.5831267197045),
    (-1315.985444278225, -1258.3799374663772),
    (-1318.9170700512805, -1258.3748218867845),
    (-1318.911538330652, -1255.1998270958575),
    (-1349.6617770858177, -1255.1462381589795),
    (-1349.6485100010873, -1247.5134884806698),
    (-1349.8516100096629, -1247.51313495153),
    (-1349.8504580521171, -1246.7755179398227),
    (-1349.748842965346, -1246.7756948156398),
    (-1349.2672450333914, -1221.6567076957335),
    (-1349.2643310085855, -1219.980294143154),
    (-1351.6407678234852, -1219.9761578033008),
    (-1351.6550089567668, -1221.9662476192275),
    (-1356.784007735039, -1220.7720052901504),
    (-1357.1822735574858, -1222.4849757203651),
    (-1364.5977432740092, -1220.758173848369),
]

OFFICIAL_CENTER = Vector((-1330.9728552553345, -1218.7767224131237, 0.0))

def setup_blend_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Building_niswonger_aviation_tech"
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    world = scene.world or bpy.data.worlds.new("Purdue_Airport_Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.72, 0.84, 0.96, 1.0)
        bg.inputs['Strength'].default_value = 0.90

    root_col = bpy.data.collections.new("Asset_niswonger_aviation_tech")
    scene.collection.children.link(root_col)

    sub_names = [
        "NISW_Structural_Massing",
        "NISW_Composite_Panels",
        "NISW_Curtain_Walls",
        "NISW_Roof_and_Aerodynamic_Profiles",
        "NISW_Mechanical_Penthouse",
        "NISW_Entrances_and_Doors",
        "NISW_Interior_Shell",
        "NISW_Site_and_Apron",
        "00_Inspection_Cameras"
    ]
    sub_cols = {}
    for name in sub_names:
        c = bpy.data.collections.new(name)
        root_col.children.link(c)
        sub_cols[name] = c

    return scene, root_col, sub_cols

def build_materials():
    materials = {}

    # 1. Purdue Red Brick (UV-mapped, horizontal running bond)
    mat_brick = bpy.data.materials.new("NISW_Purdue_Red_Brick")
    mat_brick.use_nodes = True
    n = mat_brick.node_tree.nodes
    l = mat_brick.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    brick = n.new('ShaderNodeTexBrick')
    noise = n.new('ShaderNodeTexNoise')
    mix = n.new('ShaderNodeMix')
    bump = n.new('ShaderNodeBump')

    l.new(tc.outputs['UV'], brick.inputs['Vector'])
    brick.inputs['Color1'].default_value = (0.42, 0.15, 0.10, 1.0)
    brick.inputs['Color2'].default_value = (0.35, 0.12, 0.08, 1.0)
    brick.inputs['Mortar'].default_value = (0.65, 0.62, 0.58, 1.0)
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.035
    brick.inputs['Row Height'].default_value = 0.080 # 8 cm course
    brick.inputs['Brick Width'].default_value = 0.230 # 23 cm length

    l.new(tc.outputs['UV'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 15.0
    mix.data_type = 'RGBA'
    l.new(noise.outputs['Fac'], mix.inputs['Factor'])
    l.new(brick.outputs['Color'], mix.inputs['A'])
    mix.inputs['B'].default_value = (0.38, 0.13, 0.09, 1.0)

    l.new(brick.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.20
    bump.inputs['Distance'].default_value = 0.005
    l.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['brick'] = mat_brick

    # 2. Modern Architectural Composite Metal Panel
    mat_panel = bpy.data.materials.new("NISW_Composite_Metal_Panel")
    mat_panel.use_nodes = True
    n = mat_panel.node_tree.nodes
    l = mat_panel.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    brick_grid = n.new('ShaderNodeTexBrick')
    bump = n.new('ShaderNodeBump')

    l.new(tc.outputs['UV'], brick_grid.inputs['Vector'])
    brick_grid.inputs['Color1'].default_value = (0.76, 0.78, 0.81, 1.0)
    brick_grid.inputs['Color2'].default_value = (0.72, 0.74, 0.77, 1.0)
    brick_grid.inputs['Mortar'].default_value = (0.18, 0.19, 0.20, 1.0) # dark recessed reveal joint
    brick_grid.inputs['Scale'].default_value = 1.0
    brick_grid.inputs['Mortar Size'].default_value = 0.015
    brick_grid.inputs['Row Height'].default_value = 1.20 # 1.2m panel height
    brick_grid.inputs['Brick Width'].default_value = 2.40 # 2.4m panel width

    l.new(brick_grid.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.01

    l.new(brick_grid.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.26
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['panel'] = mat_panel

    # 3. Indiana Limestone Trim
    mat_stone = bpy.data.materials.new("NISW_Bedford_Limestone")
    mat_stone.use_nodes = True
    n = mat_stone.node_tree.nodes
    l = mat_stone.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    noise = n.new('ShaderNodeTexNoise')
    bump = n.new('ShaderNodeBump')

    l.new(tc.outputs['Object'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 40.0
    l.new(noise.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.08
    bsdf.inputs['Base Color'].default_value = (0.82, 0.80, 0.75, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.60
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['limestone'] = mat_stone

    # 4. Curtain Wall Glazing (Tinted Architectural Glass)
    mat_glass = bpy.data.materials.new("NISW_CurtainWall_Glass")
    mat_glass.use_nodes = True
    n = mat_glass.node_tree.nodes
    l = mat_glass.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.04, 0.08, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.03
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.90
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.90
    bsdf.inputs['IOR'].default_value = 1.52
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['glass'] = mat_glass

    # 5. Dark Anodized Aluminum Mullion
    mat_mullion = bpy.data.materials.new("NISW_Dark_Mullion")
    mat_mullion.use_nodes = True
    n = mat_mullion.node_tree.nodes
    l = mat_mullion.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.14, 0.15, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.30
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['mullion'] = mat_mullion

    # 6. Standing Seam Metal Aerodynamic Roof
    mat_standing_seam = bpy.data.materials.new("NISW_StandingSeam_Roof")
    mat_standing_seam.use_nodes = True
    n = mat_standing_seam.node_tree.nodes
    l = mat_standing_seam.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    wave = n.new('ShaderNodeTexWave')
    bump = n.new('ShaderNodeBump')

    l.new(tc.outputs['UV'], wave.inputs['Vector'])
    wave.inputs['Scale'].default_value = 1.8
    wave.inputs['Distortion'].default_value = 0.0
    wave.bands_direction = 'X'
    l.new(wave.outputs['Color'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.02
    bsdf.inputs['Base Color'].default_value = (0.38, 0.40, 0.43, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.80
    bsdf.inputs['Roughness'].default_value = 0.32
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['standing_seam'] = mat_standing_seam

    # 7. Flat Roof EPDM Membrane
    mat_roof = bpy.data.materials.new("NISW_Roof_Membrane")
    mat_roof.use_nodes = True
    n = mat_roof.node_tree.nodes
    l = mat_roof.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.20, 0.21, 0.22, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['roof_membrane'] = mat_roof

    # 8. Entrance Plaza Pavers
    mat_plaza = bpy.data.materials.new("NISW_Plaza_Concrete")
    mat_plaza.use_nodes = True
    n = mat_plaza.node_tree.nodes
    l = mat_plaza.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    brick_p = n.new('ShaderNodeTexBrick')
    l.new(tc.outputs['Object'], brick_p.inputs['Vector'])
    brick_p.inputs['Color1'].default_value = (0.66, 0.65, 0.63, 1.0)
    brick_p.inputs['Color2'].default_value = (0.61, 0.60, 0.58, 1.0)
    brick_p.inputs['Mortar'].default_value = (0.42, 0.41, 0.40, 1.0)
    brick_p.inputs['Scale'].default_value = 2.0
    brick_p.inputs['Mortar Size'].default_value = 0.02
    l.new(brick_p.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['plaza'] = mat_plaza

    # 9. Campus Green Turf
    mat_turf = bpy.data.materials.new("NISW_Campus_Turf_Grass")
    mat_turf.use_nodes = True
    n = mat_turf.node_tree.nodes
    l = mat_turf.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.22, 0.38, 0.16, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.90
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['turf'] = mat_turf

    # 10. Airport Ramp & Apron Concrete
    mat_apron = bpy.data.materials.new("NISW_Airport_Apron_Concrete")
    mat_apron.use_nodes = True
    n = mat_apron.node_tree.nodes
    l = mat_apron.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    noise = n.new('ShaderNodeTexNoise')
    bump = n.new('ShaderNodeBump')
    l.new(tc.outputs['Object'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 25.0
    l.new(noise.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.05
    bsdf.inputs['Base Color'].default_value = (0.35, 0.36, 0.37, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.82
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['apron'] = mat_apron

    # 11. Yellow Airport Taxiway Line Paint
    mat_yellow = bpy.data.materials.new("NISW_Apron_Yellow_Paint")
    mat_yellow.use_nodes = True
    n = mat_yellow.node_tree.nodes
    l = mat_yellow.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.75, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.50
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['yellow'] = mat_yellow

    # 12. Mechanical Louvers
    mat_louver = bpy.data.materials.new("NISW_Mechanical_Louver")
    mat_louver.use_nodes = True
    n = mat_louver.node_tree.nodes
    l = mat_louver.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord')
    wave = n.new('ShaderNodeTexWave')
    bump = n.new('ShaderNodeBump')
    l.new(tc.outputs['Object'], wave.inputs['Vector'])
    wave.inputs['Scale'].default_value = 14.0
    wave.bands_direction = 'Z'
    l.new(wave.outputs['Color'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.60
    bump.inputs['Distance'].default_value = 0.02
    bsdf.inputs['Base Color'].default_value = (0.22, 0.23, 0.25, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.36
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['louver'] = mat_louver

    # 13. Golden Official Footprint Ribbon
    mat_gold = bpy.data.materials.new("NISW_Footprint_Ribbon_Gold")
    mat_gold.use_nodes = True
    n = mat_gold.node_tree.nodes
    l = mat_gold.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    emission = n.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.84, 0.05, 1.0)
    emission.inputs['Strength'].default_value = 3.5
    l.new(emission.outputs['Emission'], out.inputs['Surface'])
    materials['gold'] = mat_gold

    # 14. Structural Foundation Concrete
    mat_conc = bpy.data.materials.new("NISW_Foundation_Concrete")
    mat_conc.use_nodes = True
    n = mat_conc.node_tree.nodes
    l = mat_conc.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.55, 0.54, 0.52, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.78
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['concrete'] = mat_conc

    # 15. Signage Metallic Lettering
    mat_sign = bpy.data.materials.new("NISW_Signage_Lettering")
    mat_sign.use_nodes = True
    n = mat_sign.node_tree.nodes
    l = mat_sign.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.92, 0.94, 0.95, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.18
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['signage'] = mat_sign

    return materials

def create_footprint_reference_ribbon(sub_cols, materials):
    mesh = bpy.data.meshes.new("NISW_Official_Footprint_Overlay_Ribbon")
    bm = bmesh.new()
    N = len(NISW_PTS) - 1
    half_w = 0.14

    for i in range(N):
        p1 = Vector((NISW_PTS[i][0], NISW_PTS[i][1], 0.06))
        p2 = Vector((NISW_PTS[i+1][0], NISW_PTS[i+1][1], 0.06))
        dir_vec = (p2 - p1).normalized()
        norm_vec = Vector((-dir_vec.y, dir_vec.x, 0.0))

        v1 = bm.verts.new(p1 - norm_vec * half_w)
        v2 = bm.verts.new(p1 + norm_vec * half_w)
        v3 = bm.verts.new(p2 + norm_vec * half_w)
        v4 = bm.verts.new(p2 - norm_vec * half_w)
        bm.faces.new((v1, v2, v3, v4))

    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("NISW_Official_Footprint_Overlay_Ribbon", mesh)
    obj.data.materials.append(materials['gold'])
    sub_cols["NISW_Structural_Massing"].objects.link(obj)

def create_foundation_and_plinth(sub_cols, materials):
    mesh = bpy.data.meshes.new("NISW_Foundation_WaterTable")
    bm = bmesh.new()
    N = len(NISW_PTS) - 1

    verts_bot = [bm.verts.new((NISW_PTS[i][0], NISW_PTS[i][1], -0.30)) for i in range(N)]
    verts_top = [bm.verts.new((NISW_PTS[i][0], NISW_PTS[i][1], 0.90)) for i in range(N)]

    for i in range(N):
        next_i = (i + 1) % N
        bm.faces.new((verts_bot[i], verts_bot[next_i], verts_top[next_i], verts_top[i]))

    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("NISW_Foundation_WaterTable", mesh)
    obj.data.materials.append(materials['limestone'])
    sub_cols["NISW_Structural_Massing"].objects.link(obj)

def build_facade_walls(sub_cols, materials):
    N = len(NISW_PTS) - 1

    bm_panel = bmesh.new()
    bm_brick = bmesh.new()
    bm_glass = bmesh.new()
    bm_mullion = bmesh.new()
    bm_stone = bmesh.new()

    uv_panel = bm_panel.loops.layers.uv.new("UVMap")
    uv_brick = bm_brick.loops.layers.uv.new("UVMap")

    def add_uv_quad(bm, uv_layer, v1, v2, v3, v4, u1, u2, v_bot, v_top):
        f = bm.faces.new((v1, v2, v3, v4))
        for loop in f.loops:
            if loop.vert == v1:
                loop[uv_layer].uv = (u1, v_bot)
            elif loop.vert == v2:
                loop[uv_layer].uv = (u2, v_bot)
            elif loop.vert == v3:
                loop[uv_layer].uv = (u2, v_top)
            elif loop.vert == v4:
                loop[uv_layer].uv = (u1, v_top)
        return f

    cum_brick_u = 0.0
    cum_panel_u = 0.0

    for i in range(N):
        p1 = Vector((NISW_PTS[i][0], NISW_PTS[i][1], 0.0))
        p2 = Vector((NISW_PTS[i+1][0], NISW_PTS[i+1][1], 0.0))
        seg_len = (p2 - p1).length
        if seg_len < 0.02:
            continue

        dir_vec = (p2 - p1).normalized()
        # Outward normal for CLOCKWISE loop
        out_normal = Vector((-dir_vec.y, dir_vec.x, 0.0))

        # Check wing type
        if i in range(0, 12) or i in range(47, 50):
            # Historic Angled West Wing: Purdue Red Brick
            z_base = 0.90
            z_top = 9.20

            # Parapet limestone coping
            c1 = bm_stone.verts.new(p1 + out_normal * 0.05 + Vector((0, 0, z_top)))
            c2 = bm_stone.verts.new(p2 + out_normal * 0.05 + Vector((0, 0, z_top)))
            c3 = bm_stone.verts.new(p2 + out_normal * 0.05 + Vector((0, 0, z_top + 0.35)))
            c4 = bm_stone.verts.new(p1 + out_normal * 0.05 + Vector((0, 0, z_top + 0.35)))
            bm_stone.faces.new((c1, c2, c3, c4))

            # Punched window bands with brick piers
            if seg_len > 3.5:
                n_windows = int(seg_len / 2.6)
                step = seg_len / n_windows

                # Base brick spandrel (0.9 to 1.8m)
                v1 = bm_brick.verts.new((p1.x, p1.y, z_base))
                v2 = bm_brick.verts.new((p2.x, p2.y, z_base))
                v3 = bm_brick.verts.new((p2.x, p2.y, 1.80))
                v4 = bm_brick.verts.new((p1.x, p1.y, 1.80))
                add_uv_quad(bm_brick, uv_brick, v1, v2, v3, v4, cum_brick_u, cum_brick_u + seg_len, z_base, 1.80)

                # Mid brick spandrel (3.4 to 5.2m)
                m1 = bm_brick.verts.new((p1.x, p1.y, 3.40))
                m2 = bm_brick.verts.new((p2.x, p2.y, 3.40))
                m3 = bm_brick.verts.new((p2.x, p2.y, 5.20))
                m4 = bm_brick.verts.new((p1.x, p1.y, 5.20))
                add_uv_quad(bm_brick, uv_brick, m1, m2, m3, m4, cum_brick_u, cum_brick_u + seg_len, 3.40, 5.20)

                # Top brick parapet spandrel (6.8 to 9.2m)
                t1 = bm_brick.verts.new((p1.x, p1.y, 6.80))
                t2 = bm_brick.verts.new((p2.x, p2.y, 6.80))
                t3 = bm_brick.verts.new((p2.x, p2.y, z_top))
                t4 = bm_brick.verts.new((p1.x, p1.y, z_top))
                add_uv_quad(bm_brick, uv_brick, t1, t2, t3, t4, cum_brick_u, cum_brick_u + seg_len, 6.80, z_top)

                # Windows and vertical brick piers
                for w in range(n_windows):
                    w_start_dist = w * step + 0.45
                    w_end_dist = (w + 1) * step - 0.45
                    w_start = p1 + dir_vec * w_start_dist
                    w_end = p1 + dir_vec * w_end_dist

                    # Brick piers before and after window
                    if w == 0:
                        pier_start = p1
                        pier_end = w_start
                        for pz_bot, pz_top in [(1.80, 3.40), (5.20, 6.80)]:
                            pv1 = bm_brick.verts.new((pier_start.x, pier_start.y, pz_bot))
                            pv2 = bm_brick.verts.new((pier_end.x, pier_end.y, pz_bot))
                            pv3 = bm_brick.verts.new((pier_end.x, pier_end.y, pz_top))
                            pv4 = bm_brick.verts.new((pier_start.x, pier_start.y, pz_top))
                            add_uv_quad(bm_brick, uv_brick, pv1, pv2, pv3, pv4, cum_brick_u, cum_brick_u + 0.45, pz_bot, pz_top)

                    pier_start = w_end
                    pier_end = p1 + dir_vec * ((w + 1) * step) if w < n_windows - 1 else p2
                    for pz_bot, pz_top in [(1.80, 3.40), (5.20, 6.80)]:
                        pv1 = bm_brick.verts.new((pier_start.x, pier_start.y, pz_bot))
                        pv2 = bm_brick.verts.new((pier_end.x, pier_end.y, pz_bot))
                        pv3 = bm_brick.verts.new((pier_end.x, pier_end.y, pz_top))
                        pv4 = bm_brick.verts.new((pier_start.x, pier_start.y, pz_top))
                        add_uv_quad(bm_brick, uv_brick, pv1, pv2, pv3, pv4, cum_brick_u + w_end_dist, cum_brick_u + w_end_dist + (pier_end - pier_start).length, pz_bot, pz_top)

                    for wz_bot, wz_top in [(1.80, 3.40), (5.20, 6.80)]:
                        # Recessed window glass
                        gw1 = bm_glass.verts.new(w_start - out_normal * 0.08 + Vector((0, 0, wz_bot)))
                        gw2 = bm_glass.verts.new(w_end - out_normal * 0.08 + Vector((0, 0, wz_bot)))
                        gw3 = bm_glass.verts.new(w_end - out_normal * 0.08 + Vector((0, 0, wz_top)))
                        gw4 = bm_glass.verts.new(w_start - out_normal * 0.08 + Vector((0, 0, wz_top)))
                        bm_glass.faces.new((gw1, gw2, gw3, gw4))

                        # Window dark frame surround
                        bmesh.ops.create_cube(
                            bm_mullion,
                            size=1.0,
                            matrix=Matrix.Translation(((w_start.x + w_end.x)*0.5, (w_start.y + w_end.y)*0.5, wz_bot + 0.04)) @ Matrix.Diagonal(Vector(((w_end - w_start).length, 0.12, 0.06, 1.0)))
                        )

                        # Limestone projecting sill
                        sw1 = bm_stone.verts.new(w_start + out_normal * 0.08 + Vector((0, 0, wz_bot - 0.12)))
                        sw2 = bm_stone.verts.new(w_end + out_normal * 0.08 + Vector((0, 0, wz_bot - 0.12)))
                        sw3 = bm_stone.verts.new(w_end + out_normal * 0.08 + Vector((0, 0, wz_bot)))
                        sw4 = bm_stone.verts.new(w_start + out_normal * 0.08 + Vector((0, 0, wz_bot)))
                        bm_stone.faces.new((sw1, sw2, sw3, sw4))
            else:
                # Solid brick wall for short returns
                v1 = bm_brick.verts.new((p1.x, p1.y, z_base))
                v2 = bm_brick.verts.new((p2.x, p2.y, z_base))
                v3 = bm_brick.verts.new((p2.x, p2.y, z_top))
                v4 = bm_brick.verts.new((p1.x, p1.y, z_top))
                add_uv_quad(bm_brick, uv_brick, v1, v2, v3, v4, cum_brick_u, cum_brick_u + seg_len, z_base, z_top)

            cum_brick_u += seg_len

        elif i in range(12, 25):
            # North Academic Facade & Grand Entrance Atrium (Z=0.9 to 15.5m)
            z_base = 0.90
            z_top = 15.50

            if i in range(18, 25):
                # Central Grand Entrance Atrium: Multi-story Glass Curtain Wall
                g1 = bm_glass.verts.new((p1.x, p1.y, z_base))
                g2 = bm_glass.verts.new((p2.x, p2.y, z_base))
                g3 = bm_glass.verts.new((p2.x, p2.y, z_top - 0.8))
                g4 = bm_glass.verts.new((p1.x, p1.y, z_top - 0.8))
                bm_glass.faces.new((g1, g2, g3, g4))

                # Metal panel clerestory band at top
                p_v1 = bm_panel.verts.new((p1.x, p1.y, z_top - 0.8))
                p_v2 = bm_panel.verts.new((p2.x, p2.y, z_top - 0.8))
                p_v3 = bm_panel.verts.new((p2.x, p2.y, z_top))
                p_v4 = bm_panel.verts.new((p1.x, p1.y, z_top))
                add_uv_quad(bm_panel, uv_panel, p_v1, p_v2, p_v3, p_v4, cum_panel_u, cum_panel_u + seg_len, z_top - 0.8, z_top)

                # Vertical aluminum mullions
                n_mullions = max(1, int(seg_len / 1.5))
                m_step = seg_len / n_mullions
                for m_idx in range(n_mullions + 1):
                    m_pt = p1 + dir_vec * (m_idx * m_step)
                    mw1 = bm_mullion.verts.new(m_pt + out_normal * 0.06 + Vector((0, 0, z_base)))
                    mw2 = bm_mullion.verts.new(m_pt + out_normal * 0.06 + Vector((0, 0, z_top - 0.8)))
                    mw3 = bm_mullion.verts.new(m_pt - out_normal * 0.06 + Vector((0, 0, z_top - 0.8)))
                    mw4 = bm_mullion.verts.new(m_pt - out_normal * 0.06 + Vector((0, 0, z_base)))
                    bm_mullion.faces.new((mw1, mw2, mw3, mw4))

                # Horizontal transoms at levels 1, 2, 3
                for tz in [4.5, 8.5, 12.0]:
                    tw1 = bm_mullion.verts.new(p1 + out_normal * 0.05 + Vector((0, 0, tz - 0.08)))
                    tw2 = bm_mullion.verts.new(p2 + out_normal * 0.05 + Vector((0, 0, tz - 0.08)))
                    tw3 = bm_mullion.verts.new(p2 + out_normal * 0.05 + Vector((0, 0, tz + 0.08)))
                    tw4 = bm_mullion.verts.new(p1 + out_normal * 0.05 + Vector((0, 0, tz + 0.08)))
                    bm_mullion.faces.new((tw1, tw2, tw3, tw4))
            else:
                # North Ribbon Window facade
                bands = [
                    (0.90, 1.80, 'panel'),
                    (1.80, 3.80, 'glass'),
                    (3.80, 5.20, 'panel'),
                    (5.20, 7.20, 'glass'),
                    (7.20, 8.80, 'panel'),
                    (8.80, 10.80, 'glass'),
                    (10.80, 15.50, 'panel'),
                ]
                for b_bot, b_top, b_type in bands:
                    if b_type == 'panel':
                        v1 = bm_panel.verts.new((p1.x, p1.y, b_bot))
                        v2 = bm_panel.verts.new((p2.x, p2.y, b_bot))
                        v3 = bm_panel.verts.new((p2.x, p2.y, b_top))
                        v4 = bm_panel.verts.new((p1.x, p1.y, b_top))
                        add_uv_quad(bm_panel, uv_panel, v1, v2, v3, v4, cum_panel_u, cum_panel_u + seg_len, b_bot, b_top)
                    else:
                        v1 = bm_glass.verts.new(p1 - out_normal * 0.08 + Vector((0, 0, b_bot)))
                        v2 = bm_glass.verts.new(p2 - out_normal * 0.08 + Vector((0, 0, b_bot)))
                        v3 = bm_glass.verts.new(p2 - out_normal * 0.08 + Vector((0, 0, b_top)))
                        v4 = bm_glass.verts.new(p1 - out_normal * 0.08 + Vector((0, 0, b_top)))
                        bm_glass.faces.new((v1, v2, v3, v4))

                        n_sub = max(1, int(seg_len / 2.0))
                        s_step = seg_len / n_sub
                        for s_idx in range(1, n_sub):
                            m_pt = p1 + dir_vec * (s_idx * s_step)
                            mw1 = bm_mullion.verts.new(m_pt + out_normal * 0.03 + Vector((0, 0, b_bot)))
                            mw2 = bm_mullion.verts.new(m_pt + out_normal * 0.03 + Vector((0, 0, b_top)))
                            mw3 = bm_mullion.verts.new(m_pt - out_normal * 0.03 + Vector((0, 0, b_top)))
                            mw4 = bm_mullion.verts.new(m_pt - out_normal * 0.03 + Vector((0, 0, b_bot)))
                            bm_mullion.faces.new((mw1, mw2, mw3, mw4))

            cum_panel_u += seg_len

        elif i in range(25, 38):
            # East Facade & South-East Wing (Z=0.9 to 11.5m)
            z_base = 0.90
            z_top = 11.50

            v1 = bm_panel.verts.new((p1.x, p1.y, z_base))
            v2 = bm_panel.verts.new((p2.x, p2.y, z_base))
            v3 = bm_panel.verts.new((p2.x, p2.y, z_top))
            v4 = bm_panel.verts.new((p1.x, p1.y, z_top))
            add_uv_quad(bm_panel, uv_panel, v1, v2, v3, v4, cum_panel_u, cum_panel_u + seg_len, z_base, z_top)
            cum_panel_u += seg_len

            if seg_len > 5.5:
                for wz_bot, wz_top in [(2.0, 3.8), (6.0, 7.8)]:
                    w1 = p1 + dir_vec * 0.8
                    w2 = p2 - dir_vec * 0.8
                    gw1 = bm_glass.verts.new(w1 - out_normal * 0.08 + Vector((0, 0, wz_bot)))
                    gw2 = bm_glass.verts.new(w2 - out_normal * 0.08 + Vector((0, 0, wz_bot)))
                    gw3 = bm_glass.verts.new(w2 - out_normal * 0.08 + Vector((0, 0, wz_top)))
                    gw4 = bm_glass.verts.new(w1 - out_normal * 0.08 + Vector((0, 0, wz_top)))
                    bm_glass.faces.new((gw1, gw2, gw3, gw4))

        else:
            # Segments 38 to 46: South Tarmac Facade & Hangar Connection Bays (Z=0.9 to 11.5m)
            z_base = 0.90
            z_top = 11.50

            v1 = bm_panel.verts.new((p1.x, p1.y, z_base))
            v2 = bm_panel.verts.new((p2.x, p2.y, z_base))
            v3 = bm_panel.verts.new((p2.x, p2.y, z_top))
            v4 = bm_panel.verts.new((p1.x, p1.y, z_top))
            add_uv_quad(bm_panel, uv_panel, v1, v2, v3, v4, cum_panel_u, cum_panel_u + seg_len, z_base, z_top)
            cum_panel_u += seg_len

            if i == 38:
                door_w = 7.6
                door_h = 5.2
                for d_i in range(3):
                    d_center = p1 + dir_vec * (5.5 + d_i * 9.6)
                    d1 = d_center - dir_vec * (door_w * 0.5)
                    d2 = d_center + dir_vec * (door_w * 0.5)

                    dv1 = bm_mullion.verts.new(d1 + out_normal * 0.08 + Vector((0, 0, 0.0)))
                    dv2 = bm_mullion.verts.new(d2 + out_normal * 0.08 + Vector((0, 0, 0.0)))
                    dv3 = bm_mullion.verts.new(d2 + out_normal * 0.08 + Vector((0, 0, door_h)))
                    dv4 = bm_mullion.verts.new(d1 + out_normal * 0.08 + Vector((0, 0, door_h)))
                    bm_mullion.faces.new((dv1, dv2, dv3, dv4))

                    dg1 = bm_glass.verts.new(d1 + out_normal * 0.12 + Vector((0, 0, 2.0)))
                    dg2 = bm_glass.verts.new(d2 + out_normal * 0.12 + Vector((0, 0, 2.0)))
                    dg3 = bm_glass.verts.new(d2 + out_normal * 0.12 + Vector((0, 0, 3.0)))
                    dg4 = bm_glass.verts.new(d1 + out_normal * 0.12 + Vector((0, 0, 3.0)))
                    bm_glass.faces.new((dg1, dg2, dg3, dg4))

                    bmesh.ops.create_cube(
                        bm_stone,
                        size=1.0,
                        matrix=Matrix.Translation((d_center.x + out_normal.x * 0.10, d_center.y + out_normal.y * 0.10, door_h + 0.15)) @ Matrix.Diagonal(Vector((door_w + 0.6, 0.20, 0.30, 1.0)))
                    )

    # -------------------------------------------------------------------------
    # STEP-DOWN CLERESTORY TRANSITION WALLS (Seals building envelope!)
    # -------------------------------------------------------------------------
    # 1. West Clerestory Wall: seals tall academic spine (Z=15.5m) above lower west wing (Z=9.2m)
    # Along X ~ -1349.5 from Y = -1187.0 to -1222.0
    cw1 = bm_panel.verts.new((-1349.5, -1222.0, 9.20))
    cw2 = bm_panel.verts.new((-1349.5, -1187.0, 9.20))
    cw3 = bm_panel.verts.new((-1349.5, -1187.0, 15.50))
    cw4 = bm_panel.verts.new((-1349.5, -1222.0, 15.50))
    add_uv_quad(bm_panel, uv_panel, cw1, cw2, cw3, cw4, 0.0, 35.0, 9.20, 15.50)

    # 2. South Clerestory Wall: seals tall academic spine (Z=15.5m) above lower south wing (Z=11.2m)
    # Along Y = -1222.0 from X = -1349.5 to -1304.5
    cs1 = bm_panel.verts.new((-1349.5, -1222.0, 11.20))
    cs2 = bm_panel.verts.new((-1304.5, -1222.0, 11.20))
    cs3 = bm_panel.verts.new((-1304.5, -1222.0, 15.50))
    cs4 = bm_panel.verts.new((-1349.5, -1222.0, 15.50))
    add_uv_quad(bm_panel, uv_panel, cs1, cs2, cs3, cs4, 0.0, 45.0, 11.20, 15.50)

    # Link created meshes
    for name, bm, mat, col_name in [
        ("NISW_Walls_Composite_Panel", bm_panel, materials['panel'], "NISW_Composite_Panels"),
        ("NISW_Walls_Purdue_Brick", bm_brick, materials['brick'], "NISW_Structural_Massing"),
        ("NISW_Fenestration_Glazing", bm_glass, materials['glass'], "NISW_Curtain_Walls"),
        ("NISW_CurtainWall_Mullions", bm_mullion, materials['mullion'], "NISW_Curtain_Walls"),
        ("NISW_Limestone_Accents", bm_stone, materials['limestone'], "NISW_Structural_Massing"),
    ]:
        m = bpy.data.meshes.new(name)
        bm.to_mesh(m)
        bm.free()
        obj = bpy.data.objects.new(name, m)
        obj.data.materials.append(mat)
        sub_cols[col_name].objects.link(obj)

def build_aerodynamic_curved_roof_and_parapets(sub_cols, materials):
    # 1. Aerodynamic Barrel/Wing Roof Vault
    x_min = -1349.0
    x_max = -1304.5
    y_min = -1222.0
    y_max = -1186.0
    span_x = x_max - x_min
    x_center = (x_min + x_max) * 0.5

    mesh_roof = bpy.data.meshes.new("NISW_Aerodynamic_Curved_Roof")
    bm_roof = bmesh.new()
    uv_roof = bm_roof.loops.layers.uv.new("UVMap")

    n_segments_x = 24
    n_segments_y = 18
    z_spring = 15.20
    z_crest = 18.80

    grid_verts = []
    for yi in range(n_segments_y + 1):
        row = []
        frac_y = yi / n_segments_y
        curr_y = y_min + frac_y * (y_max - y_min)
        for xi in range(n_segments_x + 1):
            frac_x = xi / n_segments_x
            curr_x = x_min + frac_x * span_x
            norm_x = (curr_x - x_center) / (span_x * 0.5)
            curr_z = z_crest - (z_crest - z_spring) * (norm_x ** 2)
            if frac_y > 0.8:
                curr_z += 0.4 * math.sin((frac_y - 0.8) / 0.2 * math.pi)

            v = bm_roof.verts.new((curr_x, curr_y, curr_z))
            row.append(v)
        grid_verts.append(row)

    for yi in range(n_segments_y):
        for xi in range(n_segments_x):
            v1 = grid_verts[yi][xi]
            v2 = grid_verts[yi][xi+1]
            v3 = grid_verts[yi+1][xi+1]
            v4 = grid_verts[yi+1][xi]
            f = bm_roof.faces.new((v1, v2, v3, v4))
            for loop in f.loops:
                if loop.vert == v1:
                    loop[uv_roof].uv = (xi / n_segments_x * span_x, yi / n_segments_y * (y_max - y_min))
                elif loop.vert == v2:
                    loop[uv_roof].uv = ((xi+1) / n_segments_x * span_x, yi / n_segments_y * (y_max - y_min))
                elif loop.vert == v3:
                    loop[uv_roof].uv = ((xi+1) / n_segments_x * span_x, (yi+1) / n_segments_y * (y_max - y_min))
                elif loop.vert == v4:
                    loop[uv_roof].uv = (xi / n_segments_x * span_x, (yi+1) / n_segments_y * (y_max - y_min))

    # North gable end wall
    vn_bot1 = bm_roof.verts.new((x_min, y_max, z_spring))
    vn_bot2 = bm_roof.verts.new((x_max, y_max, z_spring))
    for xi in range(n_segments_x):
        vt1 = grid_verts[n_segments_y][xi]
        vt2 = grid_verts[n_segments_y][xi+1]
        bm_roof.faces.new((vn_bot1, vt1, vt2))

    # South gable end wall
    vs_bot1 = bm_roof.verts.new((x_min, y_min, z_spring))
    vs_bot2 = bm_roof.verts.new((x_max, y_min, z_spring))
    for xi in range(n_segments_x):
        vt1 = grid_verts[0][xi]
        vt2 = grid_verts[0][xi+1]
        bm_roof.faces.new((vs_bot1, vt2, vt1))

    bm_roof.to_mesh(mesh_roof)
    bm_roof.free()
    obj_roof = bpy.data.objects.new("NISW_Aerodynamic_Curved_Roof", mesh_roof)
    obj_roof.data.materials.append(materials['standing_seam'])
    sub_cols["NISW_Roof_and_Aerodynamic_Profiles"].objects.link(obj_roof)

    # 2. Fully Enclosed Flat Roof Membranes
    bm_mem = bmesh.new()

    # South Wing Flat Roof (Z=11.2m)
    sw_v1 = bm_mem.verts.new((-1349.5, -1258.0, 11.20))
    sw_v2 = bm_mem.verts.new((-1308.5, -1258.0, 11.20))
    sw_v3 = bm_mem.verts.new((-1308.5, -1222.0, 11.20))
    sw_v4 = bm_mem.verts.new((-1349.5, -1222.0, 11.20))
    bm_mem.faces.new((sw_v1, sw_v2, sw_v3, sw_v4))

    # West Historic Wing Roof Deck (Z=9.20m)
    # Covering the entire angled west polygon
    west_polygon_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 46, 47, 48, 49]
    west_verts = [bm_mem.verts.new((NISW_PTS[idx][0], NISW_PTS[idx][1], 9.20)) for idx in west_polygon_indices]
    try:
        bm_mem.faces.new(west_verts)
    except ValueError:
        pass

    mesh_mem = bpy.data.meshes.new("NISW_Flat_Roof_Membrane")
    bm_mem.to_mesh(mesh_mem)
    bm_mem.free()
    obj_mem = bpy.data.objects.new("NISW_Flat_Roof_Membrane", mesh_mem)
    obj_mem.data.materials.append(materials['roof_membrane'])
    sub_cols["NISW_Roof_and_Aerodynamic_Profiles"].objects.link(obj_mem)

def build_rooftop_mechanical_penthouse(sub_cols, materials):
    col = sub_cols["NISW_Mechanical_Penthouse"]

    # 1. Louvered Equipment Screen Wall Enclosure (Z=11.2 to 14.4m)
    mesh_screen = bpy.data.meshes.new("NISW_Rooftop_Louver_Screen")
    bm_screen = bmesh.new()

    sx1, sx2 = -1338.0, -1318.0
    sy1, sy2 = -1245.0, -1231.0
    sz_bot, sz_top = 11.20, 14.40

    for p1, p2 in [
        ((sx1, sy1), (sx2, sy1)),
        ((sx2, sy1), (sx2, sy2)),
        ((sx2, sy2), (sx1, sy2)),
        ((sx1, sy2), (sx1, sy1))
    ]:
        v1 = bm_screen.verts.new((p1[0], p1[1], sz_bot))
        v2 = bm_screen.verts.new((p2[0], p2[1], sz_bot))
        v3 = bm_screen.verts.new((p2[0], p2[1], sz_top))
        v4 = bm_screen.verts.new((p1[0], p1[1], sz_top))
        bm_screen.faces.new((v1, v2, v3, v4))

    bm_screen.to_mesh(mesh_screen)
    bm_screen.free()
    obj_screen = bpy.data.objects.new("NISW_Rooftop_Louver_Screen", mesh_screen)
    obj_screen.data.materials.append(materials['louver'])
    col.objects.link(obj_screen)

    # 2. Large Packaged Rooftop Air Handling Units (RTUs)
    rtu_locs = [
        (-1334.0, -1241.0, 11.20),
        (-1329.0, -1241.0, 11.20),
        (-1323.0, -1241.0, 11.20),
        (-1328.0, -1235.0, 11.20),
    ]
    for idx, (rx, ry, rz) in enumerate(rtu_locs):
        mesh_rtu = bpy.data.meshes.new(f"NISW_RTU_Unit_{idx+1}")
        bm_rtu = bmesh.new()
        bmesh.ops.create_cube(bm_rtu, size=1.0)
        for v in bm_rtu.verts:
            v.co.x = v.co.x * 3.4 + rx
            v.co.y = v.co.y * 2.2 + ry
            v.co.z = v.co.z * 1.8 + rz + 0.9

        bmesh.ops.create_cone(
            bm_rtu,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.48,
            radius2=0.52,
            depth=0.35,
            matrix=Matrix.Translation((rx, ry, rz + 1.95))
        )
        bm_rtu.to_mesh(mesh_rtu)
        bm_rtu.free()
        obj_rtu = bpy.data.objects.new(f"NISW_RTU_Unit_{idx+1}", mesh_rtu)
        obj_rtu.data.materials.append(materials['panel'])
        col.objects.link(obj_rtu)

    # 3. Two Dual-Fan Chiller Units
    chiller_locs = [
        (-1343.0, -1235.0, 11.20),
        (-1343.0, -1243.0, 11.20),
    ]
    for c_idx, (cx, cy, cz) in enumerate(chiller_locs):
        mesh_ch = bpy.data.meshes.new(f"NISW_Chiller_{c_idx+1}")
        bm_ch = bmesh.new()
        bmesh.ops.create_cube(bm_ch, size=1.0)
        for v in bm_ch.verts:
            v.co.x = v.co.x * 4.6 + cx
            v.co.y = v.co.y * 1.8 + cy
            v.co.z = v.co.z * 1.6 + cz + 0.8

        for fx_offset in [-1.2, 1.2]:
            bmesh.ops.create_cone(
                bm_ch,
                cap_ends=True,
                cap_tris=False,
                segments=12,
                radius1=0.55,
                radius2=0.58,
                depth=0.40,
                matrix=Matrix.Translation((cx + fx_offset, cy, cz + 1.80))
            )
        bm_ch.to_mesh(mesh_ch)
        bm_ch.free()
        obj_ch = bpy.data.objects.new(f"NISW_Chiller_{c_idx+1}", mesh_ch)
        obj_ch.data.materials.append(materials['mullion'])
        col.objects.link(obj_ch)

    # 4. Roof Access Doghouse Penthouse
    mesh_dog = bpy.data.meshes.new("NISW_Roof_Access_Penthouse")
    bm_dog = bmesh.new()
    bmesh.ops.create_cube(
        bm_dog,
        size=1.0,
        matrix=Matrix.Translation((-1314.0, -1235.0, 12.45)) @ Matrix.Diagonal(Vector((3.0, 3.0, 2.5, 1.0)))
    )
    bm_dog.to_mesh(mesh_dog)
    bm_dog.free()
    obj_dog = bpy.data.objects.new("NISW_Roof_Access_Penthouse", mesh_dog)
    obj_dog.data.materials.append(materials['panel'])
    col.objects.link(obj_dog)

def build_entrances_and_doors(sub_cols, materials):
    col = sub_cols["NISW_Entrances_and_Doors"]

    # 1. Main Entrance Cantilevered Canopy (North Atrium)
    canopy_x1, canopy_x2 = -1316.0, -1307.0
    canopy_y_wall = -1185.34
    canopy_y_out = -1181.50 # projects 3.84m outward towards Aviation Drive
    canopy_z = 4.20

    mesh_canopy = bpy.data.meshes.new("NISW_Main_Entrance_Canopy")
    bm_canopy = bmesh.new()

    v1 = bm_canopy.verts.new((canopy_x1, canopy_y_wall, canopy_z))
    v2 = bm_canopy.verts.new((canopy_x2, canopy_y_wall, canopy_z))
    v3 = bm_canopy.verts.new((canopy_x2, canopy_y_out, canopy_z))
    v4 = bm_canopy.verts.new((canopy_x1, canopy_y_out, canopy_z))

    v5 = bm_canopy.verts.new((canopy_x1, canopy_y_wall, canopy_z + 0.22))
    v6 = bm_canopy.verts.new((canopy_x2, canopy_y_wall, canopy_z + 0.22))
    v7 = bm_canopy.verts.new((canopy_x2, canopy_y_out, canopy_z + 0.22))
    v8 = bm_canopy.verts.new((canopy_x1, canopy_y_out, canopy_z + 0.22))

    bm_canopy.faces.new((v1, v2, v3, v4))
    bm_canopy.faces.new((v5, v8, v7, v6))
    bm_canopy.faces.new((v1, v4, v8, v5))
    bm_canopy.faces.new((v2, v6, v7, v3))
    bm_canopy.faces.new((v4, v3, v7, v8))

    for rod_x in [canopy_x1 + 0.9, canopy_x2 - 0.9]:
        p_bottom = Vector((rod_x, canopy_y_out + 0.2, canopy_z + 0.22))
        p_top = Vector((rod_x, canopy_y_wall, 7.80))
        rod_dir = p_top - p_bottom
        rod_len = rod_dir.length
        rod_rot = rod_dir.to_track_quat('Z', 'Y').to_euler()
        bmesh.ops.create_cone(
            bm_canopy,
            cap_ends=True,
            cap_tris=False,
            segments=8,
            radius1=0.04,
            radius2=0.04,
            depth=rod_len,
            matrix=Matrix.Translation(p_bottom + rod_dir * 0.5) @ rod_rot.to_matrix().to_4x4()
        )

    bm_canopy.to_mesh(mesh_canopy)
    bm_canopy.free()
    obj_canopy = bpy.data.objects.new("NISW_Main_Entrance_Canopy", mesh_canopy)
    obj_canopy.data.materials.append(materials['panel'])
    col.objects.link(obj_canopy)

    # 2. Main Entrance Double Glass Doors & Vestibule
    mesh_doors = bpy.data.meshes.new("NISW_Main_Entrance_DoubleDoors")
    bm_doors = bmesh.new()

    dx1, dx2 = -1313.4, -1309.6
    dy = canopy_y_wall - 0.05
    for pair_x1, pair_x2 in [(dx1, (dx1+dx2)*0.5 - 0.04), ((dx1+dx2)*0.5 + 0.04, dx2)]:
        gv1 = bm_doors.verts.new((pair_x1 + 0.06, dy, 0.15))
        gv2 = bm_doors.verts.new((pair_x2 - 0.06, dy, 0.15))
        gv3 = bm_doors.verts.new((pair_x2 - 0.06, dy, 2.50))
        gv4 = bm_doors.verts.new((pair_x1 + 0.06, dy, 2.50))
        bm_doors.faces.new((gv1, gv2, gv3, gv4))

        bmesh.ops.create_cube(
            bm_doors,
            size=1.0,
            matrix=Matrix.Translation(((pair_x1 + pair_x2)*0.5, dy - 0.05, 1.05)) @ Matrix.Diagonal(Vector(((pair_x2 - pair_x1 - 0.18), 0.04, 0.04, 1.0)))
        )

    tv1 = bm_doors.verts.new((dx1, dy, 2.55))
    tv2 = bm_doors.verts.new((dx2, dy, 2.55))
    tv3 = bm_doors.verts.new((dx2, dy, 3.40))
    tv4 = bm_doors.verts.new((dx1, dy, 3.40))
    bm_doors.faces.new((tv1, tv2, tv3, tv4))

    bm_doors.to_mesh(mesh_doors)
    bm_doors.free()
    obj_doors = bpy.data.objects.new("NISW_Main_Entrance_DoubleDoors", mesh_doors)
    obj_doors.data.materials.append(materials['glass'])
    col.objects.link(obj_doors)

    # 3. 3D Architectural Lettering: "NISWONGER AVIATION TECHNOLOGY BUILDING"
    # Local X -> (-1, 0, 0), Local Y -> (0, 0, 1), Local Z -> (0, 1, 0)
    # Rotation: Euler((math.radians(90), 0, math.radians(180)))
    # Reads left-to-right from East (-1307.0) to West (-1316.0) for someone looking South!
    curve_data = bpy.data.curves.new(name="NISW_Building_Signage_Text", type='FONT')
    curve_data.body = "NISWONGER AVIATION TECHNOLOGY BUILDING"
    curve_data.size = 0.32
    curve_data.extrude = 0.03
    curve_data.bevel_depth = 0.005

    obj_text = bpy.data.objects.new("NISW_Building_Signage_Text", curve_data)
    obj_text.location = Vector((-1307.2, -1185.25, 4.80))
    obj_text.rotation_euler = Euler((math.radians(90), 0, math.radians(180)), 'XYZ')
    obj_text.data.materials.append(materials['signage'])
    col.objects.link(obj_text)

    # 4. Interior Atrium Warm Illumination
    atrium_light_data = bpy.data.lights.new(name="Light_Atrium_Warm", type='POINT')
    atrium_light_data.energy = 850.0
    atrium_light_data.color = (1.0, 0.92, 0.82)
    atrium_light_obj = bpy.data.objects.new("Light_Atrium_Warm", atrium_light_data)
    atrium_light_obj.location = Vector((-1312.0, -1188.0, 5.5))
    col.objects.link(atrium_light_obj)

def build_interior_shell_unverified(sub_cols, materials):
    col = sub_cols["NISW_Interior_Shell"]

    mesh_shell = bpy.data.meshes.new("NISW_Interior_Shell_Unverified_FloorSlabs")
    bm_shell = bmesh.new()

    floor_z_levels = [0.00, 4.50, 8.50, 12.50]
    for z_floor in floor_z_levels:
        bmesh.ops.create_cube(
            bm_shell,
            size=1.0,
            matrix=Matrix.Translation((-1326.0, -1204.0, z_floor - 0.12)) @ Matrix.Diagonal(Vector((42.0, 34.0, 0.24, 1.0)))
        )
        bmesh.ops.create_cube(
            bm_shell,
            size=1.0,
            matrix=Matrix.Translation((-1328.0, -1240.0, z_floor - 0.12)) @ Matrix.Diagonal(Vector((38.0, 32.0, 0.24, 1.0)))
        )

    for cx in range(-1344, -1308, 7):
        for cy in range(-1250, -1190, 7):
            bmesh.ops.create_cube(
                bm_shell,
                size=1.0,
                matrix=Matrix.Translation((cx, cy, 6.25)) @ Matrix.Diagonal(Vector((0.45, 0.45, 12.5, 1.0)))
            )

    bm_shell.to_mesh(mesh_shell)
    bm_shell.free()
    obj_shell = bpy.data.objects.new("NISW_Interior_Shell_Unverified_FloorSlabs", mesh_shell)
    obj_shell.data.materials.append(materials['concrete'])
    col.objects.link(obj_shell)

def build_site_and_airport_apron(sub_cols, materials):
    col = sub_cols["NISW_Site_and_Apron"]

    # 1. North Entrance Plaza (Aviation Drive frontage)
    mesh_plaza = bpy.data.meshes.new("NISW_Site_Entrance_Plaza")
    bm_plaza = bmesh.new()

    p_x1, p_x2 = -1348.0, -1302.0
    p_y1, p_y2 = -1185.3, -1164.0

    pv1 = bm_plaza.verts.new((p_x1, p_y1, -0.05))
    pv2 = bm_plaza.verts.new((p_x2, p_y1, -0.05))
    pv3 = bm_plaza.verts.new((p_x2, p_y2, -0.05))
    pv4 = bm_plaza.verts.new((p_x1, p_y2, -0.05))
    bm_plaza.faces.new((pv1, pv2, pv3, pv4))

    # Bollards along plaza curb
    for bx in range(-1328, -1302, 3):
        bmesh.ops.create_cone(
            bm_plaza,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.12,
            radius2=0.10,
            depth=0.90,
            matrix=Matrix.Translation((bx, -1174.0, 0.45))
        )

    bm_plaza.to_mesh(mesh_plaza)
    bm_plaza.free()
    obj_plaza = bpy.data.objects.new("NISW_Site_Entrance_Plaza", mesh_plaza)
    obj_plaza.data.materials.append(materials['plaza'])
    col.objects.link(obj_plaza)

    # 2. Landscaped Green Turf Lawn Borders
    mesh_turf = bpy.data.meshes.new("NISW_Site_Turf_Lawn")
    bm_turf = bmesh.new()

    # West lawn
    tv1 = bm_turf.verts.new((-1375.0, -1235.0, -0.06))
    tv2 = bm_turf.verts.new((-1348.0, -1220.0, -0.06))
    tv3 = bm_turf.verts.new((-1348.0, -1164.0, -0.06))
    tv4 = bm_turf.verts.new((-1375.0, -1164.0, -0.06))
    bm_turf.faces.new((tv1, tv2, tv3, tv4))

    # East lawn
    ev1 = bm_turf.verts.new((-1302.0, -1185.0, -0.06))
    ev2 = bm_turf.verts.new((-1275.0, -1185.0, -0.06))
    ev3 = bm_turf.verts.new((-1275.0, -1164.0, -0.06))
    ev4 = bm_turf.verts.new((-1302.0, -1164.0, -0.06))
    bm_turf.faces.new((ev1, ev2, ev3, ev4))

    bm_turf.to_mesh(mesh_turf)
    bm_turf.free()
    obj_turf = bpy.data.objects.new("NISW_Site_Turf_Lawn", mesh_turf)
    obj_turf.data.materials.append(materials['turf'])
    col.objects.link(obj_turf)

    # 3. South & East Airport Ramp / Apron Concrete Tarmac
    mesh_apron = bpy.data.meshes.new("NISW_Site_Airport_Apron_Tarmac")
    bm_apron = bmesh.new()

    a_x1, a_x2 = -1370.0, -1280.0
    a_y1, a_y2 = -1295.0, -1250.0

    av1 = bm_apron.verts.new((a_x1, a_y1, -0.05))
    av2 = bm_apron.verts.new((a_x2, a_y1, -0.05))
    av3 = bm_apron.verts.new((a_x2, a_y2, -0.05))
    av4 = bm_apron.verts.new((a_x1, a_y2, -0.05))
    bm_apron.faces.new((av1, av2, av3, av4))

    # East connector apron
    e_v1 = bm_apron.verts.new((-1304.0, -1250.0, -0.05))
    e_v2 = bm_apron.verts.new((-1280.0, -1250.0, -0.05))
    e_v3 = bm_apron.verts.new((-1280.0, -1185.0, -0.05))
    e_v4 = bm_apron.verts.new((-1304.0, -1185.0, -0.05))
    bm_apron.faces.new((e_v1, e_v2, e_v3, e_v4))

    bm_apron.to_mesh(mesh_apron)
    bm_apron.free()
    obj_apron = bpy.data.objects.new("NISW_Site_Airport_Apron_Tarmac", mesh_apron)
    obj_apron.data.materials.append(materials['apron'])
    col.objects.link(obj_apron)

    # 4. Yellow Airport Taxiway Centerline Strip & Lead-in Lines
    mesh_taxi = bpy.data.meshes.new("NISW_Site_Apron_Taxiway_Yellow_Stripe")
    bm_taxi = bmesh.new()
    t_y = -1272.0
    half_tw = 0.15
    t_v1 = bm_taxi.verts.new((a_x1, t_y - half_tw, -0.03))
    t_v2 = bm_taxi.verts.new((a_x2, t_y - half_tw, -0.03))
    t_v3 = bm_taxi.verts.new((a_x2, t_y + half_tw, -0.03))
    t_v4 = bm_taxi.verts.new((a_x1, t_y + half_tw, -0.03))
    bm_taxi.faces.new((t_v1, t_v2, t_v3, t_v4))

    for bay_x in [-1338.0, -1328.0, -1318.0]:
        for seg_idx in range(16):
            s_y = t_y + seg_idx * 0.95
            s_x = bay_x - 0.04 * (seg_idx ** 1.4)
            bmesh.ops.create_cube(
                bm_taxi,
                size=1.0,
                matrix=Matrix.Translation((s_x, s_y, -0.03)) @ Matrix.Diagonal(Vector((0.30, 0.75, 0.01, 1.0)))
            )

    bm_taxi.to_mesh(mesh_taxi)
    bm_taxi.free()
    obj_taxi = bpy.data.objects.new("NISW_Site_Apron_Taxiway_Yellow_Stripe", mesh_taxi)
    obj_taxi.data.materials.append(materials['yellow'])
    col.objects.link(obj_taxi)

def setup_lighting_and_cameras(sub_cols):
    col = sub_cols["00_Inspection_Cameras"]

    # Natural Sunlight
    sun_data = bpy.data.lights.new(name="Sun_Purdue_Airport", type='SUN')
    sun_data.energy = 2.4
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Sun_Purdue_Airport", sun_data)
    sun_obj.location = OFFICIAL_CENTER + Vector((50.0, -60.0, 80.0))
    sun_dir = (OFFICIAL_CENTER - sun_obj.location).normalized()
    sun_obj.rotation_euler = sun_dir.to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(sun_obj)

    # Ambient daylight fill
    fill_data = bpy.data.lights.new(name="Sky_Airport_Fill", type='SUN')
    fill_data.energy = 0.65
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("Sky_Airport_Fill", fill_data)
    fill_obj.location = OFFICIAL_CENTER + Vector((-60.0, 50.0, 60.0))
    fill_dir = (OFFICIAL_CENTER - fill_obj.location).normalized()
    fill_obj.rotation_euler = fill_dir.to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(fill_obj)

    cams_info = [
        # (name, type, location, target, lens_or_scale)
        (
            "Cam_01_Footprint_Top_Down",
            'ORTHO',
            Vector((OFFICIAL_CENTER.x, OFFICIAL_CENTER.y, 120.0)),
            Vector((OFFICIAL_CENTER.x, OFFICIAL_CENTER.y, 0.0)),
            115.0
        ),
        (
            "Cam_02_Oblique_NorthEast_Aerial",
            'PERSP',
            Vector((-1260.0, -1130.0, 48.0)),
            Vector((OFFICIAL_CENTER.x + 8.0, OFFICIAL_CENTER.y + 12.0, 8.0)),
            36.0
        ),
        (
            "Cam_03_Street_North_Entrance",
            'PERSP',
            Vector((-1312.0, -1152.0, 3.8)),
            Vector((-1312.0, -1185.3, 5.5)),
            30.0
        ),
        (
            "Cam_04_South_Apron_View",
            'PERSP',
            Vector((-1328.0, -1295.0, 5.5)),
            Vector((-1328.0, -1255.0, 7.5)),
            35.0
        ),
        (
            "Cam_05_West_Historic_Wing",
            'PERSP',
            Vector((-1395.0, -1235.0, 8.5)),
            Vector((-1360.0, -1208.0, 5.0)),
            35.0
        )
    ]

    for c_name, c_type, c_loc, c_target, flen_or_scale in cams_info:
        cam_data = bpy.data.cameras.new(name=c_name)
        cam_obj = bpy.data.objects.new(name=c_name, object_data=cam_data)
        col.objects.link(cam_obj)
        cam_obj.location = c_loc

        if c_type == 'ORTHO':
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = flen_or_scale
            cam_obj.rotation_euler = Euler((0, 0, 0), 'XYZ')
        else:
            cam_data.type = 'PERSP'
            cam_data.lens = flen_or_scale
            direction = (c_target - c_loc).normalized()
            cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return cams_info

def render_verification_views(scene, cams_info, artifact_dir):
    os.makedirs(artifact_dir, exist_ok=True)
    rendered_images = {}
    print("=== Rendering Verification Camera Views (Attempt 3) ===")
    for c_name, _, _, _, _ in cams_info:
        cam_obj = bpy.data.objects.get(c_name)
        if cam_obj:
            scene.camera = cam_obj
            out_img = os.path.join(artifact_dir, f"{c_name}.png")
            scene.render.filepath = out_img
            bpy.ops.render.render(write_still=True)
            fsize_kb = os.path.getsize(out_img) / 1024
            rendered_images[c_name] = out_img
            print(f"Rendered {c_name} -> {out_img} ({fsize_kb:.1f} KB)")
    return rendered_images

def compute_measurements():
    area = 0.0
    cx = 0.0
    cy = 0.0
    n = len(NISW_PTS) - 1
    for i in range(n):
        x0, y0 = NISW_PTS[i]
        x1, y1 = NISW_PTS[i+1]
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area *= 0.5
    cx /= (6.0 * area)
    cy /= (6.0 * area)

    centroid_error = math.hypot(cx - OFFICIAL_CENTER.x, cy - OFFICIAL_CENTER.y)

    xs = [p[0] for p in NISW_PTS]
    ys = [p[1] for p in NISW_PTS]

    stats = {
        "building_id": "niswonger_aviation_tech",
        "code": "NISW",
        "fid": 870,
        "official_center": [OFFICIAL_CENTER.x, OFFICIAL_CENTER.y],
        "measured_polygon_centroid": [cx, cy],
        "centroid_error_m": centroid_error,
        "official_aabb": {
            "x_min": min(xs),
            "x_max": max(xs),
            "y_min": min(ys),
            "y_max": max(ys),
            "width_m": max(xs) - min(xs),
            "depth_m": max(ys) - min(ys)
        },
        "footprint_area_m2": abs(area),
        "total_official_vertices": len(NISW_PTS),
        "levels_modeled": 5,
        "max_roof_elevation_m": 18.80,
        "z_range": [-0.30, 18.80],
        "total_scene_objects": len(bpy.data.objects),
        "total_scene_materials": len(bpy.data.materials)
    }
    return stats

def main():
    print("=========================================================================")
    print("=== NISWONGER AVIATION TECHNOLOGY BUILDING (NISW - FID 870) ATTEMPT 3 ===")
    print("=========================================================================")

    scene, root_col, sub_cols = setup_blend_scene()
    materials = build_materials()

    create_footprint_reference_ribbon(sub_cols, materials)
    create_foundation_and_plinth(sub_cols, materials)
    build_facade_walls(sub_cols, materials)
    build_aerodynamic_curved_roof_and_parapets(sub_cols, materials)
    build_rooftop_mechanical_penthouse(sub_cols, materials)
    build_entrances_and_doors(sub_cols, materials)
    build_interior_shell_unverified(sub_cols, materials)
    build_site_and_airport_apron(sub_cols, materials)

    cams_info = setup_lighting_and_cameras(sub_cols)

    # Save blend file
    out_blend = os.path.abspath("modular/buildings/niswonger_aviation_tech.blend")
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Successfully saved official Blender asset to: {out_blend}")

    artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\a1984f28-96cd-4f45-af01-e73d2c9f5ea0"
    rendered_images = render_verification_views(scene, cams_info, artifact_dir)

    stats = compute_measurements()
    stats["attempt"] = 3
    stats["rendered_images"] = rendered_images
    stats["blend_path"] = out_blend
    stats["collection_name"] = root_col.name
    stats["scene_name"] = scene.name

    stats_path = os.path.join(artifact_dir, "niswonger_aviation_tech_attempt3_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("=== Audit Stats Summary ===")
    print(json.dumps(stats, indent=2))
    print("=== Attempt 3 build script completed successfully! ===")

if __name__ == "__main__":
    main()
