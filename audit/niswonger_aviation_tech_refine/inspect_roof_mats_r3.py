import bpy
for n in ['NISW_Photographic_Sloping_Roof','NISW_Flat_Roof_Membrane']:
 o=bpy.data.objects.get(n); print(n,'hide',o.hide_render,'mat_slots',[m.name if m else None for m in o.data.materials], 'polygons',len(o.data.polygons))
 for m in o.data.materials:
  if m:
   print('  ',m.name,m.diffuse_color[:], 'blend',m.surface_render_method)
   for node in m.node_tree.nodes:
    if node.type=='BSDF_PRINCIPLED':print(' BSDF alpha',node.inputs['Alpha'].default_value,'base',tuple(node.inputs['Base Color'].default_value))
