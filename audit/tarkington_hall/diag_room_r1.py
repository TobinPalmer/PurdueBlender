import bpy
from mathutils import Vector
for name in ['Tark_Dorm_Room118_Floor','Tark_Dorm_Room118_Wall_E','Tark_Dorm_Bed_Frame_0','Tark_Dorm_Desk_0']:
 o=bpy.data.objects.get(name)
 print(name, bool(o), 'hide_render',o.hide_render if o else None,'hide_viewport',o.hide_viewport if o else None,'collections',[c.name for c in o.users_collection] if o else [],'worldloc',tuple(o.matrix_world.translation) if o else None,'parent',o.parent.name if o and o.parent else None)
cam=bpy.data.objects.get('TarkRoom_Camera');print('cam',cam,'loc',cam.location if cam else None,'rot',cam.rotation_euler if cam else None,'matrixloc',cam.matrix_world.translation if cam else None)
if cam:
 d=cam.matrix_world.to_3x3()@Vector((0,0,-1));print('dir',d)
 hit=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.matrix_world.translation,d)
 print('ray',hit[0],hit[3].name if hit[0] else None,hit[1])
print('excluded',[(l.name,l.exclude,l.hide_viewport) for l in bpy.context.view_layer.layer_collection.children])
