import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'; FEAT=ROOT/'audit/batchC_boilermaker_aquatic_official_footprint.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; scene=bpy.context.scene; wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']
# Recompute approximate local tangent GIS coordinates from official FID 896 and sample every segment both ways.
doc=json.loads(FEAT.read_text(encoding='utf-8-sig')); ring=doc['features'][0]['geometry']['rings'][0][:-1]; lat0,lon0=40.4274,-86.9137; lon_m=111412.84*math.cos(math.radians(lat0)); lat_m=111040.0
raw=[((lon-lon0)*lon_m,(lat-lat0)*lat_m) for lon,lat,*_ in ring]; cx=(min(x for x,y in raw)+max(x for x,y in raw))/2; cy=(min(y for x,y in raw)+max(y for x,y in raw))/2; gis=[(x-cx,y-cy) for x,y in raw]
if sum(gis[i][0]*gis[(i+1)%len(gis)][1]-gis[(i+1)%len(gis)][0]*gis[i][1] for i in range(len(gis)))<0: gis.reverse()
verts=[wall.matrix_world@v.co for v in wall.data.vertices]; segs=[]
for poly in wall.data.polygons:
 ps=[verts[i] for i in poly.vertices]
 if max(p.z for p in ps)-min(p.z for p in ps)>8:
  low=[p for p in ps if abs(p.z-.58)<.01]
  if len(low)==2:segs.append(((low[0].x,low[0].y),(low[1].x,low[1].y)))
def dseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy;t=0 if den<1e-12 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def nearest(p,ss):return min(dseg(p,a,b) for a,b in ss)
gs=list(zip(gis,gis[1:]+gis[:1])); er1=[];er2=[]
for a,b in gs:
 for j in range(11):
  t=j/10;er1.append(nearest((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),segs))
for a,b in segs:
 for j in range(3):
  t=j/2;er2.append(nearest((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t),gs))
err1=max(er1);err2=max(er2);assert err1<.025 and err2<.025,(err1,err2)
windows=[o for o in asset.all_objects if o.type=='MESH' and o.name.startswith('AQUA | facade bay') and o.name.endswith('glazing')]; assert len(windows)==57
assert bpy.data.objects.get('AQUA R1 | north facade building name') and bpy.data.objects.get('AQUA R2 | north entrance dark sign plaque') is None
assert bpy.data.objects.get('AQUA R2 | 300 individual schematic spectator seats'); assert bpy.data.objects.get('AQUA R2 | schematic east mezzanine gallery')
assert sum(1 for o in asset.all_objects if o.name.startswith('AQUA R3 | schematic mezzanine stair 1 tread'))==12
seams=bpy.data.objects['AQUA R3 | subtle standing seams on estimated roof']; assert len(seams.data.splines)==86
assert all(o.data.materials for o in asset.all_objects if o.type=='MESH')
assert not any(i.source=='FILE' and i.filepath for i in bpy.data.images)
# Full elevation render, close Street View angle, sign detail.
scene.render.engine='BLENDER_EEVEE'; scene.render.image_settings.file_format='PNG'; scene.render.resolution_x=1700; scene.render.resolution_y=1050; scene.render.resolution_percentage=80
scene.camera=bpy.data.objects['AQUA R3 | North Elevation Camera']; scene.render.filepath=str(AUD/'aquatic_r3_north_elevation.png'); bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R3 | Street Approach Camera']; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=80; scene.render.filepath=str(AUD/'aquatic_r3_street_approach.png'); bpy.ops.render.render(write_still=True)
scene.camera=bpy.data.objects['AQUA R2 | North Sign Camera']; scene.render.resolution_x=1200; scene.render.resolution_y=700; scene.render.resolution_percentage=100; scene.render.filepath=str(AUD/'aquatic_r3_entry_sign_detail.png'); bpy.ops.render.render(write_still=True)
# Interior feature camera: cutaway hides shell/façade/roof/structure, roof trusses and context floor for this render only.
vis=[]
for cn in ('AQUA_Facade','AQUA_Roof','AQUA_Structure'):
 c=bpy.data.collections[cn];vis.append((c,c.hide_render));c.hide_render=True
for o in asset.all_objects:
 if o is not None and ('schematic clear-span roof truss' in o.name or o.name=='AQUA | Purdue pool-hall sign lettering'):
  vis.append((o,o.hide_render));o.hide_render=True
site=bpy.data.objects.get('AQUA R2 | preview ground plane')
if site:vis.append((site,site.hide_render));site.hide_render=True
scene.camera=bpy.data.objects['AQUA R3 | Interior Gallery Camera']; scene.render.resolution_x=1450;scene.render.resolution_y=1000;scene.render.resolution_percentage=80;scene.render.filepath=str(AUD/'aquatic_r3_interior_gallery.png');bpy.ops.render.render(write_still=True)
for o,v in vis:o.hide_render=v
# Restore saved scene camera before validation output; no save is performed from this reopened render-only session.
scene.camera=bpy.data.objects['AQUA R3 | North Elevation Camera']
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'revision':3,'passed':True,'reopened_saved_asset':True,'blender_version':bpy.app.version_string,'asset_file':'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend','asset_collection':asset.name,'asset_objects':len(asset.all_objects),'gis_feature_id':896,'official_gis_ring_vertices':len(gis),'wall_perimeter_segments':len(segs),'gis_to_wall_sample_max_error_m':round(err1,6),'wall_to_gis_sample_max_error_m':round(err2,6),'footprint_validation':'Bidirectional edge sampling across complete transformed FID 896 polygon; GIS alignment only, not survey control or proof of master placement.','ribbon_windows':len(windows),'north_piers':sum(o.name.startswith('AQUA R3 | north brick pilaster') for o in asset.all_objects),'entry_sign':'Direct-mounted warm-white name lettering at Street View-supported location; plaque removed; text scale estimated.','roof_seam_splines':len(seams.data.splines),'roof_status':'Shallow gable remains uncertain; standing seams are a plausible material-detail treatment, not a sourced roof section.','seating_capacity_published':625,'representative_seat_blocks':300,'mezzanine_present':True,'mezzanine_stair_treads_per_flight':12,'mezzanine_supports':sum(o.name.startswith('AQUA R3 | mezzanine support') for o in asset.all_objects),'interior_layout':'Schematic; no dimensioned as-built plan found.','dive_pool_depth_m':5.1816,'platform_levels_m':[1.0,3.0,5.0,7.5,10.0],'all_meshes_have_material':True,'external_image_dependencies':0,'master_or_manifest_edited':False,'asset_sha256':sha,'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r3_north_elevation.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r3_street_approach.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r3_entry_sign_detail.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r3_interior_gallery.png'],'interior_render_cutaway':'Exterior facade, roof, structure, clear-span trusses, pool-hall lettering, and preview ground hidden only during render; flags restored.'}
(AUD/'validation_r3.json').write_text(json.dumps(result,indent=2)+'\n'); (AUD/'asset_sha256_r3.txt').write_text(sha+'  modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend\n'); print(json.dumps(result,indent=2))


