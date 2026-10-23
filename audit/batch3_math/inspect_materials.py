import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/math_sciences.blend')
for n in ['MATH_Photo_Brick_Metre']:
 m=bpy.data.materials.get(n); print('MAT',n,m.diffuse_color[:])
 for x in m.node_tree.nodes:
  print(x.bl_idname,x.name)
  for i in x.inputs:
   if hasattr(i,'default_value') and isinstance(i.default_value,(float,int)):print(' ',i.name,i.default_value)
for n in ['MATH_Lib_Floor_Terrazzo','MATH_Lib_Wall_East','MATH_Lib_Wall_North','MATH_Lib_Wall_South','MATH_Corrected_GIS_Wall_Envelope']:
 o=bpy.data.objects.get(n)
 if o:print('OBJ',n,[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)])
