import bpy,json,os
from pathlib import Path
s=bpy.context.scene
P=Path(__file__).resolve().parent
records=[]
for t in (0.,6.,12.,18.):
 s['campus_time']=t;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get()
 key=bpy.data.objects['Campus Sunset Sun'].evaluated_get(dg)
 drivers=list(s.world.node_tree.animation_data.drivers)+list(bpy.data.objects['Campus Sunset Sun'].data.animation_data.drivers)
 records.append({'hour':t,'sun_energy':key.data.energy,'all_drivers_valid':all(fc.driver.is_valid for fc in drivers),'all_drivers_simple':all(fc.driver.is_simple_expression for fc in drivers)})
s['campus_time']=18.;s.update_tag();s.frame_set(s.frame_current);bpy.context.view_layer.update()
r={'file':bpy.data.filepath,'time_checks':records,'default_hour':s['campus_time'],'missing_libraries':[l.filepath for l in bpy.data.libraries if not os.path.exists(bpy.path.abspath(l.filepath))],'render_files':[p.name for p in (P/'renders').glob('*sunset.png')],'scene_suns':[o.name for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN']}
(P/'final_validation.json').write_text(json.dumps(r,indent=2))
print('FINAL_SKY_VALIDATION',json.dumps(r),flush=True)
assert all(x['all_drivers_valid'] and x['all_drivers_simple'] for x in records)
assert not r['missing_libraries']
