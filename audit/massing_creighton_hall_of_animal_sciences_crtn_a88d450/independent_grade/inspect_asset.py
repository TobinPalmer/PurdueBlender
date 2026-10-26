import bpy, json, math, hashlib, os
from pathlib import Path
root = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
asset = root/'modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend'
gis_path = root/'audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/sources/crtn_fid914_gis_snapshot.json'
evidence_path = root/'audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/crtn_evidence.json'
collection_name='Asset_massing_creighton_hall_of_animal_sciences_crtn_a88d450'
with open(gis_path,encoding='utf-8-sig') as f: gis=json.load(f)
with open(evidence_path,encoding='utf-8') as f: evidence=json.load(f)
feature=gis['features'][0]
ring=feature['geometry']['rings'][0]
origin_lon,origin_lat=-86.9137,40.4274
lon_m,lat_m=84810.60416539927,111040.0
xy=[((p[0]-origin_lon)*lon_m,(p[1]-origin_lat)*lat_m) for p in ring[:-1]]
mins=[min(p[i] for p in xy) for i in (0,1)]; maxs=[max(p[i] for p in xy) for i in (0,1)]
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection=bpy.data.collections.get(collection_name)
obj=bpy.data.objects.get('Creighton Hall of Animal Sciences (CRTN)')
assert collection is not None and obj is not None
assert obj.type=='MESH'
verts=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
ground_xy=[(round(float(v.x),6),round(float(v.y),6)) for v in verts if abs(float(v.z))<1e-6]
source_xy=[(round(float(x),6),round(float(y),6)) for x,y in xy]
source_xy_unique=list(dict.fromkeys(source_xy))
ground_xy_unique=set(ground_xy)
source_vertex_nearest=[min(math.dist(p,q) for q in ground_xy_unique) for p in source_xy_unique]
source_ground_vertex_max_error_m=max(source_vertex_nearest)
source_ground_vertex_exact=(source_ground_vertex_max_error_m<0.002)
# count mesh connected components via vertex adjacency
adj=[set() for _ in obj.data.vertices]
for e in obj.data.edges:
    adj[e.vertices[0]].add(e.vertices[1]); adj[e.vertices[1]].add(e.vertices[0])
seen=set(); components=[]
for i in range(len(adj)):
    if i in seen: continue
    stack=[i]; seen.add(i); n=0
    while stack:
        u=stack.pop(); n+=1
        for v in adj[u]:
            if v not in seen: seen.add(v); stack.append(v)
    components.append(n)
inspection={'version':bpy.app.version_string,'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'asset_bytes':asset.stat().st_size,'scene_count':len(bpy.data.scenes),'collection_objects':[o.name for o in collection.objects],'collection_count':len(collection.objects),'object_name':obj.name,'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_edges':len(obj.data.edges),'mesh_polygons':len(obj.data.polygons),'components':len(components),'component_vertex_counts':sorted(components,reverse=True)[:20],'modifiers':[m.name for m in obj.modifiers],'dimensions':[float(x) for x in obj.dimensions],'bounds_world_m':bounds,'source_bounds_xy_m':[[min(mins),max(maxs)],[min(p[1] for p in xy),max(p[1] for p in xy)]],'source_geometry_keys':list(feature['geometry'].keys()),'source_FID':feature['attributes']['FID'],'source_ABBR':feature['attributes']['BLDG_ABBR'],'num_levels':feature['attributes']['NUM_LEVELS'],'linked_libraries':len(bpy.data.libraries),'images':[(im.name,im.filepath) for im in bpy.data.images],'mesh_bbox_xy_error_m':max(abs(bounds[i][j]-evidence['horizontal_validation']['bounds_xy_m'][i][j]) for i in (0,1) for j in (0,1)),'polygon_vertex_count':len(ring)-1,'ground_z_vertex_count':len(ground_xy_unique),'source_unique_xy_vertex_count':len(source_xy_unique),'source_ground_vertex_max_error_m':source_ground_vertex_max_error_m,'source_ground_vertex_exact':source_ground_vertex_exact}
(root/'audit/massing_creighton_hall_of_animal_sciences_crtn_a88d450/independent_grade/reopen_inspection.json').write_text(json.dumps(inspection,indent=2)+'\n',encoding='utf-8')
print(json.dumps(inspection,indent=2))



