import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/burton_morgan_center.blend')
c=bpy.data.collections['Asset_burton_morgan_center']
for o in c.all_objects:
 if 'GIS perimeter' in o.name or o.type=='MESH' and o.name in list(c.all_objects)[:3]:
  print(o.name, list(o.keys()))
print('first',[(o.name,o.type) for o in list(c.all_objects)[:8]])
