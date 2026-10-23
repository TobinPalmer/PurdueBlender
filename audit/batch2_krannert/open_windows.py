import bpy,os,json,math
from mathutils import Vector
wall=bpy.data.objects['KRAN_Exterior_Masonry_Walls'];gl=bpy.data.objects['KRAN_Window_Ribbon_Glazing'];verts=[];faces=[];mats=[];cuts=0
for p in wall.data.polygons:
 points=[wall.matrix_world@wall.data.vertices[i].co for i in p.vertices];a=points[0];edge=points[1]-a;length=Vector((edge.x,edge.y,0)).length
 if length<.1:continue
 u=Vector((edge.x,edge.y,0)).normalized();n=Vector((-u.y,u.x,0));z0=min(v.z for v in points);z1=max(v.z for v in points);rects=[]
 for q in gl.data.polygons:
  vs=[gl.matrix_world@gl.data.vertices[i].co for i in q.vertices]
  if max(abs((v-a).dot(n)) for v in vs)>.12:continue
  xx=[(v-a).dot(u) for v in vs];zz=[v.z for v in vs];lo=max(0,min(xx));hi=min(length,max(xx));bot=max(z0,min(zz));top=min(z1,max(zz))
  if hi>lo+.01 and top>bot+.01:rects.append((lo,hi,bot,top))
 xs=sorted(set([0,length]+[c for r in rects for c in r[:2]]));zs=sorted(set([z0,z1]+[c for r in rects for c in r[2:]]));cuts+=len(rects)
 for l,r in zip(xs,xs[1:]):
  for b,t in zip(zs,zs[1:]):
   if any(v[0]<(l+r)/2<v[1] and v[2]<(b+t)/2<v[3] for v in rects):continue
   ids=[]
   for x,z in [(l,b),(r,b),(r,t),(l,t)]:
    pt=a+u*x;pt.z=z;ids.append(len(verts));verts.append(wall.matrix_world.inverted()@pt)
   faces.append(ids);mats.append(p.material_index)
mesh=bpy.data.meshes.new('KRAN_WindowOpenedMasonry');mesh.from_pydata(verts,[],faces)
for m in wall.data.materials:mesh.materials.append(m)
wall.data=mesh
for p,i in zip(mesh.polygons,mats):p.material_index=i
mod=wall.modifiers.new('Physical inward wall thickness','SOLIDIFY');mod.thickness=.2;mod.offset=-1
wall['window_openings_cut']=cuts
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('CUT_WINDOWS',cuts)
