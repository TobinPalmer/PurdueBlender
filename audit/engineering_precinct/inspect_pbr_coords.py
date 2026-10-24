import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\foliage_library\engineering_foliage_library.blend'
with bpy.data.libraries.load(p,link=False) as (src,dst): dst.materials=['grass_ground','asphalt_01']
for m in dst.materials:
 print('MATERIAL',m.name)
 for n in m.node_tree.nodes:
  if n.type in ('TEX_COORD','MAPPING','REROUTE'):
   print(n.name,n.type,'input',[(i.name,i.links[0].from_socket.name if i.links else None) for i in n.inputs if i.is_linked])
 for l in m.node_tree.links:
  if l.from_node.type=='TEX_COORD' or l.to_node.type in ('MAPPING','REROUTE'):
   print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
