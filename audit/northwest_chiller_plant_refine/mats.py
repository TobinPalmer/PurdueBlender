import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/northwest_chiller_plant.blend')
for name in ['northwest_chiller_plant_facade','northwest_chiller_plant_cast_stone','northwest_chiller_plant_painted_metal','northwest_chiller_plant_roofing']:
 m=bpy.data.materials[name]; print('\n',name,'diffuse',tuple(round(x,3) for x in m.diffuse_color),'nodes',m.use_nodes)
 if m.use_nodes:
  for n in m.node_tree.nodes:
   print(n.type,n.name,{i.name:(tuple(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if i.name in ('Scale','Color1','Color2','Mortar','Base Color','Roughness','Distance','Strength')})
