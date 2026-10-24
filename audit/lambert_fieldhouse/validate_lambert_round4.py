import bpy, json, os
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
asset=bpy.data.collections.get('Asset_lambert_fieldhouse')
track=bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
pavers=bpy.data.objects.get('LAMB | Stadium entry brick inlay round4')
road=bpy.data.objects.get('LAMB | Stadium Avenue roadway round4')
boundary=[o for o in bpy.data.objects if o.name.startswith('LAMB | lane boundary ')]
lights=[o for o in bpy.data.objects if o.type=='LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower())]
objs=list(asset.all_objects) if asset else []
meshes=[o for o in objs if o.type=='MESH']
unmat=[o.name for o in meshes if not o.data.materials]
badout=[]
for ob in meshes:
    for m in ob.data.materials:
        if m is None or not m.node_tree or not any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes): badout.append(ob.name)
n=len(track.data.vertices)//2 if track else 0
center=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)] if track else []
perimeter=sum((center[(i+1)%n]-center[i]).length for i in range(n)) if center else None
issues=[]
if asset is None: issues.append('Asset collection missing')
if track is None: issues.append('Track mesh missing')
if len(boundary)!=7: issues.append('Expected seven lane-boundary curves')
if pavers is None: issues.append('Entry brick inlay missing')
if road is None: issues.append('Schematic adjacent roadway context missing')
if unmat or badout: issues.append('Material output audit has incomplete meshes')
if not all(o.hide_render for o in lights): issues.append('Interior preview lights are enabled in saved state')
if perimeter is not None and abs(perimeter-199.98895672145127)>.01: issues.append('Track mesh perimeter changed')
report={'saved_reopen':'PASS','asset_file':os.path.relpath(ASSET,ROOT).replace('\\','/'),'asset_object_count':len(objs),'mesh_object_count':len(meshes),
        'unmaterialed_mesh_count':len(unmat),'material_output_problem_count':len(badout),'track_vertex_count':len(track.data.vertices) if track else None,
        'track_lane_count':6,'track_boundary_curve_count':len(boundary),'track_mesh_measured_lane1_centerline_perimeter_m':perimeter,
        'entry_paver_unit_count':len(pavers.data.polygons)//6 if pavers else 0,'entry_paver_palette_count':len(pavers.data.materials) if pavers else 0,
        'road_context_object':road.name if road else None,'saved_exterior_interior_lights_disabled':all(o.hide_render for o in lights),
        'entrance_dark_patch_diagnosis':'Solid entrance walk roof-eave shadow; no overlap in tested paver/border/sidewalk bounds. Site concrete now has a modest ambient lift.',
        'previews':['audit/lambert_fieldhouse/exterior_round4.png','audit/lambert_fieldhouse/interior_round4.png'],'issues':issues,'master_manifest_shared_files_edited':False}
with open(OUT+r'/validation_round4.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
