"""Correct the confirmed hall/dining-court identity placement error; retain size uncertainty."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
root=P.parent
asset=root/'modular/buildings/wiley_hall.blend'
backup=P/'wiley_hall_before_placement.blend'
if not backup.exists():shutil.copy2(asset,backup)
bpy.ops.wm.open_mainfile(filepath=str(asset))
if bpy.context.scene.get('wiley_location_correction_applied'):raise RuntimeError('Correction already applied')
sel=json.loads((P/'shell_selectors.json').read_text())
names=next(x['object_names'] for x in sel['buildings'] if x['group_id']=='wiley_hall')
from mathutils import Vector
pts=[o.matrix_world@Vector(c) for o in bpy.context.scene.objects if o.name in names for c in o.bound_box]
before=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
ref=next(x for x in json.loads((P/'official_building_references.json').read_text())['buildings'] if x['code']=='WILY')
b=ref['aabb_xy_m']
delta=Vector(((b[0]+b[2]-sum(before[0]))/2,(b[1]+b[3]-sum(before[1]))/2,0))
objects=list(bpy.context.scene.objects)
for o in objects:
 if o.parent is None and not o.hide_viewport:
  mat=o.matrix_world.copy();mat.translation+=delta;o.matrix_world=mat
bpy.context.view_layer.update()
bpy.context.scene['wiley_location_correction_applied']=True
bpy.context.scene['placement_status']='Hall moved from Dining Court location to official WILY footprint center; shell dimensions remain unverified'
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
record={'asset_id':'wiley_hall','file':'modular/buildings/wiley_hall.blend','objects':[o.name for o in objects],'translation_m':list(delta),'source_code':'WILY','source_fid':ref['fid'],'source_url':json.loads((P/'official_building_references.json').read_text())['source'],'evidence':'Importer/test_wiley_import.py targets (-599.2,125.6), matching WDCT dining court, despite importing residence hall geometry. Reviewed hall identity and translated its shell envelope center to official WILY envelope center.','method':'Confirmed building identity correction; envelope-center placement approximation, no scaling or rotation','before_shell_bounds_m':before,'official_bounds_xy_m':b,'dimension_status':'Unresolved: model shell is approximately 9.77m narrower and 8.70m shallower than official envelope. No arbitrary scaling applied.','position_status':'Gross identity/location corrected; exact wall registration still unverified','height_status':'unverified'}
(P/'placement_corrections.json').write_text(json.dumps([record],indent=2))
print('WILEY_CORRECTED',list(delta),flush=True)
