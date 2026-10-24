import bpy,os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
files=['rawls_hall.blend','stanley_coulter_hall.blend','wiley_hall.blend','winifred_parker_hall.blend','benjamin_harrison_hall.blend']
for fn in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn)); print('\n###',fn)
 for m in bpy.data.materials:
  if not m.use_nodes: continue
  s=m.name.lower()
  if not any(k in s for k in ['stone','limestone','concrete','roof','membrane','glass','glazing','metal','steel','aluminum','bronze','terrazzo','paver','brick','asphalt','walk','spandrel','lawn','granite']): continue
  p=m.node_tree.nodes.get('Principled BSDF');
  if not p: continue
  print(m.name,'rough',round(p.inputs['Roughness'].default_value,3),'metal',round(p.inputs['Metallic'].default_value,3),'base_link',any(l.to_node==p and l.to_socket.name=='Base Color' for l in m.node_tree.links))
  for n in m.node_tree.nodes:
   if n.type in {'TEX_COORD','TEX_NOISE','TEX_BRICK','BUMP','MAPPING'}:
    ins=[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in m.node_tree.links if l.to_node==n]
    out=[(l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links if l.from_node==n]
    vals={i.name:round(i.default_value,5) for i in n.inputs if i.name in ['Scale','Strength','Distance','Detail'] and hasattr(i,'default_value')}
    print(' ',n.name,n.type,vals,'in',ins,'out',out)
