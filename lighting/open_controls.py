import bpy
import campus_time
campus_time.register()
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.show_region_ui=True
  a.spaces.active.shading.type='MATERIAL'
  a.spaces.active.shading.use_scene_world=True
  a.spaces.active.shading.use_scene_lights=True
try:bpy.ops.blendermcp.start_server()
except Exception as e:print('Control connection:',e)
print('Campus Sky panel ready; time',bpy.context.scene.get('campus_time'))
