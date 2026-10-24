import bpy, os, json
ROOT=os.path.abspath('.')
MASTER=os.path.abspath(os.path.join(ROOT,'purdue_campus_master.blend'))
ASSET_ID='materials_science_and_electrical_engineering_msee'
COLLECTION='Asset_'+ASSET_ID
EXPECTED=[87.421,215.992]
bpy.ops.wm.open_mainfile(filepath=MASTER)
matches=[]
for o in bpy.data.objects:
    if o.instance_type=='COLLECTION' and o.instance_collection and o.instance_collection.name==COLLECTION:
        m=o.matrix_world
        lib=o.instance_collection.library
        lib_path=lib.filepath if lib else None
        lib_abs=bpy.path.abspath(lib_path) if lib_path else None
        matches.append({'object':o.name,'instance_collection':o.instance_collection.name,
                        'collection_library_filepath':lib_path,
                        'collection_library_resolved_path':lib_abs,
                        'collection_library_file_exists':bool(lib_abs and os.path.exists(lib_abs)),
                        'location_world_m':[round(float(v),4) for v in m.translation],
                        'scale_world':[round(float(v),6) for v in m.to_scale()],
                        'rotation_euler_rad':[round(float(v),7) for v in m.to_euler()],
                        'translation_matches_manifest_xy_within_0_02m':
                         abs(m.translation.x-EXPECTED[0])<=.02 and abs(m.translation.y-EXPECTED[1])<=.02})
report={'building_id':ASSET_ID,'master_path':os.path.relpath(MASTER,ROOT).replace('/','\\'),
        'opened_read_only':True,'expected_manifest_placement_origin_xy_m':EXPECTED,
        'matching_collection_instances':matches,
        'pass':len(matches)==1 and matches[0]['collection_library_file_exists'] and
               os.path.normcase(os.path.abspath(matches[0]['collection_library_resolved_path']))==os.path.normcase(os.path.abspath(os.path.join(ROOT,'modular','buildings',ASSET_ID+'.blend'))) and
               matches[0]['translation_matches_manifest_xy_within_0_02m'] and
               max(abs(s-1.0) for s in matches[0]['scale_world'])<1e-6}
out=os.path.join(ROOT,'audit','rework_batch_a',ASSET_ID+'_R6_master_registration_readonly.json')
with open(out,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
