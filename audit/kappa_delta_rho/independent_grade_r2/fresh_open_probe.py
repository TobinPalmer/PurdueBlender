import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector
root=Path.cwd()
asset=root/'modular/buildings/massing_house_1089876362_14ecd2c.blend'
out=root/'audit/kappa_delta_rho/independent_grade_r2'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
coll=bpy.data.collections.get('Asset_massing_house_1089876362_14ecd2c')
house=bpy.data.objects.get('House_1089876362')
assert scene.name=='Building_massing_house_1089876362_14ecd2c' and coll and house and house.name in coll.objects
geo=json.loads((root/'audit/kappa_delta_rho/sources/purdue_gis_fid801.geojson').read_text(encoding='utf-8'))
ring=geo['features'][0]['geometry']['coordinates'][0][:-1]
lat0=40.4274; lon0=-86.9137
xy=[]
for lon,lat in ring:
    x=(lon-lon0)*111412.84*math.cos(math.radians(lat0)); y=(lat-lat0)*111040.0
    xy.append((x,y))
base=[(float(v.co.x),float(v.co.y)) for v in house.data.vertices if abs(v.co.z)<1e-5]
dists=[]
for x,y in xy:
    dists.append(min(math.hypot(x-a,y-b) for a,b in base))
meshes=[]
for obj in coll.all_objects:
    if obj.type!='MESH': continue
    bm=None
    import bmesh
    bm=bmesh.new(); bm.from_mesh(obj.data)
    meshes.append({'object':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_edges':sum(e.is_wire for e in bm.edges),'materials':[m.name if m else None for m in obj.data.materials]})
    bm.free()
materials=[]
for m in bpy.data.materials:
    ntypes=[]
    if m.use_nodes and m.node_tree:
      ntypes=[n.type for n in m.node_tree.nodes]
    materials.append({'name':m.name,'use_nodes':m.use_nodes,'node_types':ntypes})
external=[{'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
res={'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'fresh_open_blender':bpy.app.version_string,'scene':scene.name,'collection':coll.name,'house':house.name,'house_vertices':len(house.data.vertices),'house_faces':len(house.data.polygons),'house_mats':[m.name if m else None for m in house.data.materials],'gis_fid':geo['features'][0]['id'],'gis_name':geo['features'][0]['properties']['BUILDING_N'],'gis_address':geo['features'][0]['properties']['ADDRESS'],'gis_ring_vertices':len(xy),'model_base_vertices':len(base),'footprint_nearest_vertex_max_m':max(dists),'footprint_nearest_vertex_rms_m':math.sqrt(sum(d*d for d in dists)/len(dists)),'meshes':meshes,'total_boundary_edges':sum(m['boundary_edges'] for m in meshes),'total_nonmanifold_edges':sum(m['nonmanifold_edges'] for m in meshes),'unpacked_external_images':external,'materials':materials,'object_names':sorted(o.name for o in coll.all_objects)}
(out/'fresh_open_probe.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
print('KDR_R2_PROBE='+json.dumps(res))

