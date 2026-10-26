import bpy, os
from mathutils import Vector
from pathlib import Path
base=Path(r'audit/batch3_stanley').resolve(); asset=Path(r'modular/buildings/stanley_coulter_hall.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1500;s.render.resolution_y=850;s.render.resolution_percentage=80;s.eevee.taa_render_samples=80
for nm,fn in [('Cam_SC_02_MemorialMall_East_Hero','SC_hero_r4.png'),('Cam_SC_03_East_Portico_Ground','SC_entry_r4.png')]:
 s.camera=bpy.data.objects[nm];s.render.filepath=str(base/fn);bpy.ops.render.render(write_still=True)
# Temporary cutaway: show full piano-nobile floor plate and the graduate-hub, reception, and research furnishings.
s.camera=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam=s.camera
cam.location=(34,-25,24);target=Vector((22,-7,2.0));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=20
for cn in ['SC_Exterior_Structure','SC_Fenestration','SC_Roof_and_Dormers','SC_Portico_and_Entrances','SC_Plaza_and_Site']:
 for o in bpy.data.collections[cn].objects:o.hide_render=True
for o in bpy.data.collections['SC_Interior_Shell'].objects:
 keep=o.name.startswith(('SC_Shell_Floor_1','SC_GradHub_','SC_ResearchStool_','SC_ResearchMonitor_','SC_ResearchBookTray_')) or o.name in ('SC_Lobby_Terrazzo_Floor','SC_Lobby_Reception_Desk','SC_Lobby_Staircase_Shell','SC_ResearchBench_0','SC_ResearchBench_Cabinet_0','SC_ResearchBench_1','SC_ResearchBench_Cabinet_1')
 if not keep:o.hide_render=True
s.render.filepath=str(base/'SC_interior_schematic_r4.png');bpy.ops.render.render(write_still=True)
print('Wrote R4 exterior, entrance, and focused piano-nobile cutaway renders; room layout is schematic.')
