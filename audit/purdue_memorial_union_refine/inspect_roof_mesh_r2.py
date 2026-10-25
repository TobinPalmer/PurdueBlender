import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\purdue_memorial_union.blend')
col=bpy.data.collections['Asset_purdue_memorial_union']
for n in ['PMU_Roof_North_Wing','PMU_Roof_East_Wing','PMU_Roof_West_Wing','PMU_Roof_South_Wing','PMU_EastWing_Roof_Slab']:
 o=bpy.data.objects.get(n)
 if not o: continue
 print('\n',n,'v',len(o.data.vertices),'f',len(o.data.polygons),'mat',[m.name for m in o.data.materials])
 for v in o.data.vertices:
  print(tuple(round(a,2) for a in (o.matrix_world@v.co)))
