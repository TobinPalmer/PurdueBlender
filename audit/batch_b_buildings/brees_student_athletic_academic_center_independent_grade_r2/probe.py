import bpy,json,hashlib,math
from pathlib import Path
ASSET=Path(bpy.data.filepath); ROOT=ASSET.parents[2]; AUDIT=ROOT/'audit'/'batch_b_buildings'; COL=bpy.data.collections.get('Asset_brees_student_athletic_academic_center'); objs=list(COL.all_objects) if COL else []
byname={o.name:o for o in objs}
origin=json.loads((AUDIT/'brees_student_athletic_academic_center_evidence.json').read_text(encoding='utf-8'))['official_gis']['campus_placement_origin_xy_m']
raw=json.loads((AUDIT/'brees_student_athletic_academic_center_gis_feature.json').read_text(encoding='utf-8'))
ring=raw['geometry']['rings'][0]
sx=84810.6041653993; sy=111040.0
pnts=[((lon+86.9137)*sx-origin[0],(lat-40.4274)*sy-origin[1]) for lon,lat in ring]
# Recover structural bottom boundary from mesh edges at z=0, and compare source-ring points to segments.
shell=next((o for o in objs if 'structural shell | GIS outline' in o.name),None)
actual=[]; actual_edges=[]
if shell and shell.type=='MESH':
    v=shell.data.vertices
    bottom={i for i,x in enumerate(v) if abs(x.co.z)<1e-5}
    actual=[(v[i].co.x,v[i].co.y) for i in bottom]
    actual_edges=[(v[e.vertices[0]].co.xy[:],v[e.vertices[1]].co.xy[:]) for e in shell.data.edges if e.vertices[0] in bottom and e.vertices[1] in bottom]
    actual_edges=[((float(a[0]),float(a[1])),(float(b[0]),float(b[1]))) for a,b in actual_edges]
def segdist(p,a,b):
    dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
    t=0 if den==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
source_to_mesh=max((min(segdist(p,a,b) for a,b in actual_edges) for p in pnts),default=None)
mesh_to_source=max((min(segdist(p,a,b) for a,b in zip(pnts,pnts[1:]+pnts[:1])) for p in actual),default=None)
glazing=byname.get('Facade glazing | repeated vision panels')
heights=[]
if glazing and glazing.type=='MESH':
    for f in glazing.data.polygons:
        zs=[glazing.data.vertices[i].co.z for i in f.vertices]
        if len(f.vertices)>=4: heights.append(max(zs)-min(zs))
rib=byname.get('BRES dark charcoal horizontal upper-wall siding ribs'); backing=byname.get('BRES continuous charcoal upper-cladding backing')
images=[{'name':i.name,'packed':bool(i.packed_file)} for i in bpy.data.images if i.name not in ('Render Result','Viewer Node')]
matimgs=[]
for mat in bpy.data.materials:
    if mat.use_nodes and mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image: matimgs.append({'material':mat.name,'image':n.image.name,'packed':bool(n.image.packed_file)})
report={'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'stable_collection':COL.name if COL else None,'object_count':len(objs),'shell_name':shell.name if shell else None,'shell_z_bounds': [min((v.co.z for v in shell.data.vertices),default=None),max((v.co.z for v in shell.data.vertices),default=None)] if shell else None,'source_ring_points':len(pnts),'model_bottom_vertices':len(actual),'bottom_boundary_edges':len(actual_edges),'max_source_to_model_edge_error_m':source_to_mesh,'max_model_to_source_edge_error_m':mesh_to_source,'glazing_face_height_values_m':sorted(set(round(x,3) for x in heights)),'glazing_quads':len(heights),'rib_faces':len(rib.data.polygons) if rib else None,'rib_vertices':len(rib.data.vertices) if rib else None,'backing_faces':len(backing.data.polygons) if backing else None,'packed_images':images,'image_materials':matimgs,'schematic_only_objects':[o.name for o in objs if 'schematic_only' in o.name.casefold()],'facade_named_objects':[o.name for o in objs if any(k in o.name.casefold() for k in ('slit','window','cladding','rib','banner'))]}
out=Path(__file__).with_name('direct_asset_probe.json'); out.write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
