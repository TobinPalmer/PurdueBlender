import bpy
ob=bpy.data.objects.get('Campus Sunset Sky Dome');print('FLAGS',ob.hide_render,ob.visible_camera,ob.visible_diffuse,ob.visible_glossy,ob.visible_transmission,ob.visible_shadow,ob.type,ob.parent,[c.name for c in ob.users_collection])
for link in ob.data.materials[0].node_tree.links: print('LINK',link.from_node.name,link.from_socket.name,'->',link.to_node.name,link.to_socket.name)
