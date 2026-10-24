import bpy
import json
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
MODULAR = ROOT / 'modular'
manifest = json.loads((MODULAR / 'manifest.json').read_text(encoding='utf-8'))
TEXTURE_TYPES = {
    'TEX_IMAGE', 'TEX_NOISE', 'TEX_VORONOI', 'TEX_BRICK', 'TEX_WAVE',
    'TEX_CHECKER', 'TEX_MAGIC', 'TEX_WHITE_NOISE', 'TEX_GABOR',
    'TEX_ENVIRONMENT',
}

def connected_texture_types(material):
    if not material or not material.use_nodes or not material.node_tree:
        return []
    tree = material.node_tree
    inputs = {node for node in tree.nodes if node.type == 'BSDF_PRINCIPLED'}
    inputs.update(node for node in tree.nodes if node.type == 'OUTPUT_MATERIAL')
    visited = set()
    found = set()
    stack = list(inputs)
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        if node.type in TEXTURE_TYPES:
            found.add(node.type)
        for link in tree.links:
            if link.to_node == node:
                stack.append(link.from_node)
    return sorted(found)

results = []
for asset in manifest['assets']:
    if asset.get('kind') not in {'detailed', 'massing'}:
        continue
    path = (MODULAR / asset['file']).resolve()
    try:
        with bpy.data.libraries.load(str(path), link=True) as (src, dst):
            dst.materials = list(src.materials)
        records = []
        loaded = list(dst.materials)
        for mat in loaded:
            if mat is None:
                continue
            textures = connected_texture_types(mat)
            records.append({
                'name': mat.name,
                'texture_nodes': textures,
                'has_connected_texture': bool(textures),
            })
        results.append({
            'id': asset['id'],
            'kind': asset['kind'],
            'file': asset['file'],
            'collection': asset['collection'],
            'material_count': len(records),
            'materials': records,
            'has_any_texture': any(item['has_connected_texture'] for item in records),
            'untextured_materials': [item['name'] for item in records if not item['has_connected_texture']],
        })
        for mat in loaded:
            if mat is not None and mat.users == 0:
                try:
                    bpy.data.materials.remove(mat)
                except (RuntimeError, TypeError):
                    pass
    except Exception as exc:
        results.append({'id': asset['id'], 'kind': asset['kind'], 'file': asset['file'], 'error': repr(exc)})

out = ROOT / 'audit' / 'asset_material_texture_scan.json'
out.write_text(json.dumps(results, indent=2), encoding='utf-8')
summary = {
    'asset_count': len(results),
    'scan_errors': [r for r in results if r.get('error')],
    'no_connected_texture_asset_count': sum(1 for r in results if not r.get('error') and not r.get('has_any_texture')),
    'no_connected_texture_assets': [r['id'] for r in results if not r.get('error') and not r.get('has_any_texture')],
    'assets_with_untextured_material_count': sum(1 for r in results if r.get('untextured_materials')),
    'asset_count_by_kind': {kind: sum(1 for r in results if r.get('kind') == kind) for kind in ('detailed', 'massing')},
}
print(json.dumps(summary))
