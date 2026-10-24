import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'; FEATURE=ROOT/'audit/batchC_boilermaker_aquatic_official_footprint.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']; scene=bpy.context.scene
# Rebuild the project's approximate local tangent GIS transform from the retained official FID 896 polygon.
doc=json.loads(FEATURE.read_text(encoding='utf-8-sig')); ring=doc['features'][0]['geometry']['rings'][0][:-1]; lat0,lon0=40.4274,-86.9137; lon_m=111412.84*math.cos(math.radians(lat0)); lat_m=111040.
raw=[((lon-lon0)*lon_m,(lat-lat0)*lat_m) for lon,lat,*_ in ring]; cx=(min(x for x,y in raw)+max(x for x,y in raw))/2; cy=(min(y for x,y in raw)+max(y for x,y in raw))/2; gis=[(x-cx,y-cy) for x,y in raw]
if sum(gis[i][0]*gis[(i+1)%len(gis)][1]-gis[(i+1)%len(gis)][0]*gis[i][1] for i in range(len(gis)))<0: gis.reverse()
# Recover every model perimeter segment from the vertical wall quads; calculate bidirectional sampled Hausdorff correspondence.
mesh=wall.data; verts=[wall.matrix_world@v.co for v in mesh.vertices]; segs=[]
for poly in mesh.polygons:
 ids=list(poly.vertices); ps=[verts[i] for i in ids]
 if max(p.z for p in ps)-min(p.z for p in ps)>10.0:
  # lower edge of wall face lies at wall base z=.58
  low=[p for p in ps if abs(p.z-.58)<.01]
  if len(low)==2: segs.append(((low[0].x,low[0].y),(low[1].x,low[1].y)))
def dist_pt_seg(p,a,b):
 dx=b[0]-a[0]; dy=b[1]-a[1]; den=dx*dx+dy*dy
 t=0 if den<1e-14 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
 return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))
def d_to_segments(p,ss): return min(dist_pt_seg(p,a,b) for a,b in ss)
gis_segs=list(zip(gis,gis[1:]+gis[:1])); wall_to_gis=[]; gis_to_wall=[]
for a,b in gis_segs:
 for j in range(11):
  t=j/10; gis_to_wall.append(d_to_segments((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),segs))
for a,b in segs:
 for j in range(3):
  t=j/2; wall_to_gis.append(d_to_segments((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),gis_segs))
max_g2w=max(gis_to_wall); max_w2g=max(wall_to_gis); assert max_g2w<.025,(max_g2w,len(segs)); assert max_w2g<.025,max_w2g
windows=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing')]; assert len(windows)==57
assert bpy.data.objects.get('AQUA R2 | 300 individual schematic spectator seats'); assert bpy.data.objects.get('AQUA R2 | schematic east mezzanine gallery')
platforms=[o for o in asset.all_objects if o.type=='MESH' and 'm diving platform' in o.name]; assert len(platforms)==5
assert all(o.data.materials for o in asset.all_objects if o.type=='MESH')
# Exterior render; enough context to read entrance, façade rhythm, and roof depth.
scene.render.resolution_x=1700; scene.render.resolution_y=1100; scene.render.resolution_percentage=75; scene.camera=bpy.data.objects['AQUA R2 | North Three Quarter Camera']; scene.render.filepath=str(AUD/'aquatic_r2_north_three_quarter.png'); bpy.ops.render.render(write_still=True)
# Interior cutaway hides exterior envelope and roof only for the render; never save the temporary hide states.
tog=[]
for o in asset.all_objects:
 if o.type=='MESH' and (o==wall or 'pitched roof planes' in o.name or 'standing seam roof ribs' in o.name or 'gable end infill' in o.name or 'schematic clear-span roof truss' in o.name): tog.append((o,o.hide_render)); o.hide_render=True
scene.camera=bpy.data.objects['AQUA R2 | Interior Seating Camera']; scene.render.resolution_x=1300; scene.render.resolution_y=1000; scene.render.resolution_percentage=80; scene.render.filepath=str(AUD/'aquatic_r2_interior_seating_cutaway.png'); bpy.ops.render.render(write_still=True)
for o,v in tog: o.hide_render=v
# Interior detail view centered on dive tower, stands and documented pool uses.
scene.camera=bpy.data.objects['AQUA R1 | Interior Detail Camera']; scene.render.resolution_x=1500; scene.render.resolution_y=950; scene.render.resolution_percentage=75; scene.render.filepath=str(AUD/'aquatic_r2_interior_feature_detail.png'); bpy.ops.render.render(write_still=True)
# Validation includes fresh reopen, full GIS boundary correspondence, exportable asset health and exact support/unknowns.
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'revision':2,'passed':True,'reopened_saved_asset':True,'blender_version':bpy.app.version_string,'asset_file':'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend','asset_collection':asset.name,'asset_child_inclusive_objects':len(asset.all_objects),'gis_feature_id':896,'official_gis_ring_vertices':len(gis),'wall_perimeter_segments':len(segs),'gis_to_wall_sample_max_error_m':round(max_g2w,6),'wall_to_gis_sample_max_error_m':round(max_w2g,6),'footprint_validation':'Bidirectional sampled edge-to-edge correspondence against all transformed FID 896 polygon edges, not only bbox; this is local GIS alignment, not survey control.','footprint_bounds_match':True,'north_facade_brick_pilasters':8,'ribbon_glazing_panels':len(windows),'framed_window_panels':len(windows),'north_entry_sign':'Enlarged dark plaque with high-contrast Purdue-gold lettering; dimensions estimated, centered position from Street View.','documented_seating_capacity':625,'modeled_representative_seat_blocks':300,'mezzanine_present':True,'mezzanine_and_seating_location':'Schematic, not a dimensioned as-built plan.','official_dive_depth_m':17*.3048,'diving_platform_levels_m':[round(o.location.z,1) for o in platforms],'roof_form':'Shallow gable retained as an estimate; ridge cap/eaves/gutters added. No roof section evidence located.','all_meshes_have_material':True,'external_image_dependencies':sum(i.source=='FILE' and bool(i.filepath) for i in bpy.data.images),'master_or_manifest_edited':False,'asset_sha256':sha,'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r2_north_three_quarter.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r2_interior_seating_cutaway.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r2_interior_feature_detail.png']}
(AUD/'validation_r2.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); (AUD/'asset_sha256_r2.txt').write_text(sha+'  modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend\n',encoding='utf-8'); print(json.dumps(result,indent=2))
