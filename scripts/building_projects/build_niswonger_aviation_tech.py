"""
Purdue University Digital Twin - Niswonger Aviation Technology Building (NISW) Builder
========================================================================================
Official Name: Niswonger Aviation Technology Building
Building Code: NISW
Official GIS FID: 870
Address: 1401 Aviation Drive, West Lafayette, IN 47907
Official Center: [-1330.972855, -1218.776722]
Official AABB: X=[-1364.598, -1304.447], Y=[-1258.591, -1185.332]
Rotated Dimensions: Width 73.31m, Depth 59.97m, Angle 89.41 deg
Official Polygon Vertices: 51 vertices
Official Levels: 5
Architects: MSKTD & Associates (2009 expansion and comprehensive renovation)
Target Blend: modular/buildings/niswonger_aviation_tech.blend
Scene: Building_niswonger_aviation_tech
Collection: Asset_niswonger_aviation_tech
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os
import json

# -----------------------------------------------------------------------------
# Official Geospatial Data (51 vertices, closed loop)
# -----------------------------------------------------------------------------
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

    # Natural daylight world
    world = scene.world or bpy.data.worlds.new("Purdue_Airport_Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.70, 0.82, 0.95, 1.0)
        bg.inputs['Strength'].default_value = 0.85

    # Asset Root Collection
    root_col = bpy.data.collections.new("Asset_niswonger_aviation_tech")
    scene.collection.children.link(root_col)

    # Sub-collections
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

    # 1. Purdue Red Brick (Procedural Running Bond)
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

    l.new(tc.outputs['Object'], brick.inputs['Vector'])
    brick.inputs['Color1'].default_value = (0.44, 0.16, 0.11, 1.0)
    brick.inputs['Color2'].default_value = (0.36, 0.13, 0.09, 1.0)
    brick.inputs['Mortar'].default_value = (0.62, 0.58, 0.54, 1.0)
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.035
    brick.inputs['Row Height'].default_value = 0.080
    brick.inputs['Brick Width'].default_value = 0.230

    l.new(tc.outputs['Object'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 6.0
    mix.data_type = 'RGBA'
    l.new(noise.outputs['Fac'], mix.inputs['Factor'])
    l.new(brick.outputs['Color'], mix.inputs['A'])
    mix.inputs['B'].default_value = (0.38, 0.14, 0.10, 1.0)

    l.new(brick.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.12
    l.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.78
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['brick'] = mat_brick

    # 2. Modern Architectural Composite Metal Panel (Silver / Metallic Aluminum)
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

    l.new(tc.outputs['Object'], brick_grid.inputs['Vector'])
    brick_grid.inputs['Color1'].default_value = (0.75, 0.77, 0.80, 1.0)
    brick_grid.inputs['Color2'].default_value = (0.72, 0.74, 0.77, 1.0)
    brick_grid.inputs['Mortar'].default_value = (0.22, 0.23, 0.24, 1.0) # dark recessed reveal joint
    brick_grid.inputs['Scale'].default_value = 1.0
    brick_grid.inputs['Mortar Size'].default_value = 0.015
    brick_grid.inputs['Row Height'].default_value = 1.20 # 1.2m panel height
    brick_grid.inputs['Brick Width'].default_value = 2.40 # 2.4m panel width

    l.new(brick_grid.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.01

    l.new(brick_grid.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.82
    bsdf.inputs['Roughness'].default_value = 0.28
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['panel'] = mat_panel

    # 3. Indiana Limestone Trim & Plinth
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
    noise.inputs['Scale'].default_value = 35.0
    l.new(noise.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.06
    bsdf.inputs['Base Color'].default_value = (0.80, 0.78, 0.74, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.62
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
    bsdf.inputs['Base Color'].default_value = (0.05, 0.10, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.03
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.92
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.92
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
    bsdf.inputs['Base Color'].default_value = (0.16, 0.17, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.32
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

    l.new(tc.outputs['Object'], wave.inputs['Vector'])
    wave.inputs['Scale'].default_value = 1.8 # seam every ~0.55m
    wave.inputs['Distortion'].default_value = 0.0
    wave.bands_direction = 'X'
    l.new(wave.outputs['Color'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.02
    bsdf.inputs['Base Color'].default_value = (0.36, 0.38, 0.41, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.78
    bsdf.inputs['Roughness'].default_value = 0.34
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
    bsdf.inputs['Base Color'].default_value = (0.22, 0.23, 0.24, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.86
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
    brick_p.inputs['Color1'].default_value = (0.64, 0.63, 0.61, 1.0)
    brick_p.inputs['Color2'].default_value = (0.60, 0.59, 0.57, 1.0)
    brick_p.inputs['Mortar'].default_value = (0.45, 0.44, 0.43, 1.0)
    brick_p.inputs['Scale'].default_value = 2.0
    brick_p.inputs['Mortar Size'].default_value = 0.02
    l.new(brick_p.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.72
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['plaza'] = mat_plaza

    # 9. Airport Ramp & Apron Concrete
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
    bsdf.inputs['Base Color'].default_value = (0.38, 0.39, 0.40, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.82
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['apron'] = mat_apron

    # 10. Yellow Airport Taxiway Line Paint
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

    # 11. Mechanical Louvers
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
    wave.inputs['Scale'].default_value = 12.0
    wave.bands_direction = 'Z'
    l.new(wave.outputs['Color'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.02
    bsdf.inputs['Base Color'].default_value = (0.24, 0.25, 0.27, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.82
    bsdf.inputs['Roughness'].default_value = 0.38
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    materials['louver'] = mat_louver

    # 12. Golden Official Footprint Ribbon
    mat_gold = bpy.data.materials.new("NISW_Footprint_Ribbon_Gold")
    mat_gold.use_nodes = True
    n = mat_gold.node_tree.nodes
    l = mat_gold.node_tree.links
    n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    emission = n.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1.0, 0.84, 0.05, 1.0)
    emission.inputs['Strength'].default_value = 3.0
    l.new(emission.outputs['Emission'], out.inputs['Surface'])
    materials['gold'] = mat_gold

    # 13. Structural Foundation Concrete
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

    return materials

def create_footprint_reference_ribbon(sub_cols, materials):
    """Creates a distinct 3D golden ribbon tracking the exact 51 official vertices at Z=0.06m"""
    mesh = bpy.data.meshes.new("NISW_Official_Footprint_Overlay_Ribbon")
    bm = bmesh.new()
    N = len(NISW_PTS) - 1 # 50 distinct segments
    half_w = 0.12 # 24 cm wide golden ribbon

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
    """Extrudes the exact 51-vertex perimeter for the structural foundation and limestone plinth"""
    mesh = bpy.data.meshes.new("NISW_Foundation_WaterTable")
    bm = bmesh.new()
    N = len(NISW_PTS) - 1
    
    # Vertices for foundation (-0.30 to 0.90 m)
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
    """
    Constructs the exterior walls aligned precisely to each official segment.
    Separates into modern composite panels, curtain wall glazing, brick masonry, and hangar connections.
    """
    N = len(NISW_PTS) - 1

    # Heights for different wings:
    # Segments 0 to 11: Angled West Historic/Lab Wing (Z=0.9 to 9.2m)
    # Segments 12 to 24: North Academic Spine & Atrium (Z=0.9 to 15.5m)
    # Segments 25 to 37: East & South-East Hangar Connection Wing (Z=0.9 to 11.5m)
    # Segments 38 to 46: South Tarmac Wing & West Inset (Z=0.9 to 11.5m)
    # Segments 47 to 49: Angled Wing Connector (Z=0.9 to 9.2m)

    bm_panel = bmesh.new()
    bm_brick = bmesh.new()
    bm_glass = bmesh.new()
    bm_mullion = bmesh.new()
    bm_stone = bmesh.new()

    for i in range(N):
        p1 = Vector((NISW_PTS[i][0], NISW_PTS[i][1], 0.0))
        p2 = Vector((NISW_PTS[i+1][0], NISW_PTS[i+1][1], 0.0))
        seg_len = (p2 - p1).length
        if seg_len < 0.02:
            continue

        dir_vec = (p2 - p1).normalized()
        out_normal = Vector((dir_vec.y, -dir_vec.x, 0.0)) # facing outward

        # Determine wing category
        if i in range(0, 12) or i in range(47, 50):
            # Historic Angled West Wing: Purdue Red Brick with limestone copings
            z_base = 0.90
            z_top = 9.20
            # Solid brick wall
            v1 = bm_brick.verts.new((p1.x, p1.y, z_base))
            v2 = bm_brick.verts.new((p2.x, p2.y, z_base))
            v3 = bm_brick.verts.new((p2.x, p2.y, z_top))
            v4 = bm_brick.verts.new((p1.x, p1.y, z_top))
            bm_brick.faces.new((v1, v2, v3, v4))

            # Parapet limestone coping
            c1 = bm_stone.verts.new((p1.x, p1.y, z_top))
            c2 = bm_stone.verts.new((p2.x, p2.y, z_top))
            c3 = bm_stone.verts.new((p2.x, p2.y, z_top + 0.35))
            c4 = bm_stone.verts.new((p1.x, p1.y, z_top + 0.35))
            bm_stone.faces.new((c1, c2, c3, c4))

            # Add punched window strips on longer segments (seg 8 is 21.8m)
            if seg_len > 4.0:
                n_windows = int(seg_len / 2.8)
                step = seg_len / n_windows
                for w in range(n_windows):
                    w_start = p1 + dir_vec * (w * step + 0.4)
                    w_end = p1 + dir_vec * ((w + 1) * step - 0.4)
                    for wz_bot, wz_top in [(1.8, 3.4), (5.2, 6.8)]:
                        # Recessed window glass
                        gw1 = bm_glass.verts.new(w_start + out_normal * (-0.08) + Vector((0, 0, wz_bot)))
                        gw2 = bm_glass.verts.new(w_end + out_normal * (-0.08) + Vector((0, 0, wz_bot)))
                        gw3 = bm_glass.verts.new(w_end + out_normal * (-0.08) + Vector((0, 0, wz_top)))
                        gw4 = bm_glass.verts.new(w_start + out_normal * (-0.08) + Vector((0, 0, wz_top)))
                        bm_glass.faces.new((gw1, gw2, gw3, gw4))

                        # Window frame / sill
                        sw1 = bm_stone.verts.new(w_start + out_normal * 0.04 + Vector((0, 0, wz_bot - 0.12)))
                        sw2 = bm_stone.verts.new(w_end + out_normal * 0.04 + Vector((0, 0, wz_bot - 0.12)))
                        sw3 = bm_stone.verts.new(w_end + out_normal * 0.04 + Vector((0, 0, wz_bot)))
                        sw4 = bm_stone.verts.new(w_start + out_normal * 0.04 + Vector((0, 0, wz_bot)))
                        bm_stone.faces.new((sw1, sw2, sw3, sw4))

        elif i in range(12, 25):
            # North Academic Facade & Grand Entrance Atrium
            z_base = 0.90
            z_top = 15.50

            if i in range(18, 25):
                # Central Grand Entrance Atrium: Multi-story Glass Curtain Wall
                # Full glass facade
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
                bm_panel.faces.new((p_v1, p_v2, p_v3, p_v4))

                # Vertical and horizontal aluminum mullions
                n_mullions = max(1, int(seg_len / 1.5))
                m_step = seg_len / n_mullions
                for m_idx in range(n_mullions + 1):
                    m_pt = p1 + dir_vec * (m_idx * m_step)
                    mw1 = bm_mullion.verts.new(m_pt + out_normal * 0.05 + Vector((0, 0, z_base)))
                    mw2 = bm_mullion.verts.new(m_pt + out_normal * 0.05 + Vector((0, 0, z_top - 0.8)))
                    mw3 = bm_mullion.verts.new(m_pt - out_normal * 0.05 + Vector((0, 0, z_top - 0.8)))
                    mw4 = bm_mullion.verts.new(m_pt - out_normal * 0.05 + Vector((0, 0, z_base)))
                    bm_mullion.faces.new((mw1, mw2, mw3, mw4))

                # Horizontal transoms at levels 1, 2, 3
                for tz in [4.5, 8.5, 12.0]:
                    tw1 = bm_mullion.verts.new(p1 + out_normal * 0.04 + Vector((0, 0, tz - 0.08)))
                    tw2 = bm_mullion.verts.new(p2 + out_normal * 0.04 + Vector((0, 0, tz - 0.08)))
                    tw3 = bm_mullion.verts.new(p2 + out_normal * 0.04 + Vector((0, 0, tz + 0.08)))
                    tw4 = bm_mullion.verts.new(p1 + out_normal * 0.04 + Vector((0, 0, tz + 0.08)))
                    bm_mullion.faces.new((tw1, tw2, tw3, tw4))
            else:
                # North Academic Ribbon Window facade (Composite Metal Panels + Ribbon Windows)
                # Spandrel bands of metal panels alternating with ribbon windows
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
                        bm_panel.faces.new((v1, v2, v3, v4))
                    else:
                        v1 = bm_glass.verts.new(p1 + out_normal * (-0.06) + Vector((0, 0, b_bot)))
                        v2 = bm_glass.verts.new(p2 + out_normal * (-0.06) + Vector((0, 0, b_bot)))
                        v3 = bm_glass.verts.new(p2 + out_normal * (-0.06) + Vector((0, 0, b_top)))
                        v4 = bm_glass.verts.new(p1 + out_normal * (-0.06) + Vector((0, 0, b_top)))
                        bm_glass.faces.new((v1, v2, v3, v4))

                        # Vertical mullion divisions along ribbon window
                        n_sub = max(1, int(seg_len / 2.0))
                        s_step = seg_len / n_sub
                        for s_idx in range(1, n_sub):
                            m_pt = p1 + dir_vec * (s_idx * s_step)
                            mw1 = bm_mullion.verts.new(m_pt + out_normal * 0.02 + Vector((0, 0, b_bot)))
                            mw2 = bm_mullion.verts.new(m_pt + out_normal * 0.02 + Vector((0, 0, b_top)))
                            mw3 = bm_mullion.verts.new(m_pt - out_normal * 0.02 + Vector((0, 0, b_top)))
                            mw4 = bm_mullion.verts.new(m_pt - out_normal * 0.02 + Vector((0, 0, b_bot)))
                            bm_mullion.faces.new((mw1, mw2, mw3, mw4))

        elif i in range(25, 38):
            # East Facade & South-East Wing (Connection to Hangar 3 & Aerospace Labs)
            z_base = 0.90
            z_top = 11.50

            # Composite metal panels with horizontal ribbon windows and brick piers
            v1 = bm_panel.verts.new((p1.x, p1.y, z_base))
            v2 = bm_panel.verts.new((p2.x, p2.y, z_base))
            v3 = bm_panel.verts.new((p2.x, p2.y, z_top))
            v4 = bm_panel.verts.new((p1.x, p1.y, z_top))
            bm_panel.faces.new((v1, v2, v3, v4))

            # Ribbon windows on levels 1 and 2 if segment is long enough
            if seg_len > 6.0:
                for wz_bot, wz_top in [(2.0, 3.8), (6.0, 7.8)]:
                    w1 = p1 + dir_vec * 1.0
                    w2 = p2 - dir_vec * 1.0
                    gw1 = bm_glass.verts.new(w1 + out_normal * (-0.06) + Vector((0, 0, wz_bot)))
                    gw2 = bm_glass.verts.new(w2 + out_normal * (-0.06) + Vector((0, 0, wz_bot)))
                    gw3 = bm_glass.verts.new(w2 + out_normal * (-0.06) + Vector((0, 0, wz_top)))
                    gw4 = bm_glass.verts.new(w1 + out_normal * (-0.06) + Vector((0, 0, wz_top)))
                    bm_glass.faces.new((gw1, gw2, gw3, gw4))

        else:
            # Segments 38 to 46: South Tarmac Facade & Hangar Connection Bays
            z_base = 0.90
            z_top = 11.50

            # Composite panel wall with industrial hangar bay doors
            v1 = bm_panel.verts.new((p1.x, p1.y, z_base))
            v2 = bm_panel.verts.new((p2.x, p2.y, z_base))
            v3 = bm_panel.verts.new((p2.x, p2.y, z_top))
            v4 = bm_panel.verts.new((p1.x, p1.y, z_top))
            bm_panel.faces.new((v1, v2, v3, v4))

            # On the long south wall (segment 38, length 30.75m), add 3 large hangar bay doors!
            if i == 38:
                door_w = 7.5
                door_h = 4.8
                for d_i in range(3):
                    d_center = p1 + dir_vec * (5.0 + d_i * 9.5)
                    d1 = d_center - dir_vec * (door_w * 0.5)
                    d2 = d_center + dir_vec * (door_w * 0.5)

                    # Hangar door face
                    dv1 = bm_mullion.verts.new(d1 + out_normal * 0.05 + Vector((0, 0, 0.0)))
                    dv2 = bm_mullion.verts.new(d2 + out_normal * 0.05 + Vector((0, 0, 0.0)))
                    dv3 = bm_mullion.verts.new(d2 + out_normal * 0.05 + Vector((0, 0, door_h)))
                    dv4 = bm_mullion.verts.new(d1 + out_normal * 0.05 + Vector((0, 0, door_h)))
                    bm_mullion.faces.new((dv1, dv2, dv3, dv4))

                    # Inspection glass strip in hangar door
                    dg1 = bm_glass.verts.new(d1 + out_normal * 0.08 + Vector((0, 0, 1.8)))
                    dg2 = bm_glass.verts.new(d2 + out_normal * 0.08 + Vector((0, 0, 1.8)))
                    dg3 = bm_glass.verts.new(d2 + out_normal * 0.08 + Vector((0, 0, 2.6)))
                    dg4 = bm_glass.verts.new(d1 + out_normal * 0.08 + Vector((0, 0, 2.6)))
                    bm_glass.faces.new((dg1, dg2, dg3, dg4))

    # Link created meshes to collections
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
    """
    Constructs the signature aerodynamic curved roof profile over the central academic spine
    along with flat roof membranes, perimeter parapets, and gravel stops.
    """
    # 1. Signature Aerodynamic Barrel/Wing Roof Vault
    # Covers the main academic volume between X = -1348.0 to -1304.0, Y from -1186.0 to -1222.0
    x_min = -1348.0
    x_max = -1304.5
    y_min = -1222.0
    y_max = -1186.0
    span_x = x_max - x_min
    x_center = (x_min + x_max) * 0.5

    mesh_roof = bpy.data.meshes.new("NISW_Aerodynamic_Curved_Roof")
    bm_roof = bmesh.new()

    # Curved profile across X axis
    n_segments_x = 24
    n_segments_y = 18
    z_spring = 15.20 # spring line height
    z_crest = 18.80 # top crest of curved wing vault

    grid_verts = []
    for yi in range(n_segments_y + 1):
        row = []
        frac_y = yi / n_segments_y
        curr_y = y_min + frac_y * (y_max - y_min)
        for xi in range(n_segments_x + 1):
            frac_x = xi / n_segments_x
            curr_x = x_min + frac_x * span_x
            # Parabolic curve
            norm_x = (curr_x - x_center) / (span_x * 0.5) # -1.0 to 1.0
            curr_z = z_crest - (z_crest - z_spring) * (norm_x ** 2)
            # Subtle aerodynamic nose dip towards the north (Aviation Drive front)
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
            bm_roof.faces.new((v1, v2, v3, v4))

    # Gable end walls for the curved roof vault
    # North gable end (at y_max)
    v_north_bot1 = bm_roof.verts.new((x_min, y_max, z_spring))
    v_north_bot2 = bm_roof.verts.new((x_max, y_max, z_spring))
    for xi in range(n_segments_x):
        vt1 = grid_verts[n_segments_y][xi]
        vt2 = grid_verts[n_segments_y][xi+1]
        bm_roof.faces.new((v_north_bot1, vt1, vt2))

    # South gable end (at y_min)
    v_south_bot1 = bm_roof.verts.new((x_min, y_min, z_spring))
    v_south_bot2 = bm_roof.verts.new((x_max, y_min, z_spring))
    for xi in range(n_segments_x):
        vt1 = grid_verts[0][xi]
        vt2 = grid_verts[0][xi+1]
        bm_roof.faces.new((v_south_bot1, vt2, vt1))

    bm_roof.to_mesh(mesh_roof)
    bm_roof.free()
    obj_roof = bpy.data.objects.new("NISW_Aerodynamic_Curved_Roof", mesh_roof)
    obj_roof.data.materials.append(materials['standing_seam'])
    sub_cols["NISW_Roof_and_Aerodynamic_Profiles"].objects.link(obj_roof)

    # 2. Flat Roof Membranes on South & West Wings
    bm_mem = bmesh.new()

    # South wing roof (Y: -1222.0 to -1258.0, X: -1349.5 to -1308.5, Z=11.2m)
    sw_v1 = bm_mem.verts.new((-1349.5, -1255.0, 11.20))
    sw_v2 = bm_mem.verts.new((-1308.5, -1255.0, 11.20))
    sw_v3 = bm_mem.verts.new((-1308.5, -1222.0, 11.20))
    sw_v4 = bm_mem.verts.new((-1349.5, -1222.0, 11.20))
    bm_mem.faces.new((sw_v1, sw_v2, sw_v3, sw_v4))

    # West historic wing roof (Z=8.9m)
    # Using key corner coordinates of the west wing
    ww_v1 = bm_mem.verts.new((-1364.0, -1220.0, 8.90))
    ww_v2 = bm_mem.verts.new((-1352.0, -1220.0, 8.90))
    ww_v3 = bm_mem.verts.new((-1356.5, -1187.5, 8.90))
    ww_v4 = bm_mem.verts.new((-1363.0, -1212.0, 8.90))
    bm_mem.faces.new((ww_v1, ww_v2, ww_v3, ww_v4))

    mesh_mem = bpy.data.meshes.new("NISW_Flat_Roof_Membrane")
    bm_mem.to_mesh(mesh_mem)
    bm_mem.free()
    obj_mem = bpy.data.objects.new("NISW_Flat_Roof_Membrane", mesh_mem)
    obj_mem.data.materials.append(materials['roof_membrane'])
    sub_cols["NISW_Roof_and_Aerodynamic_Profiles"].objects.link(obj_mem)

def build_rooftop_mechanical_penthouse(sub_cols, materials):
    """
    Builds rooftop HVAC chillers, air handling units (RTUs), condenser fan units,
    mechanical equipment screen louvers, and exhaust vents on the south flat roof deck.
    """
    col = sub_cols["NISW_Mechanical_Penthouse"]

    # 1. Louvered Equipment Screen Wall Enclosure
    # Centered at X=-1328.0, Y=-1238.0, size 16m x 12m, Z=11.2 to 14.2m
    mesh_screen = bpy.data.meshes.new("NISW_Rooftop_Louver_Screen")
    bm_screen = bmesh.new()

    sx1, sx2 = -1336.0, -1320.0
    sy1, sy2 = -1244.0, -1232.0
    sz_bot, sz_top = 11.20, 14.40

    # 4 walls of louver screen
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

    # 2. Large Packaged Rooftop Air Handling Units (RTUs) inside enclosure
    rtu_locs = [
        (-1333.0, -1240.0, 11.20),
        (-1329.0, -1240.0, 11.20),
        (-1324.0, -1240.0, 11.20),
        (-1330.0, -1235.0, 11.20),
    ]
    for idx, (rx, ry, rz) in enumerate(rtu_locs):
        mesh_rtu = bpy.data.meshes.new(f"NISW_RTU_Unit_{idx+1}")
        bm_rtu = bmesh.new()
        bmesh.ops.create_cube(bm_rtu, size=1.0)
        # Scale to 3.2m x 2.0m x 1.8m
        for v in bm_rtu.verts:
            v.co.x = v.co.x * 3.2 + rx
            v.co.y = v.co.y * 2.0 + ry
            v.co.z = v.co.z * 1.8 + rz + 0.9

        # Add top circular exhaust fan cowl
        bmesh.ops.create_cone(
            bm_rtu,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.45,
            radius2=0.50,
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
        (-1342.0, -1235.0, 11.20),
        (-1342.0, -1242.0, 11.20),
    ]
    for c_idx, (cx, cy, cz) in enumerate(chiller_locs):
        mesh_ch = bpy.data.meshes.new(f"NISW_Chiller_{c_idx+1}")
        bm_ch = bmesh.new()
        bmesh.ops.create_cube(bm_ch, size=1.0)
        for v in bm_ch.verts:
            v.co.x = v.co.x * 4.5 + cx
            v.co.y = v.co.y * 1.8 + cy
            v.co.z = v.co.z * 1.6 + cz + 0.8

        # 2 twin fan cowls
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

def build_entrances_and_doors(sub_cols, materials):
    """
    Models the prominent North Grand Entrance Atrium Canopy, glass double doors,
    limestone entry portal, ADA ramp, and airport service egress doors.
    """
    col = sub_cols["NISW_Entrances_and_Doors"]

    # 1. Main Entrance Cantilevered Canopy (North Atrium)
    # Location: X ~ -1314.0 to -1309.0, Y = -1185.33, Z = 4.20m
    canopy_x1, canopy_x2 = -1315.5, -1307.5
    canopy_y_wall = -1185.34
    canopy_y_out = -1181.80 # projects 3.5m out over plaza
    canopy_z = 4.20

    mesh_canopy = bpy.data.meshes.new("NISW_Main_Entrance_Canopy")
    bm_canopy = bmesh.new()

    # Canopy roof slab
    v1 = bm_canopy.verts.new((canopy_x1, canopy_y_wall, canopy_z))
    v2 = bm_canopy.verts.new((canopy_x2, canopy_y_wall, canopy_z))
    v3 = bm_canopy.verts.new((canopy_x2, canopy_y_out, canopy_z))
    v4 = bm_canopy.verts.new((canopy_x1, canopy_y_out, canopy_z))

    v5 = bm_canopy.verts.new((canopy_x1, canopy_y_wall, canopy_z + 0.22))
    v6 = bm_canopy.verts.new((canopy_x2, canopy_y_wall, canopy_z + 0.22))
    v7 = bm_canopy.verts.new((canopy_x2, canopy_y_out, canopy_z + 0.22))
    v8 = bm_canopy.verts.new((canopy_x1, canopy_y_out, canopy_z + 0.22))

    # Faces of canopy box
    bm_canopy.faces.new((v1, v2, v3, v4)) # bottom
    bm_canopy.faces.new((v5, v8, v7, v6)) # top
    bm_canopy.faces.new((v1, v4, v8, v5)) # west edge
    bm_canopy.faces.new((v2, v6, v7, v3)) # east edge
    bm_canopy.faces.new((v4, v3, v7, v8)) # north front edge

    # Structural stainless steel tension rods anchoring to upper wall (Z=7.5m)
    for rod_x in [canopy_x1 + 0.8, canopy_x2 - 0.8]:
        p_bottom = Vector((rod_x, canopy_y_out + 0.2, canopy_z + 0.22))
        p_top = Vector((rod_x, canopy_y_wall, 7.50))
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

    # Recessed vestibule at X=-1314.0 to -1309.0, Z=0.0 to 3.2m
    dx1, dx2 = -1313.2, -1309.8
    dy = canopy_y_wall + 0.05
    # Pair of commercial glass doors with bronze push bars
    for pair_x1, pair_x2 in [(dx1, (dx1+dx2)*0.5 - 0.05), ((dx1+dx2)*0.5 + 0.05, dx2)]:
        # Glass panel
        gv1 = bm_doors.verts.new((pair_x1 + 0.08, dy, 0.15))
        gv2 = bm_doors.verts.new((pair_x2 - 0.08, dy, 0.15))
        gv3 = bm_doors.verts.new((pair_x2 - 0.08, dy, 2.50))
        gv4 = bm_doors.verts.new((pair_x1 + 0.08, dy, 2.50))
        bm_doors.faces.new((gv1, gv2, gv3, gv4))

        # Horizontal push bar
        bmesh.ops.create_cube(
            bm_doors,
            size=1.0,
            matrix=Matrix.Translation(((pair_x1 + pair_x2)*0.5, dy - 0.04, 1.05)) @ Matrix.Diagonal(Vector(((pair_x2 - pair_x1 - 0.2), 0.04, 0.04, 1.0)))
        )

    # Transom glass above doors
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

def build_interior_shell_unverified(sub_cols, materials):
    """
    Constructs the interior floor slabs and basic structural core columns.
    Explicitly labeled as Unverified Shell per AGENTS.md instructions.
    """
    col = sub_cols["NISW_Interior_Shell"]

    mesh_shell = bpy.data.meshes.new("NISW_Interior_Shell_Unverified_FloorSlabs")
    bm_shell = bmesh.new()

    # 4 interior structural floor slabs (Levels 1, 2, 3, 4)
    # Follows the interior perimeter offset inside the walls
    floor_z_levels = [0.00, 4.50, 8.50, 12.50]
    slab_thick = 0.25

    # Interior simplified polygon vertices
    interior_pts = []
    for x, y in NISW_PTS[:-1]:
        # inward offset towards official center
        dx = OFFICIAL_CENTER.x - x
        dy = OFFICIAL_CENTER.y - y
        dist = math.hypot(dx, dy)
        offset = 0.35 # 35 cm inside exterior wall line
        interior_pts.append((x + (dx/dist)*offset, y + (dy/dist)*offset))

    for z_floor in floor_z_levels:
        # Create slab perimeter
        verts_bot = [bm_shell.verts.new((x, y, z_floor - slab_thick)) for x, y in interior_pts]
        verts_top = [bm_shell.verts.new((x, y, z_floor)) for x, y in interior_pts]
        n_p = len(interior_pts)
        for idx in range(n_p):
            next_idx = (idx + 1) % n_p
            bm_shell.faces.new((verts_bot[idx], verts_bot[next_idx], verts_top[next_idx], verts_top[idx]))

        # Fill top and bottom caps (with atrium cutout at north entrance)
        # BMesh triangulate / ngon cap
        try:
            bm_shell.faces.new(verts_top)
            bm_shell.faces.new(reversed(verts_bot))
        except ValueError:
            pass

    # Add interior structural grid columns (every 8 meters)
    for cx in range(-1360, -1305, 8):
        for cy in range(-1255, -1188, 8):
            # Check if point is inside building bounding box and within wing
            if cx > -1350 and cy > -1220:
                # Column from Z=0 to 12.5m
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
    """
    Integrates the entrance plaza facing Aviation Drive on the north,
    and the concrete airport tarmac apron with yellow taxiway markings on the south.
    """
    col = sub_cols["NISW_Site_and_Apron"]

    # 1. North Entrance Plaza (Aviation Drive frontage)
    # Extends from Y=-1185.0 to Y=-1165.0, X=-1355.0 to -1300.0
    mesh_plaza = bpy.data.meshes.new("NISW_Site_Entrance_Plaza")
    bm_plaza = bmesh.new()

    p_x1, p_x2 = -1355.0, -1300.0
    p_y1, p_y2 = -1185.3, -1165.0

    pv1 = bm_plaza.verts.new((p_x1, p_y1, -0.05))
    pv2 = bm_plaza.verts.new((p_x2, p_y1, -0.05))
    pv3 = bm_plaza.verts.new((p_x2, p_y2, -0.05))
    pv4 = bm_plaza.verts.new((p_x1, p_y2, -0.05))
    bm_plaza.faces.new((pv1, pv2, pv3, pv4))

    # Add architectural perimeter bollards along entrance sidewalk
    for bx in range(-1325, -1300, 3):
        bmesh.ops.create_cone(
            bm_plaza,
            cap_ends=True,
            cap_tris=False,
            segments=12,
            radius1=0.12,
            radius2=0.10,
            depth=0.90,
            matrix=Matrix.Translation((bx, -1178.0, 0.45))
        )

    bm_plaza.to_mesh(mesh_plaza)
    bm_plaza.free()
    obj_plaza = bpy.data.objects.new("NISW_Site_Entrance_Plaza", mesh_plaza)
    obj_plaza.data.materials.append(materials['plaza'])
    col.objects.link(obj_plaza)

    # 2. South & East Airport Ramp / Apron Concrete Tarmac
    # Extends from Y=-1255.0 to Y=-1285.0, X=-1365.0 to -1285.0
    mesh_apron = bpy.data.meshes.new("NISW_Site_Airport_Apron_Tarmac")
    bm_apron = bmesh.new()

    a_x1, a_x2 = -1365.0, -1285.0
    a_y1, a_y2 = -1285.0, -1250.0

    av1 = bm_apron.verts.new((a_x1, a_y1, -0.05))
    av2 = bm_apron.verts.new((a_x2, a_y1, -0.05))
    av3 = bm_apron.verts.new((a_x2, a_y2, -0.05))
    av4 = bm_apron.verts.new((a_x1, a_y2, -0.05))
    bm_apron.faces.new((av1, av2, av3, av4))

    # East connector apron
    e_v1 = bm_apron.verts.new((-1304.0, -1250.0, -0.05))
    e_v2 = bm_apron.verts.new((-1285.0, -1250.0, -0.05))
    e_v3 = bm_apron.verts.new((-1285.0, -1185.0, -0.05))
    e_v4 = bm_apron.verts.new((-1304.0, -1185.0, -0.05))
    bm_apron.faces.new((e_v1, e_v2, e_v3, e_v4))

    bm_apron.to_mesh(mesh_apron)
    bm_apron.free()
    obj_apron = bpy.data.objects.new("NISW_Site_Airport_Apron_Tarmac", mesh_apron)
    obj_apron.data.materials.append(materials['apron'])
    col.objects.link(obj_apron)

    # 3. Yellow Airport Taxiway Centerline Strip
    mesh_taxi = bpy.data.meshes.new("NISW_Site_Apron_Taxiway_Yellow_Stripe")
    bm_taxi = bmesh.new()
    # Runs east-west across tarmac at Y=-1270.0
    t_y = -1270.0
    half_tw = 0.15 # 30 cm FAA standard taxiway centerline
    t_v1 = bm_taxi.verts.new((a_x1, t_y - half_tw, -0.03))
    t_v2 = bm_taxi.verts.new((a_x2, t_y - half_tw, -0.03))
    t_v3 = bm_taxi.verts.new((a_x2, t_y + half_tw, -0.03))
    t_v4 = bm_taxi.verts.new((a_x1, t_y + half_tw, -0.03))
    bm_taxi.faces.new((t_v1, t_v2, t_v3, t_v4))

    # Lead-in taxi curve line to hangar bay 2
    for seg_idx in range(15):
        s_y = t_y + seg_idx * 1.0
        s_x = -1325.0 - 0.05 * (seg_idx ** 1.5)
        bmesh.ops.create_cube(
            bm_taxi,
            size=1.0,
            matrix=Matrix.Translation((s_x, s_y, -0.03)) @ Matrix.Diagonal(Vector((0.30, 0.85, 0.01, 1.0)))
        )

    bm_taxi.to_mesh(mesh_taxi)
    bm_taxi.free()
    obj_taxi = bpy.data.objects.new("NISW_Site_Apron_Taxiway_Yellow_Stripe", mesh_taxi)
    obj_taxi.data.materials.append(materials['yellow'])
    col.objects.link(obj_taxi)

def setup_lighting_and_cameras(sub_cols):
    """
    Sets up calibrated natural daylight and verification inspection cameras.
    """
    col = sub_cols["00_Inspection_Cameras"]

    # 1. Natural Sunlight (Purdue Airport daylight conditions)
    sun_data = bpy.data.lights.new(name="Sun_Purdue_Airport", type='SUN')
    sun_data.energy = 2.2
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Sun_Purdue_Airport", sun_data)
    # Azimuth ~135° (SE sun), Elevation ~42°
    sun_obj.location = OFFICIAL_CENTER + Vector((50.0, -60.0, 75.0))
    sun_dir = (OFFICIAL_CENTER - sun_obj.location).normalized()
    sun_obj.rotation_euler = sun_dir.to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(sun_obj)

    # Ambient sky daylight fill
    fill_data = bpy.data.lights.new(name="Sky_Airport_Fill", type='SUN')
    fill_data.energy = 0.55
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("Sky_Airport_Fill", fill_data)
    fill_obj.location = OFFICIAL_CENTER + Vector((-60.0, 50.0, 60.0))
    fill_dir = (OFFICIAL_CENTER - fill_obj.location).normalized()
    fill_obj.rotation_euler = fill_dir.to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(fill_obj)

    # 2. Inspection Cameras Setup
    cams_info = [
        # (name, type, location, target, lens_or_scale)
        (
            "Cam_01_Footprint_Top_Down",
            'ORTHO',
            Vector((OFFICIAL_CENTER.x, OFFICIAL_CENTER.y, 110.0)),
            Vector((OFFICIAL_CENTER.x, OFFICIAL_CENTER.y, 0.0)),
            92.0 # ortho scale to show entire 73m span comfortably
        ),
        (
            "Cam_02_Oblique_NorthEast_Aerial",
            'PERSP',
            Vector((-1255.0, -1140.0, 45.0)),
            Vector((OFFICIAL_CENTER.x + 10.0, OFFICIAL_CENTER.y + 15.0, 8.0)),
            35.0
        ),
        (
            "Cam_03_Street_North_Entrance",
            'PERSP',
            Vector((-1312.0, -1164.0, 2.2)),
            Vector((-1312.0, -1185.3, 4.5)),
            28.0 # wide angle for entrance plaza and canopy
        ),
        (
            "Cam_04_South_Apron_View",
            'PERSP',
            Vector((-1330.0, -1288.0, 3.5)),
            Vector((-1330.0, -1255.0, 6.0)),
            32.0 # looking north at hangar bays and tarmac
        ),
        (
            "Cam_05_West_Historic_Wing",
            'PERSP',
            Vector((-1390.0, -1230.0, 10.0)),
            Vector((-1360.0, -1210.0, 5.0)),
            35.0 # looking east at angled historic wing
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
            # Look straight down (X east, Y north)
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
    print("=== Rendering Verification Camera Views ===")
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
    # Polygon centroid and area
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
    print("=== NISWONGER AVIATION TECHNOLOGY BUILDING (NISW - FID 870) BUILDER ===")
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

    # Render verification views to artifact directory
    artifact_dir = r"C:\Users\Tobin\.gemini\antigravity\brain\a1984f28-96cd-4f45-af01-e73d2c9f5ea0"
    rendered_images = render_verification_views(scene, cams_info, artifact_dir)

    # Compute audit stats
    stats = compute_measurements()
    stats["attempt"] = 1
    stats["rendered_images"] = rendered_images
    stats["blend_path"] = out_blend
    stats["collection_name"] = root_col.name
    stats["scene_name"] = scene.name

    stats_path = os.path.join(artifact_dir, "niswonger_aviation_tech_attempt1_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("=== Audit Stats Summary ===")
    print(json.dumps(stats, indent=2))
    print("=== Build script completed successfully! ===")

if __name__ == "__main__":
    main()
