import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');m=bpy.data.materials['RAWL_CurtainWall_Glass'];
for l in m.node_tree.links: print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for o in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 ob=bpy.data.objects[o];print(o,'hide',ob.hide_render, 'parent',ob.parent.name if ob.parent else None, 'collections',[c.name for c in ob.users_collection]);
