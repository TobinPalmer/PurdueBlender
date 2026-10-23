import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
info={'collections':[], 'keywords':[]}
for c in bpy.data.collections:
 if any(t in c.name.lower() for t in ['atrium','interior','floor','bridge','roof','rawls']):info['collections'].append({'name':c.name,'objects':len(c.objects),'total':len(c.all_objects)})
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['atrium','bridge','stair','staircase','rail','interior','roof','floor','glaze']):
  if o.type=='MESH':
   corners=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
   bb=[[round(min(p[i] for p in corners),2),round(max(p[i] for p in corners),2)] for i in range(3)]
  else:bb=None
  info['keywords'].append([o.name,o.type,bb])
print(json.dumps(info,indent=2))
