import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/rawls_hall.blend'))
for n in ['RAWL_SE_Diagonal_CurtainWall_BronzeMullions','RAWL_SE_Diagonal_CurtainWall_Glass']:
 o=bpy.data.objects[n]; print(n,'verts',len(o.data.vertices),'faces',len(o.data.polygons))
 for i in range(min(16,len(o.data.vertices)),0,-8):
  pass
 for k in [0,8,16,24]:
  if k>=len(o.data.vertices):continue
  pts=[o.matrix_world@o.data.vertices[i].co for i in range(k,min(k+8,len(o.data.vertices)))]
  print('chunk',k,'bounds',[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)],'pts',[[round(v,3) for v in p] for p in pts])
