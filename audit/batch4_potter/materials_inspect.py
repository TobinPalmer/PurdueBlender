import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P)
for name in ['POTR_Meter_Brick','POTR_Precast_Concrete','POTR_Terrazzo_Estimate','POTR_Recessed_Glass']:
 m=bpy.data.materials.get(name);print('MAT',name, m and [(n.type,n.name) for n in m.node_tree.nodes] if m else None)
o=next(o for o in bpy.data.collections['Asset_potter_engineering'].objects if 'Perimeter_With_Real' in o.name)
print('wall',len(o.data.materials),[(i,m.name if m else None) for i,m in enumerate(o.data.materials)])
from collections import Counter
z=Counter()
for p in o.data.polygons:
 co=sum((o.data.vertices[v].co.z for v in p.vertices))/len(p.vertices);z[(round(co),p.material_index)]+=1
print(z)
roof=next(o for o in bpy.data.collections['Asset_potter_engineering'].objects if 'Official_864_Roof' in o.name)
print('roof material',[(m.name if m else None) for m in roof.data.materials])
