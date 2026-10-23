import bpy,json
from mathutils import Vector
o=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope']
r=[]
for p in o.data.polygons:
 n=o.matrix_world.to_3x3()@p.normal;c=o.matrix_world@p.center
 if n.y < -0.9 and abs(c.y+11.7)<0.4:r.append({'f':p.index,'c':[round(x,2) for x in c],'n':[round(x,2) for x in n],'a':round(p.area,2)})
print(json.dumps(r,indent=2))
