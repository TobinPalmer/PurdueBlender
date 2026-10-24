import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend')
for name in ['LSPS | warm gray limestone / precast','LSPS | mottled Purdue red-brown brick']:
 m=bpy.data.materials[name]; print('\n',name)
 for n in m.node_tree.nodes:
  print(n.type,n.name)
