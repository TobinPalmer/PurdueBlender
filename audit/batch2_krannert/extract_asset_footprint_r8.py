import bpy, json, math, os
from mathutils import Matrix
blend=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krannert_building.blend'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch2_krannert\asset_footprint_round8.json'
bpy.ops.wm.open_mainfile(filepath=blend)
name='KRAN_FloorSlab_Roof_Deck'
obj=bpy.data.objects.get(name)
if obj is None or obj.type!='MESH': raise RuntimeError('Missing roof deck mesh')
mesh=obj.data
zmax=max(v.co.z for v in mesh.vertices)
# The saved mesh is an identity-transformed campus-world mesh. Extract its upper perimeter in stored ring order.
points=[]
for v in mesh.vertices:
    if abs(v.co.z-zmax)<1e-5:
        co=obj.matrix_world @ v.co
        points.append([float(co.x),float(co.y)])
# Deduplicate any exact repeated vertices without reordering.
seen=set(); unique=[]
for p in points:
    key=(round(p[0],6),round(p[1],6))
    if key not in seen: seen.add(key); unique.append(p)
lat0=40.4274; lon0=-86.9137; xscale=111412.84*math.cos(math.radians(lat0)); yscale=111040.0
ring=[]
for x,y in unique:
    ring.append([lon0+(x+234.5345001220703)/xscale,lat0+(y-412.71900939941406)/yscale])
# Match each projected vertex to its closest raw FID54 ring vertex (recorded only as source-derived trace comparison).
gis=json.load(open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batch2_krannert\krannert_gis_fid54_4326.json',encoding='utf-8'))['features'][0]['geometry']['rings'][0]
def haversine_m(a,b):
    R=6371008.8; p1=math.radians(a[1]);p2=math.radians(b[1]);dl=math.radians(b[0]-a[0]);dp=p2-p1
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
dists=[]
for p in ring:
    dists.append(min(haversine_m(p,q) for q in gis))
record={
 'revision':8,'asset': 'modular/buildings/krannert_building.blend','asset_reopened':True,
 'blender_version':bpy.app.version_string,'object':name,'object_matrix_world':[[float(v) for v in row] for row in obj.matrix_world],
 'mesh_vertices':len(mesh.vertices),'mesh_polygons':len(mesh.polygons),'top_z_m':float(zmax),
 'extracted_top_ring_vertex_count':len(ring),'asset_local_xy_m':unique,'manifest_placement_origin_xy_m':[234.5345001220703,-412.71900939941406],'campus_world_xy_m':[[p[0]+234.5345001220703,p[1]-412.71900939941406] for p in unique],'wgs84_ring_from_project_approximation':ring,
 'project_approximation':{'lon_origin':lon0,'lat_origin':lat0,'x_m_per_degree':xscale,'y_m_per_degree':yscale,'status':'approximate campus-local projection; not surveyed CRS'},
 'raw_gis_nearest_vertex_comparison_m':{'mean':sum(dists)/len(dists),'max':max(dists),'warning':'Both the roof slab outline and project footprint originated from Purdue GIS; this verifies the saved asset conversion/coordinates, not independent as-built accuracy.'},
 'render':'audit/batch2_krannert/krannert_asset_footprint_ortho_overlay_r8.png',
 'limits':['roof-deck perimeter is a source-derived GIS outline, not a measured exterior wall footprint','orthophoto is a visual cross-check; shadows, parapet/overhang and display export resolution limit sub-meter claims','no translation, scale or rotation was fitted to the aerial']}
with open(out,'w',encoding='utf-8') as f: json.dump(record,f,indent=2)
print(json.dumps({k:record[k] for k in ['asset_reopened','blender_version','mesh_vertices','top_z_m','extracted_top_ring_vertex_count','raw_gis_nearest_vertex_comparison_m']},indent=2))


