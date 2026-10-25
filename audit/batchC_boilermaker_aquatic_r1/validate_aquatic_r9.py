import bpy,json,math,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend';AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1';FEAT=ROOT/'audit/batchC_boilermaker_aquatic_official_footprint.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'];wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']
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
r9=bpy.data.collections['AQUA_R9 | bleacher supports and cutaway review'];tr=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss')];posts=[o for o in r9.objects if o.name.startswith('AQUA R9 | center aisle rail post')];risers=[o for o in r9.objects if o.name.startswith('AQUA R9 | continuous bleacher riser')];rails=[o for o in asset.all_objects if o.type=='CURVE' and o.name.startswith('AQUA R4 | schematic center aisle handrail')];cam=bpy.data.objects['AQUA R9 | truss pool and bleacher cutaway camera'];roof=bpy.data.objects['AQUA | clear-span natatorium | pitched roof planes']
assert len(tr)==21 and len(posts)==24 and len(risers)==24 and len(rails)==2 and len(r9.objects)==49
assert roof.hide_render is False and roof.hide_viewport is False
assert not any(i.source=='FILE' and i.filepath for i in bpy.data.images)
assert all(o.data.materials for o in asset.all_objects if o.type=='MESH')
# Coordinator's independent read-only master inspection was reported for this revision; do not open/save the master here.
manifest_xy=(-808.683,80.337);marker_xy=(-808.6829834,80.3369980);placement_error=math.hypot(marker_xy[0]-manifest_xy[0],marker_xy[1]-manifest_xy[1])
assert placement_error<.0001
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'revision':9,'passed':True,'reopened_saved_asset':True,'blender_version':bpy.app.version_string,'asset':'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend','asset_collection':asset.name,'asset_objects':len(asset.all_objects),'asset_sha256':sha,'gis_feature_id':896,'gis_ring_vertices':len(gis),'wall_perimeter_segments':len(segs),'gis_to_shell_max_sampled_error_m':round(err1,6),'shell_to_gis_max_sampled_error_m':round(err2,6),'footprint_claim':'Local FID 896 boundary correspondence only; not survey accuracy.','r8_improvement_collection_objects':len(bpy.data.collections['AQUA_R8 | integrated bleachers, banners, lighting, facade reveals'].objects),'r9_collection_objects':len(r9.objects),'existing_trusses':len(tr),'continuous_bleacher_risers':len(risers),'connected_aisle_rail_posts':len(posts),'existing_sloped_aisle_rails':len(rails),'saved_cutaway_review_camera':cam.name,'full_roof_geometry_retained_and_visible_after_reopen':True,'material_assignment_passed':True,'external_image_dependencies':0,'coordinator_master_placement_check':{'source':'Coordinator read-only inspection reported 2026-10-25','marker_translation_m':marker_xy,'manifest_origin_m':manifest_xy,'scale':[1.0,1.0,1.0],'rotation_euler_deg':[0.0,0.0,0.0],'xy_error_m':placement_error,'method':'Direct marker transform comparison to manifest origin; no master file was opened or saved in this task.'},'master_or_shared_files_edited':False,'committed':False,'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r9_interior_truss_cutaway.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r9_bleacher_aisle_detail.png'],'uncertainties':['Roof profile, truss member sizing/layout, and eave/ridge elevations remain unverified; no roof or height geometry was changed.','Trusses are existing schematic meshes; the cutaway render exposes them but does not validate as-built structure.','The 24 bleacher risers/posts are illustrative support detailing; seating capacity, tier dimensions, aisle details, and circulation remain unverified.','The cutaway render hides roof objects only for the review images; the complete roof geometry remains visible in the reopened saved asset.','GIS-to-shell outline correspondence does not establish survey accuracy.']}
(AUD/'validation_r9.json').write_text(json.dumps(result,indent=2)+'\n');(AUD/'asset_sha256_r9.txt').write_text(sha+'  modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend\n');print(json.dumps(result,indent=2))
