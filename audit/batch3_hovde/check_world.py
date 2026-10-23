import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');w=bpy.context.scene.world;print('world',w.use_nodes,w.color[:]);
for n in w.node_tree.nodes: print(n.name,n.bl_idname,tuple(n.inputs['Color'].default_value) if 'Color' in n.inputs else '',n.inputs['Strength'].default_value if 'Strength' in n.inputs else '')
