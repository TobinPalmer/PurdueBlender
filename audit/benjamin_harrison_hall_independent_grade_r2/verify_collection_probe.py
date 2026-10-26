import bpy, json, sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0]).resolve()
target='Asset_benjamin_harrison_hall'
col=bpy.data.collections.get(target)
if col is None: raise RuntimeError('Exported collection missing after reopening probe .blend')
objects=list(col.objects)
types={}
for o in objects: types[o.type]=types.get(o.type,0)+1
images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
libraries=[l.filepath for l in bpy.data.libraries if l.filepath]
result={'reopened_probe_file':bpy.data.filepath,'collection':target,'object_count':len(objects),'object_names':sorted(o.name for o in objects),'types':types,'camera_or_light':any(o.type in {'CAMERA','LIGHT'} for o in objects),'unpacked_external_images':images,'linked_libraries':libraries,'blender_version':bpy.app.version_string}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='object_names'},indent=2),flush=True)
