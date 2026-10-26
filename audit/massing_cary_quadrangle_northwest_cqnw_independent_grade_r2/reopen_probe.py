import bpy, json, math
from pathlib import Path

root = Path(bpy.path.abspath('//')).resolve()
# Use fixed paths through environment for this standalone Blender probe.
asset = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender\modular\buildings\massing_cary_quadrangle_northwest_cqnw_e8a861e.blend')
repo = asset.parents[2]
out = repo / 'audit' / 'massing_cary_quadrangle_northwest_cqnw_independent_grade_r2'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
coll = bpy.data.collections.get('Asset_massing_cary_quadrangle_northwest_cqnw_e8a861e')
objs = list(coll.objects) if coll else []
mesh_objs = [o for o in objs if o.type == 'MESH']
expected_name='Cary Quadrangle Northwest (CQNW)'
obj = next((o for o in mesh_objs if o.name == expected_name), None)
verts=[]; faces=[]; bounds=None; material_names=[]
if obj:
    deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); me=ev.to_mesh()
    verts=[tuple(float(x) for x in ev.matrix_world @ v.co) for v in me.vertices]
    faces=[tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    if verts:
        bounds=[[min(v[a] for v in verts),max(v[a] for v in verts)] for a in range(3)]
    material_names=[m.name if m else None for m in obj.data.materials]
    # Foundation bottom ring vertices are the only large, contiguous set at Z=0.
    bottom=[(v[0],v[1]) for v in verts if abs(v[2])<1e-5]
    bottom_faces=[f for f in faces if len(f)>=8 and all(abs(verts[i][2])<1e-5 for i in f)]
    bottom_ring=max(bottom_faces,key=len) if bottom_faces else []
    bottom_poly=[(verts[i][0],verts[i][1]) for i in bottom_ring]
    # Convex hull from bottom points for a diagnostic boundary envelope.
    pts=sorted(set(bottom))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    hi=[]
    for p in reversed(pts):
        while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0: hi.pop()
        hi.append(p)
    hull=lo[:-1]+hi[:-1]
else: bottom=[]; hull=[]; bottom_poly=[]
# Validate raw source geometry independently using repository transform.
gis_path=repo/'audit'/'massing_cary_quadrangle_northwest_cqnw_e8a861e'/'sources'/'purdue_building_shapes_fid647_2026-10-26.geojson'
fc=json.loads(gis_path.read_text(encoding='utf-8-sig')); feature=fc['features'][0]
props=feature['properties']; ring=feature['geometry']['coordinates'][0]
def project(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
projected=[project(*xy) for xy in ring]
source_min=[[min(p[i] for p in projected),max(p[i] for p in projected)] for i in range(2)]
# Point-to-segment measurements from raw boundary vertices to modeled footprint hull.
def segdist(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];d=dx*dx+dy*dy;t=0 if d==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def boundary_dist(p,poly): return min(segdist(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))) if poly else None
source_to_model=[boundary_dist(p,bottom_poly) for p in projected[:-1]]
# sample shell vertices at foundation level to nearest source boundary
model_to_source=[boundary_dist(p,projected[:-1]) for p in bottom]
external=[]
for im in bpy.data.images:
    fp=im.filepath
    if fp and not fp.startswith('//') and not Path(bpy.path.abspath(fp)).exists(): external.append(fp)
report={
 'asset':str(asset.relative_to(repo)), 'blender_version':bpy.app.version_string,
 'scene':scene.name,'expected_scene':'Building_massing_cary_quadrangle_northwest_cqnw_e8a861e',
 'collection':coll.name if coll else None,'collection_object_count':len(objs),
 'collection_objects':[{'name':o.name,'type':o.type} for o in objs],
 'expected_object_found':obj is not None,'evaluated_vertex_count':len(verts),'evaluated_face_count':len(faces),
 'evaluated_bounds_world_m':bounds,'object_location':list(obj.location) if obj else None,
 'object_rotation':list(obj.rotation_euler) if obj else None,'object_scale':list(obj.scale) if obj else None,
 'modifier_count':len(obj.modifiers) if obj else None,'material_names':material_names,
 'external_missing_image_paths':external,
 'gis':{'feature_id':props.get('FID'),'abbreviation':props.get('BLDG_ABBR'),'name':props.get('BUILDING_N'),'levels':props.get('NUM_LEVELS'),'source_ring_vertices':len(ring)-1,'projected_bounds_xy_m':source_min,
 'model_foundation_vertex_count':len(bottom),'model_bottom_boundary_vertices':len(bottom_poly),'model_bottom_boundary_xy_m':bottom_poly,'max_source_vertex_distance_to_model_boundary_m':max(source_to_model) if source_to_model else None,
 'mean_source_vertex_distance_to_model_bottom_hull_m':sum(source_to_model)/len(source_to_model) if source_to_model else None,
 'max_model_bottom_vertex_distance_to_raw_source_ring_m':max(model_to_source) if model_to_source else None,
 'mean_model_bottom_vertex_distance_to_raw_source_ring_m':sum(model_to_source)/len(model_to_source) if model_to_source else None,
 'method':'Official FID 647 EPSG:4326 raw polygon converted using project local approximation; independent vertex-to-segment distances compare raw source ring against actual mesh bottom face boundary.'},
 'inspection_notes':['Saved library reopened directly in Blender.','Asset collection contains the named building mesh; preview camera/ground are outside exported collection.','joined mesh is single object but includes disconnected mesh islands for facade detail and wall/roof elements.']
}
(out/'blender_probe.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))



