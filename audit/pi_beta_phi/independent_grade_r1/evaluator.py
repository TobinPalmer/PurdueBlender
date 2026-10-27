import bpy, os, json, hashlib, math
from collections import Counter
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301838781_891384f.blend')
EXPECTED='8c1684ed6e4486fe2200af68600821c6c1f739db8939dd495ac5bdfe5b8e58c7'
OUT=os.path.join(os.path.dirname(__file__),'fresh_open_probe.json')
bpy.ops.wm.open_mainfile(filepath=ASSET)
sha=hashlib.sha256(open(ASSET,'rb').read()).hexdigest()
coll=bpy.data.collections.get('Asset_massing_house_301838781_891384f')
objs=list(coll.objects) if coll else []
mesh=[o for o in objs if o.type=='MESH']
pts=[]
for o in mesh:
    for v in o.data.vertices:
        pts.append(o.matrix_world @ v.co)
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
mats=Counter(m.name for o in mesh for m in o.data.materials if m)
external=[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE']
features=Counter()
for o in objs:
    n=o.name.lower()
    for k,terms in {'window':['window','sash','glazing'],'door':['door','entry'],'portico':['portico','column'],'roof':['roof','parapet','cornice'],'stairs':['stair','landing'],'interior':['interior','room','partition','furniture','bed','kitchen','lounge','study','floor_1','floor_2'],'brick':['brick']}.items():
        if any(t in n for t in terms): features[k]+=1
shell=bpy.data.objects.get('House_301838781')
report={
 'path':ASSET,'expected_sha256':EXPECTED,'sha256':sha,'sha_match':sha==EXPECTED,
 'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,
 'collection_present':coll is not None,'object_count':len(objs),'mesh_count':len(mesh),
 'bounds_local_m':bounds,'mesh_vertices':sum(len(o.data.vertices) for o in mesh),'mesh_polygons':sum(len(o.data.polygons) for o in mesh),
 'materials':dict(mats),'material_count':len(mats),'external_file_images':external,
 'linked_libraries':[x.filepath for x in bpy.data.libraries],
 'feature_named_object_counts':dict(features),
 'stable_shell_present':shell is not None,'shell_materials':[m.name if m else None for m in shell.data.materials] if shell else [],
 'has_camera':any(o.type=='CAMERA' for o in objs),'has_light':any(o.type=='LIGHT' for o in objs),
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
