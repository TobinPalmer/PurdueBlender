import bpy, os
from mathutils import Vector
base=r'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=75
sc.eevee.taa_render_samples=32
for c in bpy.data.collections:
 if c.name.startswith('Reference_Incompatible'): c.hide_render=True
for nm in ['Cam_SC_01_Footprint_TopDown','Cam_SC_02_MemorialMall_East_Hero','Cam_SC_03_East_Portico_Ground','Cam_SC_04_South_Courtyard_Perspective','Cam_SC_05_West_OvalDrive_Hero']:
 cam=bpy.data.objects.get(nm)
 if not cam: continue
 sc.camera=cam
 sc.render.filepath=os.path.join(base,nm+'.png')
 bpy.ops.render.render(write_still=True)
 print('RENDERED',nm,sc.render.filepath)
