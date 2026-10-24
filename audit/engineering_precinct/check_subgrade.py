import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if 'Subgrade' in o.name:
  print('OBJECT',o.name,'hide',o.hide_render,'loc',tuple(o.location),'materials',[m.name for m in o.data.materials])
  for p in o.data.polygons: print('POLYGON',p.normal[:],p.area,p.material_index)
print('collection objects',len(bpy.data.collections['Engineering_Mall_Groundwork_Patch'].objects))
