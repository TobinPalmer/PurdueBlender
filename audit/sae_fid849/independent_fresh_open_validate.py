import bpy, hashlib, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / 'modular' / 'buildings' / 'massing_sigma_alpha_epsilon_fid849.blend'
out = root / 'audit' / 'sae_fid849' / 'independent_fresh_open.json'
collection_name='Asset_massing_sigma_alpha_epsilon_fid849'
collection=bpy.data.collections.get(collection_name)
assert collection is not None
objects=list(collection.objects)
meshes=[o for o in objects if o.type=='MESH']
verts=[]
for obj in meshes:
    for v in obj.data.vertices:
        verts.append(obj.matrix_world @ v.co)
mins=[min(v[i] for v in verts) for i in range(3)]
maxs=[max(v[i] for v in verts) for i in range(3)]
materials_missing=[o.name for o in meshes if len(o.data.materials)==0]
external_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.packed_file is None]
modifiers=[o.name for o in meshes if len(o.modifiers)]
linked=[o.name for o in objects if o.library is not None]
# Independently compare projected source ring against extant facade-band corner vertices.
source=json.loads((root/'audit'/'sae_fid849'/'sources'/'purdue_fid849_raw_feature.json').read_text(encoding='utf-8'))
ring=source['feature']['geometry']['rings'][0]
lat0=40.4274; lon0=-86.9137
expected=[]
for lon,lat in ring:
    expected.append(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0))
if expected[0]==expected[-1]: expected.pop()
# Collect all facade horizontal band endpoints at z=0 from vertex positions.
base_points=[]
for o in meshes:
    if 'Facade_' in o.name:
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            if abs(p.z)<1e-5: base_points.append((p.x,p.y))
# Match expected ring coordinates to model floor outline points; each expected point occurs on multiple faces.
nearest=[]
for x,y in expected:
    nearest.append(min(math.hypot(x-a,y-b) for a,b in base_points))
result={
 'status':'PASS','fresh_open':True,'asset':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),
 'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'expected_collection':collection_name,
 'collection_object_count':len(objects),'mesh_count':len(meshes),'nonmesh_count':len(objects)-len(meshes),
 'vertex_count':sum(len(o.data.vertices) for o in meshes),'polygon_count':sum(len(o.data.polygons) for o in meshes),
 'world_bounds_m':{'min':mins,'max':maxs},'materialless_meshes':materials_missing,
 'unpacked_external_images':external_images,'objects_with_modifiers':modifiers,'linked_objects':linked,
 'gis_outline':{'source_ring_vertices':len(expected),'max_nearest_facade_base_error_m':max(nearest),'mean_nearest_facade_base_error_m':sum(nearest)/len(nearest)},
 'checks':{'collection_present':True,'all_objects_are_meshes':len(objects)==len(meshes),'all_meshes_have_materials':not materials_missing,'no_unpacked_external_images':not external_images,'no_linked_objects':not linked,'no_modifiers':not modifiers,'gis_ring_represented_at_base':max(nearest)<0.002}
}
assert all(result['checks'].values()), result
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
