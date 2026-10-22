import bpy

bpy.ops.wm.open_mainfile(filepath='modular/buildings/stanley_coulter_hall.blend')
for m in bpy.data.materials:
    if 'Brick' in m.name or 'Limestone' in m.name or 'Slate' in m.name:
        print(f"Material: {m.name}")
        for n in m.node_tree.nodes:
            print(f"   Node: {n.name} ({n.type})")
            if n.type == 'TEX_BRICK':
                print(f"      Brick colors: col1={list(n.inputs['Color1'].default_value)}, col2={list(n.inputs['Color2'].default_value)}, mortar={list(n.inputs['Mortar'].default_value)}")
            elif n.type == 'BSDF_PRINCIPLED':
                print(f"      Base color: {list(n.inputs['Base Color'].default_value)}")
