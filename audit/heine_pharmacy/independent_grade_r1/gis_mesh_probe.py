import bpy,json
from mathutils import Vector
ob=bpy.data.objects['RHPH structural shell | GIS outline']
vertices=[list(ob.matrix_world@v.co) for v in ob.data.vertices]
json.dump({'object':ob.name,'vertices':vertices,'faces':[list(p.vertices) for p in ob.data.polygons]},open('audit/heine_pharmacy/independent_grade_r1/shell_mesh.json','w'),indent=2)
print('vertices',len(vertices),'polys',len(ob.data.polygons))
