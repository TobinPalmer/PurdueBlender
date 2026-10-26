import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_hi_vine_dbdf0c5.blend')
o=bpy.data.objects['Hi Vine']; pts=[]
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if abs(p.z)<1e-4: pts.append([round(p.x,4),round(p.y,4)])
json.dump(pts,open(r'audit/massing_hi_vine_dbdf0c5/review/current_asset_footprint_xy.json','w'))
