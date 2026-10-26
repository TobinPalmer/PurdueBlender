import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent.parent.parent
ring=next(x for x in json.loads((root/'audit/official_building_references.json').read_text())['buildings'] if x['fid']==906)['rings_xy_m'][0]
idx=60;o=bpy.data.objects[f'WALC_Source906_Edge_{idx}_Band4'];pts=[o.matrix_world@v.co for v in o.data.vertices];z=min(p.z for p in pts);bottom=[p for p in pts if abs(p.z-z)<1e-4]
a,b=max([(bottom[i],bottom[j]) for i in range(4) for j in range(i+1,4)],key=lambda pair:(pair[0]-pair[1]).length)
t=Vector((b.x-a.x,b.y-a.y)).normalized(); sa,sb=ring[idx],ring[idx+1]; st=Vector((sb[0]-sa[0],sb[1]-sa[1])).normalized();
if t.dot(st)<0:t=-t
n=Vector((t.y,-t.x)) if (sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))<0) else Vector((-t.y,t.x))
c=Vector((sum(p.x for p in bottom)/4,sum(p.y for p in bottom)/4));pr=[(p.x*t.x+p.y*t.y,p.x*n.x+p.y*n.y) for p in bottom]; sc=c.dot(t);dc=c.dot(n);smin=min(x[0] for x in pr)-sc;smax=max(x[0] for x in pr)-sc;dmin=min(x[1] for x in pr)-dc;dmax=max(x[1] for x in pr)-dc
print('verts',[(round(p.x,3),round(p.y,3)) for p in bottom]);print('t,n',tuple(t),tuple(n),'center',tuple(c),'s',smin,smax,'d',dmin,dmax,'length',smax-smin)
for s in (smin-(.01),smax+.01):
 for d in (dmax-.08,dmin+.08):
  p=c+t*s+n*d;print('corner',s,d,tuple(p))
# generated candidate corners at z=6.2 near these coordinates
r4=bpy.data.objects['WALC_R4_Masonry_Bay_Fields']; candidates=[r4.matrix_world@v.co for v in r4.data.vertices if abs(v.co.z-6.2)<1e-5 and v.co.x>42.05 and v.co.y>-8.5 and v.co.y<-7.4];print('gen candidates',len(candidates),[(round(p.x,3),round(p.y,3),round(p.z,2)) for p in candidates[:20]])
