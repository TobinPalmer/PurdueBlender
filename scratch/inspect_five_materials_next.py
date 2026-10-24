import bpy, os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
for fn in ['rawls_hall.blend','stanley_coulter_hall.blend','wiley_hall.blend','winifred_parker_hall.blend','benjamin_harrison_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn)); print('\n##',fn,'objs',len(bpy.data.objects))
 mats={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   for s in o.material_slots:
    if s.material: mats[s.material.name]=mats.get(s.material.name,0)+1
 for mn,count in sorted(mats.items()):
  m=bpy.data.materials.get(mn); p=m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
  color=tuple(round(x,2) for x in p.inputs['Base Color'].default_value[:3]) if p else None
  nodes=[]
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type in {'TEX_NOISE','TEX_BRICK','TEX_IMAGE','BUMP','MAPPING','TEX_COORD','MIX_RGB','VALTORGB'}:
     links=[(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name) for l in m.node_tree.links if l.from_node==n or l.to_node==n]
     nodes.append((n.name,n.type,n.inputs.get('Scale').default_value if n.type=='TEX_NOISE' else '',len(links)))
  print(f'{mn} x{count} color={color} custom={nodes}')

