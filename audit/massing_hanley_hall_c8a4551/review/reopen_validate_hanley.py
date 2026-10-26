import bpy, json, math
from pathlib import Path

asset_id='massing_hanley_hall_c8a4551'
asset_collection='Asset_'+asset_id
scene_name='Building_'+asset_id
root=Path(bpy.data.filepath).resolve().parents[2]
audit=root/'audit'/asset_id
obj=bpy.data.objects.get('Hanley Hall')
coll=bpy.data.collections.get(asset_collection)
scene=bpy.data.scenes.get(scene_name)
assert obj and coll and scene, 'required object, collection, or scene missing after reopen'
assert list(coll.objects)==[obj], f'expected one export object; found {[x.name for x in coll.objects]}'
assert obj.type=='MESH' and len(obj.modifiers)==0
world=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
base=[(v.x,v.y) for v in world if abs(v.z)<1e-6]
osm=json.loads((audit/'sources'/'osm_way_283275000_raw.json').read_text())
way=osm['way']
nodes={e['id']:e for e in osm['nodes']}
proj=[]
for nid in way['nodes']:
    nd=nodes[nid]
    proj.append(((nd['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(nd['lat']-40.4274)*111040.0))
nearest=[min(math.hypot(x-u,y-v) for u,v in base) for x,y in proj]
gis=json.loads((audit/'sources'/'purdue_campus_gis_hanley.json').read_text())
feature=next(f for f in gis['features'] if f['attributes']['OBJECTID']==310)
gis_xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in feature['geometry']['rings'][0]]
gis_to_shell=[min(math.hypot(x-u,y-v) for u,v in base) for x,y in gis_xy]
shell_to_gis=[min(math.hypot(x-u,y-v) for u,v in gis_xy) for x,y in base]
report={
  'reopened_file':bpy.data.filepath,
  'asset_id':asset_id,
  'scene':scene.name,
  'collection':coll.name,
  'collection_objects':[o.name for o in coll.objects],
  'object_count':len(coll.objects),
  'mesh_vertices':len(obj.data.vertices),
  'mesh_faces':len(obj.data.polygons),
  'world_bounds_xyz_m':bounds,
  'structural_footprint_xy_bounds_m':[[min(x for x,y in base),max(x for x,y in base)],[min(y for x,y in base),max(y for x,y in base)]],
  'osm_way_id':283275000,
  'osm_vertex_nearest_error_max_m':max(nearest),
  'osm_vertex_nearest_error_mean_m':sum(nearest)/len(nearest),
  'official_gis_feature_id':310,
  'official_gis_to_shell_boundary_nearest_max_m':max(gis_to_shell),
  'shell_to_official_gis_boundary_nearest_max_m':max(shell_to_gis),
  'official_gis_footprint_bounds_xy_m':[[min(x for x,y in gis_xy),max(x for x,y in gis_xy)],[min(y for x,y in gis_xy),max(y for x,y in gis_xy)]],
  'modifiers':len(obj.modifiers),
  'external_image_paths':[i.filepath for i in bpy.data.images if i.source=='FILE'],
  'linked_libraries':[lib.filepath for lib in bpy.data.libraries],
  'render_preview':str(audit/'renders'/'hanley_hall_facade.png'),
  'result':'pass' if max(nearest)<0.15 and not obj.modifiers and len(coll.objects)==1 else 'fail'
}
(audit/'review'/'reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('HANLEY_REOPEN_VALIDATION '+json.dumps(report))
