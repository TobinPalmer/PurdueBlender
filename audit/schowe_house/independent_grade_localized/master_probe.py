import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
MASTER=Path(bpy.data.filepath).resolve(); ROOT=MASTER.parent; MOD=ROOT/'modular'
AID='massing_purdue_center_for_regional_development_scho_a2375c9'
OUT=Path(__file__).resolve().parent/'master_probe.json'
m=json.loads((MOD/'manifest.json').read_text(encoding='utf-8')); rec=next(a for a in m['assets'] if a['id']==AID)
marker_name='Placement_'+AID; marker=bpy.data.objects.get(marker_name); col=bpy.data.collections.get(rec['collection'])
expected_file=(MOD/rec['file']).resolve(); linked=Path(bpy.path.abspath(col.library.filepath)).resolve() if col and col.library else None
errors=[]
if marker is None: errors.append('missing placement marker')
if col is None: errors.append('missing collection')
if marker and (marker.instance_type!='COLLECTION' or marker.instance_collection!=col): errors.append('marker does not instance expected collection')
if linked!=expected_file: errors.append(f'linked path mismatch: {linked} != {expected_file}')
if marker:
    exp=rec['placement_origin_xy_m']
    if any(abs(marker.location[i]-exp[i])>.001 for i in range(2)): errors.append('marker location mismatch with manifest')
    if any(abs(marker.scale[i]-1)>.0001 for i in range(3)): errors.append('marker scale not unit')
    if any(abs(marker.rotation_euler[i])>.0001 for i in range(3)): errors.append('marker rotation not zero')
root=bpy.context.scene.collection
if col and root.children.get(col.name) is not None: errors.append('source collection remains directly linked; duplicate integration risk')
markers=[o.name for o in bpy.data.objects if o.name==marker_name]
if len(markers)!=1: errors.append(f'expected exactly one marker, found {len(markers)}')
def local_matrix(o,cache):
    if o in cache:return cache[o]
    mat=o.matrix_local.copy()
    if o.parent is not None:mat=local_matrix(o.parent,cache)@mat
    cache[o]=mat
    return mat
points=[]; objs=list(col.all_objects) if col else []; cache={}
if marker and col:
    for o in objs:
        if o.type not in {'MESH','CURVE','FONT','SURFACE','META'}:continue
        for c in o.bound_box:points.append(marker.matrix_world@(local_matrix(o,cache)@Vector(c)))
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else []
exp_bounds=rec.get('bounds_world_m',[]); maxerr=max(abs(bounds[i][j]-exp_bounds[i][j]) for i in range(3) for j in range(2)) if bounds and exp_bounds else None
if maxerr is None or maxerr>.001: errors.append(f'world bounds mismatch: max={maxerr}')
asset_sha=hashlib.sha256(expected_file.read_bytes()).hexdigest()
result={'master_path':str(MASTER),'master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'asset_sha256':asset_sha,
 'expected_asset_sha256':'43fbc9e65e24e93710b38d868ce21e0162d5493b0a9fb0d2d64353ce5ea1837d','scene_object_count':len(bpy.context.scene.objects),
 'placement_marker_count':sum(o.name.startswith('Placement_') for o in bpy.context.scene.objects),'status':'PASS' if not errors else 'FAIL','errors':errors,
 'building_id':AID,'marker':marker_name,'marker_location':list(marker.location) if marker else None,'manifest_placement_xy':rec.get('placement_origin_xy_m'),
 'marker_scale':list(marker.scale) if marker else None,'marker_rotation_euler':list(marker.rotation_euler) if marker else None,
 'collection':rec['collection'],'collection_object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),
 'linked_library_path':str(linked) if linked else None,'expected_library_path':str(expected_file),'world_bounds_m':bounds,'manifest_bounds_m':exp_bounds,'bound_error_max_m':maxerr}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if result['status']!='PASS':raise RuntimeError('master placement verification failed')
if asset_sha!=result['expected_asset_sha256']:raise RuntimeError('asset SHA mismatch')
