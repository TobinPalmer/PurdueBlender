"""Summarize the official Purdue building polygon snapshot in existing model metres."""
import json, math, pathlib
P=pathlib.Path(__file__).resolve().parent
LAT0,LON0=40.4274,-86.9137
SX=111412.84*math.cos(math.radians(LAT0)); SY=111040.
def xy(p): return ((p[0]-LON0)*SX,(p[1]-LAT0)*SY)
def ring_metrics(r):
    ps=[xy(p) for p in r]; a=cx=cy=0
    for p,q in zip(ps,ps[1:]+ps[:1]):
        cross=p[0]*q[1]-q[0]*p[1];a+=cross;cx+=(p[0]+q[0])*cross;cy+=(p[1]+q[1])*cross
    return ps,abs(a/2),(cx/(3*a),cy/(3*a)) if a else ps[0]
def hull(points):
    pts=sorted(set(points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];hi=[]
    for p in pts:
        while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]
def oriented_box(points):
    h=hull(points);best=None
    for p,q in zip(h,h[1:]+h[:1]):
        angle=math.atan2(q[1]-p[1],q[0]-p[0]);c,s=math.cos(angle),math.sin(angle)
        xs=[x*c+y*s for x,y in h];ys=[-x*s+y*c for x,y in h]
        w,l=max(xs)-min(xs),max(ys)-min(ys)
        if best is None or w*l<best[0]:best=(w*l,w,l,math.degrees(angle)%180)
    return {'width_m':best[1],'depth_m':best[2],'angle_degrees_east_ccw':best[3]}
data=json.loads((P/'official_purdue_buildings_wgs84.json').read_text())
rows=[]
for f in data['features']:
    if not f.get('geometry',{}).get('rings'):continue
    a=f['attributes']; rr=[ring_metrics(r) for r in f['geometry']['rings']]
    pts=[p for r,_,_ in rr for p in r]
    primary=max(rr,key=lambda r:r[1]);center=primary[2]
    if not (-1800<center[0]<1200 and -1500<center[1]<1900):continue
    rows.append({'code':a['BLDG_ABBR'],'name':a['BUILDING_N'],'fid':a['FID'],
                 'official_polygon_center_xy_m':center,'center_definition':'centroid of largest ring; use rings for exact alignment',
                 'aabb_xy_m':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],
                 'minimum_rotated_rectangle':oriented_box(pts),'rings_xy_m':[r[0] for r in rr],
                 'num_levels_attribute':a.get('NUM_LEVELS'),'height_status':'unverified; do not use Extrution/R as surveyed height',
                 'reference_status':'official campus map polygon, not a certified survey'})
out={'source':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0',
     'provenance':'Linked by official purdue.edu/campus_map app d7e5d06fb5344f5fb53819c42d3e91ed',
     'snapshot_date':'2026-10-22','coordinates':{'origin_lat':LAT0,'origin_lon':LON0,'x_m_per_degree':SX,'y_m_per_degree':SY,'x':'east','y':'north','z':'up','units':'metres using original project linear approximation'},
     'buildings':rows}
(P/'official_building_references.json').write_text(json.dumps(out,indent=2))
print(len(rows),'official polygon features within project area')
for r in rows:
    if r['code'] in ['AR','HOVD','CL50','HAAS','MATH','WALC','ARMS','ELLT','PMU','STEW','MACK','PKRF','PKRW','TARK','OWEN','SH','UNIV','BRNG','STDM']:
        print(r['code'],r['official_polygon_center_xy_m'],r['minimum_rotated_rectangle'])
