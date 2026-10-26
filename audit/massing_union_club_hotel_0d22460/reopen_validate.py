import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_union_club_hotel_0d22460.blend'
out=root/'audit/massing_union_club_hotel_0d22460/reopen_validation.json'
gis=json.loads((root/'audit/official_purdue_buildings_wgs84.json').read_text(encoding='utf-8'))
feature=next(f for f in gis['features'] if f['attributes'].get('FID')==663)
def xy(lon,lat): return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
expected=[xy(p[0],p[1]) for p in feature['geometry']['rings'][0]]
if math.dist(expected[0],expected[-1])<.001: expected=expected[:-1]
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll=bpy.data.collections.get('Asset_massing_union_club_hotel_0d22460')
assert coll is not None
body=bpy.data.objects.get('Union Club Hotel')
assert body is not None and body.type=='MESH'
base=[]
for v in body.data.vertices:
    if abs(v.co.z)<1e-5:
        q=(round(v.co.x,6),round(v.co.y,6))
        if q not in base: base.append(q)
# Check exact transformed GIS point match (each source point appears in wall base).
nearest=[min(math.dist(p,q) for q in base) for p in expected]
world=[]
materialless=[]
for ob in coll.objects:
    if ob.type!='MESH': continue
    if len(ob.data.materials)==0: materialless.append(ob.name)
    deps=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(deps); me=ev.to_mesh()
    for v in me.vertices: world.append(ob.matrix_world@v.co)
    ev.to_mesh_clear()
mins=[min(v[i] for v in world) for i in range(3)]
maxs=[max(v[i] for v in world) for i in range(3)]
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.packed_file is None and im.filepath and not bpy.path.abspath(im.filepath).startswith('//'):
        missing.append(im.filepath)
report={
 'asset':str(asset),'reopened_saved_asset':True,'blender_version':bpy.app.version_string,
 'expected_collection':'Asset_massing_union_club_hotel_0d22460','collection_found':coll.name,
 'collection_object_count':len(coll.objects),'mesh_object_count':sum(o.type=='MESH' for o in coll.objects),
 'body_object':body.name,'body_vertex_count':len(body.data.vertices),'body_face_count':len(body.data.polygons),
 'base_ring_vertex_count':len(base),'source_ring_vertex_count':len(expected),
 'max_source_vertex_match_error_m':max(nearest),'all_source_vertices_match':max(nearest)<0.001,
 'evaluated_world_bounds_m':[mins,maxs],'evaluated_height_m':maxs[2]-mins[2],
 'materialless_mesh_objects':materialless,'unpacked_external_images':missing,
 'source_feature':{'id':663,'name':feature['attributes'].get('BUILDING_N'),'abbreviation':feature['attributes'].get('BLDG_ABBR'),'levels':feature['attributes'].get('NUM_LEVELS'),'extrution_attribute':feature['attributes'].get('Extrution'),'elevation':feature['attributes'].get('Elevation')},
 'limitations':['GIS R=63.1 and Extrution=72 likely use feet, but units are not documented in the local attribute snapshot; the 19.23 m roof eaves and approximately 21.75 m modeled roof/tower crown are estimates, not survey measurements.','Story count comes from GIS NUM_LEVELS=7; floor heights are estimated.','Circle Design Group exterior photography directly supports a pale stone projecting tower with a tall arched opening beside the broad gabled entry; Marriott photos support brick/stone palette, paired windows, and varied slate gables. Exact position, plan, pitch, heights, window spacing, and tower proportions remain estimates because no measured exterior elevations or calibrated camera views were found. The Purdue BOT PDF supplies floor plans only.','No master file opened or changed; coordinator must verify final link and marker.']}
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
