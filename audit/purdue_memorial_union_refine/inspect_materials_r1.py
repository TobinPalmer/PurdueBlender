import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
col=bpy.data.collections['Asset_purdue_memorial_union']
for name in ['PMU_Gothic_Win_Glass_0','PMU_Gothic_Win_Hood_0','PMU_Gothic_Win_Lintel_0','PMU_Tower_Gothic_Window_Glass','PMU_Tower_Window_Head','PMU_Tower_Portal_Pillar_W']:
 o=bpy.data.objects.get(name)
 if not o: print(name,'MISSING'); continue
 print(name,'mats',[m.name for m in o.data.materials],'verts',len(o.data.vertices) if o.type=='MESH' else '-', 'faces',len(o.data.polygons) if o.type=='MESH' else '-')
 for mat in o.data.materials:
  print('  ',mat.name,'color',tuple(round(x,3) for x in mat.diffuse_color))
