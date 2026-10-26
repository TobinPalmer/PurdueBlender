import bpy, json, os, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(bpy.path.abspath('//'))
MASTER=Path(bpy.data.filepath)
manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
by_id={a['id']:a for a in manifest['assets']}

def bbox_world(obj):
    coords=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]

def relative_path(path):
    return os.path.normcase(os.path.abspath(bpy.path.abspath(path)))

def bounds_collection(coll):
    bounds=[]
    for obj in coll.all_objects:
        if obj.type!='MESH':
            continue
        co=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        bounds.append([[min(v[i] for v in co),max(v[i] for v in co)] for i in range(3)])
    return [[min(b[i][0] for b in bounds),max(b[i][1] for b in bounds)] for i in range(3)]

assert MASTER.name=='purdue_campus_master.blend',MASTER
assert bpy.context.scene is not None

# CQS is a direct campus-coordinate library link.
cqs_id='massing_cary_quadrangle_south_cqs_7ee2283'
cqs=by_id[cqs_id]
cqs_obj=bpy.data.objects.get('Cary Quadrangle South (CQS)')
assert cqs_obj and cqs_obj.library, 'CQS linked object missing'
assert relative_path(cqs_obj.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/cqs['file']))
cqs_bound=bbox_world(cqs_obj)
assert max(abs(cqs_bound[i][j]-cqs['bounds_world_m'][i][j]) for i in range(3) for j in range(2))<0.01
assert sum(bool(o.library and relative_path(o.library.filepath)==relative_path(cqs_obj.library.filepath)) for o in bpy.context.scene.objects)==1

# Duhme is directly linked in campus coordinates; the stable collection now exports full geometry.
duhme_id='massing_duhme_ophelia_residence_hall_1bb4e9c'
duhme=by_id[duhme_id]
duhme_coll=bpy.data.collections.get(duhme['collection'])
assert duhme_coll and duhme_coll.library, 'Duhme linked collection missing'
assert relative_path(duhme_coll.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/duhme['file']))
assert len(duhme_coll.all_objects)==duhme['object_count']==1491
assert len([c for c in bpy.data.collections if c.name==duhme['collection']])==1
duhme_bound=bounds_collection(duhme_coll)
assert max(abs(duhme_bound[i][j]-duhme['bounds_world_m'][i][j]) for i in range(3) for j in range(2))<0.01

# Earhart is a direct campus-coordinate library link with its reviewed 25-object model.
earhart_id='massing_earhart_hall_0f14209'
earhart=by_id[earhart_id]
earhart_coll=bpy.data.collections.get(earhart['collection'])
assert earhart_coll and earhart_coll.library, 'Earhart linked collection missing'
assert relative_path(earhart_coll.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/earhart['file']))
assert len(earhart_coll.all_objects)==earhart['object_count']==25
assert len([c for c in bpy.data.collections if c.name==earhart['collection']])==1
earhart_bound=bounds_collection(earhart_coll)
assert max(abs(earhart_bound[i][j]-earhart['bounds_world_m'][i][j]) for i in range(3) for j in range(2))<0.01
source_path=relative_path(earhart_coll.library.filepath)
earhart_scene_objects=[o for o in bpy.context.scene.objects if o.library and relative_path(o.library.filepath)==source_path]
assert len(earhart_scene_objects)==25, f'Expected 25 Earhart scene-linked objects, got {len(earhart_scene_objects)}'

# Burton is a local detailed collection instance at its manifest origin.
burton_id='burton_morgan_center'
burton=by_id[burton_id]
markers=[o for o in bpy.context.scene.objects if o.name=='Placement_burton_morgan_center']
assert len(markers)==1, f'Expected one Burton placement marker, got {len(markers)}'
marker=markers[0]
assert marker.instance_type=='COLLECTION' and marker.instance_collection, 'Burton collection instance missing'
assert marker.instance_collection.name==burton['collection']
assert relative_path(marker.instance_collection.library.filepath)==os.path.normcase(os.path.abspath(ROOT/'modular'/burton['file']))
assert len(marker.instance_collection.all_objects)==burton['object_count']==384
expected=burton['placement_origin_xy_m']+[0.0]
assert max(abs(marker.location[i]-expected[i]) for i in range(3))<0.001
assert all(abs(v-1.0)<1e-6 for v in marker.scale)

libs=[{'filepath':lib.filepath,'exists':os.path.exists(bpy.path.abspath(lib.filepath))} for lib in bpy.data.libraries]
missing=[lib for lib in libs if not lib['exists']]
assert not missing,missing

# Tobin is the coordinator on this machine: save the verified, freshly resolved master state.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_mainfile(filepath=str(MASTER))

report={
 'status':'PASS','saved':True,'master':str(MASTER),'blender_version':bpy.app.version_string,
 'scene_object_count':len(bpy.context.scene.objects),'placement_markers':sum(o.name.startswith('Placement_') for o in bpy.context.scene.objects),
 'library_count':len(libs),'missing_library_count':len(missing),
 'assets':{
  earhart_id:{'linked_file':earhart_coll.library.filepath,'collection':earhart_coll.name,'object_count':len(earhart_coll.all_objects),'bounds_world_m':earhart_bound,'grade':8.0},
  cqs_id:{'linked_file':cqs_obj.library.filepath,'object_name':cqs_obj.name,'object_count':1,'bounds_world_m':cqs_bound,'grade':8.5},
  duhme_id:{'linked_file':duhme_coll.library.filepath,'collection':duhme_coll.name,'object_count':len(duhme_coll.all_objects),'bounds_world_m':duhme_bound,'grade':8.5},
  burton_id:{'linked_file':marker.instance_collection.library.filepath,'marker':marker.name,'collection':marker.instance_collection.name,'object_count':len(marker.instance_collection.all_objects),'location_m':list(marker.location),'manifest_origin_m':expected,'grade':8.4}
 }
}
out=ROOT/'audit/master_sync_r33_handoffs.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('MASTER_SYNC_R33_PASS',json.dumps({'objects':report['scene_object_count'],'markers':report['placement_markers'],'libraries':report['library_count'],'missing':report['missing_library_count'],'duhme':len(duhme_coll.all_objects),'earhart':len(earhart_coll.all_objects),'burton':len(marker.instance_collection.all_objects),'cqs':cqs_bound}))

