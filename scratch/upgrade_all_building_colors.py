import bpy, os, json, re, shutil
from pathlib import Path
from mathutils import Vector

ROOT = Path('.').resolve()
MODULAR_DIR = ROOT / 'modular'
BUILDINGS_DIR = MODULAR_DIR / 'buildings'
BACKUP_DIR = ROOT / 'materials' / 'backups' / 'detailed_buildings'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Purdue Architectural Color Standards (sRGB linear)
PURDUE_RED_BRICK = (0.44, 0.16, 0.11, 1.0)
INDIANA_LIMESTONE = (0.82, 0.79, 0.72, 1.0)
SLATE_ROOF = (0.20, 0.21, 0.23, 1.0)
COPPER_VERDIGRIS = (0.32, 0.50, 0.42, 1.0)
ARCH_GLASS = (0.06, 0.10, 0.14, 1.0)
DARK_BRONZE = (0.22, 0.17, 0.13, 1.0)
STEEL_METAL = (0.15, 0.16, 0.17, 1.0)
ALUMINUM_SILVER = (0.75, 0.77, 0.80, 1.0)
CONCRETE_PAVEMENT = (0.58, 0.57, 0.55, 1.0)
WARM_WOOD = (0.32, 0.20, 0.12, 1.0)
PURDUE_OLD_GOLD = (0.86, 0.71, 0.28, 1.0)
TURF_GRASS = (0.18, 0.32, 0.12, 1.0)

def classify_material_role(name):
    n = name.lower()
    if any(k in n for k in ['gold']):
        return 'gold'
    if any(k in n for k in ['brick', 'masonry', 'paver']):
        return 'brick'
    if any(k in n for k in ['limestone', 'bedford', 'stone', 'coping', 'water_table', 'capital', 'pilaster']):
        return 'limestone'
    if any(k in n for k in ['slate', 'roof', 'membrane', 'shingle', 'gravel']):
        if 'copper' in n or 'verdigris' in n:
            return 'copper'
        return 'roof'
    if any(k in n for k in ['copper', 'verdigris', 'dome', 'patina']):
        return 'copper'
    if any(k in n for k in ['glass', 'glazing', 'window']):
        return 'glass'
    if any(k in n for k in ['bronze']):
        return 'bronze'
    if any(k in n for k in ['aluminum', 'aluminium', 'composite', 'panel']):
        return 'aluminum'
    if any(k in n for k in ['metal', 'steel', 'iron', 'mullion', 'rail', 'bikerack']):
        return 'metal'
    if any(k in n for k in ['concrete', 'slab', 'pavement', 'floor', 'asphalt', 'terrazzo', 'plaster']):
        return 'concrete'
    if any(k in n for k in ['wood', 'oak', 'teak', 'timber', 'deck']):
        return 'wood'
    if any(k in n for k in ['grass', 'turf', 'lawn', 'foliage', 'tree', 'shrub']):
        return 'foliage'
    return None

def enhance_material(mat):
    role = classify_material_role(mat.name)
    if not role:
        return False
        
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    p = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not p:
        p = nodes.new('ShaderNodeBsdfPrincipled')
        p.location = (0, 0)
        out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not out:
            out = nodes.new('ShaderNodeOutputMaterial')
            out.location = (300, 0)
        links.new(p.outputs['BSDF'], out.inputs['Surface'])
        
    has_image = any(n.type == 'TEX_IMAGE' for n in nodes)
    
    current_col = list(p.inputs['Base Color'].default_value)
    is_default_gray = (abs(current_col[0] - 0.8) < 0.05 and abs(current_col[1] - 0.8) < 0.05 and abs(current_col[2] - 0.8) < 0.05)
    has_input_link = len(p.inputs['Base Color'].links) > 0
    
    # If it's default gray or has no color link, set the proper Purdue colors
    if role == 'brick':
        if not has_image and (is_default_gray or not has_input_link):
            p.inputs['Base Color'].default_value = PURDUE_RED_BRICK
            p.inputs['Roughness'].default_value = 0.78
        mat.diffuse_color = PURDUE_RED_BRICK
    elif role == 'limestone':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = INDIANA_LIMESTONE
            p.inputs['Roughness'].default_value = 0.72
        mat.diffuse_color = INDIANA_LIMESTONE
    elif role == 'roof':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = SLATE_ROOF
            p.inputs['Roughness'].default_value = 0.80
        mat.diffuse_color = SLATE_ROOF
    elif role == 'copper':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = COPPER_VERDIGRIS
            p.inputs['Roughness'].default_value = 0.50
            p.inputs['Metallic'].default_value = 0.30
        mat.diffuse_color = COPPER_VERDIGRIS
    elif role == 'glass':
        p.inputs['Base Color'].default_value = ARCH_GLASS
        p.inputs['Roughness'].default_value = 0.08
        if 'Transmission Weight' in p.inputs:
            p.inputs['Transmission Weight'].default_value = 0.85
        elif 'Transmission' in p.inputs:
            p.inputs['Transmission'].default_value = 0.85
        p.inputs['IOR'].default_value = 1.50
        mat.diffuse_color = ARCH_GLASS
    elif role == 'bronze':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = DARK_BRONZE
            p.inputs['Metallic'].default_value = 0.75
            p.inputs['Roughness'].default_value = 0.35
        mat.diffuse_color = DARK_BRONZE
    elif role == 'aluminum':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = ALUMINUM_SILVER
            p.inputs['Metallic'].default_value = 0.65
            p.inputs['Roughness'].default_value = 0.30
        mat.diffuse_color = ALUMINUM_SILVER
    elif role == 'metal':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = STEEL_METAL
            p.inputs['Metallic'].default_value = 0.80
            p.inputs['Roughness'].default_value = 0.30
        mat.diffuse_color = STEEL_METAL
    elif role == 'concrete':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = CONCRETE_PAVEMENT
            p.inputs['Roughness'].default_value = 0.82
        mat.diffuse_color = CONCRETE_PAVEMENT
    elif role == 'wood':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = WARM_WOOD
            p.inputs['Roughness'].default_value = 0.45
        mat.diffuse_color = WARM_WOOD
    elif role == 'gold':
        p.inputs['Base Color'].default_value = PURDUE_OLD_GOLD
        p.inputs['Metallic'].default_value = 0.85
        p.inputs['Roughness'].default_value = 0.25
        mat.diffuse_color = PURDUE_OLD_GOLD
    elif role == 'foliage':
        if is_default_gray or not has_input_link:
            p.inputs['Base Color'].default_value = TURF_GRASS
            p.inputs['Roughness'].default_value = 0.90
        mat.diffuse_color = TURF_GRASS
        
    return True

def get_or_create_material(name, role):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    enhance_material(mat)
    return mat

def fix_unassigned_meshes(col):
    fixed_count = 0
    for o in col.all_objects:
        if o.type != 'MESH':
            continue
        needs_mat = False
        if len(o.material_slots) == 0:
            needs_mat = True
            o.data.materials.append(None)
        
        for idx, slot in enumerate(o.material_slots):
            if slot.material is None or slot.material.name.lower() in ('material', 'material.001', 'default'):
                # Assign based on object name
                role = classify_material_role(o.name)
                mat_name = f"Purdue_{role.capitalize()}" if role else "Purdue_Red_Brick"
                assigned_role = role if role else 'brick'
                slot.material = get_or_create_material(mat_name, assigned_role)
                fixed_count += 1
    return fixed_count

print("Color enhancement module defined successfully.")
