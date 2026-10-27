import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
p=Path('audit/batch2_hicks/inspection_r2.json')
c=bpy.data.collections['Asset_hicks_library']
def bbox(obj):
 pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
 return [[min(q[i] for q in pts),max(q[i] for q in pts)] for i in range(3)]
result={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'collection':c.name,'object_count':len(c.all_objects),'objects':[],'collections':[]}
for col in bpy.data.collections:
 if col==c or c in col.children_recursive:
  result['collections'].append({'name':col.name,'object_count':len(col.objects)})
for o in c.all_objects:
 result['objects'].append({'name':o.name,'type':o.type,'collections':[x.name for x in o.users_collection],'location':list(o.location),'dimensions':list(o.dimensions),'bounds':bbox(o) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'props':{k:o[k] for k in o.keys() if k!='_RNA_UI'}})
p.write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
