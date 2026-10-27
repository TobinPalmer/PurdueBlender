import bpy,math
from mathutils import Vector
sh=bpy.data.objects['RHPH structural shell | GIS outline']; ring=[]
for v in sh.data.vertices:
 p=sh.matrix_world@v.co
 if abs(p.z+1)<.001:
  xy=(round(p.x,4),round(p.y,4))
  if xy not in ring: ring.append(xy)
win=bpy.data.objects['Facade glazing | repeated vision panels']; centers=[]
for f in win.data.polygons:
 if len(f.vertices)==4:
  ps=[win.matrix_world@win.data.vertices[i].co for i in f.vertices]
  centers.append(sum(ps,Vector())/4)
best=[]
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)]; dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
 if L<5: continue
 ux,uy=dx/L,dy/L; vals=[]
 for c in centers:
  px=c.x-a[0];py=c.y-a[1];t=px*ux+py*uy; d=abs(px*uy-py*ux)
  if -1<t<L+1: vals.append((d,t,c.z))
 counts=[(tol,sum(d<tol for d,t,z in vals)) for tol in (.15,.3,.6,1,2)]
 best.append((counts[-1][1],counts[0][1],L,i,a,b,counts,sorted(vals,key=lambda x:x[0])[:3]))
for q in sorted(best,reverse=True)[:10]: print(q)
