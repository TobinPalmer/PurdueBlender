import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_potter_engineering']
o=next(o for o in c.objects if 'Structural_Envelope' in o.name);print('wall',len(o.data.materials),[(i,m.name if m else None) for i,m in enumerate(o.data.materials)])
from collections import Counter
z=Counter()
for p in o.data.polygons:
 co=sum((o.data.vertices[v].co.z for v in p.vertices))/len(p.vertices);z[(round(co),p.material_index)]+=1
print('z',z)
