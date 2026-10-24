import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for ob in bpy.data.objects:
 if ob.type!='MESH' or not (ob.name.lower().startswith(('engineering','engfountain'))): continue
 pts=[ob.matrix_world@Vector(c) for c in ob.bound_box]
 lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
 dims=[hi[i]-lo[i] for i in range(3)]
 mats=[m.name for m in ob.data.materials if m]
 print(f'{ob.name}|loc={tuple(round(v,2) for v in ob.matrix_world.translation)}|bboxcenter={tuple(round((lo[i]+hi[i])/2,2) for i in range(3))}|dims={tuple(round(x,2) for x in dims)}|mats={mats}')
