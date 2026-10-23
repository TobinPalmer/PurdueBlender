import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for name in ['Purdue_Red_Brick','Bedford_Indiana_Limestone']:
 m=bpy.data.materials[name];print('\n',name)
 for n in m.node_tree.nodes:
  if n.bl_idname=='ShaderNodeTexBrick':print(n.name,'col1',tuple(n.inputs['Color1'].default_value),'col2',tuple(n.inputs['Color2'].default_value),'mortar',tuple(n.inputs['Mortar'].default_value))
  if n.bl_idname=='ShaderNodeValToRGB':print(n.name,[(e.position,tuple(e.color)) for e in n.color_ramp.elements])
