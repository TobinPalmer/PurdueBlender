import bpy
for mn in ['Purdue_Red_Brick','Purdue_Red_Brick.001','HAAS_GooglePhotos_RedClayTiles_estimated','HAAS_R6_Red_Brick_Inlay','HAAS_Photo_Limestone']:
 m=bpy.data.materials.get(mn)
 if m and m.node_tree:
  print('\nMAT',mn,m.diffuse_color[:])
  for n in m.node_tree.nodes:
   print(n.name,n.type,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value) for i in n.inputs if i.name in ['Base Color','Color','Color1','Color2','Mortar','Roughness','Scale']])
