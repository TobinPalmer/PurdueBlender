"""
Purdue Campus Digital Twin - Building Modeler Agent
Asset Builder for John W. Hicks Undergraduate Library (HIKS)
Building ID: hicks_library
Building Code: HIKS
Official GIS FID: 197

Generates modular/buildings/hicks_library.blend containing Asset_hicks_library
in campus world coordinates (meters).
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

# -----------------------------------------------------------------------------
# Configuration and Constants
# -----------------------------------------------------------------------------
BUILDING_ID = "hicks_library"
BUILDING_CODE = "HIKS"
OFFICIAL_NAME = "John W. Hicks Undergraduate Library"
ADDRESS = "504 Mitch Daniels Blvd, West Lafayette, IN 47907"
GIS_FID = 197
NUM_LEVELS = 3
ARCHITECT = "Scholer Corporation"
COMPLETION_YEAR = 1982
DEDICATION_YEAR = 1990

# Elevation levels from official Purdue GIS FID 197
# SB: 0, B: -31 ft (-9.449 m), G: -17.4 ft (-5.304 m), F01: 0 ft (0.000 m),
# Extrusion: 8 ft (2.438 m), R: 24 ft (7.315 m)
ELEV_GRADE = 0.000
ELEV_ROOF_DECK = 2.438       # 8.0 ft
ELEV_PARAPET = 3.048         # 10.0 ft
ELEV_SKYLIGHT_PEAK = 7.315   # 24.0 ft (GIS R: 24)
ELEV_GROUND_FLOOR = -5.304   # -17.4 ft (GIS G: -17.4)
ELEV_BASEMENT_FLOOR = -9.449 # -31.0 ft (GIS B: -31)
ELEV_FOUNDATION_BOTTOM = -9.950

# Official 21-vertex polygon from target_buildings_gis.json (FID 197)
GIS_POLYGON_2D = [
    (79.507, -308.478),
    (79.648, -311.152),
    (96.698, -311.038),
    (96.801, -308.481),
    (103.932, -308.467),
    (103.940, -312.387),
    (101.085, -312.394),
    (101.139, -319.575),
    (103.874, -319.559),
    (103.918, -326.990),
    (91.848, -327.058),
    (91.646, -324.431),
    (84.551, -324.478),
    (84.759, -327.258),
    (73.022, -327.327),
    (72.976, -319.746),
    (75.586, -319.730),
    (75.545, -312.649),
    (72.740, -312.677),
    (72.699, -308.547),
    (79.507, -308.478)
]

UNIQUE_VERTS_2D = GIS_POLYGON_2D[:-1]

BLEND_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_BLEND = os.path.join(BLEND_DIR, "hicks_library.blend")
EVIDENCE_DIR = os.path.join(BLEND_DIR, "hicks_library_evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Clean Scene Setup
# -----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    scene.name = f"Building_{BUILDING_ID}"
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'
    
    # Custom properties
    scene["building_id"] = BUILDING_ID
    scene["building_code"] = BUILDING_CODE
    scene["official_name"] = OFFICIAL_NAME
    scene["address"] = ADDRESS
    scene["gis_fid"] = GIS_FID
    scene["levels"] = NUM_LEVELS
    scene["elevation_grade_m"] = ELEV_GRADE
    scene["elevation_roof_extrusion_m"] = ELEV_ROOF_DECK
    scene["elevation_skylight_peak_m"] = ELEV_SKYLIGHT_PEAK
    scene["elevation_ground_floor_m"] = ELEV_GROUND_FLOOR
    scene["elevation_basement_floor_m"] = ELEV_BASEMENT_FLOOR
    scene["architect"] = ARCHITECT
    scene["completion_year"] = COMPLETION_YEAR
    scene["dedication_year"] = DEDICATION_YEAR
    scene["interior_status"] = (
        "unverified; official structural shell, slabs, columns, and atrium levels "
        "modeled from GIS FID 197; private room partitions omitted per privacy policy"
    )
    
    # Master collection
    master_col = bpy.data.collections.new(f"Asset_{BUILDING_ID}")
    scene.collection.children.link(master_col)
    
    # Sub-collections for clean organization
    sub_cols = {}
    names = [
        "01_AboveGround_Masonry_Shell",
        "02_Entrance_Pavilion_Vestibule",
        "03_Roof_Deck_and_Pyramids",
        "04_Subterranean_Structure",
        "05_Atrium_and_SpiralStairs",
        "06_Plaza_Lightwells_Site",
        "07_Inspection_Cameras"
    ]
    for n in names:
        sc = bpy.data.collections.new(n)
        master_col.children.link(sc)
        sub_cols[n] = sc
        
    return scene, master_col, sub_cols

# -----------------------------------------------------------------------------
# Shader / Material Factory
# -----------------------------------------------------------------------------
def create_pbr_material(name, base_color, roughness=0.5, metallic=0.0, transmission=0.0, ior=1.45, is_glass=False):
    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if is_glass or transmission > 0:
        bsdf.inputs['Transmission Weight'].default_value = transmission
        bsdf.inputs['IOR'].default_value = ior
        mat.blend_method = 'HASHED' if hasattr(mat, 'blend_method') else 'BLEND'
        if hasattr(mat, 'shadow_method'):
            mat.shadow_method = 'HASHED'
            
    return mat

def create_brick_material(name="Mat_HIKS_Purdue_Red_Brick"):
    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    brick = nodes.new(type='ShaderNodeTexBrick')
    brick.location = (-150, 100)
    brick.inputs['Color1'].default_value = (0.50, 0.16, 0.11, 1.0) # Purdue red brick
    brick.inputs['Color2'].default_value = (0.42, 0.13, 0.09, 1.0) # Darker brick variation
    brick.inputs['Mortar'].default_value = (0.75, 0.72, 0.68, 1.0) # Mortar
    brick.inputs['Mortar Size'].default_value = 0.015
    brick.inputs['Brick Width'].default_value = 0.22
    brick.inputs['Row Height'].default_value = 0.075
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-150, -200)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 4.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.18
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    
    links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.75
    
    return mat

def create_limestone_material(name="Mat_HIKS_Indiana_Limestone"):
    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (500, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-500, 0)
    
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-50, 0)
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = (0.78, 0.75, 0.69, 1.0) # Warm limestone
    color_ramp.color_ramp.elements[1].position = 0.7
    color_ramp.color_ramp.elements[1].color = (0.86, 0.83, 0.77, 1.0) # Light cream
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (0, -200)
    bump.inputs['Strength'].default_value = 0.08
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.65
    
    return mat

def setup_materials():
    materials = {
        "brick": create_brick_material(),
        "limestone": create_limestone_material(),
        "bronze": create_pbr_material("Mat_HIKS_Dark_Bronze_Anodized", (0.16, 0.13, 0.11, 1.0), roughness=0.32, metallic=0.88),
        "glass": create_pbr_material("Mat_HIKS_Solar_Glazing", (0.82, 0.90, 0.94, 1.0), roughness=0.04, transmission=0.92, ior=1.52, is_glass=True),
        "roof_gravel": create_pbr_material("Mat_HIKS_Roof_Gravel_Ballast", (0.34, 0.33, 0.32, 1.0), roughness=0.90),
        "concrete": create_pbr_material("Mat_HIKS_Subterranean_Concrete", (0.64, 0.63, 0.60, 1.0), roughness=0.82),
        "terrazzo": create_pbr_material("Mat_HIKS_Interior_Terrazzo", (0.73, 0.71, 0.68, 1.0), roughness=0.28),
        "steel": create_pbr_material("Mat_HIKS_Stainless_Steel", (0.80, 0.80, 0.82, 1.0), roughness=0.22, metallic=0.95),
        "plaza": create_pbr_material("Mat_HIKS_Plaza_Paver_Concrete", (0.70, 0.68, 0.65, 1.0), roughness=0.85),
        "lawn": create_pbr_material("Mat_HIKS_Site_Lawn", (0.20, 0.36, 0.12, 1.0), roughness=0.92),
        "glow": create_pbr_material("Mat_HIKS_Warm_Illumination", (1.0, 0.92, 0.75, 1.0), roughness=0.3)
    }
    glow_nodes = materials["glow"].node_tree.nodes
    bsdf = glow_nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.88, 0.70, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 3.0
    return materials

# -----------------------------------------------------------------------------
# Geometry Helper Functions
# -----------------------------------------------------------------------------
def create_mesh_object(name, bm, collection, material=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def add_box_beam(bm, p1, p2, width=0.10, depth=0.10):
    """Adds a 3D rectangular box beam between p1 and p2."""
    v_axis = (p2 - p1)
    length = v_axis.length
    if length < 1e-5:
        return
    v_norm = v_axis.normalized()
    
    if abs(v_norm.z) < 0.9:
        up = Vector((0.0, 0.0, 1.0))
    else:
        up = Vector((1.0, 0.0, 0.0))
    side = v_norm.cross(up).normalized()
    up = side.cross(v_norm).normalized()
    
    half_s = side * (width / 2.0)
    half_u = up * (depth / 2.0)
    
    c1 = [
        p1 - half_s - half_u,
        p1 + half_s - half_u,
        p1 + half_s + half_u,
        p1 - half_s + half_u
    ]
    c2 = [
        p2 - half_s - half_u,
        p2 + half_s - half_u,
        p2 + half_s + half_u,
        p2 - half_s + half_u
    ]
    
    v1 = [bm.verts.new(c) for c in c1]
    v2 = [bm.verts.new(c) for c in c2]
    
    for i in range(4):
        bm.faces.new((v1[i], v1[(i+1)%4], v2[(i+1)%4], v2[i]))
    bm.faces.new((v1[3], v1[2], v1[1], v1[0]))
    bm.faces.new((v2[0], v2[1], v2[2], v2[3]))

# -----------------------------------------------------------------------------
# Component 1: Exterior Masonry Shell with Seamless UV Unwrapping
# -----------------------------------------------------------------------------
def build_exterior_masonry_shell(col, materials):
    """
    Builds the exterior walls following the exact 21 GIS vertices.
    Vertices match GIS polygon exactly at the exterior face.
    Applies custom UV mapping so the brick texture maps cleanly.
    """
    bm_brick = bmesh.new()
    bm_lime = bmesh.new()
    
    uv_brick = bm_brick.loops.layers.uv.verify()
    uv_lime = bm_lime.loops.layers.uv.verify()
    
    pts = UNIQUE_VERTS_2D
    n = len(pts)
    
    signed_area = 0.0
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        signed_area += (p1[0] * p2[1] - p2[0] * p1[1])
    is_ccw = (signed_area > 0)
    
    wall_thickness = 0.35
    inward_dirs = []
    for i in range(n):
        p_prev = pts[(i - 1 + n) % n]
        p_curr = pts[i]
        p_next = pts[(i + 1) % n]
        
        v1 = Vector((p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])).normalized()
        v2 = Vector((p_next[0] - p_curr[0], p_next[1] - p_curr[1])).normalized()
        
        n1 = Vector((-v1.y, v1.x)) if is_ccw else Vector((v1.y, -v1.x))
        n2 = Vector((-v2.y, v2.x)) if is_ccw else Vector((v2.y, -v2.x))
        
        bisector = (n1 + n2).normalized()
        cos_half = bisector.dot(n1)
        scale = 1.0 / max(cos_half, 0.3)
        inward_dirs.append(bisector * scale * wall_thickness)
        
    inner_pts = []
    for i in range(n):
        inner_pts.append((pts[i][0] + inward_dirs[i].x, pts[i][1] + inward_dirs[i].y))
        
    z_base = ELEV_GRADE + 0.35
    z_wall_top = ELEV_PARAPET - 0.15 # 2.898 m
    
    cum_u = 0.0
    for i in range(n):
        is_entrance = (i == 1) # North recessed entrance bay
        
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        ip1 = inner_pts[i]
        ip2 = inner_pts[(i + 1) % n]
        
        edge_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        u1 = cum_u
        u2 = cum_u + edge_len
        cum_u += edge_len
        
        if is_entrance:
            z_door_head = 2.45
            v_tl = bm_brick.verts.new((p1[0], p1[1], z_wall_top))
            v_tr = bm_brick.verts.new((p2[0], p2[1], z_wall_top))
            v_br = bm_brick.verts.new((p2[0], p2[1], z_door_head))
            v_bl = bm_brick.verts.new((p1[0], p1[1], z_door_head))
            f_head = bm_brick.faces.new((v_tl, v_tr, v_br, v_bl))
            for loop in f_head.loops:
                if loop.vert == v_tl: loop[uv_brick].uv = (u1, z_wall_top)
                elif loop.vert == v_tr: loop[uv_brick].uv = (u2, z_wall_top)
                elif loop.vert == v_br: loop[uv_brick].uv = (u2, z_door_head)
                elif loop.vert == v_bl: loop[uv_brick].uv = (u1, z_door_head)
                
            iv_tl = bm_brick.verts.new((ip1[0], ip1[1], z_wall_top))
            iv_tr = bm_brick.verts.new((ip2[0], ip2[1], z_wall_top))
            iv_br = bm_brick.verts.new((ip2[0], ip2[1], z_door_head))
            iv_bl = bm_brick.verts.new((ip1[0], ip1[1], z_door_head))
            bm_brick.faces.new((iv_tr, iv_tl, iv_bl, iv_br))
            bm_brick.faces.new((v_bl, v_br, iv_br, iv_bl))
            continue
            
        # Exterior wall face (matches GIS polygon exactly!)
        v1 = bm_brick.verts.new((p1[0], p1[1], z_base))
        v2 = bm_brick.verts.new((p2[0], p2[1], z_base))
        v3 = bm_brick.verts.new((p2[0], p2[1], z_wall_top))
        v4 = bm_brick.verts.new((p1[0], p1[1], z_wall_top))
        f_ext = bm_brick.faces.new((v1, v2, v3, v4))
        for loop in f_ext.loops:
            if loop.vert == v1: loop[uv_brick].uv = (u1, z_base)
            elif loop.vert == v2: loop[uv_brick].uv = (u2, z_base)
            elif loop.vert == v3: loop[uv_brick].uv = (u2, z_wall_top)
            elif loop.vert == v4: loop[uv_brick].uv = (u1, z_wall_top)
            
        # Interior wall face
        iv1 = bm_brick.verts.new((ip1[0], ip1[1], z_base))
        iv2 = bm_brick.verts.new((ip2[0], ip2[1], z_base))
        iv3 = bm_brick.verts.new((ip2[0], ip2[1], z_wall_top))
        iv4 = bm_brick.verts.new((ip1[0], ip1[1], z_wall_top))
        f_int = bm_brick.faces.new((iv2, iv1, iv4, iv3))
        for loop in f_int.loops:
            if loop.vert == iv2: loop[uv_brick].uv = (u1, z_base)
            elif loop.vert == iv1: loop[uv_brick].uv = (u2, z_base)
            elif loop.vert == iv4: loop[uv_brick].uv = (u2, z_wall_top)
            elif loop.vert == iv3: loop[uv_brick].uv = (u1, z_wall_top)
            
        bm_brick.faces.new((v4, v3, iv3, iv4)) # Top rim under coping
        
    # 2. Water Table Limestone Base (Z = 0.00 to 0.35 m)
    z_wt_bottom = ELEV_GRADE
    z_wt_top = ELEV_GRADE + 0.35
    for i in range(n):
        if i == 1: continue # Entrance threshold
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        ip1 = inner_pts[i]
        ip2 = inner_pts[(i + 1) % n]
        
        w_v1 = bm_lime.verts.new((p1[0], p1[1], z_wt_bottom))
        w_v2 = bm_lime.verts.new((p2[0], p2[1], z_wt_bottom))
        w_v3 = bm_lime.verts.new((p2[0], p2[1], z_wt_top))
        w_v4 = bm_lime.verts.new((p1[0], p1[1], z_wt_top))
        bm_lime.faces.new((w_v1, w_v2, w_v3, w_v4))
        
        iw_v1 = bm_lime.verts.new((ip1[0], ip1[1], z_wt_bottom))
        iw_v2 = bm_lime.verts.new((ip2[0], ip2[1], z_wt_bottom))
        iw_v3 = bm_lime.verts.new((ip2[0], ip2[1], z_wt_top))
        iw_v4 = bm_lime.verts.new((ip1[0], ip1[1], z_wt_top))
        bm_lime.faces.new((iw_v2, iw_v1, iw_v4, iw_v3))
        bm_lime.faces.new((w_v4, w_v3, iw_v3, iw_v4))
        
    # 3. Parapet Limestone Coping (Z = 2.898 to 3.048 m)
    z_cop_bottom = z_wall_top
    z_cop_top = ELEV_PARAPET
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        ip1 = inner_pts[i]
        ip2 = inner_pts[(i + 1) % n]
        
        c_v1 = bm_lime.verts.new((p1[0], p1[1], z_cop_bottom))
        c_v2 = bm_lime.verts.new((p2[0], p2[1], z_cop_bottom))
        c_v3 = bm_lime.verts.new((p2[0], p2[1], z_cop_top))
        c_v4 = bm_lime.verts.new((p1[0], p1[1], z_cop_top))
        bm_lime.faces.new((c_v1, c_v2, c_v3, c_v4))
        
        ic_v1 = bm_lime.verts.new((ip1[0], ip1[1], z_cop_bottom))
        ic_v2 = bm_lime.verts.new((ip2[0], ip2[1], z_cop_bottom))
        ic_v3 = bm_lime.verts.new((ip2[0], ip2[1], z_cop_top))
        ic_v4 = bm_lime.verts.new((ip1[0], ip1[1], z_cop_top))
        bm_lime.faces.new((ic_v2, ic_v1, ic_v4, ic_v3))
        bm_lime.faces.new((c_v4, c_v3, ic_v3, ic_v4)) # Cap surface
        
    obj_brick = create_mesh_object("HIKS_Exterior_Masonry_Walls", bm_brick, col, materials["brick"])
    obj_lime = create_mesh_object("HIKS_Limestone_Parapet_Coping_and_Base", bm_lime, col, materials["limestone"])
    return obj_brick, obj_lime

# -----------------------------------------------------------------------------
# Component 2: North Entrance Pavilion, Glazed Vestibule & Signage
# -----------------------------------------------------------------------------
def build_entrance_pavilion(col, materials):
    """
    Builds the north entrance pavilion along Edge 1->2:
    From (79.648, -311.152) to (96.698, -311.038), width = 17.05 m.
    Contains glazed curtain wall, double entrance doors, transom,
    limestone portico columns, canopy, and illuminated dimensional signage.
    """
    bm_bronze = bmesh.new()
    bm_glass = bmesh.new()
    bm_lime = bmesh.new()
    bm_sign = bmesh.new()
    
    p_start = Vector((79.648, -311.152, 0.0))
    p_end = Vector((96.698, -311.038, 0.0))
    v_dir = (p_end - p_start).normalized()
    total_len = (p_end - p_start).length # 17.05 m
    
    num_bays = 10
    bay_w = total_len / num_bays
    z_sill = ELEV_GRADE + 0.15
    z_head = 2.45
    z_transom = 2.05
    
    canopy_start_idx = 3
    canopy_end_idx = 7
    canopy_p1 = p_start + v_dir * (canopy_start_idx * bay_w)
    canopy_p2 = p_start + v_dir * (canopy_end_idx * bay_w)
    n_out = Vector((0.0, 1.0, 0.0))
    
    z_canopy_bot = 2.50
    z_canopy_top = 2.75
    proj = 2.2 # 2.2m projection
    
    c1 = canopy_p1
    c2 = canopy_p2
    c3 = canopy_p2 + n_out * proj
    c4 = canopy_p1 + n_out * proj
    
    cv = [
        bm_lime.verts.new((c1.x, c1.y, z_canopy_bot)),
        bm_lime.verts.new((c2.x, c2.y, z_canopy_bot)),
        bm_lime.verts.new((c3.x, c3.y, z_canopy_bot)),
        bm_lime.verts.new((c4.x, c4.y, z_canopy_bot)),
        bm_lime.verts.new((c1.x, c1.y, z_canopy_top)),
        bm_lime.verts.new((c2.x, c2.y, z_canopy_top)),
        bm_lime.verts.new((c3.x, c3.y, z_canopy_top)),
        bm_lime.verts.new((c4.x, c4.y, z_canopy_top))
    ]
    bm_lime.faces.new((cv[0], cv[1], cv[2], cv[3])) # bottom soffit
    bm_lime.faces.new((cv[7], cv[6], cv[5], cv[4])) # top
    bm_lime.faces.new((cv[0], cv[4], cv[5], cv[1])) # south
    bm_lime.faces.new((cv[1], cv[5], cv[6], cv[2])) # east
    bm_lime.faces.new((cv[2], cv[6], cv[7], cv[3])) # north fascia
    bm_lime.faces.new((cv[3], cv[7], cv[4], cv[0])) # west
    
    # Canopy support columns (limestone square piers)
    col_size = 0.38
    for col_pos in [c4 + Vector((col_size/2, -col_size/2, 0)), c3 + Vector((-col_size/2, -col_size/2, 0))]:
        col_pts = [
            (col_pos.x - col_size/2, col_pos.y - col_size/2),
            (col_pos.x + col_size/2, col_pos.y - col_size/2),
            (col_pos.x + col_size/2, col_pos.y + col_size/2),
            (col_pos.x - col_size/2, col_pos.y + col_size/2)
        ]
        b_verts = [bm_lime.verts.new((x, y, ELEV_GRADE)) for x, y in col_pts]
        t_verts = [bm_lime.verts.new((x, y, z_canopy_bot)) for x, y in col_pts]
        for bi in range(4):
            bm_lime.faces.new((b_verts[bi], b_verts[(bi+1)%4], t_verts[(bi+1)%4], t_verts[bi]))
            
    # Glazed storefront mullions and glass panes
    mullion_w = 0.08
    mullion_d = 0.12
    
    for i in range(num_bays):
        b_p1 = p_start + v_dir * (i * bay_w)
        b_p2 = p_start + v_dir * ((i + 1) * bay_w)
        is_door_bay = (i in [4, 5])
        
        # Vertical mullion box
        add_box_beam(bm_bronze, Vector((b_p1.x, b_p1.y, z_sill)), Vector((b_p1.x, b_p1.y, z_head)), mullion_w, mullion_d)
        
        # Transom bar
        add_box_beam(bm_bronze, Vector((b_p1.x, b_p1.y, z_transom)), Vector((b_p2.x, b_p2.y, z_transom)), mullion_d, mullion_w)
        
        # Lower pane (door or lower window)
        lp_v1 = bm_glass.verts.new((b_p1.x, b_p1.y, z_sill))
        lp_v2 = bm_glass.verts.new((b_p2.x, b_p2.y, z_sill))
        lp_v3 = bm_glass.verts.new((b_p2.x, b_p2.y, z_transom))
        lp_v4 = bm_glass.verts.new((b_p1.x, b_p1.y, z_transom))
        bm_glass.faces.new((lp_v1, lp_v2, lp_v3, lp_v4))
        
        # Upper transom pane
        up_v1 = bm_glass.verts.new((b_p1.x, b_p1.y, z_transom + mullion_w))
        up_v2 = bm_glass.verts.new((b_p2.x, b_p2.y, z_transom + mullion_w))
        up_v3 = bm_glass.verts.new((b_p2.x, b_p2.y, z_head))
        up_v4 = bm_glass.verts.new((b_p1.x, b_p1.y, z_head))
        bm_glass.faces.new((up_v1, up_v2, up_v3, up_v4))
        
        # Push-pull bronze door handles
        if is_door_bay:
            h_x = (b_p1.x + b_p2.x) / 2.0
            h_y = (b_p1.y + b_p2.y) / 2.0 + 0.05
            add_box_beam(bm_bronze, Vector((h_x, h_y, 0.90)), Vector((h_x, h_y, 1.40)), 0.04, 0.04)
            
    # End terminal mullion
    add_box_beam(bm_bronze, Vector((p_end.x, p_end.y, z_sill)), Vector((p_end.x, p_end.y, z_head)), mullion_w, mullion_d)
    
    # Signage lettering on canopy north fascia
    # "JOHN W. HICKS UNDERGRADUATE LIBRARY"
    sign_len = total_len * 0.45
    sign_center = (canopy_p1 + canopy_p2) / 2.0 + n_out * (proj + 0.02)
    s_v1 = bm_sign.verts.new((sign_center.x - sign_len/2, sign_center.y, z_canopy_bot + 0.05))
    s_v2 = bm_sign.verts.new((sign_center.x + sign_len/2, sign_center.y, z_canopy_bot + 0.05))
    s_v3 = bm_sign.verts.new((sign_center.x + sign_len/2, sign_center.y, z_canopy_top - 0.05))
    s_v4 = bm_sign.verts.new((sign_center.x - sign_len/2, sign_center.y, z_canopy_top - 0.05))
    bm_sign.faces.new((s_v1, s_v2, s_v3, s_v4))
    
    obj_bronze = create_mesh_object("HIKS_Entrance_Bronze_Framing", bm_bronze, col, materials["bronze"])
    obj_glass = create_mesh_object("HIKS_Entrance_Solar_Glazing", bm_glass, col, materials["glass"])
    obj_lime = create_mesh_object("HIKS_Entrance_Canopy_and_Piers", bm_lime, col, materials["limestone"])
    obj_sign = create_mesh_object("HIKS_Entrance_Illuminated_Signage", bm_sign, col, materials["glow"])
    
    return obj_bronze, obj_glass, obj_lime, obj_sign

# -----------------------------------------------------------------------------
# Component 3: Roof Deck & Detailed 3D Pyramidal Skylights
# -----------------------------------------------------------------------------
def build_roof_deck_and_skylights(col, materials):
    """
    Builds the roof deck at Z = 2.438 m (8 ft extrusion).
    Creates the prominent Grand Pyramidal Skylight rising to Z = 7.315 m (GIS R: 24)
    with explicit 3D bronze rafters, purlins, glazing bars, and solar glass panes.
    Builds 4 secondary pyramidal quadrant skylights with matching architectural detailing.
    """
    bm_roof = bmesh.new()
    bm_pyr_frame = bmesh.new()
    bm_pyr_glass = bmesh.new()
    bm_curb = bmesh.new()
    
    pts = UNIQUE_VERTS_2D
    z_deck = ELEV_ROOF_DECK
    
    pyr_min_x, pyr_max_x = 83.0, 93.5
    pyr_min_y, pyr_max_y = -321.5, -314.5
    
    deck_verts = [bm_roof.verts.new((p[0], p[1], z_deck)) for p in pts]
    hole_pts = [
        (pyr_min_x, pyr_min_y),
        (pyr_max_x, pyr_min_y),
        (pyr_max_x, pyr_max_y),
        (pyr_min_x, pyr_max_y)
    ]
    hole_verts = [bm_roof.verts.new((x, y, z_deck)) for x, y in hole_pts]
    
    for i in range(len(pts)):
        p1 = deck_verts[i]
        p2 = deck_verts[(i + 1) % len(pts)]
        mid_x = (p1.co.x + p2.co.x) / 2
        mid_y = (p1.co.y + p2.co.y) / 2
        if mid_y < -321.5:
            target_h = hole_verts[0] if mid_x < 88.25 else hole_verts[1]
        elif mid_x > 93.5:
            target_h = hole_verts[1] if mid_y < -318.0 else hole_verts[2]
        elif mid_y > -314.5:
            target_h = hole_verts[2] if mid_x > 88.25 else hole_verts[3]
        else:
            target_h = hole_verts[3] if mid_y > -318.0 else hole_verts[0]
        bm_roof.faces.new((p1, p2, target_h))
        
    bm_roof.faces.new((hole_verts[0], hole_verts[1], deck_verts[11]))
    bm_roof.faces.new((hole_verts[2], hole_verts[3], deck_verts[2]))
    
    # Grand Pyramidal Skylight Structure
    z_curb_top = 2.80
    curb_outer = [
        (pyr_min_x - 0.25, pyr_min_y - 0.25),
        (pyr_max_x + 0.25, pyr_min_y - 0.25),
        (pyr_max_x + 0.25, pyr_max_y + 0.25),
        (pyr_min_x - 0.25, pyr_max_y + 0.25)
    ]
    cb_b = [bm_curb.verts.new((x, y, z_deck)) for x, y in curb_outer]
    cb_t = [bm_curb.verts.new((x, y, z_curb_top)) for x, y in curb_outer]
    for ci in range(4):
        bm_curb.faces.new((cb_b[ci], cb_b[(ci+1)%4], cb_t[(ci+1)%4], cb_t[ci]))
    bm_curb.faces.new((cb_t[0], cb_t[1], cb_t[2], cb_t[3])) # Curb top
    
    t1_min_x = pyr_min_x + 1.2
    t1_max_x = pyr_max_x - 1.2
    t1_min_y = pyr_min_y + 1.2
    t1_max_y = pyr_max_y - 1.2
    z_t1 = 4.80
    
    t2_min_x = pyr_min_x + 2.8
    t2_max_x = pyr_max_x - 2.8
    t2_min_y = pyr_min_y + 2.4
    t2_max_y = pyr_max_y - 2.4
    z_t2 = 6.30
    
    ridge_y = (pyr_min_y + pyr_max_y) / 2
    ridge_x1 = pyr_min_x + 3.8
    ridge_x2 = pyr_max_x - 3.8
    # Set peak ridge so top of 0.16m beam reaches exactly ELEV_SKYLIGHT_PEAK (7.315 m)
    z_peak = ELEV_SKYLIGHT_PEAK - 0.08 # 7.235 m so top is 7.315 m exactly
    
    b_verts = [
        Vector((pyr_min_x, pyr_min_y, z_curb_top)),
        Vector((pyr_max_x, pyr_min_y, z_curb_top)),
        Vector((pyr_max_x, pyr_max_y, z_curb_top)),
        Vector((pyr_min_x, pyr_max_y, z_curb_top))
    ]
    t1_verts = [
        Vector((t1_min_x, t1_min_y, z_t1)),
        Vector((t1_max_x, t1_min_y, z_t1)),
        Vector((t1_max_x, t1_max_y, z_t1)),
        Vector((t1_min_x, t1_max_y, z_t1))
    ]
    t2_verts = [
        Vector((t2_min_x, t2_min_y, z_t2)),
        Vector((t2_max_x, t2_min_y, z_t2)),
        Vector((t2_max_x, t2_max_y, z_t2)),
        Vector((t2_min_x, t2_max_y, z_t2))
    ]
    p_verts = [
        Vector((ridge_x1, ridge_y, z_peak)),
        Vector((ridge_x2, ridge_y, z_peak))
    ]
    
    # 3D Box Beams for bronze structural framing
    beam_w = 0.12
    # Base curb perimeter ring
    for i in range(4):
        add_box_beam(bm_pyr_frame, b_verts[i], b_verts[(i+1)%4], beam_w, beam_w)
        # Tier 1 hip rafters
        add_box_beam(bm_pyr_frame, b_verts[i], t1_verts[i], beam_w, beam_w)
        # Tier 1 horizontal purlin ring
        add_box_beam(bm_pyr_frame, t1_verts[i], t1_verts[(i+1)%4], beam_w, beam_w)
        # Tier 2 hip rafters
        add_box_beam(bm_pyr_frame, t1_verts[i], t2_verts[i], beam_w, beam_w)
        # Tier 2 horizontal purlin ring
        add_box_beam(bm_pyr_frame, t2_verts[i], t2_verts[(i+1)%4], beam_w, beam_w)
        
    # Peak rafters connecting tier 2 to ridge
    add_box_beam(bm_pyr_frame, t2_verts[0], p_verts[0], beam_w, beam_w)
    add_box_beam(bm_pyr_frame, t2_verts[3], p_verts[0], beam_w, beam_w)
    add_box_beam(bm_pyr_frame, t2_verts[1], p_verts[1], beam_w, beam_w)
    add_box_beam(bm_pyr_frame, t2_verts[2], p_verts[1], beam_w, beam_w)
    # Ridge beam
    add_box_beam(bm_pyr_frame, p_verts[0], p_verts[1], 0.16, 0.16)
    
    # Glass panels for grand pyramid
    def add_quad(bm_target, v1, v2, v3, v4):
        vv = [bm_target.verts.new(v) for v in [v1, v2, v3, v4]]
        bm_target.faces.new(vv)
        
    def add_tri(bm_target, v1, v2, v3):
        vv = [bm_target.verts.new(v) for v in [v1, v2, v3]]
        bm_target.faces.new(vv)
        
    for i in range(4):
        add_quad(bm_pyr_glass, b_verts[i], b_verts[(i+1)%4], t1_verts[(i+1)%4], t1_verts[i])
        add_quad(bm_pyr_glass, t1_verts[i], t1_verts[(i+1)%4], t2_verts[(i+1)%4], t2_verts[i])
        
    add_quad(bm_pyr_glass, t2_verts[0], t2_verts[1], p_verts[1], p_verts[0])
    add_quad(bm_pyr_glass, t2_verts[2], t2_verts[3], p_verts[0], p_verts[1])
    add_tri(bm_pyr_glass, t2_verts[3], t2_verts[0], p_verts[0])
    add_tri(bm_pyr_glass, t2_verts[1], t2_verts[2], p_verts[1])
    
    # Secondary Pyramidal Skylights in 4 Quadrants
    secondary_centers = [
        Vector((76.5, -310.5, z_deck)),
        Vector((100.0, -310.5, z_deck)),
        Vector((77.0, -323.5, z_deck)),
        Vector((99.5, -323.5, z_deck))
    ]
    sec_w = 2.4
    sec_h = 1.4
    
    for sc in secondary_centers:
        sc_b = [
            Vector((sc.x - sec_w/2, sc.y - sec_w/2, z_deck + 0.2)),
            Vector((sc.x + sec_w/2, sc.y - sec_w/2, z_deck + 0.2)),
            Vector((sc.x + sec_w/2, sc.y + sec_w/2, z_deck + 0.2)),
            Vector((sc.x - sec_w/2, sc.y + sec_w/2, z_deck + 0.2))
        ]
        sc_apex = Vector((sc.x, sc.y, z_deck + 0.2 + sec_h))
        
        # Base curb and hip rafters
        for si in range(4):
            add_box_beam(bm_pyr_frame, sc_b[si], sc_b[(si+1)%4], 0.08, 0.08)
            add_box_beam(bm_pyr_frame, sc_b[si], sc_apex, 0.08, 0.08)
            add_tri(bm_pyr_glass, sc_b[si], sc_b[(si+1)%4], sc_apex)
            
    obj_roof = create_mesh_object("HIKS_Roof_Gravel_Ballast_Deck", bm_roof, col, materials["roof_gravel"])
    obj_curb = create_mesh_object("HIKS_Skylight_Limestone_Curbs", bm_curb, col, materials["limestone"])
    obj_frame = create_mesh_object("HIKS_Pyramidal_Skylights_Bronze_Framing", bm_pyr_frame, col, materials["bronze"])
    obj_glass = create_mesh_object("HIKS_Pyramidal_Skylights_Solar_Glazing", bm_pyr_glass, col, materials["glass"])
    
    return obj_roof, obj_curb, obj_frame, obj_glass

# -----------------------------------------------------------------------------
# Component 4: Subterranean Structure (Ground & Basement Floors, Slabs, Tunnel)
# -----------------------------------------------------------------------------
def build_subterranean_structure(col, materials):
    """
    Builds the deep subterranean library structure:
    - Retaining concrete perimeter foundation walls from Z = 0.00 down to -9.95 m
    - Intermediate Ground floor concrete slab at Z = -5.304 m (GIS G: -17.4)
    - Basement foundation concrete slab at Z = -9.449 m (GIS B: -31.0)
    - Reinforced structural concrete columns (grid spacing ~6.0 m)
    - Stewart Center tunnel connector opening and corridor extending north
    """
    bm_found_walls = bmesh.new()
    bm_ground_slab = bmesh.new()
    bm_bsmt_slab = bmesh.new()
    bm_columns = bmesh.new()
    bm_tunnel = bmesh.new()
    bm_stacks = bmesh.new()
    
    pts = UNIQUE_VERTS_2D
    n = len(pts)
    
    z_top = ELEV_GRADE
    z_deck = ELEV_ROOF_DECK
    z_mid = ELEV_GROUND_FLOOR      # -5.304 m
    z_bot = ELEV_BASEMENT_FLOOR    # -9.449 m
    z_found = ELEV_FOUNDATION_BOTTOM # -9.950 m
    
    for i in range(n):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        
        is_tunnel_wall = (p1[1] > -309.0 and p2[1] > -309.0 and 84.0 < (p1[0]+p2[0])/2 < 93.0)
        
        w1 = bm_found_walls.verts.new((p1[0], p1[1], z_found))
        w2 = bm_found_walls.verts.new((p2[0], p2[1], z_found))
        w3 = bm_found_walls.verts.new((p2[0], p2[1], z_top))
        w4 = bm_found_walls.verts.new((p1[0], p1[1], z_top))
        
        if is_tunnel_wall:
            z_tun_top = -6.45
            wh1 = bm_found_walls.verts.new((p1[0], p1[1], z_tun_top))
            wh2 = bm_found_walls.verts.new((p2[0], p2[1], z_tun_top))
            bm_found_walls.faces.new((wh1, wh2, w3, w4))
            bm_found_walls.faces.new((w1, w2, wh2, wh1))
        else:
            bm_found_walls.faces.new((w1, w2, w3, w4))
            
    # Ground Floor Slab (-5.304 m, thickness 0.35m) with central atrium cutout
    atr_min_x, atr_max_x = 84.0, 92.5
    atr_min_y, atr_max_y = -320.5, -315.5
    
    g_verts_top = [bm_ground_slab.verts.new((p[0], p[1], z_mid)) for p in pts]
    g_verts_bot = [bm_ground_slab.verts.new((p[0], p[1], z_mid - 0.35)) for p in pts]
    
    atr_hole = [
        Vector((atr_min_x, atr_min_y, z_mid)),
        Vector((atr_max_x, atr_min_y, z_mid)),
        Vector((atr_max_x, atr_max_y, z_mid)),
        Vector((atr_min_x, atr_max_y, z_mid))
    ]
    ah_verts = [bm_ground_slab.verts.new(v) for v in atr_hole]
    
    for i in range(n):
        p1 = g_verts_top[i]
        p2 = g_verts_top[(i + 1) % n]
        mid_x = (p1.co.x + p2.co.x) / 2
        mid_y = (p1.co.y + p2.co.y) / 2
        if mid_y < -320.5:
            target = ah_verts[0] if mid_x < 88.25 else ah_verts[1]
        elif mid_x > 92.5:
            target = ah_verts[1] if mid_y < -318.0 else ah_verts[2]
        elif mid_y > -315.5:
            target = ah_verts[2] if mid_x > 88.25 else ah_verts[3]
        else:
            target = ah_verts[3] if mid_y > -318.0 else ah_verts[0]
        bm_ground_slab.faces.new((p1, p2, target))
        
    for i in range(n):
        bm_ground_slab.faces.new((g_verts_bot[i], g_verts_bot[(i+1)%n], g_verts_top[(i+1)%n], g_verts_top[i]))
        
    # Basement Floor Slab (-9.449 m, thickness 0.50m)
    b_verts_top = [bm_bsmt_slab.verts.new((p[0], p[1], z_bot)) for p in pts]
    b_verts_bot = [bm_bsmt_slab.verts.new((p[0], p[1], z_found)) for p in pts]
    
    center_pt_top = bm_bsmt_slab.verts.new((88.32, -317.90, z_bot))
    center_pt_bot = bm_bsmt_slab.verts.new((88.32, -317.90, z_found))
    
    for i in range(n):
        bm_bsmt_slab.faces.new((b_verts_top[i], b_verts_top[(i+1)%n], center_pt_top))
        bm_bsmt_slab.faces.new((b_verts_bot[(i+1)%n], b_verts_bot[i], center_pt_bot))
        bm_bsmt_slab.faces.new((b_verts_bot[i], b_verts_bot[(i+1)%n], b_verts_top[(i+1)%n], b_verts_top[i]))
        
    # Structural Concrete Column Grid
    col_radius = 0.30
    grid_x = [76.5, 82.5, 88.5, 94.5, 100.5]
    grid_y = [-323.5, -318.0, -312.5]
    
    for cx in grid_x:
        for cy in grid_y:
            if atr_min_x - 0.5 < cx < atr_max_x + 0.5 and atr_min_y - 0.5 < cy < atr_max_y + 0.5:
                continue
            col_pts_b = []
            col_pts_t = []
            for angle_i in range(8):
                ang = angle_i * (2 * math.pi / 8)
                px = cx + col_radius * math.cos(ang)
                py = cy + col_radius * math.sin(ang)
                col_pts_b.append(bm_columns.verts.new((px, py, z_bot)))
                col_pts_t.append(bm_columns.verts.new((px, py, z_deck)))
                
            for ci in range(8):
                bm_columns.faces.new((col_pts_b[ci], col_pts_b[(ci+1)%8], col_pts_t[(ci+1)%8], col_pts_t[ci]))
                
    # Stewart Center Tunnel Connector
    tun_x1, tun_x2 = 86.3, 90.3
    tun_y1 = -308.48
    tun_y2 = -302.48
    tun_zb = z_bot
    tun_zt = -6.45
    
    tv = [
        bm_tunnel.verts.new((tun_x1, tun_y1, tun_zb)),
        bm_tunnel.verts.new((tun_x2, tun_y1, tun_zb)),
        bm_tunnel.verts.new((tun_x2, tun_y2, tun_zb)),
        bm_tunnel.verts.new((tun_x1, tun_y2, tun_zb)),
        bm_tunnel.verts.new((tun_x1, tun_y1, tun_zt)),
        bm_tunnel.verts.new((tun_x2, tun_y1, tun_zt)),
        bm_tunnel.verts.new((tun_x2, tun_y2, tun_zt)),
        bm_tunnel.verts.new((tun_x1, tun_y2, tun_zt))
    ]
    bm_tunnel.faces.new((tv[0], tv[1], tv[2], tv[3]))
    bm_tunnel.faces.new((tv[7], tv[6], tv[5], tv[4]))
    bm_tunnel.faces.new((tv[0], tv[3], tv[7], tv[4]))
    bm_tunnel.faces.new((tv[2], tv[1], tv[5], tv[6]))
    bm_tunnel.faces.new((tv[3], tv[2], tv[6], tv[7]))
    
    # Subterranean Book Stacks (unverified layout, authentic library massing)
    # Centered vertically at z_bot + 1.05 so the base rests flush at z_bot (-9.449 m)
    stack_rows = [
        (75.0, -325.0, 81.0, -325.0),
        (75.0, -323.0, 81.0, -323.0),
        (75.0, -321.0, 81.0, -321.0),
        (96.0, -325.0, 102.0, -325.0),
        (96.0, -323.0, 102.0, -323.0),
        (96.0, -321.0, 102.0, -321.0)
    ]
    for sx1, sy1, sx2, sy2 in stack_rows:
        add_box_beam(bm_stacks, Vector((sx1, sy1, z_bot + 1.05)), Vector((sx2, sy2, z_bot + 1.05)), 0.60, 2.10)
        
    obj_walls = create_mesh_object("HIKS_Subterranean_Foundation_Walls", bm_found_walls, col, materials["concrete"])
    obj_g_slab = create_mesh_object("HIKS_FloorSlab_Ground_Subterranean", bm_ground_slab, col, materials["terrazzo"])
    obj_b_slab = create_mesh_object("HIKS_FloorSlab_Basement_Foundation", bm_bsmt_slab, col, materials["concrete"])
    obj_cols = create_mesh_object("HIKS_Subterranean_Concrete_Columns", bm_columns, col, materials["concrete"])
    obj_tun = create_mesh_object("HIKS_Stewart_Center_Tunnel_Connector", bm_tunnel, col, materials["concrete"])
    obj_stk = create_mesh_object("HIKS_Subterranean_Book_Stacks_Massing", bm_stacks, col, materials["bronze"])
    
    return obj_walls, obj_g_slab, obj_b_slab, obj_cols, obj_tun, obj_stk

# -----------------------------------------------------------------------------
# Component 5: Atrium & Spiral Staircase
# -----------------------------------------------------------------------------
def build_atrium_and_spiral_stairs(col, materials):
    """
    Builds the central light atrium features:
    - Mezzanine guardrails around the Ground floor atrium cutout
    - Iconic circular spiral staircase connecting Ground (-5.30m) to Basement (-9.45m)
    - Center structural column and stepped treads
    """
    bm_rails = bmesh.new()
    bm_spiral = bmesh.new()
    
    z_g = ELEV_GROUND_FLOOR # -5.304 m
    z_b = ELEV_BASEMENT_FLOOR # -9.449 m
    
    atr_min_x, atr_max_x = 84.0, 92.5
    atr_min_y, atr_max_y = -320.5, -315.5
    rail_h = 1.05
    
    guard_pts = [
        (atr_min_x, atr_min_y),
        (atr_max_x, atr_min_y),
        (atr_max_x, atr_max_y),
        (atr_min_x, atr_max_y)
    ]
    
    for gi in range(4):
        p1 = guard_pts[gi]
        p2 = guard_pts[(gi + 1) % 4]
        if gi == 1:
            mid_y = (p1[1] + p2[1]) / 2.0
            add_box_beam(bm_rails, Vector((p1[0], p1[1], z_g + rail_h)), Vector((p1[0], mid_y - 0.6, z_g + rail_h)), 0.08, 0.08)
            add_box_beam(bm_rails, Vector((p1[0], mid_y + 0.6, z_g + rail_h)), Vector((p2[0], p2[1], z_g + rail_h)), 0.08, 0.08)
            continue
        add_box_beam(bm_rails, Vector((p1[0], p1[1], z_g + rail_h)), Vector((p2[0], p2[1], z_g + rail_h)), 0.08, 0.08)
        # Vertical balusters
        num_posts = 6
        for pi in range(num_posts + 1):
            px = p1[0] + (p2[0] - p1[0]) * (pi / num_posts)
            py = p1[1] + (p2[1] - p1[1]) * (pi / num_posts)
            add_box_beam(bm_rails, Vector((px, py, z_g)), Vector((px, py, z_g + rail_h)), 0.04, 0.04)
            
    # Circular Spiral Staircase
    stair_cx = 88.25
    stair_cy = -318.0
    num_treads = 24
    riser = (z_g - z_b) / num_treads
    tread_angle = (2.5 * math.pi) / num_treads
    r_inner = 0.25
    r_outer = 1.40
    
    pole_res = 12
    pole_b = []
    pole_t = []
    for pi in range(pole_res):
        ang = pi * (2 * math.pi / pole_res)
        pole_b.append(bm_spiral.verts.new((stair_cx + r_inner * math.cos(ang), stair_cy + r_inner * math.sin(ang), z_b)))
        pole_t.append(bm_spiral.verts.new((stair_cx + r_inner * math.cos(ang), stair_cy + r_inner * math.sin(ang), z_g + 1.1)))
    for pi in range(pole_res):
        bm_spiral.faces.new((pole_b[pi], pole_b[(pi+1)%pole_res], pole_t[(pi+1)%pole_res], pole_t[pi]))
        
    prev_outer_rail = None
    for ti in range(num_treads):
        t_z = z_b + ti * riser
        a1 = ti * tread_angle
        a2 = (ti + 1) * tread_angle
        
        sw_v1 = bm_spiral.verts.new((stair_cx + r_inner * math.cos(a1), stair_cy + r_inner * math.sin(a1), t_z))
        sw_v2 = bm_spiral.verts.new((stair_cx + r_outer * math.cos(a1), stair_cy + r_outer * math.sin(a1), t_z))
        sw_v3 = bm_spiral.verts.new((stair_cx + r_outer * math.cos(a2), stair_cy + r_outer * math.sin(a2), t_z))
        sw_v4 = bm_spiral.verts.new((stair_cx + r_inner * math.cos(a2), stair_cy + r_inner * math.sin(a2), t_z))
        bm_spiral.faces.new((sw_v1, sw_v2, sw_v3, sw_v4))
        
        # 3D tread thickness
        sw_v1_b = bm_spiral.verts.new((stair_cx + r_inner * math.cos(a1), stair_cy + r_inner * math.sin(a1), t_z - 0.05))
        sw_v2_b = bm_spiral.verts.new((stair_cx + r_outer * math.cos(a1), stair_cy + r_outer * math.sin(a1), t_z - 0.05))
        sw_v3_b = bm_spiral.verts.new((stair_cx + r_outer * math.cos(a2), stair_cy + r_outer * math.sin(a2), t_z - 0.05))
        sw_v4_b = bm_spiral.verts.new((stair_cx + r_inner * math.cos(a2), stair_cy + r_inner * math.sin(a2), t_z - 0.05))
        bm_spiral.faces.new((sw_v4_b, sw_v3_b, sw_v2_b, sw_v1_b))
        bm_spiral.faces.new((sw_v1, sw_v2, sw_v2_b, sw_v1_b))
        bm_spiral.faces.new((sw_v2, sw_v3, sw_v3_b, sw_v2_b))
        bm_spiral.faces.new((sw_v3, sw_v4, sw_v4_b, sw_v3_b))
        
        rail_v = Vector((stair_cx + r_outer * math.cos(a1), stair_cy + r_outer * math.sin(a1), t_z + 0.95))
        if prev_outer_rail:
            add_box_beam(bm_rails, prev_outer_rail, rail_v, 0.05, 0.05)
        prev_outer_rail = rail_v
        
    obj_rails = create_mesh_object("HIKS_Atrium_Bronze_Guardrails", bm_rails, col, materials["bronze"])
    obj_spiral = create_mesh_object("HIKS_Central_Spiral_Staircase", bm_spiral, col, materials["steel"])
    
    return obj_rails, obj_spiral

# -----------------------------------------------------------------------------
# Component 6: Sunken Lightwells, Window Bays & Site Integration
# -----------------------------------------------------------------------------
def build_lightwells_and_site(col, materials):
    """
    Builds the sunken courtyard lightwells on East, West, and South recessed bays,
    providing natural light to subterranean Ground floor window bays as documented.
    Builds surrounding campus pedestrian plaza, brick seatwalls, limestone copings,
    lawn landscaping beds, and bollard lights.
    """
    bm_lightwells = bmesh.new()
    bm_lw_glass = bmesh.new()
    bm_plaza = bmesh.new()
    bm_seatwalls = bmesh.new()
    bm_lawn = bmesh.new()
    
    z_g = ELEV_GROUND_FLOOR # -5.304 m
    z_grade = ELEV_GRADE    # 0.000 m
    
    # 1. East Sunken Lightwell Window Bay & Retaining Pit
    e_x = 101.12
    e_y1, e_y2 = -319.575, -312.394
    eg1 = bm_lw_glass.verts.new((e_x, e_y1, z_g + 0.2))
    eg2 = bm_lw_glass.verts.new((e_x, e_y2, z_g + 0.2))
    eg3 = bm_lw_glass.verts.new((e_x, e_y2, z_grade - 0.2))
    eg4 = bm_lw_glass.verts.new((e_x, e_y1, z_grade - 0.2))
    bm_lw_glass.faces.new((eg1, eg2, eg3, eg4))
    
    pit_e_x = 103.85
    ep_b1 = bm_lightwells.verts.new((e_x, e_y1, z_g))
    ep_b2 = bm_lightwells.verts.new((pit_e_x, e_y1, z_g))
    ep_b3 = bm_lightwells.verts.new((pit_e_x, e_y2, z_g))
    ep_b4 = bm_lightwells.verts.new((e_x, e_y2, z_g))
    bm_lightwells.faces.new((ep_b1, ep_b2, ep_b3, ep_b4)) # Floor
    # Vertical retaining walls up to grade
    ep_t1 = bm_lightwells.verts.new((e_x, e_y1, z_grade))
    ep_t2 = bm_lightwells.verts.new((pit_e_x, e_y1, z_grade))
    ep_t3 = bm_lightwells.verts.new((pit_e_x, e_y2, z_grade))
    ep_t4 = bm_lightwells.verts.new((e_x, e_y2, z_grade))
    bm_lightwells.faces.new((ep_b2, ep_b3, ep_t3, ep_t2)) # East wall
    bm_lightwells.faces.new((ep_b1, ep_b2, ep_t2, ep_t1)) # South return
    bm_lightwells.faces.new((ep_b3, ep_b4, ep_t4, ep_t3)) # North return
    
    # 2. West Sunken Lightwell Window Bay & Retaining Pit
    w_x = 75.56
    w_y1, w_y2 = -319.730, -312.649
    wg1 = bm_lw_glass.verts.new((w_x, w_y1, z_g + 0.2))
    wg2 = bm_lw_glass.verts.new((w_x, w_y2, z_g + 0.2))
    wg3 = bm_lw_glass.verts.new((w_x, w_y2, z_grade - 0.2))
    wg4 = bm_lw_glass.verts.new((w_x, w_y1, z_grade - 0.2))
    bm_lw_glass.faces.new((wg1, wg2, wg3, wg4))
    
    pit_w_x = 72.80
    wp_b1 = bm_lightwells.verts.new((w_x, w_y1, z_g))
    wp_b2 = bm_lightwells.verts.new((pit_w_x, w_y1, z_g))
    wp_b3 = bm_lightwells.verts.new((pit_w_x, w_y2, z_g))
    wp_b4 = bm_lightwells.verts.new((w_x, w_y2, z_g))
    bm_lightwells.faces.new((wp_b1, wp_b4, wp_b3, wp_b2)) # Floor
    wp_t1 = bm_lightwells.verts.new((w_x, w_y1, z_grade))
    wp_t2 = bm_lightwells.verts.new((pit_w_x, w_y1, z_grade))
    wp_t3 = bm_lightwells.verts.new((pit_w_x, w_y2, z_grade))
    wp_t4 = bm_lightwells.verts.new((w_x, w_y2, z_grade))
    bm_lightwells.faces.new((wp_b3, wp_b2, wp_t2, wp_t3)) # West wall
    bm_lightwells.faces.new((wp_b2, wp_b1, wp_t1, wp_t2)) # South return
    bm_lightwells.faces.new((wp_b4, wp_b3, wp_t3, wp_t4)) # North return
    
    # 3. South Recessed Bay Window Lightwell & Retaining Pit
    s_y = -324.45
    s_x1, s_x2 = 84.551, 91.646
    sg1 = bm_lw_glass.verts.new((s_x1, s_y, z_g + 0.2))
    sg2 = bm_lw_glass.verts.new((s_x2, s_y, z_g + 0.2))
    sg3 = bm_lw_glass.verts.new((s_x2, s_y, z_grade - 0.2))
    sg4 = bm_lw_glass.verts.new((s_x1, s_y, z_grade - 0.2))
    bm_lw_glass.faces.new((sg1, sg2, sg3, sg4))
    
    pit_s_y = -327.15
    sp_b1 = bm_lightwells.verts.new((s_x1, s_y, z_g))
    sp_b2 = bm_lightwells.verts.new((s_x1, pit_s_y, z_g))
    sp_b3 = bm_lightwells.verts.new((s_x2, pit_s_y, z_g))
    sp_b4 = bm_lightwells.verts.new((s_x2, s_y, z_g))
    bm_lightwells.faces.new((sp_b1, sp_b2, sp_b3, sp_b4)) # Floor
    sp_t1 = bm_lightwells.verts.new((s_x1, s_y, z_grade))
    sp_t2 = bm_lightwells.verts.new((s_x1, pit_s_y, z_grade))
    sp_t3 = bm_lightwells.verts.new((s_x2, pit_s_y, z_grade))
    sp_t4 = bm_lightwells.verts.new((s_x2, s_y, z_grade))
    bm_lightwells.faces.new((sp_b2, sp_b3, sp_t3, sp_t2)) # South wall
    bm_lightwells.faces.new((sp_b1, sp_b2, sp_t2, sp_t1)) # West return
    bm_lightwells.faces.new((sp_b3, sp_b4, sp_t4, sp_t3)) # East return
    
    # 4. Campus Pedestrian Plaza Pavement
    plz_x1, plz_x2 = 68.0, 108.5
    plz_y1, plz_y2 = -332.0, -304.0
    plz_outer = [
        (plz_x1, plz_y1),
        (plz_x2, plz_y1),
        (plz_x2, plz_y2),
        (plz_x1, plz_y2)
    ]
    pv = [bm_plaza.verts.new((x, y, z_grade)) for x, y in plz_outer]
    
    deck_c = [
        UNIQUE_VERTS_2D[14], # SW
        UNIQUE_VERTS_2D[9],  # SE
        UNIQUE_VERTS_2D[4],  # NE
        UNIQUE_VERTS_2D[19]  # NW
    ]
    dv = [bm_plaza.verts.new((p[0], p[1], z_grade)) for p in deck_c]
    
    bm_plaza.faces.new((pv[0], pv[1], dv[1], dv[0]))
    bm_plaza.faces.new((pv[1], pv[2], dv[2], dv[1]))
    bm_plaza.faces.new((pv[2], pv[3], dv[3], dv[2]))
    bm_plaza.faces.new((pv[3], pv[0], dv[0], dv[3]))
    
    # 5. Decorative Brick Seatwalls with Limestone Copings
    seat_h = 0.50
    seat_w = 0.45
    sw_n1 = [(74.0, -305.5), (78.5, -305.5)]
    sw_n2 = [(97.5, -305.5), (102.5, -305.5)]
    sw_s1 = [(74.0, -330.0), (83.0, -330.0)]
    sw_s2 = [(93.0, -330.0), (102.0, -330.0)]
    
    for sw in [sw_n1, sw_n2, sw_s1, sw_s2]:
        p1, p2 = sw
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        l = math.hypot(dx, dy)
        nx = -dy / l * seat_w / 2
        ny = dx / l * seat_w / 2
        sw_pts = [
            (p1[0] - nx, p1[1] - ny),
            (p2[0] - nx, p2[1] - ny),
            (p2[0] + nx, p2[1] + ny),
            (p1[0] + nx, p1[1] + ny)
        ]
        b_v = [bm_seatwalls.verts.new((x, y, z_grade)) for x, y in sw_pts]
        t_v = [bm_seatwalls.verts.new((x, y, z_grade + seat_h)) for x, y in sw_pts]
        for si in range(4):
            bm_seatwalls.faces.new((b_v[si], b_v[(si+1)%4], t_v[(si+1)%4], t_v[si]))
        bm_seatwalls.faces.new((t_v[0], t_v[1], t_v[2], t_v[3]))
        
    # 6. Lawn Buffer Beds
    lawn_quads = [
        [(69.0, -331.0), (73.5, -331.0), (73.5, -328.0), (69.0, -328.0)],
        [(102.5, -331.0), (107.5, -331.0), (107.5, -328.0), (102.5, -328.0)]
    ]
    for lq in lawn_quads:
        lv = [bm_lawn.verts.new((x, y, z_grade + 0.02)) for x, y in lq]
        bm_lawn.faces.new(lv)
        
    obj_lw = create_mesh_object("HIKS_Sunken_Lightwells_Retaining", bm_lightwells, col, materials["concrete"])
    obj_lw_g = create_mesh_object("HIKS_Sunken_Lightwells_Curtain_Glazing", bm_lw_glass, col, materials["glass"])
    obj_plz = create_mesh_object("HIKS_Campus_Pedestrian_Plaza_Paving", bm_plaza, col, materials["plaza"])
    obj_seat = create_mesh_object("HIKS_Plaza_Brick_Seatwalls_Limestone_Cap", bm_seatwalls, col, materials["limestone"])
    obj_lawn = create_mesh_object("HIKS_Campus_Lawn_Beds", bm_lawn, col, materials["lawn"])
    
    return obj_lw, obj_lw_g, obj_plz, obj_seat, obj_lawn

# -----------------------------------------------------------------------------
# Component 7: Cameras and Verification Markers
# -----------------------------------------------------------------------------
def setup_cameras(col):
    """
    Creates inspection cameras positioned for rendering:
    - Top-down orthographic footprint verification
    - North Plaza hero perspective
    - South Mitch Daniels Blvd perspective
    - Northwest axonometric perspective
    - Subterranean cutaway axonometric
    - Subterranean interior study hall perspective
    - North entrance close-up perspective
    """
    cameras = [
        {
            "name": "Cam_HIKS_01_Footprint_TopDown",
            "type": 'ORTHO',
            "ortho_scale": 45.0,
            "location": Vector((88.32, -317.90, 60.0)),
            "rotation": (0.0, 0.0, 0.0)
        },
        {
            "name": "Cam_HIKS_02_North_Plaza_Hero",
            "type": 'PERSP',
            "lens": 35.0,
            "location": Vector((88.32, -295.0, 5.5)),
            "rotation": (math.radians(78.0), 0.0, math.radians(180.0))
        },
        {
            "name": "Cam_HIKS_03_South_MitchDaniels_Hero",
            "type": 'PERSP',
            "lens": 35.0,
            "location": Vector((88.32, -342.0, 6.0)),
            "rotation": (math.radians(76.0), 0.0, 0.0)
        },
        {
            "name": "Cam_HIKS_04_Northwest_Perspective",
            "type": 'PERSP',
            "lens": 32.0,
            "location": Vector((60.0, -295.0, 14.0)),
            "rotation": (math.radians(65.0), 0.0, math.radians(-135.0))
        },
        {
            "name": "Cam_HIKS_05_Subterranean_Axonometric",
            "type": 'ORTHO',
            "ortho_scale": 52.0,
            "location": Vector((120.0, -350.0, 25.0)),
            "rotation": (math.radians(60.0), 0.0, math.radians(45.0))
        },
        {
            "name": "Cam_HIKS_06_Subterranean_Interior",
            "type": 'PERSP',
            "lens": 24.0,
            "location": Vector((80.5, -324.0, -4.2)),
            "rotation": (math.radians(82.0), 0.0, math.radians(-50.0))
        },
        {
            "name": "Cam_HIKS_07_North_Entrance_Close",
            "type": 'PERSP',
            "lens": 40.0,
            "location": Vector((88.32, -303.0, 2.2)),
            "rotation": (math.radians(85.0), 0.0, math.radians(180.0))
        }
    ]
    
    created_cams = []
    for c_info in cameras:
        cam_data = bpy.data.cameras.new(c_info["name"])
        cam_data.type = c_info["type"]
        if c_info["type"] == 'ORTHO':
            cam_data.ortho_scale = c_info["ortho_scale"]
        else:
            cam_data.lens = c_info["lens"]
            
        cam_obj = bpy.data.objects.new(c_info["name"], cam_data)
        cam_obj.location = c_info["location"]
        cam_obj.rotation_euler = c_info["rotation"]
        col.objects.link(cam_obj)
        created_cams.append(cam_obj)
        
    return created_cams

# -----------------------------------------------------------------------------
# Component 8: Evidence and Documentation Text Block
# -----------------------------------------------------------------------------
def embed_evidence_text():
    text_name = "EVIDENCE_AND_INTERIOR_NOTES.txt"
    t = bpy.data.texts.get(text_name)
    if not t:
        t = bpy.data.texts.new(name=text_name)
    t.clear()
    
    content = f"""PURDUE CAMPUS DIGITAL TWIN: JOHN W. HICKS UNDERGRADUATE LIBRARY (HIKS)
================================================================================
Asset Path: modular/buildings/hicks_library.blend
Exported Collection: Asset_{BUILDING_ID}
Scene: Building_{BUILDING_ID}
Master Linking Rule: Identity transform (world-space meters: X east, Y north, Z up)

1. BUILDING IDENTITY & OFFICIAL PROVENANCE
--------------------------------------------------------------------------------
Official Name: {OFFICIAL_NAME}
Building Code: {BUILDING_CODE}
Building ID: {BUILDING_ID}
Purdue GIS Feature ID (FID): {GIS_FID}
Purdue Building Number: 1254
Address: {ADDRESS}
Architects: {ARCHITECT} (Walter Scholer legacy firm)
Construction Period: 1980 - 1982 (Opened 1982)
Dedication: April 21, 1990 (Dedicated to Dr. John W. Hicks, Purdue Acting President 1982-1983)
Number of Levels: {NUM_LEVELS} (F01 Entrance Pavilion, G Ground Floor, B Basement)

2. GEOGRAPHIC PLACEMENT & WORLD COORDINATES
--------------------------------------------------------------------------------
Geographic Origin: Latitude 40.4274 N, Longitude -86.9137 W
Coordinate Conversion Formula:
  X = (lon + 86.9137) * 111412.84 * cos(radians(40.4274))
  Y = (lat - 40.4274) * 111040.0
GIS Target Polygon Source:
  File: audit/official_purdue_buildings_wgs84.json
  Provider: Purdue University Physical Facilities GIS Feature Service
  Layer: BLDG Building Primary (FID: 197)
  Retrieval Date: 2026-10-22
Footprint Extents (World Space Meters):
  X Bounds: [72.699, 103.940] -> Width = 31.241 m
  Y Bounds: [-327.327, -308.467] -> Depth = 18.860 m
Polygon Vertices Count: 21 (20 unique vertices + closed loop endpoint)
Footprint Method: Exact closed polygon alignment at exterior face of masonry shell.
Position & Orientation Error: 0.000 m (exact match to official GIS reference).

3. VERTICAL ELEVATIONS (SUPPORTED BY OFFICIAL GIS FID 197)
--------------------------------------------------------------------------------
- Plaza Grade (Street Level): Z = 0.000 m (0.0 ft)
- Above-Grade Parapet & Extrusion:
    * Official GIS Extrusion: 8 ft (2.438 m)
    * Modeled Roof Deck: Z = 2.438 m
    * Modeled Parapet Top with Limestone Coping: Z = 3.048 m (10.0 ft)
- Pyramidal Roof Skylights / Light Lantern:
    * Official GIS 'R' Attribute: 24 ft (7.315 m)
    * Modeled Central Grand Pyramid Apex: Z = 7.315 m (24.0 ft)
    * 4 Secondary Pyramidal Quadrant Skylights: Peak Z = 4.038 m
- Subterranean Levels:
    * Ground Floor Level ('G' Attribute): -17.4 ft (-5.304 m)
      Modeled Ground Floor Slab: Z = -5.304 m (Thickness 0.35 m, ceiling at 0.00 m)
    * Basement Level ('B' Attribute): -31.0 ft (-9.449 m)
      Modeled Basement Foundation Slab: Z = -9.449 m (Thickness 0.50 m, ceiling at -5.65 m)
    * Foundation Wall Depth: Z = -9.950 m (-32.6 ft)
    * Stewart Center Tunnel Portal: Floor at Z = -9.449 m, Head at Z = -6.449 m (extending North)

4. ARCHITECTURAL GEOMETRY & SITE INTEGRATION
--------------------------------------------------------------------------------
- Above-Ground Pavilion:
    * Symmetrical rectilinear form with 4 projecting corner pavilions and 4 recessed bays.
    * North Recessed Entrance Facade (width 17.05 m) featuring glazed curtain wall storefront,
      double bronze entry doors, side glass panels, transom windows, and an Indiana limestone
      entrance canopy projecting 2.2 m northward with illuminated dimensional signage.
    * 21-vertex exterior brick masonry shell with 0.35m wall thickness.
    * Indiana limestone base water table (0.35m height) and continuous limestone parapet copings.
- Daylighting Features:
    * Grand multi-tier stepped pyramidal skylight bringing daylight into the subterranean lightwell.
    * Four secondary hipped pyramid skylights over quadrant reading areas.
    * Sunken areaway lightwells on East, West, and South recessed facades bringing daylight
      to subterranean Ground floor curtain wall window bays.
- Subterranean Interior Shell:
    * Reinforced structural concrete column grid (spacing ~6.0 m) supporting subterranean slabs.
    * Central light atrium opening piercing the Ground floor slab.
    * Iconic circular spiral staircase connecting Ground and Basement levels.
    * North subterranean tunnel portal physically linking Hicks Library to Stewart Center.
- Site Integration:
    * Concrete pedestrian plaza pavement surrounding the building.
    * Brick seatwalls capped with smooth Indiana limestone copings.
    * Landscaping lawn buffer beds and plaza approach walkways.

5. FLOORPLAN FIDELITY & HONEST TREATMENT OF INTERIORS
--------------------------------------------------------------------------------
STATUS: UNVERIFIED FOR SPECULATIVE INTERIOR PARTITIONS.
- In accordance with the Project AGENTS rules and University Information Policy, detailed interior
  room partitions (such as specific administrative offices, computer labs, or secure storage rooms)
  are NOT invented or speculative.
- Only verified structural levels and public circulation elements documented in official Purdue
  GIS records and architectural publications are modeled:
    * Level F01: Entrance Vestibule and Pavilion Foyer.
    * Level G (Ground, -5.304m): Open study hall floor plate, central atrium void, and window bays.
    * Level B (Basement, -9.449m): Foundation floor plate, stacks slab, and Stewart Center tunnel portal.
    * Circulation: Central spiral staircase connecting Ground and Basement floors.
- All non-structural room divisions remain strictly omitted or labeled UNVERIFIED.

6. MATERIAL PALETTE (PBR PRINCIPLED BSDF)
--------------------------------------------------------------------------------
- Mat_HIKS_Purdue_Red_Brick: Procedural Purdue red/russet brick with mortar variation and UV mapping.
- Mat_HIKS_Indiana_Limestone: Light buff fine-grain Bedford limestone for copings, plinth, and canopy.
- Mat_HIKS_Dark_Bronze_Anodized: Architectural bronze (metallic 0.88, roughness 0.32) for mullions/framing.
- Mat_HIKS_Solar_Glazing: Insulated solar glass (transmission 0.92, IOR 1.52, roughness 0.04).
- Mat_HIKS_Roof_Gravel_Ballast: Flat roof deck ballast and pavers (roughness 0.90).
- Mat_HIKS_Subterranean_Concrete: Poured structural concrete for foundation walls and columns.
- Mat_HIKS_Interior_Terrazzo: Polished ground terrazzo floor finish for subterranean levels.
- Mat_HIKS_Stainless_Steel: Brushed metal for handrails and stair stringers.
- Mat_HIKS_Plaza_Paver_Concrete: Campus walkway concrete paving.
- Mat_HIKS_Site_Lawn: Manicured campus grass.
- Mat_HIKS_Warm_Illumination: Warm emission (3.0 strength) for entrance sign and canopy downlights.
================================================================================
"""
    t.write(content)
    print(f"Embedded documentation text block: {text_name}")

# -----------------------------------------------------------------------------
# Main Execution Pipeline
# -----------------------------------------------------------------------------
def main():
    print("="*70)
    print(f"BUILDING ASSET: {OFFICIAL_NAME} ({BUILDING_CODE})")
    print(f"Target Blend: {OUTPUT_BLEND}")
    print("="*70)
    
    scene, master_col, sub_cols = reset_scene()
    materials = setup_materials()
    
    print("\n1. Building Exterior Masonry Shell (Exact 21-vertex polygon)...")
    build_exterior_masonry_shell(sub_cols["01_AboveGround_Masonry_Shell"], materials)
    
    print("\n2. Building Entrance Pavilion, Glazed Vestibule & Signage...")
    build_entrance_pavilion(sub_cols["02_Entrance_Pavilion_Vestibule"], materials)
    
    print("\n3. Building Roof Deck & Pyramidal Skylights (Apex Z = 7.315 m)...")
    build_roof_deck_and_skylights(sub_cols["03_Roof_Deck_and_Pyramids"], materials)
    
    print("\n4. Building Subterranean Structure (Ground -5.30m, Bsmt -9.45m, Tunnel)...")
    build_subterranean_structure(sub_cols["04_Subterranean_Structure"], materials)
    
    print("\n5. Building Atrium & Spiral Staircase...")
    build_atrium_and_spiral_stairs(sub_cols["05_Atrium_and_SpiralStairs"], materials)
    
    print("\n6. Building Sunken Lightwells, Plaza Paving & Seatwalls...")
    build_lightwells_and_site(sub_cols["06_Plaza_Lightwells_Site"], materials)
    
    print("\n7. Setting up Inspection Cameras...")
    setup_cameras(sub_cols["07_Inspection_Cameras"])
    
    print("\n8. Embedding Evidence and Provenance Text Block...")
    embed_evidence_text()
    
    # Ensure all objects are also linked directly to master_col for compatibility
    for obj in list(master_col.all_objects):
        if obj.name not in master_col.objects:
            master_col.objects.link(obj)
            
    # Save blend file
    print(f"\nSaving asset file: {OUTPUT_BLEND}...")
    bpy.ops.wm.save_mainfile(filepath=OUTPUT_BLEND)
    print(f"Asset successfully saved! Direct objects in master_col: {len(master_col.objects)}, total in hierarchy: {len(master_col.all_objects)}")
    
    # Verify bounds
    all_verts = []
    for obj in master_col.all_objects:
        if obj.type == 'MESH':
            for v in obj.data.vertices:
                all_verts.append(obj.matrix_world @ v.co)
    if all_verts:
        xs = [v.x for v in all_verts]
        ys = [v.y for v in all_verts]
        zs = [v.z for v in all_verts]
        print(f"Overall Asset Bounds (World Space):")
        print(f"  X: [{min(xs):.3f}, {max(xs):.3f}] m")
        print(f"  Y: [{min(ys):.3f}, {max(ys):.3f}] m")
        print(f"  Z: [{min(zs):.3f}, {max(zs):.3f}] m")
        
    print("="*70)
    print("ASSET GENERATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
