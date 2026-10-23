import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for mn in ['Bedford_Indiana_Limestone','Limestone_WaterTable_Cap','Paving_Concrete','Purdue_Red_Brick_Procedural','Architectural_Glazing','Historic_Slate_Roof_Procedural']:
 m=bpy.data.materials.get(mn);print('\nMAT',mn,'color',tuple(m.diffuse_color),'nodes',m.use_nodes)
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type in ('BSDF_PRINCIPLED','VALTORGB','TEX_NOISE','TEX_BRICK','TEX_COORD','MAPPING'):
    print(n.name,n.type,[(s.name,tuple(s.default_value) if hasattr(s,'default_value') and hasattr(s.default_value,'__len__') else s.default_value) for s in n.inputs if s.name in ('Base Color','Roughness','Metallic','Alpha')])
    for out in n.outputs:
     print(' out',out.name,[(l.to_node.name,l.to_socket.name) for l in out.links])
