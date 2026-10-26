import bpy, json, math, os, hashlib
from mathutils import Vector
ASSET_ID='massing_wood_street_garage_pgw_2fa056e'
asset=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','modular','buildings',ASSET_ID+'.blend'))
if os.path.abspath(bpy.data.filepath)!=asset: raise RuntimeError(f'Unexpected opened file: {bpy.data.filepath}')
scene=bpy.data.scenes.get('Building_'+ASSET_ID)
col=bpy.data.collections.get('Asset_'+ASSET_ID)
assert scene is not None, 'Expected asset scene missing'
assert col is not None, 'Expected exported asset collection missing'
assert col.name in [c.name for c in scene.collection.children], 'Asset collection not linked directly in scene'
assert scene.get('building_id')==ASSET_ID
assert scene.get('gis_feature_id')==254
mesh_objects=[o for o in col.objects if o.type=='MESH']
assert len(mesh_objects)>=20, f'Expected detailed geometry, got {len(mesh_objects)} meshes'
assert any('stair' in o.name.lower() for o in col.objects)
assert any('ramp' in o.name.lower() for o in col.objects)
assert any('WOOD STREET GARAGE' in getattr(o.data,'body','') for o in col.objects)
# Ensure local geometry remains close to transformed GIS footprint bounds.
pts=[]
j=json.load(open(os.path.join(os.path.dirname(__file__),'raw_arcgis_fid254.json'),encoding='utf-8-sig'))
ring=j['features'][0]['geometry']['rings'][0]; R=6378137.0
for e,n in ring:
    lon=math.degrees(e/R); lat=math.degrees(math.atan(math.sinh(n/R)))
    x=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274)); y=(lat-40.4274)*111040.0; pts.append((x,y))
anchor=[(min(p[0] for p in pts)+max(p[0] for p in pts))/2,(min(p[1] for p in pts)+max(p[1] for p in pts))/2]
expected={(round(x-anchor[0],4),round(y-anchor[1],4)) for x,y in pts[:-1]}
deck=bpy.data.objects.get('PGW deck 01')
assert deck is not None
actual={(round(v.co.x,4),round(v.co.y,4)) for v in deck.data.vertices[:len(ring)-1]}
if expected!=actual: print('GIS_RING_DIFF',sorted(expected-actual),sorted(actual-expected)); raise AssertionError(f'GIS ring mismatch: missing={len(expected-actual)} extra={len(actual-expected)}')
# Inspect mesh local bounds and dependencies.
world_vertices=[]
for o in mesh_objects:
    for corner in o.bound_box:
        world_vertices.append(o.matrix_world @ Vector(corner))
bounds=[[min(v[i] for v in world_vertices),max(v[i] for v in world_vertices)] for i in range(3)]
assert abs(bounds[0][0]-min(x-anchor[0] for x,y in pts))<0.01
assert abs(bounds[1][0]-min(y-anchor[1] for x,y in pts))<0.01
assert 23.6<=bounds[2][1]<=24.3, f'height outside expected GIS roof range: {bounds[2][1]}'
assert abs(scene['world_anchor_m'][0]-anchor[0])<1e-5 and abs(scene['world_anchor_m'][1]-anchor[1])<1e-5
images=[{'name':i.name,'filepath':i.filepath,'source':i.source} for i in bpy.data.images if i.source=='FILE' and i.filepath]
assert not images, f'Unexpected external image dependencies: {images}'
missing=[]
for o in col.objects:
    if o.type in {'MESH','CURVE','FONT'} and getattr(o.data,'materials',None) is not None and not len(o.data.materials): missing.append(o.name)
assert not missing, f'Objects missing materials: {missing}'
# World-bound footprint set and reproducible asset hash.
sha=hashlib.sha256(open(asset,'rb').read()).hexdigest()
result={'status':'PASS','reopened_asset':asset,'asset_sha256':sha,'scene':scene.name,'collection':col.name,'object_count':len(col.objects),'mesh_count':len(mesh_objects),'bounds_local_m':bounds,'gis_anchor_world_m':anchor,'footprint_ring_vertices':len(ring)-1,'footprint_match':'exact vertex set after the project local transform','external_image_dependencies':len(images),'materialless_geometry':missing,'master_integration':'requires coordinator to change manifest kind to detailed and add placement marker at GIS bbox midpoint'}
out=os.path.join(os.path.dirname(__file__),'fresh_open_validation.json')
json.dump(result,open(out,'w',encoding='utf-8'),indent=2)
print(json.dumps(result,indent=2))



