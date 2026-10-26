import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_cary_quadrangle_east_cqe_230c813'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
SOURCE = ROOT / 'audit' / ASSET_ID / 'sources' / 'purdue_building_shapes_fid639_cqe_2026-10-25.geojson'
OUT = ROOT / 'audit' / 'massing_cary_quadrangle_east_cqe_independent_grade' / 'blender_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col = bpy.data.collections.get(f'Asset_{ASSET_ID}')
assert col and col.get('asset_id') == ASSET_ID
src = json.loads(SOURCE.read_text(encoding='utf-8-sig'))['features'][0]
props = src['properties']
ring = src['geometry']['coordinates'][0][:-1]
def project(ll):
    lon, lat = ll
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0)
sp = [project(p) for p in ring]
def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
def perimeter(poly):
    return sum(math.dist(poly[i], poly[(i+1)%len(poly)]) for i in range(len(poly)))
def pseg(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; d=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d)) if d else 0
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def directed(points,poly):
    return [min(pseg(p,poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))) for p in points]
wall=bpy.data.objects.get('CQE_Brick_Wall_Shell')
assert wall and wall.type=='MESH'
mesh=wall.data
bottom=[]
for v in mesh.vertices:
    q=wall.matrix_world @ v.co
    if abs(q.z-0.9)<1e-5: bottom.append((q.x,q.y))
# Deduplicate repeated corners while preserving order.
uniq=[]
for p in bottom:
    if not any(math.dist(p,q)<1e-6 for q in uniq): uniq.append(p)
# The wall's lateral faces are ordered around its footprint; extract each side's bottom vertex.
built=[]
for poly in mesh.polygons[:len(uniq)]:
    coords=[wall.matrix_world @ mesh.vertices[i].co for i in poly.vertices]
    bot=[(v.x,v.y) for v in coords if abs(v.z-0.9)<1e-5]
    if bot: built.append(bot[0])
if len(built)!=len(uniq):
    # Vertices are stored as one closed footprint ring on the bottom cap.
    built=uniq
# bidirectional boundary discrepancy, compare source and wall-shell perimeter points
s_to_b=directed(sp,built); b_to_s=directed(built,sp)
allobjs=list(col.objects)
meshobjects=[o for o in allobjs if o.type=='MESH']
coords=[o.matrix_world @ Vector(c) for o in meshobjects for c in o.bound_box]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
report={
 'asset_id':ASSET_ID,'scene':bpy.context.scene.name,'collection':col.name,
 'source_feature':{'id':src.get('id'),'FID':props.get('FID'),'BLDG_ABBR':props.get('BLDG_ABBR'),'BUILDING_N':props.get('BUILDING_N'),'NUM_LEVELS':props.get('NUM_LEVELS'),'CountOfFLO':props.get('CountOfFLO'),'Extrution':props.get('Extrution'),'source_geometry_vertices_closed':len(ring)+1,'projected_area_m2':area(sp),'projected_perimeter_m':perimeter(sp),'projected_bounds_xy_m':[[min(p[i] for p in sp),max(p[i] for p in sp)] for i in range(2)]},
 'asset':{'objects':len(allobjs),'mesh_objects':len(meshobjects),'bounds_world_m_xyz':bounds,'all_mesh_objects_identity_transform':all(max(abs(x) for x in tuple(o.location)+tuple(o.rotation_euler))<1e-6 and max(abs(x-1) for x in o.scale)<1e-6 for o in meshobjects),'external_object_libraries':sorted({o.library.filepath for o in meshobjects if o.library}),'wall_shell_vertices':len(mesh.vertices),'wall_shell_faces':len(mesh.polygons),'wall_footprint_boundary_vertices':len(built),'wall_footprint_area_m2':area(built),'wall_footprint_perimeter_m':perimeter(built),'wall_vs_source_boundary_distance_m':{'source_to_wall_max':max(s_to_b),'wall_to_source_max':max(b_to_s),'source_to_wall_mean':sum(s_to_b)/len(s_to_b),'wall_to_source_mean':sum(b_to_s)/len(b_to_s)},'roof_objects':[o.name for o in meshobjects if 'Roof' in o.name or 'Dormer' in o.name],'facade_objects':[o.name for o in meshobjects if any(t in o.name for t in ('Window','Pilaster','Entrance','Entry','Belt','Stone'))]},
 'independent_method':'Reopened saved .blend in Blender; directly measured evaluated asset mesh world bounds and extracted source-derived perimeter from brick wall shell; projected raw archived GIS WGS84 polygon using the repository conversion; compared boundary distances to raw unsimplified source ring. No builder validation result reused.'}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

