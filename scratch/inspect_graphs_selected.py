import bpy, os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
for fn in ['math_sciences.blend','neil_armstrong_hall.blend','owen_hall.blend','purdue_memorial_union.blend','ross_ade.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn)); print('\n##',fn)
 for m in bpy.data.materials:
  if not m.use_nodes: continue
  p=m.node_tree.nodes.get('Principled BSDF')
  if not p: continue
  if any(x in m.name.lower() for x in ['brick','limestone','concrete','membrane','roof','glass','granite','slate','metal','aluminum','steel','terrazzo','paver','parquet']):
   vals={k:round(p.inputs[k].default_value,3) for k in ['Roughness','Metallic']}
   print('\n',m.name,vals)
   for n in m.node_tree.nodes:
    if n.type in {'TEX_NOISE','TEX_BRICK','BUMP','TEX_COORD'}:
     outs=[(l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links if l.from_node==n]
     ins=[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in m.node_tree.links if l.to_node==n]
     print(' ',n.name,n.type,{i.name:round(i.default_value,4) for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int))},'in',ins,'out',outs)
