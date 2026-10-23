import bpy, json, math, os
p=r'modular/buildings/stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
  rows.append({'name':o.name,'coll':[c.name for c in o.users_collection],'verts':len(o.data.vertices),'dims':list(o.dimensions),'loc':list(o.location),'bounds':[[min(v[i] for v in bb) for i in range(3)],[max(v[i] for v in bb) for i in range(3)]],'mats':[m.name if m else None for m in o.data.materials]})
print('SCENE',bpy.context.scene.name,'COLLECTIONS',[(c.name,len(c.objects)) for c in bpy.data.collections])
print('OBJECTS',len(bpy.data.objects),'MESH',len(rows),'MATERIALS',[(m.name,m.diffuse_color[:]) for m in bpy.data.materials])
print(json.dumps(rows,indent=2))
