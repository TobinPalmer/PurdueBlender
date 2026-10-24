import bpy, json
objs=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name=='AssetRoot_mccutcheon_hall':
  b=[o.matrix_world @ __import__('mathutils').Vector(v) for v in o.bound_box]
  mins=[min(v[i] for v in b) for i in range(3)]; maxs=[max(v[i] for v in b) for i in range(3)]
  objs.append({'name':o.name,'z':[round(mins[2],3),round(maxs[2],3)],'xy':[[round(mins[0],3),round(maxs[0],3)],[round(mins[1],3),round(maxs[1],3)]],'mats':[m.name for m in o.data.materials]})
print('MCUT_OBJECTS='+json.dumps(sorted(objs,key=lambda x:x['z'][1],reverse=True)))
