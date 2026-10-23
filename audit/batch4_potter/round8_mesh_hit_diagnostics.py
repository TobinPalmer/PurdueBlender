import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];dg=bpy.context.evaluated_depsgraph_get()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)]
def meshdata(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh()
 if not me or not me.polygons:return None,None
 vs=[o.matrix_world@v.co for v in me.vertices];polys=[list(p.vertices) for p in me.polygons];centers=[sum((vs[i] for i in p),Vector())/len(p) for p in polys];tree=BVHTree.FromPolygons(vs,polys,all_triangles=False);ev.to_mesh_clear();return tree,centers
def box(center):
 x,y,z=center;w=.4;z0=z+.05;z1=z+2.05;vs=[Vector((x+dx,y+dy,zz)) for zz in (z0,z1) for dx,dy in [(-w,-w),(w,-w),(w,w),(-w,w)]];fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];return BVHTree.FromPolygons(vs,fs,all_triangles=False),[z0,z1]
res=[]
for core,level in [(3,0),(3,1),(3,2),(3,3),(1,1),(2,1)]:
 st=c.objects[f'POTR_2016_StairCore{core}_Level{level}_Flight'];samples=[]
 for p in st.data.polygons:
  if p.normal.z>.99 and p.area>.08:
   q=sum((st.matrix_world@st.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);t=tuple(round(x,3) for x in q)
   if not any((Vector(t)-Vector(old)).length<.1 for old in samples):samples.append(t)
 bb=bounds(st);env=[bb[0]-.8,bb[1]-.8,bb[2]-.5,bb[3]+.8,bb[4]+.8,bb[5]+2.5];obs=[]
 for o in c.all_objects:
  if o==st or o.type not in {'MESH','CURVE'}:continue
  obb=bounds(o)
  if all(obb[i+3]>=env[i] and obb[i]<=env[i+3] for i in range(3)):
   tree,centers=meshdata(o)
   if tree:obs.append((o.name,tree,centers))
 hitrecords=[]
 for p in samples:
  body,zspan=box(p);found=[]
  for nm,tree,centers in obs:
   pairs=body.overlap(tree)
   if pairs:
    zvals=[round(centers[j].z,3) for i,j in pairs]
    found.append({'object':nm,'hit_pairs':len(pairs),'hit_centroid_z_minmax':[min(zvals),max(zvals)],'box_z':[round(zspan[0],3),round(zspan[1],3)]})
  if found:hitrecords.append({'tread_xyz':list(p),'overlaps':found})
 res.append({'core':core,'level':level,'samples':len(samples),'hits':hitrecords})
(D/'round8_mesh_hit_diagnostics.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
