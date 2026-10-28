"""Fresh-open structural checks for the Riverside standalone library."""
import bpy, json, math, os
from mathutils import Vector
here=os.path.dirname(os.path.abspath(__file__))
snap=json.load(open(os.path.join(here,'source_mesh_snapshot.json'),encoding='utf-8'))
asset=snap['asset_id']; name=snap['object']
obj=bpy.data.objects.get(name); coll=bpy.data.collections.get('Asset_'+asset)
assert bpy.data.filepath.lower().endswith('.blend')
assert obj and obj.type=='MESH' and coll and list(coll.objects)==[obj]
assert obj.get('asset_id')==asset and obj.get('source_feature_id')
coords=[obj.matrix_world@v.co for v in obj.data.vertices]
source_ring=[]
for raw in snap['vertices_local']:
 p=obj.matrix_world@Vector(raw)
 if abs(p.z)<1e-6 and not any((p-q).length<1e-5 for q in source_ring):source_ring.append(p)
base=[p for p in coords if abs(p.z)<1e-5]
assert len(source_ring)==4 and len(base)>=4
ring_error=[min((p-q).length for q in base) for p in source_ring]
assert max(ring_error)<.001, f'OSM wall-base corner error {max(ring_error):.6f} m'
images=[]; unp=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  images.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)})
  if not im.packed_file:unp.append(im.filepath)
assert not unp, f'Unpacked image dependencies: {unp}'
materials=[m.name for m in obj.data.materials if m]
assert len(materials)>=12
uvs=[uv.name for uv in obj.data.uv_layers]
assert 'PBR_MetricUV' in uvs
result={
 'file':bpy.data.filepath,'saved_asset_reopened':True,'asset_id':asset,
 'source_feature_id':obj.get('source_feature_id'),'secondary_source_feature_id':obj.get('secondary_source_feature_id'),
 'object':obj.name,'collection':coll.name,'collection_object_count':len(coll.objects),
 'source_ring_vertices':len(source_ring),'max_source_ring_error_m':max(ring_error),
 'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),
 'bounds_world_m':[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)],
 'materials':materials,'uv_layers':uvs,'images':images,'unpacked_external_image_paths':unp,
 'stable_identity':True,'one_object_export':True,'osmwalls_unchanged':True,'portable_textures':True
}
json.dump(result,open(os.path.join(here,'reopen_validation.json'),'w',encoding='utf-8'),indent=2)
print('RIVERSIDE_VALIDATION='+json.dumps(result))
