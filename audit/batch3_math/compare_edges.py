import json,math
from pathlib import Path
r=Path(r'audit/batch3_math')
gis=json.loads((r/'gis_fid227.geojson').read_text())['features'][0]['geometry']['coordinates'][0]; lon0,lat0=-86.9137,40.4274
mx,my=-181.119995,-126.905003
poly=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))-mx,(lat-lat0)*111040-my) for lon,lat in gis]
comps=json.loads((r/'wall_components.json').read_text())
def pseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=0 if not den else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def dpoly(p):return min(pseg(p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))
lines=[]
for c in comps:
 x0,x1=c['x'];y0,y1=c['y']
 if x1-x0>=y1-y0:
  if x1-x0>.5:lines.append(((x0,(y0+y1)/2),(x1,(y0+y1)/2)))
 elif y1-y0>.5:lines.append((((x0+x1)/2,y0),((x0+x1)/2,y1)))
model=[]
for a,b in lines:
 n=max(1,math.ceil(math.dist(a,b)/.25));model.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)])
ms=[dpoly(p) for p in model]
gis_pts=[]
for a,b in zip(poly,poly[1:]+poly[:1]):
 n=max(1,math.ceil(math.dist(a,b)/.25));gis_pts.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)])
gs=[min(pseg(p,a,b) for a,b in lines) for p in gis_pts]
def st(v):
 q=sorted(v);return {'mean_m':sum(v)/len(v),'median_m':q[len(q)//2],'p95_m':q[int(.95*(len(q)-1))],'max_m':q[-1],'share_<=0.25m':sum(x<=.25 for x in v)/len(v),'share_<=0.5m':sum(x<=.5 for x in v)/len(v)}
out={'source_feature':227,'local_transform':'project XY minus manifest marker [-181.119995,-126.905003] m','source_crs':'EPSG:4326','method':'50 source wall-prism centerlines extracted from the saved asset source-mesh backup; the two removed window-wall prisms were rebuilt in place to the same bounds. Both centerlines and GIS boundary are sampled at <=0.25m; bidirectional minimum segment distances are reported. Centerline offset is nominally half the masonry wall thickness.','boundary_vertex_count':len(poly),'boundary_perimeter_m':sum(math.dist(a,b) for a,b in zip(poly,poly[1:]+poly[:1])),'shell_centerline_to_gis_boundary':st(ms),'gis_boundary_to_shell_centerline':st(gs)}
(r/'structural_edge_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2)); print('GIS local bounds',min(x for x,y in poly),max(x for x,y in poly),min(y for x,y in poly),max(y for x,y in poly))
