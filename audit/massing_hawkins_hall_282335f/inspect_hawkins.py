import bpy,collections
from mathutils import Vector
obj=bpy.data.objects['Hawkins Hall']
print('bbox',[(round(min(v.co[i] for v in obj.data.vertices),4),round(max(v.co[i] for v in obj.data.vertices),4)) for i in range(3)])
zs=collections.Counter(round(v.co.z,3) for v in obj.data.vertices)
print('z levels',sorted(zs.items()))
print('materials',[(m.name if m else None, sum(p.material_index==i for p in obj.data.polygons)) for i,m in enumerate(obj.data.materials)])
for i,v in enumerate(obj.data.vertices): print('V',i,tuple(round(a,3) for a in v.co))
