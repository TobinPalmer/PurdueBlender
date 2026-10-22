import bpy, os, json
from pathlib import Path

queue_file = Path('materials/review/detailed_queue.json')
queue = json.loads(queue_file.read_text())

# Also add dudley and lambertus if they exist
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

results = {}

for b in all_b:
    blend_path = Path('modular') / b['file']
    if not blend_path.exists():
        continue
    bpy.ops.wm.open_mainfile(filepath=str(blend_path.resolve()))
    mats_info = {}
    for m in bpy.data.materials:
        info = {
            'use_nodes': m.use_nodes,
            'diffuse': list(m.diffuse_color),
        }
        if m.node_tree:
            p = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if p:
                base_col = list(p.inputs['Base Color'].default_value)
                rough = p.inputs['Roughness'].default_value
                info['base_color'] = base_col
                info['roughness'] = rough
                info['has_pbr_image'] = any(n.type == 'TEX_IMAGE' for n in m.node_tree.nodes)
                info['has_bump'] = any(n.type == 'BUMP' for n in m.node_tree.nodes)
        mats_info[m.name] = info
    results[b['id']] = {
        'total_materials': len(bpy.data.materials),
        'materials': mats_info,
        'object_count': len(bpy.data.objects)
    }

output_path = Path('scratch/building_materials_summary.json')
output_path.write_text(json.dumps(results, indent=2))
print(f"Summary written for {len(results)} buildings.")
