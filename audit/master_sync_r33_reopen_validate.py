import bpy, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.path.abspath('//'))
manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
assets={a['id']:a for a in manifest['assets']}
def rel(p): return os.path.normcase(os.path.abspath(bpy.path.abspath(p)))
def bbox(o):
 c=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in c),max(v[i] for v in c)] for i in range(3)]
master=Path(bpy.data.filepath)
assert master.name=='purdue_campus_master.blend'
libs=[{'path':l.filepath,'exists':os.path.exists(bpy.path.abspath(l.filepath))} for l in bpy.data.libraries]
missing=[l for l in libs if not l['exists']]
assert not missing
cqs=assets['massing_cary_quadrangle_south_cqs_7ee2283']; cqsobj=bpy.data.objects.get('Cary Quadrangle South (CQS)')
assert cqsobj and cqsobj.library and rel(cqsobj.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/cqs['file']))
assert max(abs(bbox(cqsobj)[i][j]-cqs['bounds_world_m'][i][j]) for i in range(3) for j in range(2))<0.01
duhme=assets['massing_duhme_ophelia_residence_hall_1bb4e9c']; dc=bpy.data.collections.get(duhme['collection'])
assert dc and dc.library and rel(dc.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/duhme['file'])) and len(dc.all_objects)==1491
earhart=assets['massing_earhart_hall_0f14209']; ec=bpy.data.collections.get(earhart['collection'])
assert ec and ec.library and rel(ec.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/earhart['file'])) and len(ec.all_objects)==25
assert max(abs((lambda c: [[min(v[i] for v in c),max(v[i] for v in c)] for i in range(3)])([o.matrix_world@Vector(v) for o in ec.all_objects if o.type=='MESH' for v in o.bound_box])[i][j]-earhart['bounds_world_m'][i][j]) for i in range(3) for j in range(2))<0.01
burton=assets['burton_morgan_center']; markers=[o for o in bpy.context.scene.objects if o.name=='Placement_burton_morgan_center']
assert len(markers)==1 and markers[0].instance_collection and markers[0].instance_collection.name==burton['collection']
assert rel(markers[0].instance_collection.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/burton['file']))
assert len(markers[0].instance_collection.all_objects)==384
expected=burton['placement_origin_xy_m']+[0.0]
assert max(abs(markers[0].location[i]-expected[i]) for i in range(3))<0.001
linked_counts={}
for o in bpy.context.scene.objects:
 if o.library:
  key=os.path.basename(bpy.path.abspath(o.library.filepath)).lower()
  linked_counts[key]=linked_counts.get(key,0)+1
report={'status':'PASS','fresh_reopen':True,'master':str(master),'blender_version':bpy.app.version_string,'scene_object_count':len(bpy.context.scene.objects),'data_object_count':len(bpy.data.objects),'placement_markers':sum(o.name.startswith('Placement_') for o in bpy.context.scene.objects),'library_count':len(libs),'missing_library_count':len(missing),'linked_scene_object_counts':{k:v for k,v in linked_counts.items() if k in {os.path.basename(cqs['file']).lower(),os.path.basename(duhme['file']).lower(),os.path.basename(earhart['file']).lower()}},'CQS':{'path':cqsobj.library.filepath,'name':cqsobj.name,'bounds_world_m':bbox(cqsobj)},'Duhme':{'path':dc.library.filepath,'collection':dc.name,'object_count':len(dc.all_objects)},'Earhart':{'path':ec.library.filepath,'collection':ec.name,'object_count':len(ec.all_objects)},'Burton':{'marker':markers[0].name,'path':markers[0].instance_collection.library.filepath,'collection':markers[0].instance_collection.name,'object_count':len(markers[0].instance_collection.all_objects),'location_m':list(markers[0].location)}}
p=ROOT/'audit/master_sync_r33_handoffs.json'
prior=json.loads(p.read_text(encoding='utf8')) if p.exists() else {}
prior['fresh_reopen']=report
p.write_text(json.dumps(prior,indent=2)+'\n',encoding='utf8')
print('MASTER_SYNC_R33_REOPEN',json.dumps({'scene_objects':report['scene_object_count'],'data_objects':report['data_object_count'],'markers':report['placement_markers'],'libraries':report['library_count'],'missing':report['missing_library_count'],'linked_counts':report['linked_scene_object_counts']}))
