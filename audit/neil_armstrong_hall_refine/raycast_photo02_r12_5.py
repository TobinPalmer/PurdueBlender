import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
origin=Vector((-100,-35,1.7));target=Vector((0,-5,10));q=(target-origin).to_track_quat('-Z','Y');dep=bpy.context.evaluated_depsgraph_get();rows=[]
for u in [-.8,-.4,0,.4,.8]:
 for v in [-.4,-.2,0,.2,.4]:
  locdir=q@Vector((u*1.5,v*1.5,-1)).normalized();hit,pt,n,idx,obj,mat=bpy.context.scene.ray_cast(dep,origin,locdir,distance=500)
  if hit:
   mi=obj.data.polygons[idx].material_index if obj.type=='MESH' else -1
   m=obj.data.materials[mi].name if obj.type=='MESH' and mi<len(obj.data.materials) else None
   rows.append({'u':u,'v':v,'obj':obj.name,'mat':m,'point':[round(z,2) for z in pt]})
print(json.dumps(rows,indent=2))
