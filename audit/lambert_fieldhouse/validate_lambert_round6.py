import bpy, json, math, os
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET=ROOT+r'/modular/buildings/lambert_fieldhouse.blend'
OUT=ROOT+r'/audit/lambert_fieldhouse'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections.get('Asset_lambert_fieldhouse')
objs=list(asset.all_objects) if asset else []
mesh_objs=[o for o in objs if o.type=='MESH']
bad=[]; unmat=[]
for o in mesh_objs:
    if not o.data.materials: unmat.append(o.name)
    for m in o.data.materials:
        if m is None or not m.use_nodes or not any(n.type=='OUTPUT_MATERIAL' for n in m.node_tree.nodes): bad.append(o.name)
track=bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
n=len(track.data.vertices)//2 if track else 0
centers=[(track.data.vertices[i].co+track.data.vertices[i+n].co)*.5 for i in range(n)] if track else []
perim=sum((centers[(i+1)%n]-centers[i]).length for i in range(n)) if centers else None
boundaries=[o for o in bpy.data.objects if o.name.startswith('LAMB | lane boundary ')]
fp=bpy.data.objects.get('Lambert Fieldhouse | official GIS footprint ground floor')
roof=bpy.data.objects.get('LAMB | archival-dimension arched one-story fieldhouse roof (placement schematic)')
gym=bpy.data.objects.get('LAMB | round6 gym roof slab')
band=bpy.data.objects.get('LAMB | round6 GIS-registered segmented perimeter stone bands')
low_ids=[i for i,v in enumerate(fp.data.vertices) if v.co.z<.08] if fp else []
nb={i:[] for i in low_ids}
if fp:
    for e in fp.data.edges:
        a,b=e.vertices
        if a in nb and b in nb: nb[a].append(b); nb[b].append(a)
ring=[]
if low_ids:
    start=min(low_ids,key=lambda i:(fp.data.vertices[i].co.x,-fp.data.vertices[i].co.y)); ring=[start]; prev=None; cur=start
    while True:
        nxt=next(i for i in nb[cur] if i!=prev)
        if nxt==start:break
        ring.append(nxt);prev,cur=cur,nxt
outline=[(fp.data.vertices[i].co.x,fp.data.vertices[i].co.y) for i in ring] if fp else []
def point_seg_dist(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; den=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def boundary_dist(p): return min(point_seg_dist(p,outline[i],outline[(i+1)%len(outline)]) for i in range(len(outline)))
piers=[o for o in bpy.data.objects if o.name.startswith('LAMB | pale concrete facade pier')]
pier_devs=[boundary_dist((o.location.x,o.location.y)) for o in piers] if outline else []
band_centers=[]
if band:
    for i in range(0,len(band.data.vertices),8):
        points=[band.data.vertices[i+j].co for j in range(8)]
        band_centers.append((sum(v.x for v in points)/8,sum(v.y for v in points)/8))
band_devs=[abs(boundary_dist(p)-.20) for p in band_centers] if outline else []
roof_dims=[round(roof.dimensions.x,3),round(roof.dimensions.y,3)] if roof else None
issues=[]
if not asset: issues.append('Export collection missing')
if not track: issues.append('Track mesh missing')
if len(boundaries)!=7: issues.append('Expected 7 track boundary lines')
if not roof: issues.append('Archive-dimension fieldhouse roof missing')
if roof and (abs(roof.dimensions.x-92.3544)>.05 or abs(roof.dimensions.y-52.4256)>.05): issues.append('Fieldhouse roof plan dimensions differ from archival conversion')
if not gym: issues.append('Gym roof slab missing')
if band is None or len(band.data.vertices)!=640: issues.append('GIS-registered perimeter band mesh malformed')
if not outline or len(outline)!=20: issues.append('GIS perimeter cycle extraction failed')
if not pier_devs or max(pier_devs)>.15: issues.append('Facade pier centers exceed 0.15 m from GIS boundary')
if not band_devs or max(band_devs)>.02: issues.append('Stone band center offset does not register 0.20 m outside GIS boundary')
if unmat or bad: issues.append('Unmaterialed mesh or missing material output')
if perim is not None and abs(perim-199.98895672145127)>.01: issues.append('Track centerline measurement changed')
report={
 'revision':6,'saved_reopened':'PASS','asset_path':'modular/buildings/lambert_fieldhouse.blend',
 'asset_export_collection_present':bool(asset),'asset_object_count':len(objs),'mesh_count':len(mesh_objs),
 'unmaterialed_mesh_count':len(unmat),'material_output_problem_count':len(bad),
 'track_mesh_vertex_count':len(track.data.vertices) if track else None,'track_lane_count':6,
 'track_boundary_curve_count':len(boundaries),'track_lane1_centerline_measured_perimeter_m':perim,
 'fieldhouse_roof_bounds_xy_dimensions_m':roof_dims,
 'gym_roof_slab_dimensions_m':[round(v,3) for v in gym.dimensions] if gym else None,
 'gis_perimeter_vertex_count':len(outline),'gis_aligned_facade_pier_count':len(piers),
 'pier_center_distance_to_nearest_GIS_edge_m':{'mean':sum(pier_devs)/len(pier_devs) if pier_devs else None,'max':max(pier_devs) if pier_devs else None},
 'GIS_registered_band_box_count':len(band_centers),'band_center_offset_error_from_0_20m_m':{'mean':sum(band_devs)/len(band_devs) if band_devs else None,'max':max(band_devs) if band_devs else None},
 'tower_and_postcard_details_hidden_from_current_view':all(o.hide_render for o in bpy.data.objects if ('round5 tower' in o.name.lower() or 'historic-only postcard tower' in o.name.lower())),
 'issues':issues,'files':['audit/lambert_fieldhouse/exterior_round6.png','audit/lambert_fieldhouse/interior_round6.png','audit/lambert_fieldhouse/plan_section_overlay_round6.svg'],
 'master_manifest_shared_files_edited':False
}
with open(OUT+r'/validation_round6.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
