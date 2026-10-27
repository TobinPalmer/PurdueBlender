import bpy, bmesh, json, hashlib, math, os
from pathlib import Path
from math import cos, radians, hypot
root = Path(__file__).resolve().parents[3]
asset_path = Path(bpy.data.filepath).resolve()
asset_id = 'massing_village_bottle_shoppe_6a17e23'
scene = bpy.data.scenes.get('Building_' + asset_id)
collection = bpy.data.collections.get('Asset_' + asset_id)
obj = bpy.data.objects.get('Village Bottle Shoppe')
issues=[]
if not scene: issues.append('missing stable scene')
if not collection: issues.append('missing stable collection')
if not obj or obj.type!='MESH': issues.append('missing expected mesh object')
if collection and [o.name for o in collection.objects] != ['Village Bottle Shoppe']: issues.append('unexpected collection members')
if scene and [o.name for o in scene.objects] != ['Village Bottle Shoppe']: issues.append('unexpected scene objects')
if collection and obj and collection not in obj.users_collection: issues.append('object not linked to stable collection')
if asset_path != (root / 'modular/buildings' / f'{asset_id}.blend').resolve(): issues.append('unexpected file path')
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE']
if bpy.data.libraries: issues.append('external library link present')
if external_images: issues.append('external file image present')
mesh = obj.data if obj else None
bm=bmesh.new()
if mesh: bm.from_mesh(mesh)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
boundary=sum(len(e.link_faces)==1 for e in bm.edges)
wire=sum(not e.link_faces for e in bm.edges)
verts_world=[obj.matrix_world @ v.co for v in mesh.vertices] if obj and mesh else []
bbox=[[min(v[a] for v in verts_world), max(v[a] for v in verts_world)] for a in range(3)] if verts_world else None
shape_path=root/'audit/village_bottle_shoppe/sources/indiana_building_footprints_nearby.geojson'
shape=json.loads(shape_path.read_text(encoding='utf-8'))['features']
feature=next((f for f in shape if int(f.get('id', f.get('properties',{}).get('objectid',-1)))==409442 or int(f.get('properties',{}).get('OBJECTID',-1))==409442),None)
# Find the intended footprint by properties if ids are encoded differently.
if feature is None:
    feature=next(f for f in shape if int(f['properties'].get('objectid',f['properties'].get('OBJECTID',-1)))==409442)
ring=feature['geometry']['coordinates'][0]
def project(lon,lat):
    return ((lon+86.9137)*111412.84*cos(radians(40.4274)), (lat-40.4274)*111040.0)
projected=[project(p[0],p[1]) for p in ring[:-1]]
nearest=[]
for x,y in projected:
    nearest.append(min(hypot(v.x-x,v.y-y) for v in verts_world))
# Mesh/material portability details
materials=[]
for m in (mesh.materials if mesh else []):
    nodes=[]
    if m and m.use_nodes and m.node_tree:
        nodes=[n.type for n in m.node_tree.nodes]
    materials.append({'name':m.name if m else None,'uses_nodes':bool(m and m.use_nodes),'node_types':nodes})
report={
 'asset':str(asset_path),'sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,'scene':scene.name if scene else None,
 'collection':collection.name if collection else None,'scene_objects':[o.name for o in scene.objects] if scene else [],
 'collection_objects':[o.name for o in collection.objects] if collection else [],
 'object':obj.name if obj else None,'vertices':len(mesh.vertices) if mesh else None,
 'faces':len(mesh.polygons) if mesh else None,'edges':len(mesh.edges) if mesh else None,
 'world_bounds_xyz':bbox,'nonmanifold_edges':nonmanifold,'boundary_edges':boundary,'wire_edges':wire,
 'materials':materials,'external_libraries':len(bpy.data.libraries),'external_image_paths':external_images,
 'gis_feature_id':feature.get('id',feature.get('properties',{}).get('objectid')),
 'gis_ring_projected_xy':projected,'nearest_mesh_vertex_error_m':nearest,
 'nearest_vertex_error_max_m':max(nearest) if nearest else None,
 'asset_footprint_area_property_m2':obj.get('footprint_area_m2') if obj else None,
 'source_shape_area_property_raw':obj.get('source_shape_area_raw') if obj else None,
 'issues':issues}
out=root/'audit/village_bottle_shoppe/independent_grade_r3/fresh_open_probe.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('INDEPENDENT_FRESH_OPEN',json.dumps(report))
bm.free()
