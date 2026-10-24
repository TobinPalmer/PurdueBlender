import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_american_railway_building_rail_fc0f9a2.blend')
s=bpy.context.scene
print('world',s.world, s.world.use_nodes if s.world else None)
if s.world and s.world.node_tree:
 for n in s.world.node_tree.nodes:
  print(n.type,[(i.name,getattr(i,'default_value',None)) for i in n.inputs if i.name in ('Color','Strength')])
print('lights',[(o.name,o.type,getattr(o.data,'energy',None)) for o in bpy.data.objects if o.type=='LIGHT'])
print('orphan cams',[(o.name,o.type) for o in bpy.data.objects if o.type=='CAMERA'])
