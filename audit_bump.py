import bpy, os
p=os.path.abspath(r'modular/buildings/felix_haas_hall.blend')
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
print('camera',sc.camera.name if sc.camera else None,'engine',sc.render.engine,'res',sc.render.resolution_x,sc.render.resolution_y)
for m in bpy.data.materials:
 if m.node_tree:
  b=next((n for n in m.node_tree.nodes if n.get('codex_surface_detail')),None)
  if b:
   print(m.name,'bump',b.inputs['Strength'].default_value,b.inputs['Distance'].default_value)
   for l in m.node_tree.links:
    if l.to_node==b: print(' height from',l.from_node.name,l.from_socket.name)
