import bpy
bpy.ops.wm.open_mainfile(filepath=r'audit/engineering_precinct/engineering_mall_foliage_library_review.blend')
for m in [bpy.data.materials.get('asphalt_01'),bpy.data.materials.get('Campus_Walkway_Concrete'),bpy.data.materials.get('Street_Asphalt_Dark'),bpy.data.materials.get('Street_Curb_Concrete')]:
 if not m: continue
 print('\n',m.name,'diffuse',tuple(round(x,3) for x in m.diffuse_color))
 for n in m.node_tree.nodes if m.node_tree else []:
  if n.type=='BSDF_PRINCIPLED': print('BSDF',n.inputs['Base Color'].default_value[:], n.inputs['Roughness'].default_value)
