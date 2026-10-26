import bpy,json
for o in bpy.data.objects:
 if any(s in o.name.lower() for s in ['interior_floor','stair','room','column','gallery','commons','study']):
  pts=[o.matrix_world @ v.co for v in o.data.vertices] if o.type=='MESH' else []
  b=[[round(min(v[i] for v in pts),2),round(max(v[i] for v in pts),2)] for i in range(3)] if pts else None
  print(o.name,'dims',tuple(round(x,2) for x in o.dimensions),'loc',tuple(round(x,2) for x in o.matrix_world.translation),'bounds',b)
