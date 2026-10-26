import bpy, json, math
from pathlib import Path

asset_id='massing_henni_s_hair_shop_57f732b'
root=Path(bpy.data.filepath).resolve().parents[2]
audit=root/'audit'/asset_id
obj=bpy.data.objects.get("Henni's Hair Shop")
coll=bpy.data.collections.get('Asset_'+asset_id)
scene=bpy.data.scenes.get('Building_'+asset_id)
assert obj and coll and scene
assert len(coll.objects)==1 and coll.objects[0]==obj
assert obj.type=='MESH' and len(obj.modifiers)==0
world=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
base_all=sorted({(round(v.x,3),round(v.y,3)) for v in world if abs(v.z)<1e-5})
osm=json.loads((audit/'sources'/'osm_way_116427257_raw.json').read_text())
nodes={n['id']:n for n in osm['nodes']}
coords=[]
for nid in osm['way']['nodes']:
    n=nodes[nid]
    coords.append(((n['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(n['lat']-40.4274)*111040.0))
if len(coords)>1 and math.dist(coords[0],coords[-1])<1e-8: coords.pop()
base=[min(base_all,key=lambda v:math.hypot(v[0]-x,v[1]-y)) for x,y in coords]
errors=[min(math.hypot(x-u,y-v) for u,v in base) for x,y in coords]
report={
  'reopened_file':bpy.data.filepath,
  'asset_id':asset_id,
  'scene':scene.name,
  'collection':coll.name,
  'collection_objects':[o.name for o in coll.objects],
  'object_count':len(coll.objects),
  'mesh_vertices':len(obj.data.vertices),
  'mesh_faces':len(obj.data.polygons),
  'overall_bounds_xyz_m':bounds,
  'structural_footprint_xy_bounds_m':[[min(x for x,y in base),max(x for x,y in base)],[min(y for x,y in base),max(y for x,y in base)]],
  'structural_ring_vertices_matched':len(base),
  'osm_way_id':osm['way']['id'],
  'osm_vertex_nearest_error_max_m':max(errors),
  'osm_vertex_nearest_error_mean_m':sum(errors)/len(errors),
  'modifiers':len(obj.modifiers),
  'external_image_paths':[i.filepath for i in bpy.data.images if i.source=='FILE'],
  'image_datablocks':[i.name for i in bpy.data.images],
  'linked_libraries':[lib.filepath for lib in bpy.data.libraries],
  'render_preview':str(audit/'renders'/'henni_hair_shop_facade.png'),
  'height_status':'8.38 m visual estimate from a two-level storefront photograph; not measured',
  'result':'pass' if len(base)==4 and max(errors)<0.005 and len(coll.objects)==1 and not obj.modifiers and not any(i.source=='FILE' for i in bpy.data.images) else 'fail'
}
(audit/'review'/'reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('HENNI_REOPEN_VALIDATION '+json.dumps(report))
