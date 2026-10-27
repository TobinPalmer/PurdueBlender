import bpy,json
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wiley_dining_court_wdct_8a6c669.blend');bpy.ops.wm.open_mainfile(filepath=str(p));col=bpy.data.collections['Asset_massing_wiley_dining_court_wdct_8a6c669']
arr=[]
for o in col.objects:
 if any(t in o.name.lower() for t in ('truss','tie beam','pendant cable','vaulted oak','schematic dining table')):
  c=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]
  arr.append({'name':o.name,'hideext':o.get('hide_for_exterior_preview'),'hide_render':o.hide_render,'bounds':[[min(v[i] for v in c),max(v[i] for v in c)] for i in range(3)]})
print(json.dumps({'count':len(arr),'sample':arr[:12]},indent=2))
