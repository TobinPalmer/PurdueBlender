import bpy,json,math
from mathutils import Vector
from math import tan
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
origin=Vector((-19.1,-14.9,1.7)); target=Vector((0,15,5))
q=(target-origin).to_track_quat('-Z','Y')
deps=bpy.context.evaluated_depsgraph_get(); out=[]
# render horizontal normalized coordinate; lens 24 mm, 36 mm sensor width
for u in [-0.9,-0.7,-0.5,-0.3,0,0.3,0.6,0.9]:
 local=Vector((u*(36/24),0,-1)).normalized(); direction=q@local
 hit,loc,nor,idx,obj,mat=bpy.context.scene.ray_cast(deps,origin,direction,distance=300)
 out.append({'u':u,'hit':bool(hit),'object':obj.name if obj else None,'point':[round(v,3) for v in loc] if hit else None,'dist':round((loc-origin).length,3) if hit else None,'material':obj.data.materials[obj.data.polygons[idx].material_index].name if obj and obj.type=='MESH' and idx>=0 and obj.data.materials else None})
print(json.dumps(out,indent=2))

