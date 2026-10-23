import bpy,json
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall'];o=bpy.data.objects['HAAS_Corrected_GIS_Wall_Envelope'];
rows=[]
for p in o.data.polygons:
 n=o.matrix_world.to_3x3()@p.normal;co=o.matrix_world@p.center
 if n.x>0.9:
  rows.append({'i':p.index,'c':[round(x,2) for x in co],'n':[round(x,2) for x in n],'a':round(p.area,2),'mat':p.material_index})
print(json.dumps({'materials':[m.name for m in o.data.materials],'east_faces':rows},indent=2))
