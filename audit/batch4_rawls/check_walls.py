import bpy,math
from mathutils import Vector
fp=bpy.data.objects['RAWL_FloorSlab_L1_Ground'];poly=[fp.matrix_world@fp.data.vertices[i].co for i in range(29)];poly=[(p.x,p.y) for p in poly]
def inside(x,y):
 c=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
  j=i
 return c
for o in bpy.data.collections['Asset_rawls_hall'].all_objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):
  p=o.matrix_world.translation
  if not inside(p.x,p.y):print('OUTSIDE',o.name,tuple(round(v,2) for v in p),tuple(round(v,2) for v in o.dimensions))
