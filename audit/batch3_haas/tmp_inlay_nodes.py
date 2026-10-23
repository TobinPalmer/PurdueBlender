import bpy
for n in ['HAAS_R6_Red_Brick_Inlay','Purdue_Brick','Purdue_Red_Brick']:
 m=bpy.data.materials.get(n);print('\n',n)
 if not m or not m.use_nodes:continue
 for x in m.node_tree.nodes:
  print(x.name,x.type)
  if x.type=='BSDF_PRINCIPLED':
   for k in ['Base Color','Roughness','Normal']:
    print(k, list(x.inputs[k].default_value) if k=='Base Color' else x.inputs[k].default_value)
