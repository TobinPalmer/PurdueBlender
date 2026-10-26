from pathlib import Path
import json
import bpy
HERE=Path(__file__).resolve().parent
PROBE=HERE/'collection_export_probe.blend'
bpy.ops.wm.open_mainfile(filepath=str(PROBE))
col=bpy.data.collections.get('Asset_armory')
assert col and col.get('building_id')=='armory' and col.get('owner')=='Rosen'
assert col.get('source_feature_id')==207
assert not any(o.type in {'CAMERA','LIGHT'} for o in col.all_objects)
assert bpy.data.objects.get('Armory_Rosen_Central_Stepped_Gable')
external=[img.filepath for img in bpy.data.images if img.filepath and img.source=='FILE' and not img.packed_file]
assert not external
res={'reopened_export':str(PROBE),'collection':col.name,'object_count':len(col.all_objects),'gable_present':True,'camera_light_objects':0,'external_unpacked_images':external,'linked_libraries':[lib.filepath for lib in bpy.data.libraries]}
(HERE/'export_probe_result.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2))
