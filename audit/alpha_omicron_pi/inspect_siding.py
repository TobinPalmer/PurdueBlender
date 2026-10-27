import bpy
c=bpy.data.collections['Asset_massing_house_970455277_a3fb72a']
for o in c.all_objects:
 if o.name.startswith('AOII_SidingWall'):
  print(o.name, [m.name for m in o.data.materials],len(o.data.uv_layers),len(o.data.polygons))
  if o.data.uv_layers: print('uv0',o.data.uv_layers.active.data[0].uv[:], 'uv10',o.data.uv_layers.active.data[min(10,len(o.data.uv_layers.active.data)-1)].uv[:])
  break
m=bpy.data.materials.get('AOII | warm beige horizontal lap siding')
print('mat',m.name,[(n.name,n.bl_idname) for n in m.node_tree.nodes])
for l in m.node_tree.links: print(l.from_node.name,l.from_socket.name,'=>',l.to_node.name,l.to_socket.name)