import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
m=json.loads((ROOT/'modular/manifest.json').read_text())
out=[]
for a in m['assets']:
    b=a.get('bounds_world_m')
    if a['kind']!='massing' or not b:continue
    x=sum(b[0])/2;y=sum(b[1])/2
    if math.hypot(x-28.93,y+1.22)>240:continue
    with bpy.data.libraries.load(str(ROOT/'modular'/a['file']),link=False) as (src,dst):dst.collections=[a['collection']]
    c=dst.collections[0]; polys=[];zs=[]
    for o in c.all_objects:
        if o.type!='MESH':continue
        vs=[o.matrix_world@v.co for v in o.data.vertices];zs += [v.z for v in vs]
        for f in o.data.polygons:polys.append([[vs[i].x,vs[i].y] for i in f.vertices])
    out.append({'id':a['id'],'polygons':polys,'z':[min(zs),max(zs)]})
(ROOT/'audit/walc_review/massing_geometry.json').write_text(json.dumps(out))
print('EXTRACTED',len(out))
