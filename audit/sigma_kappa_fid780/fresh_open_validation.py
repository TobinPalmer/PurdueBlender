import bpy,json,math,collections,os
BLEND='modular/buildings/massing_house_301840869_1b80ace.blend'
OUT='audit/sigma_kappa_fid780/fresh_open_validation.json'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.data.scenes.get('Building_massing_house_301840869_1b80ace')
coll=bpy.data.collections.get('Asset_massing_house_301840869_1b80ace')
root=bpy.data.objects.get('House_301840869')
packet=json.load(open('audit/sigma_kappa_fid780/source_fid780.json',encoding='utf-8-sig'))
ring=packet['features'][0]['geometry']['rings'][0][:-1]
src=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
world=[root.matrix_world@v.co for v in root.data.vertices]
base=[(v.x,v.y) for v in world if abs(v.z)<1e-4]
nearest=[]
for x,y in src:
    nearest.append(min(math.hypot(x-a,y-b) for a,b in base))
mins=[min(v[i] for v in world) for i in range(3)]; maxs=[max(v[i] for v in world) for i in range(3)]
face_counts=collections.Counter(p.material_index for p in root.data.polygons)
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.users>0 and not im.packed_file: images.append({'name':im.name,'filepath':im.filepath})
scene_objs=list(scene.objects); collection_objs=list(coll.objects)
result={
 'building':'Sigma Kappa — Beta Sigma Chapter','fid':780,'asset':BLEND,
 'blender_version':bpy.app.version_string,
 'scene':scene.name if scene else None,'collection':coll.name if coll else None,
 'scene_object_count':len(scene_objs),'collection_object_count':len(collection_objs),
 'scene_objects':[o.name for o in scene_objs], 'collection_objects':[o.name for o in collection_objs],
 'root_object':root.name if root else None,'root_type':root.type if root else None,
 'mesh_vertices':len(root.data.vertices),'mesh_edges':len(root.data.edges),'mesh_faces':len(root.data.polygons),
 'mesh_materials':[m.name if m else None for m in root.data.materials],
 'camera_light_objects':[o.name for o in scene_objs if o.type in {'CAMERA','LIGHT'}],
 'unpacked_external_images':images,
 'world_bounds_m':{'min':mins,'max':maxs,'dimensions':[maxs[i]-mins[i] for i in range(3)]},
 'source_ring_unique_vertices':len(src),'base_vertices_at_z0':len(base),'max_nearest_source_xy_error_m':max(nearest) if nearest else None,
 'source_ring_comparison':'The shell ring is generated from this GIS ring using the project-local approximate transform; match is by construction, not independent placement or survey validation.',
 'roof_and_height':'Estimated from secondary illustration; dimensions and unseen elevations unverified.',
 'interior':'One-level schematic inserts only; no floor plan or room dimensions are sourced.',
 'pass': bool(scene and coll and root and len(scene_objs)==1 and len(collection_objs)==1 and root in collection_objs and not images)
}
open(OUT,'w',encoding='utf-8').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
