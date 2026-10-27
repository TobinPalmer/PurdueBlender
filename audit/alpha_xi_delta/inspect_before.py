import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841248_fe939c7.blend')
for c in bpy.data.collections:
 if c.name=='Asset_massing_house_301841248_fe939c7':
  print('COL',c.name,len(c.objects))
  for o in c.objects: print(o.name,o.type,list(o.location),list(o.dimensions),len(o.data.vertices) if o.type=='MESH' else '')
