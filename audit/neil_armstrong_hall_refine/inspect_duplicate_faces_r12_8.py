import bpy,json
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
bpy.ops.wm.open_mainfile(filepath=ROOT+r'\modular\buildings\neil_armstrong_hall.blend')
o=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']; xyz=[o.matrix_world@v.co for v in o.data.vertices]; seen={};dups=[]
for p in o.data.polygons:
 k=tuple(sorted(tuple(round(float(c),5) for c in xyz[i]) for i in p.vertices))
 if k in seen:
  pts=[xyz[i] for i in p.vertices]
  dups.append({'index':p.index,'first':seen[k],'verts':list(p.vertices),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'mat':p.material_index})
 else:seen[k]=p.index
print(json.dumps({'duplicate_count':len(dups),'duplicates':dups},indent=2))
