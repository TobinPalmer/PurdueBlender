import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[0]).resolve(); bpy.ops.wm.open_mainfile(filepath=str(out.parent.parent.parent/'purdue_campus_master.blend'))
matched=[]
for o in bpy.data.objects:
    if 'birck' in o.name.lower() or (o.type=='EMPTY' and 'placement' in o.name.lower()):
        if 'birck' in o.name.lower():
            matched.append({'name':o.name,'type':o.type,'location_world':list(o.matrix_world.translation),'instance_type':o.instance_type,'instance_collection':o.instance_collection.name if o.instance_collection else None,'library':o.library.filepath if o.library else None,'collections':[c.name for c in o.users_collection]})
scene_links=[]
for c in bpy.data.collections:
    if 'birck' in c.name.lower(): scene_links.append({'name':c.name,'library':c.library.filepath if c.library else None,'objects':len(c.objects),'children':len(c.children)})
r={'master_path':bpy.data.filepath,'blender_version':bpy.app.version_string,'birck_objects':matched,'birck_collections':scene_links}
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2),flush=True)
