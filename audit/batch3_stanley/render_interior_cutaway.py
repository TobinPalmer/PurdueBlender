import bpy,os
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';d=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene;cam=bpy.data.objects['Cam_SC_06_Interior_Schematic']
cam.location=(22.4,-7.5,24);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=13;s.camera=cam
# presentation-only cutaway: preserve source geometry and saved visibility state
for coln in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Portico_and_Entrances','SC_Plaza_and_Site']:
 c=bpy.data.collections[coln]
 for o in c.objects: o.hide_render=True
for o in bpy.data.collections['SC_Interior_Shell'].objects:
 if not (o.name.startswith('SC_Shell_Floor_1') or o.name.startswith('SC_GradHub_')): o.hide_render=True
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1500;s.render.resolution_y=850;s.render.resolution_percentage=80;s.eevee.taa_render_samples=64;s.render.filepath=os.path.join(d,'Cam_SC_06_Interior_Schematic_cutaway.png');bpy.ops.render.render(write_still=True);print('saved cutaway image')
