import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('modular/buildings/massing_northwestern_parking_garage_979f1a2.blend').resolve()))
o=bpy.data.objects['Northwestern Parking Garage']
levels=sorted(set(round(float((o.matrix_world@v.co).z),4) for v in o.data.vertices))
print(json.dumps({'verts':len(o.data.vertices),'faces':len(o.data.polygons),'levels':levels,'face_levels':sorted(set(round(float((o.matrix_world@sum((o.data.vertices[i].co for i in p.vertices),__import__('mathutils').Vector())/len(p.vertices)).z),4) for p in o.data.polygons))},indent=2))
