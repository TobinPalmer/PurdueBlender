import bpy,json
from pathlib import Path
from mathutils import Vector
R=json.loads((Path(bpy.data.filepath).parent.parent.parent/'audit/official_building_references.json').read_text())
b=next(x for x in R['buildings'] if x['fid']==906); ring=b['rings_xy_m'][0]
area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
print('ringlen,area',len(ring),area)
for i in (58,59,60,61):
 print('ring',i,ring[i],ring[(i+1)%len(ring)])
for i in (58,59,60,61):
 o=bpy.data.objects.get(f'WALC_Source906_Edge_{i}_Band4')
 if o:
  ps=[o.matrix_world@v.co for v in o.data.vertices]
  z0=min(p.z for p in ps); bot=[p for p in ps if p.z==z0]
  print(o.name,[[round(p.x,3),round(p.y,3)] for p in bot])
