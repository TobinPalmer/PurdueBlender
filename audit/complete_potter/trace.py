import sys,json,math
sys.path[:0]=['audit/complete_potter/deps','audit/walc_review/deps']
import fitz
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import affine_transform
D='audit/complete_potter/';doc=fitz.open(D+'study.pdf');target=Polygon(json.load(open(D+'outline.json')));out={}
for page in [51,53,54,55]:
 polys=[];segments=[]
 for d in doc[page].get_drawings():
  r=d['rect']
  if r.y0<300 or r.y1>680 or r.x0<90 or r.x1>520:continue
  pts=[]
  for it in d['items']:
   if it[0]=='l':
    a,b=it[1:];pts.extend([(a.x,a.y),(b.x,b.y)])
    if d.get('color')==(0,0,0) and d.get('width',0)>.05 and math.dist(a,b)>3:segments.append([list(a),list(b)])
   if it[0]=='re':
    rr=it[1];pts.extend([(rr.x0,rr.y0),(rr.x1,rr.y0),(rr.x1,rr.y1),(rr.x0,rr.y1)])
  if len(pts)>3 and d.get('fill') and len(set(d['fill']))>1:
   p=Polygon(pts).buffer(0)
   if p.area>50:polys.append(p)
 source=unary_union(polys);best=None
 for swap in [False,True]:
  for sx in [-1,1]:
   for sy in [-1,1]:
    aa=[0,sx,sy,0,0,0] if swap else [sx,0,0,sy,0,0];p=affine_transform(source,aa);b=p.bounds;t=target.bounds;xx=(t[2]-t[0])/(b[2]-b[0]);yy=(t[3]-t[1])/(b[3]-b[1]);a=[aa[0]*xx,aa[1]*xx,aa[2]*yy,aa[3]*yy,t[0]-b[0]*xx,t[1]-b[1]*yy];q=affine_transform(source,a);score=q.intersection(target).area/q.union(target).area
    if best is None or score>best[0]:best=(score,a)
 out[str(page)]={'iou':best[0],'affine':best[1],'segments':segments}
json.dump(out,open(D+'historic_trace.json','w'),indent=2);print({k:(v['iou'],len(v['segments']),v['affine']) for k,v in out.items()})
