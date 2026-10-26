import bpy,json
from mathutils import Vector
s=bpy.context.scene
print('scene',s.name,'engine',s.render.engine,'resolution',s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,'camera',s.camera.name if s.camera else None,'world',s.world.name if s.world else None)
for o in bpy.data.objects:
 if o.type=='CAMERA': print('CAM',o.name,'loc',list(o.location),'rot',list(o.rotation_euler),'lens',o.data.lens,'clip',o.data.clip_start,o.data.clip_end)
if s.world and s.world.use_nodes: print('world nodes',[(n.type,n.name) for n in s.world.node_tree.nodes])
for o in bpy.data.objects:
 if o.type=='MESH':
  mats=[m.name if m else None for m in o.data.materials]
  if not mats or all(x is None for x in mats): print('NOMAT',o.name)
print('mesh material assignments:')
for m in bpy.data.materials:
 if m.users: print(m.name,m.users)
