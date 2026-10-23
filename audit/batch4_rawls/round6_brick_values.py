import bpy
m=bpy.data.materials['RAWL_Purdue_Red_Brick']
for n in m.node_tree.nodes:
 if n.type=='TEX_BRICK':
  print(n.name,{s.name:list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value for s in n.inputs if s.name in ['Color1','Color2','Mortar','Mortar Size','Brick Width','Row Height']})
