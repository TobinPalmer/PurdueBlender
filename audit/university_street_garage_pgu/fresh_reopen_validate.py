import bpy,json,os,math,hashlib
from mathutils import Vector
p=bpy.data.filepath
id='massing_university_street_parking_garage_pgu_be81bec'
name='Asset_'+id
c=bpy.data.collections.get(name)
assert bpy.context.scene.name=='Building_'+id
assert c is not None
assert len(c.objects)>0
pts=[]
for o in c.objects:
    if o.type!='MESH': continue
    deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
    for v in me.vertices: pts.append(o.matrix_world @ v.co)
    ev.to_mesh_clear()
assert pts
mins=[min(v[i] for v in pts) for i in range(3)]; maxs=[max(v[i] for v in pts) for i in range(3)]
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        external.append(im.filepath)
result={'status':'PASS','asset_path':p,'scene':bpy.context.scene.name,'expected_scene':'Building_'+id,'collection':c.name,'object_count':len(c.objects),'mesh_object_count':sum(o.type=='MESH' for o in c.objects),'local_bounds_m':{'min':mins,'max':maxs,'dimensions':[maxs[i]-mins[i] for i in range(3)]},'placement_origin_xy_m':list(c.get('placement_origin_xy_m',[])),'unpacked_external_image_paths':external,'materials':sorted({m.name for o in c.objects for m in o.data.materials if m}),'camera_count':sum(o.type=='CAMERA' for o in bpy.context.scene.objects)}
with open(os.path.join(os.path.dirname(p),'..','..','audit','university_street_garage_pgu','fresh_reopen_validation.json'),'w') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
