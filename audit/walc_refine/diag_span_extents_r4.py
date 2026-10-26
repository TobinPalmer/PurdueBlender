import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent.parent.parent;ring=next(x for x in json.loads((root/'audit/official_building_references.json').read_text())['buildings'] if x['fid']==906)['rings_xy_m'][0];area=sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2
for idx in [59,60]:
 o=bpy.data.objects[f'WALC_Source906_Edge_{idx}_Band4'];ps=[o.matrix_world@v.co for v in o.data.vertices];z=min(p.z for p in ps);bot=[p for p in ps if abs(p.z-z)<1e-4];a,b=max([(bot[i],bot[j]) for i in range(4) for j in range(i+1,4)],key=lambda q:(q[0]-q[1]).length);t=Vector((b.x-a.x,b.y-a.y)).normalized();sa,sb=ring[idx],ring[idx+1];st=Vector((sb[0]-sa[0],sb[1]-sa[1])).normalized();
 if t.dot(st)<0:t=-t
 n=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x));c=Vector((sum(p.x for p in bot)/4,sum(p.y for p in bot)/4));pr=[(p.x*t.x+p.y*t.y,p.x*n.x+p.y*n.y) for p in bot];scenter=c.dot(t);dcenter=c.dot(n);smin=min(q[0] for q in pr)-scenter;smax=max(q[0] for q in pr)-scenter;dmin=min(q[1] for q in pr)-dcenter;dmax=max(q[1] for q in pr)-dcenter;out=(dmax-dmin)/2;print('edge',idx,'t',tuple(t),'n',tuple(n),'center',tuple(c),'s',smin,smax,'d',dmin,dmax,'outer',out)
 for ss in (smin-.01,smax+.01):
  for dd in (out-.16,out):
   q=c+t*ss+n*dd;print('wall',tuple(round(v,3) for v in q))
