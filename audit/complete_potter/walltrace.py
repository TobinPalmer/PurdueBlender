import sys,json
sys.path[:0]=['audit/complete_potter/deps','audit/walc_review/deps']
import fitz,numpy as np
from shapely.geometry import Polygon,LineString
D='audit/complete_potter/';doc=fitz.open(D+'study.pdf');reg=json.load(open(D+'plan_registration.json'));target=Polygon(json.load(open(D+'outline.json'))).buffer(-.45);out={}
for page in [51,53,54,55]:
 pix=doc[page].get_pixmap(matrix=fitz.Matrix(3,3));im=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3);mask=im.max(2)<85;found=[];seen=set();a=reg[str(page)]['affine']
 def cv(x,y):return (a[0]*x+a[1]*y+a[4],a[2]*x+a[3]*y+a[5])
 for axis in [0,1]:
  for v in range(322*3,656*3) if axis==0 else range(100*3,510*3):
   row=mask[v,300:1530] if axis==0 else mask[966:1968,v];offset=300 if axis==0 else 966
   starts=np.where(np.diff(np.pad(row.astype(int),(1,1)))==1)[0];ends=np.where(np.diff(np.pad(row.astype(int),(1,1)))==-1)[0]
   for st,en in zip(starts,ends):
    if en-st<25:continue
    p=((st+offset)/3,v/3) if axis==0 else (v/3,(st+offset)/3);q=((en+offset)/3,v/3) if axis==0 else (v/3,(en+offset)/3)
    key=(axis,round(v/5),round((st+offset)/6),round((en+offset)/6))
    if key in seen:continue
    seen.add(key);line=LineString([cv(*p),cv(*q)]).intersection(target)
    for geom in getattr(line,'geoms',[line]):
     if geom.geom_type=='LineString' and geom.length>1.5:found.append(list(geom.coords))
 out[str(page)]={'lines':found,'registration_iou':reg[str(page)]['iou']};print(page,len(found))
json.dump(out,open(D+'historic_walls.json','w'),indent=2)
