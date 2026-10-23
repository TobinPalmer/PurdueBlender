import bpy
m=bpy.data.materials.get('HAAS_GooglePhotos_RedClayTiles_estimated')
print('mat',m.name,'diffuse',tuple(m.diffuse_color))
for n in m.node_tree.nodes:
 print(n.name,n.type)
 if n.type=='BSDF_PRINCIPLED':
  for k in ['Base Color','Roughness','Metallic','Emission Color','Emission Strength','Specular IOR Level']:
   if k in n.inputs: print(k,n.inputs[k].default_value)
 if n.type=='BUMP': print('bump strength',n.inputs['Strength'].default_value,'distance',n.inputs['Distance'].default_value)
