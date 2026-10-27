import bpy, json, hashlib, math, os
from pathlib import Path
asset = Path(r'modular/buildings/massing_house_1089876362_14ecd2c.blend').resolve()
out = Path(r'audit/kappa_delta_rho/independent_grade/fresh_open_probe.json').resolve()
sha_before = hashlib.sha256(asset.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
coll=bpy.data.collections.get('Asset_massing_house_1089876362_14ecd2c')
house=bpy.data.objects.get('House_1089876362')
if not (scene and coll and house): raise RuntimeError('Expected scene, asset collection, stable mesh missing')
# Independently compare 20 lower-ring vertices to source GIS FID 801 using builder's documented project-local conversion.
g=json.loads(Path(r'audit/kappa_delta_rho/sources/purdue_gis_fid801.geojson').read_text(encoding='utf-8-sig'))
feat=next(f for f in g['features'] if f['properties'].get('FID')==801)
ring=feat['geometry']['coordinates'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
expected=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring]
world=[house.matrix_world @ v.co for v in house.data.vertices]
low=[(v.x,v.y,v.z) for v in world if abs(v.z)<1e-5]
# greedy nearest-neighbor pairing preserves a useful one-to-one delta without assuming winding/start vertex.
remaining=list(low); pair=[]
for p in expected:
    q=min(remaining,key=lambda v:math.hypot(p[0]-v[0],p[1]-v[1]))
    remaining.remove(q); pair.append(math.hypot(p[0]-q[0],p[1]-q[1]))
mesh_stats=[]
for o in sorted([x for x in coll.objects if x.type=='MESH'],key=lambda x:x.name):
    me=o.data
    bm=None
    try:
        import bmesh
        bm=bmesh.new(); bm.from_mesh(me)
        boundary=sum(1 for e in bm.edges if e.is_boundary)
        nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
    except Exception: boundary=nonmanifold=None
    mesh_stats.append({'name':o.name,'vertices':len(me.vertices),'faces':len(me.polygons),'materials':[m.name if m else None for m in me.materials],'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'world_bounds':[[round(min((o.matrix_world@v.co)[i] for v in me.vertices),4) for i in range(3)],[round(max((o.matrix_world@v.co)[i] for v in me.vertices),4) for i in range(3)]] if me.vertices else None})
image_info=[{'name':im.name,'source':im.source,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images]
materials=[]
for m in bpy.data.materials:
    mats={'name':m.name,'nodes':[]}
    if m.use_nodes and m.node_tree:
        mats['nodes']=[{'type':n.bl_idname,'name':n.name} for n in m.node_tree.nodes]
    materials.append(mats)
data={'fresh_open':True,'blender_version':bpy.app.version_string,'source_file':str(asset),'sha256_before_open':sha_before,'sha256_after_open':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':scene.name,'scene_object_count':len(bpy.data.objects),'asset_collection':coll.name,'collection_object_count':len(coll.objects),'stable_object':house.name,'stable_type':house.type,'stable_vertices':len(house.data.vertices),'stable_faces':len(house.data.polygons),'gis_source':{'feature_id':feat['properties'].get('FID'),'name':feat['properties'].get('BUILDING_N'),'address':feat['properties'].get('ADDRESS'),'coordinate_count':len(expected),'one_to_one_xy_delta_m':{'max':max(pair),'mean':sum(pair)/len(pair),'rms':math.sqrt(sum(x*x for x in pair)/len(pair))},'expected_bounds':[[min(p[0] for p in expected),min(p[1] for p in expected)],[max(p[0] for p in expected),max(p[1] for p in expected)]],'actual_lower_ring_count':len(low)},'mesh_objects':mesh_stats,'materials':materials,'images':image_info,'camera':scene.camera.name if scene.camera else None,'external_unpacked_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]}
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
