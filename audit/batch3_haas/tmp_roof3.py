import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
for n in m.node_tree.nodes:
 if n.type=='TEX_BRICK':
  for k in ['Color1','Color2','Mortar']:
   print(k,list(n.inputs[k].default_value))
