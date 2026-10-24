import bpy,json,math,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'; FEAT=ROOT/'audit/batchC_boilermaker_aquatic_official_footprint.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'];wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope'];
# Recompute complete GIS-vs-shell perimeter check from reopened saved file.
doc=json.loads(FEAT.read_text(encoding='utf-8-sig'));ring=doc['features'][0]['geometry']['rings'][0][:-1];lat0,lon0=40.4274,-86.9137;lon_m=111412.84*math.cos(math.radians(lat0));lat_m=111040.0
raw=[((lon-lon0)*lon_m,(lat-lat0)*lat_m) for lon,lat,*_ in ring];cx=(min(x for x,y in raw)+max(x for x,y in raw))/2;cy=(min(y for x,y in raw)+max(y for x,y in raw))/2;gis=[(x-cx,y-cy) for x,y in raw]
if sum(gis[i][0]*gis[(i+1)%len(gis)][1]-gis[(i+1)%len(gis)][0]*gis[i][1] for i in range(len(gis)))<0:gis.reverse()
verts=[wall.matrix_world@v.co for v in wall.data.vertices];segs=[]
for poly in wall.data.polygons:
 ps=[verts[i] for i in poly.vertices]
 if max(p.z for p in ps)-min(p.z for p in ps)>8:
  low=[p for p in ps if abs(p.z-.58)<.01]
  if len(low)==2:segs.append(((low[0].x,low[0].y),(low[1].x,low[1].y)))
def dseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=0 if den<1e-12 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def nearest(p,ss):return min(dseg(p,a,b) for a,b in ss)
gs=list(zip(gis,gis[1:]+gis[:1]));e1=[];e2=[]
for a,b in gs:
 for j in range(11):t=j/10;e1.append(nearest((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),segs))
for a,b in segs:
 for j in range(3):t=j/2;e2.append(nearest((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),gs))
err1=max(e1);err2=max(e2);assert err1<.025 and err2<.025,(err1,err2)
ctx=bpy.data.collections['AQUA_R5_Context | approximate site dressing'];r7=bpy.data.collections['AQUA_R7 | integrated natatorium lighting and seating'];tr=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')];fixtures=[o for o in r7.objects if o.name.startswith('AQUA R7 | LED high-bay fixture')];area_lights=[o for o in r7.objects if o.type=='LIGHT' and o.name.startswith('AQUA R7 | integrated overhead LED')];banners=[o for o in r7.objects if o.name.startswith('AQUA R7 | suspended Purdue banner')];letters=[o for o in r7.objects if o.name.startswith('AQUA R7 | Purdue banner text')]
assert len(ctx.objects)==21;assert len(r7.objects)==46;assert len(tr)==21;assert len(fixtures)==18;assert len(area_lights)==18;assert len(banners)==2;assert len(letters)==4
assert len([o for o in bpy.data.objects if o.name.startswith('AQUA R7 | pool hall integrated interior camera')])==1
assert sum(1 for o in asset.all_objects if o.name.startswith('AQUA R4 | schematic center aisle tread'))==12
assert sum(1 for o in asset.all_objects if o.name.startswith('AQUA R4 | split east grandstand step'))==24
assert len([o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing')])==57
assert all(o.data.materials for o in asset.all_objects if o.type=='MESH');assert not any(i.source=='FILE' and i.filepath for i in bpy.data.images)
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'revision':7,'passed':True,'reopened_saved_asset':True,'blender_version':bpy.app.version_string,'asset':'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend','asset_collection':asset.name,'asset_objects':len(asset.all_objects),'asset_sha256':sha,'gis_feature_id':896,'gis_ring_vertices':len(gis),'wall_perimeter_segments':len(segs),'gis_to_shell_max_sampled_error_m':round(err1,6),'shell_to_gis_max_sampled_error_m':round(err2,6),'footprint_claim':'Local FID 896 boundary correspondence only; not master registration, survey placement, height, roof or elevation validation.','r7_collection_objects':len(r7.objects),'painted_steel_truss_meshes':len(tr),'representative_molded_seats':288,'center_aisle_treads':12,'split_tier_sections':24,'ribbon_glazing_panes':57,'high_bay_fixture_meshes':len(fixtures),'integrated_area_lights':len(area_lights),'suspended_purdue_display_panels':len(banners),'purdue_display_lettering_objects':len(letters),'optional_approximate_site_context_objects':len(ctx.objects),'material_assignment_passed':True,'external_image_dependencies':0,'master_or_shared_files_edited':False,'committed':False,'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r7_interior_integrated_lighting.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r7_interior_seating_detail.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r7_north_entry_approach.png'],'uncertainties':['No measured roof section/eave/ridge height located; roof geometry remains unverified.','The exposed steel truss finish is photo-supported, but truss member layout and geometry are schematic.','High-bay lighting and Purdue banner positions/sizes are qualitative photo-based presentation estimates, not an as-built lighting plan.','Spectator count/arrangement is representative and circulation schematic; published seating capacity is 625.','The optional site collection remains approximate and un-georeferenced.','GIS-to-shell comparison does not prove campus-master placement or survey accuracy.']}
(AUD/'validation_r7.json').write_text(json.dumps(result,indent=2)+'\n');(AUD/'asset_sha256_r7.txt').write_text(sha+'  modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend\n');print(json.dumps(result,indent=2))
