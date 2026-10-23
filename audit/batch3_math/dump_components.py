import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_math/before.blend')
o=bpy.data.objects['MATH_Corrected_GIS_Wall_Envelope']
verts=o.data.vertices
arr=[]
for i in range(len(verts)//8):
 vv=[verts[i*8+j].co for j in range(8)]
 arr.append({'i':i,'x':[min(v.x for v in vv),max(v.x for v in vv)],'y':[min(v.y for v in vv),max(v.y for v in vv)],'z':[min(v.z for v in vv),max(v.z for v in vv)]})
Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_math/wall_components.json').write_text(json.dumps(arr,indent=2))
print('count',len(arr))
