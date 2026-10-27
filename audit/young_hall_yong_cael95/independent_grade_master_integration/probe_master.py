import bpy, json
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'modular'
manifest=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
asset_id='massing_young_hall_yong_cae1b95'
record=next(a for a in manifest['assets'] if a['id']==asset_id)
marker_name=f'Placement_{asset_id}'
marker=bpy.data.objects.get(marker_name)
collection=bpy.data.collections.get(record['collection'])
scene=bpy.context.scene
root_collection=scene.collection

def col_local(obj, cache=None):
    if cache is None: cache={}
    if obj in cache: return cache[obj]
    mat=obj.matrix_local.copy()
    if obj.parent is not None: mat=col_local(obj.parent,cache) @ mat
    cache[obj]=mat
    return mat

def bounds(points):
    return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None

objects=list(collection.all_objects) if collection else []
geometry=[o for o in objects if o.type in {'MESH','CURVE','FONT','SURFACE','META'}]
cache={}
local_points=[]
world_points=[]
for o in geometry:
    mat=col_local(o,cache)
    for c in o.bound_box:
        p=mat @ Vector(c)
        local_points.append(p)
        if marker is not None: world_points.append(marker.matrix_world @ p)
local_bounds=bounds(local_points)
world_bounds=bounds(world_points)
marker_instances=[o for o in bpy.data.objects if o.instance_type=='COLLECTION' and o.instance_collection==collection] if collection else []
master_root_direct=bool(collection and collection in list(root_collection.children))
source_path=(MOD/record['file']).resolve()
linked_path=Path(bpy.path.abspath(collection.library.filepath)).resolve() if collection and collection.library else None
# Bounds for the structural shell object, if present.
shell=next((o for o in geometry if o.name=='Young Hall (YONG)'),None)
shell_world_bounds=None
if shell is not None and marker is not None:
    shell_mat=marker.matrix_world @ col_local(shell,{})
    shell_world_bounds=bounds([shell_mat @ Vector(c) for c in shell.bound_box])
master_image_dependencies=[]
asset_image_dependencies=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        fp=Path(bpy.path.abspath(im.filepath))
        if fp.is_absolute() and fp.exists():
            master_image_dependencies.append(str(fp))
            im_library=Path(bpy.path.abspath(im.library.filepath)).resolve() if im.library else None
            if im_library==source_path:
                asset_image_dependencies.append(str(fp))
expected_xy=record.get('placement_origin_xy_m')
errors=[]
if marker is None: errors.append('missing placement marker')
if collection is None: errors.append('missing exported collection')
if marker and collection and marker.instance_collection!=collection: errors.append('marker references unexpected collection')
if marker and (marker.name!=marker_name): errors.append('marker name mismatch')
if marker and expected_xy and any(abs(float(marker.location[i])-float(expected_xy[i]))>0.001 for i in range(2)): errors.append('marker position disagrees with manifest')
if marker and any(abs(float(marker.rotation_euler[i]))>1e-6 for i in range(3)): errors.append('marker rotation is not identity')
if marker and any(abs(float(marker.scale[i])-1)>1e-6 for i in range(3)): errors.append('marker scale is not unit')
if collection and linked_path!=source_path: errors.append('linked source path mismatch')
if len(marker_instances)!=1: errors.append(f'expected one instance, found {len(marker_instances)}')
if master_root_direct: errors.append('asset collection is also a direct scene-root child')
if len(objects)!=record.get('object_count'): errors.append('manifest object count mismatch')
result={
 'status':'PASS' if not errors else 'FAIL',
 'date':'2026-10-26',
 'blender_version':bpy.app.version_string,
 'master_path':str(ROOT/'purdue_campus_master.blend'),
 'asset_id':asset_id,
 'asset_path':str(source_path),
 'manifest_kind':record.get('kind'),
 'local_coordinates':record.get('local_coordinates'),
 'manifest_object_count':record.get('object_count'),
 'collection_object_count':len(objects),
 'object_types':dict(Counter(o.type for o in objects)),
 'geometry_object_count':len(geometry),
 'empty_names':[o.name for o in objects if o.type=='EMPTY'],
 'marker':{
  'name':marker.name if marker else None,
  'location':list(marker.location) if marker else None,
  'rotation_euler':list(marker.rotation_euler) if marker else None,
  'scale':list(marker.scale) if marker else None,
  'instance_type':marker.instance_type if marker else None,
  'collection':marker.instance_collection.name if marker and marker.instance_collection else None,
  'instance_count_for_collection':len(marker_instances),
 },
 'collection_directly_linked_under_scene_root':master_root_direct,
 'linked_path':str(linked_path) if linked_path else None,
 'linked_path_matches_manifest':linked_path==source_path,
 'local_bounds_m':local_bounds,
 'world_bounds_m':world_bounds,
 'shell_world_bounds_m':shell_world_bounds,
 'reference_collection_world_bounds_m':[[241.42410278320312,280.38726806640625],[-564.8024291992188,-442.23077392578125],[-0.07500000298023224,31.119600296020508]],
 'asset_external_file_dependencies':asset_image_dependencies,
 'master_scene_external_images_not_attributed_to_yong':master_image_dependencies,
 'errors':errors,
}
out=ROOT/'audit'/'young_hall_yong_cael95'/'independent_grade_master_integration'/'master_probe.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
