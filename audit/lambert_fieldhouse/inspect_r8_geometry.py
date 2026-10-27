import bpy,json
from mathutils import Vector
from pathlib import Path
c=bpy.data.collections['Asset_lambert_fieldhouse']
out=[]
for o in c.all_objects:
 d=list(o.dimensions);n=o.name.lower()
 if max(d)>15 or any(t in n for t in ['line','perimeter','context','street','boundary','site','road','curb','sidewalk','gis','track edge','entrance','sign','hurdle','high-jump','event','scoreboard']):
  out.append({'name':o.name,'type':o.type,'dims':[round(v,3) for v in d],'loc':[round(v,3) for v in o.location],'collections':[co.name for co in o.users_collection],'materials':[m.name for m in o.data.materials if m] if getattr(o.data,'materials',None) else []})
Path('audit/lambert_fieldhouse/inspect_r8_geometry.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out[:120],indent=2))
