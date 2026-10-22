import bpy

brick_mat = bpy.data.materials.get("Mat_HIKS_Purdue_Red_Brick")
if brick_mat and brick_mat.node_tree:
    print("Brick Material Nodes:")
    for n in brick_mat.node_tree.nodes:
        print(f"  {n.name} ({n.type})")
        if n.type == 'TEX_BRICK':
            for inp in n.inputs:
                print(f"    {inp.name}: {inp.default_value}")
