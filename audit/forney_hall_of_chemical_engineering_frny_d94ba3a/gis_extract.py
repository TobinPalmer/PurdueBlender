import json, math
from pathlib import Path
p=Path('audit/official_purdue_buildings_wgs84.json'); d=json.loads(p.read_text(encoding='utf-8'))
f=next(x for x in d['features'] if x['attributes'].get('BLDG_ABBR')=='FRNY')
a=f['attributes']; rings=f['geometry']['rings']; origin=(40.4274,-86.9137)
coords=[]
for ring in rings:
 pts=[]
 for lon,lat in ring:
  x=(lon-origin[1])*111412.84*math.cos(math.radians(origin[0])); y=(lat-origin[0])*111040.0
  pts.append((x,y))
 coords.append(pts)
 xs=[x for x,y in coords[0]]; ys=[y for x,y in coords[0]]
 print(json.dumps({'attributes':a,'bounds_local_m':[min(xs),max(xs),min(ys),max(ys)],'ring_count':len(coords),'ring_vertex_counts':[len(r) for r in coords],'local_ring':coords[0]},indent=2))
