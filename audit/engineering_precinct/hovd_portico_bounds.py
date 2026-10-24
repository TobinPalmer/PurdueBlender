import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'modular/buildings/hovde_hall.blend'
with bpy.data.libraries.load(str(p),link=False) as (src,dst): dst.collections=['Asset_hovde_hall']
c=dst.collections[0]
for o in c.all_objects:
 if any(k in o.name.lower() for k in ('column','portico','entablature','cornice')):
  pts=[o.matrix_world @ __import__('mathutils').Vector(corner) for corner in o.bound_box]
  lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
  print(o.name,[round(q,1) for q in lo],[round(q,1) for q in hi])
