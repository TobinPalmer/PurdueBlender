import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'black_cultural_center_independent_export.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
c=bpy.data.collections.get('Asset_black_cultural_center'); assert c
objs=list(c.all_objects); types={}
for o in objs: types[o.type]=types.get(o.type,0)+1
report={'probe_path':p.name,'opened_in':bpy.app.version_string,'collection':c.name,'object_count':len(objs),'type_counts':types,'camera_light_count':sum(o.type in {'CAMERA','LIGHT'} for o in objs),'linked_libraries':[l.filepath for l in bpy.data.libraries]}
(HERE/'independent_export_reopen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2)); assert len(objs)==621 and report['camera_light_count']==0
