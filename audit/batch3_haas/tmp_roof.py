import bpy
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated']
for n in m.node_tree.nodes:
 print(n.name,n.type)
 if n.type=='TEX_BRICK':
  for k in ['Color1','Color2','Mortar','Scale','Mortar Size','Mortar Smooth','Bias','Brick Width','Row Height']:
   if k in n.inputs: print(k,n.inputs[k].default_value)
 if n.type=='BUMP':print('bump',n.inputs['Strength'].default_value,n.inputs['Distance'].default_value)
