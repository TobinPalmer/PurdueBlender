import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['Hovde_Roof_Membrane','Purdue_Red_Brick']:
 m=bpy.data.materials[n];print(n,'diff',tuple(m.diffuse_color))
 for x in m.node_tree.nodes:
  if x.bl_idname=='ShaderNodeTexBrick': print(x.name, tuple(x.inputs['Color1'].default_value),tuple(x.inputs['Color2'].default_value),tuple(x.inputs['Mortar'].default_value))
  if x.bl_idname=='ShaderNodeBsdfPrincipled': print('BS',tuple(x.inputs['Base Color'].default_value))
for n in ['HOVD_Roof_Slab','HOVD_Inferred_Hipped_Roof']:
 o=bpy.data.objects[n]; print(n,[(m.name if m else None) for m in o.data.materials],o.hide_render)
