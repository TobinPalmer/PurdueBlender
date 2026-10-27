import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/massing_house_301841610_b6ad6ed.blend')
for s in bpy.data.scenes:
 print(s.name,[(o.name,o.type,list(o.location)) for o in s.objects if o.name not in {x.name for x in bpy.data.collections['Asset_massing_house_301841610_b6ad6ed'].objects}][:40])
 print('world',s.world.name if s.world else None,'color',list(s.world.color) if s.world else None,'nodes',s.world.use_nodes if s.world else None)
