import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for mn in ['Bedford_Indiana_Limestone','Historic_Slate_Roof_Procedural']:
 n=bpy.data.materials[mn].node_tree.nodes['Mix'];print('\n',mn)
 for i,s in enumerate(n.inputs):
  try:v=str(s.default_value)
  except:v=''
  print(i,s.name,s.type,v)
