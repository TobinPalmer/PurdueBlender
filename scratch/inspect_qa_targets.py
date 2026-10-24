import bpy,os
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
for fn in ['rawls_hall.blend','stanley_coulter_hall.blend','wiley_hall.blend','winifred_parker_hall.blend','benjamin_harrison_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn)); arr=[]
 for o in bpy.data.objects:
  if o.type=='MESH':
   pts=[o.matrix_world@Vector(v) for v in o.bound_box]; c=sum(pts,Vector())/8; d=max((max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)))
   arr.append((d,o.name,tuple(round(v,1) for v in c)))
 print('\n##',fn,'meshes',len(arr))
 for row in sorted(arr,reverse=True)[:16]: print(row)
 from collections import Counter
 print('prefixes',Counter(row[1].split('_')[0] for row in arr).most_common(12))
