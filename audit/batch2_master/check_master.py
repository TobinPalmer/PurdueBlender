import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
before=json.loads((ROOT/'audit/batch2_master/manifest_before.json').read_text())
ids=['potter_engineering','mechanical_engineering','electrical_engineering','knoy_hall','class_of_1950']
rows=[]
for a in before['assets']:
    if a.get('kind')!='detailed': continue
    o=bpy.data.objects.get('Placement_'+a['id'])
    expected=a['placement_origin_xy_m']
    rows.append({'id':a['id'],'marker_present':o is not None,'expected_xy':expected,'actual_xyz':list(o.location) if o else None,'position_error_m':sum((o.location[i]-expected[i])**2 for i in range(2))**.5 if o else None,'rotation':list(o.rotation_euler) if o else None,'scale':list(o.scale) if o else None,'collection':o.instance_collection.name if o and o.instance_collection else None,'expected_collection':a['collection'],'export_objects':len(o.instance_collection.all_objects) if o and o.instance_collection else 0})
missing=[l.filepath for l in bpy.data.libraries if not Path(bpy.path.abspath(l.filepath)).is_file()]
errors=[r['id'] for r in rows if not r['marker_present'] or r['position_error_m']>.001 or r['collection']!=r['expected_collection'] or any(abs(v)>1e-6 for v in r['rotation']) or any(abs(v-1)>1e-6 for v in r['scale'])]
result={'rows':rows,'missing_libraries':missing,'errors':errors,'note':'Transform agreement with prior GIS-reviewed placement; does not verify facade or height.'}
(ROOT/'audit/batch2_master/placement_check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
if errors or missing: raise RuntimeError('Placement/link review failed')

