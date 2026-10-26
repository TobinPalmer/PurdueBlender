import bpy, json
from mathutils import Vector
path = r"C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_chi_omega_a9eb08d.blend"
with bpy.data.libraries.load(path, link=False) as (src,dst):
 dst.objects = src.objects
objs=[o for o in bpy.data.objects if o.type=='MESH']
for o in objs:
 vs=[o.matrix_world @ Vector(c) for c in o.bound_box]
 print(o.name, 'verts',len(o.data.vertices),'faces',len(o.data.polygons),'bounds',[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],'dims',list(o.dimensions),'materials',[m.name if m else None for m in o.data.materials])
