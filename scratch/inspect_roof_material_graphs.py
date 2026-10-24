import bpy,os
for f, names in [('hovde_hall',['Hovde_Roof_Membrane']),('hansen_life_sciences',['Roof_Membrane_Gravel']),('knoy_hall',['KNOY_Roof_Gravel_Membrane'])]:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend'))
 for name in names:
  m=bpy.data.materials[name]; print('\n',f,name)
  for n in m.node_tree.nodes:
   print(n.name,n.type, 'inputs',[(i.name,tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3),len(i.links)) for i in n.inputs if i.name in ['Base Color','Roughness','Normal','Height']])
