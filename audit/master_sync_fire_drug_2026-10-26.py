import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parent
MOD=ROOT/'modular'
OUT=ROOT/'audit/master_sync_fire_drug_schowe_kfpc_2026-10-26.json'
manifest=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
checks=[]
scene=bpy.context.scene
root=scene.collection

def coll_local(obj, cache):
    if obj in cache: return cache[obj]
    m=obj.matrix_local.copy()
    if obj.parent is not None: m=coll_local(obj.parent,cache) @ m
    cache[obj]=m
    return m

for asset_id in ('massing_purdue_fire_department_520430b','massing_purdue_drug_discovery_facility_fc72a4a','massing_purdue_center_for_regional_development_scho_a2375c9','massing_purdue_football_performance_complex_f106c29'):
    rec=next(a for a in manifest['assets'] if a['id']==asset_id)
    marker=bpy.data.objects.get('Placement_'+asset_id)
    col=bpy.data.collections.get(rec['collection'])
    expected=(MOD/rec['file']).resolve()
    linked=Path(bpy.path.abspath(col.library.filepath)).resolve() if col and col.library else None
    errs=[]
    if marker is None: errs.append('missing placement marker')
    if col is None: errs.append('missing linked collection')
    if col and linked!=expected: errs.append(f'library path mismatch: {linked} != {expected}')
    if marker and (marker.instance_type!='COLLECTION' or marker.instance_collection!=col): errs.append('wrong collection instance')
    if marker and any(abs(marker.location[i]-rec['placement_origin_xy_m'][i])>.001 for i in range(2)): errs.append('placement mismatch')
    if col and root.children.get(col.name) is not None: errs.append('old direct massing link remains in root scene')
    objs=list(col.all_objects) if col else []
    pts=[]
    if marker and col:
        cache={}
        for obj in objs:
            if obj.type not in {'MESH','CURVE','FONT','SURFACE','META'}: continue
            for corner in obj.bound_box:
                pts.append(marker.matrix_world @ (coll_local(obj,cache) @ Vector(corner)))
    world_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else []
    expected_bounds=rec.get('bounds_world_m',[])
    if world_bounds and expected_bounds:
        err=max(abs(world_bounds[i][j]-expected_bounds[i][j]) for i in range(3) for j in range(2))
        if err>.005: errs.append(f'world bounds differ from manifest by {err:.4f}m')
    asset_path=MOD/rec['file']
    sha=hashlib.sha256(asset_path.read_bytes()).hexdigest()
    checks.append({'id':asset_id,'status':'PASS' if not errs else 'FAIL','errors':errs,
      'marker_location':list(marker.location) if marker else None,'library':str(linked) if linked else None,
      'mesh_count':sum(o.type=='MESH' for o in objs),'object_count':len(objs),'world_bounds_m':world_bounds,
      'manifest_bounds_m':expected_bounds,'bound_error_max_m':err if pts and expected_bounds else None,'asset_sha256':sha})
result={'master_path':str(Path(bpy.data.filepath).resolve()),'master_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'scene_object_count':len(scene.objects),'placement_marker_count':sum(o.name.startswith('Placement_') for o in scene.objects),
        'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if result['status']!='PASS': raise RuntimeError('Master integration audit failed')
