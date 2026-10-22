import bpy, os, json
from pathlib import Path

queue_file = Path('materials/review/detailed_queue.json')
queue = json.loads(queue_file.read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

report = {}

for b in all_b:
    b_id = b['id']
    fpath = Path('modular') / b['file']
    if not fpath.exists():
        continue
    bpy.ops.wm.open_mainfile(filepath=str(fpath.resolve()))
    
    col_name = b.get('collection', f"Asset_{b_id}")
    col = bpy.data.collections.get(col_name)
    objs = col.all_objects if col else bpy.data.objects
    
    unassigned_objs = []
    default_mat_objs = []
    
    for o in objs:
        if o.type != 'MESH':
            continue
        if len(o.material_slots) == 0:
            unassigned_objs.append(o.name)
        else:
            for s in o.material_slots:
                if not s.material:
                    unassigned_objs.append(o.name)
                elif s.material.name.lower() in ('material', 'material.001', 'default'):
                    default_mat_objs.append(o.name)

    mats = {}
    for m in bpy.data.materials:
        p = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.node_tree else None
        has_tex = any(n.type == 'TEX_IMAGE' for n in m.node_tree.nodes) if m.node_tree else False
        base_col = list(p.inputs['Base Color'].default_value) if p and 'Base Color' in p.inputs else list(m.diffuse_color)
        mats[m.name] = {
            'base_color': [round(x, 3) for x in base_col],
            'has_tex': has_tex,
            'users': m.users
        }
        
    report[b_id] = {
        'total_mesh_objects': len([o for o in objs if o.type == 'MESH']),
        'unassigned_count': len(unassigned_objs),
        'unassigned_sample': unassigned_objs[:5],
        'default_mat_count': len(default_mat_objs),
        'default_mat_sample': default_mat_objs[:5],
        'materials': mats
    }

out_p = Path('scratch/deep_material_audit.json')
out_p.write_text(json.dumps(report, indent=2))
print("Deep audit complete!")
