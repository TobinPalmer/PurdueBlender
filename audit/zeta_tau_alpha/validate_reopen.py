"""Fresh-process candidate-file integrity check; not an architectural grade."""
import bpy, json, os, hashlib

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
PATH=os.path.join(ROOT,'modular','buildings','zeta_tau_alpha.blend')
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'reopen_validation.json')
ASSET_ID='massing_zeta_tau_alpha_af8a443'
COLL='Asset_'+ASSET_ID
bpy.ops.wm.open_mainfile(filepath=PATH)
scene=bpy.data.scenes.get('Building_'+ASSET_ID)
asset=bpy.data.collections.get(COLL)
assert scene is not None, 'Expected building scene missing'
assert asset is not None, 'Expected stable export collection missing'
objects=list(asset.all_objects)
shell=bpy.data.objects.get('ZTA_Continuous_Red_Brick_Exterior_Shell')
assert shell is not None and shell.type=='MESH'
assert len(shell.data.vertices)>0 and len(shell.data.polygons)>0
images=[]
for img in bpy.data.images:
    if img.source=='FILE':
        images.append({'name':img.name,'filepath':img.filepath,
                       'packed':img.packed_file is not None,
                       'size_px':list(img.size)})
broken=[img for img in images if not img['packed'] and not os.path.exists(bpy.path.abspath(img['filepath']))]
assert not broken, 'Missing un-packed image dependency: '+repr(broken)
origin=list(asset.get('placement_origin_xy_m',(None,None)))
assert len(origin)==2 and all(v is not None for v in origin)
report={
 'status':'PASS','file':os.path.relpath(PATH,ROOT).replace('\\','/'),
 'sha256':hashlib.sha256(open(PATH,'rb').read()).hexdigest(),
 'scene':scene.name,'export_collection':asset.name,
 'object_count':len(objects),'mesh_count':sum(o.type=='MESH' for o in objects),
 'material_count':len([m for m in bpy.data.materials if m.name.startswith('ZTA |')]),
 'shell_vertex_count':len(shell.data.vertices),'shell_polygon_count':len(shell.data.polygons),
 'shell_uv_layers':[uv.name for uv in shell.data.uv_layers],
 'local_bounds_m':[list(a) for a in shell.bound_box],
 'placement_origin_xy_m':origin,'images':images,'broken_external_images':broken,
 'candidate_is_separate_from_master':not os.path.samefile(PATH,os.path.join(ROOT,'purdue_campus_master.blend'))
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('ZTA_REOPEN_VALIDATION',json.dumps(report,indent=2))
