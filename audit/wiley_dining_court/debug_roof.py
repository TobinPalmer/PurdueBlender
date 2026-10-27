import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wiley_dining_court_wdct_8a6c669.blend');bpy.ops.wm.open_mainfile(filepath=str(p));col=bpy.data.collections['Asset_massing_wiley_dining_court_wdct_8a6c669'];scene=bpy.data.scenes['Building_massing_wiley_dining_court_wdct_8a6c669'];
rows=[]
for o in col.objects:
 if 'gable' in o.name.lower() or 'roof' in o.name.lower() or o.name=='Wiley Dining Court (WDCT)':
  cs=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append({'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_for_exterior':o.get('hide_for_exterior_preview'),'hide_interior':o.get('hide_for_interior_preview'),'bounds':[[min(v[i] for v in cs),max(v[i] for v in cs)] for i in range(3)],'materials':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []})
print(json.dumps(rows,indent=2))
for o in col.objects:
 if 'roof' in o.name.lower() or 'gable' in o.name.lower():o.hide_render=True
root=bpy.data.objects['Wiley Dining Court (WDCT)'];root.hide_render=False
scene.render.filepath=str(Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\wiley_dining_court\previews\debug_no_roof.png'));bpy.ops.render.render(write_still=True)
