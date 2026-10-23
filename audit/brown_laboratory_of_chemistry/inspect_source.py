import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_brown_laboratory_of_chemistry_brwn_aed3885.blend'
bpy.ops.wm.open_mainfile(filepath=p)
print('SCENE', [(s.name, len(s.objects)) for s in bpy.data.scenes])
for o in bpy.context.scene.objects:
 print('OBJ',o.name,o.type, 'loc',tuple(round(x,3) for x in o.location), 'dim',tuple(round(x,3) for x in o.dimensions), 'scale',tuple(o.scale))
 if o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  print(' BOUNDS',tuple(round(min(v[i] for v in pts),3) for i in range(3)),tuple(round(max(v[i] for v in pts),3) for i in range(3)))
