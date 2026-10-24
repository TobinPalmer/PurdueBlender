import bpy, os, json, math
ROOT=os.path.abspath('.')
ASSET_ID='math_sciences'
MASTER=os.path.join(ROOT,'purdue_campus_master.blend')
EXPECTED=(-181.1199951171875,-126.90500259399414)
COLLECTION='Asset_math_sciences'
bpy.ops.wm.open_mainfile(filepath=MASTER)
matches=[]
for o in bpy.data.objects:
    if o.instance_type=='COLLECTION' and o.instance_collection and o.instance_collection.name==COLLECTION:
        m=o.matrix_world; lib=o.instance_collection.library
        source=lib.filepath if lib else None
        source_abs=bpy.path.abspath(source) if source else None
        rot=m.to_euler()
        matches.append({'placement_object':o.name,'collection':o.instance_collection.name,
            'library_path':source,'resolved_library_path':source_abs,
            'library_exists':bool(source_abs and os.path.exists(source_abs)),
            'location_world_m':[round(float(x),6) for x in m.translation],
            'scale':[round(float(x),8) for x in m.to_scale()],
            'rotation_euler_rad':[round(float(x),8) for x in rot],
            'translation_matches_manifest_within_0_02m':
                abs(m.translation.x-EXPECTED[0])<=.02 and abs(m.translation.y-EXPECTED[1])<=.02})
expected_library=os.path.normcase(os.path.abspath(os.path.join(ROOT,'modular','buildings','math_sciences.blend')))
report={'building_id':ASSET_ID,'master_file':'purdue_campus_master.blend','opened_read_only':True,
    'expected_manifest_origin_xy_m':list(EXPECTED),'matching_instances':matches,
    'pass':len(matches)==1 and matches[0]['library_exists'] and
        os.path.normcase(os.path.abspath(matches[0]['resolved_library_path']))==expected_library and
        matches[0]['translation_matches_manifest_within_0_02m'] and
        all(abs(x-1)<1e-6 for x in matches[0]['scale']) and
        all(abs(x)<1e-6 for x in matches[0]['rotation_euler_rad'])}
out=os.path.join(ROOT,'audit','batch3_math','independent_review_round8_registration.json')
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
