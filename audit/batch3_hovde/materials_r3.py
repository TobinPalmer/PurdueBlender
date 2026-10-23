import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend');
for n in ['Purdue_Red_Brick','Bedford_Indiana_Limestone','Hovde_Roof_Membrane','Solar_Ribbon_Glass','Hovde_Plaster_Ivory']:
 m=bpy.data.materials[n];print(n,'diff',tuple(m.diffuse_color),'nodes',m.use_nodes)
 if m.use_nodes:
  b=m.node_tree.nodes.get('Principled BSDF');print(' bs',tuple(b.inputs['Base Color'].default_value) if b else None,'rough',b.inputs['Roughness'].default_value if b else None)
