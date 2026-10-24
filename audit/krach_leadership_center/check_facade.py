import bpy,json
s=bpy.data.objects['KRCH structural shell | GIS outline']
print('shell mats',[(m.name if m else None) for m in s.data.materials])
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['band','mullion','curtain','continuous horizontal']): print(o.name,o.type,[m.name for m in o.data.materials] if getattr(o.data,'materials',None) else [])
for m in s.data.materials:
 if m and m.use_nodes:
  print('MAT',m.name,[(n.name,n.bl_idname) for n in m.node_tree.nodes])
