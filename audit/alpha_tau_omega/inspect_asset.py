import bpy, json
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'modular/buildings/massing_house_301840870_c45a5f4.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
out={'scenes':[s.name for s in bpy.data.scenes], 'collections':[c.name for c in bpy.data.collections], 'objects':[]}
for o in bpy.data.objects:
 if o.name=='House_301840870' or o.name.startswith('House_301840870'):
  out['objects'].append({'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),'matrix_world':[[v for v in row] for row in o.matrix_world], 'vertices':len(o.data.vertices) if o.type=='MESH' else None,'polygons':len(o.data.polygons) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []})
print(json.dumps(out,indent=2))
