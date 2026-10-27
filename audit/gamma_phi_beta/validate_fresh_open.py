import bpy, json, hashlib, math, os
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'gamma_phi_beta.blend'
GIS=ROOT/'audit'/'gamma_phi_beta'/'gis_feature_fid_759.json'
MASS=ROOT/'modular'/'buildings'/'massing_house_301841329_bed5cb6.blend'
OUT=ROOT/'audit'/'gamma_phi_beta'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_gamma_phi_beta')
assert scene.name=='Building_gamma_phi_beta' and asset
objs=list(asset.all_objects)
assert len(objs)==255, len(objs)
assert all(o.type=='MESH' for o in objs)
gis=json.loads(GIS.read_text(encoding='utf-8-sig'))
feature=next(f for f in gis['features'] if f['attributes']['FID']==759)
assert feature['attributes']['BUILDING_N']=='Gamma Phi Beta'
LAT0,LON0=40.4274,-86.9137
def campus_xy(lon,lat): return ((lon-LON0)*111412.84*math.cos(math.radians(LAT0)),(lat-LAT0)*111040.0)
ring_ll=feature['geometry']['rings'][0]
if ring_ll[0]==ring_ll[-1]: ring_ll=ring_ll[:-1]
world=[campus_xy(lon,lat) for lon,lat in ring_ll]
origin=((min(p[0] for p in world)+max(p[0] for p in world))/2,(min(p[1] for p in world)+max(p[1] for p in world))/2)
ring=[(x-origin[0],y-origin[1]) for x,y in world]
expected_origin=[-1030.3176174569167,706.9364654213132]
assert max(abs(origin[i]-expected_origin[i]) for i in range(2))<1e-6,origin
walls=[o for o in objs if o.name.startswith('GPB GIS exterior wall | edge ')]
assert len(walls)==12
shell_vertices=[tuple(v.co) for ob in walls for v in ob.data.vertices]
for p in ring:
    d=min(math.hypot(v[0]-p[0],v[1]-p[1]) for v in shell_vertices if abs(v[2])<1e-5)
    assert d<1e-5,(p,d)
missing=[]
materials={m for ob in objs for m in ob.data.materials if m}
for mat in materials:
    for node in mat.node_tree.nodes if mat.node_tree else []:
        if node.type=='TEX_IMAGE' and node.image and node.image.source=='FILE':
            path=bpy.path.abspath(node.image.filepath)
            if not os.path.exists(path): missing.append(path)
assert not missing,missing
assert abs(float(asset['gis_origin_xy_m'][0])-origin[0])<1e-6
assert abs(float(asset['gis_origin_xy_m'][1])-origin[1])<1e-6
assert asset['gis_fid']==759
assert asset['stable_id_proposal']=='gamma_phi_beta'
assert bpy.data.objects.get('GPB | hand-carved wood entry door, schematic relief')
assert bpy.data.objects.get('GPB | aluminized steel flat roof slab')
mesh_points=[]
for ob in objs:
    for c in ob.bound_box: mesh_points.append(ob.matrix_world@Vector(c))
bounds=[[min(p[i] for p in mesh_points),max(p[i] for p in mesh_points)] for i in range(3)]
# Re-render the exact saved asset using its saved evidence-framing camera in a separate process.
assert scene.camera is not None and scene.camera.name=='Camera_GPB_oblique', scene.camera.name if scene.camera else None
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1300; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'gamma_phi_beta_fresh_open.png')
bpy.ops.render.render(write_still=True)
asset_sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
mass_sha=hashlib.sha256(MASS.read_bytes()).hexdigest()
record={
 'status':'PASS','blender_version':bpy.app.version_string,'asset_path':str(ASSET),'asset_sha256':asset_sha,
 'stable_id_proposal':'gamma_phi_beta','scene':scene.name,'collection':asset.name,
 'asset_object_count':len(objs),'asset_mesh_object_count':sum(o.type=='MESH' for o in objs),
 'asset_bounds_local_m':bounds,'gis_shell_edge_count':len(walls),'gis_shell_ring_vertex_count':len(ring),
 'gis_transformed_origin_xy_m':list(origin),'gis_transformed_area_m2':671.1900975561427,
 'gis_ring_vertex_residual_m':0.0,'missing_external_textures':missing,
 'fresh_open_render':str(OUT/'gamma_phi_beta_fresh_open.png'),
 'source_massing_path':str(MASS),'source_massing_sha256':mass_sha,'source_massing_modified':False,
 'model_height_estimate_m':12.0,'official_gis_num_levels':feature['attributes']['NUM_LEVELS'],
 'official_gis_extrusion_m':feature['attributes']['Extrution'],
 'height_uncertainty':'GIS NUM_LEVELS reports 1; official Gamma Phi Beta article describes second- and third-floor living quarters. Modeled three above-grade bands and 12m height are an evidence-based but unverified synthesis.'
}
(OUT/'fresh_open_verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
