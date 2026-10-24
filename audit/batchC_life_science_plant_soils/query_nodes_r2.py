import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for name in ['LSPS | mottled Purdue red-brown brick','LSPS | schematic clear facade glazing','LSPS | greenhouse clear glazing']:
 m=bpy.data.materials[name]; print('\n',name)
 for n in m.node_tree.nodes:
  ins={}
  for i in n.inputs:
   if i.name in ['Scale','Detail','Roughness','Distortion','Strength','Distance','Fac','Color1','Color2','Mortar','Mortar Size','Mortar Smooth','Brick Width','Row Height','Offset','Offset Frequency','Base Color','Roughness','Metallic']:
    v=i.default_value
    try:v=tuple(round(float(x),4) for x in v)
    except: pass
    ins[i.name]=v
  print(n.type,ins)
