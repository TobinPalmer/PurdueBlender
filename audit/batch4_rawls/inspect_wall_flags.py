import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
fp=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
verts=[fp.matrix_world@v.co for v in fp.data.vertices[:29]]
poly=[(v.x,v.y) for v in verts]
def inside(x,y):
 c=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i]; xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
  j=i
 return c
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  c=sum(pts,Vector())/8
  if not inside(c.x,c.y):
   rows.append({'name':o.name,'center':[round(c.x,3),round(c.y,3),round(c.z,3)],'xy_bbox':[[round(min(p[k] for p in pts),3),round(max(p[k] for p in pts),3)] for k in range(2)],'world_dims':[round(max(p[k] for p in pts)-min(p[k] for p in pts),3) for k in range(3)],'inside':inside(c.x,c.y)})
with open('audit/batch4_rawls/round2_wall_flags.json','w') as f:json.dump({'polygon':poly,'outside':rows},f,indent=2)
print(json.dumps({'count':len(rows),'outside':rows},indent=2))
