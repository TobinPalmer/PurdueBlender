import bpy,json
from mathutils import Vector
p=r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_hillenbrand_hall_a71e418.blend'
outpath=r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\audit\massing_hillenbrand_hall_a71e418\review\direct_reopen_r3.json'
bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.data.scenes.get('Building_massing_hillenbrand_hall_a71e418')
coll=bpy.data.collections.get('Asset_massing_hillenbrand_hall_a71e418')
objs=[o for o in bpy.data.objects if o.type=='MESH']
checks={'scene_exists':scene is not None,'collection_exists':coll is not None,'one_mesh':len(objs)==1,'object_name':len(objs)==1 and objs[0].name=='Hillenbrand Hall','mesh_in_export_collection':len(objs)==1 and coll is not None and objs[0].name in coll.objects,'identity_transform':len(objs)==1 and all(abs(x)<1e-6 for x in objs[0].location) and all(abs(x-1)<1e-6 for x in objs[0].scale),'no_modifiers':len(objs)==1 and len(objs[0].modifiers)==0,'no_external_images':all(not im.filepath for im in bpy.data.images if im.source=='FILE')}
items=[]
for o in objs:
 b=[o.matrix_world @ Vector(c) for c in o.bound_box]
 items.append({'name':o.name,'verts':len(o.data.vertices),'faces':len(o.data.polygons),'bounds_world_m':[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(3)],'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'materials':[m.name for m in o.data.materials],'modifiers':[m.name for m in o.modifiers],'asset_id':o.get('asset_id'),'floor_count_status':o.get('floor_count_status'),'height_status':o.get('height_status'),'roof_status':o.get('roof_status'),'entry_status':o.get('entry_status')})
result={'asset':p,'blender_version':bpy.app.version_string,'scene':scene.name if scene else None,'collection':coll.name if coll else None,'object_count':len(objs),'objects':items,'checks':checks,'all_checks_pass':all(checks.values())}
open(outpath,'w',encoding='utf-8').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
