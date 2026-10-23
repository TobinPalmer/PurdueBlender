import bpy,json
from mathutils import Vector
w=bpy.data.objects['KNOY_Footprint_Reference_Wire'];v=[w.matrix_world@x.co for x in w.data.vertices]
open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch4_knoy\gis_vertices_local.json','w').write(json.dumps([[round(p.x,3),round(p.y,3)] for p in v],indent=2))
