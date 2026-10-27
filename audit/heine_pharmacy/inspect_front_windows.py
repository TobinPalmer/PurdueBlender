import bpy,math,json
from mathutils import Vector
ob=bpy.data.objects['Facade glazing | repeated vision panels']
# front facade approximate line from known GIS vertices
A=Vector((8.131,-17.539,0)); B=Vector((36.169,8.369,0)); d=B-A; L=d.length; u=d.normalized(); n=Vector((u.y,-u.x,0))
faces=[]
for p in ob.data.polygons:
 if len(p.vertices)!=4: continue
 vs=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices]; c=sum(vs,Vector())/4
 # distance perpendicular from line in XY and projection
 proj=(Vector((c.x,c.y,0))-Vector((A.x,A.y,0))).dot(Vector((u.x,u.y,0)))
 dist=abs((Vector((c.x,c.y,0))-Vector((A.x,A.y,0))).dot(Vector((n.x,n.y,0))))
 if dist<10 and 0<proj<L:
  faces.append((round(proj,2),round(c.z,2),round(dist,2)))
print('L',L,'faces',len(faces),'samples',faces[:120])
