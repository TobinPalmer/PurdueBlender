import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['SC_Portico_and_Entrances']
for o in c.objects:
  if any(x in o.name.lower() for x in ['step','balustrade','pedestal','column','portal','canopy','entablature','slab','door','fanlight','text']):
    pts=[o.matrix_world @ Vector(corner) for corner in o.bound_box]
    lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
    print(o.name, o.type, [round(hi[i]-lo[i],2) for i in range(3)], [round(x,2) for x in lo], [round(x,2) for x in hi])
