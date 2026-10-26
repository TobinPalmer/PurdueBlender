import bpy,json
from collections import Counter
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('modular/buildings/massing_northwestern_parking_garage_979f1a2.blend').resolve()))
o=bpy.data.objects['Northwestern Parking Garage']
levels=Counter(round((o.matrix_world@v.co).z,3) for v in o.data.vertices)
faces=Counter(round((o.matrix_world@sum((o.data.vertices[i].co for i in p.vertices),__import__('mathutils').Vector())/len(p.vertices)).z,3) for p in o.data.polygons)
print(json.dumps({'vertex_z_levels':levels,'face_center_z_levels':faces},indent=2))
