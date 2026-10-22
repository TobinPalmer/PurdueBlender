import bpy

bpy.ops.wm.open_mainfile(filepath='modular/buildings/wiley_hall.blend')
brick_mats = [m for m in bpy.data.materials if 'brick' in m.name.lower() or 'masonry' in m.name.lower()]
print(f"Brick materials in Wiley Hall: {[m.name for m in brick_mats]}")

for m in brick_mats[:5]:
    print(f"\n==================== Material: {m.name} ====================")
    if not m.node_tree:
        print("No node tree!")
        continue
    for n in m.node_tree.nodes:
        print(f"Node: {n.name} ({n.type})")
        if n.type == 'TEX_IMAGE' and n.image:
            print(f"   Image: {n.image.name}, filepath: {n.image.filepath}, colorspace: {n.image.colorspace_settings.name}")
        elif n.type == 'MAPPING':
            print(f"   Mapping scale: {list(n.inputs['Scale'].default_value)}")
        elif n.type == 'TEX_COORD':
            print(f"   TexCoord outputs: {[o.name for o in n.outputs]}")
    for link in m.node_tree.links:
        print(f"   Link: {link.from_node.name}.{link.from_socket.name} -> {link.to_node.name}.{link.to_socket.name}")
