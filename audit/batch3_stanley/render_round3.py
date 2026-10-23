import bpy,os,json
from mathutils import Vector
base=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley';p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p);sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1500;sc.render.resolution_y=850;sc.render.resolution_percentage=75;sc.eevee.taa_render_samples=48
for c in bpy.data.collections:
 if c.name.startswith('Reference_Incompatible'):c.hide_render=True
for nm in ['Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground']:
 sc.camera=bpy.data.objects[nm];sc.render.filepath=os.path.join(base,nm+'_round3.png');bpy.ops.render.render(write_still=True)
# Interior-only schematic view for evidence. Exterior and upper floors are hidden only for this render.
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Portico_and_Entrances','SC_Roof_and_Dormers','SC_Plaza_and_Site']:
 c=bpy.data.collections.get(cn)
 if c:c.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('SC_Shell_Floor_'):o.hide_render=True
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam.data.type='ORTHO';cam.data.ortho_scale=16.0
cam.location=(23,-7,18);cam.rotation_euler=(Vector((23,-7,1.9))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
sc.render.filepath=os.path.join(base,'Cam_SC_06_Interior_Schematic_round3.png');bpy.ops.render.render(write_still=True)
print('DONE')
