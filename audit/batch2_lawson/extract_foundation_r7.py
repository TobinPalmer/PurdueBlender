import bpy,json
from mathutils import Vector
ob=bpy.data.objects['LWSN_Foundation_Base']; mw=ob.matrix_world
polys=[]
for p in ob.data.polygons:
 vv=[mw@ob.data.vertices[i].co for i in p.vertices]
 if vv and all(abs(v.z-.8)<1e-4 for v in vv):polys.append([[round(v.x,6),round(v.y,6)] for v in vv])
with open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/r7_foundation_top_faces.json','w') as f:json.dump(polys,f,indent=2)
print('top faces',len(polys))
