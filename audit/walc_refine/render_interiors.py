import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]; out=root/'audit/walc_refine'; scene=bpy.data.scenes['Building_walc']
scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='outdoor.sl'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.background_type='WORLD'; scene.display.shading.show_shadows=False; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'; scene.display.shading.curvature_ridge_factor=0.8; scene.display.shading.curvature_valley_factor=0.35
scene.world=scene.world or bpy.data.worlds.new('WALC_Review'); scene.world.color=(.72,.75,.8)
for name in ['03 Reading room reference','04 Atrium reference','05 Atrium stairs','06 Library stacks','07 Hiler theatre','08 Active learning','09 Basement']:
 cam=bpy.data.objects.get(name)
 if not cam or cam.type!='CAMERA': print('MISSING',name); continue
 scene.camera=cam
 scene.render.filepath=str(out/(name.lower().replace(' ','_')+'.png'))
 bpy.ops.render.render(write_still=True)
print('Rendered existing saved inspection cameras.')
