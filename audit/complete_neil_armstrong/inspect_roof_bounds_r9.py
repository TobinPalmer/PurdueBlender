import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
for name in ['ARMS_East_Roof_Slab','ARMS_West_Roof_Slab','ARMS_R5_Coarse_LiDAR_wing_low','ARMS_R5_Coarse_LiDAR_wing_mid','ARMS_R5_Coarse_LiDAR_roof_high']:
 o=bpy.data.objects[name]; vs=[o.matrix_world@v.co for v in o.data.vertices]
 print(name,'loc',list(o.location),'bbox',[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)],'materials',[m.name for m in o.data.materials])
 for p in o.data.polygons:
  if p.normal.z>.75:
   co=p.center; print(' top sample',list(co),o.data.materials[p.material_index].name);break
