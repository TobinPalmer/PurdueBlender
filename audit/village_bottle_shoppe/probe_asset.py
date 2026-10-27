import bpy, json, math, os
from mathutils import Vector
path=bpy.data.filepath
scenes=[]
for s in bpy.data.scenes:
    scenes.append({'scene':s.name,'collections':[c.name for c in s.collection.children]})
out={'file':path,'scenes':scenes,'objects':[],'collections':[]}
for c in bpy.data.collections:
    out['collections'].append({'name':c.name,'objects':[o.name for o in c.objects]})
for o in bpy.data.objects:
    if o.type=='MESH':
        pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
        out['objects'].append({'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'materials':[m.name if m else None for m in o.data.materials],'dimensions':list(o.dimensions),'location':list(o.location)})
print('PROBE_JSON='+json.dumps(out))
