import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
o=bpy.data.objects['RAWL_Atrium_Mezzanine_Balustrades']
print('Z levels', sorted(set(round((o.matrix_world@v.co).z,3) for v in o.data.vertices)))
from collections import defaultdict
zxy=defaultdict(list)
for v in o.data.vertices:
 p=o.matrix_world@v.co
 zxy[round(p.z,3)].append((round(p.x,2),round(p.y,2)))
for z,arr in zxy.items():print(z, sorted(set(arr))[:32])
