import bpy
n=bpy.data.node_groups.new('x','ShaderNodeTree') if False else bpy.data.node_groups
m=bpy.data.materials.new('temp'); m.use_nodes=True; sky=m.node_tree.nodes.new('ShaderNodeTexSky')
print('SKY_ATTRS='+str([x for x in dir(sky) if not x.startswith('_')]))
