import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
asset=root/'modular'/'buildings'/'massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend'
expected='B90ADA781E76E8C7C3A08B59D95A28CD97CFA763C59D09278DDDA99781F0707E'
sha=hashlib.sha256(asset.read_bytes()).hexdigest().upper()
assert sha==expected, f'Unexpected candidate SHA256 {sha}'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene_name='Building_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
collection_name='Asset_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
scene=bpy.data.scenes.get(scene_name); col=bpy.data.collections.get(collection_name)
assert scene and col
objs=list(col.all_objects); meshes=[o for o in objs if o.type=='MESH']
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
missing=[o.name for o in meshes if not o.data.materials]
unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
bounds={'min':[min((o.matrix_world@Vector(c))[i] for o in meshes for c in o.bound_box) for i in range(3)],'max':[max((o.matrix_world@Vector(c))[i] for o in meshes for c in o.bound_box) for i in range(3)]}
props={str(k):str(col[k]) for k in col.keys()}
counts={}
for prefix in ['LSR_Greenhouse_','LSR_Service_','LSR_Interior_','LSR_Conveyor','LSR_Bench','LSR_Plant','LSR_Frame','LSR_Glass']:
 counts[prefix]=sum(1 for o in objs if o.name.startswith(prefix))
for obj in sorted(objs,key=lambda o:o.name):
 if 'Roof' in obj.name or 'Ridge' in obj.name or 'Eave' in obj.name or 'Service' in obj.name:
  pass
out={'asset':str(asset),'sha256':sha,'scene':scene.name,'collection':col.name,'object_count':len(objs),'mesh_count':len(meshes),'material_count':len(materials),'materials':materials,'missing_material_meshes':missing,'unpacked_external_images':unpacked,'bounds_m':bounds,'collection_properties':props,'feature_counts':counts}
Path(__file__).resolve().parent.joinpath('fresh_open_probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
