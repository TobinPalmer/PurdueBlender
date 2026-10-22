import bpy, os, json
from pathlib import Path

queue_file = Path('materials/review/detailed_queue.json')
queue = json.loads(queue_file.read_text())
extra = [
    {"id": "dudley_hall", "file": "buildings/dudley_hall.blend", "collection": "Asset_dudley_hall"},
    {"id": "lambertus_hall", "file": "buildings/lambertus_hall.blend", "collection": "Asset_lambertus_hall"}
]
all_b = queue + extra

all_unassigned = {}

for b in all_b:
    b_id = b['id']
    fpath = Path('modular') / b['file']
    if not fpath.exists():
        continue
    bpy.ops.wm.open_mainfile(filepath=str(fpath.resolve()))
    col = bpy.data.collections.get(b.get('collection', f"Asset_{b_id}"))
    objs = col.all_objects if col else bpy.data.objects
    
    unassigned = []
    for o in objs:
        if o.type != 'MESH':
            continue
        if len(o.material_slots) == 0 or any(s.material is None for s in o.material_slots):
            unassigned.append(o.name)
    if unassigned:
        all_unassigned[b_id] = unassigned

print("Summary of unassigned meshes:")
for b_id, objs in all_unassigned.items():
    print(f"=== {b_id}: {len(objs)} objects ===")
    print("   ", objs[:10])

Path('scratch/all_unassigned_details.json').write_text(json.dumps(all_unassigned, indent=2))
