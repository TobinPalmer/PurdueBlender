import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
s=bpy.context.scene
for n in ['KNOY_L2_TypicalPlan_InteriorPartitions','KNOY_TypicalPlanCamera','KNOY_TypicalPlanRender_Sun','KNOY_TypicalPlanRender_Ground']:
 o=bpy.data.objects.get(n); print('OBJ',n,o and o.hide_render,o and tuple(round(v,2) for v in o.location),o and tuple(round(v,2) for v in o.dimensions))
print('cam before',s.camera and s.camera.name,s.camera and tuple(s.camera.rotation_euler))
if s.camera:print('direction',s.camera.matrix_world.to_3x3()@Vector((0,0,-1)))
