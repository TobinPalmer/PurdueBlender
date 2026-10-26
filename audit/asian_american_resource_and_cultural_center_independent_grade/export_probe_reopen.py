import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/'independent_collection_export_probe.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
c=bpy.data.collections.get('Asset_asian_american_resource_and_cultural_center')
assert c is not None
objects=list(c.all_objects)
types={}
for o in objects: types[o.type]=types.get(o.type,0)+1
report={'probe_path':p.name,'opened_in':bpy.app.version_string,'collection':c.name,'object_count':len(objects),'type_counts':types,'camera_or_light_count':sum(o.type in {'CAMERA','LIGHT'} for o in objects),'external_libraries':[l.filepath for l in bpy.data.libraries]}
(HERE/'portable_export_probe_reopen.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert len(objects)==433 and report['camera_or_light_count']==0
