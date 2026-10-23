import sys,json
sys.path[:0]=['audit/complete_potter/deps','audit/walc_review/deps']
import fitz,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import affine_transform
D='audit/complete_potter/';doc=fitz.open(D+'study.pdf');target=Polygon(json.load(open(D+'outline.json')));out={}
for page in [51,53,54,55]:
 pix=doc[page].get_pixmap();im=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3);col=im.max(2)-im.min(2);mask=(col>12)&(im.min(2)>60)
 shapes=[]
 for y in range(322,656,2):
  row=mask[y,100:510];starts=np.where(np.diff(np.pad(row.astype(int),(1,1)))==1)[0];ends=np.where(np.diff(np.pad(row.astype(int),(1,1)))==-1)[0]
  shapes.extend(box(a+100,y,b+100,y+2) for a,b in zip(starts,ends) if b-a>4)
 source=unary_union(shapes).buffer(2).buffer(-2);best=None
 for swap in [False,True]:
  for sx in [-1,1]:
   for sy in [-1,1]:
    aa=[0,sx,sy,0,0,0] if swap else [sx,0,0,sy,0,0];p=affine_transform(source,aa);b=p.bounds;t=target.bounds;xx=(t[2]-t[0])/(b[2]-b[0]);yy=(t[3]-t[1])/(b[3]-b[1]);a=[aa[0]*xx,aa[1]*xx,aa[2]*yy,aa[3]*yy,t[0]-b[0]*xx,t[1]-b[1]*yy];q=affine_transform(source,a);score=q.intersection(target).area/q.union(target).area
    if best is None or score>best[0]:best=(score,a)
 out[str(page)]={'iou':best[0],'affine':best[1]};print(page,best)
json.dump(out,open(D+'plan_registration.json','w'),indent=2)
