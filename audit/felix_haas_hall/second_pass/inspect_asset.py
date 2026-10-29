"""Inspect the exact saved Haas source without saving or modifying the library."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
P=ROOT/'modular/buildings/felix_haas_hall.blend'
C=bpy.data.collections['Asset_felix_haas_hall']
rows=[]
for o in C.all_objects:
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    bounds=[[round(min(v[i] for v in p),5) for i in range(3)],[round(max(v[i] for v in p),5) for i in range(3)]] if p else None
    rows.append({'name':o.name,'type':o.type,'bounds':bounds,'hide_render':o.hide_render,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'modifiers':[(m.name,m.type) for m in o.modifiers]})
record={'asset_path':str(P.relative_to(ROOT)).replace('\\','/'),'asset_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'expected_collection':C.name,'object_count':len(rows),'objects':rows,'images':[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images],'collections':[c.name for c in bpy.data.collections]}
(OUT/'baseline_inspection.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sha256':record['asset_sha256'],'objects':len(rows),'images':record['images'],'exterior_candidates':[r for r in rows if any(x in r['name'] for x in ('Brick_Wall','Photo_','GIS','West','North','South'))]},indent=2))
