import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parents[2]
ASSET=Path(bpy.data.filepath).resolve()
COLL='Asset_massing_purdue_center_for_regional_development_scho_a2375c9'
GIS=ROOT/'audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json'
OUT=Path(__file__).resolve().parent/'fresh_asset_probe.json'
raw=json.loads(GIS.read_text(encoding='utf-8'))
feature=raw['features'][0]
attrs=feature['attributes']
ring=feature['geometry']['rings'][0]
lat0=40.4274; lon0=-86.9137; sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
source=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring]
scene=bpy.context.scene
col=bpy.data.collections.get(COLL)
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
wall=next((o for o in meshes if o.name.endswith('_Perimeter_Brickwork')),None)
wall_segments=[]; wall_xy=[]
if wall:
    ev=wall.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    coords=[ev.matrix_world@v.co for v in mesh.vertices]
    wall_xy=[(p.x,p.y) for p in coords if abs(p.z)<0.005]
    for e in mesh.edges:
        a,b=(coords[e.vertices[0]],coords[e.vertices[1]])
        if abs(a.z)<0.005 and abs(b.z)<0.005 and math.hypot(a.x-b.x,a.y-b.y)>1e-5:
            wall_segments.append(((a.x,a.y),(b.x,b.y)))
    ev.to_mesh_clear()

def pd(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];d=dx*dx+dy*dy
    if d==0:return math.dist(p,a)
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
source_segments=list(zip(source,source[1:]+source[:1]))
def sample(seg,step=.25):
    a,b=seg; n=max(1,math.ceil(math.dist(a,b)/step))
    return [(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)]
source_samples=[p for s in source_segments for p in sample(s)]
wall_samples=[p for s in wall_segments for p in sample(s)]
source_to_wall=max((min(pd(p,*s) for s in wall_segments) for p in source_samples),default=None)
wall_to_source=max((min(pd(p,*s) for s in source_segments) for p in wall_samples),default=None)
mean_source_to_wall=sum(min(pd(p,*s) for s in wall_segments) for p in source_samples)/max(1,len(source_samples))
allpts=[ev.matrix_world@Vector(c) for o in meshes for c in o.bound_box for ev in [o.evaluated_get(bpy.context.evaluated_depsgraph_get())]]
bounds=[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)] if allpts else []
source_bounds=[[min(p[i] for p in source),max(p[i] for p in source)] for i in range(2)]
material_names=sorted({m.name for o in meshes for m in o.data.materials if m})
images=[]
for img in bpy.data.images:
    if img.name=='Render Result':continue
    images.append({'name':img.name,'packed':bool(img.packed_file),'filepath':img.filepath})
result={'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'blender_version':bpy.app.version_string,'scene':scene.name,'collection':COLL if col else None,'object_count':len(objs),'mesh_count':len(meshes),'wall_object':wall.name if wall else None,'gis_feature_id':attrs.get('OBJECTID'),'gis_name':attrs.get('Name'),'gis_address':attrs.get('ADDRESS'),'gis_area_m2':attrs.get('Shape.STArea()'),'gis_bounds_m':source_bounds,'evaluated_bounds_m':bounds,'wall_ground_bounds_m':[[min(p[i] for p in wall_xy),max(p[i] for p in wall_xy)] for i in range(2)] if wall_xy else [],'wall_ground_vertex_count':len(wall_xy),'wall_ground_edge_segment_count':len(wall_segments),'source_boundary_sample_count':len(source_samples),'wall_to_gis_max_sampled_distance_m':wall_to_source,'gis_to_wall_max_sampled_distance_m':source_to_wall,'gis_to_wall_mean_sampled_distance_m':mean_source_to_wall,'materials':material_names,'images':images}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if result['asset_sha256']!='05b7286ddab789bef1c7023a2d20bc2ada2daffc418991ec612bfe2ed340c4ef': raise RuntimeError('Unexpected asset SHA')
if not col or not wall or scene.name!='Building_massing_purdue_center_for_regional_development_scho_a2375c9': raise RuntimeError('Expected scene/collection/wall missing')
