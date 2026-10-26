import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ASSET=Path(bpy.data.filepath).resolve()
ROOT=ASSET.parents[2]
COLL_NAME='Asset_massing_purdue_center_for_regional_development_scho_a2375c9'
GIS=ROOT/'audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json'
OUT=Path(__file__).resolve().parent/'fresh_asset_probe.json'
EXPECTED='5a75fff4a316b5f101f613272779317a719b4b2478e1f22960ac362c55552693'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
scene=bpy.context.scene
coll=bpy.data.collections.get(COLL_NAME)
all_objs=list(coll.all_objects) if coll else []
meshes=[o for o in all_objs if o.type=='MESH']
deps=bpy.context.evaluated_depsgraph_get()
world_points=[]
for obj in meshes:
    ev=obj.evaluated_get(deps)
    world_points.extend(ev.matrix_world @ Vector(c) for c in ev.bound_box)
world_bounds=[[min(p[i] for p in world_points),max(p[i] for p in world_points)] for i in range(3)] if world_points else []
raw=json.loads(GIS.read_text(encoding='utf-8'))
feat=raw['features'][0]
attrs=feat['attributes']
ring=feat['geometry']['rings'][0]
lat0=40.4274; lon0=-86.9137; sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
poly=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring[:-1]]
source_segments=list(zip(poly,poly[1:]+poly[:1]))
wall=next((o for o in meshes if o.name.endswith('_Perimeter_Brickwork')),None)
wall_segments=[]
if wall:
    ev=wall.evaluated_get(deps); mesh=ev.to_mesh()
    co=[ev.matrix_world @ v.co for v in mesh.vertices]
    for e in mesh.edges:
        a,b=(co[e.vertices[0]],co[e.vertices[1]])
        if abs(a.z)<0.005 and abs(b.z)<0.005 and math.hypot(a.x-b.x,a.y-b.y)>1e-5:
            wall_segments.append(((a.x,a.y),(b.x,b.y)))
    ev.to_mesh_clear()
def dist_seg(p, seg):
    a,b=seg; dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
    if den==0: return math.dist(p,a)
    t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def sample(seg, step=.25):
    a,b=seg; n=max(1,math.ceil(math.dist(a,b)/step))
    return [(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)]
gis_samples=[p for s in source_segments for p in sample(s)]
wall_samples=[p for s in wall_segments for p in sample(s)]
gis_to_wall=[min(dist_seg(p,s) for s in wall_segments) for p in gis_samples] if wall_segments else []
wall_to_gis=[min(dist_seg(p,s) for s in source_segments) for p in wall_samples] if source_segments else []
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
missing_material=[o.name for o in meshes if not o.data.materials]
images=[{'name':i.name,'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images if i.name!='Render Result']
roof_objects=[o.name for o in meshes if any(w in o.name.lower() for w in ('cross_gable','roof','gable','chimney'))]
source_bounds=[[min(p[i] for p in poly),max(p[i] for p in poly)] for i in range(2)]
probe={'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_sha256':sha,'expected_sha256':EXPECTED,'sha_matches_expected':sha==EXPECTED,
 'blender_version':bpy.app.version_string,'scene':scene.name,'collection':COLL_NAME if coll else None,'object_count':len(all_objs),'mesh_count':len(meshes),
 'collection_library_paths':[c.library.filepath for c in bpy.data.collections if c==coll and c.library],
 'gis_feature_id':attrs.get('OBJECTID'),'gis_name':attrs.get('Name'),'gis_address':attrs.get('ADDRESS'),'gis_area_m2':attrs.get('Shape.STArea()'),
 'gis_bounds_m':source_bounds,'evaluated_bounds_m':world_bounds,'perimeter_wall_name':wall.name if wall else None,
 'wall_segment_count':len(wall_segments),'gis_sample_count':len(gis_samples),'wall_sample_count':len(wall_samples),
 'gis_to_wall_max_m':max(gis_to_wall) if gis_to_wall else None,'wall_to_gis_max_m':max(wall_to_gis) if wall_to_gis else None,
 'gis_to_wall_mean_m':sum(gis_to_wall)/len(gis_to_wall) if gis_to_wall else None,
 'material_names':materials,'meshes_without_material':missing_material,'images':images,'roof_related_objects':roof_objects}
OUT.write_text(json.dumps(probe,indent=2),encoding='utf-8')
print(json.dumps(probe,indent=2))
if sha!=EXPECTED: raise RuntimeError('Unexpected asset hash')
if not coll or not wall: raise RuntimeError('Expected building collection or perimeter wall is missing')
