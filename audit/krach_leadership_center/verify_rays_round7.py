import bpy,json
from mathutils import Vector
s=bpy.data.objects['KRCH structural shell | GIS outline']
checks=[]
for name,o,d in [('end_opening',(-36,-12.70,4.88),(1,0,0)),('end_brick',(-36,-13.4,4.88),(1,0,0)),('south_window', (9.3,-16,4.88),(0,1,0)),('south_brick',(7,-16,4.88),(0,1,0)),('storefront',(10,-16,1.5),(0,1,0)),('above_storefront',(10,-16,3.6),(0,1,0))]:
 origin=s.matrix_world.inverted()@Vector(o);direction=s.matrix_world.inverted().to_3x3()@Vector(d);hit,loc,n,fi=s.ray_cast(origin,direction);checks.append({'name':name,'hit':hit,'location':list(loc) if hit else None,'face':fi})
print(json.dumps(checks,indent=2))
