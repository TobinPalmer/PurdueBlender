import bpy

print("--- SHADER NODES & NORMAL INSPECTION ---")
for mat in bpy.data.materials:
    print(f"\nMATERIAL: {mat.name}")
    if not mat.use_nodes:
        print("  (No node tree)")
        continue
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            print(f"  Node: {n.name} ({n.type})")
            for inp in n.inputs:
                if inp.is_linked:
                    link = inp.links[0]
                    print(f"    Input '{inp.name}' linked from {link.from_node.name}.{link.from_socket.name}")
                elif inp.default_value is not None:
                    # check if float, vector, color
                    val = inp.default_value
                    if hasattr(val, '__len__'):
                        val_str = tuple(round(x, 3) for x in val)
                    elif isinstance(val, float):
                        val_str = round(val, 3)
                    else:
                        val_str = val
                    # only print interesting ones
                    if inp.name in ["Base Color", "Metallic", "Roughness", "IOR", "Alpha", "Transmission Weight", "Specular IOR Level", "Emission Color", "Emission Strength"]:
                        print(f"    Input '{inp.name}': {val_str}")
        elif n.type in ['TEX_IMAGE', 'TEX_NOISE', 'BUMP', 'NORMAL_MAP', 'MAPPING', 'TEX_COORD']:
            print(f"  Procedural/Texture Node: {n.name} ({n.type})")

