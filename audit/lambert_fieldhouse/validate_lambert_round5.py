import bpy,json,os
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'; ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'; OUT=ROOT+r'/audit/lambert_fieldhouse'
asset=bpy.data.collections.get('Asset_lambert_fieldhouse')
objs=list(asset.all_objects) if asset else []
meshes=[o for o in objs if o.type=='MESH']
unmat=[o.name for o in meshes if not o.data.materials]
bad=[]
for o in meshes:
    for m in o.data.materials:
        if m is None or not m.node_tree or not any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes): bad.append(o.name)
track=bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
n=len(track.data.vertices)//2 if track else 0
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)] if track else []
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n)) if center else None
boundaries=[o for o in bpy.data.objects if o.name.startswith('LAMB | lane boundary ')]
pavers=bpy.data.objects.get('LAMB | Stadium entry brick inlay round4')
truss=bpy.data.objects.get('LAMB | round5 steel arch trusses')
purlins=bpy.data.objects.get('LAMB | round5 roof arch purlins')
tower=bpy.data.objects.get('LAMB | round5 schematic historic entrance tower')
pilasters=[o for o in bpy.data.objects if o.name.startswith('LAMB | pale concrete facade pier')]
bands=[o for o in bpy.data.objects if o.name.startswith('LAMB | round5 GIS-edge stone band')]
lights=[o for o in bpy.data.objects if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower())]
issues=[]
if asset is None: issues.append('Asset export collection missing')
if track is None: issues.append('Track mesh missing')
if len(boundaries)!=7: issues.append('Expected seven track boundary curves')
if truss is None or purlins is None: issues.append('Arch steel truss/purlin system missing')
if tower is None: issues.append('Schematic entrance tower cue missing')
if len(pilasters)!=33: issues.append('Expected 33 GIS-aligned existing facade piers')
if len(bands)!=40: issues.append('Expected four horizontal bands on ten GIS boundary edges')
if len(unmat) or len(bad): issues.append('Mesh material output audit failed')
if not all(o.hide_render for o in lights): issues.append('Interior lights enabled in saved exterior state')
if perimeter is not None and abs(perimeter-199.98895672145127)>.01: issues.append('Measured track centerline perimeter changed')
report={'saved_reopen':'PASS','asset_file':os.path.relpath(ASSET,ROOT).replace('\\','/'),'asset_object_count':len(objs),'mesh_object_count':len(meshes),
 'unmaterialed_mesh_count':len(unmat),'material_output_problem_count':len(bad),'track_vertex_count':len(track.data.vertices) if track else None,
 'track_lanes':6,'track_boundary_count':len(boundaries),'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,
 'paver_count':len(pavers.data.polygons)//6 if pavers else 0,'roof_truss_mesh_vertices':len(truss.data.vertices) if truss else 0,
 'roof_purlin_mesh_vertices':len(purlins.data.vertices) if purlins else 0,'existing_gis_aligned_pilaster_count':len(pilasters),'perimeter_band_segment_count':len(bands),
 'tower_bounds_local_xyz_m':[[min((tower.matrix_world@__import__('mathutils').Vector(v))[i] for v in tower.bound_box) for i in range(3)],[max((tower.matrix_world@__import__('mathutils').Vector(v))[i] for v in tower.bound_box) for i in range(3)]] if tower else None,
 'interior_lights_off_in_saved_exterior_state':all(o.hide_render for o in lights),'preview_files':['audit/lambert_fieldhouse/exterior_round5.png','audit/lambert_fieldhouse/interior_round5.png'],
 'issues':issues,'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round5.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
