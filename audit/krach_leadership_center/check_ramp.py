import bpy
m=bpy.data.materials['KRACH_LEADERSHIP_CENTER | evidence palette textured masonry']
for n in m.node_tree.nodes:
 if n.bl_idname=='ShaderNodeValToRGB': print(n.name,[(e.position,tuple(e.color)) for e in n.color_ramp.elements])
