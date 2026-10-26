import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0]).resolve(); col=bpy.data.collections.get('Asset_birck_nanotechnology_center')
if col is None: raise RuntimeError('named export collection missing')
objects=list(col.objects); types={}
for o in objects: types[o.type]=types.get(o.type,0)+1
images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
libraries=[l.filepath for l in bpy.data.libraries if l.filepath]
r={'file':bpy.data.filepath,'blender_version':bpy.app.version_string,'collection':col.name,'object_count':len(objects),'object_names':sorted(o.name for o in objects),'types':types,'camera_or_light':any(o.type in {'CAMERA','LIGHT'} for o in objects),'unpacked_external_images':images,'linked_libraries':libraries}
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:v for k,v in r.items() if k!='object_names'},indent=2),flush=True)
