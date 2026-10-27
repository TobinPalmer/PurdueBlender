import bpy, json, os, math
from datetime import datetime, timezone
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
audit=os.path.join(root,'audit','west_lafayette_junior_senior_high_school')
asset_id='massing_west_lafayette_junior_senior_high_school_fa45bd1'
coll_name='Asset_'+asset_id
scene_name='Building_'+asset_id
asset=bpy.data.collections.get(coll_name)
scene=bpy.data.scenes.get(scene_name)
raw=json.load(open(os.path.join(audit,'sources','osm_way_283537867_raw.json'),encoding='utf-8'))
way=next(x for x in raw['elements'] if x['type']=='way' and x['id']==283537867)
nodes={x['id']:(x['lat'],x['lon']) for x in raw['elements'] if x['type']=='node'}
osm=[((nodes[n][1]+86.9137)*84810.60416539927,(nodes[n][0]-40.4274)*111040) for n in way['nodes'][:-1]]
mesh_objs=[o for o in (asset.objects if asset else []) if o.type=='MESH']
primary=next((o for o in mesh_objs if o.name=='West Lafayette Junior-Senior High School'),None)
base=[(v.co.x,v.co.y) for v in primary.data.vertices if abs(v.co.z)<1e-6] if primary else []
# Compare unordered plan vertices; the primary shell must reproduce every unique OSM node.
dists=[]
for x,y in osm:
    dists.append(min(math.hypot(x-a,y-b) for a,b in base) if base else None)
coords=[(v.co.x,v.co.y,v.co.z) for o in mesh_objs for v in o.data.vertices]
bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)] if coords else None
result={
 'validated_at_utc':datetime.now(timezone.utc).isoformat(),
 'file':os.path.relpath(bpy.data.filepath,root).replace('\\\\','/'),
 'fresh_open':True,
 'scene_present':bool(scene),
 'asset_collection_present':bool(asset),
 'asset_collection':coll_name,
 'asset_mesh_count':len(mesh_objs),
 'asset_object_count':len(asset.objects) if asset else 0,
 'asset_nonmesh_objects':[o.name+':'+o.type for o in asset.objects if o.type!='MESH'] if asset else [],
 'primary_shell_present':bool(primary),
 'osm_way_id':283537867,
 'osm_closed_ring':way['nodes'][0]==way['nodes'][-1],
 'osm_unique_vertex_count':len(osm),
 'matched_shell_base_vertex_count':len(base),
 'max_osm_to_shell_vertex_error_m':max(dists) if dists else None,
 'campus_world_bounds_m':bounds,
 'scene_render_engine':scene.render.engine if scene else None,
 'preview_files':{n:os.path.exists(os.path.join(audit,'previews',n+'.png')) for n in ['aerial','east','south','northwest']},
}
result['checks_passed']=(result['scene_present'] and result['asset_collection_present'] and result['primary_shell_present'] and result['osm_closed_ring'] and result['osm_unique_vertex_count']==34 and result['matched_shell_base_vertex_count']==34 and result['max_osm_to_shell_vertex_error_m']<0.001 and not result['asset_nonmesh_objects'] and all(result['preview_files'].values()))
open(os.path.join(audit,'validation.json'),'w',encoding='utf8').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
