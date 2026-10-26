import bpy, json
from pathlib import Path
from mathutils import Vector
asset=bpy.data.collections['Asset_walc']
items=[]
for o in sorted(asset.all_objects,key=lambda x:x.name):
    if not o.name.startswith('WALC_Source906_Edge_'): continue
    if o.type!='MESH': continue
    corners=[o.matrix_world@Vector(c) for c in o.bound_box]
    bounds=[[min(p[i] for p in corners),max(p[i] for p in corners)] for i in range(3)]
    items.append({'name':o.name,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'bounds':bounds,'materials':[s.material.name if s.material else None for s in o.material_slots],'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection]})
path=Path(__file__).with_name('walc_facade_objects_r3.json')
path.write_text(json.dumps(items,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(items),'examples':items[:10],'output':str(path)},indent=2))
