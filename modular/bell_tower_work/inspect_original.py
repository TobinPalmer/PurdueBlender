import bpy,json
from mathutils import Vector
from pathlib import Path
p=Path(__file__).parent
obs=list(bpy.data.collections['Asset_bell_tower'].all_objects)
out=[]
for o in obs:
 b=[o.matrix_world@Vector(c) for c in o.bound_box]
 out.append({'name':o.name,'location':list(o.location),'dimensions':list(o.dimensions),'bounds':[[min(v[i] for v in b) for i in range(3)],[max(v[i] for v in b) for i in range(3)]]})
(p/'original_metrics.json').write_text(json.dumps(out,indent=2))
print('OBJECTS',len(obs),'BOUNDS',[[min(x['bounds'][0][i] for x in out) for i in range(3)],[max(x['bounds'][1][i] for x in out) for i in range(3)]])
