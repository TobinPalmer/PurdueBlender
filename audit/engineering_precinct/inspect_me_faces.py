import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]; man=json.loads((ROOT/'modular/manifest.json').read_text())
rec=next(a for a in man['assets'] if a['id']=='mechanical_engineering')
with bpy.data.libraries.load(str(ROOT/'modular'/rec['file']),link=False) as (src,dst): dst.collections=[rec['collection']]
col=dst.collections[0]
for ob in col.all_objects:
 if ob.type!='MESH' or 'Envelope' not in ob.name: continue
 print('OBJECT',ob.name,'loc',tuple(ob.location))
 for p in ob.data.polygons:
  if p.area>300 and p.normal.y>.35 and abs(p.center.z-3.6)<.1:
   c=ob.matrix_world@p.center
   coords=[ob.data.vertices[i].co for i in p.vertices]
   lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
   print('FACE',round(p.area,1),tuple(round(v,1) for v in c),tuple(round(v,2) for v in p.normal),'BOUNDS',tuple(round(v,1) for v in lo),tuple(round(v,1) for v in hi))
