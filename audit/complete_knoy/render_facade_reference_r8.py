import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene
for n in ['Cam_KNOY_02_Grant_Street_East','Cam_KNOY_02_Grant_Street_East.001','Cam_KNOY_04_South_Plaza_Elevation']:
 c=bpy.data.objects.get(n)
 if c:
  print('CAM',n,tuple(c.location),tuple(c.rotation_euler),c.data.type,c.data.lens)
  s.camera=c;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1280;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\facade_material_review_r8_'+n.replace('.','_')+'.png'
  bpy.ops.render.render(write_still=True)

