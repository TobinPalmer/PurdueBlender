import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
scene=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
glass=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
wall_names=['RAWL_Masonry_Exterior_Walls','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00']
def bvh_obj(name):
 o=bpy.data.objects[name]; e=o.evaluated_get(dg); m=e.to_mesh()
 try:
  vs=[e.matrix_world@v.co for v in m.vertices]; fs=[tuple(p.vertices) for p in m.polygons]
  return BVHTree.FromPolygons(vs,fs,all_triangles=False)
 finally:e.to_mesh_clear()
trees={n:bvh_obj(n) for n in wall_names}
panes=[]
for poly in glass.data.polygons:
 pts=[glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices]
 c=sum(pts,Vector())/len(pts); n=(glass.matrix_world.to_3x3()@poly.normal).normalized()
 panes.append((poly.index,c,n))
desks=sorted([o for o in bpy.data.objects if o.name.startswith('RAWL_2026_1086_Desk') and o.type=='MESH'],key=lambda o:o.name)
targets=[(o.name, o.matrix_world.translation.copy()+Vector((0,0,0.45))) for o in desks]
for n in ['RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02','RAWL_1086_R10_Schematic_Lectern_Top']:
 o=bpy.data.objects.get(n)
 if o:targets.append((n,o.matrix_world.translation.copy()))
results=[]
for idx,c,n in panes:
 start=c+n*0.02
 for name,t in targets:
  d=t-start; length=d.length
  if length<0.1:continue
  direction=d/length
  hits=[]
  for wallname,tree in trees.items():
   loc,norm,face,dist=tree.ray_cast(start,direction,length)
   if loc is not None:hits.append((wallname,float(dist)))
  if not hits:results.append({'pane':idx,'target':name,'distance':round(length,3)})
results.sort(key=lambda x:x['distance'])
with open('audit/batch4_rawls/r11_sightline_matrix.json','w') as f:json.dump({'pane_count':len(panes),'target_count':len(targets),'clear_pairs':len(results),'examples':results[:100]},f,indent=2)
print(json.dumps({'pane_count':len(panes),'target_count':len(targets),'clear_pairs':len(results),'examples':results[:30]},indent=2))
