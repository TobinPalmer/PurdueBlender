import bpy,json,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
fp=bpy.data.objects['RAWL_FloorSlab_L1_Ground']; poly=[( (fp.matrix_world@fp.data.vertices[i].co).x, (fp.matrix_world@fp.data.vertices[i].co).y) for i in range(29)]
def inside(x,y):
 c=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
  j=i
 return c
def edge_dist(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy+1e-20)));return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('RAWL_2026_Plan'):continue
 ps=[o.matrix_world@Vector(c) for c in o.bound_box]; c=(sum(p.x for p in ps)/8,sum(p.y for p in ps)/8)
 if not inside(*c):
  outpts=[(p.x,p.y) for p in ps if not inside(p.x,p.y)]
  distances=[min(edge_dist(q,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))) for q in outpts]
  rows.append({'name':o.name,'centroid_xy':[round(x,2) for x in c],'centroid_nearest_edge_m':round(min(edge_dist(c,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))),2),'bbox_corners_outside':len(outpts),'bbox_max_outside_distance_m':round(max(distances),2),'bbox_mean_outside_distance_m':round(sum(distances)/len(distances),2)})
with open('audit/batch4_rawls/round2_wall_edge_review.json','w') as f:json.dump(rows,f,indent=2)
print(json.dumps(rows,indent=2))
