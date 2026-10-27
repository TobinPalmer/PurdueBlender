import bpy,json
p='modular/buildings/massing_house_301841603_654031c.blend'; bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
print('SCENE',sc.name)
for c in bpy.data.collections:
 if c.name.startswith('Asset_'):
  print('COL',c.name, 'objs',[(o.name,o.type,list(o.dimensions)) for o in c.objects])
for o in bpy.data.objects:
 if o.name=='House_301841603': print('OBJ',o.name, o.type, list(o.location), list(o.dimensions), list(o.rotation_euler),len(o.data.vertices) if o.type=='MESH' else '')
