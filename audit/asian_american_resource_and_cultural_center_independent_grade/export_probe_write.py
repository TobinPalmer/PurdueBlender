import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=ROOT/'modular/buildings/asian_american_resource_and_cultural_center.blend'
out=HERE/'independent_collection_export_probe.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
c=bpy.data.collections.get('Asset_asian_american_resource_and_cultural_center')
assert c and len(c.all_objects)==433
bpy.data.libraries.write(str(out),{c},fake_user=True,compress=True)
(HERE/'portable_export_probe_write.json').write_text(json.dumps({'source':str(source),'output':str(out),'source_object_count':len(c.all_objects)},indent=2)+'\n')
print('WROTE',out,'objects',len(c.all_objects))
