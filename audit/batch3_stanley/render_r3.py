import bpy,os
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';d=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1500;s.render.resolution_y=850;s.render.resolution_percentage=80;s.eevee.taa_render_samples=80
for nm,fn in [('Cam_SC_02_MemorialMall_East_Hero','SC_hero_r3.png'),('Cam_SC_03_East_Portico_Ground','SC_entry_r3.png')]:
 s.camera=bpy.data.objects[nm];s.render.filepath=os.path.join(d,fn);bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Cam_SC_06_Interior_Schematic']
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Portico_and_Entrances','SC_Plaza_and_Site']:
 for o in bpy.data.collections[cn].objects:o.hide_render=True
for o in bpy.data.collections['SC_Interior_Shell'].objects:
 if not (o.name.startswith('SC_Shell_Floor_1') or o.name.startswith('SC_GradHub_')):o.hide_render=True
bpy.data.objects['SC_Portico_3D_Text'].hide_render=True
s.render.filepath=os.path.join(d,'SC_interior_cutaway_r3.png');bpy.ops.render.render(write_still=True)
print('R3 validation renders saved')

