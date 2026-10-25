import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
o=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
rows=[]
for i in list(range(8,24))+[8+((s*4+j)*9+k)*2 for s in range(5) for j,k in [(0,0),(0,8),(3,0),(3,8)]]:
 p=o.matrix_world@o.data.vertices[i].co;rows.append((i,[round(v,2) for v in p]))
print(json.dumps(rows,indent=2))
