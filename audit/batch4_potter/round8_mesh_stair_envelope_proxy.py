import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];dg=bpy.context.evaluated_depsgraph_get()
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)]
def mesh_bvh(o):
 ev=o.evaluated_get(dg);me=ev.to_mesh()
 if not me or not me.polygons:return None
 vs=[o.matrix_world@v.co for v in me.vertices];ps=[list(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(vs,ps,all_triangles=False);ev.to_mesh_clear();return tree
def cubebvh(center):
 x,y,z=center;w=.4;l=.4;z0=z+.05;z1=z+2.05
 vs=[Vector((x+dx,y+dy,zz)) for zz in (z0,z1) for dx,dy in [(-w,-l),(w,-l),(w,l),(-w,l)]]
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 return BVHTree.FromPolygons(vs,fs,all_triangles=False)
results=[]
for core in range(1,4):
 for level in range(4 if core==3 else 3):
  fn=f'POTR_2016_StairCore{core}_Level{level}_Flight';st=c.objects.get(fn)
  if not st or st.type!='MESH':continue
  b=bounds(st);samples=[]
  for poly in st.data.polygons:
   if poly.normal.z>.99 and poly.area>.08:
    cent=sum((st.matrix_world@st.data.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices)
    key=tuple(round(v,3) for v in cent)
    if not any((Vector(key)-Vector(q)).length<.10 for q in samples): samples.append(key)
  # Actual local mesh obstacles (walls, rails, slabs, roof, adjacent flights/landings) whose bounds overlap the envelope region.
  pad=.8;zlo=b[2]-.5;zhi=b[5]+2.5;env=[b[0]-pad,b[1]-pad,zlo,b[3]+pad,b[4]+pad,zhi];obstacles=[]
  for o in c.all_objects:
   if o==st or o.type not in {'MESH','CURVE'}:continue
   bb=bounds(o)
   if all(bb[i+3]>=env[i] and bb[i]<=env[i+3] for i in range(3)):
    tree=mesh_bvh(o)
    if tree:obstacles.append((o.name,tree))
  hits=[]
  for pt in samples:
   body=cubebvh(pt);coll=[]
   for name,tree in obstacles:
    pairs=body.overlap(tree)
    if pairs:coll.append(name)
   if coll:hits.append({'walk_surface_xyz':list(pt),'collisions':coll})
  # Actual flight span across XY bounds; narrow dimension is only an envelope indication, not clear-width measurement.
  dx=b[3]-b[0];dy=b[4]-b[1]
  results.append({'core':core,'level':level,'samples':len(samples),'body_width_m':.8,'body_height_m':2.0,'body_bottom_offset_m':.05,'geometry_obstacles_checked':len(obstacles),'collision_count':len(hits),'first_collisions':hits[:20],'flight_xy_bounds_m':[round(dx,3),round(dy,3)],'narrow_xy_dimension_m':round(min(dx,dy),3),'interpretation':'Axis-aligned 0.8 x 0.8 x 2.0m box overlap proxy at each upward tread-face centroid; excludes supporting flight mesh, includes nearby modeled mesh/curve geometry after evaluated conversion. Not code or accessibility review.'})
res={'opened_asset':str(P),'reopened':True,'body_envelope_proxy':'axis aligned box at tread top +0.05m, width/depth 0.8m, height 2.0m; check against nearby actual evaluated mesh/curve BVHs; supporting flight excluded to avoid floor-touch collisions','flight_results':results}
(D/'round8_mesh_stair_envelope_proxy.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
