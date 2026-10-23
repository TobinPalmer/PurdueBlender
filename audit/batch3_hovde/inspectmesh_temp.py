import bpy
for name in ['HOVD_Portico_Entablature','HOVD_Portico_Cornice','HOVD_Portico_Pediment_Base','HOVD_Portico_Pediment_Crown']:
 o=bpy.data.objects[name]
 print('\n',name,o.type,o.dimensions[:],o.scale[:],o.location[:],o.rotation_euler[:],o.data.name, len(o.data.vertices) if o.type=='MESH' else '')
 if o.type=='MESH':
  print('bounds',[(min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)])
  print('verts', [tuple(round(x,2) for x in v.co) for v in list(o.data.vertices)[:12]])
