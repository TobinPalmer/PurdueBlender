import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/university_hall.blend'
collection=bpy.data.collections['Asset_university_hall']
names=sorted([{'name':o.name,'type':o.type,'location':[round(v,4) for v in o.location],'dimensions':[round(v,4) for v in o.dimensions],'collections':[c.name for c in o.users_collection]} for o in collection.all_objects],key=lambda x:x['name'])
(root/'audit/university_hall_refine/object_inventory.json').write_text(json.dumps(names,indent=2)+'\n',encoding='utf-8')
print('objects',len(names))
print('\n'.join(x['name'] for x in names if any(k in x['name'].lower() for k in ('wall','floor','roof','tower','window','stair','door','interior','room','foundation','masonry','cornice'))))
