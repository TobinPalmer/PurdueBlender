import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['Historic_Slate_Roof_Procedural','Aged_Copper_Trim','Bedford_Indiana_Limestone','Architectural_Glazing','Dark_Bronze_Framing']:
 m=bpy.data.materials.get(n);print('\nMAT',n,'use nodes',bool(m and m.use_nodes),'surface method',getattr(m,'surface_render_method',''))
 if m and m.use_nodes:
  for nd in m.node_tree.nodes:
   print(' NODE',nd.name,nd.type)
   if nd.type=='BSDF_PRINCIPLED':
    print('    ', 'base',tuple(nd.inputs['Base Color'].default_value),'metal',nd.inputs['Metallic'].default_value,'rough',nd.inputs['Roughness'].default_value,'trans',nd.inputs['Transmission Weight'].default_value,'alpha',nd.inputs['Alpha'].default_value)
