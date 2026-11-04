import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).parent
asset=bpy.data.collections['Asset_mechanical_engineering']
rows=[]
for ob in asset.all_objects:
    pts=[ob.matrix_world@Vector(c) for c in ob.bound_box] if ob.type in {'MESH','FONT'} else [ob.location]
    rows.append({'name':ob.name,'type':ob.type,'location':list(ob.location),'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'vertices':len(ob.data.vertices) if ob.type=='MESH' else 0})
(out/'asset_inventory.json').write_text(json.dumps(rows,indent=2))
print('OBJECTS',len(rows));print(json.dumps([r for r in rows if any(x in r['name'] for x in ['Arch','Portal','Entry','Roof','Envelope','Root','Window_Glazing','Facade_Window'])],indent=2))
