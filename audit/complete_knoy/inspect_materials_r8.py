import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for m in bpy.data.materials:
 if any(k in m.name.lower() for k in ['brick','concrete','glass','spandrel','mullion']):
  print('\nMAT',m.name,'diffuse',tuple(m.diffuse_color))
  if m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='BSDF_PRINCIPLED':
     print('  PRINC',[(s.name,tuple(s.default_value) if hasattr(s,'default_value') and hasattr(s.default_value,'__len__') else s.default_value) for s in n.inputs if s.name in ['Base Color','Roughness','Metallic']])
    elif n.type in ['TEX_BRICK','TEX_NOISE','TEX_COORD','MIX_RGB','VALTORGB']:
     print(' ',n.type,n.name,[(s.name,tuple(s.default_value) if hasattr(s,'default_value') and hasattr(s.default_value,'__len__') else s.default_value) for s in n.inputs if hasattr(s,'default_value')])
