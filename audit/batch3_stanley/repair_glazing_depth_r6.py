"""Put R6 east glazing on the visible facade plane and refresh the saved hash."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_stanley_coulter_hall']
archive=bpy.data.collections['SC_Archived_Facade_Windows_R6']
def bounds(o):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def transform(o):
    if o.data.users>1:o.data=o.data.copy()
    inv=o.matrix_world.inverted()
    for v in o.data.vertices:
        p=o.matrix_world@v.co;p.x+=0.26;v.co=inv@p
    o.data.update()
existing=[o for o in asset.all_objects if o.name.startswith('SC_R6_East_Glazing_')]
if len(existing)!=14:raise RuntimeError(f'Expected 14 R6 glazing objects; found {len(existing)}')
old_trim=bpy.data.objects.get('SC_Win_East_Level3_ThirdFloor_0_LimestoneTrim')
target= max(p[0] for p in [old_trim.matrix_world@Vector(c) for c in old_trim.bound_box]) if old_trim else None
before={o.name:bounds(o) for o in existing}
for o in existing:transform(o)
bpy.context.view_layer.update()
after={o.name:bounds(o) for o in existing}
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'asset':str(ASSET),'sha256':sha,'glazing_object_count':len(existing),'translation_x_m':0.26,'comparison_reference_limestone_frame_xmax_m':target,'bounds_before':before,'bounds_after':after,'archived_window_count':len(archive.all_objects),'note':'Moved the R6 glass ribbons, limestone rails, and mullions outward to the exterior plane, so they cover the uncut brick backing instead of sitting behind it.'}
(ROOT/'audit/batch3_stanley/glazing_depth_r6.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
