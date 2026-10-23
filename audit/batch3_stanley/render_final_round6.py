import bpy,os
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';d=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=p);sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1500;sc.render.resolution_y=850;sc.render.resolution_percentage=80;sc.eevee.taa_render_samples=64
for nm in ['Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_06_Interior_Schematic']:
 sc.camera=bpy.data.objects[nm];sc.render.filepath=os.path.join(d,nm+'_final.png');bpy.ops.render.render(write_still=True);print('render',nm)
