import bpy
for n in ['HAAS_Photo_Limestone','HAAS_Bedford_Limestone','HAAS_Limestone_Warm','Purdue_Red_Brick','Purdue_Red_Brick.001']:
 m=bpy.data.materials.get(n)
 if m:
  print(n,tuple(round(v,3) for v in m.diffuse_color))
  if m.use_nodes:
   for n0 in m.node_tree.nodes:
    if n0.type=='BSDF_PRINCIPLED':print('  pbsdf',tuple(round(v,3) for v in n0.inputs['Base Color'].default_value),round(float(n0.inputs['Roughness'].default_value),2))
