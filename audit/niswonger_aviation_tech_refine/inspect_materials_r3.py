import bpy,json
for n in ['NISW_Roof_Membrane','NISW_Photographic_Satin_Metal','NISW_Satin_Metal','NISW_R2_Composite_Aluminum_Roof']:
 m=bpy.data.materials.get(n)
 if m:
  bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
  print(n, 'diffuse',list(m.diffuse_color),'BS',({k:bs.inputs[k].default_value for k in ['Base Color','Metallic','Roughness']} if bs else None))
