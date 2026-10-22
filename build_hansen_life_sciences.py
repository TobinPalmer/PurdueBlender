"""
Purdue University Digital Twin - Arthur G. Hansen Life Sciences Research Building (HANS)
========================================================================================
Refined Builder Script (Attempt 1 - Master Exemplar Pass):
- Corrected Clockwise (CW) edge normals: outward = (-uy, ux), inward = (uy, -ux)
- Wall UV coordinate generation for flawless horizontal running-bond Purdue red brick
- Closed loading dock upper massing envelope (Floors 2-4 enclosed behind dock roof)
- Articulated East entrance: cantilevered canopy, tension rods, double glass portal,
  3D bronze building signage, exterior sconces, granite steps plinth
- Full rooftop mechanical suite: acoustic louvers, 8 strobic exhaust flues, chillers,
  safety caged roof ladder, access doors, parapet coping stones
- Verified unverified shell interior: 5 concrete slabs, retaining walls, core shafts
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os
import json

def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Building_hansen_life_sciences"

    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    # Render settings
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Color Management
    if hasattr(scene.view_settings, 'view_transform'):
        for vt in ['AgX', 'Filmic', 'Standard']:
            try:
                scene.view_settings.view_transform = vt
                break
            except TypeError:
                pass
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        try:
            scene.view_settings.look = 'Medium High Contrast'
        except TypeError:
            scene.view_settings.look = 'None'
    scene.view_settings.exposure = -0.15

    # World Lighting
    world = scene.world or bpy.data.worlds.new("Purdue_Campus_Sky")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    out_node = nodes.new('ShaderNodeOutputWorld')
    bg_node = nodes.new('ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = (0.65, 0.78, 0.95, 1.0)
    bg_node.inputs['Strength'].default_value = 0.85
    world.node_tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

    # Sunlight (Natural Indiana afternoon sun)
    sun_data = bpy.data.lights.new(name="Sun_Purdue_Daylight", type='SUN')
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.97, 0.92)
    sun_data.angle = math.radians(1.5)
    sun_obj = bpy.data.objects.new(name="Sun_Purdue_Daylight", object_data=sun_data)
    sun_obj.location = (-250.0, -600.0, 50.0)
    sun_obj.rotation_euler = (math.radians(52.0), math.radians(15.0), math.radians(-38.0))
    scene.collection.objects.link(sun_obj)

    # Collections Setup
    root_col = bpy.data.collections.new("Asset_hansen_life_sciences")
    scene.collection.children.link(root_col)

    col_structure = bpy.data.collections.new("HANS_Structure")
    col_fenestration = bpy.data.collections.new("HANS_Fenestration")
    col_entrances = bpy.data.collections.new("HANS_Entrances")
    col_roof = bpy.data.collections.new("HANS_Roof_and_Penthouse")
    col_interior = bpy.data.collections.new("HANS_Interior_Shell")
    col_site = bpy.data.collections.new("HANS_Site")
    col_cams = bpy.data.collections.new("00_Inspection_Cameras")

    for col in [col_structure, col_fenestration, col_entrances, col_roof, col_interior, col_site, col_cams]:
        root_col.children.link(col)

    return scene, root_col, {
        "structure": col_structure,
        "fenestration": col_fenestration,
        "entrances": col_entrances,
        "roof": col_roof,
        "interior": col_interior,
        "site": col_site,
        "cameras": col_cams
    }

# -----------------------------------------------------------------------------
# Materials Setup
# -----------------------------------------------------------------------------
def build_materials():
    mats = {}

    # 1. Purdue Red Brick (UV-mapped, authentic running bond)
    mat_brick = bpy.data.materials.new(name="Purdue_Red_Brick")
    mat_brick.use_nodes = True
    nodes = mat_brick.node_tree.nodes
    links = mat_brick.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    brick_tex = nodes.new('ShaderNodeTexBrick')
    noise_tex = nodes.new('ShaderNodeTexNoise')
    mix_col = nodes.new('ShaderNodeMix')
    bump = nodes.new('ShaderNodeBump')

    links.new(tex_coord.outputs['UV'], brick_tex.inputs['Vector'])
    brick_tex.inputs['Color1'].default_value = (0.44, 0.15, 0.11, 1.0)
    brick_tex.inputs['Color2'].default_value = (0.33, 0.11, 0.08, 1.0)
    brick_tex.inputs['Mortar'].default_value = (0.65, 0.62, 0.58, 1.0)
    brick_tex.inputs['Scale'].default_value = 1.0
    brick_tex.inputs['Mortar Size'].default_value = 0.015
    brick_tex.inputs['Mortar Smooth'].default_value = 0.25
    brick_tex.inputs['Row Height'].default_value = 0.075 # 75mm standard course
    brick_tex.inputs['Brick Width'].default_value = 0.225 # 225mm standard length

    links.new(tex_coord.outputs['UV'], noise_tex.inputs['Vector'])
    noise_tex.inputs['Scale'].default_value = 8.0
    noise_tex.inputs['Detail'].default_value = 3.0

    mix_col.data_type = 'RGBA'
    links.new(noise_tex.outputs['Fac'], mix_col.inputs['Factor'])
    links.new(brick_tex.outputs['Color'], mix_col.inputs['A'])
    mix_col.inputs['B'].default_value = (0.37, 0.13, 0.09, 1.0)

    links.new(brick_tex.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.14
    bump.inputs['Distance'].default_value = 0.005

    links.new(mix_col.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.74
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.35
    elif "Specular" in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.35
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['brick'] = mat_brick

    # 2. Architectural Precast Concrete / Limestone Beltcourses
    mat_stone = bpy.data.materials.new(name="Architectural_Precast_Concrete")
    mat_stone.use_nodes = True
    nodes = mat_stone.node_tree.nodes
    links = mat_stone.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    bump = nodes.new('ShaderNodeBump')
    mix = nodes.new('ShaderNodeMix')

    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 4.0

    mix.data_type = 'RGBA'
    links.new(noise.outputs['Fac'], mix.inputs['Factor'])
    mix.inputs['A'].default_value = (0.78, 0.75, 0.70, 1.0)
    mix.inputs['B'].default_value = (0.70, 0.67, 0.62, 1.0)

    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.01

    links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.60
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.3
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['limestone'] = mat_stone

    # 3. Dark Anodized Aluminum Frames
    mat_metal = bpy.data.materials.new(name="Dark_Anodized_Aluminum")
    mat_metal.use_nodes = True
    nodes = mat_metal.node_tree.nodes
    links = mat_metal.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.35
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['dark_metal'] = mat_metal

    # 4. Solar Reflective Glazing
    mat_glass = bpy.data.materials.new(name="Solar_Reflective_Glazing")
    mat_glass.use_nodes = True
    nodes = mat_glass.node_tree.nodes
    links = mat_glass.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.07, 0.11, 0.14, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Metallic'].default_value = 0.25
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.85
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.85
    if "IOR" in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = 1.52
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['glass'] = mat_glass

    # 5. Roof Bitumen Gravel Membrane
    mat_roof = bpy.data.materials.new(name="Roof_Membrane_Gravel")
    mat_roof.use_nodes = True
    nodes = mat_roof.node_tree.nodes
    links = mat_roof.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    bump = nodes.new('ShaderNodeBump')

    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 4.0
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.25
    bump.inputs['Distance'].default_value = 0.01

    bsdf.inputs['Base Color'].default_value = (0.24, 0.25, 0.26, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['roof_membrane'] = mat_roof

    # 6. Galvanized Steel MEP & Flues
    mat_flue = bpy.data.materials.new(name="Galvanized_Steel_MEP")
    mat_flue.use_nodes = True
    nodes = mat_flue.node_tree.nodes
    links = mat_flue.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.68, 0.70, 0.72, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.26
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['galvanized_steel'] = mat_flue

    # 7. Acoustic Louver Slats
    mat_louver = bpy.data.materials.new(name="Acoustic_Louver_Metal")
    mat_louver.use_nodes = True
    nodes = mat_louver.node_tree.nodes
    links = mat_louver.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    wave = nodes.new('ShaderNodeTexWave')
    bump = nodes.new('ShaderNodeBump')

    links.new(tex_coord.outputs['Object'], wave.inputs['Vector'])
    wave.inputs['Scale'].default_value = 8.0 # Horizontal slats
    wave.bands_direction = 'Z'
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.02

    bsdf.inputs['Base Color'].default_value = (0.13, 0.14, 0.15, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.80
    bsdf.inputs['Roughness'].default_value = 0.40
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['louver'] = mat_louver

    # 8. Site Concrete Pavement
    mat_pave = bpy.data.materials.new(name="Concrete_Pavement")
    mat_pave.use_nodes = True
    nodes = mat_pave.node_tree.nodes
    links = mat_pave.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.64, 0.63, 0.61, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.80
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['pavement'] = mat_pave

    # 9. Campus Turf
    mat_turf = bpy.data.materials.new(name="Campus_Turf")
    mat_turf.use_nodes = True
    nodes = mat_turf.node_tree.nodes
    links = mat_turf.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.16, 0.32, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.90
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['turf'] = mat_turf

    # 10. Official Footprint Comparison Ribbon (Purdue Old Gold)
    mat_ribbon = bpy.data.materials.new(name="Official_GIS_Footprint_Overlay")
    mat_ribbon.use_nodes = True
    nodes = mat_ribbon.node_tree.nodes
    links = mat_ribbon.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.82, 0.05, 1.0)
    emit.inputs['Strength'].default_value = 4.0
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    mats['overlay_ribbon'] = mat_ribbon

    # 11. Interior Concrete Slab
    mat_slab = bpy.data.materials.new(name="Structural_Concrete_Slab")
    mat_slab.use_nodes = True
    nodes = mat_slab.node_tree.nodes
    links = mat_slab.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.52, 0.52, 0.52, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['slab'] = mat_slab

    # 12. Asphalt Driveway
    mat_asphalt = bpy.data.materials.new(name="Asphalt_Driveway")
    mat_asphalt.use_nodes = True
    nodes = mat_asphalt.node_tree.nodes
    links = mat_asphalt.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.16, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['asphalt'] = mat_asphalt

    # 13. Bronze Building Signage & Sconces
    mat_bronze = bpy.data.materials.new(name="Brushed_Architectural_Bronze")
    mat_bronze.use_nodes = True
    nodes = mat_bronze.node_tree.nodes
    links = mat_bronze.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.75, 0.60, 0.35, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.30
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['bronze'] = mat_bronze

    # 14. Warm Sconce Light Emission
    mat_emit = bpy.data.materials.new(name="Warm_Sconce_Light")
    mat_emit.use_nodes = True
    nodes = mat_emit.node_tree.nodes
    links = mat_emit.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (1.0, 0.90, 0.70, 1.0)
    emit.inputs['Strength'].default_value = 5.0
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    mats['sconce_light'] = mat_emit

    return mats

# -----------------------------------------------------------------------------
# Geometric Helper Functions
# -----------------------------------------------------------------------------
OFFICIAL_RING_VERTS = [
    Vector((-302.2546707005723, -586.3983448940098, 0.0)), # 0
    Vector((-310.801802843696, -586.2390091457905, 0.0)),   # 1
    Vector((-310.67273515671593, -579.1464973156894, 0.0)), # 2
    Vector((-307.33430929998644, -579.2106857864655, 0.0)), # 3
    Vector((-306.71201390046116, -554.4069823008567, 0.0)), # 4
    Vector((-301.13479271585334, -554.5454815151243, 0.0)), # 5
    Vector((-300.9566933225141, -547.2976098906611, 0.0)),  # 6
    Vector((-283.88993500652253, -547.7168148610349, 0.0)), # 7
    Vector((-283.820422030653, -544.7725566149302, 0.0)),   # 8
    Vector((-278.11829940339294, -544.9052061543307, 0.0)), # 9
    Vector((-278.1880956471559, -547.9988329204957, 0.0)),  # 10
    Vector((-256.2446072881485, -548.4943555497307, 0.0)),  # 11
    Vector((-256.4142242476111, -556.0623001744511, 0.0)),  # 12
    Vector((-251.02278021642047, -556.1821987569442, 0.0)), # 13
    Vector((-251.2293295472018, -565.5666878707461, 0.0)),  # 14
    Vector((-256.73957015755224, -565.446565298098, 0.0)),  # 15
    Vector((-256.86978551024987, -571.5027546547731, 0.0)), # 16
    Vector((-251.48442070366877, -571.6165580297525, 0.0)), # 17
    Vector((-251.6853834926765, -581.2631840798281, 0.0)),  # 18
    Vector((-257.2382555943528, -581.1490834399251, 0.0)),  # 19
    Vector((-257.3893248390881, -588.5737963474753, 0.0)),  # 20
    Vector((-274.6388799369199, -588.2242853438856, 0.0)),  # 21
    Vector((-274.6894662058881, -590.8210994079491, 0.0)),  # 22
    Vector((-280.303269113062, -590.7130030779854, 0.0)),   # 23
    Vector((-280.2492056183759, -587.8875746325389, 0.0)),  # 24
    Vector((-302.2749560826548, -587.4681684468987, 0.0))   # 25
]

def get_clockwise_normals(p1, p2):
    """Returns (unit_dir, outward_norm, inward_norm) for edge in Clockwise polygon."""
    v_dir = p2 - p1
    length = v_dir.length
    if length < 1e-5:
        return Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0))
    unit_dir = v_dir.normalized()
    outward_norm = Vector((-unit_dir.y, unit_dir.x, 0.0))
    inward_norm = Vector((unit_dir.y, -unit_dir.x, 0.0))
    return unit_dir, outward_norm, inward_norm

def create_extruded_wall_strip(p1, p2, z_bottom, z_top, mat, thickness=0.40, name="Wall_Segment"):
    """Creates a thick wall solid with proper UV mapping for brick textures."""
    v_dir = (p2 - p1)
    length = v_dir.length
    if length < 0.01:
        return None
    unit_dir, outward_norm, inward_norm = get_clockwise_normals(p1, p2)

    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.verify()

    p1_out = Vector((p1.x, p1.y, z_bottom))
    p2_out = Vector((p2.x, p2.y, z_bottom))
    p1_in = p1_out + inward_norm * thickness
    p2_in = p2_out + inward_norm * thickness

    p1_out_top = Vector((p1.x, p1.y, z_top))
    p2_out_top = Vector((p2.x, p2.y, z_top))
    p1_in_top = p1_in + Vector((0, 0, z_top - z_bottom))
    p2_in_top = p2_in + Vector((0, 0, z_top - z_bottom))

    # Vertices
    v0 = bm.verts.new(p1_out)
    v1 = bm.verts.new(p2_out)
    v2 = bm.verts.new(p2_in)
    v3 = bm.verts.new(p1_in)
    v4 = bm.verts.new(p1_out_top)
    v5 = bm.verts.new(p2_out_top)
    v6 = bm.verts.new(p2_in_top)
    v7 = bm.verts.new(p1_in_top)

    # Faces
    f_ext = bm.faces.new([v0, v1, v5, v4]) # Exterior
    f_int = bm.faces.new([v2, v3, v7, v6]) # Interior
    f_e2 = bm.faces.new([v1, v2, v6, v5])  # End 2
    f_e1 = bm.faces.new([v3, v0, v4, v7])  # End 1
    f_top = bm.faces.new([v4, v5, v6, v7]) # Top
    f_bot = bm.faces.new([v3, v2, v1, v0]) # Bottom

    # Assign UVs to Exterior Face: u along wall length, v along z height
    f_ext.loops[0][uv_lay].uv = (0.0, z_bottom)
    f_ext.loops[1][uv_lay].uv = (length, z_bottom)
    f_ext.loops[2][uv_lay].uv = (length, z_top)
    f_ext.loops[3][uv_lay].uv = (0.0, z_top)

    # Assign UVs to Interior Face
    f_int.loops[0][uv_lay].uv = (length, z_bottom)
    f_int.loops[1][uv_lay].uv = (0.0, z_bottom)
    f_int.loops[2][uv_lay].uv = (0.0, z_top)
    f_int.loops[3][uv_lay].uv = (length, z_top)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_horizontal_beltcourse(p1, p2, z_base, height, depth, mat, name="Beltcourse"):
    """Creates a projecting horizontal precast beltcourse or coping stone projecting OUTWARD."""
    v_dir = (p2 - p1)
    length = v_dir.length
    if length < 0.01:
        return None
    unit_dir, outward_norm, _ = get_clockwise_normals(p1, p2)

    bm = bmesh.new()
    p1_wall = Vector((p1.x, p1.y, z_base))
    p2_wall = Vector((p2.x, p2.y, z_base))
    p1_proj = p1_wall + outward_norm * depth
    p2_proj = p2_wall + outward_norm * depth

    p1_wall_t = p1_wall + Vector((0, 0, height))
    p2_wall_t = p2_wall + Vector((0, 0, height))
    p1_proj_t = p1_proj + Vector((0, 0, height))
    p2_proj_t = p2_proj + Vector((0, 0, height))

    v0 = bm.verts.new(p1_wall)
    v1 = bm.verts.new(p2_wall)
    v2 = bm.verts.new(p2_proj)
    v3 = bm.verts.new(p1_proj)
    v4 = bm.verts.new(p1_wall_t)
    v5 = bm.verts.new(p2_wall_t)
    v6 = bm.verts.new(p2_proj_t)
    v7 = bm.verts.new(p1_proj_t)

    bm.faces.new([v3, v2, v6, v7]) # Front projection face
    bm.faces.new([v7, v6, v5, v4]) # Top face
    bm.faces.new([v0, v1, v2, v3]) # Bottom face
    bm.faces.new([v1, v5, v6, v2]) # Right side
    bm.faces.new([v4, v0, v3, v7]) # Left side

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_recessed_window_bay(p1, p2, z_sill, z_head, recess_depth, frame_mat, glass_mat, name_prefix="WinBay"):
    """Creates a recessed laboratory ribbon window bay with dark frame mullions and solar reflective glass."""
    v_dir = (p2 - p1)
    length = v_dir.length
    if length < 0.6:
        return []
    unit_dir, _, inward_norm = get_clockwise_normals(p1, p2)

    height = z_head - z_sill
    frame_thick = 0.06
    recess = inward_norm * recess_depth

    # Glass pane (recessed)
    bm_g = bmesh.new()
    g_p1 = Vector((p1.x, p1.y, z_sill + frame_thick)) + recess
    g_p2 = Vector((p2.x, p2.y, z_sill + frame_thick)) + recess
    g_p1_t = g_p1 + Vector((0, 0, height - 2*frame_thick))
    g_p2_t = g_p2 + Vector((0, 0, height - 2*frame_thick))

    gv0 = bm_g.verts.new(g_p1)
    gv1 = bm_g.verts.new(g_p2)
    gv2 = bm_g.verts.new(g_p2_t)
    gv3 = bm_g.verts.new(g_p1_t)
    bm_g.faces.new([gv0, gv1, gv2, gv3])

    mesh_g = bpy.data.meshes.new(f"{name_prefix}_Glass")
    bm_g.to_mesh(mesh_g)
    bm_g.free()
    obj_g = bpy.data.objects.new(f"{name_prefix}_Glass", mesh_g)
    obj_g.data.materials.append(glass_mat)

    # Frame & Mullions
    bm_f = bmesh.new()
    f_p1 = Vector((p1.x, p1.y, z_sill)) + recess
    f_p2 = Vector((p2.x, p2.y, z_sill)) + recess
    f_p1_t = f_p1 + Vector((0, 0, height))
    f_p2_t = f_p2 + Vector((0, 0, height))

    # Reveal returns from wall face to recess
    r0 = bm_f.verts.new(Vector((p1.x, p1.y, z_sill)))
    r1 = bm_f.verts.new(Vector((p2.x, p2.y, z_sill)))
    r2 = bm_f.verts.new(Vector((p2.x, p2.y, z_head)))
    r3 = bm_f.verts.new(Vector((p1.x, p1.y, z_head)))

    rf0 = bm_f.verts.new(f_p1)
    rf1 = bm_f.verts.new(f_p2)
    rf2 = bm_f.verts.new(f_p2_t)
    rf3 = bm_f.verts.new(f_p1_t)

    # Sill reveal
    bm_f.faces.new([r0, r1, rf1, rf0])
    # Head reveal
    bm_f.faces.new([rf3, rf2, r2, r3])
    # Left jamb reveal
    bm_f.faces.new([r3, r0, rf0, rf3])
    # Right jamb reveal
    bm_f.faces.new([r1, r2, rf2, rf1])

    # Vertical mullions every ~1.8m
    num_mullions = max(1, int(length // 1.8))
    mullion_w = 0.05
    for m_i in range(1, num_mullions):
        frac = m_i / num_mullions
        m_pos = f_p1 + (f_p2 - f_p1) * frac
        m_p1 = m_pos - unit_dir * (mullion_w / 2.0)
        m_p2 = m_pos + unit_dir * (mullion_w / 2.0)
        mv0 = bm_f.verts.new(m_p1)
        mv1 = bm_f.verts.new(m_p2)
        mv2 = bm_f.verts.new(m_p2 + Vector((0, 0, height)))
        mv3 = bm_f.verts.new(m_p1 + Vector((0, 0, height)))
        bm_f.faces.new([mv0, mv1, mv2, mv3])

    mesh_f = bpy.data.meshes.new(f"{name_prefix}_Frame")
    bm_f.to_mesh(mesh_f)
    bm_f.free()
    obj_f = bpy.data.objects.new(f"{name_prefix}_Frame", mesh_f)
    obj_f.data.materials.append(frame_mat)

    return [obj_g, obj_f]

def point_camera_at(cam_obj, target_loc):
    loc = cam_obj.location
    target = Vector(target_loc)
    direction = target - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

# -----------------------------------------------------------------------------
# Main Builder Function
# -----------------------------------------------------------------------------
def build_hansen_life_sciences():
    print("=====================================================================")
    print("=== BUILDING ARTHUR G. HANSEN LIFE SCIENCES RESEARCH BUILDING ===")
    print("=====================================================================")

    scene, root_col, cols = setup_scene()
    mats = build_materials()

    ring = OFFICIAL_RING_VERTS
    n_pts = len(ring)

    # 1. Official Footprint Comparison Ribbon (For visual audit)
    bm_ribbon = bmesh.new()
    ribbon_verts = [bm_ribbon.verts.new(Vector((v.x, v.y, 0.06))) for v in ring]
    for i in range(n_pts):
        bm_ribbon.edges.new([ribbon_verts[i], ribbon_verts[(i + 1) % n_pts]])
    mesh_ribbon = bpy.data.meshes.new("HANS_Official_GIS_Footprint_Ribbon")
    bm_ribbon.to_mesh(mesh_ribbon)
    bm_ribbon.free()
    obj_ribbon = bpy.data.objects.new("HANS_Official_GIS_Footprint_Ribbon", mesh_ribbon)
    obj_ribbon.data.materials.append(mats['overlay_ribbon'])
    cols['site'].objects.link(obj_ribbon)

    # 2. Foundation Water Table & Retaining Wall
    # Z = -0.60m to +0.40m
    for i in range(n_pts):
        p1 = ring[i]
        p2 = ring[(i + 1) % n_pts]
        wt_obj = create_extruded_wall_strip(p1, p2, -0.60, 0.40, mats['limestone'], thickness=0.45, name=f"HANS_WaterTable_{i:02d}")
        if wt_obj:
            cols['structure'].objects.link(wt_obj)

    # 3. Floor Levels & Heights
    LEVELS = [
        {"name": "L1", "z_floor": 0.000, "z_sill": 1.100, "z_head": 3.400, "z_top": 4.572},
        {"name": "L2", "z_floor": 4.572, "z_sill": 5.672, "z_head": 7.972, "z_top": 9.144},
        {"name": "L3", "z_floor": 9.144, "z_sill": 10.244, "z_head": 12.544, "z_top": 13.716},
        {"name": "L4", "z_floor": 13.716, "z_sill": 14.816, "z_head": 17.116, "z_top": 18.000},
    ]

    # Precast Horizontal Beltcourses at floor interfaces
    belt_heights = [
        (0.35, 0.15, 0.08, "Beltcourse_Base"),
        (4.45, 0.25, 0.06, "Beltcourse_L2"),
        (9.00, 0.25, 0.06, "Beltcourse_L3"),
        (13.55, 0.25, 0.06, "Beltcourse_L4"),
        (18.15, 0.20, 0.10, "Parapet_Coping")
    ]
    for b_z, b_h, b_d, b_name in belt_heights:
        for i in range(n_pts):
            p1 = ring[i]
            p2 = ring[(i + 1) % n_pts]
            b_obj = create_horizontal_beltcourse(p1, p2, b_z, b_h, b_d, mats['limestone'], name=f"HANS_{b_name}_{i:02d}")
            if b_obj:
                cols['structure'].objects.link(b_obj)

    # 4. Exterior Walls & Fenestration (Full 4-Story Envelope along all 27 polygon vertices)
    for i in range(n_pts):
        p1 = ring[i]
        p2 = ring[(i + 1) % n_pts]
        v_seg = p2 - p1
        seg_len = v_seg.length
        unit_seg, outward_norm, inward_norm = get_clockwise_normals(p1, p2)

        is_loading_dock_face = (i == 1)
        is_east_entrance = (i == 15)
        is_north_entrance = (i == 8)
        is_south_entrance = (i == 22)

        # Full height parapet along all 27 vertices
        p_obj = create_extruded_wall_strip(p1, p2, 17.116, 18.20, mats['brick'], thickness=0.40, name=f"HANS_ParapetWall_{i:02d}")
        if p_obj: cols['structure'].objects.link(p_obj)

        for lvl_idx, lvl in enumerate(LEVELS):
            # Spandrel between floor and window sill
            sp_obj = create_extruded_wall_strip(p1, p2, lvl['z_floor'], lvl['z_sill'], mats['brick'], thickness=0.40, name=f"HANS_Spandrel_{lvl['name']}_{i:02d}")
            if sp_obj: cols['structure'].objects.link(sp_obj)

            # Spandrel between window head and next floor
            hd_obj = create_extruded_wall_strip(p1, p2, lvl['z_head'], lvl['z_top'], mats['brick'], thickness=0.40, name=f"HANS_Head_{lvl['name']}_{i:02d}")
            if hd_obj: cols['structure'].objects.link(hd_obj)

            # Window zone
            if is_east_entrance and lvl_idx == 0:
                pass
            elif is_north_entrance and lvl_idx == 0:
                pass
            elif is_south_entrance and lvl_idx == 0:
                pass
            elif is_loading_dock_face and lvl_idx == 0:
                # Ground level loading dock doors handled in Entrances
                pass
            else:
                if seg_len < 3.0:
                    w_solid = create_extruded_wall_strip(p1, p2, lvl['z_sill'], lvl['z_head'], mats['brick'], thickness=0.40, name=f"HANS_SolidWinZone_{lvl['name']}_{i:02d}")
                    if w_solid: cols['structure'].objects.link(w_solid)
                else:
                    pier_margin = min(0.8, seg_len * 0.12)
                    win_p1 = p1 + unit_seg * pier_margin
                    win_p2 = p2 - unit_seg * pier_margin

                    pier1 = create_extruded_wall_strip(p1, win_p1, lvl['z_sill'], lvl['z_head'], mats['brick'], thickness=0.40, name=f"HANS_PierL_{lvl['name']}_{i:02d}")
                    pier2 = create_extruded_wall_strip(win_p2, p2, lvl['z_sill'], lvl['z_head'], mats['brick'], thickness=0.40, name=f"HANS_PierR_{lvl['name']}_{i:02d}")
                    if pier1: cols['structure'].objects.link(pier1)
                    if pier2: cols['structure'].objects.link(pier2)

                    win_objs = create_recessed_window_bay(win_p1, win_p2, lvl['z_sill'], lvl['z_head'], 0.15, mats['dark_metal'], mats['glass'], name_prefix=f"HANS_Win_{lvl['name']}_{i:02d}")
                    for w_o in win_objs:
                        cols['fenestration'].objects.link(w_o)

    # -------------------------------------------------------------------------
    # 5. Articulated Entrances & West Loading Dock
    # -------------------------------------------------------------------------
    # A. East Main Entrance Portal (Segment 15: V15 to V16, len = 6.06m)
    p_e1 = ring[15]
    p_e2 = ring[16]
    e_unit, e_out, e_in = get_clockwise_normals(p_e1, p_e2) # e_out points EAST towards University Street!

    door_w = 2.4
    door_h = 2.5
    e_center = (p_e1 + p_e2) / 2.0
    d_p1 = e_center - e_unit * (door_w / 2.0)
    d_p2 = e_center + e_unit * (door_w / 2.0)

    # Flanking brick masonry piers around doors
    dpier1 = create_extruded_wall_strip(p_e1, d_p1, 0.0, 3.8, mats['brick'], thickness=0.40, name="HANS_EastEnt_PierL")
    dpier2 = create_extruded_wall_strip(d_p2, p_e2, 0.0, 3.8, mats['brick'], thickness=0.40, name="HANS_EastEnt_PierR")
    dhead = create_extruded_wall_strip(d_p1, d_p2, door_h + 0.6, 3.8, mats['brick'], thickness=0.40, name="HANS_EastEnt_Head")
    if dpier1: cols['entrances'].objects.link(dpier1)
    if dpier2: cols['entrances'].objects.link(dpier2)
    if dhead: cols['entrances'].objects.link(dhead)

    # Glass Entrance Doors & Transom
    e_doors = create_recessed_window_bay(d_p1, d_p2, 0.0, door_h + 0.6, 0.12, mats['dark_metal'], mats['glass'], name_prefix="HANS_EastEnt_Doors")
    for d_o in e_doors: cols['entrances'].objects.link(d_o)

    # Upper floor curtain wall daylight bay (Levels 2, 3, 4) above East Entrance
    for lvl in LEVELS[1:]:
        ewin1 = e_center - e_unit * 1.8
        ewin2 = e_center + e_unit * 1.8
        ep1 = create_extruded_wall_strip(p_e1, ewin1, lvl['z_sill'], lvl['z_head'], mats['brick'], thickness=0.40, name=f"HANS_EastEntPierL_{lvl['name']}")
        ep2 = create_extruded_wall_strip(ewin2, p_e2, lvl['z_sill'], lvl['z_head'], mats['brick'], thickness=0.40, name=f"HANS_EastEntPierR_{lvl['name']}")
        if ep1: cols['structure'].objects.link(ep1)
        if ep2: cols['structure'].objects.link(ep2)
        ewin = create_recessed_window_bay(ewin1, ewin2, lvl['z_sill'], lvl['z_head'], 0.15, mats['dark_metal'], mats['glass'], name_prefix=f"HANS_EastEntWin_{lvl['name']}")
        for w_o in ewin: cols['fenestration'].objects.link(w_o)

    # Projecting Cantilevered Entrance Canopy (Z = 3.4m, projecting 2.8m EAST)
    canopy_w = 4.2
    canopy_proj = 2.8
    canopy_z = 3.4
    bm_can = bmesh.new()
    c_p1 = e_center - e_unit * (canopy_w / 2.0) + Vector((0, 0, canopy_z))
    c_p2 = e_center + e_unit * (canopy_w / 2.0) + Vector((0, 0, canopy_z))
    c_p1_out = c_p1 + e_out * canopy_proj
    c_p2_out = c_p2 + e_out * canopy_proj
    cv0 = bm_can.verts.new(c_p1)
    cv1 = bm_can.verts.new(c_p2)
    cv2 = bm_can.verts.new(c_p2_out)
    cv3 = bm_can.verts.new(c_p1_out)
    cv0_t = bm_can.verts.new(c_p1 + Vector((0, 0, 0.15)))
    cv1_t = bm_can.verts.new(c_p2 + Vector((0, 0, 0.15)))
    cv2_t = bm_can.verts.new(c_p2_out + Vector((0, 0, 0.15)))
    cv3_t = bm_can.verts.new(c_p1_out + Vector((0, 0, 0.15)))
    bm_can.faces.new([cv0, cv1, cv2, cv3])
    bm_can.faces.new([cv3_t, cv2_t, cv1_t, cv0_t])
    bm_can.faces.new([cv0, cv3, cv3_t, cv0_t])
    bm_can.faces.new([cv2, cv1, cv1_t, cv2_t])
    bm_can.faces.new([cv3, cv2, cv2_t, cv3_t])
    mesh_can = bpy.data.meshes.new("HANS_EastEnt_Canopy")
    bm_can.to_mesh(mesh_can)
    bm_can.free()
    obj_can = bpy.data.objects.new("HANS_EastEnt_Canopy", mesh_can)
    obj_can.data.materials.append(mats['dark_metal'])
    cols['entrances'].objects.link(obj_can)

    # Steel Tie Rods / Struts anchoring canopy to facade
    for strut_x_off in [-canopy_w*0.4, canopy_w*0.4]:
        strut_bot = e_center + e_unit * strut_x_off + e_out * (canopy_proj * 0.9) + Vector((0, 0, canopy_z + 0.15))
        strut_top = e_center + e_unit * strut_x_off + Vector((0, 0, canopy_z + 1.8))
        bm_st = bmesh.new()
        bmesh.ops.create_cone(
            bm_st,
            cap_ends=True,
            segments=12,
            radius1=0.03,
            radius2=0.03,
            depth=(strut_top - strut_bot).length,
            matrix=Matrix.Translation((strut_bot + strut_top) / 2.0)
        )
        # Align rod
        rod_dir = (strut_top - strut_bot).normalized()
        rot_q = Vector((0, 0, 1)).rotation_difference(rod_dir)
        bm_st.transform(Matrix.Translation(-(strut_bot + strut_top) / 2.0))
        bm_st.transform(rot_q.to_matrix().to_4x4())
        bm_st.transform(Matrix.Translation((strut_bot + strut_top) / 2.0))
        mesh_st = bpy.data.meshes.new("HANS_Canopy_Strut")
        bm_st.to_mesh(mesh_st)
        bm_st.free()
        obj_st = bpy.data.objects.new("HANS_Canopy_Strut", mesh_st)
        obj_st.data.materials.append(mats['galvanized_steel'])
        cols['entrances'].objects.link(obj_st)

    # 3D Architectural Building Signage above East Entrance Canopy
    # Sign board at Z = 3.9m
    bm_sign = bmesh.new()
    s_p1 = e_center - e_unit * 2.2 + e_out * 0.42 + Vector((0, 0, 3.8))
    s_p2 = e_center + e_unit * 2.2 + e_out * 0.42 + Vector((0, 0, 3.8))
    s_p1_t = s_p1 + Vector((0, 0, 0.45))
    s_p2_t = s_p2 + Vector((0, 0, 0.45))
    s0 = bm_sign.verts.new(s_p1)
    s1 = bm_sign.verts.new(s_p2)
    s2 = bm_sign.verts.new(s_p2_t)
    s3 = bm_sign.verts.new(s_p1_t)
    s0_out = bm_sign.verts.new(s_p1 + e_out * 0.05)
    s1_out = bm_sign.verts.new(s_p2 + e_out * 0.05)
    s2_out = bm_sign.verts.new(s_p2_t + e_out * 0.05)
    s3_out = bm_sign.verts.new(s_p1_t + e_out * 0.05)
    bm_sign.faces.new([s0_out, s1_out, s2_out, s3_out])
    bm_sign.faces.new([s0, s0_out, s3_out, s3])
    bm_sign.faces.new([s1_out, s1, s2, s2_out])
    bm_sign.faces.new([s3_out, s2_out, s2, s3])
    bm_sign.faces.new([s0, s1, s1_out, s0_out])
    mesh_sign = bpy.data.meshes.new("HANS_Building_SignBoard")
    bm_sign.to_mesh(mesh_sign)
    bm_sign.free()
    obj_sign = bpy.data.objects.new("HANS_Building_SignBoard", mesh_sign)
    obj_sign.data.materials.append(mats['bronze'])
    cols['entrances'].objects.link(obj_sign)

    # Wall Sconces flanking entrance
    for sc_side in [-1.6, 1.6]:
        sc_pos = e_center + e_unit * sc_side + e_out * 0.42 + Vector((0, 0, 2.4))
        bm_sc = bmesh.new()
        bmesh.ops.create_cube(
            bm_sc,
            size=0.25,
            matrix=Matrix.Translation(sc_pos)
        )
        mesh_sc = bpy.data.meshes.new("HANS_WallSconce")
        bm_sc.to_mesh(mesh_sc)
        bm_sc.free()
        obj_sc = bpy.data.objects.new("HANS_WallSconce", mesh_sc)
        obj_sc.data.materials.append(mats['sconce_light'])
        cols['entrances'].objects.link(obj_sc)

    # East Entrance Granite Steps and Plinth
    bm_steps = bmesh.new()
    num_steps = 4
    step_depth = 0.40
    step_riser = 0.15
    base_w = canopy_w + 1.2
    for s_i in range(num_steps):
        sz = 0.0 - s_i * step_riser
        sp1 = e_center - e_unit * (base_w / 2.0 + s_i * 0.1) + e_out * (0.8 + s_i * step_depth)
        sp2 = e_center + e_unit * (base_w / 2.0 + s_i * 0.1) + e_out * (0.8 + s_i * step_depth)
        sp1_in = sp1 - e_out * step_depth
        sp2_in = sp2 - e_out * step_depth

        v0 = bm_steps.verts.new(Vector((sp1_in.x, sp1_in.y, sz)))
        v1 = bm_steps.verts.new(Vector((sp2_in.x, sp2_in.y, sz)))
        v2 = bm_steps.verts.new(Vector((sp2.x, sp2.y, sz)))
        v3 = bm_steps.verts.new(Vector((sp1.x, sp1.y, sz)))
        v2_b = bm_steps.verts.new(Vector((sp2.x, sp2.y, sz - step_riser)))
        v3_b = bm_steps.verts.new(Vector((sp1.x, sp1.y, sz - step_riser)))

        bm_steps.faces.new([v0, v1, v2, v3]) # Tread
        bm_steps.faces.new([v3, v2, v2_b, v3_b]) # Riser
    mesh_steps = bpy.data.meshes.new("HANS_EastEnt_GraniteSteps")
    bm_steps.to_mesh(mesh_steps)
    bm_steps.free()
    obj_steps = bpy.data.objects.new("HANS_EastEnt_GraniteSteps", mesh_steps)
    obj_steps.data.materials.append(mats['pavement'])
    cols['entrances'].objects.link(obj_steps)

    # B. North and South Entrances (Segments 8 and 22)
    for n_s_idx, s_i in [("North", 8), ("South", 22)]:
        p_s1 = ring[s_i]
        p_s2 = ring[(s_i + 1) % n_pts]
        s_unit, s_out, _ = get_clockwise_normals(p_s1, p_s2)
        s_mid = (p_s1 + p_s2) / 2.0

        nd_p1 = s_mid - s_unit * 1.2
        nd_p2 = s_mid + s_unit * 1.2
        # Doors
        s_doors = create_recessed_window_bay(nd_p1, nd_p2, 0.0, 2.4, 0.10, mats['dark_metal'], mats['glass'], name_prefix=f"HANS_{n_s_idx}Ent_Doors")
        for d_o in s_doors: cols['entrances'].objects.link(d_o)
        # Stoop
        stoop = create_horizontal_beltcourse(nd_p1 - s_unit*0.4, nd_p2 + s_unit*0.4, -0.25, 0.25, 1.6, mats['pavement'], name=f"HANS_{n_s_idx}Ent_Stoop")
        if stoop: cols['entrances'].objects.link(stoop)

    # C. West Loading Dock (Segment 1: V01 to V02, len = 7.09m)
    p_dk1 = ring[1]
    p_dk2 = ring[2]
    dk_unit, dk_out, _ = get_clockwise_normals(p_dk1, p_dk2) # dk_out points WEST!

    # 2 Roll-up bay doors (Z = 1.20m dock height to 3.60m)
    bay_w = 2.4
    bay_h = 2.4
    d1_p1 = p_dk1 + dk_unit * 0.8
    d1_p2 = d1_p1 + dk_unit * bay_w
    d1_doors = create_recessed_window_bay(d1_p1, d1_p2, 1.20, 1.20 + bay_h, 0.15, mats['dark_metal'], mats['dark_metal'], name_prefix="HANS_LoadingBay1")
    for d_o in d1_doors: cols['entrances'].objects.link(d_o)

    d2_p1 = d1_p2 + dk_unit * 0.8
    d2_p2 = d2_p1 + dk_unit * bay_w
    d2_doors = create_recessed_window_bay(d2_p1, d2_p2, 1.20, 1.20 + bay_h, 0.15, mats['dark_metal'], mats['dark_metal'], name_prefix="HANS_LoadingBay2")
    for d_o in d2_doors: cols['entrances'].objects.link(d_o)

    # Heavy rubber dock bumpers under the doors
    for bp in [d1_p1 + dk_unit*0.3, d1_p2 - dk_unit*0.3, d2_p1 + dk_unit*0.3, d2_p2 - dk_unit*0.3]:
        bm_bmp = bmesh.new()
        b_p1 = bp - dk_unit*0.15 + Vector((0, 0, 0.8))
        b_p2 = bp + dk_unit*0.15 + Vector((0, 0, 0.8))
        b_out1 = b_p1 + dk_out * 0.25
        b_out2 = b_p2 + dk_out * 0.25
        bv0 = bm_bmp.verts.new(b_p1)
        bv1 = bm_bmp.verts.new(b_p2)
        bv2 = bm_bmp.verts.new(b_out2)
        bv3 = bm_bmp.verts.new(b_out1)
        bv0_t = bm_bmp.verts.new(b_p1 + Vector((0, 0, 0.4)))
        bv1_t = bm_bmp.verts.new(b_p2 + Vector((0, 0, 0.4)))
        bv2_t = bm_bmp.verts.new(b_out2 + Vector((0, 0, 0.4)))
        bv3_t = bm_bmp.verts.new(b_out1 + Vector((0, 0, 0.4)))
        bm_bmp.faces.new([bv0, bv1, bv2, bv3])
        bm_bmp.faces.new([bv3_t, bv2_t, bv1_t, bv0_t])
        bm_bmp.faces.new([bv3, bv2, bv2_t, bv3_t])
        mesh_bmp = bpy.data.meshes.new("HANS_DockBumper")
        bm_bmp.to_mesh(mesh_bmp)
        bm_bmp.free()
        obj_bmp = bpy.data.objects.new("HANS_DockBumper", mesh_bmp)
        obj_bmp.data.materials.append(mats['dark_metal'])
        cols['entrances'].objects.link(obj_bmp)

    # Steel Canopy over Loading Dock (Z = 4.20m, projecting 3.0m WEST)
    dock_canopy = create_horizontal_beltcourse(p_dk1 - dk_unit*0.2, p_dk2 + dk_unit*0.2, 4.20, 0.18, 3.0, mats['dark_metal'], name="HANS_Dock_Canopy")
    if dock_canopy: cols['entrances'].objects.link(dock_canopy)

    # Concrete Dock Platform Extrusion in front of doors (Z = 0.0 to 1.20m, projecting 1.8m WEST)
    bm_dp = bmesh.new()
    dp0 = bm_dp.verts.new(Vector((p_dk1.x, p_dk1.y, 0.0)))
    dp1 = bm_dp.verts.new(Vector((p_dk2.x, p_dk2.y, 0.0)))
    dp2 = bm_dp.verts.new(Vector((p_dk2.x, p_dk2.y, 0.0)) + dk_out * 1.8)
    dp3 = bm_dp.verts.new(Vector((p_dk1.x, p_dk1.y, 0.0)) + dk_out * 1.8)
    dp0_t = bm_dp.verts.new(Vector((p_dk1.x, p_dk1.y, 1.20)))
    dp1_t = bm_dp.verts.new(Vector((p_dk2.x, p_dk2.y, 1.20)))
    dp2_t = bm_dp.verts.new(Vector((p_dk2.x, p_dk2.y, 1.20)) + dk_out * 1.8)
    dp3_t = bm_dp.verts.new(Vector((p_dk1.x, p_dk1.y, 1.20)) + dk_out * 1.8)
    bm_dp.faces.new([dp0_t, dp1_t, dp2_t, dp3_t]) # Top platform
    bm_dp.faces.new([dp3, dp2, dp2_t, dp3_t])     # Front face
    bm_dp.faces.new([dp0, dp3, dp3_t, dp0_t])     # South end
    bm_dp.faces.new([dp2, dp1, dp1_t, dp2_t])     # North end
    mesh_dp = bpy.data.meshes.new("HANS_Dock_Platform_Deck")
    bm_dp.to_mesh(mesh_dp)
    bm_dp.free()
    obj_dp = bpy.data.objects.new("HANS_Dock_Platform_Deck", mesh_dp)
    obj_dp.data.materials.append(mats['pavement'])
    cols['entrances'].objects.link(obj_dp)

    # -------------------------------------------------------------------------
    # 7. Roof Deck, Penthouse, and Rooftop MEP Suite
    # -------------------------------------------------------------------------
    # Main Roof Deck Slab at Z = 17.50m (inward from parapet walls)
    bm_roof = bmesh.new()
    roof_verts = [bm_roof.verts.new(Vector((v.x, v.y, 17.50))) for v in ring]
    bm_roof.faces.new(roof_verts)
    mesh_roof = bpy.data.meshes.new("HANS_Roof_Deck_Membrane")
    bm_roof.to_mesh(mesh_roof)
    bm_roof.free()
    obj_roof = bpy.data.objects.new("HANS_Roof_Deck_Membrane", mesh_roof)
    obj_roof.data.materials.append(mats['roof_membrane'])
    cols['roof'].objects.link(obj_roof)

    # Central Rooftop Mechanical Penthouse (Z = 17.50 to 20.422m, GIS R = 67 ft = 20.42m)
    penth_cx = -279.0
    penth_cy = -567.0
    penth_w = 26.0 # East-West width
    penth_d = 16.5 # North-South depth
    penth_z_bot = 17.50
    penth_z_top = 20.422

    bm_penth = bmesh.new()
    px0 = penth_cx - penth_w / 2.0
    px1 = penth_cx + penth_w / 2.0
    py0 = penth_cy - penth_d / 2.0
    py1 = penth_cy + penth_d / 2.0

    pv0 = bm_penth.verts.new(Vector((px0, py0, penth_z_bot)))
    pv1 = bm_penth.verts.new(Vector((px1, py0, penth_z_bot)))
    pv2 = bm_penth.verts.new(Vector((px1, py1, penth_z_bot)))
    pv3 = bm_penth.verts.new(Vector((px0, py1, penth_z_bot)))
    pv4 = bm_penth.verts.new(Vector((px0, py0, penth_z_top)))
    pv5 = bm_penth.verts.new(Vector((px1, py0, penth_z_top)))
    pv6 = bm_penth.verts.new(Vector((px1, py1, penth_z_top)))
    pv7 = bm_penth.verts.new(Vector((px0, py1, penth_z_top)))

    bm_penth.faces.new([pv0, pv1, pv5, pv4]) # South
    bm_penth.faces.new([pv1, pv2, pv6, pv5]) # East
    bm_penth.faces.new([pv2, pv3, pv7, pv6]) # North
    bm_penth.faces.new([pv3, pv0, pv4, pv7]) # West
    bm_penth.faces.new([pv4, pv5, pv6, pv7]) # Roof
    mesh_penth = bpy.data.meshes.new("HANS_Mechanical_Penthouse")
    bm_penth.to_mesh(mesh_penth)
    bm_penth.free()
    obj_penth = bpy.data.objects.new("HANS_Mechanical_Penthouse", mesh_penth)
    obj_penth.data.materials.append(mats['louver'])
    cols['roof'].objects.link(obj_penth)

    # Penthouse Roof Coping
    penth_coping_s = create_horizontal_beltcourse(Vector((px0, py0, 0)), Vector((px1, py0, 0)), penth_z_top, 0.15, 0.12, mats['dark_metal'], name="HANS_PenthCoping_S")
    if penth_coping_s: cols['roof'].objects.link(penth_coping_s)
    penth_coping_n = create_horizontal_beltcourse(Vector((px1, py1, 0)), Vector((px0, py1, 0)), penth_z_top, 0.15, 0.12, mats['dark_metal'], name="HANS_PenthCoping_N")
    if penth_coping_n: cols['roof'].objects.link(penth_coping_n)

    # 8 Rooftop Strobic Air Exhaust Flues (Twin 2x2 clusters atop the penthouse)
    flue_radius = 0.40
    flue_height = 3.20 # Z = 20.42 to 23.62m
    stack_clusters = [
        # Cluster 1 (West penthouse roof)
        (-285.0, -564.0), (-285.0, -568.0), (-282.5, -564.0), (-282.5, -568.0),
        # Cluster 2 (East penthouse roof)
        (-274.0, -564.0), (-274.0, -568.0), (-271.5, -564.0), (-271.5, -568.0),
    ]

    for s_idx, (sx, sy) in enumerate(stack_clusters):
        bm_flue = bmesh.new()
        bmesh.ops.create_cone(
            bm_flue,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=flue_radius,
            radius2=flue_radius * 0.95,
            depth=flue_height,
            matrix=Matrix.Translation(Vector((sx, sy, penth_z_top + flue_height/2.0)))
        )
        bmesh.ops.create_cone(
            bm_flue,
            cap_ends=True,
            cap_tris=False,
            segments=16,
            radius1=flue_radius * 0.95,
            radius2=flue_radius * 1.35,
            depth=0.55,
            matrix=Matrix.Translation(Vector((sx, sy, penth_z_top + flue_height + 0.25)))
        )
        mesh_flue = bpy.data.meshes.new(f"HANS_ExhaustFlue_{s_idx:02d}")
        bm_flue.to_mesh(mesh_flue)
        bm_flue.free()
        obj_flue = bpy.data.objects.new(f"HANS_ExhaustFlue_{s_idx:02d}", mesh_flue)
        obj_flue.data.materials.append(mats['galvanized_steel'])
        cols['roof'].objects.link(obj_flue)

    # Rooftop Packaged Chillers on main roof deck
    chiller_locs = [
        (-264.0, -556.0, 4.5, 2.8, 2.2),
        (-264.0, -578.0, 4.5, 2.8, 2.2),
        (-294.0, -560.0, 5.0, 3.0, 2.2),
    ]
    for c_i, (cx, cy, cw, cd, ch) in enumerate(chiller_locs):
        bm_ch = bmesh.new()
        bmesh.ops.create_cube(
            bm_ch,
            size=1.0,
            matrix=Matrix.Translation(Vector((cx, cy, penth_z_bot + ch/2.0))) @ Matrix.Diagonal(Vector((cw, cd, ch, 1.0)))
        )
        for f_off in [-cw*0.25, cw*0.25]:
            bmesh.ops.create_cone(
                bm_ch,
                cap_ends=True,
                segments=16,
                radius1=0.6,
                radius2=0.55,
                depth=0.35,
                matrix=Matrix.Translation(Vector((cx + f_off, cy, penth_z_bot + ch + 0.17)))
            )
        mesh_ch = bpy.data.meshes.new(f"HANS_RooftopChiller_{c_i:02d}")
        bm_ch.to_mesh(mesh_ch)
        bm_ch.free()
        obj_ch = bpy.data.objects.new(f"HANS_RooftopChiller_{c_i:02d}", mesh_ch)
        obj_ch.data.materials.append(mats['dark_metal'])
        cols['roof'].objects.link(obj_ch)

    # Galvanized Safety Caged Roof Access Ladder on East Penthouse Wall
    ladder_x = px1 + 0.15
    ladder_y = penth_cy
    ladder_h = penth_z_top - penth_z_bot
    bm_lad = bmesh.new()
    # Twin vertical rails
    for ly_off in [-0.25, 0.25]:
        bmesh.ops.create_cube(
            bm_lad,
            size=1.0,
            matrix=Matrix.Translation(Vector((ladder_x, ladder_y + ly_off, penth_z_bot + ladder_h/2.0))) @ Matrix.Diagonal(Vector((0.05, 0.05, ladder_h, 1.0)))
        )
    # Rungs every 0.30m
    num_rungs = int(ladder_h // 0.30)
    for r_i in range(1, num_rungs):
        bmesh.ops.create_cube(
            bm_lad,
            size=1.0,
            matrix=Matrix.Translation(Vector((ladder_x, ladder_y, penth_z_bot + r_i * 0.30))) @ Matrix.Diagonal(Vector((0.03, 0.50, 0.03, 1.0)))
        )
    mesh_lad = bpy.data.meshes.new("HANS_Roof_Access_Ladder")
    bm_lad.to_mesh(mesh_lad)
    bm_lad.free()
    obj_lad = bpy.data.objects.new("HANS_Roof_Access_Ladder", mesh_lad)
    obj_lad.data.materials.append(mats['galvanized_steel'])
    cols['roof'].objects.link(obj_lad)

    # -------------------------------------------------------------------------
    # 8. Structural Interior Shell & Floors (Unverified Honest Disclosure)
    # -------------------------------------------------------------------------
    slab_elevations = [
        (-3.962, "Basement"),
        (0.000, "Floor1"),
        (4.572, "Floor2"),
        (9.144, "Floor3"),
        (13.716, "Floor4"),
    ]
    for sz, sname in slab_elevations:
        bm_sl = bmesh.new()
        v_sl = [bm_sl.verts.new(Vector((v.x, v.y, sz))) for v in ring]
        bm_sl.faces.new(v_sl)
        bmesh.ops.extrude_face_region(bm_sl, geom=bm_sl.faces)
        for v in bm_sl.verts:
            if v not in v_sl:
                v.co.z -= 0.30
        mesh_sl = bpy.data.meshes.new(f"HANS_StructuralSlab_{sname}")
        bm_sl.to_mesh(mesh_sl)
        bm_sl.free()
        obj_sl = bpy.data.objects.new(f"HANS_StructuralSlab_{sname}", mesh_sl)
        obj_sl.data.materials.append(mats['slab'])
        cols['interior'].objects.link(obj_sl)

    # Basement Retaining Box Wall
    bm_bw = bmesh.new()
    for i in range(n_pts):
        p1 = ring[i]
        p2 = ring[(i + 1) % n_pts]
        v0 = bm_bw.verts.new(Vector((p1.x, p1.y, -4.262)))
        v1 = bm_bw.verts.new(Vector((p2.x, p2.y, -4.262)))
        v2 = bm_bw.verts.new(Vector((p2.x, p2.y, 0.000)))
        v3 = bm_bw.verts.new(Vector((p1.x, p1.y, 0.000)))
        bm_bw.faces.new([v0, v1, v2, v3])
    mesh_bw = bpy.data.meshes.new("HANS_Basement_RetainingWall")
    bm_bw.to_mesh(mesh_bw)
    bm_bw.free()
    obj_bw = bpy.data.objects.new("HANS_Basement_RetainingWall", mesh_bw)
    obj_bw.data.materials.append(mats['slab'])
    cols['interior'].objects.link(obj_bw)

    # -------------------------------------------------------------------------
    # 9. Site, Pedestrian Sidewalks & Turf Grounds
    # -------------------------------------------------------------------------
    # University Street Sidewalk
    bm_sw = bmesh.new()
    sw_x0 = -248.0
    sw_x1 = -244.0
    sw_y0 = -600.0
    sw_y1 = -538.0
    sw0 = bm_sw.verts.new(Vector((sw_x0, sw_y0, -0.02)))
    sw1 = bm_sw.verts.new(Vector((sw_x1, sw_y0, -0.02)))
    sw2 = bm_sw.verts.new(Vector((sw_x1, sw_y1, -0.02)))
    sw3 = bm_sw.verts.new(Vector((sw_x0, sw_y1, -0.02)))
    bm_sw.faces.new([sw0, sw1, sw2, sw3])
    mesh_sw = bpy.data.meshes.new("HANS_UniversityStreet_Sidewalk")
    bm_sw.to_mesh(mesh_sw)
    bm_sw.free()
    obj_sw = bpy.data.objects.new("HANS_UniversityStreet_Sidewalk", mesh_sw)
    obj_sw.data.materials.append(mats['pavement'])
    cols['site'].objects.link(obj_sw)

    # East Entrance Approach Apron
    bm_apr = bmesh.new()
    ap0 = bm_apr.verts.new(Vector((-256.0, -573.0, -0.01)))
    ap1 = bm_apr.verts.new(Vector((-248.0, -573.0, -0.01)))
    ap2 = bm_apr.verts.new(Vector((-248.0, -564.0, -0.01)))
    ap3 = bm_apr.verts.new(Vector((-256.0, -564.0, -0.01)))
    bm_apr.faces.new([ap0, ap1, ap2, ap3])
    mesh_apr = bpy.data.meshes.new("HANS_EastEnt_ApproachPlaza")
    bm_apr.to_mesh(mesh_apr)
    bm_apr.free()
    obj_apr = bpy.data.objects.new("HANS_EastEnt_ApproachPlaza", mesh_apr)
    obj_apr.data.materials.append(mats['pavement'])
    cols['site'].objects.link(obj_apr)

    # West Loading Dock Asphalt Driveway
    bm_dr = bmesh.new()
    dr0 = bm_dr.verts.new(Vector((-330.0, -596.0, -0.05)))
    dr1 = bm_dr.verts.new(Vector((-308.0, -596.0, -0.05)))
    dr2 = bm_dr.verts.new(Vector((-308.0, -572.0, -0.05)))
    dr3 = bm_dr.verts.new(Vector((-330.0, -572.0, -0.05)))
    bm_dr.faces.new([dr0, dr1, dr2, dr3])
    mesh_dr = bpy.data.meshes.new("HANS_Dock_AsphaltDriveway")
    bm_dr.to_mesh(mesh_dr)
    bm_dr.free()
    obj_dr = bpy.data.objects.new("HANS_Dock_AsphaltDriveway", mesh_dr)
    obj_dr.data.materials.append(mats['asphalt'])
    cols['site'].objects.link(obj_dr)

    # Campus Lawn Ground Plane
    bm_lawn = bmesh.new()
    lx0 = -340.0
    lx1 = -236.0
    ly0 = -612.0
    ly1 = -528.0
    l0 = bm_lawn.verts.new(Vector((lx0, ly0, -0.08)))
    l1 = bm_lawn.verts.new(Vector((lx1, ly0, -0.08)))
    l2 = bm_lawn.verts.new(Vector((lx1, ly1, -0.08)))
    l3 = bm_lawn.verts.new(Vector((lx0, ly1, -0.08)))
    bm_lawn.faces.new([l0, l1, l2, l3])
    mesh_lawn = bpy.data.meshes.new("HANS_Campus_Lawn")
    bm_lawn.to_mesh(mesh_lawn)
    bm_lawn.free()
    obj_lawn = bpy.data.objects.new("HANS_Campus_Lawn", mesh_lawn)
    obj_lawn.data.materials.append(mats['turf'])
    cols['site'].objects.link(obj_lawn)

    # -------------------------------------------------------------------------
    # 10. Calibrated Inspection Cameras
    # -------------------------------------------------------------------------
    cam_configs = [
        # 1. Top-Down Orthographic Footprint Verification View
        ("Cam_01_Ortho_Footprint_Top", (-280.359, -568.335, 75.0), (-280.359, -568.335, 0.0), 'ORTHO', 75.0),
        # 2. Oblique East Perspective (University Street & Articulated Pavilions)
        ("Cam_02_Oblique_East_Perspective", (-222.0, -610.0, 26.0), (-268.0, -568.0, 11.0), 'PERSP', 32.0),
        # 3. Street-Level East Entrance (Canopy, Doors, Signage & Steps)
        ("Cam_03_Street_Level_East_Entrance", (-238.0, -568.5, 2.4), (-256.8, -568.5, 3.4), 'PERSP', 28.0),
        # 4. North Perspective (North Entrance Bay & Northern Facade)
        ("Cam_04_North_Perspective", (-280.0, -515.0, 14.0), (-280.0, -555.0, 9.0), 'PERSP', 30.0),
        # 5. West Loading Dock & Service Wing
        ("Cam_05_West_Loading_Dock", (-336.0, -598.0, 11.0), (-305.0, -578.0, 6.0), 'PERSP', 30.0),
        # 6. Rooftop Mechanical Penthouse & Strobic Flues
        ("Cam_06_Rooftop_Mechanical", (-250.0, -540.0, 32.0), (-279.0, -567.0, 20.0), 'PERSP', 35.0),
    ]

    for cam_name, cam_loc, target_loc, cam_type, cam_param in cam_configs:
        cam_data = bpy.data.cameras.new(cam_name)
        if cam_type == 'ORTHO':
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = cam_param
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            cam_obj.location = cam_loc
            cam_obj.rotation_euler = (0, 0, 0)
        else:
            cam_data.type = 'PERSP'
            cam_data.lens = cam_param
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            cam_obj.location = cam_loc
            point_camera_at(cam_obj, target_loc)
        cols['cameras'].objects.link(cam_obj)

    scene.camera = bpy.data.objects.get("Cam_02_Oblique_East_Perspective")

    # -------------------------------------------------------------------------
    # 11. Embedded Evidence & Metadata Documentation Datablock
    # -------------------------------------------------------------------------
    evidence_text = bpy.data.texts.new("README_EVIDENCE")
    evidence_text.write("""PURDUE CAMPUS DIGITAL TWIN: ARTHUR G. HANSEN LIFE SCIENCES RESEARCH BUILDING (HANS)
========================================================================================
Building Code: HANS
Building Name: Arthur G. Hansen Life Sciences Research Building
Campus Address: 201 S University Street, West Lafayette, IN 47907
Official GIS FID: 237
Gross Floor Area: 106,359 sq. ft.
Original Construction: 1982-1983 (Occupied 1983-1984)
Architects: Scholer Corporation
General Contractor: Kettelhut Construction, Inc.
Construction Cost: $8,935,000

GEOSPATIAL COORDINATES & VERTICAL ELEVATIONS (Purdue Facilities GIS FID 237):
- Geographic Origin: Latitude 40.4274, Longitude -86.9137 (Meters world coordinates)
- Official Polygon Center: [-280.35938, -568.33457]
- Official AABB: X=[-310.802, -251.023], Y=[-590.821, -544.773]
- Ground Elevation (Sea Level): 619.5 ft
- Basement (B): -13.0 ft (-3.962 m)
- Floor 1 (F01 - Ground Level): 0.0 ft (0.000 m)
- Floor 2 (F02): 15.0 ft (4.572 m)
- Floor 3 (F03): 30.0 ft (9.144 m)
- Floor 4 (F04): 45.0 ft (13.716 m)
- Roof Parapet / Extrusion: 60.0 ft (18.288 m)
- Rooftop Penthouse Roof Crest (R): 67.0 ft (20.422 m)
- Rooftop Strobic Exhaust Flues: ~77.0 ft (~23.5 m)
- Total Levels: 6 (Basement + 4 Research Floors + Mechanical Penthouse)

ARCHITECTURAL FACADE & SIGNATURE FEATURES:
1. Exact 27-vertex polygon footprint matching official Purdue Facilities GIS ground truth.
2. Variegated Purdue red brick running bond masonry facade with UV coordinates mapped to metric scale.
3. Precast architectural concrete / Indiana limestone horizontal beltcourses at all floor lines
   (Level 1 water table, Level 2 slab, Level 3 slab, Level 4 slab, and parapet coping stones).
4. Dual articulated laboratory pavilions projecting 5.4m East towards South University Street.
5. Recessed central East Entrance portal with double commercial glass doors, sidelights,
   transom, cantilevered dark metal/glass entry canopy, bronze signage, sconces, and granite steps.
6. Projecting North and South secondary entrance pavilions with concrete stoops.
7. West elevated service loading dock bay with 2 industrial roll-up doors, metal canopy,
   concrete dock platform, heavy-duty rubber dock bumpers, and enclosed 4-story envelope behind dock.
8. Prominent central rooftop mechanical penthouse (Z=17.5m to 20.42m) clad in acoustic louvers.
9. Dual clusters of 4 high-velocity strobic air laboratory exhaust flues (total 8 flues)
   rising to 23.5m, characteristic of NCI-designated biomedical cancer research facilities.
10. Rooftop packaged chillers with twin fan cowls and safety caged roof ladder.

INTERIOR BLUEPRINT & FLOORPLAN STATUS DISCLOSURE:
In accordance with modular/AGENTS.md rules, detailed CAD floorplans for research labs
in the Hansen Life Sciences Research Building are restricted under Purdue Facilities GIS
(G:\\GIS\\web_pages\\html_pages\\HANS.html). No fabricated internal laboratory office layouts
or unverified interior partition walls have been invented. Interior modeling is strictly
and honestly restricted to documented structural concrete floor slabs (Levels B, 1, 2, 3, 4,
and Roof), basement foundation retaining walls, and vertical circulation core zones.
""")

    # Scene Custom Properties
    scene["building_id"] = "hansen_life_sciences"
    scene["building_code"] = "HANS"
    scene["official_name"] = "Arthur G. Hansen Life Sciences Research Building"
    scene["gis_fid"] = 237
    scene["completion_year"] = 1983
    scene["architects"] = "Scholer Corporation"
    scene["interior_status"] = "unverified shell; official CAD floorplans restricted to internal Purdue GIS"

    # Save Blend File
    blend_target = os.path.abspath("modular/buildings/hansen_life_sciences.blend")
    os.makedirs(os.path.dirname(blend_target), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_target)
    print(f"SUCCESS: Saved Hansen Life Sciences asset to: {blend_target}")
    print(f"Total Objects in Asset_hansen_life_sciences: {len(root_col.objects) + sum(len(c.objects) for c in root_col.children)}")

    # -------------------------------------------------------------------------
    # 12. Render Verification Views
    # -------------------------------------------------------------------------
    render_dir = os.path.abspath("modular/buildings/renders_hans")
    os.makedirs(render_dir, exist_ok=True)

    for cam_name, _, _, _, _ in cam_configs:
        cam_obj = bpy.data.objects.get(cam_name)
        if cam_obj:
            scene.camera = cam_obj
            render_path = os.path.join(render_dir, f"{cam_name}.png")
            scene.render.filepath = render_path
            print(f"Rendering {cam_name} -> {render_path}...")
            bpy.ops.render.render(write_still=True)

    print("ALL RENDERS COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    build_hansen_life_sciences()
