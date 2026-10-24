import bpy,json
from pathlib import Path
p=Path('modular/manifest.json');m=json.load(open(p));a=next(x for x in m['assets'] if 'materials_science' in x['id'])
with bpy.data.libraries.load(str(Path(__file__).resolve().parents[2]/'modular'/a['file']),link=False) as (src,dst):dst.collections=[a['collection']]
c=dst.collections[0]
for o in c.all_objects:
 if o.type=='MESH':
  co=[o.matrix_world@v.co for v in o.data.vertices]
  lo=[min(v[i] for v in co) for i in range(3)];hi=[max(v[i] for v in co) for i in range(3)]
  print(o.name,tuple(round(v,1) for v in lo),tuple(round(v,1) for v in hi))
