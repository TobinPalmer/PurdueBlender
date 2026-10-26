import bpy, json, hashlib, math
from pathlib import Path
ROOT=Path(bpy.data.filepath).resolve().parents[2]
EVID=ROOT/'audit/purdue_football_performance_complex'
ASSET_ID='massing_purdue_football_performance_complex_f106c29'
COLL='Asset_'+ASSET_ID
SCENE='Building_'+ASSET_ID
collection=bpy.data.collections.get(COLL)
scene=bpy.data.scenes.get(SCENE)
errors=[]
if collection is None: errors.append('expected collection absent')
if scene is None: errors.append('expected scene absent')
objs=list(collection.all_objects) if collection else []
geom=[o for o in objs if o.type in {'MESH','CURVE','FONT','SURFACE','META'}]
meshes=[o for o in geom if o.type=='MESH']
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        path=bpy.path.abspath(im.filepath)
        external.append(path)
if external: errors.append('unpacked external images: '+str(external))
linked=[o.name for o in objs if o.library is not None]
if linked: errors.append('linked external objects inside asset: '+str(linked[:10]))
if any(o.type=='MESH' and not len(o.data.materials) for o in meshes): errors.append('mesh without material slots')
plinth=next((o for o in meshes if o.name=='KFPC | structural ground plinth'),None)
if plinth is None: errors.append('structural plinth absent')
source=json.loads((EVID/'sources/purdue_gis_fpc_fid1202_2026-10-26.geojson').read_text(encoding='utf-8'))
feature=next(f for f in source['features'] if int(f.get('id', f['properties'].get('OBJECTID',-1)))==1202)
ring=feature['geometry']['coordinates'][0]
ev=json.loads((EVID/'build_evidence.json').read_text(encoding='utf-8'))
origin=ev['placement_origin_xy_m']
lat0,lon0=40.4274,-86.9137
sxy=[]
for lon,lat,*_ in ring:
    x=(lon-lon0)*111412.84*math.cos(math.radians(lat0)); y=(lat-lat0)*111040.0
    sxy.append((x-origin[0],y-origin[1]))
if len(sxy)>1 and math.dist(sxy[0],sxy[-1])<1e-7: sxy.pop()
modelxy=[]
if plinth:
    for v in plinth.data.vertices:
        modelxy.append((float(v.co.x),float(v.co.y)))
# source and plinth have the GIS exterior vertices on both top/bottom layers.
nearest=[]
for p in sxy:
    nearest.append(min(math.dist(p,q) for q in modelxy) if modelxy else float('inf'))
footprint_err=max(nearest) if nearest else None
if footprint_err is None or footprint_err>0.01: errors.append(f'GIS/plinth boundary mismatch; max source vertex distance={footprint_err}')
# Local geometry bounds from every exported object.
points=[o.matrix_world@__import__('mathutils').Vector(c) for o in geom for c in o.bound_box]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else []
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
result={'asset_path':str(Path(bpy.data.filepath).resolve()),'asset_sha256':sha,'scene':SCENE,'scene_found':scene is not None,'collection':COLL,'collection_found':collection is not None,'object_count':len(objs),'geometry_object_count':len(geom),'mesh_count':len(meshes),'material_count':len(bpy.data.materials),'unpacked_external_images':external,'linked_objects':linked,'local_bounds_m':bounds,'source_feature_id':feature.get('id',feature['properties'].get('OBJECTID')),'source_vertex_count':len(sxy),'plinth_vertex_count':len(modelxy),'max_source_to_plinth_vertex_distance_m':footprint_err,'status':'PASS' if not errors else 'FAIL','errors':errors}
(EVID/'independent_grade/fresh_asset_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if errors: raise RuntimeError('Independent fresh-open check failed')
