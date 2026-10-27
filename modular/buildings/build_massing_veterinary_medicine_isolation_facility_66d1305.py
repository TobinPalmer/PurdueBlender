import bpy, json, math, os
from mathutils import Vector, Quaternion
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_veterinary_medicine_isolation_facility_66d1305'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
AUDIT = ROOT / 'audit' / 'veterinary_medicine_isolation_facility'
FEATURE_PATH = AUDIT / 'purdue_gis_VMIF_feature.json'
COLLECTION_NAME = f'Asset_{ASSET_ID}'
SCENE_NAME = f'Building_{ASSET_ID}'

feature = json.loads(FEATURE_PATH.read_text(encoding='utf-8'))
attrs = feature['attributes']
ring = feature['geometry']['rings'][0]
# Project the official WGS84 GIS polygon into the project's documented local
# tangent-plane approximation (metres east/north), then use its area centroid.
lat0, lon0 = 40.4274, -86.9137
mxlon, mlat = 111412.84 * math.cos(math.radians(lat0)), 111040.0
world = [((lon-lon0)*mxlon, (lat-lat0)*mlat) for lon, lat in ring[:-1]]
def polygon_centroid(points):
    a2 = cx = cy = 0.0
    for i, (x,y) in enumerate(points):
        x2,y2 = points[(i+1)%len(points)]
        cross = x*y2-x2*y
        a2 += cross; cx += (x+x2)*cross; cy += (y+y2)*cross
    return (cx/(3*a2), cy/(3*a2))
anchor = polygon_centroid(world)
coordinate_area_m2=abs(sum(world[i][0]*world[(i+1)%len(world)][1]-world[(i+1)%len(world)][0]*world[i][1] for i in range(len(world)))/2)
poly = [(x-anchor[0], y-anchor[1]) for x,y in world]

# Orient the schematic room plan to the principal footprint axes.
mean_x = sum(p[0] for p in poly)/len(poly); mean_y = sum(p[1] for p in poly)/len(poly)
xx = sum((x-mean_x)**2 for x,y in poly); yy = sum((y-mean_y)**2 for x,y in poly)
xy = sum((x-mean_x)*(y-mean_y) for x,y in poly)
theta = 0.5*math.atan2(2*xy, xx-yy)
# Ensure U follows the long axis.
if xx < yy: theta += math.pi/2
ct, st = math.cos(theta), math.sin(theta)
def to_uv(p): return (ct*p[0]+st*p[1], -st*p[0]+ct*p[1])
def to_xy(u,v): return (ct*u-st*v, st*u+ct*v)
uv = [to_uv(p) for p in poly]
u_min,u_max = min(p[0] for p in uv),max(p[0] for p in uv)
v_min,v_max = min(p[1] for p in uv),max(p[1] for p in uv)
L,W=u_max-u_min,v_max-v_min

# Fresh asset scene, preserving stable scene/collection contract.
scene=bpy.context.scene; scene.name=SCENE_NAME
scene.unit_settings.system='METRIC'; scene.render.engine='CYCLES'
scene.render.resolution_x=1100; scene.render.resolution_y=850; scene.render.resolution_percentage=100
scene.cycles.samples=24
scene.world=bpy.data.worlds.new('VMIF studio world'); scene.world.use_nodes=True; scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0.24,0.27,0.31,1); scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=0.65; scene.world.color=(0.19,0.22,0.27)
coll=bpy.data.collections.new(COLLECTION_NAME); scene.collection.children.link(coll)

# Material palette: restrained service-facility palette. Masonry and roof choices
# are visualization assumptions because no facade specification was found.
def mat(name, color, rough=.72, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    return m
brick=mat('Light painted masonry (interior photo reference; exterior finish inferred)',(0.70,0.68,0.60)); roofmat=mat('White low-slope membrane roof (aerial reference)',(0.78,0.79,0.77)); trim=mat('Pale concrete plinth and edge',(0.73,0.72,0.67)); glass=mat('Observation window glazing',(0.22,0.34,0.40),.24); metal=mat('Galvanized service door',(0.36,0.39,0.39),.52,0.18); floor=mat('Interior sealed concrete',(0.39,0.40,0.38)); partition=mat('Washable pale interior masonry',(0.76,0.75,0.68)); stallmat=mat('Stall divider enamel',(0.30,0.32,0.30),.48,0.16); labelmat=mat('Room markers',(0.84,0.79,0.60))

# Optionally add a procedural masonry bump; no external texture paths.
p=brick.node_tree.nodes.get('Principled BSDF'); tex=brick.node_tree.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=38; tex.inputs['Detail'].default_value=2.0
bump=brick.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.07; bump.inputs['Distance'].default_value=.018
brick.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']); brick.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
# Faint block coursing follows the cream-painted masonry visible in Purdue's 2005
# interior photo; exterior use of this finish is a low-confidence inference.
wave=brick.node_tree.nodes.new('ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='Z'; wave.inputs['Scale'].default_value=18.0; wave.inputs['Distortion'].default_value=0.0
bump2=brick.node_tree.nodes.new('ShaderNodeBump'); bump2.inputs['Strength'].default_value=.13; bump2.inputs['Distance'].default_value=.012
brick.node_tree.links.new(wave.outputs['Color'],bump2.inputs['Height']); brick.node_tree.links.new(bump2.outputs['Normal'],p.inputs['Normal'])

def mesh_obj(name, verts, faces, material, target=coll):
    me=bpy.data.meshes.new(name+'Mesh'); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); target.objects.link(ob); return ob

def box(name, center, dims, material, rotation=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(center[0],center[1],center[2]))
    ob=bpy.context.object; ob.name=name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob); ob.dimensions=dims; ob.rotation_euler[2]=rotation
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(material); return ob

def beam_uv(name,u0,v0,u1,v1,z0,z1,width,material):
    du,dv=u1-u0,v1-v0; length=math.hypot(du,dv); um,vm=(u0+u1)/2,(v0+v1)/2; x,y=to_xy(um,vm)
    return box(name,(x,y,(z0+z1)/2),(length,width,z1-z0),material,theta+math.atan2(dv,du))

# GIS wall shell with one interpreted large-animal service opening on the paved
# west side. Aerial imagery shows the adjacent service apron, but cannot resolve
# the door leaf itself; its dimensions/location are conservative and inferred.
eave=3.60 # visualization estimate for one storey; GIS extrusion units are undocumented
wall_top=eave
door_edge=10
door_width=3.0; door_height=2.85
edge_length=math.hypot(poly[(door_edge+1)%len(poly)][0]-poly[door_edge][0],poly[(door_edge+1)%len(poly)][1]-poly[door_edge][1])
door_t0=.45-door_width/(2*edge_length); door_t1=.45+door_width/(2*edge_length)
def edge_point(i,t):
    a=poly[i]; b=poly[(i+1)%len(poly)]; return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
verts=[]; faces=[]
def add_wall_cell(i,t0,t1,z0,z1):
    a=edge_point(i,t0); b=edge_point(i,t1); k=len(verts)
    verts.extend([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)])
    faces.append((k,k+1,k+2,k+3))
for i in range(len(poly)):
    if i==door_edge:
        add_wall_cell(i,0,door_t0,0,wall_top); add_wall_cell(i,door_t1,1,0,wall_top)
        add_wall_cell(i,door_t0,door_t1,door_height,wall_top)
    else: add_wall_cell(i,0,1,0,wall_top)
mesh_obj('GIS footprint exterior wall shell with west service opening',verts,faces,brick)
# GIS boundary plinth interrupted at the inferred service opening.
for i,(x0,y0) in enumerate(poly):
    x1,y1=poly[(i+1)%len(poly)]; dx,dy=x1-x0,y1-y0; length=math.hypot(dx,dy); rot=math.atan2(dy,dx)
    if i==door_edge:
        for t0,t1 in ((0,door_t0),(door_t1,1)):
            a=edge_point(i,t0); b=edge_point(i,t1); inward=Vector((-dy,dx)).normalized() if sum(poly[j][0]*poly[(j+1)%len(poly)][1]-poly[(j+1)%len(poly)][0]*poly[j][1] for j in range(len(poly)))>0 else Vector((dy,-dx)).normalized()
            box(f'Concrete perimeter plinth {i+1:02d}-{t0:.2f}',((a[0]+b[0])/2+inward.x*.11,(a[1]+b[1])/2+inward.y*.11,.16),(length*(t1-t0),.22,.32),trim,rot)
    else:
        inward=Vector((-dy,dx)).normalized() if sum(poly[j][0]*poly[(j+1)%len(poly)][1]-poly[(j+1)%len(poly)][0]*poly[j][1] for j in range(len(poly)))>0 else Vector((dy,-dx)).normalized()
        box(f'Concrete perimeter plinth {i+1:02d}',((x0+x1)/2+inward.x*.11,(y0+y1)/2+inward.y*.11,.16),(length,.22,.32),trim,rot)
# Flush sliding service door leaf and simple galvanized frame/track.
a=edge_point(door_edge,(door_t0+door_t1)/2); outward=Vector((a[0],a[1])).normalized(); a=(a[0]-outward.x*.055,a[1]-outward.y*.055); edge_a=poly[door_edge]; edge_b=poly[(door_edge+1)%len(poly)]; door_rot=math.atan2(edge_b[1]-edge_a[1],edge_b[0]-edge_a[0])
box('Inferred large animal service slider',(a[0],a[1],door_height/2),(door_width-.12,.07,door_height-.08),metal,door_rot)
box('Service door head track',(a[0],a[1],door_height+.035),(door_width+.18,.09,.07),stallmat,door_rot)
for side in (-1,1):
    bx,by=edge_point(door_edge,(door_t0+door_t1)/2+side*(door_width/2)/edge_length); bx-=outward.x*.065; by-=outward.y*.065
    box(f'Service door jamb {side}',(bx,by,door_height/2),(.10,.10,door_height),trim,door_rot)

# Current vertical aerial imagery shows a white, low-slope membrane roof. Exact
# pitch and parapet/eave height remain unmeasured; the shallow edge is only a fascia.
roofz=eave+.20
mesh_obj('Low-slope white membrane roof plane',[(x,y,roofz) for x,y in poly],[tuple(range(len(poly)))],roofmat)
for i,(x0,y0) in enumerate(poly):
    x1,y1=poly[(i+1)%len(poly)]; dx,dy=x1-x0,y1-y0; le=math.hypot(dx,dy)
    inward=Vector((-dy,dx)).normalized() if sum(poly[j][0]*poly[(j+1)%len(poly)][1]-poly[(j+1)%len(poly)][0]*poly[j][1] for j in range(len(poly)))>0 else Vector((dy,-dx)).normalized()
    box(f'Roof edge fascia {i+1:02d}',((x0+x1)/2+inward.x*.06,(y0+y1)/2+inward.y*.06,eave+.10),(le,.12,.18),trim,math.atan2(dy,dx))
# Roof equipment centers mapped from the current aerial tile to WGS84 then to
# the project's local approximate metre frame. Tile imagery capture date is unknown.
for name,center,dims in [('Aerial rooftop plant west',(-2.37,.50),(1.55,.85,.72)),('Aerial rooftop plant east',(14.69,-.64),(1.45,.90,.65))]:
    x,y=to_xy(*center); box(name,(x,y,roofz+dims[2]/2),(dims[0],dims[1],dims[2]),metal,theta)
    box(name+' curb',(x,y,roofz+.08),(dims[0]+.18,dims[1]+.18,.16),trim,theta)

# Ground slab and conceptual room-plan walls, respecting the GIS cross-shaped outline.
mesh_obj('Interior floor slab',[(x,y,.05) for x,y in poly],[tuple(range(len(poly)))],floor)
# The GIS plan is a cross-shaped facility: the long east-west arm measures
# roughly 37 x 10 m; north and south projections form support wings. The exact
# room locations are not shown in the historical record, so partitions are schematic.
# Eight documented 12 x 12 ft stalls occupy two banks of four; this arrangement
# is an informed interpretation because no VMIF floor plan is available.
stall_dim=12*0.3048; corridor_width=1.5; stall_start=-2*stall_dim; stall_end=2*stall_dim
v_corr_s=-corridor_width/2; v_corr_n=corridor_width/2
v_south=v_corr_s-stall_dim; v_north=v_corr_n+stall_dim
# Corridor walls use one documented viewing window and access door per stall.
for row,(va,vb,linev) in enumerate([(v_south,v_corr_s,v_corr_s),(v_corr_n,v_north,v_corr_n)],1):
    for k in range(4):
        ua=stall_start+k*stall_dim; ub=ua+stall_dim; win0=ua+.42; win1=ua+1.12; door0=ua+2.05; door1=ua+3.20
        for a,b in ((ua,win0),(win1,door0),(door1,ub)):
            beam_uv(f'Stall bank {row} corridor masonry {k+1} {a:.2f}',a,linev,b,linev,.05,2.65,.10,partition)
        beam_uv(f'Stall bank {row} window sill masonry {k+1}',win0,linev,win1,linev,.05,1.48,.10,partition)
        beam_uv(f'Stall bank {row} window head masonry {k+1}',win0,linev,win1,linev,2.08,2.65,.10,partition)
        x,y=to_xy((win0+win1)/2,linev); box(f'Stall bank {row} viewing window {k+1}',(x,y,1.78),(.70,.055,.58),glass,theta)
        x,y=to_xy((door0+door1)/2,linev); box(f'Stall bank {row} protocol stall door {k+1}',(x,y,1.08),(1.15,.07,2.06),metal,theta)
        box(f'Stall bank {row} door vision lite {k+1}',(x,y,1.76),(.48,.035,.30),glass,theta)
        for uedge in (ua,ub):
            if uedge==stall_start or uedge==stall_end: continue
            beam_uv(f'Stall bank {row} partition at {uedge:.2f}',uedge,va,uedge,vb,.05,2.45,.10,partition)
        for z in (.55,1.05,1.55): beam_uv(f'Stall bank {row} divider rail {k+1} at {z}',ua,va if row==1 else vb,ub,va if row==1 else vb,z,z+.05,.08,stallmat)
# Lower spur is the schematic mechanical / air-handling zone, consistent with
# archival description of a large mechanical room containing specialized HVAC.
beam_uv('Mechanical room cross partition',-5.35,-9.15,4.25,-9.15,.05,2.75,.12,partition)
beam_uv('Mechanical room side partition',-1.0,-11.1,-1.0,-4.45,.05,2.75,.12,partition)
for i,(uu,vv) in enumerate([(-4.1,-7.2),(-2.1,-7.2),(1.0,-7.2),(2.8,-7.2)],1):
    x,y=to_xy(uu,vv); box(f'Mechanical air-handling equipment mass {i}',(x,y,1.05),(0.85,.9,2.0),metal,theta)
# Upper spur holds schematic treatment / sterilization / stores / office zones.
beam_uv('North support rooms partition A',-5.35,7.35,4.35,7.35,.05,2.65,.10,partition)
beam_uv('North support rooms partition B',-.4,6.0,-.4,8.35,.05,2.65,.10,partition)
beam_uv('North support rooms partition C',2.25,6.0,2.25,8.35,.05,2.65,.10,partition)
# Exterior window placement remains unverified; one conservatively inferred west service door is cut through the GIS wall shell. Interior observation windows and stall doors are documented by the Purdue article.
# Scene lighting and orthographic elevated preview camera.
def point(obj,at): obj.rotation_euler=(Vector(at)-obj.location).to_track_quat('-Z','Y').to_euler()
ld=bpy.data.lights.new('Large softbox','AREA'); lo=bpy.data.objects.new('Large softbox',ld); scene.collection.objects.link(lo); lo.location=(30,-35,55); ld.energy=22000; ld.shape='DISK'; ld.size=38; point(lo,(0,0,0))
ld2=bpy.data.lights.new('Fill','AREA'); lo2=bpy.data.objects.new('Fill',ld2); scene.collection.objects.link(lo2); lo2.location=(-35,22,24); ld2.energy=11000; ld2.size=30; point(lo2,(0,0,1))
camdata=bpy.data.cameras.new('VMIF preview camera'); cam=bpy.data.objects.new('VMIF preview camera',camdata); scene.collection.objects.link(cam); cam.location=(L*.78,-W*1.15,34); point(cam,(0,0,1.4)); camdata.type='ORTHO'; camdata.ortho_scale=max(L,W)*1.95; scene.camera=cam
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(AUDIT/'vmif_preview.png'); scene.render.film_transparent=False
# Set modest ambient occlusion and color management for readable surfaces.
scene.view_settings.view_transform='AgX'
# Asset has exact GIS XY geometry at local origin; the campus anchor is recorded separately.
# Cameras/lights live in the scene but outside the exported asset collection.
# Store source provenance as custom props for quick inspection.
coll['building_id']=ASSET_ID; coll['source_feature']='Purdue BuildingShapesZip4 FID 78 / VMIF'; coll['coordinates']='local meters; X east, Y north, Z up'
scene['building_id']=ASSET_ID; scene['anchor_campus_xy_m']=list(anchor); scene['footprint_source_area_m2']=attrs['Shape__Area']; scene['height_status']='estimated from GIS Extrution=12 interpreted as feet; not field verified'
# Ensure only model objects are exported inside contract collection; render rig stays in scene root.
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
bpy.ops.render.render(write_still=True)
for ob in coll.objects:
    if ob.name.startswith('Low-slope white membrane roof plane') or ob.name.startswith('Roof edge fascia') or ob.name.startswith('Aerial rooftop plant'):
        ob.hide_render=True
scene.render.filepath=str(AUDIT/'vmif_cutaway.png'); bpy.ops.render.render(write_still=True)
for ob in coll.objects: ob.hide_render=False
scene.render.filepath=str(AUDIT/'vmif_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))

# Write structured provenance/uncertainty/evidence summary.
import hashlib
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
report={
 'building_id':ASSET_ID,'asset_path':'modular/buildings/'+ASSET.name,'collection':COLLECTION_NAME,'scene':SCENE_NAME,
 'source_feature':{'provider':'Purdue University GIS / BuildingShapesZip4','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0','feature_id':78,'building_abbreviation':'VMIF','name':attrs['BUILDING_N'],'address':attrs['ADDRESS'],'repository_snapshot':'audit/official_purdue_buildings_wgs84.json; source audit ledger retrieved 2026-10-22','snapshot':'audit/veterinary_medicine_isolation_facility/purdue_gis_VMIF_feature.json','crs':'EPSG:4326 WGS84','transform':'Project documented local approximation: X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040; meters east/north; area centroid local origin','reported_polygon_area_m2':attrs['Shape__Area'],'coordinate_ring_area_projected_m2':coordinate_area_m2,'reported_perimeter_m':attrs['Shape__Length'],'stories':attrs['NUM_LEVELS'],'extrusion_field_value':attrs['Extrution'],'extrusion_units':'not specified in layer metadata','measurement_method':'GIS polygon converted without scaling; anchor is GIS polygon area centroid.'},
 'official_news_source':{'provider':'Purdue News Service','url':'https://www.purdue.edu/uns/html4ever/2005/050112.Levy.isolation.html','published':'2005-01-12','retrieved':'2026-10-26','raw_snapshot':'audit/veterinary_medicine_isolation_facility/purdue_news_vmif_2005.html','photo_url':'https://www.purdue.edu/uns/images/+2004/vet-isolation.jpg','photo_file':'audit/veterinary_medicine_isolation_facility/vet-isolation.jpg','content':'Reports eight 12-by-12-foot stalls, one configured for cattle; treatment/sterilization/storage/office spaces; hallway viewing windows; stall doors display protocol notices. Image depicts interior, not exterior elevations.'},
 'official_historic_database_source':{'provider':'Purdue University Libraries Archives and Special Collections','url':'https://collections.lib.purdue.edu/campus/buildings/24','retrieved':'2026-10-26','page_snapshot':'audit/veterinary_medicine_isolation_facility/page_0.html','recorded_square_footage':5324},
 'official_facilities_inventory_source':{'provider':'Purdue University Treasurer / Facilities inventory','url':'https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/03/Space-Report_1.13.1HE_Buiding_List_Oct2021.pdf','published':'2021 inventory; retrieved 2026-10-26','reported_square_footage':5323.99},
 'area_conflict':{'gis_shape_area_field_m2':attrs['Shape__Area'],'gis_shape_area_field_sqft':round(attrs['Shape__Area']*10.7639104167,1),'area_from_GIS_ring_after_documented_local_projection_m2':coordinate_area_m2,'ring_area_sqft':round(coordinate_area_m2*10.7639104167,1),'field_vs_ring_difference_m2':round(attrs['Shape__Area']-coordinate_area_m2,3),'field_vs_ring_difference_percent_of_ring':round((attrs['Shape__Area']/coordinate_area_m2-1)*100,1),'purdue_news_2005_sqft':5740,'historic_database_sqft':5324,'treasurer_inventory_sqft':5323.99,'interpretation':'The GIS Shape__Area attribute (849.074 m²) materially disagrees with area calculated from its own 12 polygon vertices in the documented local projection (491.252 m²). Published 5,324 sq ft facility area is close to the projected ring area; 2005 Purdue News reports 5,740 sq ft. These values may reflect different measurement bases, but the provider field-vs-ring discrepancy remains unresolved. Model follows source vertices without scaling.'},
 'aerial_source':{'provider':'Esri World Imagery','url':'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer','tile_url':'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/19/197687/135564','service_metadata':'audit/veterinary_medicine_isolation_facility/esri_world_imagery_service_metadata.json','tile_snapshot':'audit/veterinary_medicine_isolation_facility/esri_world_imagery_vmif_z19.jpg','gis_overlay':'audit/veterinary_medicine_isolation_facility/esri_world_imagery_vmif_gis_overlay.png','retrieved':'2026-10-26','tile':'level 19, column 135564, row 197687','crs':'Web Mercator / WKID 3857 tile scheme, imagery reprojection verified by GIS overlay','source_capture_date':'not exposed for this tile','method':'Tile projected from WGS84 Web Mercator quad; GIS ring overlaid. Roof plan broadly aligns; roof is pale/white and two rooftop equipment clusters are visible; wall openings are occluded from above.'},
 'additional_identity_source':{'provider':'Purdue University campus map','url':'https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/Purdue_414cab09-65bd-4c2d-9fe4-89b4771056ef.pdf','content':'Lists VMIF as Veterinary Medicine Isolation Facility in map grid G10.'},
 'anchor_campus_xy_m':list(anchor),'local_footprint_dimensions_m':{'major':L,'minor':W,'source_area':attrs['Shape__Area']},
 'modeled_detail':{'exterior_service_door':'One approximately 3 m sliding animal/service door on west facade; conservative placement on aerial-visible paved service side, inferred because aerial does not show door elevation.','exterior_windows':'No unambiguous exterior window pattern is visible in aerial/current sources; none invented.','interior_stall_doors':8,'interior_observation_windows':8,'stall_clear_dimensions_m':[stall_dim,stall_dim],'roof_units':2,'facade':'Light painted block courses based on the official 2005 interior photo; extending the finish to exterior is an assumption.'},
 'model_notes':['Exterior footprint follows the official GIS ring at native scale; projected coordinate ring area is 491.252 m² while the same feature Shape__Area attribute says 849.074 m². The roof outline broadly aligns with the imagery; geometry was not rescaled.','Interior stall bays are dimensioned to documented 12 x 12 ft; room arrangement remains inferred because no plan was found.','Single storey follows official GIS NUM_LEVELS=1 / CountOfFLO=1.','Eave is set to 3.60 m and roof top to 3.80 m as visual estimates only. GIS Extrution=12 has undocumented units and was not treated as measured height.','Low-slope, pale roof form and two rooftop equipment clusters follow aerial imagery; exact pitch, parapet and vertical dimensions are unknown.','Wall course detail is visible in official interior photo; matching exterior material/course is a cautious visual extrapolation.','GIS Shape__Area attribute 849.074 m² conflicts with the 491.252 m² calculated from source vertices (72.8% relative to ring area). The projected ring area is close to 5,324 sq ft in Purdue inventory; Purdue News reports 5,740 sq ft. The footprint remains unscaled.','Existing massing used 16 m fallback height; no master or shared placement data was edited.'],
 'uncertainty':['GIS identity is supported by FID 78, VMIF abbreviation, name, address and GlobalID.','GIS Shape__Area versus coordinate ring area is an unresolved internal provider conflict; the GIS ring itself aligns closely with roof imagery and remains unscaled.','Aerial tile capture date is unknown; it confirms roof silhouette and visible rooftop plant but not elevation.','Exterior service door is a clearly marked inference on the west paved service side, not directly visible in aerial.','Exterior window locations, materials beyond the interior photo, exact eave/roof elevations and room positions remain unverified.'],
 'preview':'audit/veterinary_medicine_isolation_facility/vmif_preview.png','cutaway_preview':'audit/veterinary_medicine_isolation_facility/vmif_cutaway.png','blend_sha256':sha,'object_count_exported':len(coll.objects)
}
(AUDIT/'evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'asset':str(ASSET),'sha256':sha,'exported_objects':len(coll.objects),'anchor':anchor,'dimensions':[L,W],'area':attrs['Shape__Area'],'collection':COLLECTION_NAME,'scene':SCENE_NAME},indent=2))








